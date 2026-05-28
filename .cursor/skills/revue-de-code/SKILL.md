# Prompt de Revue de Code – Mode Plan

Examine ce plan en profondeur avant d’apporter la moindre modification au code.  
Pour chaque problème ou recommandation, explique les compromis concrets, formule une recommandation argumentée, et demande mon validation avant de partir dans une direction.

---

## Préférences d’ingénierie

À utiliser comme cadre de référence pour tes recommandations :

- **Le principe DRY est prioritaire** — signale toute répétition de manière proactive.
- **Le code doit être solidement testé** ; je préfère trop de tests que pas assez.
- Je souhaite un code **« suffisamment industrialisé »** — ni sous-conçu (fragile, bricolé), ni sur-conçu (abstraction prématurée, complexité inutile).
- Je privilégie la gestion exhaustive des cas limites ; **la rigueur prime sur la vitesse**.
- Favoriser une écriture **explicite plutôt qu’astucieuse**.

---

# 1. Revue d’Architecture

Évaluer :

- La conception globale du système et les frontières entre composants.
- Le graphe de dépendances et les risques de couplage excessif.
- Les flux de données et les goulots d’étranglement potentiels.
- Les caractéristiques de montée en charge et les points uniques de défaillance.
- L’architecture de sécurité (authentification, accès aux données, périmètre des API).

---

# 2. Revue de Qualité du Code

Évaluer :

- L’organisation du code et la structuration des modules.
- Les violations du principe DRY — être particulièrement attentif.
- Les patterns de gestion d’erreurs et les cas limites non couverts (les expliciter).
- Les zones de dette technique.
- Les éléments sur-conçus ou sous-conçus au regard de mes préférences.

---

# 3. Revue des Tests

Évaluer :

- Les lacunes de couverture (unitaires, intégration, end-to-end).
- La qualité des tests et la robustesse des assertions.
- Les cas limites non couverts — être exhaustif.
- Les modes de défaillance et chemins d’erreur non testés.

---

# 4. Revue de Performance

Évaluer :

- Les requêtes N+1 et les patterns d’accès aux bases de données.
- Les problématiques d’usage mémoire.
- Les opportunités de mise en cache.
- Les portions de code lentes ou à forte complexité algorithmique.

---

# Pour chaque problème identifié

Pour chaque problème spécifique (bug, code smell, défaut de conception ou risque) :

- Décrire le problème de manière concrète, avec références fichier et ligne.
- Proposer 2 à 3 options, y compris « ne rien faire » si pertinent.
- Pour chaque option, préciser :
  - L’effort d’implémentation
  - Le niveau de risque
  - L’impact sur le reste du code
  - La charge de maintenance
- Formuler une recommandation argumentée en cohérence avec mes préférences.
- Me demander explicitement si je valide ou souhaite une autre orientation avant de poursuivre.

---

# Modalités de travail et interaction

- Ne pas présumer de mes priorités en termes de délais ou d’échelle.
- Après chaque section, s’arrêter et solliciter mon retour avant de continuer.

---

# Avant de commencer

Demander si je souhaite l’une des deux options suivantes :

1. **CHANGEMENT MAJEUR**  
   Revue interactive section par section  
   (Architecture → Qualité du Code → Tests → Performance)  
   avec un maximum de 4 problèmes majeurs par section.

2. **CHANGEMENT MINEUR**  
   Revue interactive avec UNE seule question par section.

---

# Pour chaque étape de revue

- Présenter l’analyse détaillée.
- Exposer les avantages et inconvénients des différentes options.
- Donner une recommandation argumentée.
- Numéroter les problèmes.
- Identifier les options par des lettres (A, B, C).
- Faire apparaître l’option recommandée en première position.
- Utiliser une question explicite pour validation avant de passer à l’étape suivante.
