# Import modules
from scripts.screens.screenTemplate import *

# Use a class to create the screen
class settingsScreen(screenTemplate):
    # Initialise the class with a constructor
    def __init__(self, game, screen, settings, controls):
        # Initialise the parent class
        super().__init__(game, screen, settings, controls)
        
        # Add to the buttons dictionary
        self.buttons["apply"] = self.createButton(
            "center", "bottom", self.changeSettings, None, (0, -100), text="APPLY"
        )

        startX = 75
        startY = 250
        seperationY = 100
        seperationX = 450
        
        resolutions = ["1920x1080", "1600x900", "1280x720", "1120x630", "960x540", "800x600","800x450"]
        
        # Add to the droplist dictionary
        self.droplists["resolution"] = \
            droplist(self.settings, startX+seperationX, startY+10, items=resolutions,
                    command=self.changeResolution, label="RESOLUTION", currentItem=f"{self.settings['windowSize'][0]}x{self.settings['windowSize'][1]}")
        self.droplists["maxFps"] = \
            droplist(self.settings, startX+seperationX*1.5, startY+10, items=[0, 30, 60, 120, 144, 165, 200, 240, 360],
                    command=self.changeFps, label="FPS", currentItem=self.settings["maxFps"])

        # Add to the checkbox dictionary
        self.checkboxes["shadows"] = \
            checkbox(self.settings, startX, startY, 75, 75, label="GAME\nSHADOWS", labelFont=self.settings["mediumFont"],
                    checked=self.settings["enableShadows"], boxCurve=self.buttonAttrs["curve"],
                    command=self.toggleShadows)
        self.checkboxes["fullscreen"] = \
            checkbox(self.settings, startX, startY+seperationY, 75, 75, label="FULLSCREEN", labelFont=self.settings["mediumFont"],
                    checked=self.settings["fullscreen"], boxCurve=self.buttonAttrs["curve"],
                    command=self.toggleFullscreen)
        self.checkboxes["clickParticles"] = \
            checkbox(self.settings, startX, startY+seperationY*2, 75, 75, label="CLICK\nPARTICLES", labelFont=self.settings["mediumFont"],
                    checked=self.settings["fullscreen"], boxCurve=self.buttonAttrs["curve"],
                    command=self.toggleParticles)

        # Add to the text dictionary
        self.texts["title"] = \
            text(self.settings, "center", 50, WHITE, "SETTINGS", font=self.settings["largeFont"],
                doSineY=True, shadowOffset=(-7, 7))
        
        # Create a copy of the settings to not directly alter the games settings without applying
        self.settingsCopy = self.settings.copy()
        # Create a flag to keep track if the window has been changed in any way
        self.changedWindow = False

    # Subroutine to enable the lists to be mouse scrolled
    def doListMouseScroll(self, event, dt):
        # Loop through the drop lists
        for name, dlist in self.droplists.items():
            # Call their scroll function
            dlist.scrollMouse(event, dt, self.game.mouseRect)

    # Subroutine to go to back to the previous screen
    def returnLastScreen(self):
        self.game.toBeCurrentScreen = self.lastScreen
        self.drawnFrame = False
        self.game.startedTransition = True
        self.changedWindow = False

    # Create a subroutine to change the resolution of the game
    def changeResolution(self, res):
        # Set the settings to the value
        self.settingsCopy["windowSize"] = (int(res.split("x")[0]), int(res.split("x")[1]))
        # Set the changed window flag to true
        self.changedWindow = True

    # Create a subroutine to change the max fps of the game
    def changeFps(self, fps):
        # Set the settings to the value
        self.settingsCopy["maxFps"] = int(fps)

    # Create a subroutine to toggle the click particles
    def toggleParticles(self, checkVal):
        # Set the settings to the value
        if checkVal:
            self.settingsCopy["clickParticles"] = SETTINGS["clickParticles"]
        else:
            self.settingsCopy["clickParticles"] = 0

    # Create a subroutine to toggle fullscreen
    def toggleFullscreen(self, checkVal):
        # Set the settings to the value
        self.settingsCopy["fullscreen"] = checkVal
        # Set the changed window flag to true
        self.changedWindow = True

    # Create a subroutine to toggle the games text shadows
    def toggleShadows(self, checkVal):
        # Set the settings to the value
        self.settingsCopy["enableShadows"] = checkVal
        
    # Create a subroutine to set the widgets to the games settings
    def setOriginalSettings(self, settings):
        self.settings = settings.copy()
        self.settingsCopy["windowSize"] = self.settings["windowSize"]
        # Set the checkboxes to their settings state
        self.checkboxes["shadows"].checked = self.settings["enableShadows"]
        self.checkboxes["fullscreen"].checked = self.settings["fullscreen"]
        if self.settings["clickParticles"] == 0:
            self.checkboxes["clickParticles"].checked = False
        else:
            self.checkboxes["clickParticles"].checked = True
        # Set the selected items of the drop lists
        self.droplists["resolution"].currentItem = f"{self.settings['windowSize'][0]}x{self.settings['windowSize'][1]}"
        self.droplists["resolution"].createContents()
        self.droplists["maxFps"].currentItem = self.settings["maxFps"]
        self.droplists["maxFps"].createContents()

    # Create a subroutine to sync the new settings with the games main settings
    def changeSettings(self):
        self.game.setNewSettings(self.settingsCopy)
        self.game.updateSettings(self.changedWindow)
        # Reset any flags
        self.changedWindow = False

    # Create a subroutine to update the screen
    def update(self, deltaTime):
        self.updateWidgets()
        
    # Create a subroutine to draw the screen
    def draw(self):
        self.drawBackground()
        self.drawWidgets()
        self.drawnFrame = True