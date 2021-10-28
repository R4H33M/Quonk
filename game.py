import pygame, sys, time, qiskit, math
from qiskit import *
import numpy as np
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
simulator = Aer.get_backend('aer_simulator')


probabilities = [] # Used to keep all probability data

# Gate selector buttons
class Button:
  def __init__(self, width, height, name, color):
    self.width = width
    self.height = height
    self.name = name
    self.color = color

  # Returns true if mouse position is on the button
  def mouseOnButton(self, left, top, mouse_pos):
    return (mouse_pos[0] > left and mouse_pos[0] < left + self.width and mouse_pos[1] > top and mouse_pos[1] < top + self.height)

  # Render button
  def draw(self, left, top): 
    button = pygame.Surface((self.width, self.height))
    pygame.draw.rect(button, self.color, pygame.Rect(0, 0, self.width, self.height))
    label = myfont.render(self.name, True, (255, 255, 255))
    button.blit(label, ((self.width-label.get_width())/2, (self.height-label.get_height())/2))
    screen.blit(button, (left, top))

def quitGame():
  pygame.display.quit()
  sys.exit()

#Draw a grid of size GRID_SIZE within a bounding box
def drawGrid(boundingRect):
  #Draw vertical lines
  vert_spacing = boundingRect.width/(GRID_SIZE+1)
  for i in range(GRID_SIZE):
    pygame.draw.rect(screen, (255,0,0), ((i+1)*vert_spacing + boundingRect.left, boundingRect.top, GRID_THICKNESS, boundingRect.height))
  #Draw horizontal lines
  hori_spacing = boundingRect.height/(GRID_SIZE+1)
  for i in range(GRID_SIZE):
    pygame.draw.rect(screen, (255,0,0), (boundingRect.left, (i+1)*hori_spacing + boundingRect.top, boundingRect.width ,GRID_THICKNESS))


# Convert mouse's x,y position to i,j on the grid
def mouseCoordToGrid(boundingRect):
  mouse_pos = pygame.mouse.get_pos()
  vert_spacing = boundingRect.width/(GRID_SIZE+1)
  hori_spacing = boundingRect.height/(GRID_SIZE+1)
  i = math.floor((mouse_pos[0] - boundingRect.left - 0.5 * vert_spacing)/vert_spacing)
  j = math.floor((mouse_pos[1] - boundingRect.top - 0.5 * hori_spacing)/hori_spacing)
  if i < 0 or i > GRID_SIZE - 1 or j < 0 or j > GRID_SIZE - 1:
    i = -1
    j = -1
  return(i, j)

# Handles user input
def handleEvents():
  global current_gate, board
  events = pygame.event.get()
  for i in range(len(events)):
    if events[i].type == pygame.QUIT:
      quitGame()
    elif events[i].type == pygame.MOUSEBUTTONDOWN:
      # check if pressing button
      for i in range(len(buttons)):
        if buttons[i].mouseOnButton(bounding_box.left + i * (buttons[i].width + button_spacing), bounding_box.top + bounding_box.height + button_margin, pygame.mouse.get_pos()):
          print("BUTTON " + buttons[i].name)
          global current_gate # very funky python is weird
          current_gate = buttons[i].name
          return
      # check if out of bounds
      if (mouse_pos[0]) < 0:
        return
      if (current_gate == '0'):
        return
      # update board
      board[mouse_pos[0]][mouse_pos[1]] = current_gate
      images = calculateGraphs()
    elif events[i].type == pygame.KEYUP:
      rotateBoard()
      print(board)

def boardLineToCircuit(player, qubit):
  global board
  qc = qiskit.QuantumCircuit(1)
  for i in range(GRID_SIZE):
    if player == 1:
      if board[i][qubit] == "H": qc.h(0)
      if board[i][qubit] == "X": qc.x(0)
      if board[i][qubit] == "Y": qc.y(0)
      if board[i][qubit] == "Z": qc.z(0)
    elif player == 2:
      if board[qubit][i] == "H": qc.h(0)
      if board[qubit][i] == "X": qc.x(0)
      if board[qubit][i] == "Y": qc.y(0)
      if board[qubit][i] == "Z": qc.z(0)
  return qc

def drawGridElements(boundingRect):
  global board
  vert_spacing = boundingRect.width/(GRID_SIZE+1)
  hori_spacing = boundingRect.height/(GRID_SIZE+1)
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      if (board[i][j] != "0"):
        # H gate
        color = (0, 0, 0)
        if board[i][j] == "H":
          color = (255, 0, 0)
        # X gate
        if board[i][j] == "X":
          color = (255, 255, 0)
        # Y gate
        if board[i][j] == "Y":
          color = (0, 0, 255)
        # Z gate
        if board[i][j] == "Z":
          color = (0, 255, 0)
        radius = vert_spacing * .4
        pygame.draw.circle(screen, color, (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), radius)
        # text
        label = myfont.render(board[i][j], True, (255, 255, 255))
        screen.blit(label, (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)* hori_spacing))



def drawButtons(buttons, left, top):
  for i in range(len(buttons)):
    buttons[i].draw(left + i * (buttons[i].width + button_spacing), top)


def calculateScore(player, qubit):
  global simulator
  circuit = boardLineToCircuit(player, qubit)
  circuit.save_statevector()
  circuit = transpile(circuit, simulator)
  result = simulator.run(circuit).result()
  statevector = result.get_statevector(circuit)
  return np.around(np.real(statevector[1]*np.conj(statevector[1])), decimals = 2)

# Calculate Probability Vector
def getProbability(qc):
    state = Statevector(qc)
    probs = state.probabilities()
    probabilities.append(probs)
    return probs #NumPy array

# Visualising the Probability Distribution

# Generate all possible binary strings of length n
# list returns [0, 1, 2, ..., 1<<n - 1] in binary
def generateCode(n):
  if n==1:
    return ['0', '1']
  
  else:
    return ['0'+x for x in generateCode(n-1)] + ['1'+x for x in generateCode(n-1)]

# Plot probability using matplotlib
def plotProbability(data):
  n = math.log2(data.size)
  xk = generateCode(n)
  pk = data

  l = plt.plot(np.arange(data.size), pk)
  for i in range(data.size):
    plt.fill([i-0.5, i-0.5, i+0.5, i+0.5],[0, pk[i], pk[i], 0] ,color='red', alpha = 0.5)

  plt.xticks(np.arange(data.size), xk)
  l = l.pop(0)
  l.remove() 
  plt.savefig("./plot.png")

#clockwise 90 degree rotation (no animations!)
def rotateBoard():
  global board
  newboard = []
  for i in range(GRID_SIZE):
    newboard.append(board[i].copy())
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      newboard[GRID_SIZE-i-1][j] = board[j][i]
  board = newboard


def boardsToCircuit():
  global board
  qc1 = qiskit.QuantumCircuit(GRID_SIZE)
  qc2 = qiskit.QuantumCircuit(GRID_SIZE)
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      if (board[i][j] == "H"): qc1.h(j)
      if (board[i][j] == "X"): qc1.x(j)
      if (board[i][j] == "Y"): qc1.y(j)
      if (board[i][j] == "Z"): qc1.z(j)
  for j in range(GRID_SIZE):
    for i in range(GRID_SIZE):
      if (board[i][j] == "H"): qc2.h(i)
      if (board[i][j] == "X"): qc2.x(i)
      if (board[i][j] == "Y"): qc2.y(i)
      if (board[i][j] == "Z"): qc2.z(i)
  return [qc1, qc2]

# Visualising the Quantum State as a QSphere
def qsphere(qc):
    state = Statevector(qc)
    state.draw('qsphere')

def drawScores():
  global myfont, screen, bounding_box
  hori_spacing = bounding_box.height/(GRID_SIZE+1)
  vert_spacing = bounding_box.width/(GRID_SIZE+1)
  # for player 1
  for qubit in range(GRID_SIZE):
    textsurface = myfont.render(str(calculateScore(1, qubit)), False, (0, 0, 0))
    screen.blit(textsurface, (bounding_box.right,(qubit+1)*hori_spacing + bounding_box.top))
  
  # for player 2
  for qubit in range(GRID_SIZE):
    textsurface = myfont.render(str(calculateScore(2, qubit)), False, (0, 0, 0))
    screen.blit(textsurface, ((qubit+1)*vert_spacing + bounding_box.left, bounding_box.bottom))

def calculateGraphs():
  print("calculate")
  plotProbability(getProbability(boardsToCircuit()[0]))
  image1 = pygame.image.load("./plot.png")
  image1 = pygame.transform.scale(image1, (400, image1.get_height() * 400.0 / image1.get_width()))
  plotProbability(getProbability(boardsToCircuit()[1]))
  image2 = pygame.image.load("./plot.png")
  image2 = pygame.transform.scale(image2, (400, image2.get_height() * 400.0 / image2.get_width()))
  return (image1, image2)

def drawGraphs(images):
  margin = 50
  screen.blit(images[0], (bounding_box.left + bounding_box.width + margin, 50))
  screen.blit(images[1], (bounding_box.left + bounding_box.width + margin, 50 + images[0].get_height() + 20))

pygame.init()

# Create screen
SCREEN_X = 640 * 1.5
SCREEN_Y = 480 * 1.5
screen = pygame.display.set_mode((SCREEN_X,SCREEN_Y))

# Create grid board
GRID_SIZE = 3
GRID_THICKNESS = 5
board = []
for i in range(GRID_SIZE):
  row = []
  for j in range(GRID_SIZE):
    row.append("0")
  board.append(row)
bounding_box = pygame.Rect(100,100,400,400)

# Create buttons  
current_gate = '0'
button_width = 50
button_height = 50
button_margin = 50
button_spacing = 50
buttons = [
  Button(button_width, button_height, 'H', (255, 0, 0)),
  Button(button_width, button_height, 'X', (255, 255, 0)),
  Button(button_width, button_height, 'Y', (0, 0, 255)),
  Button(button_width, button_height, 'Z', (0, 255, 0)),
]

# Prepare stuff for text drawing
pygame.font.init()
myfont = pygame.font.SysFont('Comic Sans MS', 45)

# Testing board state
board[0][0] = "H"
board[1][0] = "X"
print(boardsToCircuit()[0])
print(boardsToCircuit()[1])

images = calculateGraphs()

while True:
    drawGrid(bounding_box)
    drawButtons(buttons, bounding_box.left, bounding_box.top + bounding_box.height + button_margin)
    drawScores()
    drawGraphs(images)
    mouse_pos = mouseCoordToGrid(bounding_box)
    drawGridElements(bounding_box)
    handleEvents()
    pygame.display.update()
    screen.fill((255,255,255))
    time.sleep(0.01)
