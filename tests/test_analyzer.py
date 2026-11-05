import json
from src.analyzer import analyze


def test_alert(tmp_path):
    file = tmp_path / 'logs.jsonl'
    entries = [
        {'timestamp': '2026-01-01T00:00:00Z', 'service': 'ingest', 'level': 'INFO'},
        {'timestamp': '2026-01-01T00:00:01Z', 'service': 'ingest', 'level': 'ERROR'},
    ]
    file.write_text('\n'.join(json.dumps(e) for e in entries))
    report = analyze(file, 0.2)
    assert report['alert'] is True
    assert report['error_rate'] == 0.5


def test_invalid_entries(tmp_path):
    file = tmp_path / 'logs.jsonl'
    file.write_text('not json\n')
    report = analyze(file)
    assert report['valid_entries'] == 0
    assert report['invalid_entries'] == 1
    assert report['alert'] is False


def test_invalid_threshold(tmp_path):
    import pytest
    with pytest.raises(ValueError):
        analyze(tmp_path / 'none', 2)
