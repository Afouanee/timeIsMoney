import arcade
import os
import sys

SCREEN_WIDTH = 724
SCREEN_HEIGHT = 724
SCREEN_TITLE = "Main Menu"

class Button(arcade.SpriteSolidColor):
    def __init__(self, width, height, color, hover_color, text, font_color, font_size):
        super().__init__(width, height, color)
        self.hover_color = hover_color
        self.original_color = color
        self.text = text
        self.font_color = font_color
        self.font_size = font_size
        self.is_hovered = False

    def on_draw(self):
        # Draw the button
        self.draw()
        # Draw the text on the button
        arcade.draw_text(self.text, self.center_x, self.center_y,
                         color=self.font_color, font_size=self.font_size,
                         anchor_x="center", anchor_y="center")

    def check_hover(self, x, y):
        """Check if the mouse is hovering over the button."""
        if self.collides_with_point((x, y)):
            self.color = self.hover_color
            self.is_hovered = True
        else:
            self.color = self.original_color
            self.is_hovered = False

class Menu(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.AMAZON)
        
        # Load background image
        self.background_texture = arcade.load_texture(os.path.join("../resources/", "affiche.png"))
        
        # Create the "Play" button
        self.start_button = Button(
            200, 50, arcade.color.WHITE, arcade.color.PURPLE, 
            "Jouer", arcade.color.BLACK, 20
        )
        self.start_button.center_x = width // 2
        self.start_button.center_y = height // 1.5

    def on_draw(self):
        self.clear()
        # Draw the background image
        arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                                      SCREEN_WIDTH, SCREEN_HEIGHT,
                                      self.background_texture)
        self.start_button.on_draw()

    def on_mouse_motion(self, x, y, dx, dy):
        """Update button color based on hover state."""
        self.start_button.check_hover(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.start_button.is_hovered:
            print("Start button clicked!")
            # Launch the game and close the menu window
            self.start_game()

    def start_game(self):
        """Launch the timetwister.py file and close the menu window."""
        # Get the absolute path to timetwister.py
        timetwister_path = os.path.join(os.path.dirname(__file__), 'TimeTwister.py')
        # Replace the current process with timetwister.py
        os.execv(sys.executable, [sys.executable, timetwister_path])
        # Close the menu window (this line will not be reached due to os.execv)
        self.close()

def main():
    window = Menu(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()
    my_sound = arcade.load_sound("/home/roland/PycharmProjects/timeIsMoney/resources/The Unwound Future.mp3")
    arcade.play_sound(my_sound)

if __name__ == "__main__":
    main()
