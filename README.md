# Analyseur de journaux SSH

Ce programme lit les fichiers `auth.log` et `auth.log.*` du dossier `data/`
(y compris les fichiers `.gz`). Il utilise des expressions régulières pour
compter les connexions SSH échouées, les utilisateurs inconnus et les
connexions réussies, puis affiche un tableau de six graphiques.

Les principales IP publiques sont géolocalisées via ipwho.is. Les résultats
sont conservés dans `data/ip_locations.json` pour éviter de refaire les mêmes
requêtes. Jusqu'à 40 nouvelles adresses sont recherchées par lancement ; les
adresses restantes sont traitées aux lancements suivants. Cette fonction
nécessite une connexion Internet.

## Lancer le programme

Avec Python 3.14 ou plus :

```powershell
python main.py
```

Ou avec `uv` :

```powershell
uv run main.py
```

Le programme affiche d'abord un résumé texte, puis ouvre les graphiques.
