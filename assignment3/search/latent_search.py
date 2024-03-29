from __future__ import annotations
import copy
from math import inf
import torch

from dsl import DSL
from karel.environment import Environment
from vae.models.base_vae import BaseVAE
from logger.stdout_logger import StdoutLogger
from tasks.task import Task
from config import Config


class LatentSearch:
    """Implements the CEM method from LEAPS paper.
    """
    def __init__(self, model: BaseVAE, task_cls: type[Task], dsl: DSL):
        self.model = model
        self.dsl = dsl
        self.device = self.model.device
        self.population_size = Config.search_population_size
        self.elitism_rate = Config.search_elitism_rate
        self.n_elite = int(Config.search_elitism_rate * self.population_size)
        self.number_executions = Config.search_number_executions
        self.number_iterations = Config.search_number_iterations
        self.sigma = Config.search_sigma
        self.model_hidden_size = Config.model_hidden_size
        self.task_envs = [task_cls(i) for i in range(self.number_executions)]
        self.reduce_to_mean = Config.search_reduce_to_mean
        self.seed = Config.env_seed
        

    def init_population(self) -> torch.Tensor:
        """Initializes the CEM population from a normal distribution.

        Returns:
            torch.Tensor: Initial population as a tensor.
        """
        return torch.stack([
            torch.randn(self.model_hidden_size, device=self.device) for _ in range(self.population_size)
        ])
        
        
    def execute_population(self, population: torch.Tensor) -> tuple[list[str], torch.Tensor]:
        """Runs the given population in the environment and returns a list of mean rewards, after
        `Config.search_number_executions` executions.

        Args:
            population (torch.Tensor): Current population as a tensor.

        Returns:
            tuple[list[str], torch.Tensor]: List of programs as strings and list of mean rewards
            as tensor.
        """
        programs_tokens = self.model.decode_vector(population)
        rewards = []
        programs = []
        for program_tokens in programs_tokens:
            program_str = self.dsl.parse_int_to_str(program_tokens)
            programs.append(program_str)
            try:
                program = self.dsl.parse_str_to_node(program_str)
            except AssertionError: # Invalid program
                mean_reward = -1
                rewards.append(mean_reward)
                continue
            mean_reward = 0.
            for task_env in self.task_envs:
                task_env.reset_state()
                state = task_env.get_state()
                reward = 0
                steps = 0
                for _ in program.run_generator(state):
                    terminated, instant_reward = task_env.get_reward(state)
                    reward += instant_reward
                    steps += 1
                    if terminated or steps > Config.data_max_demo_length:
                        break
                mean_reward += reward
            mean_reward /= self.number_executions
            rewards.append(mean_reward)
        return programs, torch.tensor(rewards, device=self.device)
    
    def search(self) -> tuple[str, float]:
        population = self.init_population()
        best_reward = -float("inf")
        best_program = ""
        for _ in range(self.number_iterations):
            programs, rewards = self.execute_population(population)
            topk = torch.topk(rewards, self.n_elite)
            elite = population[topk.indices]
            if self.reduce_to_mean:
                elite = torch.mean(elite, dim=0).repeat(self.n_elite, 1)
            sample_indices = torch.ones(self.n_elite, device=self.device).multinomial(
                self.population_size, replacement=True)                
            # Best program
            if best_reward < torch.max(rewards):
                best_program = programs[torch.argmax(rewards)]
                best_reward = torch.max(rewards)
            # Prepare next iteration
            population = []
            for index in sample_indices:
                individual = elite[index] + self.sigma * torch.randn(self.model_hidden_size, device=self.device)
                population.append(individual)
            population = torch.stack(population)
        return best_program, best_reward

    def save_gifs(self, program):
        """
        Produces one gif with the execution of best_program (provided as a string) for each of the environments
        used in training. The gifs are saved with the name trace_x.gif, where x specifies the task id. 
        """
        exec_program = self.dsl.parse_str_to_node(program)
        env_number = 1
        for task_env in self.task_envs:
            path = f'output/gifs/mean/{self.seed}/' if self.reduce_to_mean else f'output/gifs/sample/{self.seed}/'

            task_env.reset_state()
            state = task_env.get_state()
            env = Environment(state, exec_program)
            env.run_and_trace(path + 'trace_' + str(env_number) + '.gif')
            env_number += 1
