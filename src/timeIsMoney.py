import arcade
import random

# Constantes
SCREEN_WIDTH = 840
SCREEN_HEIGHT = 520
SCREEN_TITLE = "Platformer"

# Constantes utilisées pour redimensionner nos sprites par rapport à leur taille originale
CHARACTER_SCALING = 0.5  # Réduit la taille du joueur
TILE_SCALING = 0.5

# Vitesse de déplacement du joueur, en pixels par frame
PLAYER_MOVEMENT_SPEED = 5

# Constantes du timer
TIMER_START = 3600  # 1 heure en secondes

# Constantes du score
INITIAL_MONEY = 0
COIN_VALUE = 10

# Constantes du labyrinthe
TILE_SIZE = 64
MAP_WIDTH = 13  # Largeur du tableau (en nombre de tuiles)
MAP_HEIGHT = 8  # Hauteur du tableau (en nombre de tuiles)

# Exemple de tableau de labyrinthe
MAZE_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

class MyGame(arcade.Window):
    """
    Classe principale de l'application.
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.scene = None
        self.player_sprite = None
        self.enemy_list = None
        self.coin_list = None  # Liste pour les pièces
        self.physics_engine = None
        self.timer = TIMER_START
        self.money = INITIAL_MONEY
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Configure le jeu ici. Appelez cette fonction pour redémarrer le jeu."""

        self.scene = arcade.Scene()

        # Configurer le joueur, en le plaçant à une position libre dans le labyrinthe
        image_source = ":resources:images/animated_characters/male_person/malePerson_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.place_player()

        self.scene.add_sprite("Player", self.player_sprite)

        # Créer les murs et autres objets du labyrinthe à partir du tableau
        self.create_maze()
        
        # Créer le moteur physique
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

    def place_player(self):
        """Place le joueur dans une position libre du labyrinthe."""
        while True:
            row = random.randint(0, MAP_HEIGHT - 1)
            col = random.randint(0, MAP_WIDTH - 1)
            if MAZE_MAP[row][col] == 0:
                self.player_sprite.center_x = col * TILE_SIZE + TILE_SIZE / 2
                self.player_sprite.center_y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE / 2)
                break

    def create_maze(self):
        """Crée le labyrinthe en fonction du tableau MAZE_MAP."""

        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                x = col * TILE_SIZE + TILE_SIZE / 2
                y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE / 2)
                if MAZE_MAP[row][col] == 1:
                    # Créer un mur
                    wall = arcade.Sprite(":resources:images/tiles/dirtHalf.png", TILE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    self.scene.add_sprite("Walls", wall)
                elif MAZE_MAP[row][col] == 0:
                    # Placer des pièces ou des ennemis aléatoirement
                    if random.choice([True, False]):  # Chance de 50% pour une pièce
                        coin = arcade.Sprite(":resources:images/items/coinGold_ul.png", TILE_SCALING)
                        coin.center_x = x
                        coin.center_y = y
                        self.coin_list.append(coin)
                        self.scene.add_sprite("Coins", coin)
                    else:
                        enemy = arcade.Sprite("blastalot-wings-crouch-alpha.png", CHARACTER_SCALING)
                        enemy.center_x = x
                        enemy.center_y = y
                        self.enemy_list.append(enemy)
                        self.scene.add_sprite("Enemies", enemy)

    def on_update(self, delta_time):
        """Mouvement et logique du jeu"""

        # Mettre à jour le moteur physique
        self.physics_engine.update()

        # Vérifier les collisions entre le joueur et les ennemis
        enemies_hit = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
        for enemy in enemies_hit:
            self.create_coin_from_enemy(enemy)
            enemy.remove_from_sprite_lists()

        # Vérifier les collisions entre le joueur et les pièces
        coins_hit = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coins_hit:
            self.money += COIN_VALUE
            coin.remove_from_sprite_lists()

        # Décrémenter le timer
        self.timer -= delta_time
        if self.timer < 0:
            self.timer = 0

    def create_coin_from_enemy(self, enemy):
        """Crée une pièce à l'emplacement de l'ennemi mort et l'ajoute à la liste des pièces."""
        coin = arcade.Sprite(":resources:images/items/coinGold_ul.png", TILE_SCALING)
        coin.center_x = enemy.center_x
        coin.center_y = enemy.center_y
        self.coin_list.append(coin)
        self.scene.add_sprite("Coins", coin)

    def on_draw(self):
        """Rend l'écran."""

        self.clear()
        self.scene.draw()

        minutes, seconds = divmod(int(self.timer), 60)
        arcade.draw_text(f"Life Time : {minutes:02}:{seconds:02}", 10, 10, arcade.color.BLACK, 16)
        arcade.draw_text(f"Argent : {self.money}", SCREEN_WIDTH - 200, 10, arcade.color.BLACK, 16)

    def on_key_press(self, key, modifiers):
        """Appelé à chaque fois qu'une touche est enfoncée"""
        if key == arcade.key.UP:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Appelé à chaque fois qu'une touche est relâchée"""
        if key == arcade.key.UP or key == arcade.key.DOWN:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

def main():
    """Fonction principale"""
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
