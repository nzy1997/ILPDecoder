# Examples

This page mirrors the scripts in `examples/` and explains what they do. The code
blocks are split into sections with commentary in between for easier reading.

## `examples/basic_usage.py`

**Purpose:** a grab bag of basic workflows (parity-check decoding, weights,
Stim DEM parsing, solver switching, batch decoding).

**Run:**

```bash
python examples/basic_usage.py
```

### Imports

```python
import numpy as np

from ilpdecoder import Decoder, get_available_solvers
```

These imports cover matrix handling and the main decoder API.

### Repetition code example

```python
def example_repetition_code():
    """Example: Decode a 5-qubit repetition code."""
    print("=" * 60)
    print("Example: 5-Qubit Repetition Code")
    print("=" * 60)

    H = np.array([
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
    ])

    # Create decoder (uses default solver)
    decoder = Decoder.from_parity_check_matrix(H)
    print(f"Decoder: {decoder}")

    # Test case: single error on qubit 2
    true_error = np.array([0, 0, 1, 0, 0])
    syndrome = (H @ true_error) % 2
    print(f"\nTrue error: {true_error}")
    print(f"Syndrome: {syndrome}")

    correction = decoder.decode(syndrome)
    print(f"Correction: {correction}")

    is_valid = np.array_equal((H @ correction) % 2, syndrome)
    print(f"Valid correction: {is_valid}")

    correction, weight = decoder.decode(syndrome, return_weight=True)
    print(f"Solution weight: {weight}")
```

This shows how to build an ILP from a parity-check matrix and verify that the
correction matches the syndrome.

### Weighted decoding example

```python
def example_weighted_decoding():
    """Example: Maximum-likelihood decoding with weighted errors."""
    print("\n" + "=" * 60)
    print("Example: Weighted Decoding (Maximum Likelihood)")
    print("=" * 60)

    H = np.array([[1, 1, 0], [0, 1, 1]])
    error_probs = [0.1, 0.01, 0.1]  # Middle qubit more reliable

    decoder = Decoder.from_parity_check_matrix(H, error_probabilities=error_probs)

    print(f"Error probabilities: {error_probs}")
    print(f"Computed weights: {decoder.get_weights()}")

    syndrome = [1, 1]
    print(f"\nSyndrome: {syndrome}")

    correction = decoder.decode(syndrome)
    print(f"Correction: {correction}")
    print("(Should prefer [1,0,1] since middle qubit is more reliable)")
```

This demonstrates how different per-qubit probabilities map to different
weights in the objective function.

### Stim DEM parsing example

```python
def example_stim_dem():
    """Example: Decoding with Stim detector error model."""
    print("\n" + "=" * 60)
    print("Example: Stim Detector Error Model")
    print("=" * 60)

    dem_str = """
error(0.1) D0 L0
error(0.1) D0 D1
error(0.1) D1 L1
"""

    decoder = Decoder.from_stim_dem(dem_str)
    print(f"Decoder: {decoder}")
    print(f"Detectors: {decoder.num_detectors}")
    print(f"Observables: {decoder.num_observables}")
    print(f"Error mechanisms: {decoder.num_errors}")

    detector_outcomes = [1, 0]
    print(f"\nDetector outcomes: {detector_outcomes}")

    correction, observables = decoder.decode(detector_outcomes)
    print(f"Predicted observables: {observables}")
```

This shows the simplest possible DEM parsing workflow without needing Stim.

### Solver switching example

```python
def example_solver_switching():
    """
    Example: Switching between solvers.

    You can switch solvers without rebuilding the model.
    """
    print("\n" + "=" * 60)
    print("Example: Solver Switching")
    print("=" * 60)

    available = get_available_solvers()
    print(f"Available solvers: {available}")

    if not available:
        print("No solvers available. Install SCIP, HiGHS, CBC, or GLPK.")
        return

    H = np.array([[1, 1, 0], [0, 1, 1]])
    decoder = Decoder.from_parity_check_matrix(H)

    for solver in available:
        print(f"\n--- Using {solver.upper()} ---")

        # Switch solver
        decoder.set_solver(solver, verbose=False)

        syndrome = [1, 0]
        correction, weight = decoder.decode(syndrome, return_weight=True)

        print(f"Correction: {correction}")
        print(f"Weight: {weight}")
```

This loops over installed solvers and decodes the same syndrome with each one.

### Batch decoding example

```python
def example_batch_decoding():
    """Example: Batch decoding multiple syndromes."""
    print("\n" + "=" * 60)
    print("Example: Batch Decoding")
    print("=" * 60)

    H = np.array([
        [1, 1, 0, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 1, 0],
        [0, 0, 0, 1, 1],
    ])

    decoder = Decoder.from_parity_check_matrix(H)

    np.random.seed(42)
    syndromes = np.random.randint(0, 2, size=(5, 4))

    print("Syndromes:")
    for i, s in enumerate(syndromes):
        print(f"  {i}: {s}")

    corrections = decoder.decode_batch(syndromes)

    print("\nCorrections:")
    for i, c in enumerate(corrections):
        valid = np.array_equal((H @ c) % 2, syndromes[i])
        print(f"  {i}: {c} (valid: {valid})")
```

This shows the vectorized batch API and a quick validity check.

### Script entry point

```python
def main():
    """Run all examples."""
    print("ILPDecoder Examples")
    print("=" * 60)
    print(f"Available solvers: {get_available_solvers()}")

    if not get_available_solvers():
        print("\nNo solver available!")
        print("Install one of: SCIP, HiGHS, CBC, GLPK")
        return

    example_repetition_code()
    example_weighted_decoding()
    example_stim_dem()
    example_solver_switching()
    example_batch_decoding()

    print("\n" + "=" * 60)
    print("All examples completed!")


if __name__ == "__main__":
    main()
```

## `examples/surface_code_example.py`

**Purpose:** build a circuit-level surface code with Stim, decode detection
shots, and compare solver runtimes.

**Run:**

```bash
python examples/surface_code_example.py
```

### Imports and availability checks

```python
import numpy as np

try:
    import stim
    STIM_AVAILABLE = True
except ImportError:
    STIM_AVAILABLE = False

from ilpdecoder import Decoder, get_available_solvers
```

This loads Stim if available and sets a flag so the script can exit cleanly
when Stim is missing.

### Main decoding example

```python
def surface_code_example():
    """Decode a rotated surface code using ILP."""
    print("=" * 60)
    print("Surface Code Decoding with ILPDecoder")
    print("=" * 60)

    if not STIM_AVAILABLE:
        print("Stim is not installed. Install with: pip install stim")
        return

    if not get_available_solvers():
        print("No solver available. Install SCIP, HiGHS, CBC, or GLPK.")
        return

    distance = 3
    rounds = 3
    noise = 0.01

    print("\nGenerating surface code circuit:")
    print(f"  Distance: {distance}")
    print(f"  Rounds: {rounds}")
    print(f"  Noise: {noise}")

    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_x",
        distance=distance,
        rounds=rounds,
        after_clifford_depolarization=noise
    )

    dem = circuit.detector_error_model(decompose_errors=True)
    print("\nDetector error model:")
    print(f"  Detectors: {dem.num_detectors}")
    print(f"  Observables: {dem.num_observables}")
    print(f"  Error mechanisms: {dem.num_errors}")

    decoder = Decoder.from_stim_dem(dem)
    print(f"\nDecoder: {decoder}")

    num_shots = 100
    print(f"\nSampling {num_shots} shots...")

    sampler = circuit.compile_detector_sampler()
    detection_events, actual_observables = sampler.sample(
        shots=num_shots,
        separate_observables=True
    )

    print("Decoding...")

    num_correct = 0
    num_detected = 0

    for i in range(num_shots):
        if np.any(detection_events[i]):
            num_detected += 1

        _, predicted = decoder.decode(detection_events[i])

        if np.array_equal(predicted, actual_observables[i]):
            num_correct += 1

    print("\nResults:")
    print(f"  Shots with detections: {num_detected}/{num_shots}")
    print(f"  Correct predictions: {num_correct}/{num_shots}")
    print(f"  Logical error rate: {(num_shots - num_correct) / num_shots:.2%}")
```

This mirrors the end-to-end workflow: circuit -> DEM -> ILP -> decoded
observables.

### Solver comparison

```python
def compare_solvers():
    """Compare solve times between different solvers."""
    print("\n" + "=" * 60)
    print("Solver Comparison")
    print("=" * 60)

    if not STIM_AVAILABLE or not get_available_solvers():
        print("Stim or solver not available. Skipping.")
        return

    import time

    circuit = stim.Circuit.generated(
        "surface_code:rotated_memory_x",
        distance=3,
        rounds=3,
        after_clifford_depolarization=0.01
    )

    dem = circuit.detector_error_model(decompose_errors=True)

    sampler = circuit.compile_detector_sampler()
    detection_events, _ = sampler.sample(shots=20, separate_observables=True)

    available = get_available_solvers()
    print(f"\nAvailable solvers: {available}")
    print(f"Testing with {len(detection_events)} shots...")

    for solver in available:
        decoder = Decoder.from_stim_dem(dem, solver=solver)

        start = time.time()
        for i in range(len(detection_events)):
            decoder.decode(detection_events[i])
        elapsed = time.time() - start

        avg_time = elapsed / len(detection_events)
        print(f"  {solver.upper():8s}: {avg_time*1000:6.1f} ms/shot")
```

This provides a quick solver timing comparison on a small test case.

### Script entry point

```python
def main():
    print("ILPDecoder Surface Code Example")
    print("=" * 60)

    surface_code_example()
    compare_solvers()

    print("\n" + "=" * 60)
    print("Example completed!")


if __name__ == "__main__":
    main()
```
