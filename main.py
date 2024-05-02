from map_components import Edge
from map_components import Node
from map_components import Graph
from session_components import AStar
from session_components import User

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton

import pygame
from assets import *

# Initialize map information
graph = Graph(20, 20)
aStar = AStar()

# Initialize user object
activeUser: User

# Initialize PyGame
pygame.init()

# Initialize screen
windowWidth: int = 1152
windowHeight: int = 828
screen = pygame.display.set_mode((windowWidth, windowHeight))

# Initialize storage for UI Nodes
clickableNodes: list[ClickableNode] = []

def main():
    # Load in data from the login.ui file
    Form, Window = uic.loadUiType("login.ui")

    # Get the application, window, and form
    app = QApplication([])
    window = Window()
    form = Form()
    
    # Setup the UI using the window, display the window to the app
    form.setupUi(window)
    window.show()
    
    # Initialize various QWidget variables
    usernameLineEdit: QLineEdit
    signUpPushButton: QPushButton
    logInPushButton: QPushButton
    
    # Get the necessary QWidgets from the app
    for widget in app.allWidgets():
        if type(widget) == QLineEdit:
            usernameLineEdit = widget
            continue
        if type(widget) == QPushButton and widget.objectName == "signUpPushButton":
            signUpPushButton = widget
            continue
        if type(widget) == QPushButton and widget.objectName == "logInPushButton":
            logInPushButton = widget
            continue
    
    # Execute the application
    app.exec()
    
    print(app.widgetAt)
    
    # Displays the screen, including the Nodes
    resetScreen()
    
    # Initialize list of selected nodes
    selectedNodes: list[ClickableNode] = []
    routeDisplayed = False
    
    keepRunning = True
    while (keepRunning):
        # If 2 nodes have been selected, generate and display a route between them
        if (len(selectedNodes) == 2 and not routeDisplayed):
            generateAndDisplayRoute(selectedNodes[0], selectedNodes[1])
            routeDisplayed = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                keepRunning = False
                
            # Handle node clicking
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Iterate through all nodes, checking which one was clicked
                for node in clickableNodes:
                    if node.clickRect.collidepoint(event.pos):
                        # If this is the third node clicked, then reset the route and selectedNodes
                        if (len(selectedNodes) >= 2):
                            selectedNodes.clear()
                            routeDisplayed = False
                            resetScreen()
                        
                        # Update the node's color to purple
                        pygame.draw.circle(node.surface, "purple", (node.radius, node.radius), node.radius)
                        
                        # Draw the new purple node to the screen
                        screen.blit(node.surface, 
                                   (node.x - node.surface.get_width()/2, 
                                    node.y - node.surface.get_height()/2))
                        
                        # Mark the node as selected
                        selectedNodes.append(node)
                        
                        # Don't check any more nodes
                        break
                
                # Update the screen
                pygame.display.update()
                        
    pygame.quit()
    
    # Initialize active user object
    # global activeUser
    # activeUser = loginMenu()
    
    # mainMenu()

# Resets the screen to how it looked upon boot
def resetScreen(displayEdges: bool = False):
    # Copy the non-ADA to the screen
    screen.blit(mapNoADAImage, (0,0))
    
    # Display all nodes
    displayAllNodes()
    
    # Only display edges if requested
    if displayEdges:
        displayAllEdges()
        
    # Update the window
    pygame.display.update()

# Display a default visual representation of all nodes
def displayAllNodes():
    # Create a UI Node for each node in the graph
    for node in graph.nodes:
        newClickableNode = ClickableNode(node.ID, int(node.xCoordinate), int(node.yCoordinate))
        clickableNodes.append(newClickableNode)
        
        # Copy the new ClickableNode to the screen
        screen.blit(newClickableNode.surface, 
                    (newClickableNode.x - newClickableNode.surface.get_width()/2, 
                     newClickableNode.y - newClickableNode.surface.get_height()/2))
        
    # Update the window
    pygame.display.update()

# Display a visual representation of all edges
def displayAllEdges():
    # Draw lines representing edges for each node
    for edge in graph.edges:
        # Initialize leftmost and rightmost node variables
        leftmostNode: Node
        rightmostNode: Node
        
        # Get the leftmost node 
        if (int(edge.nodes[0].xCoordinate) <= int(edge.nodes[1].xCoordinate)):
            leftmostNode = edge.nodes[0]
            rightmostNode = edge.nodes[1]
        else:
            leftmostNode = edge.nodes[1]
            rightmostNode = edge.nodes[0]
        
        pygame.draw.line(screen, "green", 
                         (int(leftmostNode.xCoordinate), int(leftmostNode.yCoordinate)), 
                         (int(rightmostNode.xCoordinate), int(rightmostNode.yCoordinate)), 
                         3)        
    
    # Update the window
    pygame.display.update()

# Generates a route between the two nodes via AStar and displays it
def generateAndDisplayRoute(firstNode: ClickableNode, secondNode: ClickableNode):
    global graph
    
    # Get the backend nodes that the UI nodes represent
    backendFirstNode = graph.getNodeFromID(firstNode.ID)
    backendSecondNode = graph.getNodeFromID(secondNode.ID)
    
    # Get a route between the two nodes
    routeEdgeIDs = aStar.generateRoutePath(graph, backendFirstNode.ID, backendSecondNode.ID)
    
    # Display route via edges
    for edgeID in routeEdgeIDs:
        edge = graph.getEdgeFromID(edgeID)
        
        # Initialize leftmost and rightmost node variables
        leftmostNode: Node
        rightmostNode: Node
        
        # Get the leftmost node 
        if (int(edge.nodes[0].xCoordinate) <= int(edge.nodes[1].xCoordinate)):
            leftmostNode = edge.nodes[0]
            rightmostNode = edge.nodes[1]
        else:
            leftmostNode = edge.nodes[1]
            rightmostNode = edge.nodes[0]
        
        pygame.draw.line(screen, "blue", 
                         (int(leftmostNode.xCoordinate), int(leftmostNode.yCoordinate)), 
                         (int(rightmostNode.xCoordinate), int(rightmostNode.yCoordinate)), 
                         3)
        
    # Reset graph due to issues with deep copy
    graph = Graph(20, 20)
        
    pygame.display.update()
  
main()