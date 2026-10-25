from pathlib import Path

from arc_rgbt import cli, studio


def test_studio_is_packaged_and_local():
    path = Path(studio.resources.files("arc_rgbt").joinpath("studio.html"))
    assert path.is_file()
    document = path.read_text(encoding="utf-8")
    assert "RGB–Thermal Studio" in document
    assert "image/png,image/jpeg,image/webp" in document
    assert 'id="rgb"' in document
    assert 'id="thermal"' in document
    assert 'id="sample"' in document
    assert 'id="clear"' in document
    assert "Try an example" in document
    assert "data.rgb.isDemo && data.thermal.isDemo" in document
    assert "Dimension mismatch" in document
    assert "spatial alignment unverified" in document
    assert "radiometric_calibration:false" in document
    assert "MAX_PIXELS = 4_000_000" in document
    assert "fetch(" not in document
    assert "<script src=" not in document
    assert "https://" not in document
    assert "http://" not in document


def test_studio_no_open_prints_existing_path(capsys, monkeypatch):
    monkeypatch.setattr(studio.webbrowser, "open", lambda *args, **kwargs:
                        (_ for _ in ()).throw(AssertionError("Browser launch forbidden")))
    studio.main(["--no-open"])
    output = capsys.readouterr().out
    assert "RGB–Thermal Studio:" in output
    assert "studio.html" in output


def test_studio_browser_uses_local_file_uri(monkeypatch, capsys):
    urls = []
    monkeypatch.setattr(studio.webbrowser, "open", lambda url, new=0: urls.append(url) or True)
    studio.main([])
    assert len(urls) == 1
    assert urls[0].startswith("file://")
    assert "studio.html" in capsys.readouterr().out


def test_unified_cli_studio_help(capsys):
    import pytest

    with pytest.raises(SystemExit) as error:
        cli.main(["studio", "--help"])
    assert error.value.code == 0
    assert "--no-open" in capsys.readouterr().out
