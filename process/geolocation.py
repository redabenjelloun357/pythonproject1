import ipaddress
import json
import logging
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

URL = 'https://ipwho.is/{}'
MAX_LOOKUPS_PER_RUN = 40



def _lookup(ip: str) -> dict | None:
    url = URL.format(quote(ip, safe=''))
    request = Request(url, headers={'User-Agent': 'SSHLogAnalyser/1.0'})
    try:
        with urlopen(request, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
    except HTTPError as error:
        if error.code == 429:
            raise GeolocationRateLimitError('limite de requêtes atteinte') from error
        logging.warning('Géolocalisation impossible pour %s : %s', ip, error)
        return None
    except (URLError, TimeoutError, UnicodeDecodeError, json.JSONDecodeError) as error:
        logging.warning('Géolocalisation impossible pour %s : %s', ip, error)
        return None

    if not isinstance(data, dict) or not data.get('success'):
        logging.warning('Réponse de géolocalisation invalide pour %s', ip)
        return None
    connection = data.get('connection')
    return {
        'country': data.get('country') or 'Inconnu',
        'city': data.get('city'),
        'org': connection.get('org') if isinstance(connection, dict) else None,
    }


def load_locations(
    ips: list[str],
    cache_file: str | Path,
    limit: int = MAX_LOOKUPS_PER_RUN,
) -> dict[str, dict]:
    if limit < 0:
        raise ValueError('limit doit être positif ou nul')

    cache_path = Path(cache_file)
    if cache_path.exists():
        cached = json.loads(cache_path.read_text(encoding='utf-8'))
        if not isinstance(cached, dict):
            raise ValueError(f'Cache de géolocalisation invalide : {cache_path}')
    else:
        cached = {}

    uncached = []
    for ip in ips:
        try:
            address = ipaddress.ip_address(ip)
        except ValueError:
            logging.warning('Adresse IP ignorée car invalide : %s', ip)
            continue
        if address.is_global and ip not in cached and ip not in uncached:
            uncached.append(ip)

    for index, ip in enumerate(uncached[:limit]):
        try:
            location = _lookup(ip)
        except GeolocationRateLimitError as error:
            logging.warning('Géolocalisation interrompue : %s', error)
            break
        if location:
            cached[ip] = location
        if index < min(len(uncached), limit) - 1:
            time.sleep(1)

    if cached:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(
            json.dumps(cached, ensure_ascii=False, indent=2),
            encoding='utf-8',
        )
    return cached
