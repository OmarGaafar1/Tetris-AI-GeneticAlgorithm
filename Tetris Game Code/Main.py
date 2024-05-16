import tkinter as tk
import random, time, pygame, sys
from pygame.locals import *
import copy
from PIL import Image, ImageTk

##############################################################################
# SETTING UP GENERAL CONSTANTS
##############################################################################
random.seed(42)

# Board config
FPS          = 30
WINDOWWIDTH  = 650
WINDOWHEIGHT = 690
BOXSIZE      = 25
BOARDWIDTH   = 10
BOARDHEIGHT  = 25
BLANK        = '.'
XMARGIN      = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN    = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

# Timing config
# Every time the player pushes the left or right arrow key down, the falling
# piece should move one box over to the left or right, respectively. However,
# the player can also hold down the left or right arrow key to keep moving the
# falling piece. The MOVESIDEWAYSFREQ constant will set it so that every 0.15
# seconds that passes with the left or right arrow key held down, the piece
# will move another space over.
MOVESIDEWAYSFREQ = 0.15
MOVEDOWNFREQ     = 0.1

# Colors
#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR     = BLUE
BGCOLOR         = BLACK
TEXTCOLOR       = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS          = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS     = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)

# Each color must have light color
assert len(COLORS) == len(LIGHTCOLORS)

# Piece Templates
# The TEMPLATEWIDTH and TEMPLATEHEIGHT constants simply set how large each row
# and column for each shape’s rotation should be
TEMPLATEWIDTH  = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {
        'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE
          }


# Genetic Algorithm Configs
EVOLUTIONS_NUMBER = 10
MUTATION_RATE = 0.1
SELECTION_RATE = 0.5
POPULATION_SIZE = 12
CHROMOSOME_LENGTH = 7


# Define if the game is manual or not
MANUAL_GAME = False

##############################################################################
# MAIN GAME
##############################################################################

def display_menu():
    root = tk.Tk()
    root.title("Tetris AI Menu")

    # Set fixed window size
    root.geometry("860x860")

    # Prevent window resizing
    root.resizable(False, False)

    # Load background GIF
    bg_image = Image.open("tetris full hd.jpg")
    bg_photo = ImageTk.PhotoImage(bg_image)
    background_label = tk.Label(root, image=bg_photo)
    background_label.image = bg_photo
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # Welcome message
    welcome_label = tk.Label(root, text="Welcome to FCAI Tetris Game!", font=("Helvetica", 24, "bold"))
    welcome_label.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

    def start_game(selection):
        root.destroy()
        if selection == 1:
            RunTetrisNormally()
        elif selection == 2:
            RunTetrisGeneticAlgorithm()
        elif selection == 3:
            RunTetrisBeastMode()

    def on_button_click(selection):
        start_game(selection)

    menu_options = [
        "Play Tetris Normally",
        "Start The Genetic Algorithm",
        "Start Testing (Beast Mode)"
    ]

    for i in range(3):
        button = tk.Button(root, text=menu_options[i], command=lambda selection=i + 1: on_button_click(selection),
                           bd=3, relief=tk.RAISED, font=("Helvetica", 12, "bold"))
        button.place(relx=0.5, rely=0.3 + i * 0.1, anchor=tk.CENTER)

    root.mainloop()
##############################################################################
# GAME FUNCTIONS
##############################################################################

def make_text_objs(text, font, color):
    surf = font.render(text, True, color)

    return surf, surf.get_rect()


def terminate():
    """Terminate the game"""
    pygame.quit()
    sys.exit()


def check_key_press():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    check_quit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def show_text_screen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.

    # Draw the text drop shadow
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTSHADOWCOLOR)
    title_rect.center      = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the text
    title_surf, title_rect = make_text_objs(text, BIGFONT, TEXTCOLOR)
    title_rect.center      = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(title_surf, title_rect)

    # Draw the additional "Press a key to play." text.
    press_key_surf, press_key_rect = make_text_objs('Press a key to play.', BASICFONT, TEXTCOLOR)
    press_key_rect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(press_key_surf, press_key_rect)

    while check_key_press() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def check_quit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present

    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calc_level_and_fall_freq(score):
    """ Calculate level and fall frequency
        Based on the score, return the level the player is on and
        how many seconds pass until a falling piece falls one space.

    Args:
        score: game score

    """
    level     = int(score / 400) + 1
    fall_freq = 0.27 - (level * 0.02)

    if (not MANUAL_GAME):
        fall_freq = 0.00

    return level, fall_freq+1


def get_new_piece():
    """Return a random new piece in a random rotation and color"""

    shape= random.choice(list(PIECES.keys()))

    new_piece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}

    return new_piece


def add_to_board(board, piece):
    """Fill in the board based on piece's location, shape, and rotation"""

    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']


def get_blank_board():
    """Create and return a new blank board data structure"""

    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)

    return board


def is_on_board(x, y):
    """Check if the piece is on the board"""

    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def is_valid_position(board, piece, adj_X=0, adj_Y=0):
    """Return True if the piece is within the board and not colliding"""
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            is_above_board = y + piece['y'] + adj_Y < 0
            if is_above_board or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue

            if not is_on_board(x + piece['x'] + adj_X, y + piece['y'] + adj_Y):
                return False

            if board[x + piece['x'] + adj_X][y + piece['y'] + adj_Y] != BLANK:
                return False

    return True


def is_complete_line(board, y):
    """Return True if the line filled with boxes with no gaps"""

    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False

    return True


def remove_complete_lines(board):
    """Remove any completed lines on the board.

    After remove any completed lines, move everything above them dowm and
    return the number of complete lines.

    """
    num_removed_lines = 0
    y = BOARDHEIGHT - 1     # Start y at the bottom of the board

    while y >= 0:
        if is_complete_line(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY-1]

            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK

            num_removed_lines += 1

            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # Move on to check next row up

    return num_removed_lines


def conv_to_pixels_coords(boxx, boxy):
    """Convert the given xy coordinates to the screen coordinates

    Convert the given xy coordinates of the board to xy coordinates of the
    location on the screen.

    """
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def draw_box(boxx, boxy, color, pixelx=None, pixely=None):
    """Draw box

    Draw a single box (each tetromino piece has four boxes) at xy coordinates
    on the board. Or, if pixelx and pixely are specified, draw to the pixel
    coordinates stored in pixelx and pixely (this is used for the "Next" piece).

    """
    if color == BLANK:
        return

    if pixelx == None and pixely == None:
        pixelx, pixely = conv_to_pixels_coords(boxx, boxy)

    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def draw_board(board):
    """Draw board"""

    # Draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # Fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))

    # Draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            draw_box(x, y, board[x][y])


def draw_statusForNormal(score, level):
    """Draw status"""

    # Draw the score text
    score_surf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 80)
    DISPLAYSURF.blit(score_surf, score_rect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 110)
    DISPLAYSURF.blit(levelSurf, levelRect)

def draw_statusGeneticMode(score, level, total_lines_removed, currnet_evolution_number, current_chromosome_number, moves_taken,
                           current_chromosome):
    """Draw status"""
    # Draw the score text
    score_surf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(score_surf, score_rect)

    lines_surf = BASICFONT.render('Lines: %s' % total_lines_removed, True, TEXTCOLOR)
    lines_rect = lines_surf.get_rect()
    lines_rect.topleft = (WINDOWWIDTH - 150, 140)
    DISPLAYSURF.blit(lines_surf, lines_rect)
    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 110)
    DISPLAYSURF.blit(levelSurf, levelRect)

    EvolSurf = BASICFONT.render(f' Evolution: %s / {EVOLUTIONS_NUMBER}'  % currnet_evolution_number, True, TEXTCOLOR)
    EvolRect = EvolSurf.get_rect()
    EvolRect.topleft = (WINDOWWIDTH - 650, 110)
    DISPLAYSURF.blit(EvolSurf, EvolRect)

    ChromSurf = BASICFONT.render(f' Chromosome: %s /{POPULATION_SIZE}' % current_chromosome_number,   True, TEXTCOLOR)
    ChromRect = ChromSurf.get_rect()
    ChromRect.topleft = (WINDOWWIDTH - 650, 80)
    DISPLAYSURF.blit(ChromSurf, ChromRect)


    SMALL_FONT_SIZE = 16
    SMALL_FONT = pygame.font.Font('freesansbold.ttf', SMALL_FONT_SIZE)

    CurrentChromoSurf = SMALL_FONT.render(f'Current Chromo: {current_chromosome}', True, TEXTCOLOR)
    CurrentChromoRect = CurrentChromoSurf.get_rect()
    CurrentChromoRect.topleft = (WINDOWWIDTH - 650, 30)
    DISPLAYSURF.blit(CurrentChromoSurf, CurrentChromoRect)

    MovesTakenSurf = BASICFONT.render(f'Moves: %s ' %moves_taken, True, TEXTCOLOR)
    MovesTakenRect = MovesTakenSurf.get_rect()
    MovesTakenRect.topleft = (WINDOWWIDTH - 150, 80)
    DISPLAYSURF.blit(MovesTakenSurf, MovesTakenRect)

def draw_statusBeastMode(score, level, total_lines_removed,moves_taken,current_chromosome):
    """Draw status"""
    # Draw the score text
    score_surf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    score_rect = score_surf.get_rect()
    score_rect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(score_surf, score_rect)

    lines_surf = BASICFONT.render('Lines: %s' % total_lines_removed, True, TEXTCOLOR)
    lines_rect = lines_surf.get_rect()
    lines_rect.topleft = (WINDOWWIDTH - 150, 140)
    DISPLAYSURF.blit(lines_surf, lines_rect)
    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 110)
    DISPLAYSURF.blit(levelSurf, levelRect)

    SMALL_FONT_SIZE = 16
    SMALL_FONT = pygame.font.Font('freesansbold.ttf', SMALL_FONT_SIZE)

    CurrentChromoSurf = SMALL_FONT.render(f'Testing Chromo: {current_chromosome}', True, TEXTCOLOR)
    CurrentChromoRect = CurrentChromoSurf.get_rect()
    CurrentChromoRect.topleft = (WINDOWWIDTH - 650, 30)
    DISPLAYSURF.blit(CurrentChromoSurf, CurrentChromoRect)

    MovesTakenSurf = BASICFONT.render(f'Moves: %s ' % moves_taken, True, TEXTCOLOR)
    MovesTakenRect = MovesTakenSurf.get_rect()
    MovesTakenRect.topleft = (WINDOWWIDTH - 150, 80)
    DISPLAYSURF.blit(MovesTakenSurf, MovesTakenRect)


def draw_piece(piece, pixelx=None, pixely=None):
    """Draw piece"""

    shape_to_draw = PIECES[piece['shape']][piece['rotation']]

    if pixelx == None and pixely == None:
        # If pixelx and pixely hasn't been specified, use the location stored
        # in the piece data structure
        pixelx, pixely = conv_to_pixels_coords(piece['x'], piece['y'])

    # Draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shape_to_draw[y][x] != BLANK:
                draw_box(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def draw_next_piece(piece):
    """Draw next piece"""

    # draw the "next" text
    next_surf = BASICFONT.render('Next:', True, TEXTCOLOR)
    next_rect = next_surf.get_rect()
    next_rect.topleft = (WINDOWWIDTH - 150, 160)
    DISPLAYSURF.blit(next_surf, next_rect)

    # draw the "next" piece
    draw_piece(piece, pixelx=WINDOWWIDTH-150, pixely=160)


##############################################################################
# GAME STATISTICS FUNCTIONS
##############################################################################

def calc_move_info(board, piece, x, r, total_holes_bef, total_blocking_bloks_bef):
    """Calculate informations based on the current play"""

    piece['rotation'] = r
    piece['y']        = 0
    piece['x']        = x

    # Check if it's a valid position
    if (not is_valid_position(board, piece)):
        return [False]

    # Goes down the piece while it's a valid position
    while is_valid_position(board, piece, adj_X=0, adj_Y=1):
        piece['y']+=1

    # Create a hypothetical board
    new_board = get_blank_board()
    for x2 in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            new_board[x2][y] = board[x2][y]

    # Add the piece to the new_board
    add_to_board(new_board, piece)

    # Calculate the sides in contact
    piece_sides, floor_sides, wall_sides = calc_sides_in_contact(board, piece)

    # Calculate removed lines
    num_removed_lines = remove_complete_lines(new_board)

    total_blocking_block = 0
    total_holes          = 0
    max_height           = 0

    for x2 in range(0, BOARDWIDTH):
        b = calc_heuristics(new_board, x2)
        total_holes += b[0]
        total_blocking_block += b[1]
        max_height += b[2]

    new_holes           = total_holes - total_holes_bef
    new_blocking_blocks = total_blocking_block - total_blocking_bloks_bef

    return [True, max_height, num_removed_lines, new_holes, new_blocking_blocks, piece_sides, floor_sides, wall_sides]

def calc_initial_move_info(board):
    total_holes          = 0
    total_blocking_bocks = 0

    for x2 in range(0, BOARDWIDTH):
        b = calc_heuristics(board, x2)

        total_holes          += b[0]
        total_blocking_bocks += b[1]

    return total_holes, total_blocking_bocks

def calc_heuristics(board, x):
    """Calculate heuristics

    The heuristics are composed by: number of holes, number of blocks above
    hole and maximum height.

    """
    total_holes        = 0
    locals_holes       = 0
    blocks_above_holes = 0
    is_hole_exist      = False
    sum_heights        = 0

    for y in range(BOARDHEIGHT-1, -1,-1):
        if board[x][y] == BLANK:
            locals_holes += 1
        else:
            sum_heights += BOARDHEIGHT-y

            if locals_holes > 0:
                total_holes += locals_holes
                locals_holes = 0

            if total_holes > 0:
                blocks_above_holes += 1

    return total_holes, blocks_above_holes, sum_heights

def calc_sides_in_contact(board, piece):
    """Calculate sides in contacts"""

    piece_sides = 0
    floor_sides = 0
    wall_sides  = 0

    for Px in range(TEMPLATEWIDTH):
        for Py in range(TEMPLATEHEIGHT):

            # Wall
            if not PIECES[piece['shape']][piece['rotation']][Py][Px] == BLANK: # Quadrante faz parte da peça
                if piece['x']+Px == 0 or piece['x']+Px == BOARDWIDTH-1:
                    wall_sides += 1

                if piece['y']+Py == BOARDHEIGHT-1:
                    floor_sides += 1
                else:
                # Para outras opecas no contorno do template:
                    if Py == TEMPLATEHEIGHT-1 and not board[piece['x']+Px][piece['y']+Py+1] == BLANK:
                        piece_sides += 1

                #os extremos do template sao colorido: confere se ha pecas do lado deles
                if Px == 0 and piece['x']+Px > 0 and not board[piece['x']+Px-1][piece['y']+Py] == BLANK:
                        piece_sides += 1

                if Px == TEMPLATEWIDTH-1 and piece['x']+Px < BOARDWIDTH -1 and not board[piece['x']+Px+1][piece['y']+Py] == BLANK:
                        piece_sides += 1

            # Other pieces in general
            elif piece['x']+Px < BOARDWIDTH and piece['x']+Px >= 0 and piece['y']+Py < BOARDHEIGHT and not board[piece['x']+Px][piece['y']+Py] == BLANK:  #quadrante do tabuleiro colorido mas nao do template

                # O quadrante vazio do template esta colorido no tabuleiro
                if not PIECES[piece['shape']][piece['rotation']][Py-1][Px] == BLANK:
                    piece_sides += 1

                if Px > 0 and not PIECES[piece['shape']][piece['rotation']][Py][Px-1] == BLANK:
                    piece_sides += 1

                if Px < TEMPLATEWIDTH-1 and not PIECES[piece['shape']][piece['rotation']][Py][Px+1] == BLANK:
                    piece_sides += 1

                    #(nao pode haver pecas em cima)

    return  piece_sides, floor_sides, wall_sides


##############################################################################
# GENETIC ALGORITHM
##############################################################################

def GenerateAllPossibleMovesWithScores(board , piece, current_chromosome):
    moves = []
    for rotation in range(0 , len(PIECES[piece['shape']])):
        for x in range(-2 , 8):
            MoveInfo = calc_move_info(board , piece , x , rotation , 0 , 0)
            isValidMove = MoveInfo[0]
            if not isValidMove:
                continue
            move_score = CalculateFitnessScore(MoveInfo , current_chromosome)
            moves.append((rotation, x, move_score))
    return moves


def chooseBestMove(moves):
    moves.sort(key=lambda move: move[2] , reverse=True)
    return moves[0]


def Initalize_population():
    population = []
    chromosome_size = 7
    for i in range(0, POPULATION_SIZE):
        chromosome =[]
        for j in range(0, chromosome_size):
            chromosome.append(random.randint(-10,10))
        population.append(chromosome)
    return population

def CalculateFitnessScore(MoveInfo , CurrentChromosome):
    score = 0
    for Feature , Value in zip(MoveInfo[1:],CurrentChromosome):
        score += Feature * Value
    return score

def choose_Best_Chromosomes(population , ChoosingRate = 0.5 ):
    chromosomes_To_select = int(len(population) * ChoosingRate)
    population.sort(key = lambda chromosomeWithScore:chromosomeWithScore[1] , reverse=True)
    return population[:chromosomes_To_select]


def cross_over(bestChromosomes):
    offsprings = []
    for i in range(0, len(bestChromosomes)):
        parent1 = random.choice(bestChromosomes)
        parent2 = random.choice(bestChromosomes)
        crossover_point = random.randint(1, CHROMOSOME_LENGTH - 1)
        child = parent1[:crossover_point] + parent2[crossover_point:]
        offsprings.append(child)
    return offsprings

def Mutation(offSprings):
    mutated_offspring = []
    for chromosomes in offSprings:
        for i in range(len(chromosomes)):
            if random.random() < MUTATION_RATE:
                chromosomes[i] = chromosomes[i] / 2 + random.random()  +random.randint(-2,5)
        mutated_offspring.append(chromosomes)
    return mutated_offspring


def drop_score(Chromosoems_with_scores):
    Chromosomes_Without_Scores =[]
    for Chromosome in Chromosoems_with_scores:
        Chromosomes_Without_Scores.append(Chromosome[0])
    return Chromosomes_Without_Scores


##############################################################################
# Normal Tetris Function
##############################################################################


def RunTetrisNormally():
    # Setup variables
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetris Genetic Algorithm')
    board= get_blank_board()
    last_movedown_time = time.time()
    last_moveside_time = time.time()
    last_fall_time     = time.time()
    moving_down        = False # note: there is no movingUp variable
    moving_left        = False
    moving_right       = False
    score              = 0
    level, fall_freq   = calc_level_and_fall_freq(score)

    falling_piece      = get_new_piece()
    next_piece         = get_new_piece()

    while True:
        # Game Loop
        if (falling_piece == None):
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece    = get_new_piece()
            score += 1

            # Reset last_fall_time
            last_fall_time = time.time()

            if (not is_valid_position(board, falling_piece)):
                # GAME-OVER
                # Can't fit a new piece on the board, so game over.
                return

        # Check for quit
        check_quit()

        for event in pygame.event.get():
            # Event handling loop
            if (event.type == KEYUP):
                if (event.key == K_p):
                    # PAUSE the game
                    DISPLAYSURF.fill(BGCOLOR)
                    # Pause until a key press
                    show_text_screen('Paused')

                    # Update times
                    last_fall_time     = time.time()
                    last_movedown_time = time.time()
                    last_moveside_time = time.time()

                elif (event.key == K_LEFT or event.key == K_a):
                    moving_left = False
                elif (event.key == K_RIGHT or event.key == K_d):
                    moving_right = False
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = False

            elif event.type == KEYDOWN:
                # Moving the piece sideways
                if (event.key == K_LEFT or event.key == K_a) and \
                    is_valid_position(board, falling_piece, adj_X=-1):

                    falling_piece['x'] -= 1
                    moving_left         = True
                    moving_right        = False
                    last_moveside_time  = time.time()

                elif (event.key == K_RIGHT or event.key == K_d) and \
                    is_valid_position(board, falling_piece, adj_X=1):

                    falling_piece['x'] += 1
                    moving_right        = True
                    moving_left         = False
                    last_moveside_time  = time.time()

                # Rotating the piece (if there is room to rotate)
                elif (event.key == K_UP or event.key == K_w):
                    falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])

                    if (not is_valid_position(board, falling_piece)):
                        falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(PIECES[falling_piece['shape']])

                elif (event.key == K_q):
                    falling_piece['rotation'] = (falling_piece['rotation'] - 1) % len(PIECES[falling_piece['shape']])

                    if (not is_valid_position(board, falling_piece)):
                        falling_piece['rotation'] = (falling_piece['rotation'] + 1) % len(PIECES[falling_piece['shape']])

                # Making the piece fall faster with the down key
                elif (event.key == K_DOWN or event.key == K_s):
                    moving_down = True

                    if (is_valid_position(board, falling_piece, adj_Y=1)):
                        falling_piece['y'] += 1

                    last_movedown_time = time.time()

                # Move the current piece all the way down
                elif event.key == K_SPACE:
                    moving_down  = False
                    moving_left  = False
                    moving_right = False

                    for i in range(1, BOARDHEIGHT):
                        if (not is_valid_position(board, falling_piece, adj_Y=i)):
                            break

                    falling_piece['y'] += i - 1

        # Handle moving the piece because of user input
        if (moving_left or moving_right) and time.time() - last_moveside_time > MOVESIDEWAYSFREQ:
            if moving_left and is_valid_position(board, falling_piece, adj_X=-1):
                falling_piece['x'] -= 1
            elif moving_right and is_valid_position(board, falling_piece, adj_X=1):
                falling_piece['x'] += 1

            last_moveside_time = time.time()

        if moving_down and time.time() - last_movedown_time > MOVEDOWNFREQ and is_valid_position(board, falling_piece, adj_Y=1):
            falling_piece['y'] += 1
            last_movedown_time = time.time()

        # Let the piece fall if it is time to fall
        if time.time() - last_fall_time > fall_freq:
            # See if the piece has landed
            if (not is_valid_position(board, falling_piece, adj_Y=1)):
                # Falling piece has landed, set it on the board
                add_to_board(board, falling_piece)
                num_removed_lines = remove_complete_lines(board)
                # Bonus score for complete lines at once
                # 40   pts for 1 line
                # 120  pts for 2 lines
                # 300  pts for 3 lines
                # 1200 pts for 4 lines

                if(num_removed_lines == 1):
                    score += 40
                elif (num_removed_lines == 2):
                    score += 120
                elif (num_removed_lines == 3):
                    score += 300
                elif (num_removed_lines == 4):
                    score += 1200

                level, fall_freq = calc_level_and_fall_freq(score)
                falling_piece    = None

            else:
                # Piece did not land, just move the piece down
                falling_piece['y'] += 1
                last_fall_time      = time.time()

        # Drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_statusForNormal(score, level)
        draw_next_piece(next_piece)

        if falling_piece != None:
            draw_piece(falling_piece)
        pygame.display.update()
        FPSCLOCK.tick(FPS)


##############################################################################
# Generic Algorithm Tetris Functions
##############################################################################


def RunTetrisGeneticAlgorithm():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK    = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT   = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT     = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetris AI')
    f = open("scores.txt" , "a")
    f.write("************************************************************************************************\n")
    population = Initalize_population()
    population[0] =      [-1.42 , 7 ,-8 , -2.41 , 8,6,8]

    for Evolution in range(0, EVOLUTIONS_NUMBER):
        f.write(f"\t\t\t\t\t Evolution # {Evolution}\n")
        for i in range(0 , len(population)):
            current_chromosome = population[i]
            score, moves_taken , linesRemoved = run_game_return_score(current_chromosome ,Evolution , i)
            f.write(f"Chromosome {current_chromosome}\n\tscored: {score}\n\t Moves:{moves_taken}\n\t LinesRemoved:{linesRemoved}\n")
            population[i] = [current_chromosome, score]
        # With Score means each array consisnt of [chromosome , Score] for filteration purposes
        best_chromosomes_With_Scores = choose_Best_Chromosomes(population, SELECTION_RATE)
        best_chromosome = drop_score(best_chromosomes_With_Scores)
        offSprings = cross_over(best_chromosome)
        mutated_offsprings = Mutation(offSprings)
        population = best_chromosome + mutated_offsprings


    f.close()


def run_game_return_score(current_chromosome , currnet_evolution_number , current_chromosome_number):
    # Setup variables
    board = get_blank_board()
    score = 0
    total_lines_removed = 0
    falling_piece = get_new_piece()
    next_piece = get_new_piece()
    moves_taken = 0
    while True:
        # Game Loop
        if (falling_piece == None):
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()
            score += 1
            if (not is_valid_position(board, falling_piece)):
                # GAME-OVER
                # Can't fit a new piece on the board, so game over.
                print(f"Score is now {score}")
                return score, moves_taken, total_lines_removed
        # Check for quit
        check_quit()
        moves = GenerateAllPossibleMovesWithScores(board , falling_piece , current_chromosome)
        if(len(moves) == 0):# IF there is no moves availabe to  play
            print(f"Score is now {score}")
            return score ,moves_taken , total_lines_removed
        bestMove  = chooseBestMove(moves)
        rotation = bestMove[0]
        x = bestMove[1]
        falling_piece["x"] = x
        falling_piece["y"] = -1
        falling_piece['rotation'] = rotation

        for i in range(1, BOARDHEIGHT):
            if (not is_valid_position(board, falling_piece, adj_Y=i)):
                break
        falling_piece['y'] += i - 1
        # Falling piece has landed, set it on the board
        add_to_board(board, falling_piece)
        # time.sleep(6)
        num_removed_lines = remove_complete_lines(board)
        total_lines_removed += num_removed_lines
        # Bonus score for complete lines at once
        # 40   pts for 1 line
        # 120  pts for 2 lines
        # 300  pts for 3 lines
        # 1200 pts for 4 lines

        if(num_removed_lines == 1):
            score += 40
        elif (num_removed_lines == 2):
            score += 120
        elif (num_removed_lines == 3):
            score += 300
        elif (num_removed_lines == 4):
            score += 1200

        level, fall_freq = calc_level_and_fall_freq(score)
        falling_piece    = None



        # Drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_statusGeneticMode(score, level, total_lines_removed, currnet_evolution_number, current_chromosome_number, moves_taken, current_chromosome)
        draw_next_piece(next_piece)

        if falling_piece != None:
            draw_piece(falling_piece)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        moves_taken += 1


##############################################################################
# Beast Mode Function (Infinity Moves)
##############################################################################

def RunTetrisBeastMode():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetris AI')
    f = open("Test score.txt", "a")
    f.write("************************************************************************************************\n")
    testing_chromosome = [-1.42 , 7 ,-8 , -2.41 , 8,6,8]
    score, moves_taken, linesRemoved = RunGameReturnScoreBeastMode(testing_chromosome)
    f.write(f"Chromosome {testing_chromosome}\n\tscored: {score}\n\t Moves:{moves_taken}\n\t LinesRemoved:{linesRemoved}\n")
    f.close()

def RunGameReturnScoreBeastMode(current_chromosome):
    # Setup variables
    board = get_blank_board()
    score = 0
    total_lines_removed = 0
    falling_piece = get_new_piece()
    next_piece = get_new_piece()
    moves_taken = 0
    while True:
        # Game Loop
        if (falling_piece == None):
            # No falling piece in play, so start a new piece at the top
            falling_piece = next_piece
            next_piece = get_new_piece()
            score += 1
            if (not is_valid_position(board, falling_piece)):
                # GAME-OVER
                # Can't fit a new piece on the board, so game over.
                print(f"Score is now {score}")
                return score, moves_taken, total_lines_removed
        # Check for quit
        check_quit()
        moves = GenerateAllPossibleMovesWithScoresBeastMode(board, copy.deepcopy(falling_piece), current_chromosome, copy.deepcopy(next_piece))

        if (len(moves) == 0):  # IF there is no moves availabe to  play
            print(f"Score is now {score}")
            return score, moves_taken, total_lines_removed
        best_move = chooseBestMove(moves) #[rotation , X , Score]
        falling_piece["x"] = best_move[1]
        falling_piece["y"] = -1
        falling_piece['rotation'] = best_move[0]
        for i in range(1, BOARDHEIGHT):
            if (not is_valid_position(board, falling_piece, adj_Y=i)):
                break
        falling_piece['y'] += i - 1
        # Falling piece has landed, set it on the board
        add_to_board(board, falling_piece)
        num_removed_lines = remove_complete_lines(board)
        total_lines_removed += num_removed_lines
        # Bonus score for complete lines at once
        # 40   pts for 1 line
        # 120  pts for 2 lines
        # 300  pts for 3 lines
        # 1200 pts for 4 lines

        if (num_removed_lines == 1):
            score += 40
        elif (num_removed_lines == 2):
            score += 120
        elif (num_removed_lines == 3):
            score += 300
        elif (num_removed_lines == 4):
            score += 1200

        level, fall_freq = calc_level_and_fall_freq(score)
        falling_piece = None
        # Drawing everything on the screen
        DISPLAYSURF.fill(BGCOLOR)
        draw_board(board)
        draw_statusBeastMode(score, level, total_lines_removed, moves_taken,current_chromosome)

        draw_next_piece(next_piece)

        if falling_piece != None:
            draw_piece(falling_piece)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        moves_taken += 1
def GenerateAllPossibleMovesWithScoresBeastMode(board, falling_piece, current_chromosome, next_piece=None):
    moves = []
    for rotation in range(len(PIECES[falling_piece['shape']])):
        for x in range(-2, 8):
            move_info = calc_move_info(board, falling_piece, x, rotation, 0, 0)
            next_piece_score = 0

            isValidMove = move_info[0]
            if isValidMove:
                if next_piece is not None:
                    new_board = copy.deepcopy(board)
                    falling_piece["x"] = x
                    falling_piece["rotation"] = rotation

                    for i in range(1, BOARDHEIGHT):
                        if (not is_valid_position(board, falling_piece, adj_Y=i)):
                            break
                    falling_piece['y'] += i - 1
                    add_to_board(new_board, falling_piece)
                    moves2 = GenerateAllPossibleMovesWithScoresBeastMode(new_board, next_piece, current_chromosome, None)
                    best_move = chooseBestMove(moves2)
                    next_piece_score += best_move[2]
                move_score = CalculateFitnessScore(move_info, current_chromosome)
                moves.append((rotation, x, move_score + next_piece_score))

    return moves



if __name__ == "__main__":
    display_menu()
