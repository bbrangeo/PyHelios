#!/usr/bin/env python3
"""
Script pour créer une heatmap des résultats SkyViewFactor avec matplotlib.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import griddata
import os


def load_skyviewfactor_data(filename):
    """
    Charge les données SkyViewFactor depuis un fichier texte.
    
    Args:
        filename (str): Chemin vers le fichier de résultats
        
    Returns:
        tuple: (points, svf_values) où points est un array (N, 2) des coordonnées X,Y
               et svf_values est un array (N,) des valeurs SkyViewFactor
    """
    points = []
    svf_values = []
    
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            # Ignorer les commentaires et lignes vides
            if line.startswith('#') or not line:
                continue
            
            # Parser la ligne: Point_ID X Y Z SkyViewFactor
            parts = line.split()
            if len(parts) >= 5:
                try:
                    point_id = int(parts[0])
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    svf = float(parts[4])
                    
                    points.append([x, y])
                    svf_values.append(svf)
                except ValueError:
                    print(f"Erreur lors du parsing de la ligne: {line}")
                    continue
    
    return np.array(points), np.array(svf_values)


def create_heatmap_2d(points, svf_values, resolution=100, method='linear'):
    """
    Crée une heatmap 2D des valeurs SkyViewFactor.
    
    Args:
        points (np.array): Array (N, 2) des coordonnées X,Y
        svf_values (np.array): Array (N,) des valeurs SkyViewFactor
        resolution (int): Résolution de la grille pour l'interpolation
        method (str): Méthode d'interpolation ('linear', 'nearest', 'cubic')
        
    Returns:
        tuple: (X, Y, Z) pour la heatmap
    """
    if len(points) == 0:
        print("Aucune donnée à traiter")
        return None, None, None
    
    # Définir les limites de la grille
    x_min, x_max = points[:, 0].min(), points[:, 0].max()
    y_min, y_max = points[:, 1].min(), points[:, 1].max()
    
    # Ajouter une petite marge
    margin_x = (x_max - x_min) * 0.1
    margin_y = (y_max - y_min) * 0.1
    
    x_min -= margin_x
    x_max += margin_x
    y_min -= margin_y
    y_max += margin_y
    
    # Créer la grille
    x_grid = np.linspace(x_min, x_max, resolution)
    y_grid = np.linspace(y_min, y_max, resolution)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # Interpoler les valeurs sur la grille
    if len(points) >= 3:  # Besoin d'au moins 3 points pour l'interpolation
        Z = griddata(points, svf_values, (X, Y), method=method, fill_value=0)
    else:
        # Si pas assez de points, créer une grille simple
        Z = np.zeros_like(X)
        for i, (x, y) in enumerate(points):
            # Trouver la cellule la plus proche
            idx_x = np.argmin(np.abs(x_grid - x))
            idx_y = np.argmin(np.abs(y_grid - y))
            Z[idx_y, idx_x] = svf_values[i]
    
    return X, Y, Z


def plot_heatmap(X, Y, Z, points=None, svf_values=None, title="SkyViewFactor Heatmap", 
                 save_path=None, show_points=True):
    """
    Affiche la heatmap avec matplotlib.
    
    Args:
        X, Y, Z: Grilles pour la heatmap
        points: Points originaux (optionnel)
        svf_values: Valeurs originales (optionnel)
        title: Titre du graphique
        save_path: Chemin pour sauvegarder l'image
        show_points: Afficher les points originaux
    """
    plt.figure(figsize=(12, 10))
    
    # Créer la heatmap
    im = plt.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                    origin='lower', cmap='viridis', aspect='auto')
    
    # Ajouter une barre de couleur
    cbar = plt.colorbar(im, shrink=0.8)
    cbar.set_label('Sky View Factor', rotation=270, labelpad=20)
    
    # Afficher les points originaux si demandé
    if show_points and points is not None and svf_values is not None:
        scatter = plt.scatter(points[:, 0], points[:, 1], c=svf_values, 
                             s=100, edgecolors='white', linewidth=2, 
                             cmap='viridis', vmin=Z.min(), vmax=Z.max())
    
    # Configuration du graphique
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    
    # Ajuster la mise en page
    plt.tight_layout()
    
    # Sauvegarder si demandé
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap sauvegardée: {save_path}")
    
    plt.show()


def plot_3d_surface(X, Y, Z, title="SkyViewFactor 3D Surface"):
    """
    Crée une visualisation 3D de la surface SkyViewFactor.
    """
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Créer la surface 3D
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8, linewidth=0, antialiased=True)
    
    # Configuration
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_zlabel('Sky View Factor')
    ax.set_title(title)
    
    # Ajouter une barre de couleur
    fig.colorbar(surf, shrink=0.5, aspect=5)
    
    plt.tight_layout()
    plt.show()


def main():
    """Fonction principale."""
    # Chemin vers le fichier de résultats
    results_file = "skyviewfactor_results.txt"
    
    if not os.path.exists(results_file):
        print(f"Fichier {results_file} non trouvé!")
        return
    
    print("Chargement des données SkyViewFactor...")
    points, svf_values = load_skyviewfactor_data(results_file)
    
    if len(points) == 0:
        print("Aucune donnée trouvée dans le fichier!")
        return
    
    print(f"Chargé {len(points)} points de données")
    print(f"Valeurs SVF: min={svf_values.min():.3f}, max={svf_values.max():.3f}, "
          f"moyenne={svf_values.mean():.3f}")
    
    # Créer la heatmap 2D
    print("Création de la heatmap 2D...")
    X, Y, Z = create_heatmap_2d(points, svf_values, resolution=50)
    
    if X is not None:
        # Afficher la heatmap 2D
        plot_heatmap(X, Y, Z, points, svf_values, 
                    title="SkyViewFactor Heatmap - Vue 2D",
                    save_path="skyviewfactor_heatmap_2d.png")
        
        # Créer aussi une vue 3D si on a assez de données
        if len(points) >= 3:
            print("Création de la visualisation 3D...")
            plot_3d_surface(X, Y, Z, title="SkyViewFactor - Vue 3D")
    
    # Afficher les statistiques
    print("\nStatistiques des données:")
    print(f"Nombre de points: {len(points)}")
    print(f"Coordonnées X: {points[:, 0].min():.2f} à {points[:, 0].max():.2f}")
    print(f"Coordonnées Y: {points[:, 1].min():.2f} à {points[:, 1].max():.2f}")
    print(f"Valeurs SVF: {svf_values.min():.3f} à {svf_values.max():.3f}")
    print(f"Moyenne SVF: {svf_values.mean():.3f}")
    print(f"Écart-type SVF: {svf_values.std():.3f}")


if __name__ == "__main__":
    main()
