import gzip
from pathlib import Path


def read_logs(path: str | Path) -> list[str]:
    directory = Path(path)
    rows = []
    for file_path in sorted(directory.iterdir()):
        if not file_path.is_file() or not (
            file_path.name == 'auth.log' or file_path.name.startswith('auth.log.')
        ):
            continue
        opener = gzip.open if file_path.suffix == '.gz' else open
        with opener(file_path, mode='rt', encoding='utf-8', errors='replace') as f:
            rows.extend(line.rstrip('\n') for line in f)
    return rows
