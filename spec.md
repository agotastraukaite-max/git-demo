# spec.md

## Goal

To build a command-line interface (CLI) tool that reads a CSV file of synthetic events and generates a summary CSV file grouping identical events.

## Inputs

The input is a CSV file (`events.csv`) with a header row and the following columns:
- `timestamp`: The ISO 8601 timestamp of the event (e.g., `2026-07-09T15:30:00Z`).
- `level`: The event severity (e.g., 'INFO', 'warn').
- `service`: The name of the originating service.
- `message`: The event's description.

## Outputs

The output is a CSV file (`summary.csv`) with a header row and the following columns:
- `level`: The uppercase event severity.
- `service`: The originating service name.
- `message`: The normalized event message.
- `count`: The total number of events in the group.
- `first_seen`: The earliest timestamp for that event group.
- `last_seen`: The latest timestamp for that event group.

## Normalisation Rules

1. **level**: The value from the `level` column is converted to its uppercase equivalent for grouping.
2. **message**: Leading and trailing whitespace is stripped from the `message` for grouping.

## Grouping Rule

Events are grouped together if they share the exact same values for `level` (post-normalisation), `service`, and `message` (post-normalisation).

## Aggregation

For each group, the output row will contain:
- `count`: The total number of events in the group.
- `first_seen`: The minimum (earliest) `timestamp` from all events in the group.
- `last_seen`: The maximum (latest) `timestamp` from all events in the group.

## Edge Cases

- **Empty Input**: If the input file is empty or contains only a header, the output file will be created with only a header row.
- **Malformed Timestamp**: Rows with a `timestamp` that cannot be parsed as ISO 8601 will be skipped. A warning will be printed to `stderr` for each skipped row.
- **Missing Level**: Rows with an empty `level` field will be skipped. A warning will be printed to `stderr` for each skipped row.

## CLI

- **Arguments**:
 - `--input <path>`: Required path to the source `events.csv` file.
 - `--output <path>`: Required path for the destination `summary.csv` file.
- **Exit Codes**:
 - `0`: Success.
 - `1`: Failure (e.g., input file not found, permission denied).

## Out of Scope

- Processing non-CSV file formats.
- Real-time data streaming or monitoring.
- Advanced filtering of events (e.g., by date range, regex).
- Implementation with external dependencies (must use Python 3.11 standard library only).

## Signed off
A.I. - 2026-07-09

Goal. src/logsum.py plus data/sample_events.csv and data/summary.csv, with a sample run matching the spec.
Superpower moment. You can move from spec to running code without accepting an unread diff.

---

## Implementation Notes

**Timestamp ISO 8601 Handling**: The implementation normalizes the 'Z' timezone designator to '+00:00' before parsing with `fromisoformat()`. This is necessary because Python's `fromisoformat()` (3.11) does not accept the 'Z' suffix directly. Output timestamps use the full ISO format with timezone offset (`+00:00`), which preserves timezone info and maintains round-trip compatibility.

**Warning Behavior**: Warnings to `stderr` do not affect the exit code—the tool returns `0` on success even when skipping rows. This allows partial data ingestion with visibility into what was dropped, following the Unix philosophy of "do one thing well" with optional diagnostic output.
