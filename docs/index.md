# ILPDecoder

ILPDecoder is a Python package for maximum-likelihood quantum error correction decoding
using integer linear programming (ILP). It builds an ILP from parity-check matrices
or Stim DetectorErrorModels and solves it with a direct HiGHS backend by default
(no Pyomo required). Optional backends are available for direct Gurobi (licensed)
or Pyomo-based solvers.

## Installation

```bash
# Basic installation (direct HiGHS backend)
pip install ilpdecoder

# Optional: Pyomo backend for other solvers
pip install ilpdecoder[pyomo]

# Optional: direct Gurobi backend (licensed)
pip install ilpdecoder[gurobi]

# Optional: sinter integration (benchmarking)
pip install ilpdecoder[sinter]

# With Stim support
pip install ilpdecoder[stim]

# With SciPy sparse-matrix support
pip install ilpdecoder[scipy]
```

## Quickstart

### Parity-check matrix decoding

```python
import numpy as np
from ilpdecoder import Decoder

H = np.array([
    [1, 1, 0],
    [0, 1, 1],
], dtype=np.uint8)

# Uses direct HiGHS by default.
decoder = Decoder.from_parity_check_matrix(H)

syndrome = np.array([1, 0], dtype=np.uint8)
error, _ = decoder.decode(syndrome)
print(error)
```

### Stim DetectorErrorModel decoding

```python
import stim
from ilpdecoder import Decoder

circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    distance=3,
    rounds=3,
    after_clifford_depolarization=0.01,
)

dem = circuit.detector_error_model(decompose_errors=True)
decoder = Decoder.from_stim_dem(dem)

sampler = circuit.compile_detector_sampler()
detections, observables = sampler.sample(shots=100, separate_observables=True)

for i in range(5):
    _, predicted = decoder.decode(detections[i])
    print(f"shot {i}: predicted={predicted}, actual={observables[i]}")
```

## Documentation Map

- Solver backends and configuration: `solvers.md`
- ILP formulation and assumptions: `math.md`
- Stim DEM support and caveats: `stim_dem.md`
- Sinter integration: `sinter.md`
- Examples walkthrough: `examples.md`
- Benchmarks and scripts: `benchmarks.md`
