---
name: data-science-stack
description: Guides exploratory analysis, spatial workflows, SQL analytics, and classical ML using pandas, GeoPandas, DuckDB, and scikit-learn. Use when the user works on EDA, GeoDataFrames, Parquet/GeoParquet, DuckDB queries, or sklearn pipelines on tabular or geospatial data.
---

# Data scientist : pandas, GeoPandas, DuckDB, scikit-learn

## Rôle de chaque brique

| Outil | Rôle principal |
|-------|----------------|
| **pandas** | Tables, types, jointures attributaires, time series, EDA sur données non géométriques ou après extraction d’attributs. |
| **GeoPandas** | `GeoDataFrame`, géométries, CRS, jointures spatiales (`sjoin`), buffers, agrégations par zone. |
| **DuckDB** | Requêtes analytiques rapides, agrégations lourdes, SQL sur Parquet/CSV, pont efficace avec DataFrames pandas enregistrés. |
| **scikit-learn** | Prétraitement, pipelines, modèles tabulaires supervisés/non supervisés, métriques — **sans** dépendance native aux géométries (utiliser des features dérivées). |

## Dépendances (uv)

```bash
uv add pandas geopandas duckdb scikit-learn
```

Sur PyPI le paquet s’appelle `scikit-learn` ; l’import Python est `sklearn`. GeoPandas tire souvent **pyproj** / **shapely** en transitif.

## Chaînage typique

1. **Charger** : `geopandas.read_file(...)` ou `pandas.read_parquet` / DuckDB `read_parquet`.
2. **Harmoniser le CRS** (`to_crs`) avant toute opération spatiale métrique.
3. **Spatiale** : `sjoin`, `overlay`, dissolve — rester dans GeoPandas pour la sémantique géométrique.
4. **Gros volumes / SQL** : écrire en Parquet/GeoParquet si besoin, puis DuckDB pour filtres/agrégations ; ou `con.register("gdf", gdf.drop(columns="geometry"))` pour la partie attributaire pure.
5. **ML** : construire un `pandas.DataFrame` de features (numériques/catégorielles encodées), puis `sklearn.pipeline.Pipeline` + `train_test_split` (ou CV) en veillant à **fit uniquement sur le train**.

Pour publication ou optimisation spatiale en GeoParquet, utiliser la skill projet **geoparquet** (`gpio`).

## DuckDB ↔ pandas

- Requête directe sur fichiers : `duckdb.sql("SELECT ... FROM 'data.parquet' WHERE ...").df()`
- DataFrame en mémoire : enregistrer puis SQL, ou passer via `duckdb.query` selon l’API utilisée dans le projet.
- Préférer DuckDB aux boucles Python pour gros `group by`, fenêtres, jointures massives sur colonnes alignées.

Éviter de dupliquer inutilement des tables énormes : filtrer/projeter en SQL puis ramener un échantillon ou des agrégats.

## GeoPandas : rappels utiles

- Toujours vérifier **`gdf.crs`** ; documenter les reprojections.
- Les jointures spatiales (`sjoin`) produisent souvent des doublons — dédoublonner ou agréger avant ML si une ligne = une entité métier.
- Pour le ML, exporter des colonnes stables (aires, distances, centroïdes, labels de zone) plutôt que des WKB bruts, sauf pipeline spécialisé.

## scikit-learn : discipline

- **`Pipeline`** pour enchaîner imputation, encodage, scaling, modèle — ordre de `fit`/`transform` cohérent.
- **`ColumnTransformer`** quand types mixtes (numérique vs catégoriel).
- Pas de fuite : fit des transformeurs **uniquement** sur les données d’entraînement ; même logique pour toute feature issue d’agrégations temporelles ou spatiales (calculer stats sur train, appliquer au test).

## Anti-patterns

- Mélanger CRS ou unités sans conversion explicite.
- Charger tout un GeoParquet multi-giga en GeoPandas « pour filtrer » — préfiltrer en DuckDB ou par bbox/tuiles.
- `fit` sur tout le jeu avant `train_test_split` pour des transformations qui dépendent de la distribution des labels ou des agrégats globaux.

## Ressources projet

- Données spatiales / GeoParquet : `.cursor/skills/geoparquet/SKILL.md`
- Environnement **uv** : `.cursor/skills/python-uv/SKILL.md`
