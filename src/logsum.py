import csv
import sys
import argparse
from collections import defaultdict
from datetime import datetime
from pathlib import Path


def parse_iso8601(timestamp_str: str) -> datetime | None:
    """Parse ISO 8601 timestamp, returning None if invalid."""
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None


def normalize_level(level: str) -> str | None:
    """Normalize level to uppercase. Return None if empty."""
    level = level.strip()
    if not level:
        return None
    return level.upper()


def normalize_message(message: str) -> str:
    """Strip leading/trailing whitespace from message."""
    return message.strip()


def process_events(input_path: str, output_path: str) -> int:
    """Read events, group them, and write summary. Return exit code."""
    try:
        input_file = Path(input_path)
        if not input_file.exists():
            print(f"Error: Input file not found: {input_path}", file=sys.stderr)
            return 1
        
        # Group events by (level, service, message)
        groups = defaultdict(lambda: {'count': 0, 'first_seen': None, 'last_seen': None})
        
        try:
            with open(input_file, 'r', newline='', encoding='utf-8') as infile:
                reader = csv.DictReader(infile)
                
                for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                    timestamp_str = row.get('timestamp', '').strip()
                    level = normalize_level(row.get('level', ''))
                    service = row.get('service', '').strip()
                    message = normalize_message(row.get('message', ''))
                    
                    # Validate timestamp
                    timestamp = parse_iso8601(timestamp_str)
                    if timestamp is None:
                        print(f"Warning: Row {row_num}: Malformed timestamp '{timestamp_str}'", file=sys.stderr)
                        continue
                    
                    # Validate level
                    if level is None:
                        print(f"Warning: Row {row_num}: Missing or empty level", file=sys.stderr)
                        continue
                    
                    # Group key
                    key = (level, service, message)
                    group = groups[key]
                    
                    group['count'] += 1
                    if group['first_seen'] is None or timestamp < group['first_seen']:
                        group['first_seen'] = timestamp
                    if group['last_seen'] is None or timestamp > group['last_seen']:
                        group['last_seen'] = timestamp
        
        except IOError as e:
            print(f"Error reading input file: {e}", file=sys.stderr)
            return 1
        
        # Write output
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=['level', 'service', 'message', 'count', 'first_seen', 'last_seen'])
                writer.writeheader()
                
                for (level, service, message), group in sorted(groups.items()):
                    writer.writerow({
                        'level': level,
                        'service': service,
                        'message': message,
                        'count': group['count'],
                        'first_seen': group['first_seen'].isoformat(),
                        'last_seen': group['last_seen'].isoformat(),
                    })
        
        except IOError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
        
        return 0
    
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


def main():
    parser = argparse.ArgumentParser(description='Group identical events from a CSV and generate a summary.')
    parser.add_argument('--input', required=True, help='Path to the input events.csv file')
    parser.add_argument('--output', required=True, help='Path to the output summary.csv file')
    
    args = parser.parse_args()
    
    return process_events(args.input, args.output)


if __name__ == '__main__':
    sys.exit(main())
