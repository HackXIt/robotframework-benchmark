"""
Tests for the CLI entry point.
"""

from __future__ import annotations

import json
import io

import pytest

from robotframework_benchmark.cli import main


class TestCLI:
    def test_no_command_returns_nonzero(self) -> None:
        assert main([]) != 0

    def test_list_command_runs(self, capsys: pytest.CaptureFixture) -> None:
        rc = main(["list"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "parsing" in out
        assert "execution" in out
        assert "model" in out
        assert "memory" in out

    def test_run_parsing_console(self, capsys: pytest.CaptureFixture) -> None:
        rc = main(["run", "--suite", "parsing"])
        assert rc == 0
        out = capsys.readouterr().out
        assert "parse" in out.lower()

    def test_run_all_json(self, capsys: pytest.CaptureFixture) -> None:
        rc = main(["run", "--suite", "parsing", "--format", "json"])
        assert rc == 0
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "name" in data[0]
        assert "mean_ms" in data[0]
