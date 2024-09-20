import random

import arcade
import threading
import time
from collections import deque

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
SCREEN_TITLE = "Time Twister"

# Constantes pour la vitesse de mouvement
HORIZONTAL_SPEED = 5  # Vitesse horizontale
VERTICAL_SPEED = 5    # Vitesse verticale (plus rapide)

MOVEMENT_SPEED = 5
UPDATES_PER_FRAME = 5  # Pour gérer la vitesse de l'animation

PAUSE = 1.7
TELEPORT_INTERVAL = 12  # Seconds
TELEPORT_COOLDOWN = 1  # Minimum time between teleports in seconds
TRAIL_LENGTH = 100  # Number of positions to keep for the trail
REWIND_SPEED = 20  # Speed of the rewind animation
POINT_SKIP = 2  # Number of points to skip to increase rewind speed

# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """ Charger les textures pour la direction gauche et droite """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    def __init__(self):
        # Initialisation de la classe parent
        super().__init__()

        self.background = None

        # Par défaut, le personnage regarde à droite
        self.character_face_direction = RIGHT_FACING

        # Compteur de la texture actuelle
        self.cur_texture = 0

        # Échelle du personnage (tu peux l'ajuster si nécessaire)
        self.scale = SPRITE_SCALING

        # Chemin vers les ressources du robot
        main_path = ":resources:images/animated_characters/robot/robot"

        # Charger les textures pour l'état d'attente (idle)
        self.idle_texture_pair = load_texture_pair(f"{main_path}_idle.png")

        # Charger les textures pour la marche
        self.walk_textures = []
        for i in range(8):  # Il y a 8 frames d'animation pour la marche
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Définir la texture initiale
        self.texture = self.idle_texture_pair[RIGHT_FACING]

    def update_animation(self, delta_time: float = 1 / 60):
        """ Mettre à jour l'animation du personnage """

        # Déterminer la direction du personnage
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Animation d'attente
        if self.change_x == 0 and self.change_y == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Animation de marche
        self.cur_texture += 1
        if self.cur_texture > 7 * UPDATES_PER_FRAME:
            self.cur_texture = 0
        frame = self.cur_texture // UPDATES_PER_FRAME
        direction = self.character_face_direction
        self.texture = self.walk_textures[frame][direction]


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        """ Initialiser le jeu et les variables """
        super().__init__(width, height, title)

        # Listes de sprites
        self.player_list = None
        self.box_list = None  # Liste pour les caisses
        self.door_list = None

        # Configuration du joueur
        self.player_sprite = None

        # Suivi de l'état des touches appuyées
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Couleur de fond
        arcade.set_background_color(arcade.color.BLACK_BEAN)

        self.button1 = False
        self.button2 = False
        self.button3 = False

        # Liste pour stocker les positions du joueur pour la téléportation
        self.position_history = deque(maxlen=int(TELEPORT_INTERVAL / 0.1))  # Stocker les positions des 5 dernières secondes

        # Liste pour stocker les positions pour l'effet de traînée
        self.trail = deque(maxlen=TRAIL_LENGTH)  # Stocker les positions pour l'effet de traînée

        # Liste pour stocker le chemin inverse pour l'effet de rembobinage
        self.reverse_path = []

        # Suivi du temps de la dernière téléportation
        self.last_teleport_time = 0

        # Drapeau d'état de rembobinage
        self.is_rewinding = False

        # Drapeau de contrôle du thread
        self.thread_started = False

    def setup(self):
        self.background = arcade.load_texture("/home/roland/PycharmProjects/timeIsMoney/resources/bg.jpg")

        """ Configurer le jeu et initialiser les variables. """
        # Listes de sprites
        self.player_list = arcade.SpriteList()
        self.box_list = arcade.SpriteList()  # Initialiser la liste des caisses
        self.door_list = arcade.SpriteList()

        # Configurer le joueur
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 100
        self.player_sprite.center_y = 100
        self.player_list.append(self.player_sprite)

        # Configurer un obstacle
        self.obstacle1 = arcade.Sprite("../resources/NonPressedBouton.png", SPRITE_SCALING / 3)
        self.obstacle1.center_x = 100
        self.obstacle1.center_y = 240

        self.obstacle2 = arcade.Sprite("../resources/NonPressedBouton.png", SPRITE_SCALING / 3)
        self.obstacle2.center_x = 400
        self.obstacle2.center_y = 140

        self.obstacle3 = arcade.Sprite("../resources/NonPressedBouton.png", SPRITE_SCALING / 3)
        self.obstacle3.center_x = 400
        self.obstacle3.center_y = 340

        for i in range(3):
            door = arcade.Sprite("../resources/door.png", SPRITE_SCALING / 1.5)
            door.center_x = 207 + i * 39
            door.center_y = 480
            self.door_list.append(door)

        # Ajouter des caisses
        for i in range(13):  # Ajouter 5 caisses pour l'exemple
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 12 + i * 39  # Changer les coordonnées selon tes besoins
            box.center_y = 12
            self.box_list.append(box)
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 12 # Changer les coordonnées selon tes besoins
            box.center_y = 12 + i * 39
            self.box_list.append(box)
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 480  # Changer les coordonnées selon tes besoins
            box.center_y = 12 + i * 39
            self.box_list.append(box)


        for i in range(5):
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 12 + i * 39  # Changer les coordonnées selon tes besoins
            box.center_y = 480
            self.box_list.append(box)
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 323 + i * 39  # Changer les coordonnées selon tes besoins
            box.center_y = 480
            self.box_list.append(box)



        # Démarrer le thread pour imprimer la position du joueur toutes les 5 secondes
        if not self.thread_started:
            self.position_thread = threading.Thread(target=self.print_player_position)
            self.position_thread.daemon = True
            self.position_thread.start()
            self.thread_started = True

    def on_draw(self):
        """ Rendre l'écran. """
        self.clear()
        if self.background:
            arcade.draw_lrwh_rectangle_textured(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background)
        # Dessiner la traînée uniquement si le rembobinage n'est pas en cours
        if not self.is_rewinding:
            self.draw_trail()

        self.obstacle1.draw()
        self.obstacle2.draw()
        self.obstacle3.draw()

        self.player_list.draw()
        self.box_list.draw()  # Dessiner les caisses
        self.door_list.draw()

    # Constantes pour la vitesse de mouvement
    HORIZONTAL_SPEED = 5  # Vitesse horizontale
    VERTICAL_SPEED = 8  # Vitesse verticale (plus rapide)

    def update_player_speed(self):
        """ Calculer la vitesse en fonction des touches appuyées """
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = VERTICAL_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -VERTICAL_SPEED

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -HORIZONTAL_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = HORIZONTAL_SPEED

        # Pour éviter d'avoir un boost en diagonale, on ajuste ici:
        if self.left_pressed or self.right_pressed:
            self.player_sprite.change_y /= 1.5
        if self.up_pressed or self.down_pressed:
            self.player_sprite.change_x /= 1.5

    def first_boutons(self):
        if arcade.check_for_collision(self.player_sprite, self.obstacle1) and self.button1 == False:
            my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/d.mp3")
            arcade.play_sound(my_sound)
            self.obstacle1 = arcade.Sprite("../resources/PressedBouton.png", SPRITE_SCALING / 3)
            self.obstacle1.center_x = 100
            self.obstacle1.center_y = 240
            self.button1 = True
            arcade.schedule(self.reset_bouton1, PAUSE)

    def reset_bouton1(self, delta_time):
        """ Réinitialise le bouton 2 """
        self.button1 = False  # Remet le bouton à l'état non pressé
        self.obstacle1.texture = arcade.load_texture(
            "../resources/NonPressedBouton.png")
        arcade.unschedule(self.reset_bouton1)

    def second_boutons(self):
        if arcade.check_for_collision(self.player_sprite, self.obstacle2) and self.button2 == False:
            my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/d.mp3")
            arcade.play_sound(my_sound)
            self.obstacle2 = arcade.Sprite("../resources/PressedBouton.png", SPRITE_SCALING / 3)
            self.obstacle2.center_x = 400
            self.obstacle2.center_y = 140
            self.button2 = True
            arcade.schedule(self.reset_bouton2, PAUSE)

    def reset_bouton2(self, delta_time):
        """ Réinitialise le bouton 2 """
        self.button2 = False  # Remet le bouton à l'état non pressé
        self.obstacle2.texture = arcade.load_texture(
            "../resources/NonPressedBouton.png")
        arcade.unschedule(self.reset_bouton2)

    def third_boutons(self):
        if arcade.check_for_collision(self.player_sprite, self.obstacle3) and self.button3 == False:
            my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/d.mp3")
            arcade.play_sound(my_sound)
            self.obstacle3 = arcade.Sprite("../resources/PressedBouton.png", SPRITE_SCALING / 3)
            self.obstacle3.center_x = 400
            self.obstacle3.center_y = 340
            self.button3 = True
            arcade.schedule(self.reset_bouton3, PAUSE)

    def reset_bouton3(self, delta_time):
        """ Réinitialise le bouton 2 """
        self.button3 = False  # Remet le bouton à l'état non pressé
        self.obstacle3.texture = arcade.load_texture(
            "../resources/NonPressedBouton.png")
        arcade.unschedule(self.reset_bouton3)

    def destroy_doors(self):
        """Détruire toutes les portes dans la liste door_list."""
        for door in self.door_list:
            door.kill()  # Supprimer la porte de la liste des sprites
        print("Les portes ont été détruites.")
        my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/ddd.mp3")
        arcade.play_sound(my_sound)

    def on_update(self, delta_time):
        """ Logique de mouvement et de jeu """
        # Mettre à jour le sprite du joueur
        self.player_list.update()
        self.player_list.update_animation()  # Mettre à jour l'animation


        self.first_boutons()
        self.second_boutons()
        self.third_boutons()
        if self.button1 and self.button2 and self.button3:
            self.destroy_doors()

        # Vérifier si les trois boutons sont activés


        # Sauvegarder la position du joueur à chaque mise à jour
        self.save_player_position()

        # Mettre à jour les positions de la traînée
        self.update_trail()

        # Vérifier les collisions avec les caisses et les gérer
        self.handle_collisions()

        # Vérifier si le joueur est hors de la zone de jeu
        self.check_player_out_of_bounds()

        # Rembobiner si le joueur est en mode rembobinage
        if self.is_rewinding:
            self.rewind_movement()

    def check_player_out_of_bounds(self):
        """Vérifie si le joueur est hors de la zone de jeu et réinitialise le niveau si c'est le cas."""
        if (self.player_sprite.center_x < 0 or self.player_sprite.center_x > SCREEN_WIDTH or
                self.player_sprite.center_y < 0 or self.player_sprite.center_y > SCREEN_HEIGHT):
            LEVEL2 = True
            LEVEL1 = False
            self.reset_level()

    def setup_obstacles(self):
        """Ajouter des obstacles dans le niveau."""


        # Ajouter d'autres obstacles si nécessaire

    def reset_level(self):
        # Effacer toutes les listes de sprites, y compris les obstacles
        self.player_list = arcade.SpriteList()
        self.box_list = arcade.SpriteList()
        self.door_list = arcade.SpriteList()  # Ajouter cette ligne pour réinitialiser les portes
        self.obstacle1.kill()
        self.obstacle2.kill()
        self.obstacle3.kill()

        # Replacer le joueur à la position initiale dans le nouveau niveau vierge
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = 150  # Début du labyrinthe
        self.player_sprite.center_y = 150  # Début du labyrinthe
        self.player_list.append(self.player_sprite)

        # Réinitialiser les autres variables du jeu si nécessaire
        self.trail.clear()
        self.position_history.clear()
        self.reverse_path = []
        self.is_rewinding = False
        self.last_teleport_time = 0

        # Réinitialiser les drapeaux de boutons
        self.button1 = False
        self.button2 = False
        self.button3 = False

        self.obstacle1 = arcade.Sprite("../resources/NonPressedBouton.png", SPRITE_SCALING / 3)
        self.obstacle1.center_x = 100
        self.obstacle1.center_y = 240

        self.obstacle2 = arcade.Sprite("../resources/NonPressedBouton.png", SPRITE_SCALING / 3)
        self.obstacle2.center_x = 400
        self.obstacle2.center_y = 140

        self.obstacle3 = arcade.Sprite("../resources/NonPressedBouton.png", SPRITE_SCALING / 3)
        self.obstacle3.center_x = 400
        self.obstacle3.center_y = 340

        for i in range(3):
            door = arcade.Sprite("../resources/door.png", SPRITE_SCALING / 1.5)
            door.center_x = 207 + i * 39
            door.center_y = 480
            self.door_list.append(door)

        # Ajouter des caisses
        for i in range(13):  # Ajouter 5 caisses pour l'exemple
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 12 + i * 39  # Changer les coordonnées selon tes besoins
            box.center_y = 12
            self.box_list.append(box)
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 12  # Changer les coordonnées selon tes besoins
            box.center_y = 12 + i * 39
            self.box_list.append(box)
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 480  # Changer les coordonnées selon tes besoins
            box.center_y = 12 + i * 39
            self.box_list.append(box)

        for i in range(5):
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 12 + i * 39  # Changer les coordonnées selon tes besoins
            box.center_y = 480
            self.box_list.append(box)
            box = arcade.Sprite("../resources/wall.png", SPRITE_SCALING / 1.5)
            box.center_x = 323 + i * 39  # Changer les coordonnées selon tes besoins
            box.center_y = 480
            self.box_list.append(box)

        # Changer la couleur de fond pour indiquer une nouvelle dimension
        arcade.set_background_color(arcade.color.BLACK)

        #self.obstacle1.draw()
        #self.obstacle2.draw()
        #self.obstacle3.draw()
        self.box_list.draw()  # Dessiner les caisses
        self.door_list.draw()

    def on_key_press(self, key, modifiers):
        """Appelée à chaque fois qu'une touche est enfoncée."""
        if self.is_rewinding:
            # Si le jeu est en mode rembobinage, ne pas traiter les autres touches
            return

        if key == arcade.key.Z:
            self.up_pressed = True
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = True
            self.update_player_speed()
        elif key == arcade.key.Q:
            self.left_pressed = True
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = True
            self.update_player_speed()
        elif key == arcade.key.SPACE:
            self.start_rewind()

    def on_key_release(self, key, modifiers):
        """Appelée lorsque l'utilisateur relâche une touche. """
        if key == arcade.key.Z:
            self.up_pressed = False
            self.update_player_speed()
        elif key == arcade.key.S:
            self.down_pressed = False
            self.update_player_speed()
        elif key == arcade.key.Q:
            self.left_pressed = False
            self.update_player_speed()
        elif key == arcade.key.D:
            self.right_pressed = False
            self.update_player_speed()

    def save_player_position(self):
        """Sauvegarder la position actuelle du joueur dans l'historique."""
        if not self.is_rewinding:
            current_position = (self.player_sprite.center_x, self.player_sprite.center_y)
            self.position_history.append(current_position)

    def update_trail(self):
        """Mettre à jour les positions de la traînée avec la position actuelle du joueur."""
        if not self.is_rewinding:
            current_position = (self.player_sprite.center_x, self.player_sprite.center_y)
            self.trail.append(current_position)

    def draw_trail(self):
        """Dessiner la traînée du joueur."""
        if len(self.trail) > 1:
            arcade.draw_line_strip(self.trail, arcade.color.GRAY, 2)

    def start_rewind(self):
        my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/rewind.mp3")
        arcade.play_sound(my_sound)
        """Initier le processus de rembobinage vers la position où le joueur était il y a 5 secondes."""
        current_time = time.time()
        if current_time - self.last_teleport_time >= TELEPORT_COOLDOWN:
            if len(self.position_history) >= int(TELEPORT_INTERVAL / 0.1):
                # Effacer la traînée pour éviter de montrer une ligne entre l'ancienne et la nouvelle position
                self.trail.clear()

                # Préparer le chemin inverse
                # Sauter des points dans le chemin inverse pour accélérer le rembobinage
                self.reverse_path = list(self.position_history)[::-POINT_SKIP]  # Sauter des points pour un rembobinage plus rapide
                self.is_rewinding = True
                print("Rewind started...")
        else:
            print("Rewind is on cooldown. Please wait.")

    def rewind_movement(self):
        """Déplacer le joueur le long du chemin inverse."""
        if self.reverse_path:
            target_x, target_y = self.reverse_path.pop(0)
            direction_x = target_x - self.player_sprite.center_x
            direction_y = target_y - self.player_sprite.center_y

            distance = (direction_x ** 2 + direction_y ** 2) ** 0.5

            if distance > REWIND_SPEED:
                # Déplacer le joueur vers la cible à la vitesse de REWIND_SPEED
                direction_x /= distance
                direction_y /= distance

                self.player_sprite.center_x += direction_x * REWIND_SPEED
                self.player_sprite.center_y += direction_y * REWIND_SPEED
            else:
                # Recaler à la position si assez proche
                self.player_sprite.center_x = target_x
                self.player_sprite.center_y = target_y
        else:
            # Rembobinage terminé
            self.is_rewinding = False
            self.last_teleport_time = time.time()
            print("Rewind completed.")

    def handle_collisions(self):
        """Vérifier les collisions entre le joueur, les caisses et les portes, et arrêter le mouvement du joueur si une collision est détectée."""
        # Vérifier les collisions avec les caisses
        if arcade.check_for_collision_with_list(self.player_sprite, self.box_list):
            # Vérifier la direction dans laquelle le joueur se déplace et inverser le mouvement
            if self.up_pressed:
                self.player_sprite.center_y -= MOVEMENT_SPEED
            elif self.down_pressed:
                self.player_sprite.center_y += MOVEMENT_SPEED

            if self.left_pressed:
                self.player_sprite.center_x += MOVEMENT_SPEED
            elif self.right_pressed:
                self.player_sprite.center_x -= MOVEMENT_SPEED

        # Vérifier les collisions avec les portes
        if arcade.check_for_collision_with_list(self.player_sprite, self.door_list):
            # Vérifier la direction dans laquelle le joueur se déplace et inverser le mouvement
            if self.up_pressed:
                self.player_sprite.center_y -= MOVEMENT_SPEED
            elif self.down_pressed:
                self.player_sprite.center_y += MOVEMENT_SPEED

            if self.left_pressed:
                self.player_sprite.center_x += MOVEMENT_SPEED
            elif self.right_pressed:
                self.player_sprite.center_x -= MOVEMENT_SPEED

    def print_player_position(self):
        """Imprimer la position du joueur toutes les 5 secondes."""
        while True:
            if self.player_sprite is not None:
                print(f"Position du joueur: x={self.player_sprite.center_x}, y={self.player_sprite.center_y}")
            time.sleep(5)


def main():
    """ Fonction principale """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
    my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/The Unwound Future.mp3")
    arcade.play_sound(my_sound)


if __name__ == "__main__":
    main()
