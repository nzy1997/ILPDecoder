# Benchmarks

This page summarizes the benchmark scripts and recent local results. Numbers
will vary by machine and solver versions.

## Benchmark Environment

Use a dedicated virtual environment under `benchmark/` to avoid polluting your
global Python:

```bash
python3 -m venv benchmark/.venv
source benchmark/.venv/bin/activate
python -m pip install --upgrade pip

# ILPDecoder + optional solver backends
python -m pip install -e ".[pyomo,gurobi]"

# Benchmark dependencies
python -m pip install stim pymatching ldpc
```

Notes:
- Gurobi requires a valid license and Python < 3.13.
- If you do not need Gurobi, drop `gurobi` from the extras.

## Requirements

```bash
pip install stim pymatching ldpc
```

Non-HiGHS solvers require the Pyomo extra (`pip install ilpdecoder[pyomo]`),
except for the direct Gurobi backend (`pip install ilpdecoder[gurobi]`).

Notes:

- Direct backends: HiGHS, Gurobi.
- Pyomo backends: HiGHS, SCIP, CBC, GLPK, Gurobi, CPLEX.
- BPOSD runs with `max_iter=50`, `osd_order=0`, and `bp_method=minimum_sum`.

## Circuit-level rotated surface code memory

```bash
benchmark/.venv/bin/python benchmark/benchmark_decoders.py \
  --compare-ilp-solvers --ilp-solvers highs,scip,gurobi,cbc,glpk \
  --shots 10000 --distance 3 --rounds 3 --noise 0.01
```

Results from a local macOS arm64 run (shots=10000):

| Decoder | Time (ms/shot) | Logical Error Rate |
| --- | --- | --- |
| ILP[highs] (direct) | 2.7469 | 1.610% |
| ILP[gurobi] (direct) | 0.5923 | 1.620% |
| ILP[scip] (Pyomo) | 27.1241 | 1.620% |
| ILP[cbc] (Pyomo) | 13.7808 | 1.620% |
| ILP[glpk] (Pyomo) | 7.8176 | 1.610% |
| MWPM (pymatching) | 0.0034 | 2.090% |
| BPOSD (ldpc) | 0.0308 | 7.740% |

## Code-capacity surface code (data errors only, perfect syndrome)

```bash
benchmark/.venv/bin/python benchmark/benchmark_decoders.py \
  --noise-model code_capacity --compare-ilp-solvers \
  --ilp-solvers highs,scip,gurobi,cbc,glpk \
  --shots 10000 --distance 3 --rounds 1 --noise 0.01
```

Results from a local macOS arm64 run (shots=10000):

| Decoder | Time (ms/shot) | Logical Error Rate |
| --- | --- | --- |
| ILP[highs] (direct) | 3.1914 | 0.120% |
| ILP[gurobi] (direct) | 0.0826 | 0.120% |
| ILP[scip] (Pyomo) | 22.6194 | 0.120% |
| ILP[cbc] (Pyomo) | 9.8211 | 0.120% |
| ILP[glpk] (Pyomo) | 4.7919 | 0.120% |
| MWPM (pymatching) | 0.0033 | 0.120% |
| BPOSD (ldpc) | 0.0029 | 0.120% |

## Color code (`color_code:memory_xyz`)

```bash
benchmark/.venv/bin/python benchmark/benchmark_decoders.py \
  --code-task color_code:memory_xyz --compare-ilp-solvers \
  --ilp-solvers highs,scip,gurobi,cbc,glpk \
  --shots 10000 --distance 3 --rounds 3 --noise 0.01
```

Results from a local macOS arm64 run (shots=10000):

| Decoder | Time (ms/shot) | Logical Error Rate |
| --- | --- | --- |
| ILP[highs] (direct) | 2.0008 | 4.510% |
| ILP[gurobi] (direct) | 0.3164 | 4.500% |
| ILP[scip] (Pyomo) | 24.0461 | 4.500% |
| ILP[cbc] (Pyomo) | 11.0780 | 4.510% |
| ILP[glpk] (Pyomo) | 5.8961 | 4.500% |
| MWPM (pymatching) | 0.0041 | 13.610% |
| BPOSD (ldpc) | 0.0124 | 9.970% |
