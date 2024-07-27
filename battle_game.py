from math import trunc
import pygame
import sys
from random import choice
from random import randint
import queue


#seed(1)
pygame.init()

ScreenSize = (640, 260)

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
cyan = (0, 255, 255)
red = (255, 0, 0)

cellSize = (20, 20)
fillSize = (18, 18)
y_field = 30
x_field = 10



my_field = [[0 for i in range(11)] for j in range(11)]
enemy_field = [[0 for i in range(11)] for j in range(11)]
my_shoots = [[0 for i in range(11)] for j in range(11)]
enemy_shoots = [[0 for i in range(11)] for j in range(11)]
start_game_button = 0

game_phase = 0
# 0 - arrange ships
# 1 - my fleet ready
# 2 - game started
# 10 - game over

horizontal_queue_left = queue.Queue()
horizontal_queue_right = queue.Queue()
vertical_queue_left = queue.Queue()
vertical_queue_right = queue.Queue()

button_left = 265
button_top = 35
button_height = 40
button_width = 100


real_screen = pygame.display.set_mode(ScreenSize, pygame.RESIZABLE)

screen = real_screen.copy()

pygame.display.set_caption('Battleships')
pygame.font.init() 

screen.fill(white)
sound_miss = pygame.mixer.Sound("sound/miss.wav")
sound_hit = pygame.mixer.Sound("sound/hit.wav")
you_won = pygame.mixer.Sound("sound/you_won.wav")
you_lost = pygame.mixer.Sound("sound/you_lost.wav")

def DrawSquare(x, y, color):
    cell = pygame.Rect((x, y), cellSize)
    fill = pygame.Rect((x + 1, y + 1), fillSize)
    pygame.draw.rect(screen, black, cell)
    pygame.draw.rect(screen, color, fill)

def drawText(text, size, x, y, color):
    myfont = pygame.font.SysFont('Times New Roman', size)
    textsurface = myfont.render(text, True, color)
    screen.blit(textsurface,(x,y))

def DrawCellOnField(Field, l, c, color):
    
    y = y_field + c * 20
    x = x_field + l * 20
    if Field == 1:
        x = x_field + 400 + l * 20

    DrawSquare(x, y, color)

def drawGameField():
    pygame.mixer.music.load('sound/bgmusic_placing.wav')
    pygame.mixer.music.play(-1)
    for c in range(11):
        for l in range(11):
            DrawCellOnField(0, l, c, white)
        if c > 0:
            drawText(str(c), 10, x_field + 7 + c * 20, y_field + 2, black)
            drawText(chr(c + 64), 10, x_field + 7, y_field + 2 + c * 20, black)

    for c in range(11):
        for l in range(11):
            DrawCellOnField(1, l, c, white)
        if c > 0:
            drawText(str(c), 10, x_field + 407 + c * 20, y_field + 2, black)
            drawText(chr(c + 64), 10, x_field + 407, y_field + 2 + c * 20, black)


    drawText("My ships",16, y_field, 0, black)
    drawText("Enemy ships",16, y_field + 400, 0, black)

def clearFields():
    for c in range(1, 11):
        for l in range(1, 11):
            my_field[l][c] = 0
            enemy_field[l][c] = 0
            my_shoots[l][c] = 0
            enemy_shoots[l][c] = 0
    screen.fill(white)
    drawGameField()

def drawStartGameButton():
    global start_game_button
    if start_game_button == 1:
        return
    button_back = pygame.Rect((button_left, button_top), (button_width, button_height))
    pygame.draw.rect(screen, black, button_back)
    drawText("Start game",14, button_left + 20, button_top + 10, white)
    start_game_button = 1

def eraseStartGameButton(force):
    global start_game_button
    if start_game_button == 0 and not force:
        return
    button_back = pygame.Rect((265, 287), (100, 40))
    pygame.draw.rect(screen, white, button_back)
    start_game_button = 0

def checkDiagonals(field, y, x, visited, straight):
    if straight == True:
        if x > 1 and field[y][x - 1] == 1:
            return False
        elif x < 10 and field[y][x + 1] == 1:
            return False
        elif y > 1 and field[y - 1][x] == 1:
            return False
        elif y < 10 and field[y + 1][x] == 1:
            return False

    if x > 1: #check left diagonals
        if y > 0: # check top-left
            if field[y - 1][x - 1] == 1:
                return False
            else:
                visited[y - 1][x - 1] = 1
        if y < 10: # test bottom-left
            if field[y + 1][x - 1] == 1:
                return False
            else:
                visited[y + 1][x - 1] = 1
    if x < 10:
        if y > 0: # check top-right
            if field[y - 1][x + 1] == 1:
                return False
            else:
                visited[y - 1][x + 1] = 1
        if y < 10: # test bottom-right
            if field[y + 1][x + 1] == 1:
                return False
            else:
                visited[y + 1][x + 1] = 1
    return True

def testMyShip(y, x, visited, ships):
    if checkDiagonals(my_field, y, x, visited, False) == False:
        return False
    ship_length = 1
    current_x = x
    while current_x > 0:
        current_x -= 1
        if my_field[y][current_x] == 1:
            if checkDiagonals(my_field, y, current_x, visited, False) == False:
                return False
            visited[y][current_x] = 1
            ship_length += 1
        else:
            break
    current_x = x
    while current_x < 10:
        current_x += 1
        if my_field[y][current_x] == 1:
            if checkDiagonals(my_field, y, current_x, visited, False) == False:
                return False
            visited[y][current_x] = 1
            ship_length += 1
        else:
            break
    if ship_length == 1:
        current_y = y
        while current_y > 0:
            current_y -= 1
            if my_field[current_y][x] == 1:
                if checkDiagonals(my_field, current_y, x, visited, False) == False:
                    return False
                visited[current_y][x] = 1
                ship_length += 1
            else:
                break
        current_y = y
        while current_y < 10:
            current_y += 1
            if my_field[current_y][x] == 1:
                if checkDiagonals(my_field, current_y, x, visited, False) == False:
                    return False
                visited[current_y][x] = 1
                ship_length += 1
            else:
                break
    if ship_length >= len(ships):
        return False
    ships[ship_length] += 1
    return True

def validateMyField():
    visited = [[0 for i in range(12)] for j in range(12)]
    ships = [0 for _ in range(6)]
    for i in range(11): # y
        for j in range(11): # x
            if visited[i][j] == 1:
                continue
            visited[i][j] = 1
            if my_field[i][j] == 1:
                if testMyShip(i, j, visited, ships) == False:
                    return False
    if ships[5] == 1 and ships[4] == 1 and ships[3] == 1 and ships[2] == 2 and ships[1] == 2:
        return True
    return False

def tryPutShip(ship_length, direction, max_x, max_y):
    x = randint(1, max_x)
    y = randint(1, max_y)
    visited = [[0 for i in range(11)] for j in range(11)]
    if direction == False:
        for current_x in range(x, x + ship_length):
            if enemy_field[y][current_x] != 0 or checkDiagonals(enemy_field, y, current_x, visited, True) == False:
                return False
    else:
        for current_y in range(y, y + ship_length):
            if enemy_field[current_y][x] != 0  or checkDiagonals(enemy_field, current_y, x, visited, True) == False:
                return False
    if direction == False:
        for current_x in range(x, x + ship_length):
            enemy_field[y][current_x] = 1
            #DrawCellOnField(1, current_x, y, red)
    else:
        for current_y in range(y, y + ship_length):
            enemy_field[current_y][x] = 1
            #DrawCellOnField(1, x, current_y, red)
    return True
    
def placeEnemyShips():
    ships = [ (5, 1), (4, 1), (3, 1), (2, 2), (1,2)]
    for ship in ships:
        direction = choice([False, True]) # true = vertical
        (ship_length, ships_count) = ship
        max_x = 10 - ship_length if not direction else 10
        max_y = 10 - ship_length if direction else 10
        while ships_count > 0:
            if tryPutShip(ship_length, direction, max_x, max_y):
                ships_count -= 1

def drawSample():
    global my_field, game_phase
    my_field = [
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0,1,1],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,0,1,1],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,1,0,0,1,1,1],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,1,1,1,1],
        [0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,1,1,1,1,1],
    ]
    for y in range(0, 11):
        for x in range(0, 11):
            if my_field[y][x] == 1:
                DrawCellOnField(0, x, y, green)
    drawStartGameButton()
    game_phase = 1

def checkGameOver():
    i_have_ships = False
    enemy_has_ships = False
    for i in range(11): # y
        for j in range(11): # x
            if my_field[i][j] == 1:
                i_have_ships = True
            if enemy_field[i][j] == 1:
                enemy_has_ships = True
    global game_phase
    if i_have_ships == False:
        drawText("You lost!", 18, button_left + 20, button_top + 60, red)
        pygame.mixer.music.stop()
        you_lost.play()
        for i in range(11):
            for j in range(11):
                if enemy_field[i][j] == 1 and my_shoots[i][j] == 0:
                    DrawCellOnField(1, j, i, blue)

        game_phase = 3
    if enemy_has_ships == False:
        drawText("You Won!", 18, button_left + 20, button_top + 60, blue)
        pygame.mixer.music.stop()
        you_won.play()

        game_phase = 3

def computerMove():
    shoot = False
    global vertical_queue_left, vertical_queue_right, horizontal_queue_left, horizontal_queue_right
    while shoot == False:
        shoot_x = randint(1, 10)
        shoot_y = randint(1, 10)
        priotiry = False
        if horizontal_queue_left.qsize() > 0:
            priotiry = True
            (shoot_x, shoot_y) = horizontal_queue_left.get()
            if my_field[shoot_y][shoot_x] == 1:
                vertical_queue_left = queue.Queue()
                vertical_queue_right = queue.Queue()
            else:
                horizontal_queue_left = queue.Queue()
        elif horizontal_queue_right.qsize() > 0:
            priotiry = True
            (shoot_x, shoot_y) = horizontal_queue_right.get()
            if my_field[shoot_y][shoot_x] == 1:
                vertical_queue_left = queue.Queue()
                vertical_queue_right = queue.Queue()
            else:
                horizontal_queue_right = queue.Queue()
        elif vertical_queue_left.qsize() > 0:
            priotiry = True
            (shoot_x, shoot_y) = vertical_queue_left.get()
            if my_field[shoot_y][shoot_x] == 1:
                horizontal_queue_left = queue.Queue()
                horizontal_queue_right = queue.Queue()
            else:
                vertical_queue_left = queue.Queue()
        elif vertical_queue_right.qsize() > 0:
            priotiry = True
            (shoot_x, shoot_y) = vertical_queue_right.get()
            if my_field[shoot_y][shoot_x] == 1:
                horizontal_queue_left = queue.Queue()
                horizontal_queue_right = queue.Queue()
            else:
                vertical_queue_right = queue.Queue()

        if enemy_shoots[shoot_y][shoot_x] == 0:
            enemy_shoots[shoot_y][shoot_x] = 1
            shoot = True
            if my_field[shoot_y][shoot_x] == 0:
                DrawCellOnField(0, shoot_x, shoot_y, cyan)
            else:
                DrawCellOnField(0, shoot_x, shoot_y, red)
                my_field[shoot_y][shoot_x] = 0
                enemy_shoots[shoot_y][shoot_x] = 1
                if not priotiry:
                    if shoot_x > 1:
                        for x in range(shoot_x - 1, 0, -1):
                            horizontal_queue_left.put((x, shoot_y))
                    if shoot_x < 10:
                        for x in range(shoot_x + 1, 11):
                            horizontal_queue_right.put((x, shoot_y))
                    if shoot_y > 1:
                        for y in range(shoot_y - 1, 0, -1):
                            vertical_queue_left.put((shoot_x, y))
                    if shoot_y < 10:
                        for y in range(shoot_y + 1, 11):
                            vertical_queue_right.put((shoot_x, y))

                diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
                for deviation in diagonals:
                    (deviation_x, deviation_y) = deviation
                    diagonal_x = shoot_x + deviation_x
                    diagonal_y = shoot_y + deviation_y
                    if diagonal_x > 0 and diagonal_x < 11 and diagonal_y > 0 and diagonal_y < 11:
                        enemy_shoots[diagonal_y][diagonal_x] = 1

def handleMouseClick(x, y):
    global game_phase
    print("x: " + str(x) + " y: " + str(y))
    if x >= 10 and x <= 230 and y >= 30 and y <= 250:
        if game_phase == 0 or game_phase == 1:
            #my field
            cell_x = int((x - 10) / 20)
            cell_y = int((y - 30) / 20)
            if (cell_x < 1 or cell_x > 10 or cell_y < 1 or cell_y > 10):
                return
            sound_miss.play()
            if my_field[cell_y][cell_x] == 1:
                my_field[cell_y][cell_x] = 0
                DrawCellOnField(0, cell_x, cell_y, white)
            else:
                my_field[cell_y][cell_x] = 1
                DrawCellOnField(0, cell_x, cell_y, green)
            if validateMyField() == True:
                drawStartGameButton()
                game_phase = 1
            else:
                eraseStartGameButton(False)
                game_phase = 0
    elif x >= 410 and x <= 630 and y >= 30 and y <= 250:
        #enemy field
        if game_phase == 2:
            cell_x = int((x - 410) / 20)
            cell_y = int((y - 30) / 20)
            if (cell_x < 1 or cell_x > 10 or cell_y < 1 or cell_y > 10):
                return
            if my_shoots[cell_y][cell_x] != 1:
                if enemy_field[cell_y][cell_x] == 0:
                    sound_miss.play()
                    DrawCellOnField(1, cell_x, cell_y, cyan)
                else:
                    DrawCellOnField(1, cell_x, cell_y, red)
                    enemy_field[cell_y][cell_x] = 0
                    sound_hit.play()
                    my_shoots[cell_y][cell_x] = 1
                computerMove()
                checkGameOver()

    elif x >= button_left and x <= button_left + button_width and y >= button_top and y <= button_top + button_height:
        # start game button
        if game_phase == 1:
            button_back = pygame.Rect((button_left, button_top), (button_width, button_height))
            pygame.draw.rect(screen, blue, button_back)
            drawText("Stop game",14, button_left + 20, button_top + 10, white)
            game_phase = 2
            global start_game_button
            start_game_button = 0
            placeEnemyShips()
            pygame.mixer.music.stop()
            pygame.mixer.music.load('sound/bgmusic_game.wav')
            pygame.mixer.music.play(-1)

        elif game_phase == 2 or game_phase == 3:
            clearFields()
            game_phase = 0

drawGameField()



#drawSample()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            original_x, original_y = event.pos
            x = trunc(original_x * ScreenSize[0] / real_screen.get_rect().size[0])
            y = trunc(original_y * ScreenSize[1] / real_screen.get_rect().size[1])
            handleMouseClick(x, y)
    real_screen.blit(pygame.transform.scale(screen, real_screen.get_rect().size), (0, 0))
    pygame.display.update()
