from collections import Counter
from pathlib import Path

from ingestion.raw import read_logs
from process.geolocation import load_locations
from process.extract_transform import extract
from serving.dashboard import show

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / 'data'


def main() -> None:
    events = extract(read_logs(DATA_DIR))
    totals = Counter()
    ips = Counter()
    users = Counter()

    for event in events:
        count = event['count']
        totals[event['event']] += count
        if event['event'] in ('FAILED', 'INVALID'):
            ips[event['ip']] += count
            users[event['user']] += count

    print(f'{len(events)} événements SSH analysés')
    print(f"Échecs de connexion : {totals['FAILED']}")
    print(f"Utilisateurs inconnus : {totals['INVALID']}")
    print(f"Connexions réussies : {totals['ACCEPTED']}")

    print('\nAdresses IP les plus actives :')
    for ip, count in ips.most_common(10):
        print(f'  {ip:<40} {count}')

    print('\nUtilisateurs les plus ciblés :')
    for user, count in users.most_common(10):
        print(f'  {user:<20} {count}')

    locations = load_locations(
        [ip for ip, _ in ips.most_common()],
        DATA_DIR / 'ip_locations.json',
    )
    located_count = sum(ip in locations for ip in ips)
    print(f'\nAdresses IP géolocalisées : {located_count}/{len(ips)}')
    if located_count < len(ips):
        print('Les autres IP seront traitées lors des prochains lancements.')

    show(events, locations)


if __name__ == '__main__':
    main()
