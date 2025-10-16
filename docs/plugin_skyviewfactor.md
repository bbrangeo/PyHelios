# Plugin SkyViewFactor

## Description

Le plugin SkyViewFactor calcule le **facteur de vue du ciel** (Sky View Factor, SVF) pour des points donnés dans une scène 3D. Le facteur de vue du ciel mesure la fraction de la voûte céleste visible depuis un point donné, variant de 0 (complètement confiné) à 1 (complètement dégagé).

## Définition mathématique

Le sky view factor est défini comme :

```
f_sky = (1/π) ∫ V(θ,φ) cos²(θ) dω
```

Où :
- **V(θ,φ)** est la fonction de visibilité (1 si le ciel est visible, 0 si masqué)
- **θ** est l'angle zénithal
- **dω** est l'élément d'angle solide

## Installation

Le plugin SkyViewFactor est inclus dans PyHelios. Pour l'activer, compilez PyHelios avec le plugin :

```bash
python build_scripts/build_helios.py --plugins skyviewfactor
```

## Utilisation de base

### Importation

```python
from pyhelios import Context, SkyViewFactorModel, SkyViewFactorCamera
```

### Création d'un modèle

```python
# Créer un contexte HELIOS
context = Context()

# Créer le modèle SkyViewFactor
svf_model = SkyViewFactorModel(context)
```

### Configuration du modèle

```python
# Définir le nombre de rayons (plus de rayons = plus de précision)
svf_model.set_ray_count(2000)

# Définir la longueur maximale des rayons
svf_model.set_max_ray_length(1000.0)

# Activer/désactiver les messages de console
svf_model.set_message_flag(True)

# Vérifier la disponibilité CUDA/OptiX
print(f"CUDA disponible: {svf_model.is_cuda_available()}")
print(f"OptiX disponible: {svf_model.is_optix_available()}")
```

## Calcul du Sky View Factor

### Calcul pour un point unique

```python
# Calculer le SVF pour un point (accélération GPU)
x, y, z = 0.0, 0.0, 0.0
svf = svf_model.calculate_sky_view_factor(x, y, z)
print(f"SVF au point ({x}, {y}, {z}): {svf:.3f}")

# Calculer le SVF en utilisant l'implémentation CPU
svf_cpu = svf_model.calculate_sky_view_factor_cpu(x, y, z)
print(f"SVF (CPU) au point ({x}, {y}, {z}): {svf_cpu:.3f}")
```

### Calcul pour plusieurs points

```python
# Définir plusieurs points
points = [
    (0.0, 0.0, 0.0),   # Point 1
    (1.0, 0.0, 0.0),   # Point 2
    (0.0, 1.0, 0.0),   # Point 3
    (0.0, 0.0, 1.0)    # Point 4
]

# Calculer les SVF pour tous les points
svfs = svf_model.calculate_sky_view_factors(points)

# Afficher les résultats
for i, (point, svf) in enumerate(zip(points, svfs)):
    print(f"Point {i+1} {point}: SVF = {svf:.3f}")
```

### Calcul pour les centres des primitives

```python
# Calculer le SVF pour tous les centres de primitives
primitive_svfs = svf_model.calculate_sky_view_factors_for_primitives()
print(f"SVF calculés pour {len(primitive_svfs)} primitives")
```

## Visualisation avec caméra

### Création d'une caméra

```python
# Créer une caméra SkyViewFactor
camera = svf_model.create_camera()
```

### Configuration de la caméra

```python
# Position de la caméra
camera.set_position(0.0, 0.0, 10.0)

# Cible de la caméra
camera.set_target(0.0, 0.0, 0.0)

# Vecteur "up" de la caméra
camera.set_up(0.0, 1.0, 0.0)

# Champ de vue en degrés
camera.set_field_of_view(60.0)

# Résolution de l'image
camera.set_resolution(512, 512)

# Nombre de rayons par pixel
camera.set_ray_count(100)

# Longueur maximale des rayons
camera.set_max_ray_length(1000.0)
```

### Rendu et exportation

```python
# Rendre l'image
success = camera.render()
if success:
    print("Rendu réussi!")
    
    # Obtenir les données de l'image
    image_data = camera.get_image()
    print(f"Image contient {len(image_data)} pixels")
    
    # Obtenir la valeur d'un pixel spécifique
    pixel_value = camera.get_pixel_value(256, 256)  # Centre de l'image
    print(f"Valeur du pixel central: {pixel_value:.3f}")
    
    # Exporter l'image
    camera.export_image("skyviewfactor_visualization.ppm")
    print("Image exportée vers skyviewfactor_visualization.ppm")
```

## Export et import de données

### Export des résultats

```python
# Exporter les SVF calculés vers un fichier
success = svf_model.export_sky_view_factors("results.txt")
if success:
    print("Résultats exportés vers results.txt")
```

### Import des résultats

```python
# Charger les SVF depuis un fichier
success = svf_model.load_sky_view_factors("results.txt")
if success:
    print("Résultats chargés depuis results.txt")
    
    # Récupérer les données chargées
    loaded_svfs = svf_model.get_sky_view_factors()
    print(f"SVF chargés: {len(loaded_svfs)} valeurs")
```

## Statistiques et informations

### Statistiques du modèle

```python
# Obtenir les statistiques du modèle
stats = svf_model.get_statistics()
print("Statistiques du modèle:")
print(stats)
```

### Statistiques de la caméra

```python
# Obtenir les statistiques de la caméra
camera_stats = camera.get_statistics()
print("Statistiques de la caméra:")
print(camera_stats)
```

## Exemple complet

```python
#!/usr/bin/env python3
"""
Exemple complet d'utilisation du plugin SkyViewFactor
"""

from pyhelios import Context, SkyViewFactorModel, SkyViewFactorCamera

def main():
    # Créer la scène 3D
    context = Context()
    
    # Ajouter des obstacles (bâtiments, arbres, etc.)
    context.addTriangle(
        (-2.0, -2.0, 0.0),
        (2.0, -2.0, 0.0),
        (0.0, 2.0, 0.0)
    )
    
    # Créer le modèle SkyViewFactor
    svf_model = SkyViewFactorModel(context)
    svf_model.set_ray_count(2000)
    svf_model.set_max_ray_length(1000.0)
    
    # Définir les points d'analyse
    points = [
        (0.0, 0.0, 0.5),   # Près du bâtiment
        (3.0, 0.0, 0.5),   # Loin du bâtiment
        (0.0, 0.0, 5.0)    # Au-dessus des obstacles
    ]
    
    # Calculer les SVF
    print("Calcul des sky view factors...")
    svfs = svf_model.calculate_sky_view_factors(points)
    
    # Afficher les résultats
    for i, (point, svf) in enumerate(zip(points, svfs)):
        print(f"Point {i+1} {point}: SVF = {svf:.3f}")
    
    # Créer une caméra pour la visualisation
    camera = svf_model.create_camera()
    camera.set_position(0.0, 0.0, 10.0)
    camera.set_target(0.0, 0.0, 0.0)
    camera.set_resolution(256, 256)
    camera.set_ray_count(100)
    
    # Rendre et exporter l'image
    print("Rendu de l'image...")
    if camera.render():
        camera.export_image("skyviewfactor_result.ppm")
        print("Image exportée vers skyviewfactor_result.ppm")
    
    # Afficher les statistiques
    print("\nStatistiques du modèle:")
    print(svf_model.get_statistics())

if __name__ == "__main__":
    main()
```

## Interprétation des résultats

### Valeurs du Sky View Factor

- **1.0** : Ciel complètement dégagé (aucun obstacle)
- **0.8-0.9** : Ciel très ouvert (très peu d'obstacles)
- **0.6-0.8** : Ciel majoritairement ouvert
- **0.4-0.6** : Ciel partiellement obstrué
- **0.2-0.4** : Ciel fortement obstrué
- **0.0-0.2** : Ciel très obstrué
- **0.0** : Ciel complètement masqué

### Facteurs influençant la précision

1. **Nombre de rayons** : Plus de rayons = meilleure précision mais calcul plus long
2. **Longueur maximale des rayons** : Doit être suffisante pour détecter tous les obstacles
3. **Complexité de la scène** : Plus d'objets = calcul plus long
4. **Accélération GPU** : CUDA/OptiX améliore significativement les performances

## Performance et optimisation

### Recommandations

- **Développement** : 100-500 rayons pour des tests rapides
- **Production** : 1000-5000 rayons pour une bonne précision
- **Haute précision** : 10000+ rayons pour des analyses détaillées

### Accélération GPU

Le plugin supporte l'accélération CUDA/OptiX pour des calculs rapides :

```python
if svf_model.is_cuda_available():
    print("Accélération CUDA disponible")
if svf_model.is_optix_available():
    print("Accélération OptiX disponible")
```

## Limitations actuelles

1. **Primitives supportées** : Actuellement optimisé pour les triangles
2. **Accélération GPU** : Nécessite OptiX pour l'accélération complète
3. **Précision** : Dépend du nombre de rayons utilisés

## Dépannage

### Erreurs communes

1. **"SkyViewFactorModel functions are not available"**
   - Solution : Compiler PyHelios avec le plugin skyviewfactor

2. **"Failed to calculate sky view factor"**
   - Solution : Vérifier que le contexte contient des primitives valides

3. **"Camera must be rendered before getting image data"**
   - Solution : Appeler `camera.render()` avant d'accéder aux données

### Vérification de l'installation

```python
from pyhelios import SkyViewFactorModel

# Vérifier si le plugin est disponible
if SkyViewFactorModel is not None:
    print("Plugin SkyViewFactor disponible")
else:
    print("Plugin SkyViewFactor non disponible")
```

## Support et contribution

Pour signaler des bugs ou proposer des améliorations, veuillez consulter la documentation du projet PyHelios ou créer une issue sur le dépôt GitHub.

---

*Documentation du plugin SkyViewFactor - PyHelios v1.0*
