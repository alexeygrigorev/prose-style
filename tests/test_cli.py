"""Tests for the command-line interface."""

import sys

from stylint.cli import main


def test_cli_lists_style_guide_paths(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["stylint", "--style-guide"])

    assert main() == 0

    output = capsys.readouterr().out
    assert "voice:" in output
    assert "polish:" in output


def test_cli_prints_one_style_guide(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["stylint", "--style-guide", "voice"])

    assert main() == 0

    output = capsys.readouterr().out
    assert output.startswith("# ")


def test_cli_rejects_unknown_style_guide(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["stylint", "--style-guide", "missing"])

    assert main() == 2

    err = capsys.readouterr().err
    assert "Unknown style guide" in err
    assert "voice, formatting, code-style, polish" in err


def test_cli_prints_agents_checklist(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["stylint", "--agents"])

    assert main() == 0

    output = capsys.readouterr().out
    assert output.startswith("Use this before and after editing technical text.")
    assert "stylint --style-guide voice" in output


def test_cli_help_points_agents_to_checklist(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["stylint", "--help"])

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 0

    output = capsys.readouterr().out
    assert "Agent workflow" in output
    assert "stylint --agents" in output
