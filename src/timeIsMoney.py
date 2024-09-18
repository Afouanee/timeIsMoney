import arcade

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

class MyGame(arcade.Window):
    """
    Classe principale de l'application.
    """

    def __init__(self):
        # Appelle la classe parente et configure la fenêtre
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Objet Scene
        self.scene = None

        # Variable séparée qui contient le sprite du joueur
        self.player_sprite = None

        # Notre moteur physique
        self.physics_engine = None

        # Timer
        self.timer = TIMER_START

        # Score d'argent
        self.money = INITIAL_MONEY

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        """Configure le jeu ici. Appelez cette fonction pour redémarrer le jeu."""

        # Initialiser la scène
        self.scene = arcade.Scene()

        # Configurer le joueur, en le plaçant spécifiquement à ces coordonnées
        image_source = ":resources:images/animated_characters/male_person/malePerson_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128
        self.scene.add_sprite("Player", self.player_sprite)

        # Créer le sol
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/dirtHalf.png", TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            self.scene.add_sprite("Walls", wall)

        # Placer des meubles sur le sol
        coordinate_list = [[512, 96], [256, 96], [768, 96]]

        for coordinate in coordinate_list:
            # Ajouter un meuble sur le sol
            wall = arcade.Sprite(
                ":resources:images/items/coinGold_ul.png", TILE_SCALING  # Changez pour un sprite de meuble si nécessaire
            )
            wall.position = coordinate
            self.scene.add_sprite("Walls", wall)

        # Créer le moteur physique
        self.physics_engine = arcade.PhysicsEngineSimple(
            self.player_sprite, self.scene.get_sprite_list("Walls")
        )

    def on_draw(self):
        """Rend l'écran."""

        # Effacer l'écran avec la couleur de fond
        self.clear()

        # Dessiner notre scène
        self.scene.draw()

        # Dessiner le timer
        minutes = int(self.timer // 60)
        seconds = int(self.timer % 60)
        timer_text = f"Temps restant : {minutes:02}:{seconds:02}"
        arcade.draw_text(timer_text, 10, SCREEN_HEIGHT - 40, arcade.color.BLACK, 16)

        # Dessiner le score d'argent
        money_text = f"Argent : ${self.money}"
        arcade.draw_text(money_text, 10, SCREEN_HEIGHT - 80, arcade.color.BLACK, 16)

    def on_key_press(self, key, modifiers):
        """Appelé lorsque une touche est pressée."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """Appelé lorsque l'utilisateur relâche une touche."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

    def on_update(self, delta_time):
        """Mouvement et logique du jeu"""

        # Déplacer le joueur avec le moteur physique
        self.physics_engine.update()

        # Mettre à jour le timer
        self.timer -= delta_time
        if self.timer < 0:
            self.timer = 0

def main():
    """Fonction principale"""
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
