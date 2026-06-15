# Time Is Money 🪙

> **Jeu de labyrinthe 2D en Python/arcade : collecte de pièces, boutique d'améliorations et chrono de survie.**

![Python](https://img.shields.io/badge/Python-14b8a6?style=flat-square)
![Type](https://img.shields.io/badge/Projet%20perso-555?style=flat-square)

## ✨ Aperçu
Projet personnel : « Labyrinthe avec Boutique », un jeu 2D développé en Python avec la bibliothèque `arcade`. Le joueur explore un labyrinthe en tuiles, ramasse des pièces pour gagner de l'argent et doit survivre à un compte à rebours. L'argent récolté permet d'acheter des améliorations dans une boutique. Le projet illustre la création d'un jeu complet avec moteur physique, gestion des sprites et boucle de jeu.

## 🚀 Fonctionnalités
- **Labyrinthe en tuiles** : carte 12×9 définie par `MAZE_MAP`.
- **Économie de jeu** : collecte de pièces convertie en argent.
- **Chrono de survie** : compte à rebours « Life Time » (`TIMER_START = 3600`).
- **Boutique** : touche `1` = Power Up (50 $), touche `2` = +10 minutes (100 $).
- **Moteur physique** : déplacements gérés par `arcade.PhysicsEngineSimple`, sprites intégrés (`:resources:`).

## 🛠️ Stack technique
- **Langage** : Python
- **Bibliothèques / frameworks** : arcade (+ `random`, `math`)
- **Outils** : interpréteur Python standard

## ▶️ Lancer le projet
```bash
pip install arcade
python src/timeIsMoney.py
```

## 📂 Structure
```
src/
├── timeIsMoney.py   # jeu principal : class MyGame(arcade.Window), main() → arcade.run()
└── BulletCursor.py  # démo arcade séparée
# + ressources images
```

---
👤 **Auteur** : Afouane MOUHAMAD — [Portfolio](https://afouanee.dev) · [LinkedIn](https://linkedin.com/in/afouane-mouhamad)
