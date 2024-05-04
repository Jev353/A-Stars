from map_components import Edge
from map_components import Node
from map_components import Graph
from session_components import AStar
from session_components import User

from database_connector import *

import os

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QLineEdit, QPushButton, QLabel
from PyQt6.QtCore import pyqtSlot

import pygame
from assets import *

# Initialize map information
graph = Graph(20, 20)
aStar = AStar()

# Initialize user object
activeUser: User = None

# Initialize pygame screen
windowWidth: int = 1152
windowHeight: int = 828
screen = pygame.display.set_mode((windowWidth, windowHeight))

# Load in data from the login.ui file
Form, Window = uic.loadUiType("login.ui")

# Get the application, window, and form
app = QApplication([])
window = Window()
form = Form()

# Initialize storage for UI Nodes
clickableNodes: list[ClickableNode] = []

# Initialize various QWidget variables
usernameLineEdit: QLineEdit = QLineEdit()
signUpPushButton: QPushButton = QPushButton()
logInPushButton: QPushButton = QPushButton()
errorLabel: QLabel = QLabel()

def main():
    # Initialize and display the Login menu
    initLoginMenu()
    
    # If we've reached here and the activeUser is still None, then the user X'd out of the login screen
    if activeUser == None:
        return
    
    # Initialize PyGame
    pygame.init()
    
    # Displays the PyGame screen, including the Nodes
    resetScreen()
    
    # Initialize list of selected nodes
    selectedNodes: list[ClickableNode] = []
    routeDisplayed = False
    
    # Run PyGame until the user exits
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

# Attempts to log the user in with the username in usernameLineEdit.
def attemptLogin():
    # You can't pass arguments to button functions D:
    global usernameLineEdit
    global activeUser
    global app
    global errorLabel
    
    # You literally have to get a widget every time the button is pressed or the 
    # text won't update. Insane
    for widget in app.allWidgets():
        if type(widget) == QLineEdit:
            usernameLineEdit = widget
            continue
        if type(widget) == QLabel and widget.text() == "":
            errorLabel = widget
            continue
    
    user = getUserFromUsername(usernameLineEdit.text())
    
    # Display error message if account doesn't exist
    if (user == None):
        errorLabel.setText("Login Failed")
    else:
        activeUser = user
        
        # Advance to the PyGame part if we've logged in
        app.quit()

# Attempts create an account with the username in usernameLineEdit.
def attemptAccountCreation():
    # You can't pass arguments to button functions D:
    global usernameLineEdit
    global activeUser
    global app
    global errorLabel
    
    # You literally have to get a widget every time the button is pressed or the 
    # text won't update. Insane
    for widget in app.allWidgets():
        if type(widget) == QLineEdit:
            usernameLineEdit = widget
            continue
        if type(widget) == QLabel and widget.text() == "":
            errorLabel = widget
            continue
    
    user = addNewUser(usernameLineEdit.text())
    
    # Display error message if account can't be created
    if (user == -1):
        errorLabel.setText("Username Taken")
    else:
        activeUser = getUserFromUsername(usernameLineEdit.text())
        
        # Advance to the PyGame part if we've logged in
        app.quit()

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

def initLoginMenu():
    global usernameLineEdit
    global activeUser
    global app
    global errorLabel
    
    # Setup the UI using the window, display the window to the app
    form.setupUi(window)
    window.show()
    
    # Set window position
    window.move(705, 96)
    
    # Get the necessary QWidgets from the app
    for widget in app.allWidgets():
        if type(widget) == QLineEdit:
            usernameLineEdit = widget
            continue
        if type(widget) == QPushButton and widget.text() == "Sign up":
            signUpPushButton = widget
            continue
        if type(widget) == QPushButton and widget.text() == "Login":
            logInPushButton = widget
            continue
        if type(widget) == QLabel and widget.text() == "":
            errorLabel = widget
            continue
    
    # Connect buttons to functions
    signUpPushButton.clicked.connect(attemptAccountCreation)
    logInPushButton.clicked.connect(attemptLogin)
    
    # Execute the application
    app.exec()

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