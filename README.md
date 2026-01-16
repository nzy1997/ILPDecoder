# ILPDecoder

[![CI](https://github.com/nzy1997/ILPDecoder/actions/workflows/ci.yml/badge.svg)](https://github.com/nzy1997/ILPDecoder/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/nzy1997/ILPDecoder/branch/main/graph/badge.svg)](https://codecov.io/gh/nzy1997/ILPDecoder)

ILPDecoder is a Python package for maximum-likelihood quantum error correction decoding using integer linear programming (ILP). It turns parity-check matrices or Stim `DetectorErrorModel`s into an ILP and solves it with a built-in backend out of the box. It is aimed at correctness-focused baselines, solver comparisons, and small-to-medium code studies rather than high-throughput production decoding.

Documentation: https://nzy1997.github.io/ILPDecoder/

## Scope and Highlights

What it does well:
- **Out-of-the-box decoding** with minimal setup.
- **Inputs from parity-check matrices** or **Stim DetectorErrorModel**.
- **Maximum-likelihood decoding** via weights or error probabilities.
- **PyMatching-like API** for easy experimentation.

When it is not a fit:
- Large code distances or high-shot workloads where ILP scaling dominates; use MWPM/BPOSD for throughput.

## Installation

```bash
# Basic installation
pip install ilpdecoder

# With Stim support
pip install ilpdecoder[stim]

# With SciPy sparse-matrix support
pip install ilpdecoder[scipy]
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/nzy1997/ILPDecoder
cd ILPDecoder

# Create virtual environment (using uv)
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv add highspy numpy scipy stim
uv add pyomo --dev
uv add pytest --dev

# Or using pip
pip install -e ".[dev]"
```

### Running Tests Locally

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_decoder.py -v

# Run a quick functionality check
python main.py
```

### Running Examples

```bash
python examples/basic_usage.py
python examples/surface_code_example.py
benchmark/.venv/bin/python benchmark/benchmark_decoders.py --shots 10000 --distance 3 --rounds 3 --noise 0.01
```

## Quick Start

### Parity-Check Matrix Decoding

```python
import numpy as np
from ilpdecoder import Decoder

# Define a simple repetition code parity-check matrix
H = np.array([
    [1, 1, 0, 0, 0],
    [0, 1, 1, 0, 0],
    [0, 0, 1, 1, 0],
    [0, 0, 0, 1, 1],
])

# Create decoder
decoder = Decoder.from_parity_check_matrix(H)

# Decode a syndrome
syndrome = [1, 0, 0, 1]
correction = decoder.decode(syndrome)
print(f"Correction: {correction}")
```

Note: passing SciPy sparse matrices requires `scipy` to be installed (e.g., `pip install ilpdecoder[scipy]`).

### Stim DetectorErrorModel Decoding

```python
import stim
from ilpdecoder import Decoder

# Generate a surface code circuit
circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    distance=3,
    rounds=3,
    after_clifford_depolarization=0.01
)

# Get detector error model
dem = circuit.detector_error_model(decompose_errors=True)

# Create decoder
decoder = Decoder.from_stim_dem(dem)

# Sample and decode
sampler = circuit.compile_detector_sampler()
detection_events, observables = sampler.sample(shots=100, separate_observables=True)

for i in range(10):
    _, predicted_obs = decoder.decode(detection_events[i])
    print(f"Shot {i}: predicted={predicted_obs}, actual={observables[i]}")
```

#### Stim DEM Support Notes

- Only `error(p)` lines are parsed; tags in `error[...]` are ignored. `detector` and
  `logical_observable` metadata lines are ignored. `shift_detectors` offsets are applied.
  `repeat` blocks are flattened by default; this can expand large DEMs.
  `detector_separator` is unsupported and raises an error.
- The `^` separator is treated as whitespace and does not change parsing.
- If you want to fail fast instead of flattening, pass `flatten_dem=False`.

### Maximum-Likelihood Decoding with Weights

```python
import numpy as np
from ilpdecoder import Decoder

H = np.array([[1, 1, 0], [0, 1, 1]])
error_probs = [0.1, 0.01, 0.1]

# Weights are computed automatically from probabilities
decoder = Decoder.from_parity_check_matrix(H, error_probabilities=error_probs)

syndrome = [1, 1]
correction, weight = decoder.decode(syndrome, return_weight=True)
print(f"ML correction: {correction}, weight: {weight}")
```

Note: `error_probabilities` must be in (0, 0.5]; pass explicit `weights` for p > 0.5.

## Benchmark

Install optional deps for the benchmarks:

```bash
pip install stim pymatching ldpc tesseract-decoder
```

Notes:
- BPOSD runs with `max_iter=50`, `osd_order=0`, and `bp_method=minimum_sum`.
- Tesseract runs with `det_beam=50` by default (adjustable via `--tesseract-beam`).

### Circuit-level rotated surface code memory

```bash
benchmark/.venv/bin/python benchmark/benchmark_decoders.py --compare-ilp-solvers --ilp-solvers highs,scip,gurobi,cbc,glpk --shots 10000 --distance 3 --rounds 3 --noise 0.01
```

Results from a local macOS arm64 run (shots=10000, your numbers will vary):

| Decoder | Time (ms/shot) | Logical Error Rate |
|--------|---------------|--------------------|
| ILP[highs] (direct) | 2.7469 | 1.610% |
| ILP[gurobi] (direct) | 0.5923 | 1.620% |
| ILP[scip] | 27.1241 | 1.620% |
| ILP[cbc] | 13.7808 | 1.620% |
| ILP[glpk] | 7.8176 | 1.610% |
| MWPM (pymatching) | 0.0034 | 2.090% |
| BPOSD (ldpc) | 0.0308 | 7.740% |
| Tesseract | 0.2195 | 1.540% |

### Code-capacity surface code (data errors only, perfect syndrome)

```bash
benchmark/.venv/bin/python benchmark/benchmark_decoders.py --noise-model code_capacity --compare-ilp-solvers --ilp-solvers highs,scip,gurobi,cbc,glpk --shots 10000 --distance 3 --rounds 1 --noise 0.01
```

Results from a local macOS arm64 run (shots=10000, your numbers will vary):

| Decoder | Time (ms/shot) | Logical Error Rate |
|--------|---------------|--------------------|
| ILP[highs] (direct) | 3.1914 | 0.120% |
| ILP[gurobi] (direct) | 0.0826 | 0.120% |
| ILP[scip] | 22.6194 | 0.120% |
| ILP[cbc] | 9.8211 | 0.120% |
| ILP[glpk] | 4.7919 | 0.120% |
| MWPM (pymatching) | 0.0033 | 0.120% |
| BPOSD (ldpc) | 0.0029 | 0.120% |
| Tesseract | 0.0150 | 0.120% |

### Color code (`color_code:memory_xyz`)

```bash
benchmark/.venv/bin/python benchmark/benchmark_decoders.py --code-task color_code:memory_xyz --compare-ilp-solvers --ilp-solvers highs,scip,gurobi,cbc,glpk --shots 10000 --distance 3 --rounds 3 --noise 0.01
```

Results from a local macOS arm64 run (shots=10000, your numbers will vary):

| Decoder | Time (ms/shot) | Logical Error Rate |
|--------|---------------|--------------------|
| ILP[highs] (direct) | 2.0008 | 4.510% |
| ILP[gurobi] (direct) | 0.3164 | 4.500% |
| ILP[scip] | 24.0461 | 4.500% |
| ILP[cbc] | 11.0780 | 4.510% |
| ILP[glpk] | 5.8961 | 4.500% |
| MWPM (pymatching) | 0.0041 | 13.610% |
| BPOSD (ldpc) | 0.0124 | 9.970% |
| Tesseract | 0.0931 | 4.240% |

## API Reference

### `Decoder`

Main decoder class.

**Class Methods:**
- `from_parity_check_matrix(H, weights=None, error_probabilities=None, solver=None)` - Create from parity-check matrix
- `from_stim_dem(dem, solver=None, merge_parallel_edges=True, flatten_dem=True)` - Create from Stim DetectorErrorModel

**Instance Methods:**
- `decode(syndrome, return_weight=False)` - Decode a single syndrome
- `decode_batch(syndromes)` - Decode multiple syndromes
- `set_solver(name, **options)` - Switch solver

**Properties:**
- `num_detectors` - Number of parity checks/detectors
- `num_errors` - Number of error mechanisms
- `num_observables` - Number of logical observables (for DEM)
- `solver_name` - Current solver name

### `get_available_solvers()`

Returns a list of available solver names.

```python
from ilpdecoder import get_available_solvers
print(get_available_solvers())  # e.g., ['scip', 'highs', 'cbc']
```

## License

MIT License
