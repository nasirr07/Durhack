# Import libraries to be used
import pygame, math

# Create a class for the text object
class text():
    # Initialise the class with a constructor
    def __init__(self, settings, x=0, y=0, colour=(255,255,255), label="TEXT",
                shadow=True, shadowOffset=(-3,3), shadowDarkness=100, font=pygame.font.SysFont(None, 32),
                positionOffset=(0,0), showText=True,
                ySpeed=150,yAmplitude=15,doSineY=False):
        # Initialise the parameter variables
        self.settings = settings
        self.x, self.y = x, y
        self.colour, self.label = colour, label
        self.shadow, self.shadowOffset, self.shadowDarkness = shadow, shadowOffset, shadowDarkness
        self.font = font
        self.positionOffset = positionOffset
        self.showText = showText
        self.doSineY = doSineY
        # Set variables to store original values to compensate for resizing
        self.originalPosition = (x, y)
        self.originalShadowOffset = shadowOffset
        self.originalPositionOffset = positionOffset
        # Initialise extra variables
        self.mutliplier = 1
        # Set extra variables
        self.positionStrX = ""
        self.positionStrY = ""
        # Create the text
        self.text = self.createText(255)
        self.textShadow = self.createText(self.shadowDarkness)
        # Change the variables so they fit the resized screen (if even resized)
        # Check if the x and y values are strings -- positioned in specified places on the screen
        if type(self.x) == str:
            self.positionStrX = self.x
            self.x = self.convertStringPosition(self.x, "x")
        else: self.x *= settings["multX"]
        if type(self.y) == str:
            self.positionStrY = self.y
            self.y = self.convertStringPosition(self.y, "y")
        else: self.y *= settings["multY"]
        # Multiply variables to account for screen resizing
        self.shadowOffset = (self.shadowOffset[0]*settings["multX"], self.shadowOffset[1]*settings["multY"])
        self.positionOffset = (self.positionOffset[0]*settings["multX"], self.positionOffset[1]*settings["multY"])
        # Create variables to make the text move in a sine wave
        self.sineOffsetY = 0
        self.yAngle = 0
        self.ySpeed = ySpeed
        self.yAmplitude = yAmplitude
        
    # Subroutine to change the size of the text
    def changeSize(self, multiplier=1):
        self.mutliplier = multiplier
        #width = self.text.get_width()
        #height = self.text.get_height()
        self.text = self.createText(255)#pygame.transform.scale(self.text, (width*multiplier, height*multiplier))
        self.textShadow = self.createText(self.shadowDarkness)

    # Subroutine to update the sizes and positions of the text -- for screen resizing
    def updateSize(self, settings):
        self.settings = settings
        # Create the new text
        self.text = self.createText(255)
        self.textShadow = self.createText(self.shadowDarkness)
        # Calculate the new text positions
        if self.positionStrX == "": self.x = self.originalPosition[0] * self.settings["multX"]
        else: self.x = self.convertStringPosition(self.positionStrX, "x")
        if self.positionStrY == "": self.y = self.originalPosition[1] * self.settings["multY"]
        else: self.y = self.convertStringPosition(self.positionStrY, "y")
        self.shadowOffset = (self.originalShadowOffset[0]*self.settings["multX"], self.originalShadowOffset[1]*self.settings["multY"])
        self.positionOffset = (self.originalPositionOffset[0]*self.settings["multX"], self.originalPositionOffset[1]*self.settings["multY"])
    
    # Subroutine to change the label of the text
    def changeLabel(self, label):
        # Change the value of the label variable
        self.label = label
        # Create the text with the new label
        self.text = self.createText(255)
        self.textShadow = self.createText(self.shadowDarkness)
        
    # Subroutine to change the colour of the text
    def changeColour(self, colour):
        # Change the value of the colour variable
        self.colour = colour
        # Create the text with the new colour
        self.text = self.createText(255)
        self.textShadow = self.createText(self.shadowDarkness)
    
    # Subroutine to change the position of the text
    def changePosition(self, x=0, y=0, resize=True):
        if type(x) == str:
            self.positionStrX = x
            self.x = self.convertStringPosition(x, "x")
        else:
            self.originalPosition = (x, self.originalPosition[1])
            if resize:
                self.x = x * self.settings["multX"]
            else:
                self.x = x
        if type(y) == str:
            self.positionStrY = y
            self.y = self.convertStringPosition(y, "y")
        else:
            self.originalPosition = (self.originalPosition[0], y)
            if resize:
                self.y = y * self.settings["multY"]
            else:
                self.y = y
        
    # Subroutine to create and return texts
    def createText(self, alpha):
        # Create the original text object
        text = self.font.render(self.label, True, self.colour)
        # Change the alpha value of the text
        text.set_alpha(alpha)
        # Change the size of the text
        text = pygame.transform.scale(text, (text.get_width()*self.settings["multX"]*self.mutliplier,
                                            text.get_height()*self.settings["multY"]*self.mutliplier))
        # Return the text
        return text.convert_alpha()
        
    # Subroutine to convert a string position into a numerical value
    def convertStringPosition(self, position, axis):
        # Check which axis is being changed
        if axis.lower() == "x":
            # Check which position is to be calculated
            # And return the calculated position
            if position.lower() in ["center", "centre"]:
                return (self.settings["windowSize"][0] / 2) - (self.text.get_width() / 2)
            elif position.lower() == "left":
                return 0
            elif position.lower() == "right":
                return self.settings["windowSize"][0] - self.text.get_width()
            return 0
        elif axis.lower() == "y":
            if position.lower() in ["center", "centre"]:
                return (self.settings["windowSize"][1] / 2) - (self.text.get_height() / 2)
            elif position.lower() == "top":
                return 0
            elif position.lower() == "bottom":
                return self.settings["windowSize"][1] - self.text.get_height()
            return 0
    
    # Subroutine to keep the objects updated
    def update(self, settings, dt=0):
        # Keep the settings up do date
        self.settings = settings
        
        # Check if the text should be moving in a sine wave
        if self.doSineY:
            # Update the angle
            self.yAngle += self.ySpeed * dt
            # Bound the angle between 0 and 360 so the angle doesnt get too big
            if self.yAngle >= 360:
                self.yAngle = 0
            self.sineOffsetY = self.yAmplitude * math.sin(math.radians(self.yAngle))
        else:
            self.sineOffsetY = 0
            
    
    # Subroutine to draw the text to the given surface
    def draw(self, screen):
        # Calculate the x and y positions for the text
        x = self.x + self.positionOffset[0]
        y = self.y + self.positionOffset[1] + self.sineOffsetY
        # Check if the text should even be drawn
        if self.showText:
            # Check if the shadow for the text should be drawn
            if self.shadow:
                # Draw the text shadow surface
                screen.blit(self.textShadow, (x+self.shadowOffset[0], y+self.shadowOffset[1]))
            # Draw the text surface
            screen.blit(self.text, (x, y))