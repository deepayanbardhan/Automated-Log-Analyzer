# Automated JSONL Log Analyzer

A dependency-free Python CLI that summarizes structured service logs, handles malformed lines, and returns an alert exit code for CI or cron jobs.

## Quick start

```bash
python -m src.analyzer samples/robot-service.jsonl --threshold 0.2 --output report.json
```

The sample contains 2 errors out of 5 valid entries (40%), so the CLI exits with code `2` to signal an alert. This is expected. Use `--threshold 0.5` to get exit code `0`.

## Exit codes

- `0`: success, no threshold breach
- `1`: invalid arguments, unreadable file, or other processing error
- `2`: error rate exceeds threshold

## Test

```bash
python -m pip install pytest==8.3.4 ruff==0.9.2
ruff check src tests
pytest -q
```

## Input schema

One JSON object per line, with timezone-aware ISO-8601 `timestamp`, `service`, and `level` fields. `ERROR` and `CRITICAL` count as errors. Malformed lines are counted but excluded from the error-rate denominator. The threshold is strict (`>`).

## Automation example

```bash
python -m src.analyzer /var/log/myservice.jsonl --threshold 0.1 --output report.json
status=$?
if [ "$status" -eq 2 ]; then echo "Error-rate alert"; fi
exit "$status"
```

## Future improvements

Add sliding windows, per-service thresholds, Slack notifications, and streaming inputs.
