import arcade
import threading
import time
from collections import deque

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Better Move Sprite with Keyboard Example"

MOVEMENT_SPEED = 5
TELEPORT_INTERVAL = 10  # Seconds
TELEPORT_COOLDOWN = 3  # Minimum time between teleports in seconds
TRAIL_LENGTH = 100  # Number of positions to keep for the trail
REWIND_SPEED = 20  # Speed of the rewind animation
POINT_SKIP = 2  # Number of points to skip to increase rewind speed


class Player(arcade.Sprite):
    def update(self):
        """ Move the player """
        self.center_x += self.change_x
        self.center_y += self.change_y

        # Check for out-of-bounds
        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

        if self.bottom < 0:
            self.bottom = 0
        elif self.top > SCREEN_HEIGHT - 1:
            self.top = SCREEN_HEIGHT - 1


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        """ Initializer """
        super().__init__(width, height, title)

        # Variables that will hold sprite lists
        self.player_list = None
        self.obstacle1 = None

        # Set up the player info
        self.player_sprite = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        self.bouton1 = False
        self.bouton2 = False
        self.bouton3 = False

        # List to store player positions for teleportation
        self.position_history = deque(maxlen=int(TELEPORT_INTERVAL / 0.1))  # Store positions for last 5 seconds

        # List to store the trail positions
        self.trail = deque(maxlen=TRAIL_LENGTH)  # Store positions for trail effect

        # List to store the reverse path for the rewind effect
        self.reverse_path = []

        # Track time of last teleport
        self.last_teleport_time = 0

        # Rewinding state flag
        self.is_rewinding = False

        # Thread control flag
        self.thread_started = False

    def setup(self):
        """ Set up the game and initialize the variables. """
        # Sprite lists
        self.player_list = arcade.SpriteList()
        #self.obstacle_list = arcade.SpriteList()

        # Set up the player
        self.player_sprite = Player(":resources:images/animated_characters/female_person/femalePerson_idle.png", SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        # Set up an obstacle
        self.obstacle1 = arcade.Sprite("/home/roland/PycharmProjects/timeIsMoney/resources/NonPressedBouton.png", SPRITE_SCALING / 2.5)
        self.obstacle1.center_x = 400
        self.obstacle1.center_y = 300
        #self.obstacle_list.append(obstacle1)

        # Start the thread to print player position every 5 seconds
        if not self.thread_started:
            self.position_thread = threading.Thread(target=self.print_player_position)
            self.position_thread.daemon = True
            self.position_thread.start()
            self.thread_started = True

    def on_draw(self):
        """ Render the screen. """
        self.clear()
        # Draw the trail only if not rewinding
        if not self.is_rewinding:
            self.draw_trail()

        # Draw all the sprites.
        self.obstacle1.draw()
        self.player_list.draw()

    def update_player_speed(self):
        """ Calculate speed based on the keys pressed """
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -MOVEMENT_SPEED

        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def first_boutons(self):
        if arcade.check_for_collision(self.player_sprite, self.obstacle1):
            self.obstacle1 = arcade.Sprite("/home/roland/PycharmProjects/timeIsMoney/resources/PressedBouton.png", SPRITE_SCALING / 2.5)
            self.obstacle1.center_x = 400
            self.obstacle1.center_y = 300

    def on_update(self, delta_time):
        """ Movement and game logic """
        # Call update to move the sprite
        self.player_list.update()
        self.first_boutons()

        # Save the player's position every update
        self.save_player_position()

        # Update the trail positions
        self.update_trail()

        # Rewind if the player is in rewind mode
        if self.is_rewinding:
            self.rewind_movement()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
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
        """Called when the user releases a key. """
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
        """Save the current player position to history."""
        if not self.is_rewinding:
            current_position = (self.player_sprite.center_x, self.player_sprite.center_y)
            self.position_history.append(current_position)

    def update_trail(self):
        """Update the trail positions with the current player position."""
        if not self.is_rewinding:
            current_position = (self.player_sprite.center_x, self.player_sprite.center_y)
            self.trail.append(current_position)

    def draw_trail(self):
        """Draw the player's trail."""
        if len(self.trail) > 1:
            arcade.draw_line_strip(self.trail, arcade.color.YELLOW, 2)

    def start_rewind(self):
        """Initiate the rewind process to the position the player was at 5 seconds ago."""
        current_time = time.time()
        if current_time - self.last_teleport_time >= TELEPORT_COOLDOWN:
            if len(self.position_history) >= int(TELEPORT_INTERVAL / 0.1):
                # Clear the trail to avoid showing a line from the old to new position
                self.trail.clear()

                # Prepare the reverse path
                # Skip points in reverse path to accelerate the rewind
                self.reverse_path = list(self.position_history)[::-POINT_SKIP]  # Skip points for faster rewind
                self.is_rewinding = True
                print("Rewind started...")
        else:
            print("Rewind is on cooldown. Please wait.")

    def rewind_movement(self):
        """Move the player along the reverse path."""
        if self.reverse_path:
            target_x, target_y = self.reverse_path.pop(0)
            direction_x = target_x - self.player_sprite.center_x
            direction_y = target_y - self.player_sprite.center_y

            distance = (direction_x ** 2 + direction_y ** 2) ** 0.5

            if distance > REWIND_SPEED:
                # Move the player towards the target at REWIND_SPEED
                direction_x /= distance
                direction_y /= distance

                self.player_sprite.center_x += direction_x * REWIND_SPEED
                self.player_sprite.center_y += direction_y * REWIND_SPEED
            else:
                # Snap to the position if close enough
                self.player_sprite.center_x = target_x
                self.player_sprite.center_y = target_y
        else:
            # Rewind complete
            self.is_rewinding = False
            self.last_teleport_time = time.time()
            print("Rewind completed.")

    def print_player_position(self):
        """Prints the player's position every 5 seconds."""
        while True:
            if self.player_sprite is not None:
                print(f"Position du joueur: x={self.player_sprite.center_x}, y={self.player_sprite.center_y}")
            time.sleep(5)

def main():
    """ Main function """
    window = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
