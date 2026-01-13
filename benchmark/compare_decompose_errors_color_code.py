"""
Compare ILP decoding results for a color code DEM with decompose_errors on/off.

Example:
    benchmark/.venv/bin/python benchmark/compare_decompose_errors_color_code.py \
        --distance 3 --rounds 3 --shots 1000 --noise 0.01
"""

import argparse
import time

import numpy as np

from ilpdecoder import Decoder, get_available_solvers


def decode_stats(decoder, detections, observables):
    """Return (ms_per_shot, logical_error_rate)."""
    start = time.perf_counter()
    correct = 0
    shots = detections.shape[0]
    for i in range(shots):
        _, pred = decoder.decode(detections[i])
        if observables.size and np.array_equal(pred, observables[i]):
            correct += 1
    elapsed = time.perf_counter() - start
    ms_per_shot = (elapsed / shots) * 1000.0
    ler = None
    if observables.size:
        ler = 1.0 - (correct / shots)
    return ms_per_shot, ler


def main():
    parser = argparse.ArgumentParser(
        description="Compare decompose_errors=True/False on a color code circuit."
    )
    parser.add_argument("--distance", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--shots", type=int, default=1000)
    parser.add_argument("--noise", type=float, default=0.01)
    parser.add_argument("--solver", type=str, default=None)
    args = parser.parse_args()

    try:
        import stim
    except Exception as exc:
        raise SystemExit("stim is required (pip install stim)") from exc

    if args.solver:
        available = [s.lower() for s in get_available_solvers()]
        if args.solver.lower() not in available:
            raise SystemExit(
                f"Requested solver '{args.solver}' is not available. "
                f"Available: {', '.join(available) if available else 'none'}"
            )

    circuit = stim.Circuit.generated(
        "color_code:memory_xyz",
        distance=args.distance,
        rounds=args.rounds,
        after_clifford_depolarization=args.noise,
    )

    sampler = circuit.compile_detector_sampler()
    detections, observables = sampler.sample(
        shots=args.shots, separate_observables=True
    )
    detections = detections.astype(np.uint8)
    observables = observables.astype(np.uint8)

    dem_true = circuit.detector_error_model(decompose_errors=True)
    dem_false = circuit.detector_error_model(decompose_errors=False)

    print(
        "color_code:memory_xyz distance={distance} rounds={rounds} shots={shots} "
        "noise={noise}".format(
            distance=args.distance,
            rounds=args.rounds,
            shots=args.shots,
            noise=args.noise,
        )
    )
    print("Note: decompose_errors=False keeps correlated error mechanisms.")
    print("      This decoder ignores '^' alternatives, so results are approximate.")

    decoder_true = Decoder.from_stim_dem(dem_true, solver=args.solver)
    decoder_false = Decoder.from_stim_dem(dem_false, solver=args.solver)

    results = []
    for label, decoder in (
        ("decompose_errors=True", decoder_true),
        ("decompose_errors=False", decoder_false),
    ):
        ms_per_shot, ler = decode_stats(decoder, detections, observables)
        results.append((label, ms_per_shot, ler))

    for label, ms_per_shot, ler in results:
        if ler is None:
            ler_text = "n/a"
        else:
            ler_text = f"{ler:.3%}"
        print(f"{label:22s} {ms_per_shot:9.4f} ms/shot  logical error rate: {ler_text}")


if __name__ == "__main__":
    main()
