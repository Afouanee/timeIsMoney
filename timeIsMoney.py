import pygame
from pygame.locals import *

pygame.init()

# Dimensions de la fenêtre
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("TimeCoin - Businessman Edition")

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Police
font = pygame.font.Font(None, 36)

# Temps (24 heures) et argent
total_seconds = 24 * 60 * 60  # 24 heures en secondes
money = 50  # 50$ au début
money_multiplier = 1  # Multiplicateur d'argent
clock = pygame.time.Clock()

# Variables de la boutique
time_cost = 10  # 10 $ pour acheter 30 secondes
multiplier_cost = 50  # 50 $ pour augmenter le multiplicateur d'argent

# Fonction pour afficher le temps en haut à droite
def display_time():
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    time_text = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    time_rendered = font.render(time_text, True, BLACK)
    screen.blit(time_rendered, (600, 50))

# Fonction pour afficher l'argent en dessous du temps
def display_money():
    money_text = font.render(f"Argent: ${money}", True, BLACK)
    screen.blit(money_text, (600, 100))

# Fonction pour afficher la boutique en haut à droite
def display_shop():
    shop_text = font.render("BOUTIQUE", True, BLACK)
    pygame.draw.rect(screen, GRAY, (600, 150, 180, 200))  # Fenêtre de la boutique
    screen.blit(shop_text, (620, 160))

    # Options de la boutique
    buy_time_text = font.render(f"J: +30s (-${time_cost})", True, BLACK)
    buy_multiplier_text = font.render(f"K: x2 Argent (-${multiplier_cost})", True, BLACK)
    another_action_text = font.render(f"L: ???", True, BLACK)  # Action personnalisée

    # Afficher les options
    screen.blit(buy_time_text, (620, 200))
    screen.blit(buy_multiplier_text, (620, 240))
    screen.blit(another_action_text, (620, 280))

# Boucle de jeu principale
running = True
while running:
    delta_time = clock.tick(60) / 1000  # Temps écoulé en secondes

    # Gérer les événements
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            # Acheter du temps avec la touche J
            if event.key == K_j and money >= time_cost:
                total_seconds += 30  # Ajouter 30 secondes
                money -= time_cost  # Réduire l'argent après l'achat

            # Acheter un multiplicateur d'argent avec la touche K
            if event.key == K_k and money >= multiplier_cost:
                money_multiplier *= 2  # Doubler le multiplicateur d'argent
                money -= multiplier_cost  # Réduire l'argent après l'achat
                multiplier_cost *= 2  # Le prix du multiplicateur augmente à chaque achat

            # Action personnalisée avec la touche L (exemple)
            if event.key == K_l:
                # Exemple : une action spéciale qui pourrait être ajoutée plus tard
                print("Action spéciale!")

    # Décompte du temps
    total_seconds -= delta_time * 1  # Le temps passe normalement (modifier ce facteur pour accélérer ou ralentir)

    # Vérifier si le temps est écoulé
    if total_seconds <= 0:
        print("Temps écoulé! Vous avez perdu!")
        running = False

    # Actualisation de l'affichage
    screen.fill(WHITE)

    # Afficher le temps, l'argent et la boutique
    display_time()
    display_money()
    display_shop()

    pygame.display.flip()

pygame.quit()
