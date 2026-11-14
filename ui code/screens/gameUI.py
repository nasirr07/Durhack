# Import modules
from scripts.settings import *
from scripts.screens.screenTemplate import *

# Use a class to create the screen
class gameUI(screenTemplate):
    # Initialise the class with a constructor
    def __init__(self, game, screen, settings, controls):
        # Initialise the parent class
        super().__init__(game, screen, settings, controls)
        # Initialise extra variables
        self.lastScreen = "save"

    # Create a subroutine to update the screen
    def update(self, deltaTime):
        self.updateWidgets()
        
    # Create a subroutine to draw the screen
    def draw(self):
        self.drawWidgets()