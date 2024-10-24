class GameStats:
    """track statistics for Alien Invasion."""

    def __init__(self, ai_game):
        """Inititalize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False

        # Initialize high_score
        self.high_score = 0  # Default value
        self.update_high_score()

        self.level = 1

    def reset_stats(self):
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def update_high_score(self):
         # Attempt to read high score from file
        try:
            with open('high_score.txt') as score_object:
                hs = score_object.read().strip()  # Read and strip whitespace
                if hs:  # Check if hs is not an empty string
                    self.high_score = int(hs)  # Convert to integer
        except FileNotFoundError:
            # If the file doesn't exist, we can keep the default value
            print("High score file not found. Starting with high score of 0.")
        except ValueError:
            # Handle the case where the file contains invalid data
            print("Invalid data in high score file. Starting with high score of 0.")

