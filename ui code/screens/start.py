# Import modules
from scripts.settings import *
from scripts.screens.screenTemplate import *

# Use a class to create the screen
class startScreen(screenTemplate):
    # Initialise the class with a constructor
    def __init__(self, game, screen, settings, controls):
        # Initialise the parent class
        super().__init__(game, screen, settings, controls)
        
        # Remove the return button from the buttons dictionary
        del self.buttons["return"]
        # Add buttons to the buttons dictionary
        self.buttons["play"] = \
            self.createButton("center", "center", self.game.startGame, text="START", offset=(0, -100))
        self.buttons["settings"] = \
            self.createButton("center", "center", self.game.goSettings, text="SETTINGS", offset=(0, 0))
        self.buttons["controls"] = \
            self.createButton("center", "center", self.game.goControls, text="CONTROLS", offset=(0, 100))
        self.buttons["quit"] = \
            self.createButton("center", "center", self.game.doQuitGame, text="QUIT", offset=(0, 200))
        
        # Add to the text dictionary
        self.texts["title"] = \
            text(self.settings, "center", 50, WHITE, "TITLE", font=self.settings["largeFont"],
                doSineY=True, shadowOffset=(-7, 7))
        
    # Create a subroutine to update the screen
    def update(self, deltaTime):
        self.updateWidgets()
        
    # Create a subroutine to draw the screen
    def draw(self):
        self.drawBackground()
        self.drawWidgets()
        self.drawnFrame = True