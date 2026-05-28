---
name: sql-jinja2-duckdb
description: Remplace les f-strings SQL dynamiques par des templates Jinja2 pour DuckDB. Utiliser quand une requete SQL a des parametres optionnels, des filtres conditionnels, des listes de colonnes, ou quand l'utilisateur mentionne DuckDB, dbt, Jinja2, f-strings SQL, requetes dynamiques, if/for dans SQL.
---

# SQL Jinja2 DuckDB

## Objectif

Ecrire des requetes SQL dynamiques DuckDB dans des templates Jinja2 plutot que dans des f-strings Python.

Principes:
- Garder toute la logique SQL (variables, conditions, boucles) dans le template.
- Garder Python pour preparer le contexte et executer la requete.
- Privilegier des templates lisibles, proches d'un modele dbt.

## Quand appliquer ce skill

Utiliser ce skill si:
- la requete SQL contient des parties optionnelles (`WHERE`, `JOIN`, `ORDER BY`, colonnes);
- du code assemble des morceaux SQL en Python (`+=`, listes de strings, f-strings imbriques);
- l'utilisateur veut un style "comme dbt" avec `{{ ... }}` et `{% ... %}`.

## Workflow recommande

1. Identifier la requete dynamique et ses zones conditionnelles.
2. Creer un template Jinja2 unique qui contient:
   - variables: `{{ variable }}`
   - conditions: `{% if condition %} ... {% endif %}`
   - boucles: `{% for item in items %} ... {% endfor %}`
3. Preparer en Python un dictionnaire `context` avec toutes les valeurs.
4. Rendre le SQL avec Jinja2, puis l'executer via DuckDB.
5. Verifier que le SQL rendu reste valide quand des parametres optionnels sont absents.

## Pattern de base

```python
from jinja2 import Environment, BaseLoader

template = """
select
    id,
    score
    {% if extra_cols %}
    {% for col in extra_cols %}, {{ col }}{% endfor %}
    {% endif %}
from {{ source_table }}
where 1=1
{% if min_score is not none %}
  and score >= {{ min_score }}
{% endif %}
{% if regions %}
  and region in (
    {% for r in regions %}
      '{{ r }}'{% if not loop.last %}, {% endif %}
    {% endfor %}
  )
{% endif %}
"""

context = {
    "source_table": "samples",
    "extra_cols": ["region", "exposure_class"],
    "min_score": 0.35,
    "regions": ["NORD", "SUD"],
}

sql = Environment(loader=BaseLoader(), trim_blocks=True, lstrip_blocks=True)\
    .from_string(template)\
    .render(**context)
```

## Regles de qualite

- Eviter de melanger logique conditionnelle SQL entre template et Python.
- Eviter les concatenations SQL en Python sauf cas trivial.
- Nommer clairement les variables de contexte (`min_score`, `regions`, `date_start`).
- Garder les blocs Jinja2 compacts pour preserver la lisibilite SQL.
- Preferer des templates multiline plutot que des one-liners opaques.

## Anti-patterns

- Construire `WHERE` via `if` Python multiples + concatenation.
- Mettre des morceaux de `JOIN` dans des fonctions Python separees sans necessite.
- Laisser des virgules finales ou `AND` orphelins apres rendu.

## Template de migration f-string -> Jinja2

1. Extraire la requete dans une variable `template_sql`.
2. Remplacer les interpolations f-string par `{{ ... }}`.
3. Deplacer les `if/for` Python qui touchent le SQL vers `{% if %}` et `{% for %}`.
4. Conserver en Python uniquement:
   - calcul des parametres
   - validation/assainissement
   - rendu et execution.

## Checklist rapide

- [ ] Une seule source de verite pour la logique SQL dynamique (template Jinja2)
- [ ] Python ne fait pas d'assemblage SQL conditionnel complexe
- [ ] Le SQL rendu est lisible et executable avec/without parametres optionnels
- [ ] Les noms de variables de contexte sont explicites
