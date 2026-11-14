# Import libraries
import pygame
from scripts.settings import *

# Set a class for the button object
class button:
    # Create a constructor to initialse the class and set class parameters
    def __init__(self, settings:dict,
                x=0,y=0,width=125,height=50,colours:tuple=((200,0,0),(250,0,0),(150,0,0),(50,50,50),(255,255,255)),
                label:str="button",labelShadow:bool=True,labelShadowOffset:tuple=(-3,3),labelFont=pygame.font.SysFont(None,32),
                labelPos:str="center",
                buttonShadow:bool=True,buttonShadowOffset:tuple=(-5,5),
                cursorRect:pygame.Rect=None,doController:bool=False,controller:pygame.joystick.Joystick=None,
                controllerControlls:dict={},
                command=None,commandParameters:list=None,sound=None,
                inactive:bool=False,
                buttonOffset=(0,0), labelOffset=(0,0),
                buttonCurve=0,
                buttonShadowAlpha=100,labelShadowAlpha=100,
                image=None):
        """
        x and y can be strings: x = "center", "left", "right"  y = "center", "top", "bottom".
        colours = ((idle colour), (hover colour), (press colour), (inactive colour), (label colour)).
        -- settings --
            - must include ["multX"] and ["multY"] as numbers since position and size values are scaled by this.
            - must include ["windowSize"] as a tuple of integers if x or y are strings!
        Sound - pass in the sound location and not the sound object!
        Image - must pass in an image object
        
        
        IF a command parameter is "label", the command parameter will be the buttons label and not the string "label"
        """
        # Initialise parameter variables
        self.settings = settings
        self.x, self.y, self.width, self.height = x, y, width, height
        self.colours = colours
        self.label, self.labelShadow, self.labelShadowOffset, self.labelFont = label, labelShadow, labelShadowOffset, labelFont
        self.labelPos = labelPos
        self.buttonShadow, self.buttonShadowOffset = buttonShadow, buttonShadowOffset
        self.cursorRect, self.doController, self.controller = cursorRect, doController, controller
        self.controllerControlls = controllerControlls
        self.command, self.commandParameters, self.sound = command, commandParameters, sound
        self.inactive = inactive
        self.buttonOffset, self.labelOffset = buttonOffset, labelOffset
        self.buttonCurve = buttonCurve
        self.buttonShadowAlpha, self.labelShadowAlpha = buttonShadowAlpha, labelShadowAlpha
        self.image = image
        # Save the values before rescaling
        self.originalPosition = (0, 0) # Got when calculating new position values
        self.originalSize = (self.width, self.height)
        self.originalShadowOffset = self.labelShadowOffset
        self.originalButtonShadowOffset = self.buttonShadowOffset
        self.originalButtonOffset = self.buttonOffset
        self.originalLabelOffset = self.labelOffset
        # Customise Variables
        self.width *= self.settings["multX"]
        self.height *= self.settings["multY"]
        self.labelShadowOffset = (self.labelShadowOffset[0]*self.settings["multX"],self.labelShadowOffset[1]*self.settings["multY"])
        self.buttonShadowOffset = (self.buttonShadowOffset[0]*self.settings["multX"],self.buttonShadowOffset[1]*self.settings["multY"])
        self.buttonOffset = (self.buttonOffset[0]*self.settings["multX"],self.buttonOffset[1]*self.settings["multY"])
        self.labelOffset = (self.labelOffset[0]*self.settings["multX"],self.labelOffset[1]*self.settings["multY"])
        # Initialise extra variables
        # Set varaibles to check whether a preset position has been passed in instead of a number value
        self.posXStr = ""
        self.posYStr = ""
        # Set a current colour variable for the button
        self.currentColour = self.colours[0]
        # -- Create the rect for the button --
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        # Check whether the position values are strings
        if type(self.x) == str:
            # Convert the x position using a subroutine to a number
            self.posXStr = self.x
            self.x = self.convertAxis(self.x, "x")
        else:
            self.originalPosition = (self.x, self.originalPosition[1])
            self.x *= self.settings["multX"]
        if type(self.y) == str:
            # Convert the y position using a subroutine to a number
            self.posYStr = self.y
            self.y = self.convertAxis(self.y, "y")
        else:
            self.originalPosition = (self.originalPosition[0], self.y)
            self.y *= self.settings["multY"]
        # Set the position of the rect
        self.rect.x = self.x + self.buttonOffset[0]
        self.rect.y = self.y + self.buttonOffset[1]
        # -- Create the shadow for the button from a subroutine --
        self.buttonShadowSurface = self.createButtonShadow()
        # -- Create a text surface --
        self.text = self.createText(255)
        # -- Create shadow for the text --
        self.textShadow = self.createText(self.labelShadowAlpha)
        # Calculate the position of the text -- center of the button
        self.textX, self.textY = self.getTextPos(self.labelPos)
        # Set variables to handle inputs with the mouse and the button
        self.canClick = False
        self.canPress = False
        # Set variable to keep the button colour as pressed
        self.keepPressColour = False
        self.didPress = False
        # Resize the image to the dimensions passed in
        if self.image:
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
            # Also create a copy of the image
            self.imageHover = self.createImageAlpha(0)
            self.buttonShadowSurface = self.createImageAlpha(self.buttonShadowAlpha)
        # Create the inactive darkener
        self.inactiveDarken = self.createButtonShadow(200, BLACK)

    # Subroutine to change the label of the button
    def changeLabel(self, lbl):
        self.label = lbl
        # -- Create a text surface --
        self.text = self.createText(255)
        # -- Create shadow for the text --
        self.textShadow = self.createText(self.labelShadowAlpha)
        # Calculate the position of the text -- center of the button
        self.textX, self.textY = self.getTextPos(self.labelPos)

    # Subroutine to change the button colour
    def changeColour(self, cols):
        self.colours = cols
        # Update the button shadow
        self.buttonShadowSurface = self.createButtonShadow()
        # Update the text
        # -- Create a text surface --
        self.text = self.createText(255)
        # -- Create shadow for the text --
        self.textShadow = self.createText(self.labelShadowAlpha)
            
    # Subroutine to change the current colour of the button
    def changeCurrentColour(self, cols, ind):
        self.currentColour = cols[ind]
            
    # Subroutine to set a new position
    def setPosition(self, x=None, y=None, resize=False, offset=None):
        if x != None:
            if type(x) == str:
                self.posXStr = x
                self.x = self.convertAxis(x, "x")
            else:
                self.originalPosition = (x, self.originalPosition[1])
                if resize:
                    self.x = x * self.settings["multX"]
                else:
                    self.x = x
        if y != None:
            if type(y) == str:
                self.posYStr = y
                self.y = self.convertAxis(y, "y")
            else:
                self.originalPosition = (self.originalPosition[0], y)
                if resize:
                    self.y = y * self.settings["multY"]
                else:
                    self.y = y
            
        if offset:
            self.originalButtonOffset = offset
            self.buttonOffset = (offset[0] * self.settings["multX"], offset[1] * self.settings["multY"])
            
        self.rect.x = self.x + self.buttonOffset[0]
        self.rect.y = self.y + self.buttonOffset[1]
        self.textX, self.textY = self.getTextPos(self.labelPos)

    # Subroutine to get the position of the text based on the given string position
    def getTextPos(self, pos):
        if pos.lower() in ["center", "centre"]:
            return ((self.rect.centerx - (self.text.get_width()/2)) + self.labelOffset[0], (self.rect.centery - (self.text.get_height()/2)) + self.labelOffset[1])
        elif pos.lower() == "left":
            return ((self.rect.left - self.text.get_width() + self.labelOffset[0]), (self.rect.centery - (self.text.get_height()/2)) + self.labelOffset[1])
        elif pos.lower() == "right":
            return ((self.rect.right + self.labelOffset[0]), (self.rect.centery - (self.text.get_height()/2)) + self.labelOffset[1])
        elif pos.lower() == "bottom":
            return ((self.rect.centerx - (self.text.get_width()/2)) + self.labelOffset[0], (self.rect.bottom + self.labelOffset[1]))
        elif pos.lower() == "top":
            return ((self.rect.centerx - (self.text.get_width()/2)) + self.labelOffset[0], (self.rect.top - self.text.get_height() + self.labelOffset[1]))

    # Subroutine to create a shadow for the button for images
    def createImageAlpha(self, alpha):
        # Create a mask for the image, turns the image black and white (white is the object)
        shadow = pygame.mask.from_surface(self.image)
        # Make the object in the mask black and the bg white
        shadow.invert()
        # Make the mask a surface so it can be minipulated
        shadow = shadow.to_surface()
        # Set the colourkey of the surface to white so no white colour is shown
        shadow.set_colorkey((255,255,255))
        # Set the alpha value of the surface to the given alpha value
        shadow.set_alpha(alpha)
        # Return the made shadow
        return shadow
            
    # Subroutine to create a shadow for the button
    def createButtonShadow(self, shadowAlpha=None, shadowColour=None):
        # Set the alpha value to the given alpha value
        if shadowAlpha != None:
            alpha = shadowAlpha
        else:
            alpha = self.buttonShadowAlpha
        # Set the colour value to the given colour value
        if shadowColour != None:
            colour = shadowColour
        else:
            colour = self.currentColour
        # Create a surface for the shadow and make it the same size as the button
        surf = pygame.Surface((self.rect.width, self.rect.height))
        # Fill the surface to a colour
        surf.fill((1,1,4))
        # Set a colourkey for the surface the same colour as filled to make it transparrent
        surf.set_colorkey((1,1,4))
        # Draw the button rect copy on the surface
        pygame.draw.rect(surf, colour, (0,0,self.rect.width,self.rect.height), 0, self.buttonCurve)
        # Set the transparrency value of the surface to make it darker -- simulates shadow effect
        surf.set_alpha(alpha)
        # Return the surface
        return surf.convert_alpha()

    # Subroutine to create a shadow for the text
    def createText(self, alphaValue):
        # Create a surface for the text
        if "\\n" in self.label:
            self.label = self.label.replace("\\n", "\n")
        surf = self.labelFont.render(self.label, True, self.colours[-1])
        # Resize the surface
        surf = pygame.transform.scale(surf, (surf.get_width()*self.settings["multX"],surf.get_height()*self.settings["multY"]))
        # Set the alpha value of the surface
        surf.set_alpha(alphaValue)
        # Return the text surface
        return surf.convert_alpha()

    # Subroutine to convert string positions into numbers
    def convertAxis(self, position, axisType):
        # Check whether the x-axis is being affected
        if axisType.lower() == "x":
            # Check if the position entered is "left"
            if position.lower() == "left": return 0
            # Check if the position entered is "right"
            elif position.lower() == "right": return self.settings["windowSize"][0] - self.rect.width
            # Check if the position entered is "center"
            elif position.lower() in ["center", "centre"]: return (self.settings["windowSize"][0]/2) - (self.rect.width/2)
            # If the position entered is wrong, return 0
            return 0
        # Check whether the y-axis is being affected
        elif axisType.lower() == "y":
            # Check if the position entered is "up"
            if position.lower() == "up": return 0
            # Check if the position entered is "down"
            elif position.lower() == "bottom": return self.settings["windowSize"][1] - self.rect.height
            # Check if the position entered is "center"
            elif position.lower() in ["center", "centre"]: return (self.settings["windowSize"][1]/2) - (self.rect.height/2)
            # If the position entered is wrong, return 0
            return 0
        # If the axis entered is wrong, return 0
        return 0
    
    # Subroutine to resize the button
    def updateSize(self, settings, image=None):
        self.settings = settings
        # Get the new text surface
        self.text = self.createText(255)
        # Get the new text shadow surface
        self.textShadow = self.createText(self.labelShadowAlpha)
        # Calculate the new button size
        self.rect.width = self.originalSize[0] * self.settings["multX"]
        self.rect.height = self.originalSize[1] * self.settings["multY"]
        # Get the new rect shadow surface
        self.buttonShadowSurface = self.createButtonShadow()
        # Get the new inactive darkener
        self.inactiveDarken = self.createButtonShadow(200, BLACK)
        # Calculate the new values
        # X and Y
        if self.posXStr == "": self.x = self.originalPosition[0] * self.settings["multX"]
        else: self.x = self.convertAxis(self.posXStr, "x")
        if self.posYStr == "": self.y = self.originalPosition[1] * self.settings["multY"]
        else: self.y = self.convertAxis(self.posYStr, "y")
        # Offsets
        self.labelOffset = (self.originalLabelOffset[0]*self.settings["multX"], self.originalLabelOffset[1]*self.settings["multY"])
        self.buttonOffset = (self.originalButtonOffset[0]*self.settings["multX"], self.originalButtonOffset[1]*self.settings["multY"])
        self.shadowOffset = (self.originalShadowOffset[0]*self.settings["multX"], self.originalShadowOffset[1]*self.settings["multY"])
        self.buttonShadowOffset = (self.originalButtonShadowOffset[0]*self.settings["multX"], self.originalButtonShadowOffset[1]*self.settings["multY"])
        # Update rect x and y values
        self.rect.x = self.x + self.buttonOffset[0]
        self.rect.y = self.y + self.buttonOffset[1]
        # text X and Y
        self.textX, self.textY = self.getTextPos(self.labelPos)
        # Image size if there are any images
        if self.image:
            # Resize the image
            self.image = pygame.transform.scale(image, (self.rect.width, self.rect.height))
            # Also resize the image darkener for interation
            self.imageHover = self.createImageAlpha(0)
            # Also resize the image shadow
            self.buttonShadowSurface = self.createImageAlpha(self.buttonShadowAlpha)
            
    # Subroutine to handle command calling and sound playing
    def handlePress(self):
        # Change the opacity of the text surfaces
        self.text.set_alpha(int(self.text.get_alpha()/1.5))
        self.textShadow.set_alpha(int(self.textShadow.get_alpha()/1.5))

        # Check if there is a command present
        if self.command != None:
            # Check if there are any parameters
            if self.commandParameters != None:
                # Call the command with the parameters
                parameters = self.commandParameters
                # Check if the parameters are a list
                if type(parameters) == list:
                    # Check if the string label is in the parameters
                    if "label" in parameters:
                        # Get the index of the item
                        idx = parameters.index("label")
                        # Change that value to the actual label
                        parameters[idx] = self.label
                    # Call the function with the unpacked parameters
                    self.command(*parameters)
                else:
                    if parameters == "label": parameters = self.label
                    self.command(parameters)
            # If there aren't any parameters, call the function normally
            else:
                self.command()
        # Check if there is a sound passed in
        if self.sound != None:
            # Create a sound object
            sound = pygame.mixer.Sound(self.sound)
            sound.play()

    # Subroutine to handle hand input
    def handInput(self, handPinch):
        # Check if the mouse has interacted with the button
        for pinch in handPinch:
            if pinch:
                # Change the colour of the button to "pressed"
                self.currentColour = self.colours[2]
                self.keepPressColour = True
                if self.image:
                    self.imageHover.set_alpha(50)
                self.didPress = True

    # Subroutine to handle controller input
    def controllerInput(self, controllerButton):
        # Check if the controller has interacted with the button
        if controllerButton and self.canPress:
            # Change the colour of the button to "pressed"
            self.currentColour = self.colours[2]
            self.keepPressColour = True
            if self.image:
                self.imageHover.set_alpha(50)
            self.canPress = False
            self.didPress = True

    # Subroutine to handle mouse input
    def mouseInput(self, mouseButton):
        # Check if the mouse has interacted with the button
        if mouseButton == (1, 0, 0) and self.canClick:
            # Change the colour of the button to "pressed"
            self.currentColour = self.colours[2]
            self.keepPressColour = True
            if self.image:
                self.imageHover.set_alpha(50)
            self.canClick = False
            self.didPress = True

    # Subroutine to draw the button onto the given surface
    def draw(self, screen):
        # Check if the shadow for the button is enabled
        if self.buttonShadow:
            # Calculate the x position of the surface
            shadowX = self.rect.x + self.buttonShadowOffset[0]
            # Calculate the y position of the surface
            shadowY = self.rect.y + self.buttonShadowOffset[1]
            # Draw the shadow onto the surface
            screen.blit(self.buttonShadowSurface, (shadowX, shadowY))
        # Check if there is an image present
        if self.image:
            # Draw the image
            screen.blit(self.image, (self.rect.x, self.rect.y))
            screen.blit(self.imageHover, (self.rect.x, self.rect.y))
        else:
            # Draw the button rect onto the surface
            pygame.draw.rect(screen, self.currentColour, self.rect, 0, self.buttonCurve)

        # Check if the shadow for the text is enabled
        if self.labelShadow:
            # Calculate the x position for the surface
            shadowX = self.textX + self.labelShadowOffset[0]
            # Calculate the y position for the surface
            shadowY = self.textY + self.labelShadowOffset[1]
            # Draw the shadow onto the surface
            screen.blit(self.textShadow, (shadowX, shadowY))
        # Draw the text surface onto the screen
        screen.blit(self.text, (self.textX, self.textY))
        
        # Check if the button is inactive
        if self.inactive:
            # Draw a shadow over the button to show that its inactive
            screen.blit(self.inactiveDarken, (self.rect.x, self.rect.y))

    # Subroutine to update the button
    def update(self, settings, cursorRects, controller=None, allowController=None, controllerName=None, handPinch=None):
        # Update the settings dict
        self.settings = settings
        # Update the mouse rect
        self.cursorRects = cursorRects
        # Get the attributes for the mouse
        mouseButton = pygame.mouse.get_pressed()
        # Check if a controller exists
        if controller and allowController:
            self.doController = True
            self.controller = controller
            controllerButton = self.controller.get_button(self.controllerControlls[controllerName]["click"])
        else:
            self.doController = False
            self.controller = None
            controllerButton = None

        # Check if the button is being pressed -- used so clicks can only happen 1 at a time
        if mouseButton != (1, 0, 0):
            # Set the click to true
            self.canClick = True
            # Set the keep press colour variable to false as the LMB is not being pressed
            self.keepPressColour = False
        # Check if the controller button is being pressed
        if controllerButton == False:
            # Set the press to True
            self.canPress = True
            # Set the keep press colour variable to false as the LMB is not being pressed
            self.keepPressColour = False

        # Check if the button is active
        colliding =  False
        if not self.inactive:
            # Check if the button intersects with the middle of the cursor rect
            for rect in self.cursorRects:
                if self.rect.collidepoint(rect.center):
                    colliding = True
            if colliding:
                # Change the colour of the button to "hover"
                self.currentColour = self.colours[1]
                # Check if an image is present
                if self.image:
                    # Change the opacity of the black surface
                    self.imageHover.set_alpha(100)
                # Check if the controller is being used as main input
                if allowController and controller:
                    self.controllerInput(controllerButton)
                # Else call subroutine to handle mouse input
                self.mouseInput(mouseButton)
                if handPinch != None:
                    self.handInput(handPinch)
            else:
                # If not colliding, set the colour of the button to "idle"
                self.currentColour = self.colours[0]
                # Set the keep press colour variable to false as the cursor if not colliding anymore
                self.keepPressColour = False
                # Change the opacity of the image copy to clear
                if self.image:
                    self.imageHover.set_alpha(0)    
        
        # Check if the colour of the button should be "press"
        if self.keepPressColour:
            self.currentColour = self.colours[2]
            if self.image:
                self.imageHover.set_alpha(50)
        else:
            self.text.set_alpha(255)
            self.textShadow.set_alpha(self.labelShadowAlpha)
            if self.didPress and colliding:
                self.handlePress()
                self.didPress = False
            else:
                self.didPress = False

        # Update the shadow -- to match colours
        self.buttonShadowSurface = self.createButtonShadow()

        # Check if the button is being pressed -- used so clicks can only happen 1 at a time
        if mouseButton == (1, 0, 0):
            # Set the click to false
            self.canClick = False
        # Check if the controller button is being pressed
        if controllerButton:
            # Set the press to False
            self.canPress = False
