"""
Show that decompose_errors=True/False can produce different ILP problems.

Example:
    benchmark/.venv/bin/python benchmark/compare_decompose_ilp_problem.py \
        --distance 3 --rounds 3 --noise 0.01
"""

import argparse

import numpy as np

from ilpdecoder import Decoder


def parse_dem(dem):
    """Parse a Stim DEM into ILP matrices without solving."""
    decoder = Decoder()
    return decoder._parse_dem(dem, merge_parallel=True, flatten_dem=True)


def count_caret_lines(dem_text):
    """Count error lines that use the '^' separator."""
    count = 0
    example = None
    for line in dem_text.splitlines():
        if line.startswith("error") and "^" in line:
            count += 1
            if example is None:
                example = line
    return count, example


def main():
    parser = argparse.ArgumentParser(
        description="Compare ILP parsing for decompose_errors True vs False."
    )
    parser.add_argument("--distance", type=int, default=3)
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--noise", type=float, default=0.01)
    args = parser.parse_args()

    try:
        import stim
    except Exception as exc:
        raise SystemExit("stim is required (pip install stim)") from exc

    circuit = stim.Circuit.generated(
        "color_code:memory_xyz",
        distance=args.distance,
        rounds=args.rounds,
        after_clifford_depolarization=args.noise,
    )

    dem_true = circuit.detector_error_model(decompose_errors=True)
    dem_false = circuit.detector_error_model(decompose_errors=False)

    text_true = str(dem_true)
    text_false = str(dem_false)
    caret_true, example_true = count_caret_lines(text_true)
    caret_false, example_false = count_caret_lines(text_false)

    H_true, obs_true, w_true = parse_dem(dem_true)
    H_false, obs_false, w_false = parse_dem(dem_false)

    print(
        "color_code:memory_xyz distance={distance} rounds={rounds} noise={noise}".format(
            distance=args.distance, rounds=args.rounds, noise=args.noise
        )
    )
    print("DEM errors (stim): true={true} false={false}".format(
        true=dem_true.num_errors, false=dem_false.num_errors
    ))
    print("caret lines: true={true} false={false}".format(
        true=caret_true, false=caret_false
    ))
    if example_true:
        print("example with '^' (true):", example_true)
    if example_false:
        print("example with '^' (false):", example_false)

    print("ILP H shapes: true={true} false={false}".format(
        true=H_true.shape, false=H_false.shape
    ))
    print("ILP obs shapes: true={true} false={false}".format(
        true=obs_true.shape, false=obs_false.shape
    ))
    if H_true.shape == H_false.shape:
        diff_h = np.count_nonzero(H_true != H_false)
        print("H differs at {count} entries".format(count=diff_h))
    else:
        print("H shapes differ")

    if w_true.shape == w_false.shape:
        diff_w = np.count_nonzero(np.abs(w_true - w_false) > 1e-12)
        max_diff = float(np.max(np.abs(w_true - w_false)))
        print("weights differ at {count} entries (max diff {max_diff:.3e})".format(
            count=diff_w, max_diff=max_diff
        ))
    else:
        print("weights shapes differ")


if __name__ == "__main__":
    main()
