"""
Guide d'utilisation du calcul de Sky View Factor avec Helios.

Ce script montre comment intégrer le calcul de SVF dans vos simulations Helios existantes.
"""

import math
import numpy as np
import pandas as pd
from typing import List, Tuple, Optional

from pyhelios import Context, RadiationModel, Visualizer
from pyhelios.types import *


def integrate_svf_in_existing_simulation(context: Context) -> None:
    """
    Exemple d'intégration du SVF dans une simulation existante.
    """
    print("🔗 Intégration du SVF dans une simulation existante")
    print("=" * 60)
    
    # 1. Calculer le SVF pour tous les points d'intérêt
    points_of_interest = [
        vec3(0, 0, 1.5),    # Point central
        vec3(5, 5, 1.5),    # Près d'un bâtiment
        vec3(-5, -5, 1.5),  # Zone ouverte
    ]
    
    svf_values = {}
    for point in points_of_interest:
        svf = calculate_svf_for_point(context, point)
        svf_values[f"point_{len(svf_values)}"] = svf
        print(f"   Point ({point.x:.1f}, {point.y:.1f}, {point.z:.1f}): SVF = {svf:.3f}")
    
    # 2. Utiliser le SVF pour ajuster les paramètres de simulation
    for point_name, svf in svf_values.items():
        if svf > 0.8:
            print(f"   {point_name}: Zone très ouverte - Exposition solaire maximale")
        elif svf > 0.5:
            print(f"   {point_name}: Zone modérément ouverte - Exposition solaire moyenne")
        else:
            print(f"   {point_name}: Zone fermée - Exposition solaire limitée")


def calculate_svf_for_point(context: Context, point: vec3) -> float:
    """
    Calcule le SVF pour un point spécifique.
    
    Args:
        context: Contexte Helios
        point: Position du point
        
    Returns:
        Valeur du SVF (0-1)
    """
    try:
        with RadiationModel(context) as rad:
            # Configuration pour le calcul du SVF
            rad.addRadiationBand("SVF")
            rad.setDiffuseRayCount("SVF", 1000)
            
            # Patch de test
            test_patch = context.addPatch(
                center=point,
                size=vec2(0.01, 0.01),
                color=RGBcolor(1, 0, 0)
            )
            
            # Rayonnement diffus isotrope
            rad.setDiffuseRadiationFlux("SVF", 1000.0)
            
            # Simulation
            rad.updateGeometry()
            rad.runBand("SVF")
            
            # Récupération du flux
            flux = context.getPrimitiveData(test_patch, "radiation_flux_SVF")
            
            if flux is None:
                return 0.0
            
            # Calcul du SVF
            svf = min(flux / 1000.0, 1.0)
            return svf
            
    except Exception as e:
        print(f"❌ Erreur calcul SVF: {e}")
        return 0.0


def create_svf_analysis_report(
    context: Context,
    analysis_points: List[vec3],
    output_file: str = "svf_analysis_report.txt"
) -> None:
    """
    Crée un rapport d'analyse du SVF.
    
    Args:
        context: Contexte Helios
        analysis_points: Points d'analyse
        output_file: Fichier de sortie
    """
    print(f"📝 Création du rapport d'analyse: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("RAPPORT D'ANALYSE DU SKY VIEW FACTOR\n")
        f.write("=" * 50 + "\n\n")
        
        f.write(f"Nombre de points analysés: {len(analysis_points)}\n")
        f.write(f"Date d'analyse: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        svf_values = []
        
        for i, point in enumerate(analysis_points):
            svf = calculate_svf_for_point(context, point)
            svf_values.append(svf)
            
            f.write(f"Point {i+1}:\n")
            f.write(f"  Position: ({point.x:.2f}, {point.y:.2f}, {point.z:.2f})\n")
            f.write(f"  SVF: {svf:.3f}\n")
            
            # Classification
            if svf >= 0.8:
                classification = "Très ouvert"
            elif svf >= 0.6:
                classification = "Ouvert"
            elif svf >= 0.4:
                classification = "Modérément fermé"
            elif svf >= 0.2:
                classification = "Fermé"
            else:
                classification = "Très fermé"
            
            f.write(f"  Classification: {classification}\n\n")
        
        # Statistiques globales
        f.write("STATISTIQUES GLOBALES\n")
        f.write("-" * 30 + "\n")
        f.write(f"SVF moyen: {np.mean(svf_values):.3f}\n")
        f.write(f"SVF médian: {np.median(svf_values):.3f}\n")
        f.write(f"SVF min: {np.min(svf_values):.3f}\n")
        f.write(f"SVF max: {np.max(svf_values):.3f}\n")
        f.write(f"Écart-type: {np.std(svf_values):.3f}\n")
        
        # Distribution
        f.write(f"\nDISTRIBUTION\n")
        f.write("-" * 20 + "\n")
        very_high = np.sum(np.array(svf_values) >= 0.8)
        high = np.sum((np.array(svf_values) >= 0.6) & (np.array(svf_values) < 0.8))
        medium = np.sum((np.array(svf_values) >= 0.4) & (np.array(svf_values) < 0.6))
        low = np.sum((np.array(svf_values) >= 0.2) & (np.array(svf_values) < 0.4))
        very_low = np.sum(np.array(svf_values) < 0.2)
        
        f.write(f"Très ouvert (≥0.8): {very_high} points ({very_high/len(svf_values)*100:.1f}%)\n")
        f.write(f"Ouvert (0.6-0.8): {high} points ({high/len(svf_values)*100:.1f}%)\n")
        f.write(f"Modérément fermé (0.4-0.6): {medium} points ({medium/len(svf_values)*100:.1f}%)\n")
        f.write(f"Fermé (0.2-0.4): {low} points ({low/len(svf_values)*100:.1f}%)\n")
        f.write(f"Très fermé (<0.2): {very_low} points ({very_low/len(svf_values)*100:.1f}%)\n")
        
        # Recommandations
        f.write(f"\nRECOMMANDATIONS\n")
        f.write("-" * 20 + "\n")
        
        avg_svf = np.mean(svf_values)
        if avg_svf >= 0.7:
            f.write("• Zone très ouverte - Exposition solaire maximale\n")
            f.write("• Risque de surchauffe en été\n")
            f.write("• Recommandation: Ajouter de l'ombrage\n")
        elif avg_svf >= 0.5:
            f.write("• Zone modérément ouverte - Exposition solaire équilibrée\n")
            f.write("• Conditions thermiques favorables\n")
            f.write("• Recommandation: Maintenir l'équilibre actuel\n")
        else:
            f.write("• Zone fermée - Exposition solaire limitée\n")
            f.write("• Risque de manque de lumière naturelle\n")
            f.write("• Recommandation: Ouvrir la canopée\n")
    
    print(f"✅ Rapport sauvegardé: {output_file}")


def optimize_svf_calculation(context: Context, points: List[vec3]) -> List[float]:
    """
    Version optimisée du calcul de SVF pour de nombreux points.
    
    Args:
        context: Contexte Helios
        points: Liste des points à analyser
        
    Returns:
        Liste des valeurs de SVF
    """
    print(f"⚡ Calcul optimisé du SVF pour {len(points)} points")
    
    # Configuration unique pour tous les points
    with RadiationModel(context) as rad:
        rad.addRadiationBand("SVF")
        rad.setDiffuseRayCount("SVF", 2000)  # Plus de rayons pour précision
        
        # Créer tous les patches de test
        test_patches = []
        for point in points:
            patch = context.addPatch(
                center=point,
                size=vec2(0.01, 0.01),
                color=RGBcolor(1, 0, 0)
            )
            test_patches.append(patch)
        
        # Configuration du rayonnement
        rad.setDiffuseRadiationFlux("SVF", 1000.0)
        
        # Simulation unique
        rad.updateGeometry()
        rad.runBand("SVF")
        
        # Récupération des flux
        svf_values = []
        for patch in test_patches:
            flux = context.getPrimitiveData(patch, "radiation_flux_SVF")
            if flux is None:
                svf_values.append(0.0)
            else:
                svf = min(flux / 1000.0, 1.0)
                svf_values.append(svf)
        
        return svf_values


def main():
    """
    Démonstration de l'utilisation du SVF dans Helios.
    """
    print("🌌 Guide d'utilisation du Sky View Factor avec Helios")
    print("=" * 70)
    
    # Créer un contexte de test
    with Context() as context:
        print("🏗️  Création de la scène de test...")
        
        # Créer un sol
        ground = context.addPatch(
            center=vec3(0, 0, 0),
            size=vec2(30, 30),
            color=RGBcolor(0.5, 0.5, 0.5)
        )
        
        # Créer des obstacles
        obstacles = []
        for i in range(5):
            for j in range(5):
                if i == 2 and j == 2:  # Laissez le centre libre
                    continue
                
                obstacle = context.addPatch(
                    center=vec3(i * 4 - 8, j * 4 - 8, 2),
                    size=vec2(2, 2),
                    color=RGBcolor(0.8, 0.8, 0.8)
                )
                obstacles.append(obstacle)
        
        print(f"✅ Scène créée: 1 sol, {len(obstacles)} obstacles")
        
        # 1. Intégration dans une simulation existante
        integrate_svf_in_existing_simulation(context)
        
        # 2. Création d'un rapport d'analyse
        analysis_points = [
            vec3(0, 0, 1.5),    # Centre
            vec3(4, 4, 1.5),    # Près d'un obstacle
            vec3(-4, -4, 1.5),  # Zone ouverte
            vec3(8, 0, 1.5),    # Bord
            vec3(-8, 8, 1.5),   # Coin
        ]
        
        create_svf_analysis_report(context, analysis_points)
        
        # 3. Calcul optimisé
        print(f"\n⚡ Test du calcul optimisé...")
        svf_values = optimize_svf_calculation(context, analysis_points)
        
        print("Résultats du calcul optimisé:")
        for i, (point, svf) in enumerate(zip(analysis_points, svf_values)):
            print(f"   Point {i+1}: SVF = {svf:.3f}")
        
        print("\n✅ Démonstration terminée!")
        print("\n📋 Résumé des fonctionnalités:")
        print("   • Calcul du SVF pour des points spécifiques")
        print("   • Intégration dans des simulations existantes")
        print("   • Génération de rapports d'analyse")
        print("   • Calcul optimisé pour de nombreux points")
        print("   • Classification et recommandations automatiques")


if __name__ == "__main__":
    main()
