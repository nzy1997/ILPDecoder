# Sinter Integration

ILPDecoder provides a sinter decoder wrapper for benchmarking and sampling
workflows that use Stim + sinter.

## Install

```bash
pip install ilpdecoder[sinter]
```

This extra installs `sinter` and `stim`. The sinter adapter currently uses the
direct HiGHS backend only.

## Usage with `sinter.collect`

```python
import sinter
import stim
from ilpdecoder.sinter_decoder import SinterIlpDecoder

circuit = stim.Circuit.generated(
    "surface_code:rotated_memory_x",
    distance=3,
    rounds=3,
    after_clifford_depolarization=0.01,
)

tasks = [
    sinter.Task(
        circuit=circuit,
        decoder="ilpdecoder",
        json_metadata={"d": 3, "r": 3},
    )
]

stats = sinter.collect(
    tasks=tasks,
    custom_decoders={"ilpdecoder": SinterIlpDecoder()},
)
```

## Tuning the Solver

You can pass solver settings to the adapter:

```python
decoder = SinterIlpDecoder(
    time_limit=30,
    gap=0.01,
    threads=4,
    verbose=False,
)
```

Any extra HiGHS options can be provided via `options`:

```python
decoder = SinterIlpDecoder(options={"mip_rel_gap": 0.01})
```

## Notes

- The adapter uses `compile_decoder_for_dem` and reuses the direct HiGHS model
  across shots for speed.
- Only the direct HiGHS backend is supported in sinter mode for now.
