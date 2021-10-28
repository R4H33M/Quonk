import pygame, sys, time, qiskit, math
from qiskit import *
import numpy as np
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt

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
    pygame.draw.rect(screen, self.color, pygame.Rect(left, top, self.width, self.height))


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
  events = pygame.event.get()
  for i in range(len(events)):
    if events[i].type == pygame.QUIT:
      quitGame()
    if events[i].type == pygame.MOUSEBUTTONDOWN:
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

def boardToCircuit():
  global board
  qc1 = qiskit.QuantumCircuit(GRID_SIZE)
  qc2 = qiskit.QuantumCircuit(GRID_SIZE)
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      if (board[i][j] == "H"):
        qc1.h(j)
  for j in range(GRID_SIZE):
    for i in range(GRID_SIZE):
      if (board[i][j] == "H"):
        qc2.h(i)

  print(qc1)
  print(qc2)
  return [qc1, qc2]

def drawGridElements(boundingRect):
  global board
  vert_spacing = boundingRect.width/(GRID_SIZE+1)
  hori_spacing = boundingRect.height/(GRID_SIZE+1)
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      # H gate
      if board[i][j] == "H":
        pygame.draw.circle(screen, (255, 0, 0), (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), 30)
      # X gate
      if board[i][j] == "X":
        pygame.draw.circle(screen, (255, 255, 0), (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), 30)
      # Y gate
      if board[i][j] == "Y":
        pygame.draw.circle(screen, (0, 0, 255), (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), 30)
      # Z gate
      if board[i][j] == "Z":
        pygame.draw.circle(screen, (0, 255, 0), (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), 30)


def drawButtons(buttons, left, top):
  for i in range(len(buttons)):
    buttons[i].draw(left + i * (buttons[i].width + button_spacing), top)



#Deleted this function and replaced with getProbability.

#def calculateScores():
 # global simulator
  #circuits = boardToCircuit()
  #circuits[0].save_statevector()
  #circuits[0] = transpile(circuits[0], simulator)
  #resultp1 = simulator.run(circuits[0]).result()
  #statevectorp1 = resultp1.get_statevector(circuits[0])

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


# Visualising the Quantum State as a QSphere
def qsphere(qc):
    state = Statevector(qc)
    state.draw('qsphere')


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

while True:
    drawGrid(bounding_box)
    drawButtons(buttons, bounding_box.left, bounding_box.top + bounding_box.height + button_margin)
    mouse_pos = mouseCoordToGrid(bounding_box)
    drawGridElements(bounding_box)
    handleEvents()
    pygame.display.update()
    screen.fill((255,255,255))
    time.sleep(0.01)
