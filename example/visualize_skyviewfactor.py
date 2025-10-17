#!/usr/bin/env python3
"""
Script principal pour visualiser les résultats SkyViewFactor avec des heatmaps.
Utilise matplotlib pour créer des visualisations 2D et 3D.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy.interpolate import griddata
import os
import argparse
import sys


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


def plot_heatmap_2d(X, Y, Z, points=None, svf_values=None, title="SkyViewFactor Heatmap", 
                   save_path=None, show_points=True, colormap='viridis'):
    """
    Affiche la heatmap 2D avec matplotlib.
    
    Args:
        X, Y, Z: Grilles pour la heatmap
        points: Points originaux (optionnel)
        svf_values: Valeurs originales (optionnel)
        title: Titre du graphique
        save_path: Chemin pour sauvegarder l'image
        show_points: Afficher les points originaux
        colormap: Colormap à utiliser
    """
    plt.figure(figsize=(12, 10))
    
    # Créer la heatmap
    im = plt.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()], 
                    origin='lower', cmap=colormap, aspect='auto')
    
    # Ajouter une barre de couleur
    cbar = plt.colorbar(im, shrink=0.8)
    cbar.set_label('Sky View Factor', rotation=270, labelpad=20)
    
    # Afficher les points originaux si demandé
    if show_points and points is not None and svf_values is not None:
        scatter = plt.scatter(points[:, 0], points[:, 1], c=svf_values, 
                             s=100, edgecolors='white', linewidth=2, 
                             cmap=colormap, vmin=Z.min(), vmax=Z.max())
    
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
        print(f"Heatmap 2D sauvegardée: {save_path}")
    
    plt.show()


def plot_heatmap_3d(X, Y, Z, title="SkyViewFactor 3D Surface", save_path=None):
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
    
    # Sauvegarder si demandé
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Heatmap 3D sauvegardée: {save_path}")
    
    plt.show()


def plot_contour(X, Y, Z, points=None, svf_values=None, title="SkyViewFactor Contour", 
                save_path=None, levels=20):
    """
    Crée un graphique de contour des valeurs SkyViewFactor.
    """
    plt.figure(figsize=(12, 10))
    
    # Créer les contours
    contour = plt.contour(X, Y, Z, levels=levels, colors='black', alpha=0.6, linewidths=0.5)
    contourf = plt.contourf(X, Y, Z, levels=levels, cmap='viridis', alpha=0.8)
    
    # Ajouter une barre de couleur
    cbar = plt.colorbar(contourf, shrink=0.8)
    cbar.set_label('Sky View Factor', rotation=270, labelpad=20)
    
    # Afficher les points originaux
    if points is not None and svf_values is not None:
        plt.scatter(points[:, 0], points[:, 1], c=svf_values, 
                   s=50, edgecolors='white', linewidth=1, 
                   cmap='viridis', vmin=Z.min(), vmax=Z.max())
    
    # Configuration
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Contour sauvegardé: {save_path}")
    
    plt.show()


def print_statistics(points, svf_values):
    """Affiche les statistiques des données."""
    print("\n" + "="*50)
    print("STATISTIQUES DES DONNÉES")
    print("="*50)
    print(f"Nombre de points: {len(points)}")
    print(f"Coordonnées X: {points[:, 0].min():.2f} à {points[:, 0].max():.2f}")
    print(f"Coordonnées Y: {points[:, 1].min():.2f} à {points[:, 1].max():.2f}")
    print(f"Valeurs SVF: {svf_values.min():.3f} à {svf_values.max():.3f}")
    print(f"Moyenne SVF: {svf_values.mean():.3f}")
    print(f"Médiane SVF: {np.median(svf_values):.3f}")
    print(f"Écart-type SVF: {svf_values.std():.3f}")
    
    # Distribution des valeurs
    print(f"\nDistribution des valeurs SVF:")
    print(f"  Très ouvert (SVF > 0.8): {np.sum(svf_values > 0.8)} points ({np.sum(svf_values > 0.8)/len(svf_values)*100:.1f}%)")
    print(f"  Ouvert (0.6 < SVF ≤ 0.8): {np.sum((svf_values > 0.6) & (svf_values <= 0.8))} points ({np.sum((svf_values > 0.6) & (svf_values <= 0.8))/len(svf_values)*100:.1f}%)")
    print(f"  Partiellement obstrué (0.4 < SVF ≤ 0.6): {np.sum((svf_values > 0.4) & (svf_values <= 0.6))} points ({np.sum((svf_values > 0.4) & (svf_values <= 0.6))/len(svf_values)*100:.1f}%)")
    print(f"  Fortement obstrué (0.2 < SVF ≤ 0.4): {np.sum((svf_values > 0.2) & (svf_values <= 0.4))} points ({np.sum((svf_values > 0.2) & (svf_values <= 0.4))/len(svf_values)*100:.1f}%)")
    print(f"  Très obstrué (SVF ≤ 0.2): {np.sum(svf_values <= 0.2)} points ({np.sum(svf_values <= 0.2)/len(svf_values)*100:.1f}%)")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(description='Visualiser les résultats SkyViewFactor avec des heatmaps')
    parser.add_argument('--file', '-f', default='skyviewfactor_results.txt',
                       help='Fichier de données SkyViewFactor (défaut: skyviewfactor_results.txt)')
    parser.add_argument('--resolution', '-r', type=int, default=100,
                       help='Résolution de la grille d\'interpolation (défaut: 100)')
    parser.add_argument('--method', '-m', choices=['linear', 'nearest', 'cubic'], default='linear',
                       help='Méthode d\'interpolation (défaut: linear)')
    parser.add_argument('--colormap', '-c', default='viridis',
                       help='Colormap à utiliser (défaut: viridis)')
    parser.add_argument('--no-points', action='store_true',
                       help='Ne pas afficher les points originaux')
    parser.add_argument('--no-3d', action='store_true',
                       help='Ne pas afficher la visualisation 3D')
    parser.add_argument('--contour', action='store_true',
                       help='Afficher aussi un graphique de contour')
    parser.add_argument('--save', '-s', action='store_true',
                       help='Sauvegarder les graphiques')
    
    args = parser.parse_args()
    
    # Vérifier que le fichier existe
    if not os.path.exists(args.file):
        print(f"Erreur: Le fichier {args.file} n'existe pas!")
        print("Fichiers disponibles:")
        for f in os.listdir('.'):
            if f.endswith('.txt') and 'skyviewfactor' in f.lower():
                print(f"  - {f}")
        return
    
    print(f"Chargement des données depuis {args.file}...")
    points, svf_values = load_skyviewfactor_data(args.file)
    
    if len(points) == 0:
        print("Aucune donnée trouvée dans le fichier!")
        return
    
    print(f"Chargé {len(points)} points de données")
    
    # Afficher les statistiques
    print_statistics(points, svf_values)
    
    # Créer la heatmap 2D
    print(f"\nCréation de la heatmap 2D (résolution: {args.resolution}x{args.resolution})...")
    X, Y, Z = create_heatmap_2d(points, svf_values, resolution=args.resolution, method=args.method)
    
    if X is not None:
        # Heatmap 2D
        save_path_2d = f"skyviewfactor_heatmap_2d_{os.path.splitext(args.file)[0]}.png" if args.save else None
        plot_heatmap_2d(X, Y, Z, points, svf_values, 
                       title=f"SkyViewFactor Heatmap - {args.file}",
                       save_path=save_path_2d,
                       show_points=not args.no_points,
                       colormap=args.colormap)
        
        # Visualisation 3D
        if not args.no_3d and len(points) >= 3:
            print("Création de la visualisation 3D...")
            save_path_3d = f"skyviewfactor_heatmap_3d_{os.path.splitext(args.file)[0]}.png" if args.save else None
            plot_heatmap_3d(X, Y, Z, 
                           title=f"SkyViewFactor 3D - {args.file}",
                           save_path=save_path_3d)
        
        # Graphique de contour
        if args.contour:
            print("Création du graphique de contour...")
            save_path_contour = f"skyviewfactor_contour_{os.path.splitext(args.file)[0]}.png" if args.save else None
            plot_contour(X, Y, Z, points, svf_values,
                        title=f"SkyViewFactor Contour - {args.file}",
                        save_path=save_path_contour)
    
    print("\nVisualisation terminée!")


if __name__ == "__main__":
    main()
