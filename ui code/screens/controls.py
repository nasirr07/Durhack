# Import modules
from scripts.screens.screenTemplate import *

# Use a class to create the screen
class controlsScreen(screenTemplate):
    # Initialise the class with a constructor
    def __init__(self, game, screen, settings, controls):
        # Initialise the parent class
        super().__init__(game, screen, settings, controls)
        
        # Initialise parameter variables
        self.controls = controls
        # Initialise extra variables
        self.settingButton = False
        self.setControl = None

        # Add to the buttons dictionary
        self.buttons["apply"] = self.createButton(
            "center", "bottom", self.changeControls, None, (0, -100), text="APPLY"
        )

        startX = 100
        startY = 250
        seperationY = 125
        seperationX = 275
        textYOffset = -40

        # Add to the button dictionary
        self.buttons["up"] = \
        self.createButton(startX, startY, self.setButton, "up", (0, 0), 200, 50, self.buttonAttrs["font"],
                          self.buttonAttrs["colours"], self.controls["up"])
        self.buttons["down"] = \
        self.createButton(startX, startY+seperationY*1, self.setButton, "down", (0, 0), 200, 50, self.buttonAttrs["font"],
                          self.buttonAttrs["colours"], self.controls["down"])
        self.buttons["left"] = \
        self.createButton(startX, startY+seperationY*2, self.setButton, "left", (0, 0), 200, 50, self.buttonAttrs["font"],
                          self.buttonAttrs["colours"], self.controls["left"])
        self.buttons["right"] = \
        self.createButton(startX, startY+seperationY*3, self.setButton, "right", (0, 0), 200, 50, self.buttonAttrs["font"],
                          self.buttonAttrs["colours"], self.controls["right"])
        self.buttons["pause"] = \
        self.createButton(startX+seperationX*1, startY, self.setButton, "pause", (0, 0), 200, 50, self.buttonAttrs["font"],
                          self.buttonAttrs["colours"], self.controls["pause"])

        # Add to the text dictionary
        self.texts["title"] = \
            text(self.settings, "center", 50, WHITE, "CONTROLS", font=self.settings["largeFont"],
                doSineY=True, shadowOffset=(-7, 7))
        self.texts["up"] = \
            text(self.settings, startX, startY+textYOffset, WHITE, "Move Up", font=self.settings["mediumFont"],
                shadowOffset=(-5, 5))
        self.texts["down"] = \
            text(self.settings, startX, startY+textYOffset+seperationY*1, WHITE, "Move Down", font=self.settings["mediumFont"],
                shadowOffset=(-5, 5))
        self.texts["left"] = \
            text(self.settings, startX, startY+textYOffset+seperationY*2, WHITE, "Move Left", font=self.settings["mediumFont"],
                shadowOffset=(-5, 5))
        self.texts["right"] = \
            text(self.settings, startX, startY+textYOffset+seperationY*3, WHITE, "Move Right", font=self.settings["mediumFont"],
                shadowOffset=(-5, 5))
        self.texts["pause"] = \
            text(self.settings, startX+seperationX*1, startY+textYOffset, WHITE, "Pause", font=self.settings["mediumFont"],
                shadowOffset=(-5, 5))

        # Create text to display when setting a button
        self.setButtonTxt = text(self.settings, "center", "center", WHITE, "PRESS ANY KEY",
                                 font=self.settings["largeFont"], doSineY=True, shadowOffset=(-7, 7))
        
        # Create a copy of the controls to not directly alter the games controls without applying
        self.controlsCopy = self.controls.copy()

    # Overwrite this subroutine to add the set button text
    def extraUpdateSize(self):
        self.setButtonTxt.updateSize(self.settings)

    # Overwrite this subroutine to add the set button text
    def extraSetShadows(self, boolVal):
        self.setButtonTxt.shadow = boolVal

    # Create a subroutine to convert a string to a symbol
    def convertStringToSymbol(self, value):
        v = value.lower()
        if v == "exclamation": return "!"
        elif v == "at": return "@"
        elif v == "hashtag": return "#"
        elif v == "dollar": return "$",
        elif v == "percent": return "%"
        elif v == "caret": return "^"
        elif v == "and": return "&"
        elif v == "asterisk": return "*"
        elif v == "leftparenthesis": return "("
        elif v == "rightparenthesis": return ")"
        elif v == "minus": return "-"
        elif v == "underscore": return "_"
        elif v == "equals": return "="
        elif v == "plus": return "+"
        elif v == "leftbracket": return "["
        elif v == "rightbracket": return "]"
        elif v == "leftcurlybracket": return "{"
        elif v == "rightcurlybracket": return "}"
        elif v == "backslash": return "\\"
        elif v == "bar": return "|"
        elif v == "comma": return ","
        elif v == "leftarrow": return "<"
        elif v == "rightarrow": return ">"
        elif v == "period": return "."
        elif v == "slash": return "/"
        elif v == "questionmark": return "?"
        elif v == "colon": return ":"
        elif v == "semicolon": return ";"
        elif v == "doublequotationmarks": return '"'
        elif v == "singlequotationmarks": return "'"
        return value

    # Create a subroutine to begin changing the controls
    def setButton(self, control):
        self.setControl = control
        self.settingButton = True

    # Create a subroutine to change the control -- called in main events subroutine
    def setButtonValue(self, value):
        # Set the new value to the controls
        self.controlsCopy[self.setControl] = value
        # Convert the value to a symbol for the label
        symbol = self.convertStringToSymbol(value)
        # Set the button label to the new control
        self.buttons[self.setControl].changeLabel(symbol)
        # Set the set control value to none
        self.setControl = None
        # Set the setting button flag to false
        self.settingButton = False

    # Create a subroutine to sync the new controls with the games main controls
    def changeControls(self):
        self.game.setNewControls(self.controlsCopy)

    # Create a subroutine to change the labels of the buttons to show the original controls when opening the screen
    def setOriginalControls(self):
        # Set the original controls
        self.buttons["up"].changeLabel(self.controls["up"])
        self.buttons["down"].changeLabel(self.controls["down"])
        self.buttons["left"].changeLabel(self.controls["left"])
        self.buttons["right"].changeLabel(self.controls["right"])
        self.buttons["pause"].changeLabel(self.controls["pause"])

    # Create a subroutine to update the screen
    def update(self, deltaTime):
        # Check if a button is not being set
        if not self.settingButton:
            self.updateWidgets()
        else:
            # Update the set button text
            self.setButtonTxt.update(self.settings, deltaTime)
        
    # Create a subroutine to draw the screen
    def draw(self):
        self.drawBackground()
        self.drawWidgets()
        self.drawnFrame = True
        # Check if a button is being set
        if self.settingButton:
            # Draw the dark surface
            self.drawDarkSurf()
            # Draw the set button text
            self.setButtonTxt.draw(self.screen)