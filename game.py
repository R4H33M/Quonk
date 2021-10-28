import pygame, sys, time, qiskit, math
from qiskit import Aer, transpile
simulator = Aer.get_backend('aer_simulator')

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

def mouseCoordToGrid(boundingRect):
  mouse_pos = pygame.mouse.get_pos()
  vert_spacing = boundingRect.width/(GRID_SIZE+1)
  hori_spacing = boundingRect.height/(GRID_SIZE+1)
  i = math.floor((mouse_pos[0] - boundingRect.left - 0.5 * vert_spacing)/vert_spacing)
  j = math.floor((mouse_pos[1] - boundingRect.top - 0.5 * hori_spacing)/hori_spacing)
  if i < 0 or i > GRID_SIZE - 1 or j < 0 or j > GRID_SIZE - 1:
    i = -1
    j -1
  return(i, j)

def handleEvents():
    events = pygame.event.get()
    for i in range(len(events)):
        if events[i].type == pygame.QUIT:
          quitGame()
        if events[i].type == pygame.MOUSEBUTTONDOWN:
            if (mouse_pos[0]) < 0:
                return
            board[mouse_pos[0]][mouse_pos[1]] = 'H'

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
        pygame.draw.circle(screen, (0,0,200), (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), 30)
      # X gate
      if board[i][j] == "X":
        pygame.draw.circle(screen, (0,200,0), (boundingRect.left + (i+1)*vert_spacing, boundingRect.top + (j+1)*hori_spacing), 30)

def calculateScores():
  global simulator
  circuits = boardToCircuit()
  circuits[0].save_statevector()
  circuits[0] = transpile(circuits[0], simulator)
  resultp1 = simulator.run(circuits[0]).result()
  statevectorp1 = resultp1.get_statevector(circuits[0])

pygame.init()
SCREEN_X = 640
SCREEN_Y = 480
screen = pygame.display.set_mode((SCREEN_X,SCREEN_Y))
GRID_SIZE = 3
GRID_THICKNESS = 5
board = []
for i in range(GRID_SIZE):
  row = []
  for j in range(GRID_SIZE):
    row.append("0")
  board.append(row)

while True:
    bounding_box = pygame.Rect(50,100,400,400)
    drawGrid(bounding_box)
    mouse_pos = mouseCoordToGrid(bounding_box)
    drawGridElements(bounding_box)
    handleEvents()
    pygame.display.update()
    screen.fill((255,255,255))
    time.sleep(0.01)