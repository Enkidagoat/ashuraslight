from __future__ import annotations

from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def test_app_renders_defaults_and_calculation_produces_two_plots() -> None:
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    assert not at.exception
    assert at.title[0].value == "Ashura’s Light"
    assert len(at.multiselect[0].options) == 3
    assert len(at.multiselect[0].value) == 2

    at.button[0].click().run()
    assert not at.exception
    assert not at.error
    assert len(at.get("plotly_chart")) == 2


def test_app_requires_two_selected_sites_without_crashing() -> None:
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    at.multiselect[0].set_value([])
    at.button[0].click().run()
    assert not at.exception
    assert any("at least two" in item.value.lower() for item in at.error)


def test_app_can_switch_to_a_different_candidate_pair() -> None:
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    options = list(at.multiselect[0].options)
    at.multiselect[0].set_value([options[1], options[2]])
    at.button[0].click().run()
    assert not at.exception
    assert not at.error
    assert len(at.get("plotly_chart")) == 2


def test_app_shows_actionable_missing_data_error(monkeypatch) -> None:
    missing_dir = Path(__file__).resolve().parent / "does-not-exist-kernels"
    monkeypatch.setenv("ASHURASLIGHT_KERNEL_DIR", str(missing_dir))
    at = AppTest.from_file(str(APP), default_timeout=60).run()
    at.button[0].click().run()
    assert not at.exception
    assert any("provision_kernels.py" in item.value for item in at.error)
