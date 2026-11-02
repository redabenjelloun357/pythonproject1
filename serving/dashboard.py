from collections import Counter
from datetime import datetime

import matplotlib.pyplot as plt


def show(events: list[dict], locations: dict[str, dict]) -> None:
    totals = Counter()
    by_day = {}
    by_hour = Counter()
    ips = Counter()
    users = Counter()
    countries = Counter()

    for event in events:
        count = event['count']
        kind = event['event']
        totals[kind] += count
        day = event['happened_at'].rsplit(' ', 1)[0]
        by_day.setdefault(day, Counter())[kind] += count
        by_hour[int(event['happened_at'].rsplit(' ', 1)[1].split(':')[0])] += count

        if kind in ('FAILED', 'INVALID'):
            ips[event['ip']] += count
            users[(event['user'], kind)] += count
            location = locations.get(event['ip'])
            if location:
                countries[location['country']] += count

    figure, axes = plt.subplots(2, 3, figsize=(18, 10))
    figure.suptitle(
        f"Analyse des connexions SSH — {sum(totals.values())} tentatives",
        fontsize=15,
    )

    outcome_labels = ('Échec', 'Utilisateur inconnu', 'Accepté')
    outcome_values = [totals['FAILED'], totals['INVALID'], totals['ACCEPTED']]
    if sum(outcome_values):
        axes[0, 0].pie(
            outcome_values,
            labels=outcome_labels,
            autopct=lambda percent: f'{percent:.1f}%' if percent > 1 else '',
            colors=('tomato', 'gold', 'mediumseagreen'),
            startangle=90,
        )
    axes[0, 0].set_title('Résultat des connexions')

    day_names = sorted(
        by_day,
        key=lambda day: datetime.strptime(day, '%b %d'),
    )
    axes[0, 1].bar(
        day_names,
        [by_day[day]['FAILED'] for day in day_names],
        label='Échec',
        color='tomato',
    )
    axes[0, 1].bar(
        day_names,
        [by_day[day]['INVALID'] for day in day_names],
        bottom=[by_day[day]['FAILED'] for day in day_names],
        label='Utilisateur inconnu',
        color='gold',
    )
    axes[0, 1].set_title('Tentatives par jour')
    axes[0, 1].tick_params(axis='x', rotation=45)
    axes[0, 1].legend()

    axes[0, 2].bar(range(24), [by_hour[hour] for hour in range(24)], color='slateblue')
    axes[0, 2].set_xticks(range(0, 24, 2))
    axes[0, 2].set_title('Tentatives par heure')
    axes[0, 2].set_xlabel('Heure')

    top_ips = ips.most_common(10)
    axes[1, 0].barh(
        [f"{ip} [{locations.get(ip, {}).get('country', 'Inconnu')}]" for ip, _ in top_ips],
        [count for _, count in top_ips],
        color='indianred',
    )
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_title('Principales adresses IP')

    top_countries = countries.most_common(10)
    axes[1, 1].barh(
        [country for country, _ in top_countries],
        [count for _, count in top_countries],
        color='teal',
    )
    axes[1, 1].invert_yaxis()
    axes[1, 1].set_title('Tentatives par pays géolocalisé')

    top_users = users.most_common(10)
    axes[1, 2].barh(
        [f'{user} ({kind.lower()})' for (user, kind), _ in top_users],
        [count for _, count in top_users],
        color=['tomato' if kind == 'FAILED' else 'gold' for (user, kind), _ in top_users],
    )
    axes[1, 2].invert_yaxis()
    axes[1, 2].set_title('Utilisateurs les plus ciblés')

    for axis in (axes[0, 1], axes[0, 2], axes[1, 0], axes[1, 1], axes[1, 2]):
        axis.grid(axis='x', alpha=0.25)
    figure.tight_layout()
    plt.show()
