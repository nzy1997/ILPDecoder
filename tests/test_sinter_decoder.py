"""Tests for the sinter adapter."""

import numpy as np
import pytest

from ilpqec import get_available_solvers


def _require_sinter_and_stim():
    pytest.importorskip("sinter")
    return pytest.importorskip("stim")


def _require_highs():
    if "highs" not in get_available_solvers():
        pytest.skip("HiGHS solver not available")


def test_sinter_compiled_decoder_bit_packed_roundtrip():
    _require_highs()
    stim = _require_sinter_and_stim()
    from ilpqec.sinter_decoder import SinterIlpDecoder

    dem = stim.DetectorErrorModel("error(0.1) D0 L0")
    decoder = SinterIlpDecoder()
    compiled = decoder.compile_decoder_for_dem(dem=dem)

    shots = np.array([[1], [0], [1]], dtype=np.uint8)
    bit_packed = np.packbits(shots, axis=1, bitorder="little")
    predictions = compiled.decode_shots_bit_packed(
        bit_packed_detection_event_data=bit_packed
    )

    pred_bits = np.unpackbits(predictions, axis=1, bitorder="little")[:, 0:1]
    np.testing.assert_array_equal(pred_bits, shots)


def test_sinter_compiled_decoder_bit_packed_no_detectors():
    _require_highs()
    stim = _require_sinter_and_stim()
    from ilpqec.sinter_decoder import SinterIlpDecoder

    dem = stim.DetectorErrorModel("error(0.1) L0")
    decoder = SinterIlpDecoder()
    compiled = decoder.compile_decoder_for_dem(dem=dem)

    bit_packed = np.zeros((4, 0), dtype=np.uint8)
    predictions = compiled.decode_shots_bit_packed(
        bit_packed_detection_event_data=bit_packed
    )

    assert predictions.shape == (4, 1)
    assert predictions.dtype == np.uint8
    assert not predictions.any()


def test_sinter_decode_via_files(tmp_path):
    _require_highs()
    stim = _require_sinter_and_stim()
    from ilpqec.sinter_decoder import SinterIlpDecoder

    dem = stim.DetectorErrorModel("error(0.1) D0 L0")
    dem_path = tmp_path / "model.dem"
    dets_path = tmp_path / "dets.b8"
    obs_path = tmp_path / "obs.b8"
    dem.to_file(dem_path)

    shots = np.array([[0], [1], [1], [0]], dtype=np.uint8)
    stim.write_shot_data_file(
        data=shots, path=dets_path, format="b8", num_detectors=1
    )

    decoder = SinterIlpDecoder()
    decoder.decode_via_files(
        num_shots=shots.shape[0],
        num_dets=1,
        num_obs=1,
        dem_path=dem_path,
        dets_b8_in_path=dets_path,
        obs_predictions_b8_out_path=obs_path,
        tmp_dir=tmp_path,
    )

    predictions = stim.read_shot_data_file(
        path=obs_path, format="b8", num_observables=1
    )
    np.testing.assert_array_equal(predictions, shots)


def test_sinter_decode_via_files_no_detectors(tmp_path):
    _require_highs()
    stim = _require_sinter_and_stim()
    from ilpqec.sinter_decoder import SinterIlpDecoder

    dem = stim.DetectorErrorModel("")
    dem_path = tmp_path / "model.dem"
    dets_path = tmp_path / "dets.b8"
    obs_path = tmp_path / "obs.b8"
    dem.to_file(dem_path)
    dets_path.write_bytes(b"")

    decoder = SinterIlpDecoder()
    decoder.decode_via_files(
        num_shots=3,
        num_dets=0,
        num_obs=9,
        dem_path=dem_path,
        dets_b8_in_path=dets_path,
        obs_predictions_b8_out_path=obs_path,
        tmp_dir=tmp_path,
    )

    predictions = stim.read_shot_data_file(
        path=obs_path, format="b8", num_observables=9
    )
    assert predictions.shape == (3, 9)
    assert not predictions.any()


def test_sinter_collect_end_to_end():
    _require_highs()
    stim = _require_sinter_and_stim()
    import sinter

    from ilpqec.sinter_decoder import SinterIlpDecoder

    circuit = stim.Circuit.generated(
        "repetition_code:memory",
        distance=3,
        rounds=3,
        before_round_data_depolarization=0.01,
    )
    dem = circuit.detector_error_model(decompose_errors=True)
    task = sinter.Task(circuit=circuit, decoder="ilp", detector_error_model=dem)
    stats = sinter.collect(
        num_workers=1,
        tasks=[task],
        max_shots=5,
        custom_decoders={"ilp": SinterIlpDecoder()},
    )

    assert len(stats) == 1
    assert stats[0].shots > 0
