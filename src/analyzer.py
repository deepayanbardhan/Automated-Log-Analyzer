"""Analyze JSONL service logs and exit nonzero when an error threshold is exceeded."""
import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


def analyze(path: Path, threshold: float = 0.2) -> dict:
    if not 0 <= threshold <= 1:
        raise ValueError('threshold must be between 0 and 1')
    levels = Counter()
    services = Counter()
    invalid = 0
    first = last = None
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                if not isinstance(entry, dict) or not isinstance(entry.get('level'), str) or not isinstance(entry.get('service'), str):
                    raise ValueError('missing level or service')
                timestamp = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                if timestamp.tzinfo is None:
                    raise ValueError('timestamp must include timezone')
                timestamp = timestamp.astimezone(timezone.utc)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError, AttributeError):
                invalid += 1
                continue
            levels[entry['level'].upper()] += 1
            services[entry['service']] += 1
            first = timestamp if first is None else min(first, timestamp)
            last = timestamp if last is None else max(last, timestamp)
    total = sum(levels.values())
    errors = levels['ERROR'] + levels['CRITICAL']
    error_rate = errors / total if total else 0
    return {
        'valid_entries': total, 'invalid_entries': invalid,
        'levels': dict(levels), 'services': dict(services),
        'error_count': errors, 'error_rate': round(error_rate, 4),
        'threshold': threshold, 'alert': bool(total and error_rate > threshold),
        'first_timestamp': first.isoformat() if first else None,
        'last_timestamp': last.isoformat() if last else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', type=Path, help='Input JSONL file')
    parser.add_argument('--threshold', type=float, default=0.2, help='Error rate threshold (0..1)')
    parser.add_argument('--output', type=Path, help='Optional JSON report path')
    args = parser.parse_args()
    try:
        report = analyze(args.file, args.threshold)
        output = json.dumps(report, indent=2)
        print(output)
        if args.output:
            args.output.write_text(output + '\n', encoding='utf-8')
        return 2 if report['alert'] else 0
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
