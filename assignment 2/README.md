# Bee Search

Project for solving SyGuS tasks using bee search and bustle-like model.

## Sample Usage

`bee.py` contains code for bee-search and `bus.py` contains code for BUS. Both work with following signature however create different log files: `bee-search.log` and `bus.log` respectively.

```sh
# Go to src dir
python3 bee.py 57 0
# Generic syntax: bee.py [TaskID] [Easy|Hard]
```

Here, `0 = easy, 1 = hard`. `TaskID` is the SyGuS task number, all tasks names are listed in `config/sygus_string_benchmarks.txt` and actual tasks are in `sygus_string_tasks/`

Running a task will create a log file in logs folder named `bee-search.log`. For the above mentioned task it will have logs like:

```
...
[Task: 56] Benchmark: exceljet1.sl
[Task: 56] Result: Success
[Task: 56] Program: _arg_1.Substr((_arg_1.IndexOf("_") + 1),_arg_1.Length())
[Task: 56] Number of evaluations: 20705
[Task: 56] 2023-02-13 15:44:44.304960
[Task: 56] Time taken: 0:00:02.525268
...
```

## src

It is the source code directory and contains all the source code in python for running bee-search with Wu cost fn.

## models

Contains pre-trained models

## config

It contains the benchmark and properties configuration
