"""
Pytest tests for logsum CLI tool.

Tests cover:
1. Grouping identical events
2. Level normalization (case conversion)
3. Message normalization (whitespace stripping)
4. Timestamp aggregation (first_seen, last_seen)
5. Count aggregation
6. Missing level handling (skip + stderr warning)
7. Malformed timestamp handling (skip + stderr warning)
8. Empty input file handling
9. Header-only input file handling
10. Missing input file (exit code 1)
11. CLI argument parsing
12. Exit code 0 on success
"""

import csv
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Fixture providing a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def events_csv_basic(temp_dir):
    """Fixture creating a basic events.csv with 3 identical events and 1 different."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:00:00Z", "level": "INFO", "service": "web", "message": "User login"},
            {"timestamp": "2026-07-09T10:05:00Z", "level": "INFO", "service": "web", "message": "User login"},
            {"timestamp": "2026-07-09T10:10:00Z", "level": "INFO", "service": "web", "message": "User login"},
            {"timestamp": "2026-07-09T10:15:00Z", "level": "ERROR", "service": "db", "message": "Connection failed"},
        ])
    return csv_path


@pytest.fixture
def events_csv_level_normalization(temp_dir):
    """Fixture for testing level case normalization."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:00:00Z", "level": "info", "service": "web", "message": "test"},
            {"timestamp": "2026-07-09T10:05:00Z", "level": "INFO", "service": "web", "message": "test"},
            {"timestamp": "2026-07-09T10:10:00Z", "level": "InFo", "service": "web", "message": "test"},
        ])
    return csv_path


@pytest.fixture
def events_csv_message_normalization(temp_dir):
    """Fixture for testing message whitespace stripping."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:00:00Z", "level": "INFO", "service": "web", "message": "  message  "},
            {"timestamp": "2026-07-09T10:05:00Z", "level": "INFO", "service": "web", "message": "message"},
            {"timestamp": "2026-07-09T10:10:00Z", "level": "INFO", "service": "web", "message": "\tmessage\n"},
        ])
    return csv_path


@pytest.fixture
def events_csv_with_missing_level(temp_dir):
    """Fixture with rows having empty level field."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:00:00Z", "level": "INFO", "service": "web", "message": "valid"},
            {"timestamp": "2026-07-09T10:05:00Z", "level": "", "service": "web", "message": "missing level"},
            {"timestamp": "2026-07-09T10:10:00Z", "level": "WARN", "service": "web", "message": "another valid"},
        ])
    return csv_path


@pytest.fixture
def events_csv_with_malformed_timestamp(temp_dir):
    """Fixture with malformed timestamps."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:00:00Z", "level": "INFO", "service": "web", "message": "valid"},
            {"timestamp": "not-a-date", "level": "ERROR", "service": "web", "message": "bad timestamp"},
            {"timestamp": "2026/07/09 10:00:00", "level": "WARN", "service": "web", "message": "wrong format"},
            {"timestamp": "2026-07-09T10:05:00Z", "level": "INFO", "service": "web", "message": "valid"},
        ])
    return csv_path


@pytest.fixture
def events_csv_empty(temp_dir):
    """Fixture for empty CSV (only header)."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
    return csv_path


@pytest.fixture
def events_csv_timestamp_aggregation(temp_dir):
    """Fixture for testing first_seen and last_seen aggregation."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:30:00Z", "level": "INFO", "service": "web", "message": "event"},
            {"timestamp": "2026-07-09T10:00:00Z", "level": "INFO", "service": "web", "message": "event"},
            {"timestamp": "2026-07-09T10:15:00Z", "level": "INFO", "service": "web", "message": "event"},
        ])
    return csv_path


@pytest.fixture
def events_csv_mixed_grouping(temp_dir):
    """Fixture with multiple groups for comprehensive testing."""
    csv_path = temp_dir / "events.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "level", "service", "message"])
        writer.writeheader()
        writer.writerows([
            {"timestamp": "2026-07-09T10:00:00Z", "level": "INFO", "service": "web", "message": "User login"},
            {"timestamp": "2026-07-09T10:05:00Z", "level": "info", "service": "web", "message": "User login"},
            {"timestamp": "2026-07-09T10:10:00Z", "level": "INFO", "service": "web", "message": "  User login  "},
            {"timestamp": "2026-07-09T10:15:00Z", "level": "ERROR", "service": "db", "message": "Connection failed"},
            {"timestamp": "2026-07-09T10:20:00Z", "level": "error", "service": "db", "message": "Connection failed"},
            {"timestamp": "2026-07-09T10:25:00Z", "level": "WARN", "service": "api", "message": "  Rate limit  "},
        ])
    return csv_path


def read_summary_csv(path):
    """Helper to read summary.csv and return rows."""
    rows = []
    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def run_logsum(input_path, output_path):
    """Helper to run logsum CLI."""
    result = subprocess.run(
        [sys.executable, "-m", "src.logsum", "--input", str(input_path), "--output", str(output_path)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True,
    )
    return result


class TestGroupingIdenticalEvents:
    """Test 1: Grouping identical events."""

    def test_groups_identical_events(self, events_csv_basic, temp_dir):
        """Events with identical level, service, and message are grouped."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_basic, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 2
        
        info_group = next((r for r in rows if r["count"] == "3"), None)
        assert info_group is not None
        assert info_group["level"] == "INFO"
        assert info_group["service"] == "web"
        assert info_group["message"] == "User login"


class TestLevelNormalization:
    """Test 2: Level normalization (case conversion)."""

    def test_level_case_insensitive_grouping(self, events_csv_level_normalization, temp_dir):
        """Events with different case levels are grouped together and normalized to uppercase."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_level_normalization, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 1
        assert rows[0]["level"] == "INFO"
        assert rows[0]["count"] == "3"


class TestMessageNormalization:
    """Test 3: Message normalization (whitespace stripping)."""

    def test_message_whitespace_stripped(self, events_csv_message_normalization, temp_dir):
        """Messages with leading/trailing whitespace are normalized for grouping."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_message_normalization, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 1
        assert rows[0]["message"] == "message"
        assert rows[0]["count"] == "3"


class TestTimestampAggregation:
    """Test 4: Timestamp aggregation (first_seen, last_seen)."""

    def test_first_seen_is_earliest_timestamp(self, events_csv_timestamp_aggregation, temp_dir):
        """first_seen contains the earliest timestamp in the group."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_timestamp_aggregation, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 1
        assert rows[0]["first_seen"] in ["2026-07-09T10:00:00Z", "2026-07-09T10:00:00+00:00"]

    def test_last_seen_is_latest_timestamp(self, events_csv_timestamp_aggregation, temp_dir):
        """last_seen contains the latest timestamp in the group."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_timestamp_aggregation, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 1
        assert rows[0]["last_seen"] in ["2026-07-09T10:30:00Z", "2026-07-09T10:30:00+00:00"]


class TestCountAggregation:
    """Test 5: Count aggregation."""

    def test_count_reflects_group_size(self, events_csv_basic, temp_dir):
        """count field shows the number of events in the group."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_basic, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        counts = sorted([int(r["count"]) for r in rows])
        assert counts == [1, 3]


class TestMissingLevelHandling:
    """Test 6: Missing level handling (skip + stderr warning)."""

    def test_skips_rows_with_empty_level(self, events_csv_with_missing_level, temp_dir):
        """Rows with empty level field are skipped."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_with_missing_level, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 2

    def test_stderr_warning_for_missing_level(self, events_csv_with_missing_level, temp_dir):
        """stderr contains warning for rows with missing level."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_with_missing_level, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        assert "level" in result.stderr.lower() or "empty" in result.stderr.lower() or "skip" in result.stderr.lower()


class TestMalformedTimestampHandling:
    """Test 7: Malformed timestamp handling (skip + stderr warning)."""

    def test_skips_rows_with_malformed_timestamp(self, events_csv_with_malformed_timestamp, temp_dir):
        """Rows with malformed timestamps are skipped."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_with_malformed_timestamp, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 1
        assert rows[0]["count"] == "2"

    def test_stderr_warning_for_malformed_timestamp(self, events_csv_with_malformed_timestamp, temp_dir):
        """stderr contains warning for rows with malformed timestamps."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_with_malformed_timestamp, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        assert "timestamp" in result.stderr.lower() or "skip" in result.stderr.lower()


class TestEmptyInputHandling:
    """Test 8: Empty input file handling."""

    def test_empty_input_creates_header_only_output(self, events_csv_empty, temp_dir):
        """Empty input file (only header) creates output with header only."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_empty, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 0

    def test_output_has_correct_headers(self, events_csv_empty, temp_dir):
        """Output CSV has correct header columns."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_empty, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        
        with open(output_path, "r") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
        expected_headers = ["level", "service", "message", "count", "first_seen", "last_seen"]
        assert headers == expected_headers


class TestHeaderOnlyInputHandling:
    """Test 9: Header-only input file handling (same as Test 8)."""

    def test_header_only_input_creates_header_only_output(self, events_csv_empty, temp_dir):
        """Header-only input file creates output with header only."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_empty, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        
        with open(output_path, "r") as f:
            content = f.read().strip()
        
        lines = content.split("\n")
        assert len(lines) == 1


class TestMissingInputFileHandling:
    """Test 10: Missing input file (exit code 1)."""

    def test_missing_input_file_exit_code_1(self, temp_dir):
        """Missing input file results in exit code 1."""
        nonexistent_input = temp_dir / "nonexistent.csv"
        output_path = temp_dir / "summary.csv"
        
        result = run_logsum(nonexistent_input, output_path)
        
        assert result.returncode == 1, "Expected exit code 1 for missing input file"


class TestCLIArgumentParsing:
    """Test 11: CLI argument parsing."""

    def test_requires_input_argument(self, temp_dir):
        """CLI requires --input argument."""
        output_path = temp_dir / "summary.csv"
        
        result = subprocess.run(
            [sys.executable, "-m", "src.logsum", "--output", str(output_path)],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode != 0

    def test_requires_output_argument(self, events_csv_basic, temp_dir):
        """CLI requires --output argument."""
        result = subprocess.run(
            [sys.executable, "-m", "src.logsum", "--input", str(events_csv_basic)],
            cwd=Path(__file__).parent.parent,
            capture_output=True,
            text=True,
        )
        
        assert result.returncode != 0

    def test_accepts_input_and_output_arguments(self, events_csv_basic, temp_dir):
        """CLI accepts --input and --output arguments."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_basic, output_path)
        
        assert result.returncode == 0


class TestExitCode0OnSuccess:
    """Test 12: Exit code 0 on success."""

    def test_exit_code_0_on_success(self, events_csv_basic, temp_dir):
        """CLI returns exit code 0 on successful execution."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_basic, output_path)
        
        assert result.returncode == 0

    def test_exit_code_0_with_empty_input(self, events_csv_empty, temp_dir):
        """CLI returns exit code 0 even with empty input."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_empty, output_path)
        
        assert result.returncode == 0

    def test_exit_code_0_with_warnings(self, events_csv_with_missing_level, temp_dir):
        """CLI returns exit code 0 even when warnings are issued."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_with_missing_level, output_path)
        
        assert result.returncode == 0


class TestIntegration:
    """Integration tests combining multiple features."""

    def test_mixed_grouping_scenario(self, events_csv_mixed_grouping, temp_dir):
        """Complex scenario with multiple groups and normalizations."""
        output_path = temp_dir / "summary.csv"
        result = run_logsum(events_csv_mixed_grouping, output_path)
        
        assert result.returncode == 0, f"logsum failed: {result.stderr}"
        rows = read_summary_csv(output_path)
        
        assert len(rows) == 3
        
        counts = sorted([int(r["count"]) for r in rows])
        assert counts == [1, 2, 3]
        
        for row in rows:
            assert row["level"] == row["level"].upper()

    def test_output_file_created(self, events_csv_basic, temp_dir):
        """Output file is created if it doesn't exist."""
        output_path = temp_dir / "new_summary.csv"
        
        assert not output_path.exists()
        result = run_logsum(events_csv_basic, output_path)
        
        assert result.returncode == 0
        assert output_path.exists()

    def test_output_file_overwritten(self, events_csv_basic, temp_dir):
        """Output file is overwritten if it already exists."""
        output_path = temp_dir / "summary.csv"
        
        output_path.write_text("old content")
        
        result = run_logsum(events_csv_basic, output_path)
        
        assert result.returncode == 0
        rows = read_summary_csv(output_path)
        assert len(rows) == 2
