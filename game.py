import pygame, sys, time, qiskit, math

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

class Button:
  def __init__(self, width, height, name, color):
    self.width = width
    self.height = height
    self.name = name
    self.color = color
  
  def mouseOnButton(self, left, top, mouse_pos):
    return (mouse_pos[0] > left and mouse_pos[0] < left + self.width and mouse_pos[1] > top and mouse_pos[1] < top + self.height)

  def draw(self, left, top):
    pygame.draw.rect(screen, self.color, pygame.Rect(left, top, self.width, self.height))
    
def renderButtons(buttons, left, top):
  button_spacing = 50
  for i in range(len(buttons)):
    buttons[i].draw(left + i * (buttons[i].width + button_spacing), top)

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

current_gate = '0'

def handleEvents():
  events = pygame.event.get()
  for i in range(len(events)):
    if events[i].type == pygame.QUIT:
      quitGame()
    if events[i].type == pygame.MOUSEBUTTONDOWN:
      for button in buttons:
        if button.mouseOnButton(bounding_box.left, bounding_box.top + bounding_box.height + button_margin, pygame.mouse.get_pos()):
          print("BUTTON " + button.name)
          global current_gate # bad practice but works for now
          current_gate = button.name
          return
      if (mouse_pos[0]) < 0:
        return
      if (current_gate == '0'):
        return
      board[mouse_pos[0]][mouse_pos[1]] = current_gate


current_gate = '0'
pygame.init()
SCREEN_X = 1280 * 2/3
SCREEN_Y = 960 * 2/3
screen = pygame.display.set_mode((SCREEN_X,SCREEN_Y))
GRID_SIZE = 3
GRID_THICKNESS = 5
board = []
for i in range(GRID_SIZE):
  row = []
  for j in range(GRID_SIZE):
    row.append("0")
  board.append(row)
boardToCircuit()
bounding_box = pygame.Rect(100,100,400,400)
button_width = 50
button_height = 50
buttons = [
  Button(button_width, button_height, 'H', (255, 0, 0)),
  Button(button_width, button_height, 'X', (255, 255, 0)),
  Button(button_width, button_height, 'Y', (0, 0, 255)),
  Button(button_width, button_height, 'Z', (0, 255, 0)),
]
button_margin = 50

while True:
  drawGrid(bounding_box)
  mouse_pos = mouseCoordToGrid(bounding_box)
  drawGridElements(bounding_box)
  renderButtons(buttons, bounding_box.left, bounding_box.top + bounding_box.height + button_margin)
  handleEvents()
  print(current_gate)
  pygame.display.update()
  screen.fill((255,255,255))
  time.sleep(0.01)
