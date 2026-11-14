# Import libraries
from scripts.settings import *
from scripts.widgets.text import *
from scripts.widgets.button import *
from scripts.widgets.checkbox import *
from scripts.widgets.dropList import *

class screenTemplate():
    def __init__(self, game, screen, settings, controls):
        # Initialise parameter variables
        self.game = game
        self.screen = screen
        self.settings = settings.copy()
        self.controls = controls.copy()
    
        # Initialise extra variables
        self.lastScreen = "start"
        self.drawnFrame = False
        # -- buttons --
        self.buttonAttrs = {
            "startX": 50,
            "startY": 50,
            "spacingY": 50,
            "spacingX": 50,
            "curve": 20,
            "width": 225,
            "height": 75,
            "colours": (RED150, RED255, RED100, WHITE),#(GRAY100, GRAY150, GRAY50, WHITE),
            "font": self.settings["mediumFont"],
        }
        # Object Dictionaries
        self.texts = {}
        self.checkboxes = {}
        self.droplists = {}
        self.buttons = {
            "return": button(self.settings,width=self.buttonAttrs["width"]/0.9,height=self.buttonAttrs["height"]/1.2,
                        labelFont=self.settings["mediumFont"],colours=self.buttonAttrs["colours"],
                        command=self.returnLastScreen,label="RETURN", buttonCurve=self.buttonAttrs["curve"],
                        x="right",y="top", buttonOffset=(-15, 15))
            }
        # Surfaces
        self.backgroundColour = GRAY25
        # Create a surface to darken the background so the buttons are more visible
        self.darkSurf = pygame.Surface((self.settings["windowSize"][0], self.settings["windowSize"][1]))
        self.darkSurf.fill(BLACK)
        self.darkSurf.set_alpha(200)
        self.darkSurf.convert_alpha()
        
    # Subroutine to create the buttons
    def createButton(self, x=0, y=0, command=None, commandParameters=None, offset=(0, 0),
                    width=None, height=None, font=None, colours=None, text="button"):
        if width == None: width = self.buttonAttrs["width"]
        if height == None: height = self.buttonAttrs["height"]
        if font == None: font = self.buttonAttrs["font"]
        if colours == None: colours = self.buttonAttrs["colours"]
        
        return button(self.settings, x=x, y=y, width=width, height=height, colours=colours,
                    labelFont=font, label=text, buttonOffset=offset, command=command,
                    commandParameters=commandParameters, buttonCurve=self.buttonAttrs["curve"])
        
    # Subroutine to allow for classes to add their own extra update dicts methods
    def extraUpdateDicts(self, settings, controls):
        pass

    # Subroutine to update the data dictionaries
    def updateDicts(self, settings, controls):
        # Update the settings dictionary
        self.settings = settings.copy()
        # Update the controls dictionary
        self.controls = controls.copy()
        # Update extra dicts
        self.extraUpdateDicts(settings, controls)

    # Subroutine to go to back to the previous screen
    def returnLastScreen(self):
        self.game.toBeCurrentScreen = self.lastScreen
        self.drawnFrame = False
        self.game.startedTransition = True

    # Subroutine to allow for classes to add their own extra update size methods
    def extraUpdateSize(self):
        pass

    # Subroutine to update the sizes of the screens
    def updateSizes(self):
        # Loop through the texts dictionary
        for name, text in self.texts.items():
            # Update the size using its function
            text.updateSize(self.settings)

        # Loop through the buttons dictionary
        for name, button in self.buttons.items():
            # Update the size using its function
            button.updateSize(self.settings)

        # Loop through the checkbox dictionary
        for name, box in self.checkboxes.items():
            # Update the size using its function
            box.updateSize(self.settings)

        # Loop through the droplist dictionary
        for name, dlist in self.droplists.items():
            # Update the size using its function
            dlist.updateSize(self.settings)

        # Call the extra update size
        self.extraUpdateSize()

    # Subroutine to update the background
    def updateBackground(self):
        # Update the brightness for the settings screen
        self.darkSurf = pygame.transform.scale(self.darkSurf, (self.settings["windowSize"][0], self.settings["windowSize"][1]))

    # Subroutine to allow for classes to add their own set shadows methods
    def extraSetShadows(self, boolVal):
        pass

    # Subroutine to set all of the shadows to one value
    def setShadows(self, boolVal):
        # Loop through the texts dictionary
        for name, text in self.texts.items():
            # Set the shadow to the value
            text.shadow = boolVal

        # Loop through the buttons dictionary
        for name, button in self.buttons.items():
            # Set the shadow to the value
            button.labelShadow = boolVal
            # Set the shadow to the value
            button.buttonShadow = boolVal

        # Loop through the checkbox dictionary
        for name, box in self.checkboxes.items():
            # Set the shadow to the value
            box.labelShadow = boolVal
            # Set the shadow to the value
            box.boxShadow = boolVal

        # Loop through the droplist dictionary
        for name, dlist in self.droplists.items():
            # Set the shadow to the value
            dlist.labelShadow = boolVal
            # Set the shadow to the value
            dlist.textShadow = boolVal
            # Set the shadow to the value
            dlist.listShadow = boolVal
        
        # Call the extra set shadows
        self.extraSetShadows(boolVal)

    # Subroutine to update all widgets
    def updateWidgets(self):
        # Loop through the buttons dictionary
        for name, button in self.buttons.items():
            # Update button
            button.update(self.settings, [self.game.mouseRect])
        
        # Loop through the texts dictionary
        for name, text in self.texts.items():
            # Update text
            text.update(self.settings, self.game.deltaTime)

        # Loop through the checkbox dictionary
        for name, box in self.checkboxes.items():
            # Update checkbox
            box.update(self.settings, self.game.mouseRect)
        
        # Loop through the droplist dictionary
        for name, dlist in self.droplists.items():
            # Update droplist
            dlist.update(self.game.mouseRect)

    # Subroutine to draw all widgets
    def drawWidgets(self):
        # Loop through the buttons dictionary
        for name, button in self.buttons.items():
            # Draw the button
            button.draw(self.screen)
        
        # Loop through the texts dictionary
        for name, text in self.texts.items():
            # Draw the text
            text.draw(self.screen)
        
        # Loop through the checkbox dictionary
        for name, box in self.checkboxes.items():
            # Draw the checkbox
            box.draw(self.screen)

        # Loop through the droplist dictionary
        for name, dlist in self.droplists.items():
            # Update the size using its function
            dlist.draw(self.screen)
            
    # Subroutine to draw the background
    def drawBackground(self):
        # Fill the screen with a solid colour
        self.screen.fill(GRAY25)
            
    # Subroutine to draw the dark surface
    def drawDarkSurf(self):
        self.screen.blit(self.darkSurf, (0, 0))