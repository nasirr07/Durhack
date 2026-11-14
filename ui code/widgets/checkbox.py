import pygame
from scripts.settings import *

# Create a class for the checkboxes
class checkbox:
    # Initialise the class with a construcor
    def __init__(self, settings:dict,
                x=0,y=0,width=100,height=100,colours:tuple=((255,255,255), (255,255,255),(255,255,255)),
                label:str="box",labelShadow:bool=True,labelShadowOffset:tuple=(-3,3),labelFont=pygame.font.SysFont(None,32),
                boxShadow:bool=True,boxShadowOffset:tuple=(-5,5),
                cursorRect:pygame.Rect=None,doController:bool=False,controller:pygame.joystick.Joystick=None,
                controllerControlls:dict={},
                command=None,commandParameters:list=None,sound=None,
                inactive:bool=False, checked:bool=False,
                boxOffset=(0,0), labelOffset=(0,0),
                boxCurve=0,
                boxShadowAlpha=100,labelShadowAlpha=100):
        # Initialise parameter variables
        self.settings = settings
        self.x, self.y, self.width, self.height = x, y, width, height
        self.colours = colours
        self.label, self.labelShadow, self.labelShadowOffset, self.labelFont = label, labelShadow, labelShadowOffset, labelFont
        self.boxShadow, self.boxShadowOffset = boxShadow, boxShadowOffset
        self.cursorRect, self.doController, self.controller = cursorRect, doController, controller
        self.controllerControlls = controllerControlls
        self.command, self.commandParameters, self.sound = command, commandParameters, sound
        self.inactive, self.checked = inactive, checked
        self.boxOffset, self.labelOffset = boxOffset, labelOffset
        self.boxCurve = boxCurve
        self.boxShadowAlpha, self.labelShadowAlpha = boxShadowAlpha, labelShadowAlpha
        # Save the values before rescaling
        self.originalPosition = (0, 0) # Got when calculating new position values
        self.originalSize = (self.width, self.height)
        self.originalShadowOffset = self.labelShadowOffset
        self.originalboxShadowOffset = self.boxShadowOffset
        self.originalboxOffset = self.boxOffset
        self.originalLabelOffset = self.labelOffset
        # Customise Variables
        self.width *= self.settings["multX"]
        self.height *= self.settings["multY"]
        self.labelShadowOffset = (self.labelShadowOffset[0]*self.settings["multX"],self.labelShadowOffset[1]*self.settings["multY"])
        self.boxShadowOffset = (self.boxShadowOffset[0]*self.settings["multX"],self.boxShadowOffset[1]*self.settings["multY"])
        self.boxOffset = (self.boxOffset[0]*self.settings["multX"],self.boxOffset[1]*self.settings["multY"])
        self.labelOffset = (self.labelOffset[0]*self.settings["multX"],self.labelOffset[1]*self.settings["multY"])
        # Initialise extra variables
        # Set varaibles to check whether a preset position has been passed in instead of a number value
        self.posXStr = ""
        self.posYStr = ""
        # Set a current colour variable for the box
        self.currentColour = self.colours[0]
        # -- Create the rect for the box --
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
        self.rect.x = self.x + self.boxOffset[0]
        self.rect.y = self.y + self.boxOffset[1]
        # -- Create the shadow for the box from a subroutine --
        self.boxShadowSurface = self.createboxShadow()
        # -- Create a text surface --
        self.text = self.createText(255)
        # -- Create shadow for the text --
        self.textShadow = self.createText(self.labelShadowAlpha)
        # -- Calculate the text position -- 
        self.textX = self.rect.right + (10 * self.settings["multX"]) + self.labelOffset[0]
        self.textY = self.rect.centery - self.text.get_height()/2 + self.labelOffset[1]
        # Set variables to handle inputs with the mouse and the box
        self.canClick = False
        self.canPress = False
                
    # Subroutine to create a shadow for the box
    def createboxShadow(self):
        # Create a surface for the shadow and make it the same size as the box
        surf = pygame.Surface((self.rect.width, self.rect.height))
        # Fill the surface to a colour
        surf.fill((1,1,4))
        # Set a colourkey for the surface the same colour as filled to make it transparrent
        surf.set_colorkey((1,1,4))
        # Draw the box rect copy on the surface
        pygame.draw.rect(surf, self.currentColour, (0,0,self.rect.width,self.rect.height), 0, self.boxCurve)
        # Set the transparrency value of the surface to make it darker -- simulates shadow effect
        surf.set_alpha(self.boxShadowAlpha)
        # Return the surface
        return surf.convert_alpha()

    # Subroutine to create a shadow for the text
    def createText(self, alphaValue):
        # Create a surface for the text
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
    
    # Subroutine to resize the box
    def updateSize(self, settings):
        self.settings = settings
        # Get the new text surface
        self.text = self.createText(255)
        # Get the new text shadow surface
        self.textShadow = self.createText(self.labelShadowAlpha)
        # Calculate the new box size
        self.rect.width = self.originalSize[0] * self.settings["multX"]
        self.rect.height = self.originalSize[1] * self.settings["multY"]
        # Get the new rect shadow surface
        self.boxShadowSurface = self.createboxShadow()
        # Calculate the new values
        # X and Y
        if self.posXStr == "": self.x = self.originalPosition[0] * self.settings["multX"]
        else: self.x = self.convertAxis(self.posXStr, "x")
        if self.posYStr == "": self.y = self.originalPosition[1] * self.settings["multY"]
        else: self.y = self.convertAxis(self.posYStr, "y")
        # Offsets
        self.labelOffset = (self.originalLabelOffset[0]*self.settings["multX"], self.originalLabelOffset[1]*self.settings["multY"])
        self.boxOffset = (self.originalboxOffset[0]*self.settings["multX"], self.originalboxOffset[1]*self.settings["multY"])
        self.shadowOffset = (self.originalShadowOffset[0]*self.settings["multX"], self.originalShadowOffset[1]*self.settings["multY"])
        self.boxShadowOffset = (self.originalboxShadowOffset[0]*self.settings["multX"], self.originalboxShadowOffset[1]*self.settings["multY"])
        # Update rect x and y values
        self.rect.x = self.x + self.boxOffset[0]
        self.rect.y = self.y + self.boxOffset[1]
        # text X and Y
        self.textX = self.rect.right + (10 * self.settings["multX"]) + self.labelOffset[0]
        self.textY = self.rect.centery - self.text.get_height()/2 + self.labelOffset[1]
    
    # Subroutine to handle controller input
    def controllerInput(self, controllerButton):
        # Check if the controller has interacted with the button
        if controllerButton and self.canPress:
            self.canPress = False
            self.handlePress()

    # Subroutine to handle mouse input
    def mouseInput(self, mouseButton):
        # Check if the mouse has interacted with the button
        if mouseButton == (1, 0, 0) and self.canClick:
            self.canClick = False
            self.handlePress()
            
    # Subroutine to handle command calling and sound playing
    def handlePress(self):
        if self.checked: self.checked = False
        else: self.checked = True

        # Check if there is a command present
        if self.command != None:
            # Check if there are any parameters
            if self.commandParameters != None:
                # Call the command with the parameters
                parameters = self.commandParameters
                if parameters == "label": parameters = self.label
                self.command(self.checked, parameters)
            # If there aren't any parameters, call the function normally
            else:
                self.command(self.checked)
        # Check if there is a sound passed in
        if self.sound != None:
            # Create a sound object
            sound = pygame.mixer.Sound(self.sound)
            sound.play()

    # Subroutine to update the box
    def update(self, settings, cursorRect, controller=None, allowController=None, controllerName=None):
        # Update the settings dict
        self.settings = settings
        # Update the mouse rect
        self.cursorRect = cursorRect
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

        if not self.doController:
            # Check if the button is being pressed -- used so clicks can only happen 1 at a time
            if mouseButton != (1, 0, 0):
                # Set the click to true
                self.canClick = True
        else:
            # Check if the controller button is being pressed
            if not controllerButton:
                # Set the press to True
                self.canPress = True
                
        # Check if the button intersects with the middle of the cursor rect
        if self.rect.collidepoint(self.cursorRect.center):
            # Check if the controller is being used as main input
            if self.doController: self.controllerInput(controllerButton)
            # Else call subroutine to handle mouse input
            else: self.mouseInput(mouseButton)
    
        # Only check if the current input is the mouse
        if not self.doController:
            # Check if the button is being pressed -- used so clicks can only happen 1 at a time
            if mouseButton == (1, 0, 0):
                # Set the click to false
                self.canClick = False
        else:
            # Check if the controller button is being pressed
            if controllerButton:
                # Set the press to True
                self.canPress = False
            
    # Subroutine to draw the button onto the given surface
    def draw(self, screen):
        # Check if the shadow for the button is enabled
        if self.boxShadow:
            # Calculate the x position of the surface
            shadowX = self.rect.x + self.boxShadowOffset[0]
            # Calculate the y position of the surface
            shadowY = self.rect.y + self.boxShadowOffset[1]
            # Draw the shadow onto the surface
            screen.blit(self.boxShadowSurface, (shadowX, shadowY))

        # Draw the box rect onto the surface
        # Check if the box is checked
        if self.checked:
            pygame.draw.rect(screen, self.currentColour, self.rect, 0, self.boxCurve)
        else:
            pygame.draw.rect(screen, self.currentColour, self.rect, int(7*self.settings["multY"]), self.boxCurve)

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
    
     