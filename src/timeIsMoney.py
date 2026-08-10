import arcade
import random

# Constantes
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Time Is Money"

# Redimensionnement des sprites
CHARACTER_SCALING = 0.5
TILE_SCALING = 0.5

# Vitesse du joueur
PLAYER_MOVEMENT_SPEED = 5
POWER_UP_SPEED_BONUS = 4
POWER_UP_DURATION = 8.0

# Timer et argent
TIMER_START = 90  # 1min30 pour une partie qui se termine réellement
INITIAL_MONEY = 0
COIN_VALUE = 10

# Ennemis
ENEMY_SPEED = 2
ENEMY_COUNT = 3
ENEMY_PENALTY = 20
ENEMY_HIT_COOLDOWN = 1.5  # secondes d'invulnérabilité après un contact

# Taille des tuiles et dimensions du labyrinthe
TILE_SIZE = 64
MAP_WIDTH = 12
MAP_HEIGHT = 9

# États du jeu
STATE_TITLE = "TITLE"
STATE_PLAYING = "PLAYING"
STATE_WIN = "WIN"
STATE_LOSE = "LOSE"

# Labyrinthe
MAZE_MAP = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]


class MyGame(arcade.Window):
    """
    Time Is Money : labyrinthe avec boutique, ennemis et chrono de survie.
    """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.scene = None
        self.player_sprite = None
        self.enemy_list = None
        self.coin_list = None
        self.physics_engine = None
        self.timer = TIMER_START
        self.money = INITIAL_MONEY
        self.game_state = STATE_TITLE

        # Power up
        self.power_up_time_left = 0.0

        # Ennemis / invulnérabilité
        self.enemy_hit_cooldown = 0.0

        # Objectif
        self.total_coins = 0

        # Sons
        self.sound_coin = arcade.load_sound(":resources:sounds/coin1.wav")
        self.sound_hit = arcade.load_sound(":resources:sounds/hit1.wav")
        self.sound_powerup = arcade.load_sound(":resources:sounds/upgrade1.wav")
        self.sound_win = arcade.load_sound(":resources:sounds/gameover1.wav")
        self.sound_lose = arcade.load_sound(":resources:sounds/gameover2.wav")

        # Textes pré-construits (plus performant que draw_text)
        self.text_timer = arcade.Text("", 10, 10, arcade.color.BLACK, 16)
        self.text_money = arcade.Text("", SCREEN_WIDTH - 200, 10, arcade.color.BLACK, 16)
        self.text_shop_title = arcade.Text("Boutique", SCREEN_WIDTH - 220, SCREEN_HEIGHT - 50, arcade.color.BLACK, 24)
        self.text_shop_1 = arcade.Text("1. Power Up - $50", SCREEN_WIDTH - 220, SCREEN_HEIGHT - 100, arcade.color.BLACK, 16)
        self.text_shop_2 = arcade.Text("2. 10min for $100", SCREEN_WIDTH - 220, SCREEN_HEIGHT - 150, arcade.color.BLACK, 16)
        self.text_goal = arcade.Text("", SCREEN_WIDTH - 220, SCREEN_HEIGHT - 190, arcade.color.BLACK, 16)
        self.text_powerup_status = arcade.Text("", 10, SCREEN_HEIGHT - 30, arcade.color.ORANGE, 16, bold=True)

        self.text_title = arcade.Text(
            "TIME IS MONEY", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
            arcade.color.BLACK, 40, anchor_x="center", bold=True
        )
        self.text_title_sub = arcade.Text(
            "Ramasse toutes les pièces avant la fin du chrono. Evite les ennemis !",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10,
            arcade.color.DARK_SLATE_GRAY, 18, anchor_x="center"
        )
        self.text_title_prompt = arcade.Text(
            "Appuyez sur ESPACE pour jouer", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 40,
            arcade.color.BLACK, 20, anchor_x="center"
        )

        self.text_end_title = arcade.Text(
            "", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 40,
            arcade.color.BLACK, 44, anchor_x="center", bold=True
        )
        self.text_end_score = arcade.Text(
            "", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10,
            arcade.color.BLACK, 20, anchor_x="center"
        )
        self.text_end_prompt = arcade.Text(
            "ESPACE pour rejouer   -   ECHAP pour quitter", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60,
            arcade.color.BLACK, 18, anchor_x="center"
        )

        arcade.set_background_color(arcade.csscolor.LIGHT_SKY_BLUE)

    def setup(self):
        """Configure une nouvelle partie."""
        self.scene = arcade.Scene()

        # Configuration du joueur
        image_source = ":resources:images/animated_characters/male_person/malePerson_idle.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)

        # Créer le labyrinthe (murs + pièces + ennemis)
        self.create_maze()

        self.place_player()
        self.scene.add_sprite("Player", self.player_sprite)

        # Créer le moteur physique
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.scene.get_sprite_list("Walls"))

        self.timer = TIMER_START
        self.money = INITIAL_MONEY
        self.power_up_time_left = 0.0
        self.enemy_hit_cooldown = 0.0
        self.total_coins = len(self.coin_list)
        self.game_state = STATE_PLAYING

    def free_tiles(self):
        """Retourne la liste des cases (row, col) libres du labyrinthe."""
        return [
            (row, col)
            for row in range(MAP_HEIGHT)
            for col in range(MAP_WIDTH)
            if MAZE_MAP[row][col] == 0
        ]

    def tile_to_pixels(self, row, col):
        x = col * TILE_SIZE + TILE_SIZE / 2
        y = SCREEN_HEIGHT - (row * TILE_SIZE + TILE_SIZE / 2) - 50 + TILE_SIZE
        return x, y

    def place_player(self):
        """Place le joueur sur une case libre, sans chevaucher une pièce ou un ennemi."""
        occupied = {(round(s.center_x), round(s.center_y)) for s in self.coin_list}
        occupied |= {(round(s.center_x), round(s.center_y)) for s in self.enemy_list}

        candidates = self.free_tiles()
        random.shuffle(candidates)
        for row, col in candidates:
            x, y = self.tile_to_pixels(row, col)
            if (round(x), round(y)) not in occupied:
                self.player_sprite.center_x = x
                self.player_sprite.center_y = y
                return

        # Repli si jamais tout est occupé (ne devrait pas arriver)
        row, col = candidates[0]
        x, y = self.tile_to_pixels(row, col)
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y

    def create_maze(self):
        """Crée le labyrinthe : murs, pièces (une par case libre) et ennemis."""
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()

        free_positions = []

        for row in range(MAP_HEIGHT):
            for col in range(MAP_WIDTH):
                x, y = self.tile_to_pixels(row, col)
                if MAZE_MAP[row][col] == 1:
                    wall = arcade.Sprite(":resources:images/tiles/dirtHalf.png", TILE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    self.scene.add_sprite("Walls", wall)
                else:
                    free_positions.append((row, col, x, y))

        # Une pièce sur environ une case libre sur deux, sans jamais se superposer
        random.shuffle(free_positions)
        coin_spots = free_positions[: max(1, len(free_positions) // 2)]
        for row, col, x, y in coin_spots:
            coin = arcade.Sprite(":resources:images/items/coinGold_ul.png", TILE_SCALING)
            coin.center_x = x
            coin.center_y = y
            self.coin_list.append(coin)
            self.scene.add_sprite("Coins", coin)

        # Ennemis : placés sur des cases libres restées sans pièce si possible
        coin_coords = {(x, y) for _, _, x, y in coin_spots}
        enemy_candidates = [p for p in free_positions if (p[2], p[3]) not in coin_coords]
        if len(enemy_candidates) < ENEMY_COUNT:
            enemy_candidates = free_positions

        random.shuffle(enemy_candidates)
        for i in range(min(ENEMY_COUNT, len(enemy_candidates))):
            _, _, x, y = enemy_candidates[i]
            enemy = arcade.Sprite(":resources:images/animated_characters/zombie/zombie_idle.png", CHARACTER_SCALING)
            enemy.center_x = x
            enemy.center_y = y
            # Direction de patrouille aléatoire (horizontale ou verticale)
            if random.choice([True, False]):
                enemy.change_x = random.choice([-1, 1]) * ENEMY_SPEED
            else:
                enemy.change_y = random.choice([-1, 1]) * ENEMY_SPEED
            self.enemy_list.append(enemy)
            self.scene.add_sprite("Enemies", enemy)

    def update_enemies(self, delta_time):
        """Fait patrouiller les ennemis et les fait rebondir sur les murs."""
        walls = self.scene.get_sprite_list("Walls")
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            enemy.center_y += enemy.change_y

            hit_wall = arcade.check_for_collision_with_list(enemy, walls)
            out_of_bounds = not (0 <= enemy.center_x <= SCREEN_WIDTH and 0 <= enemy.center_y <= SCREEN_HEIGHT)
            if hit_wall or out_of_bounds:
                enemy.center_x -= enemy.change_x
                enemy.center_y -= enemy.change_y
                enemy.change_x *= -1
                enemy.change_y *= -1

    def trigger_power_up(self):
        self.power_up_time_left = POWER_UP_DURATION
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0
        arcade.play_sound(self.sound_powerup)

    def current_speed(self):
        if self.power_up_time_left > 0:
            return PLAYER_MOVEMENT_SPEED + POWER_UP_SPEED_BONUS
        return PLAYER_MOVEMENT_SPEED

    def end_game(self, won):
        self.game_state = STATE_WIN if won else STATE_LOSE
        arcade.play_sound(self.sound_win if won else self.sound_lose)

    def on_update(self, delta_time):
        if self.game_state != STATE_PLAYING:
            return

        self.physics_engine.update()
        self.update_enemies(delta_time)

        # Power up : décompte
        if self.power_up_time_left > 0:
            self.power_up_time_left = max(0.0, self.power_up_time_left - delta_time)

        # Invulnérabilité après un coup
        if self.enemy_hit_cooldown > 0:
            self.enemy_hit_cooldown = max(0.0, self.enemy_hit_cooldown - delta_time)

        # Collisions avec les pièces
        coins_hit = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)
        for coin in coins_hit:
            self.money += COIN_VALUE
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.sound_coin)

        # Collisions avec les ennemis
        if self.enemy_hit_cooldown <= 0:
            enemies_hit = arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)
            if enemies_hit:
                self.money = max(0, self.money - ENEMY_PENALTY)
                self.enemy_hit_cooldown = ENEMY_HIT_COOLDOWN
                arcade.play_sound(self.sound_hit)

        # Condition de victoire : toutes les pièces ramassées
        if self.total_coins > 0 and len(self.coin_list) == 0:
            self.end_game(won=True)
            return

        # Décrémenter le timer
        self.timer -= delta_time
        if self.timer <= 0:
            self.timer = 0
            self.end_game(won=False)

    def on_draw(self):
        self.clear()

        if self.game_state == STATE_TITLE:
            self.draw_title_screen()
            return

        self.scene.draw()

        # Halo visuel simple pendant le power up
        if self.power_up_time_left > 0:
            arcade.draw_circle_outline(
                self.player_sprite.center_x, self.player_sprite.center_y,
                26, arcade.color.ORANGE, 3
            )

        minutes, seconds = divmod(int(self.timer), 60)
        self.text_timer.text = f"Life Time : {minutes:02}:{seconds:02}"
        self.text_timer.draw()

        self.text_money.text = f"Argent : {self.money}"
        self.text_money.draw()

        self.text_shop_title.draw()
        self.text_shop_1.draw()
        self.text_shop_2.draw()

        coins_left = len(self.coin_list)
        self.text_goal.text = f"Pièces restantes : {coins_left}/{self.total_coins}"
        self.text_goal.draw()

        if self.power_up_time_left > 0:
            self.text_powerup_status.text = f"Power Up actif : {self.power_up_time_left:0.1f}s"
            self.text_powerup_status.draw()

        if self.game_state in (STATE_WIN, STATE_LOSE):
            self.draw_end_screen()

    def draw_title_screen(self):
        self.text_title.draw()
        self.text_title_sub.draw()
        self.text_title_prompt.draw()

    def draw_end_screen(self):
        arcade.draw_lrbt_rectangle_filled(
            0, SCREEN_WIDTH, 0, SCREEN_HEIGHT, (0, 0, 0, 160)
        )
        if self.game_state == STATE_WIN:
            self.text_end_title.text = "VICTOIRE !"
            self.text_end_title.color = arcade.color.GOLD
        else:
            self.text_end_title.text = "GAME OVER"
            self.text_end_title.color = arcade.color.RED

        self.text_end_title.draw()

        self.text_end_score.text = f"Argent final : {self.money}   |   Pièces ramassées : {self.total_coins - len(self.coin_list)}/{self.total_coins}"
        self.text_end_score.draw()

        self.text_end_prompt.draw()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.ESCAPE:
            self.close()
            return

        if self.game_state == STATE_TITLE:
            if key == arcade.key.SPACE:
                self.setup()
            return

        if self.game_state in (STATE_WIN, STATE_LOSE):
            if key == arcade.key.SPACE:
                self.setup()
            return

        # STATE_PLAYING
        speed = self.current_speed()
        if key == arcade.key.UP:
            self.player_sprite.change_y = speed
        elif key == arcade.key.DOWN:
            self.player_sprite.change_y = -speed
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -speed
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = speed
        elif key == arcade.key.KEY_1:  # Acheter un power-up
            if self.money >= 50 and self.power_up_time_left <= 0:
                self.money -= 50
                self.trigger_power_up()
        elif key == arcade.key.KEY_2:  # Acheter du temps
            if self.money >= 100:
                self.money -= 100
                self.timer += 60

    def on_key_release(self, key, modifiers):
        if self.game_state != STATE_PLAYING:
            return
        if key in (arcade.key.UP, arcade.key.DOWN):
            self.player_sprite.change_y = 0
        elif key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player_sprite.change_x = 0


def main():
    """Fonction principale."""
    window = MyGame()
    arcade.run()


if __name__ == "__main__":
    main()
