# Time Is Money 🪙

> **Jeu de labyrinthe 2D en Python/arcade : collecte de pièces, esquive d'ennemis, boutique d'améliorations et chrono de survie.**

![Python](https://img.shields.io/badge/Python-14b8a6?style=flat-square)
![Type](https://img.shields.io/badge/Projet%20perso-555?style=flat-square)

## ✨ Aperçu
Projet personnel : « Time Is Money », un jeu 2D complet développé en Python avec la bibliothèque `arcade`. Le joueur explore un labyrinthe en tuiles, ramasse toutes les pièces avant la fin du chrono tout en évitant des ennemis qui patrouillent, et peut dépenser son argent dans une boutique pour prendre l'avantage.

## 🎮 Télécharger et jouer (Windows)
Aucune installation de Python requise : téléchargez l'exécutable depuis la [dernière release GitHub](https://github.com/Afouanee/timeIsMoney/releases/latest) et lancez `timeIsMoney.exe`.

## 🚀 Fonctionnalités
- **Écran titre** : appuyez sur `ESPACE` pour démarrer une partie.
- **Labyrinthe en tuiles** : carte 12×9 définie par `MAZE_MAP`, pièces réparties aléatoirement sur les cases libres sans jamais se superposer aux murs, aux ennemis ou au joueur.
- **Ennemis patrouilleurs** : plusieurs ennemis se déplacent dans le labyrinthe et rebondissent sur les murs. Un contact fait perdre de l'argent et déclenche une courte invulnérabilité pour éviter le spam de dégâts.
- **Économie de jeu** : collecte de pièces convertie en argent (son de collecte inclus).
- **Boutique** :
  - touche `1` = **Power Up** (50 $) : booste la vitesse du joueur pendant 8 secondes, avec un indicateur visuel à l'écran et un halo autour du personnage.
  - touche `2` = **+1 minute** (100 $) sur le chrono.
- **Chrono de survie** : compte à rebours « Life Time » affiché en permanence.
- **Objectif clair** : ramasser toutes les pièces du labyrinthe avant la fin du chrono pour gagner.
- **Conditions de fin de partie** :
  - **Victoire** si toutes les pièces sont ramassées à temps.
  - **Game Over** si le chrono atteint 0 avant d'avoir tout ramassé.
  - Écran de fin avec score final (argent + pièces collectées), et possibilité de rejouer (`ESPACE`) ou de quitter (`ECHAP`).
- **Son** : effets sonores pour la collecte de pièces, les coups reçus, l'achat de power-up, la victoire et la défaite.
- **Moteur physique** : déplacements gérés par `arcade.PhysicsEngineSimple`, sprites intégrés (`:resources:`).

## 🕹️ Contrôles
| Touche | Action |
|---|---|
| `ESPACE` | Démarrer / rejouer une partie |
| `↑ ↓ ← →` | Déplacer le joueur |
| `1` | Acheter un Power Up (50 $) |
| `2` | Acheter +1 minute (100 $) |
| `ECHAP` | Quitter le jeu |

## 🎯 Objectif
Ramassez toutes les pièces du labyrinthe avant que le chrono n'atteigne 0, tout en évitant les ennemis qui vous font perdre de l'argent. Utilisez la boutique pour acheter un coup de vitesse ou du temps supplémentaire si la partie devient serrée.

## 🛠️ Stack technique
- **Langage** : Python
- **Bibliothèques / frameworks** : arcade 3.x (+ `random`)
- **Packaging** : PyInstaller (exécutable Windows autonome)

## ▶️ Lancer le projet depuis le code source
```bash
pip install arcade
python src/timeIsMoney.py
```

## 📦 Construire l'exécutable soi-même
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name timeIsMoney src/timeIsMoney.py
```
L'exécutable est généré dans `dist/timeIsMoney.exe`. Le hook PyInstaller officiel fourni par `arcade` embarque automatiquement les ressources graphiques et sonores utilisées (`:resources:`).

## 📂 Structure
```
src/
├── timeIsMoney.py   # jeu principal : class MyGame(arcade.Window), main() → arcade.run()
└── BulletCursor.py  # démo arcade séparée
```
