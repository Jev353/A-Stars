import pygame

# Get images
mapADAImage = pygame.image.load("assets\\mapADA.png")
mapNoADAImage = pygame.image.load("assets\\mapNoADA.png")

## UI Object representing a node that can be clicked
class ClickableNode:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        
        self.radius = 25
        surfaceWidth = self.radius * 2
        surfaceHeight = self.radius * 2
        
        # Create transparent surface
        self.surface = pygame.Surface((surfaceWidth, surfaceHeight), pygame.SRCALPHA)
        
        # Draw a circle on the surface
        pygame.draw.circle(self.surface, "red", (self.radius, self.radius), self.radius)
        
        # Move the rect to the actual location
        self.clickRect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)