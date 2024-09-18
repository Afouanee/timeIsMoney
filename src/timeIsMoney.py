import arcade
import random

# Constantes
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

# Constantes utilisées pour redimensionner nos sprites par rapport à leur taille originale
CHARACTER_SCALING = 1
TILE_SCALING = 0.5

# Vitesse de déplacement du joueur, en pixels par frame
PLAYER_MOVEMENT_SPEED = 5

# Constantes du timer
TIMER_START = 24 * 60 * 60  # 24 heures en secondes

# Constantes du score
INITIAL_MONEY = 0
COIN_VALUE = 10

# Constantes du labyrinthe
TILE_SIZE = 64
WALLS = [
    # (x, y) coordonnées des murs
    (200, 200), (300, 200), (400, 200), (500, 200),
    (200, 300), (500, 300),
    (200, 400), (300, 400), (400, 400), (500, 400),
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

        # Configurer le joueur, en le plaçant spécifiquement à ces coordonnées
        image_source = ":resources:images/animated_characters/male_person/malePerson_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Créer les murs du labyrinthe
        for (x, y) in WALLS:
            wall = arcade.Sprite(":resources:images/tiles/dirtHalf.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = SCREEN_HEIGHT - y
            self.scene.add_sprite("Walls", wall)

        # Créer les pièces
        self.coin_list = arcade.SpriteList()
        self.place_coins()

        # Créer les ennemis
        self.enemy_list = arcade.SpriteList()
        self.create_enemies()

        # Créer le moteur physique
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

    def place_coins(self):
        """Place des pièces aléatoirement dans le labyrinthe."""
        for _ in range(10):  # Nombre de pièces à placer
            while True:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)
                if not any(abs(x - wx) < TILE_SIZE and abs(y - wy) < TILE_SIZE for wx, wy in WALLS):
                    coin = arcade.Sprite(":resources:images/items/coinGold_ul.png", TILE_SCALING)
                    coin.center_x = x
                    coin.center_y = y
                    self.coin_list.append(coin)
                    self.scene.add_sprite("Coins", coin)
                    break

    def create_enemies(self):
        """Crée des ennemis et les place dans la scène."""

        num_enemies = 5  # Nombre d'ennemis
        for _ in range(num_enemies):
            while True:
                x = random.randint(100, SCREEN_WIDTH - 100)
                y = random.randint(100, SCREEN_HEIGHT - 100)
                if not any(abs(x - wx) < TILE_SIZE and abs(y - wy) < TILE_SIZE for wx, wy in WALLS):
                    enemy = arcade.Sprite("blastalot-wings-crouch-alpha.png", CHARACTER_SCALING)
                    enemy.center_x = x
                    enemy.center_y = y
                    self.enemy_list.append(enemy)
                    self.scene.add_sprite("Enemies", enemy)
                    break

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
        arcade.draw_text(f"Temps restant : {minutes:02}:{seconds:02}", 10, SCREEN_HEIGHT - 40, arcade.color.BLACK, 16)
        arcade.draw_text(f"Argent : {self.money}", 10, SCREEN_HEIGHT - 60, arcade.color.BLACK, 16)

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
