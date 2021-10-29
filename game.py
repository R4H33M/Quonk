from qiskit import *
import pygame, sys, time, qiskit, math, random
import numpy as np
from qiskit.quantum_info import Statevector
import matplotlib.pyplot as plt
from qiskit.providers.aer import QasmSimulator

class Button:
  def __init__(self, name, left, top, width, height):
    self.name = name
    self.left = left
    self.top = top
    self.width = width 
    self.height = height
    self.image = pygame.image.load("./assets/" + self.name + ".png")
    self.image = pygame.transform.scale(self.image, (width, height))

  # Returns true if mouse position is on the button
  def mouseOnButton(self, mouse_pos):
    return (mouse_pos[0] > self.left and mouse_pos[0] < self.left + self.width and mouse_pos[1] > self.top and mouse_pos[1] < self.top + self.height)

  # Render button
  def draw(self): 
    if (self.mouseOnButton(pygame.mouse.get_pos())):
      HOVER_SCALE = 1.1
      image = pygame.transform.scale(self.image, (self.width * HOVER_SCALE, self.height * HOVER_SCALE))
      screen.blit(image, (self.left - (self.width*HOVER_SCALE - self.width)/2, self.top - (self.height*HOVER_SCALE - self.height)/2))
    else: 
      screen.blit(self.image, (self.left, self.top))

def scoreNumber(qc1, qc2, cs1, cs2, targetNum):    
    playerNums = oneShot(qc1, qc2)
    print(playerNums[0])
    if((playerNums[0] == targetNum and playerNums[1] == targetNum)):
        cs1 += 3
        cs2 += 3
        print('Player 1 and 2 Both Attained the Target!')
    elif(playerNums[0] == targetNum):
        cs1 += 3
        print('Player 1 Attained the Target!')
    elif(playerNums[1] == targetNum):
        cs1 += 3
        print('Player 1 Attained the Target!')
    elif(playerNums[0] == playerNums[1]):
        cs1 += 1
        cs2 += 1
        print('Player 1 and 2 Attained the Same Number!')
    elif(int(playerNums[0]) < int(playerNums[1])):
        cs2 += 1
        print('Player 2 Wins!')
    elif(int(playerNums[0]) > int(playerNums[1])):
        cs1 += 1
        print('Player 1 Wins!')
    return cs1, cs2, playerNums[0], playerNums[1]

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

def generateCode(n):
  if n==1:
    return ['0', '1']
  else:
    return ['0'+ x for x in generateCode(n-1)] + ['1'+x for x in generateCode(n-1)]

def targetNumber(GRID_SIZE):
  numstr = ''
  for i in range(GRID_SIZE):
    numstr += str(random.randint(0, 1))
  return numstr

def getProbability(qc):
    state = Statevector(qc)
    probs = state.probabilities()
    return probs #NumPy array

def rotateBoard(direction, gameBoard):
  newboard = []
  for i in range(GRID_SIZE):
      newboard.append(gameBoard[i].copy())
  if (direction == 'cw'):
    for i in range(GRID_SIZE):
      for j in range(GRID_SIZE):
        newboard[GRID_SIZE-i-1][j] = gameBoard[j][i]
  elif (direction == 'ccw'):  
    for i in range(GRID_SIZE):
      for j in range(GRID_SIZE):
        newboard[i][GRID_SIZE - j - 1] = gameBoard[j][i]
  return newboard

def drawButtons(buttons):
  for button in buttons:
    button.draw()

def calculateGraphs(gameBoard):
  player = 0
  plotProbability(getProbability(boardsToCircuit(gameBoard)[player]))
  image1 = pygame.image.load("./plot.png")
  image1 = pygame.transform.scale(image1, (356, image1.get_height() * 356 / image1.get_width()))
  player = 1
  plotProbability(getProbability(boardsToCircuit(gameBoard)[player]))
  image2 = pygame.image.load("./plot.png")
  image2 = pygame.transform.scale(image2, (356, image2.get_height() * 356 / image2.get_width()))
  return (image1, image2)

def drawGridElements(boundingRect):
  vert_spacing = boundingRect.width/(GRID_SIZE+1)
  hori_spacing = boundingRect.height/(GRID_SIZE+1)
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      if (board[i][j] != "0"):
        radius = vert_spacing * .4
        gate = ASSETS[board[i][j]]
        gate = pygame.transform.scale(gate, (radius*2,radius*2))
        screen.blit(gate, (boundingRect.left + (i+1)*vert_spacing - radius, boundingRect.top + (j+1)*hori_spacing - radius))

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
  plt.clf()

def drawGraphs(images, Box1, Box2):
  screen.blit(images[0], (Box1.left, Box1.top))
  screen.blit(images[0], (Box2.left, Box2.top))

# RETURN TWO BOARDS: PLAYER 1s and PLAYER 2s
def boardsToCircuit(gameBoard):
  qc1 = qiskit.QuantumCircuit(GRID_SIZE,GRID_SIZE)
  qc2 = qiskit.QuantumCircuit(GRID_SIZE, GRID_SIZE)
  for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
      if (gameBoard[i][j] == "H"): qc1.h(j)
      if (gameBoard[i][j] == "X"): qc1.x(j)
      if (gameBoard[i][j] == "Y"): qc1.y(j)
      if (gameBoard[i][j] == "Z"): qc1.z(j)
  for j in range(GRID_SIZE):
    for i in range(GRID_SIZE):
      if (gameBoard[i][j] == "H"): qc2.h(i)
      if (gameBoard[i][j] == "X"): qc2.x(i)
      if (gameBoard[i][j] == "Y"): qc2.y(i)
      if (gameBoard[i][j] == "Z"): qc2.z(i)
  return [qc1, qc2]

# DRAWING GRID BASE
def drawGrid(surface, boundingRect, color1, color2, cTurn):
  #Draw vertical lines
  #v_s = vert_spacing
  v_s = boundingRect.width/(GRID_SIZE+1)
  if cTurn%2==0: color1, color2 = color2, color1
  for i in range(GRID_SIZE):
    pygame.draw.rect(surface, color2, ((i+1)*v_s + boundingRect.left, boundingRect.top, GRID_THICKNESS, boundingRect.height))
  #Draw horizontal lines
  #h_s = horizontal_spacing
  h_s = boundingRect.height/(GRID_SIZE+1)
  for i in range(GRID_SIZE):
    pygame.draw.rect(surface, color1, (boundingRect.left, (i+1)*h_s + boundingRect.top, boundingRect.width, GRID_THICKNESS))
  #Draw the player 1 triangles
  for i in range(GRID_SIZE):
    pygame.draw.polygon(surface, color1, 
      [[boundingRect.right, (i+1)*v_s + boundingRect.top + GRID_THICKNESS/2],[boundingRect.right-10, (i+1)*v_s+10  + boundingRect.top + GRID_THICKNESS/2],[boundingRect.right-10, (i+1)*v_s-10  + boundingRect.top + GRID_THICKNESS/2]])
  #Draw the player 2 triangles
    pygame.draw.polygon(surface, color2, 
      [[boundingRect.left + (i+1)*v_s + GRID_THICKNESS/2 , boundingRect.bottom],[boundingRect.left + (i+1)*v_s+10 + GRID_THICKNESS/2 , boundingRect.bottom-10],[boundingRect.left + (i+1)*v_s-10 + GRID_THICKNESS/2, boundingRect.bottom-10]])

  # draw q0, q1, q2 on board
  myfont = pygame.font.SysFont('Comic Sans MS', 30)
  textsurface = myfont.render('q0', False, (0, 0, 0))
  surface.blit(textsurface, (v_s + boundingRect.left - 30, boundingRect.top, GRID_THICKNESS, boundingRect.height))
  textsurface = myfont.render('q1', False, (0, 0, 0))
  surface.blit(textsurface, (v_s*2 + boundingRect.left - 30, boundingRect.top, GRID_THICKNESS, boundingRect.height))
  textsurface = myfont.render('q2', False, (0, 0, 0))
  surface.blit(textsurface, (v_s*3 + boundingRect.left - 30, boundingRect.top, GRID_THICKNESS, boundingRect.height))
  textsurface = myfont.render('q0', False, (0, 0, 0))
  surface.blit(textsurface, (boundingRect.left, 1*h_s + boundingRect.top-30, boundingRect.width, GRID_THICKNESS))
  textsurface = myfont.render('q1', False, (0, 0, 0))
  surface.blit(textsurface, (boundingRect.left, (2)*h_s + boundingRect.top-30, boundingRect.width, GRID_THICKNESS))
  textsurface = myfont.render('q2', False, (0, 0, 0))
  surface.blit(textsurface, (boundingRect.left, 3*h_s + boundingRect.top-30, boundingRect.width, GRID_THICKNESS))

def oneShot(qc1, qc2):
  backend = QasmSimulator(method = 'statevector')
  register = np.arange(0, qc1.num_qubits, 1)
  print(register)
  qc1.measure(register, register)
  qc2.measure(register, register)
  result1 = execute(qc1, backend=backend, shots = 1).result()
  count1 = result1.get_counts()
  result2 = execute(qc2, backend=backend, shots = 1).result()
  count2 = result2.get_counts()
  number1 = list(count1.keys())[list(count1.values()).index(1)]
  number2 = list(count2.keys())[list(count1.values()).index(1)]
  return [number1, number2]

# INIT
pygame.init()
SCREEN_X = 640 * 1.5
SCREEN_Y = 480 * 1.5 + 70 + 18
screen = pygame.display.set_mode((SCREEN_X,SCREEN_Y))
pygame.display.set_caption('Quonk')

# GAME LABELS
scoreLabel = "Player {num} score: {score}"
statusLabel = "P1 Measured = {p1} | P2 Measured = {p2} | Target = {t} | Turns left = {tl}"

# GAME VARIABLES
GRID_SIZE = 3
GRID_THICKNESS = 5
score1 = 0
score2 = 0
PURPLE = (148,0,211)
BLACK = (0,0,0)
BACKGROUND_COLOR = (245, 245, 220)

#Odd if player 1, even if player 2
currentTurn = 1
currentGate = "0"
pm1 = -1
pm2 = -1
targetN = targetNumber(GRID_SIZE)
numTurns = 7

# FONT
mainFont = pygame.font.SysFont('Comic Sans MS', 50)
mainFontSmall = pygame.font.SysFont('Comic Sans MS', 37)

# DONT CHANGE ANYTHING!
topRect = pygame.Rect(36, 36, 888, 70)
gridRect = pygame.Rect(36,36 + 70 + 18, 500,500)
buttonsRect = pygame.Rect(36,572 - 18 + 70 + 18, 500, 50)
infoBox1 = pygame.Rect(36+500+36, 36 + 70 + 18, 352, 42)
distRect1 = pygame.Rect(36+500+36, 36+42+10 + 70 + 18, 356, 267)
infoBox2 = pygame.Rect(36+500+36, 36+42+10+267+10 + 70 + 18, 352, 42)
distRect2 = pygame.Rect(36+500+36, 36+42+10+267+10+42+10 + 70 + 18, 356, 267)

# LOAD ASSETS
ASSETS = {}
for i in ["H", "X", "Y", "Z"]:
  ASSETS[i] = pygame.image.load("./assets/" + i + ".png")
  
# INITIALIZE THE BOARD
board = []
for i in range(GRID_SIZE):
  row = []
  for j in range(GRID_SIZE):
    row.append("0")
  board.append(row)

# BUTTONS
button_names = ['H', 'X', 'Y', 'Z', 'rotatecw', 'rotateccw', 'trash']
buttons = []
button_spacing = (buttonsRect.width - len(button_names) * buttonsRect.height) / (len(button_names) - 1)
for i in range(len(button_names)):
  buttons.append(Button(button_names[i], buttonsRect.left + (buttonsRect.height + button_spacing) * i, buttonsRect.top, buttonsRect.height, buttonsRect.height))

calBoard = calculateGraphs(board)

while True:
  # HANDLE EVENTS
  events = pygame.event.get()
  for i in range(len(events)):
    # QUIT EVENT
    if events[i].type == pygame.QUIT:
      pygame.display.quit()
      sys.exit()
    # MOUSEDOWN EVENT
    if events[i].type == pygame.MOUSEBUTTONDOWN:
      button_pressed = False
      for i in range(len(buttons)):
        if buttons[i].mouseOnButton(pygame.mouse.get_pos()):
          button_pressed = True
          print("BUTTON " + buttons[i].name)
          if len(buttons[i].name) == 1:
            currentGate = buttons[i].name
          elif (buttons[i].name == 'rotatecw'):
            board = rotateBoard('cw', board)
            calBoard = calculateGraphs(board)
            currentTurn += 1
            circs = boardsToCircuit(board)
            score1, score2, pm1, pm2 = scoreNumber(circs[0], circs[1], score1, score2, targetN)
          elif (buttons[i].name == 'rotateccw'):
            board = rotateBoard('ccw', board)
            calBoard = calculateGraphs(board)
            currentTurn += 1
            circs = boardsToCircuit(board)
            score1, score2, pm1, pm2 = scoreNumber(circs[0], circs[1], score1, score2, targetN)
          elif (buttons[i].name == 'trash'):
            currentGate = '0'
      if button_pressed:
        continue

      mouseGrid = mouseCoordToGrid(gridRect)
      if (mouseGrid[0] < 0):
        continue

      # Add gate
      board[mouseGrid[0]][mouseGrid[1]] = currentGate
      # New turn
      currentTurn+=1
      # Update distributions
      calBoard = calculateGraphs(board)
      # UPDATE SCORES
      # get circuits
      circs = boardsToCircuit(board)
      score1, score2, pm1, pm2 = scoreNumber(circs[0], circs[1], score1, score2, targetN)


  # Clear the screen
  screen.fill(BACKGROUND_COLOR)

  # Draw the scores
  textColor1 = PURPLE
  textColor2 = BLACK
  if currentTurn%2 == 0: textColor1, textColor2 = textColor2, textColor1
  screen.blit(mainFont.render(scoreLabel.format(num=1, score=score1), True, textColor1), (infoBox1.left, infoBox1.top))
  screen.blit(mainFont.render(scoreLabel.format(num=2, score=score2), True, textColor2), (infoBox2.left, infoBox2.top))

  # Draw the grid
  drawGrid(screen, gridRect, PURPLE, BLACK, currentTurn)

  # Draw probability distributions
  drawGraphs(calBoard, distRect1, distRect2)

  # Draw game status
  screen.blit(mainFontSmall.render(statusLabel.format(p1=pm1, p2=pm2, t=targetN, tl=numTurns-currentTurn), True, PURPLE), (topRect.left, topRect.top))

  # Draw grid elements
  drawGridElements(gridRect)
  pygame.draw.rect(screen, BACKGROUND_COLOR, buttonsRect)

  # Draw button
  drawButtons(buttons)

  # UPDATE THE SCREEN
  pygame.display.update()
  time.sleep(0.01)
