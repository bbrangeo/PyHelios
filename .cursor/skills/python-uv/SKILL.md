---
name: python-uv
description: Manages Python projects with uv (dependencies, lockfile, venv, scripts, tools). Use when adding packages, running Python, bootstrapping projects, migrating from pip/poetry, or when the user mentions uv, pyproject.toml, or fast Python tooling.
---

# Python avec uv

## Principe

Préférer les commandes **uv** natives (`uv add`, `uv sync`, `uv run`) plutôt que `pip install` dans un venv manuel, dès qu’un `pyproject.toml` / `uv.lock` est présent ou qu’on initialise un projet.

## Décision rapide

| Situation | Action |
|-----------|--------|
| Nouveau projet applicatif | `uv init` (optionnel: `--name`, `--python 3.12`) |
| Dépendance runtime | `uv add <pkg>` |
| Dépendance dev (tests, lint) | `uv add --dev <pkg>` ou `--group dev` selon convention du projet |
| Installer tout depuis le lock | `uv sync` |
| Exécuter sans activer le venv | `uv run python …` ou `uv run pytest` |
| Outil CLI global (ruff, etc.) | `uv tool install <pkg>` |
| Projet legacy sans pyproject | `uv venv` puis `uv pip install -r requirements.txt` si nécessaire |

## Workflow courant

1. **Synchroniser** après `git pull` : `uv sync` (reproduit l’environnement depuis `uv.lock`).
2. **Ajouter une lib** : `uv add requests` → met à jour `pyproject.toml` et `uv.lock`.
3. **Lancer du code** : `uv run python src/main.py` ou entrée `[project.scripts]` si définie.
4. **Tests / qualité** : `uv run pytest`, `uv run ruff check .` (selon ce qui est dans le projet).

## Fichiers à respecter

- **`pyproject.toml`** : source de vérité des métadonnées et des dépendances déclarées.
- **`uv.lock`** : versions résolues — **à versionner** pour des builds reproductibles.
- **`.venv`** : environnement local (souvent ignoré par git) ; uv le crée/maintient près du projet par défaut.

Ne pas suggérer d’éditer `uv.lock` à la main.

## Versions de Python

- Limiter la plage dans `[project] requires-python` (ex. `>=3.11,<3.14`).
- Pour une version précise locale : `uv python install 3.12` puis `uv venv --python 3.12` ou `uv init --python 3.12`.
- Fichier **`.python-version`** : utile avec pyenv ou conventions d’équipe ; aligner avec `requires-python`.

## Groupes de dépendances (optionnel)

Si le projet utilise des groupes (ex. `dependency-groups` ou `[tool.uv]`):

- `uv add --group dev ruff` pour séparer outils de dev.
- `uv sync --all-groups` ou `--group dev` selon le besoin (CI vs local).

Suivre la convention déjà présente dans le `pyproject.toml` du dépôt.

## Scripts et applications

- **Script one-off** : `uv run --with httpx python script.py` pour dépendances ponctuelles sans polluer le projet.
- **PEP 723 inline scripts** : si le script a `# /// script` / metadata deps, `uv run script.py` peut suffire.

## Outils CLI (hors projet)

- `uv tool install <distribution>` installe un binaire isolé (ex. `uv tool install ruff`).
- `uv tool run <cmd>` pour exécuter sans installation persistante si pertinent.

## CI / Docker

- Installer uv puis **`uv sync --frozen`** (ou équivalent strict) pour refuser toute résolution implicite en CI.
- Cacher le répertoire de wheels uv accélère les pipelines.

## Anti-patterns

- Mélanger **`pip install`** dans `.venv` géré par uv et **`uv sync`** sans documenter l’exception → dérive non reflétée dans le lock.
- Commiter des secrets dans `pyproject.toml` ou variables d’environnement en dur.
- Oublier **`uv lock`** / **`uv add`** après changement manuel des deps dans une branche partagée.

## Référence rapide des commandes

```bash
uv init                    # nouveau projet
uv add pandas              # dépendance
uv add --dev pytest        # dev
uv sync                    # installer depuis lock
uv lock                    # régénérer le lock (après édition contrôlée des deps)
uv run python main.py      # exécuter dans l’env du projet
uv tree                    # arbre des dépendances (si disponible / utile)
uv venv                    # créer .venv seul
```

Pour détails ou cas limites (monorepos, workspaces, index privés PyPI), consulter la doc officielle : [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/).
