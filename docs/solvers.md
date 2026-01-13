# Solver Backends

ILPDecoder uses a direct HiGHS backend by default. Optional backends are
available for direct Gurobi (licensed) and for Pyomo-based solvers.

## Backend Matrix

| Solver | Backend | Install | Notes |
| --- | --- | --- | --- |
| HiGHS | Direct | `pip install ilpdecoder` | Default backend via highspy. |
| HiGHS | Pyomo | `pip install ilpdecoder[pyomo]` + HiGHS binary | Optional Pyomo path. |
| Gurobi | Direct | `pip install ilpdecoder[gurobi]` | Requires a valid license. |
| Gurobi | Pyomo | `pip install ilpdecoder[pyomo]` + gurobi | Uses Pyomo interface. |
| SCIP | Pyomo | `pip install ilpdecoder[pyomo]` + scip | Open source (binary required). |
| CBC | Pyomo | `pip install ilpdecoder[pyomo]` + cbc | Open source (binary required). |
| GLPK | Pyomo | `pip install ilpdecoder[pyomo]` + glpk | Open source (binary required). |
| CPLEX | Pyomo | `pip install ilpdecoder[pyomo]` + cplex | Commercial license. |

## Switching Solvers

```python
from ilpdecoder import Decoder

# Create a decoder and switch backends later.
decoder = Decoder.from_parity_check_matrix(H)

# Use a Pyomo solver.
decoder.set_solver("scip", time_limit=30)

# Use the direct Gurobi backend (if installed).
decoder.set_solver("gurobi")
```

If a non-HiGHS solver is requested without Pyomo installed, ILPDecoder fails
fast with a one-line install hint.

## Solver Options

```python
decoder.set_solver(
    "scip",
    direct=False,     # Use the Pyomo backend
    time_limit=30,    # Max solve time (seconds)
    gap=0.01,         # Relative ILP gap tolerance
    threads=4,        # Thread count (solver-dependent)
    verbose=True,     # Print solver output
)
```

| Option | Description | Supported Solvers |
| --- | --- | --- |
| `time_limit` | Max solving time (seconds) | All |
| `gap` | Relative ILP gap tolerance | All |
| `threads` | Thread count | HiGHS, Gurobi, CPLEX |
| `verbose` | Print solver output | All |
| `direct` | Use direct backend (default for HiGHS) | HiGHS, Gurobi |

## Availability Checks

`get_available_solvers()` lists solvers based on installed Python packages
and (for Pyomo) solver discovery. The direct Gurobi backend can be imported
without a valid license; a license error is raised when the solver is first
used.
