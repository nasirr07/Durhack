# Import modules
from scripts.settings import *
from scripts.screens.screenTemplate import *

# Use a class to create the screen
class selectSave(screenTemplate):
    # Initialise the class with a constructor
    def __init__(self, game, screen, settings, controls):
        # Initialise the parent class
        super().__init__(game, screen, settings, controls)
        
        # Add to the text dictionary
        self.texts["title"] = \
            text(self.settings, "center", 50, WHITE, "SELECT SAVE", font=self.settings["largeFont"],
                doSineY=True, shadowOffset=(-7, 7))

        # Add buttons to the dictionary
        self.buttons["newSave"] = self.createButton(
            "center", "center", self.game.data.makeNewSave, width=200, height=100, font=self.buttonAttrs["font"],
            colours= self.buttonAttrs["colours"], text="NEW SAVE"
        )
        self.buttons["deleteSave"] = self.createButton(
            "center", "bottom", self.deleteSave, width=200, height=100, font=self.buttonAttrs["font"],
            colours= self.buttonAttrs["colours"], text="DELETE", offset=(200, -50)
        )
        self.buttons["loadSave"] = self.createButton(
            "center", "bottom", self.loadSave, width=200, height=100, font=self.buttonAttrs["font"],
            colours= self.buttonAttrs["colours"], text="LOAD", offset=(-200, -50)
        )

        # Create a list to store the save buttons
        self.saveButtons = []
        # Create a variable to keep track of which save is selected
        self.currentSave = None
        # Create a varaible to keep track of which save is which button
        self.currentSaveButtonIndex = -1

        # Create variables to position the save buttons
        self.buttonPositions = [-200 - 200*2, -100-200, 0, 100+200, 200+200*2, 200+200*10]

        # Create the buttons to select the save
        self.createSaveButtons()

    # Create a subroutine to load a save
    def loadSave(self):
        # Check if a save has been selected
        if self.currentSave != None and self.currentSaveButtonIndex != -1:
            # Load the save
            self.game.loadSave(self.currentSave)
            # Uncheck the current save
            self.currentSave = None
            self.currentSaveButtonIndex = -1

    # Create a subroutine to delete a save
    def deleteSave(self):
        # Check if a save has been selected
        if self.currentSave != None and self.currentSaveButtonIndex != -1:
            # Remove the save file
            # Check if the file exists first
            if os.path.exists(f"data\\saves\\{self.currentSave}"):
                # Remove the file
                os.remove(f"data\\saves\\{self.currentSave}")
                # Delete the button
                self.saveButtons.pop(self.currentSaveButtonIndex)
                # Reset the save variables
                self.currentSave = None
                self.currentSaveButtonIndex = -1
                self.createSaveButtons()

    # Create a subroutine to select a save
    def selectSave(self, currentSave, btnIndex):
        # Set the current save to the selected save
        self.currentSave = currentSave
        # Set the current save index to the index
        self.currentSaveButtonIndex = btnIndex

    # Create a subroutine to create a save button
    def createSaveButton(self,  file):
        # Get the index
        index = len(self.saveButtons)
        # Get the name
        name = file.replace(".txt", "")
        # Create the button
        self.saveButtons.append(self.createButton(
            "center", "center", self.selectSave, [file, index], (self.buttonPositions[index], 0), 200, 100,
            self.buttonAttrs["font"], self.buttonAttrs["colours"], name 
        ))

    # Create a subroutine to create the save buttons
    def createSaveButtons(self):
        # Clear the save buttons list
        self.saveButtons = []
        # Check if the directory exists
        if not os.path.exists("data\\saves"):
            # Create the directory
            os.makedirs("data\\saves")

        # Loop though the saves directory
        for _, _, files in os.walk("data\\saves"):
            # Make and index variable to keep track of the index
            index = 0
            # Loop through each file
            for file in files:
                # Get the name of the file
                name = file.replace(".txt", "")
                # Create the button
                self.saveButtons.append(self.createButton(
                    "center", "center", self.selectSave, [file, index], (self.buttonPositions[index], 0), 200, 100,
                    self.buttonAttrs["font"], self.buttonAttrs["colours"], name 
                ))
                # Increment the index
                index += 1
        
    # Change the update size subroutine to change the size of the save buttons
    def extraSetShadows(self, boolVal):
        # Loop through the buttons list
        for button in self.saveButtons:
            # Set the shadow to the value
            button.labelShadow = boolVal
            # Set the shadow to the value
            button.buttonShadow = boolVal

    # Change the update size subroutine to change the size of the save buttons
    def extraUpdateSize(self):
        # Loop through the buttons list
        for button in self.saveButtons:
            # Update button
            button.updateSize(self.settings)

    # Create a subroutine to update the screen
    def update(self, deltaTime):
        self.updateWidgets()
        # Change the position of the new save button
        self.buttons["newSave"].setPosition(offset=(self.buttonPositions[self.game.data.getNumSaves()], 0))
        # Update the save buttons
        # Loop through the buttons
        for idx, button in enumerate(self.saveButtons):
            # Update the button
            button.update(self.settings, [self.game.mouseRect])
            # Change the colour of the button based on if it is the current save button
            # Check if the loops index is the current save index
            if idx == self.currentSaveButtonIndex:
                # Change the colour of the button to green
                button.changeColour((GREEN200, GREEN255, GREEN150, WHITE))
            else:
                # Change the colour of the button to original
                button.changeColour(self.buttonAttrs["colours"])

    # Create a subroutine to draw the screen
    def draw(self):
        self.drawBackground()
        self.drawWidgets()
        # Loop through the buttons
        for button in self.saveButtons:
            # Draw the button
            button.draw(self.screen)
        self.drawnFrame = True