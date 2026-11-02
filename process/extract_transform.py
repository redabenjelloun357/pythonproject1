import re

LINE = re.compile(
    r'^(?P<month>[A-Za-z]{3})\s+(?P<day>\d{1,2})\s+'
    r'(?P<time>\d{2}:\d{2}:\d{2})\s+\S+\s+sshd\[\d+\]:\s*(?P<message>.*)$'
)
IP = r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3}|[0-9A-Fa-f:]+)'

EVENTS = [
    ('FAILED', re.compile(
        rf'Failed \w+ for (?:invalid user )?(?P<user>\S*) from {IP} port (?P<port>\d+)'
    )),
    ('ACCEPTED', re.compile(
        rf'Accepted \w+ for (?P<user>\S+) from {IP} port (?P<port>\d+)'
    )),
    ('INVALID', re.compile(
        rf'Invalid user (?P<user>\S*)\s+from {IP}(?: port (?P<port>\d+))?'
    )),
]
REPEATED = re.compile(r'message repeated (\d+) times')


def extract_from_row(row: str) -> dict | None:
    line = LINE.match(row)
    if not line:
        return None
    message = line['message']
    for name, regex in EVENTS:
        found = regex.search(message)
        if found:
            repeated = REPEATED.search(message)
            return {
                'happened_at': f"{line['month']} {line['day']} {line['time']}",
                'event': name,
                'user': found['user'] or '(empty)',
                'ip': found['ip'],
                'port': int(found['port']) if found['port'] else None,
                'count': int(repeated.group(1)) if repeated else 1,
            }
    return None


def extract(rows: list[str]) -> list[dict]:
    return [event for event in map(extract_from_row, rows) if event]
