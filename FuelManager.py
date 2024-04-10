#!/usr/bin/env python3
#
#  This is a proposed GUI for PWR Fuel Management
#  Copyright 2021 Paramita ltd
#  Initial commit by : Andrew Whyte 29/01/2021
#
import pygame, sys, random
from pygame.locals import *
from math import sqrt
from DropDown import DropDown
from Checkbox import Checkbox
from Assembly import Assembly
from StoredInventory import StoredInventory, InventoryItem
import copy

# detect if the code has been packaged using pyinstaller
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)

# GUI - strings (useful for internationalisation etc)
# note that leading spaces matter!
IMPORT_DISCHARGE_PATTERN_MSG = 'Import Start Pattern'
IMPORT_FUEL_INVENTORY_MSG    = 'Import Fuel Inventory'
RESET_MSG                    = 'Undo Fuel Shuffle'
NEW_UNIFORM_MSG              = 'Reset Pattern'
SAVE_EXPORT_MSG              = 'Save/Export'
SOLVE_MSG                    = 'Solve'
CLICK_TO_SWAP_MSG            = "Click Assembly to Rotate, Swap or Retire."
SELECT_SWAP_OR_ROTATE_MSG    = " selected.  Select an assembly to swap · 'WASD', to move · 'E' & 'Q' to Rotate · 'R' to Retire"
SWAPPING_MSG                 = "Swapping Assemblies... "
ROTATE_MSG                   = "Rotating Assemblies..."
CORE_SHUFFLE_MSG             = "Shuffled Reload Core:"
EXIT_LOADING_MSG             = "Startup Core or Core at EOC (Fixed):"
INVENTORY_MSG                = "Fuel Inventory List:"
BURN_MSG                     = "RUN CYCLE"
SYM_CHECKBOX_MSG             = "Select Symmetry for Transforms"
REDO_MSG                     = "Redo Moves"
EMPTY_ASSEMBLY_MSG           = "Fill all Assemblies with fuel before proceeding"
EXTRACTED_ASSEMBLY_MSG       = "extracted from pos. "
SELECTED_INVENTORY_ITEM_MSG  = " selected from Fuel Inventory - select a location to load"

# Create the core constants
CORE_TYPE = "BEAVRS"
CORESHAPES = ["Eighth", "Quarter", "Full", "1/8 BEAVRS", "1/4 BEAVRS", "BEAVRS"]

WINDOWWIDTH = 1320
WINDOWHEIGHT = 700
RIGHT_MENU_POS = WINDOWWIDTH - (WINDOWWIDTH/4)
MENU_ITEM_SEPARATION = 40
INVENTORY_COLUMN_SIZE = 225
TILE_PER_COLUMN_INVENTORY = 5

FPS = 30
# shorthand notation
BLANK = None
BL = BLANK

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    ( 10,  85, 255)
DARKTURQUOISE = (  3,  54,  73)
MED_TURQUOISE = ( 33,  84, 103)
LIT_TURQUOISE = ( 93, 154, 173)
GREEN         = (  0, 204,   0)
LIT_RED       = (237,  96, 106)
DARKTEXT      = (100, 105, 150)

BGCOLOR       = DARKTURQUOISE
BTNCOLOR      = MED_TURQUOISE
TILECOLOR     = GREEN
TEXTCOLOR     = WHITE
BORDERCOLOR   = BRIGHTBLUE
TILEOUTLINE   = LIT_RED
MOVED_ASSY    = LIT_RED
BASICFONTSIZE = 20

COLOR_INACTIVE      = MED_TURQUOISE
COLOR_ACTIVE        = LIT_TURQUOISE
COLOR_LIST_INACTIVE = MED_TURQUOISE
COLOR_LIST_ACTIVE   = LIT_TURQUOISE

BUTTONCOLOR     = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR    = WHITE

CYCLE_MOVE_LIST = [] # this is an output of the batch (updated only after the burn button is pressed)

def setCoreType(b = CORE_TYPE):
    """This function sets the right data into **globals** for a set core strings
       it is called with the global CORE_TYPE at the start of main and when the core changes."""
    global CORE_TYPE
    global NUMCOORD_START_OFFSET
    global ALPHABETCOORD_START_OFFSET
    global ALPHABETCOORDS
    global COREWIDTH  # number of columns in the boa
    global COREHEIGHT # number of rows in the boa
    global TILESIZE
    global LABELFONTSIZE
    global WINDOWWIDTH
    global WINDOWHEIGHT
    global XMAIN_MARGIN
    global XSTART_MARGIN
    global YMARGIN
    global INVENTORY_COLUMN_SIZE
    CORE_TYPE = b
    ALPHABETCOORDS = []
    if b == "Quarter" or b == "1/4 BEAVRS":
        NUMCOORD_START_OFFSET=8
        ALPHABETCOORD_START_OFFSET=0
        COREWIDTH = 8  # number of columns in the core
        COREHEIGHT = 8 # number of rows in the core
        TILESIZE = 35
        print(COREWIDTH)
    elif b == "SIMPLEEIGHTH":
        NUMCOORD_START_OFFSET=8
        ALPHABETCOORD_START_OFFSET=3
        COREWIDTH = 5  # number of columns in the core
        COREHEIGHT = 7 # number of rows in the core
        TILESIZE = 45
    elif b == "Eighth" or b == "1/8 BEAVRS":
        NUMCOORD_START_OFFSET=8
        ALPHABETCOORD_START_OFFSET=3
        COREWIDTH = 6  # number of columns in the core
        COREHEIGHT = 8 # number of rows in the core
        TILESIZE = 45
    elif b == "Full" or b=="BEAVRS":
        NUMCOORD_START_OFFSET=1
        ALPHABETCOORD_START_OFFSET=0
        COREWIDTH = 15  # number of columns in the core
        COREHEIGHT = 15 # number of rows in the core
        TILESIZE = 25
        LABELFONTSIZE = 14
    else:
        NUMCOORD_START_OFFSET=8
        ALPHABETCOORD_START_OFFSET=0
        COREWIDTH = 6  # number of columns in the core
        COREHEIGHT = 6 # number of rows in the core
        TILESIZE = 35
    for letter in range(0,26):
        ALPHABETCOORDS.append(str(chr(letter+65+ALPHABETCOORD_START_OFFSET))) # 65 is the start of the alphabet in ascii
    del ALPHABETCOORDS[15]
    del ALPHABETCOORDS[14]
    del ALPHABETCOORDS[8]
    XMAIN_MARGIN = int((WINDOWWIDTH - (TILESIZE * COREWIDTH + (COREWIDTH - 1))) / 2)
    XSTART_MARGIN = 25
    YMARGIN = int((WINDOWHEIGHT - (TILESIZE * COREHEIGHT + (COREHEIGHT - 1))) / 2) -60

def main():
    """ Entry point of the code and main program loop"""
    #GUI messages
    global IMPORT_DISCHARGE_PATTERN_MSG, IMPORT_FUEL_INVENTORY_MSG, RESET_MSG, NEW_UNIFORM_MSG, SAVE_EXPORT_MSG, SOLVE_MSG, CLICK_TO_SWAP_MSG, SELECT_SWAP_OR_ROTATE_MSG, SWAPPING_MSG, ROTATE_MSG, REDO_MSG, CORE_SHUFFLE_MSG, EXIT_LOADING_MSG, INVENTORY_MSG, BURN_MSG, SYM_CHECKBOX_MSG, EMPTY_ASSEMBLY_MSG
    global CORE_SHUFFLE_MSG, EXIT_LOADING_MSG, INVENTORY_MSG, BURN_MSG
    global FPSCLOCK, DISPLAYSURF, BASICFONT, LABELFONT
    global DROPDOWNMENU
    global LOAD_INPUTS_SURF, LOAD_INVENT_SURF, RESET_SURF, NEW_SURF, SAVE_SURF, SOLVE_SURF, BURN_SURF, REDO_SURF
    global LOAD_INPUTS_RECT, LOAD_INVENT_RECT, RESET_RECT, NEW_RECT, SAVE_RECT, SOLVE_RECT, BURN_RECT, REDO_RECT
    global startCore, CYCLE_MOVE_LIST
    global CORE_TYPE
    global SYMMETRY_LIST
    global STORED_INVENTORY
    global NA_SOUND_LIST

    setCoreType() # set the global data to the right data for the core.
    swapFrom = False # first position selected
    swapTo = False   # second position.
    moveFocus = False# when usinng keys we want to keep focus on the new assembly
    swapFromx = 0    # assembly coords of the assembly to move
    swapFromy = 0

    ## pygame set up.
    pygame.init()
    icon = pygame.image.load('resources/small-window-icon.png')
    pygame.display.set_icon(icon)
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('PWR Loading Pattern Tool')
    BASICFONT = pygame.font.Font('resources/Oswald-Medium.ttf', BASICFONTSIZE)
    LABELFONT = pygame.font.Font('resources/Oswald-Medium.ttf', LABELFONTSIZE)
	
    NA_SOUND_LIST = [pygame.mixer.Sound('resources/NA1.wav'),pygame.mixer.Sound('resources/NA2.wav'),pygame.mixer.Sound('resources/NA3.wav')]

    # Store the option buttons and their rectangles in OPTIONS.
    LOAD_INPUTS_SURF, LOAD_INPUTS_RECT = makeText2(IMPORT_DISCHARGE_PATTERN_MSG,  TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, 1* MENU_ITEM_SEPARATION)
    LOAD_INVENT_SURF, LOAD_INVENT_RECT = makeText2(IMPORT_FUEL_INVENTORY_MSG, TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, 2* MENU_ITEM_SEPARATION)

    BURN_SURF, BURN_RECT   = makeText2(BURN_MSG,        TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, WINDOWHEIGHT - 6* MENU_ITEM_SEPARATION)
    REDO_SURF, REDO_RECT   = makeText2(REDO_MSG,        TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, WINDOWHEIGHT - 4* MENU_ITEM_SEPARATION)
    RESET_SURF, RESET_RECT = makeText2(RESET_MSG,       TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, WINDOWHEIGHT - 5* MENU_ITEM_SEPARATION)
    NEW_SURF,   NEW_RECT   = makeText2(NEW_UNIFORM_MSG, TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, WINDOWHEIGHT - 3 * MENU_ITEM_SEPARATION)
    SAVE_SURF,  SAVE_RECT  = makeText2(SAVE_EXPORT_MSG,         TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, WINDOWHEIGHT - 2 * MENU_ITEM_SEPARATION)
    SOLVE_SURF, SOLVE_RECT = makeText2(SOLVE_MSG,               TEXTCOLOR, BTNCOLOR, RIGHT_MENU_POS, WINDOWHEIGHT - 1 * MENU_ITEM_SEPARATION)
    DROPDOWNMENU = DropDown(
        [COLOR_INACTIVE, COLOR_ACTIVE],
        [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
        RIGHT_MENU_POS, 3.5* MENU_ITEM_SEPARATION, 200, 40,
        BASICFONT,
        "Select Core", CORESHAPES, "Core Pattern Selector:")
    SYMMETRY_LIST = []
    for i, sym in enumerate(["None", "Quarter", "Eighth"]):
        box = Checkbox(DISPLAYSURF, RIGHT_MENU_POS, (i+7)*MENU_ITEM_SEPARATION, i, TEXTCOLOR, sym[i],
            TEXTCOLOR, TEXTCOLOR, 10, TEXTCOLOR, (28, 1), LABELFONT)
        SYMMETRY_LIST.append(box)
    STORED_INVENTORY = generateInventory("Example")
    mainCore, startCore, solutionSeq = generateNewPattern(CORE_TYPE)
    allMoves = [] # list of moves made from the solved configuration
    redoMoves = [] # backup of undone moves list.

    msg = CLICK_TO_SWAP_MSG # contains the message to show in the upper left corner.
    while True: # main game loop
        # start by drawing the screen (in case any junk is left over from the last loop)
        drawGUI(mainCore, startCore, STORED_INVENTORY, msg)
        checkForQuit()
        event_list = pygame.event.get()
        for event in event_list: # The event handler :processes the event list - any incoming interation
            if event.type == MOUSEBUTTONDOWN or event.type == MOUSEMOTION:
                selected_option = DROPDOWNMENU.update(event_list)
                if selected_option >= 0:
                    CORE_TYPE = DROPDOWNMENU.options[selected_option]
                    #print(CORE_TYPE)
                    setCoreType(CORE_TYPE)
                    print(len(mainCore))
                    mainCore = getStartingCore()
                    startCore=copy.deepcopy(mainCore)
                    # clear any selected assembly
                    #TODO: create an interpreter to change the instruction list...
                    swapFrom = False
                    msg = CLICK_TO_SWAP_MSG
                    allMoves = []

                    drawGUI(mainCore, startCore, StoredInventory, msg)
                    DROPDOWNMENU.main = DROPDOWNMENU.options[selected_option]
                    DROPDOWNMENU.draw(DISPLAYSURF)
                    pygame.display.flip()

            elif event.type == MOUSEBUTTONUP:
                # If clicked in inventory
                spotx, spoty = getSpotClicked(mainCore, event.pos[0], event.pos[1], coreImage="Inventory")
                if (spotx, spoty) != (None, None):
                    if swapFrom == False:
                        swapFrom = True
                        msg = str(STORED_INVENTORY.inventoryList[spoty].assembly.label) + SELECTED_INVENTORY_ITEM_MSG
                        swapFromy = spoty
                        swapFromx = -1
                    else:
                        if swapFromx == -1: # double inventory selection!
                            if swapFromy == spoty: # deselect
                                swapFrom = False
                                msg = CLICK_TO_SWAP_MSG
                            else:
                                swapFrom = True
                                msg = str(STORED_INVENTORY.inventoryList[spoty].assembly.label) + SELECTED_INVENTORY_ITEM_MSG
                                swapFromy = spoty
                                swapFromx = -1
                        else:
                            swapTo = True
                            swap1 = (-1, spoty)
                            swap2 = (swapFromx, swapFromy)

                spotx, spoty = getSpotClicked(mainCore, event.pos[0], event.pos[1])
                # If clicked off Main Core
                if (spotx, spoty) == (None, None): # not in an assembly so
                    #TODO: checkbox not working labels not shown
                    changed = False
                    for i, box in enumerate(SYMMETRY_LIST):
                        changed = changed or box.update_checkbox(event)
                        if changed:
                            tempIndx = i
                    if changed:
                        temp = SYMMETRY_LIST[tempIndx].checked
                        if temp:
                            for box in SYMMETRY_LIST:
                                box.checked = False
                            SYMMETRY = SYMMETRY_LIST[tempIndx].caption
                        else:
                            SYMMETRY = "None"
                        SYMMETRY_LIST[tempIndx].checked = temp
                        #debugging
                        for box in SYMMETRY_LIST:
                            if box.checked:
                                print(str(box.caption)+ " is checked")
                            if not box.checked:
                                print(str(box.caption)+ " is not checked")
                    # check if the user clicked on an option button
                    if LOAD_INPUTS_RECT.collidepoint(event.pos):
                        random.choice(NA_SOUND_LIST).play()
                    elif LOAD_INVENT_RECT.collidepoint(event.pos):
                        random.choice(NA_SOUND_LIST).play()
                    elif BURN_RECT.collidepoint(event.pos):
                        mainCore, startCore, allMoves, msg = doBurnup(mainCore, startCore, allMoves)
                    elif REDO_RECT.collidepoint(event.pos):
                        allMoves = resetAnimation(mainCore, startCore, redoMoves, reverse=False) # clicked on Reset button
                    elif RESET_RECT.collidepoint(event.pos):
                        redoMoves = copy.deepcopy(allMoves)
                        resetAnimation(mainCore, startCore, allMoves) # clicked on Reset button
                        allMoves = []
                    elif NEW_RECT.collidepoint(event.pos):
                        mainCore, startCore, solutionSeq = generateNewPattern(CORE_TYPE) # clicked on New Game button
                        allMoves = []
                    elif SAVE_RECT.collidepoint(event.pos):
                        random.choice(NA_SOUND_LIST).play()
                    elif SOLVE_RECT.collidepoint(event.pos):# clicked on Solve button
                        #TODO: Write something nifty to solve the core loading problem...
                        resetAnimation(mainCore,startCore, solutionSeq + allMoves)
                        allMoves = []
                else:
                    if mainCore[int(spoty)][int(spotx)].label != BLANK : # allow selection of empty assemblies...
                        if swapFrom == False:
                            swapFrom = True
                            moveFocus = False
                            swapFromx = spotx
                            swapFromy = spoty
                            print(swapFrom)
                            print(swapFromx)
                            print(swapFromy)
                            msg = str(mainCore[int(spoty)][int(spotx)].label) + SELECT_SWAP_OR_ROTATE_MSG
                        else:
                            if swapFromx == spotx  and swapFromy == spoty: # ignore if same
                                swapFrom = False
                                msg = CLICK_TO_SWAP_MSG
                            else:
                                swapTo = True
                                swap1 = [swapFromx, swapFromy]
                                swap2 = [spotx, spoty]
            elif event.type == KEYUP:
                if swapFrom != False and swapFromx != -1:
                    print("key event: " +str(event.key))
                    if event.key in (K_e, K_q):
                        direction = -1 if event.key ==K_q else 1
                        swap1 = [swapFromx, swapFromy]
                        print("Rotate assembly" + str(swapFromx)+" "+str(swapFromy) )
                        print(direction)
                        rotateAnimation(mainCore, startCore, STORED_INVENTORY, swap1, direction, ROTATE_MSG, animationSpeedSeconds=0.65)
                        makeRotate(mainCore, swap1, direction)
                        allMoves.append(["rotate", swap1, direction])
                        swapTo = False  # position to swap to...
                        swapFrom = False
                        msg = CLICK_TO_SWAP_MSG
                    # check if the user pressed a key to slide a tile
                    elif event.key is K_r:
                        if mainCore[int(swapFromy)][int(swapFromx)].label != "Empty":
                            swap1 = [swapFromx, swapFromy]
                            index = makeRemove(mainCore, swap1)
                            allMoves.append(["remove", swap1, index])#mainCore[int(swapFromy)][int(swapFromx)]])
                            swapTo = False  # position to swap to...
                            swapFrom = False
                            msg = CLICK_TO_SWAP_MSG
                    elif event.key in (K_LEFT, K_a) and isValidSwap(mainCore, [swapFromx, swapFromy], [(swapFromx-1)%COREWIDTH, swapFromy]):
                        swap1 = [swapFromx, swapFromy]
                        swap2 = [(swapFromx-1)%COREWIDTH, swapFromy]
                        swapTo = True
                        moveFocus = True
                    elif event.key in (K_RIGHT, K_d) and isValidSwap(mainCore, [swapFromx, swapFromy], [(swapFromx+1)%COREWIDTH, swapFromy]):
                        swap1 = [swapFromx, swapFromy]
                        swap2 = [(swapFromx+1)%COREWIDTH, swapFromy]
                        swapTo = True
                        moveFocus = True
                    elif event.key in (K_UP, K_w) and isValidSwap(mainCore, [swapFromx, swapFromy], [swapFromx, (swapFromy-1)%COREHEIGHT]):
                        swap1 = [swapFromx, swapFromy]
                        swap2 = [swapFromx, (swapFromy-1)%COREHEIGHT]
                        swapTo = True
                        moveFocus = True
                    elif event.key in (K_DOWN, K_s) and isValidSwap(mainCore, [swapFromx, swapFromy], [swapFromx, (swapFromy+1)%COREHEIGHT]):
                        swap1 = [swapFromx, swapFromy]
                        swap2 = [swapFromx, (swapFromy+1)%COREHEIGHT]
                        swapTo = True
                        moveFocus = True
        # there used to be a separation of animation and function in the main loop...
        # this is being lost... :(
        if swapTo:
            redoMoves = []
            #allMoves.append([swapFrom, swapTo]) # record the slide
            swapAnimation(mainCore, startCore, STORED_INVENTORY, swap1, swap2, SWAPPING_MSG, animationSpeedSeconds=0.65)
            if(swap1[0] == -1):
                removed = makeLoad(mainCore, swap2, swap1[1])
                allMoves.append(removed)
                allMoves.append(["load", swap2, swap1[1]])
            else:
                makeSwap(mainCore, swap1, swap2)
                allMoves.append(["swap",swap1,swap2])
            swapTo = False  # position to swap to...
            swapFrom = False
            msg = CLICK_TO_SWAP_MSG
            if moveFocus: # used keys to move assembly so change swapFrom to the old swapFrom
                swapFrom = True
                swapFromx = swap2[0]
                swapFromy = swap2[1]
                #print(str(swapFromx)+ "  " +str(swapFromy))
                msg = str(mainCore[swapFromy][swapFromx].label) + SELECT_SWAP_OR_ROTATE_MSG
                moveFocus = False
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def terminate():
    pygame.quit()
    sys.exit()

def checkForQuit():
    """ Gracefully exit  - animations could take a second or two so we may need to check for exits outside of the event loop..."""
    # FIXME: this is a bit hacky, events should really be carried out in the event loop, but this is ok at a push...
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def getStartingCore():
    """ This code sets the data of the core structure. """
    # Return a core data structure
    if CORE_TYPE == "1/8 BEAVRS":
        assert COREWIDTH == 6 and COREHEIGHT ==8
        core =[[Assembly( "H8",1.6),],
                [Assembly( "H9",2.4),Assembly( "G9",1.6),],
                [Assembly("H10",1.6),Assembly("G10",2.4),Assembly("F10",1.6),],
                [Assembly("H11",2.4),Assembly("G11",1.6),Assembly("F11",2.4),Assembly("E11",1.6),],
                [Assembly("H12",1.6),Assembly("G12",2.4),Assembly("F12",1.6),Assembly("E12",2.4),Assembly("D12",2.4),],
                [Assembly("H13",2.4),Assembly("G13",1.6),Assembly("F13",2.4),Assembly("E13",1.6),Assembly("D13",2.4),Assembly("C13",3.2),],
                [Assembly("H14",1.6),Assembly("G14",3.2),Assembly("F14",1.6),Assembly("E14",3.2),Assembly("D14",3.2),Assembly("C14",3.2),],
                [Assembly("H15",3.2),Assembly("G15",3.2),Assembly("F15",3.2),Assembly("E15",3.2),  Assembly( BL),    Assembly( BL),      ]]
        return core
    elif CORE_TYPE == "1/4 BEAVRS" :
        assert COREWIDTH == 8 and COREHEIGHT ==8
        core = [ [ Assembly("H8", 1.6),Assembly( "G8",2.4), Assembly("F8",1.6), Assembly("E8",2.4), Assembly("D8",1.6), Assembly("C8",2.4), Assembly("B8", 1.6), Assembly("A8",3.2)],
                  [ Assembly(       BL),Assembly( "G9",1.6), Assembly("F9",2.4), Assembly("E9",1.6), Assembly("D9",2.4), Assembly("C9",1.6), Assembly("B9", 3.2), Assembly("A9",3.2)],
                  [ Assembly(       BL),Assembly("G10",2.4),Assembly("F10",1.6),Assembly("E10",2.4),Assembly("D10",1.6),Assembly("C10",2.4),Assembly("B10",1.6), Assembly("A10",3.2)],
                  [ Assembly(       BL),Assembly("G11",1.6),Assembly("F11",2.4),Assembly("E11",1.6),Assembly("D11",2.4),Assembly("C11",1.6),Assembly("B11",3.2), Assembly("A11",3.2)],
                  [ Assembly(       BL),Assembly("G12",2.4),Assembly("F12",1.6),Assembly("E12",2.4),Assembly("D12",2.4),Assembly("C12",2.4),Assembly("B12",3.2), Assembly( BL),],
                  [ Assembly(       BL),Assembly("G13",1.6),Assembly("F13",2.4),Assembly("E13",1.6),Assembly("D13",2.4),Assembly("C13",3.2),Assembly("B13",3.2), Assembly( BL),],
                  [ Assembly(       BL),Assembly("G14",3.2),Assembly("F14",1.6),Assembly("E14",3.2),Assembly("D14",3.2),Assembly("C14",3.2),Assembly( BL),       Assembly( BL),],
                  [ Assembly(       BL),Assembly("G15",3.2),Assembly("F15",3.2),Assembly("E15",3.2),  Assembly( BL),    Assembly( BL),      Assembly( BL),       Assembly( BL),],
                ]
        return core
    elif CORE_TYPE == "Quarter":
        assert COREWIDTH == 8 and COREHEIGHT ==8
        core = [ [ Assembly("H8"),Assembly( "G8"),Assembly( "F8"),Assembly( "E8"),Assembly( "D8"),Assembly( "C8"),Assembly( "B8"),Assembly( "A8")],
                  [ Assembly(  BL),Assembly( "G9"),Assembly( "F9"),Assembly( "E9"),Assembly( "D9"),Assembly( "C9"),Assembly( "B9"),Assembly( "A9")],
                  [ Assembly(  BL),Assembly("G10"),Assembly("F10"),Assembly("E10"),Assembly("D10"),Assembly("C10"),Assembly("B10"),Assembly("A10")],
                  [ Assembly(  BL),Assembly("G11"),Assembly("F11"),Assembly("E11"),Assembly("D11"),Assembly("C11"),Assembly("B11"),Assembly("A11")],
                  [ Assembly(  BL),Assembly("G12"),Assembly("F12"),Assembly("E12"),Assembly("D12"),Assembly("C12"),Assembly("B12"),Assembly(   BL)],
                  [ Assembly(  BL),Assembly("G13"),Assembly("F13"),Assembly("E13"),Assembly("D13"),Assembly("C13"),Assembly("B13"),Assembly(   BL)],
                  [ Assembly(  BL),Assembly("G14"),Assembly("F14"),Assembly("E14"),Assembly("D14"),Assembly("C14"),Assembly(   BL),Assembly(   BL)],
                  [ Assembly(  BL),Assembly("G15"),Assembly("F15"),Assembly("E15"),Assembly(   BL),Assembly(   BL),Assembly(   BL),Assembly(   BL)],
                ]
        return core
    elif CORE_TYPE == "BEAVRS":
        assert COREWIDTH == 15 and COREHEIGHT ==15
        core = [[Assembly(   BL),    Assembly(   BL),     Assembly(   BL),    Assembly(   BL),    Assembly( "L1",3.2),Assembly( "K1",3.2),Assembly( "J1",3.2),Assembly( "H1",3.2),Assembly( "G1",3.2), Assembly("F1",3.2), Assembly("E1",3.2),  Assembly( BL),    Assembly( BL),      Assembly( BL),       Assembly( BL),],
                 [Assembly(   BL),    Assembly(   BL),     Assembly( "N2",3.2),Assembly( "M2",3.2),Assembly( "L2",3.2),Assembly( "K2",1.6),Assembly( "J2",3.2),Assembly( "H2",1.6),Assembly( "G2",3.2), Assembly("F2",1.6), Assembly("E2",3.2), Assembly("D2",3.2), Assembly("C2",3.2), Assembly( BL),       Assembly( BL),],
                 [Assembly(   BL),    Assembly( "P3", 3.2),Assembly( "N3",3.2),Assembly( "M3",2.4),Assembly( "L3",1.6),Assembly( "K3",2.4),Assembly( "J3",1.6),Assembly( "H3",2.4),Assembly( "G3",1.6), Assembly("F3",2.4), Assembly("E3",1.6), Assembly("D3",2.4), Assembly("C3",3.2), Assembly("B3", 3.2), Assembly( BL),],
                 [Assembly(   BL),    Assembly( "P4", 3.2),Assembly( "N4",2.4),Assembly( "M4",2.4),Assembly( "L4",2.4),Assembly( "K4",1.6),Assembly( "J4",2.4),Assembly( "H4",1.6),Assembly( "G4",2.4), Assembly("F4",1.6), Assembly("E4",2.4), Assembly("D4",2.4), Assembly("C4",2.4), Assembly("B4", 3.2), Assembly( BL),],
                 [Assembly( "R5",3.2),Assembly( "P5", 3.2),Assembly( "N5",1.6),Assembly( "M5",2.4),Assembly( "L5",1.6),Assembly( "K5",2.4),Assembly( "J5",1.6),Assembly( "H5",2.4),Assembly( "G5",1.6), Assembly("F5",2.4), Assembly("E5",1.6), Assembly("D5",2.4), Assembly("C5",1.6), Assembly("B5", 3.2), Assembly("A5",3.2)],
                 [Assembly( "R6",3.2),Assembly( "P6", 1.6),Assembly( "N6",2.4),Assembly( "M6",1.6),Assembly( "L6",2.4),Assembly( "K6",1.6),Assembly( "J6",2.4),Assembly( "H6",1.6),Assembly( "G6",2.4), Assembly("F6",1.6), Assembly("E6",2.4), Assembly("D6",1.6), Assembly("C6",2.4), Assembly("B6", 1.6), Assembly("A6",3.2)],
                 [Assembly( "R7",3.2),Assembly( "P7", 3.2),Assembly( "N7",1.6),Assembly( "M7",2.4),Assembly( "L7",1.6),Assembly( "K7",2.4),Assembly( "J7",1.6),Assembly( "H7",2.4),Assembly( "G7",1.6), Assembly("F7",2.4), Assembly("E7",1.6), Assembly("D7",2.4), Assembly("C7",1.6), Assembly("B7", 3.2), Assembly("A7",3.2)],
                 [Assembly( "R8",3.2),Assembly( "P8", 1.6),Assembly( "N8",2.4),Assembly( "M8",1.6),Assembly( "L8",2.4),Assembly( "K8",1.6),Assembly( "J8",2.4),Assembly( "H8",1.6),Assembly( "G8",2.4), Assembly("F8",1.6), Assembly("E8",2.4), Assembly("D8",1.6), Assembly("C8",2.4), Assembly("B8", 1.6), Assembly("A8",3.2)],
                 [Assembly( "R9",3.2),Assembly( "P9", 3.2),Assembly( "N9",1.6),Assembly( "M9",2.4),Assembly( "L9",1.6),Assembly( "K9",2.4),Assembly( "J9",1.6),Assembly( "H9",2.4),Assembly( "G9",1.6), Assembly("F9",2.4), Assembly("E9",1.6), Assembly("D9",2.4), Assembly("C9",1.6), Assembly("B9", 3.2), Assembly("A9",3.2)],
                 [Assembly("R10",3.2),Assembly("P10", 1.6),Assembly("N10",2.4),Assembly("M10",1.6),Assembly("L10",2.4),Assembly("K10",1.6),Assembly("J10",2.4),Assembly("H10",1.6),Assembly("G10",2.4),Assembly("F10",1.6),Assembly("E10",2.4),Assembly("D10",1.6),Assembly("C10",2.4),Assembly("B10",1.6),Assembly("A10",3.2)],
                 [Assembly("R11",3.2),Assembly("P11", 3.2),Assembly("N11",1.6),Assembly("M11",2.4),Assembly("L11",1.6),Assembly("K11",2.4),Assembly("J11",1.6),Assembly("H11",2.4),Assembly("G11",1.6),Assembly("F11",2.4),Assembly("E11",1.6),Assembly("D11",2.4),Assembly("C11",1.6),Assembly("B11",3.2),Assembly("A11",3.2)],
                 [Assembly(   BL),    Assembly("P12", 3.2),Assembly("N12",2.4),Assembly("M12",2.4),Assembly("L12",2.4),Assembly("K12",1.6),Assembly("J12",2.4),Assembly("H12",1.6),Assembly("G12",2.4),Assembly("F12",1.6),Assembly("E12",2.4),Assembly("D12",2.4),Assembly("C12",2.4),Assembly("B12",3.2), Assembly( BL),],
                 [Assembly(   BL),    Assembly("P13", 3.2),Assembly("N13",3.2),Assembly("M13",2.4),Assembly("L13",1.6),Assembly("K13",2.4),Assembly("J13",1.6),Assembly("H13",2.4),Assembly("G13",1.6),Assembly("F13",2.4),Assembly("E13",1.6),Assembly("D13",2.4),Assembly("C13",3.2),Assembly("B13",3.2), Assembly( BL),],
                 [Assembly(   BL),    Assembly(   BL),     Assembly("N14",3.2),Assembly("M14",3.2),Assembly("L14",3.2),Assembly("K14",1.6),Assembly("J14",3.2),Assembly("H14",1.6),Assembly("G14",3.2),Assembly("F14",1.6),Assembly("E14",3.2),Assembly("D14",3.2),Assembly("C14",3.2),Assembly( BL),       Assembly( BL),],
                 [Assembly(   BL),    Assembly(   BL),     Assembly(   BL),    Assembly(   BL),    Assembly("L15",3.2),Assembly("K15",3.2),Assembly("J15",3.2),Assembly("H15",3.2),Assembly("G15",3.2),Assembly("F15",3.2),Assembly("E15",3.2),  Assembly( BL),    Assembly( BL),      Assembly( BL),       Assembly( BL),],
                ]
        return core
    elif CORE_TYPE == "Full":
        assert COREWIDTH == 15 and COREHEIGHT ==15
        core = [[Assembly(   BL),Assembly(   BL),Assembly(   BL),Assembly(   BL),Assembly( "L1"),Assembly( "K1"),Assembly( "J1"),Assembly( "H1"),Assembly( "G1"), Assembly("F1"), Assembly("E1"),  Assembly( BL),   Assembly( BL),  Assembly( BL), Assembly( BL),],
                 [Assembly(   BL),Assembly(   BL),Assembly( "N2"),Assembly( "M2"),Assembly( "L2"),Assembly( "K2"),Assembly( "J2"),Assembly( "H2"),Assembly( "G2"), Assembly("F2"), Assembly("E2"), Assembly("D2"),  Assembly("C2"),  Assembly( BL), Assembly( BL),],
                 [Assembly(   BL),Assembly( "P3"),Assembly( "N3"),Assembly( "M3"),Assembly( "L3"),Assembly( "K3"),Assembly( "J3"),Assembly( "H3"),Assembly( "G3"), Assembly("F3"), Assembly("E3"), Assembly("D3"),  Assembly("C3"), Assembly("B3"), Assembly( BL),],
                 [Assembly(   BL),Assembly( "P4"),Assembly( "N4"),Assembly( "M4"),Assembly( "L4"),Assembly( "K4"),Assembly( "J4"),Assembly( "H4"),Assembly( "G4"), Assembly("F4"), Assembly("E4"), Assembly("D4"),  Assembly("C4"), Assembly("B4"), Assembly( BL),],
                 [Assembly( "R5"),Assembly( "P5"),Assembly( "N5"),Assembly( "M5"),Assembly( "L5"),Assembly( "K5"),Assembly( "J5"),Assembly( "H5"),Assembly( "G5"), Assembly("F5"), Assembly("E5"), Assembly("D5"),  Assembly("C5"), Assembly("B5"), Assembly("A5")],
                 [Assembly( "R6"),Assembly( "P6"),Assembly( "N6"),Assembly( "M6"),Assembly( "L6"),Assembly( "K6"),Assembly( "J6"),Assembly( "H6"),Assembly( "G6"), Assembly("F6"), Assembly("E6"), Assembly("D6"),  Assembly("C6"), Assembly("B6"), Assembly("A6")],
                 [Assembly( "R7"),Assembly( "P7"),Assembly( "N7"),Assembly( "M7"),Assembly( "L7"),Assembly( "K7"),Assembly( "J7"),Assembly( "H7"),Assembly( "G7"), Assembly("F7"), Assembly("E7"), Assembly("D7"),  Assembly("C7"), Assembly("B7"), Assembly("A7")],
                 [Assembly( "R8"),Assembly( "P8"),Assembly( "N8"),Assembly( "M8"),Assembly( "L8"),Assembly( "K8"),Assembly( "J8"),Assembly( "H8"),Assembly( "G8"), Assembly("F8"), Assembly("E8"), Assembly("D8"),  Assembly("C8"), Assembly("B8"), Assembly("A8")],
                 [Assembly( "R9"),Assembly( "P9"),Assembly( "N9"),Assembly( "M9"),Assembly( "L9"),Assembly( "K9"),Assembly( "J9"),Assembly( "H9"),Assembly( "G9"), Assembly("F9"), Assembly("E9"), Assembly("D9"),  Assembly("C9"), Assembly("B9"), Assembly("A9")],
                 [Assembly("R10"),Assembly("P10"),Assembly("N10"),Assembly("M10"),Assembly("L10"),Assembly("K10"),Assembly("J10"),Assembly("H10"),Assembly("G10"),Assembly("F10"),Assembly("E10"),Assembly("D10"), Assembly("C10"),Assembly("B10"), Assembly("A10")],
                 [Assembly("R11"),Assembly("P11"),Assembly("N11"),Assembly("M11"),Assembly("L11"),Assembly("K11"),Assembly("J11"),Assembly("H11"),Assembly("G11"),Assembly("F11"),Assembly("E11"),Assembly("D11"), Assembly("C11"),Assembly("B11"), Assembly("A11")],
                 [Assembly(   BL),Assembly("P12"),Assembly("N12"),Assembly("M12"),Assembly("L12"),Assembly("K12"),Assembly("J12"),Assembly("H12"),Assembly("G12"),Assembly("F12"),Assembly("E12"),Assembly("D12"), Assembly("C12"),Assembly("B12"), Assembly( BL),],
                 [Assembly(   BL),Assembly("P13"),Assembly("N13"),Assembly("M13"),Assembly("L13"),Assembly("K13"),Assembly("J13"),Assembly("H13"),Assembly("G13"),Assembly("F13"),Assembly("E13"),Assembly("D13"), Assembly("C13"),Assembly("B13"), Assembly( BL),],
                 [Assembly(   BL),Assembly(   BL),Assembly("N14"),Assembly("M14"),Assembly("L14"),Assembly("K14"),Assembly("J14"),Assembly("H14"),Assembly("G14"),Assembly("F14"),Assembly("E14"),Assembly("D14"), Assembly("C14"),  Assembly( BL), Assembly( BL),],
                 [Assembly(   BL),Assembly(   BL),Assembly(   BL),Assembly(   BL),Assembly("L15"),Assembly("K15"),Assembly("J15"),Assembly("H15"),Assembly("G15"),Assembly("F15"),Assembly("E15"),  Assembly( BL),   Assembly( BL),  Assembly( BL), Assembly( BL),],
                ]
        # core = [[   BL,   BL,   BL,   BL, "L1", "K1", "J1", "H1", "G1", "F1", "E1",   BL,   BL,   BL,  BL,],
        #          [   BL,   BL, "N2", "M2", "L2", "K2", "J2", "H2", "G2", "F2", "E2", "D2", "C2",   BL,  BL,],
        #          [   BL, "P3", "N3", "M3", "L3", "K3", "J3", "H3", "G3", "F3", "E3", "D3", "C3", "B3",  BL,],
        #          [   BL, "P4", "N4", "M4", "L4", "K4", "J4", "H4", "G4", "F4", "E4", "D4", "C4", "B4",  BL,],
        #          [ "R5", "P5", "N5", "M5", "L5", "K5", "J5", "H5", "G5", "F5", "E5", "D5", "C5", "B5", "A5"],
        #          [ "R6", "P6", "N6", "M6", "L6", "K6", "J6", "H6", "G6", "F6", "E6", "D6", "C6", "B6", "A6"],
        #          [ "R7", "P7", "N7", "M7", "L7", "K7", "J7", "H7", "G7", "F7", "E7", "D7", "C7", "B7", "A7"],
        #          [ "R8", "P8", "N8", "M8", "L8", "K8", "J8", "H8", "G8", "F8", "E8", "D8", "C8", "B8", "A8"],
        #          [ "R9", "P9", "N9", "M9", "L9", "K9", "J9", "H9", "G9", "F9", "E9", "D9", "C9", "B9", "A9"],
        #          ["R10","P10","N10","M10","L10","K10","J10","H10","G10","F10","E10","D10","C10","B10","A10"],
        #          ["R11","P11","N11","M11","L11","K11","J11","H11","G11","F11","E11","D11","C11","B11","A11"],
        #          [   BL,"P12","N12","M12","L12","K12","J12","H12","G12","F12","E12","D12","C12","B12",  BL,],
        #          [   BL,"P13","N13","M13","L13","K13","J13","H13","G13","F13","E13","D13","C13","B13",  BL,],
        #          [   BL,   BL,"N14","M14","L14","K14","J14","H14","G14","F14","E14","D14","C14",   BL,  BL,],
        #          [   BL,   BL,   BL,   BL,"L15","K15","J15","H15","G15","F15","E15",   BL,   BL,   BL,  BL,],
        #         ]
        return core
    elif CORE_TYPE == "SIMPLEEIGHTH":
        assert COREWIDTH == 5 and COREHEIGHT ==7
        core = [[ 1],
                 [ 2, 3 ],
                 [ 4, 5, 6],
                 [ 7, 8, 9,10],
                 [11,12,13,14,15],
                 [16,17,18,19],
                 [20,21],
                ]
    elif CORE_TYPE == "Eighth":
        assert COREWIDTH == 6 and COREHEIGHT ==8
        core =[[Assembly( "H8"),],
                [Assembly( "H9"),Assembly( "G9"),],
                [Assembly("H10"),Assembly("G10"),Assembly("F10"),],
                [Assembly("H11"),Assembly("G11"),Assembly("F11"),Assembly("E11"),],
                [Assembly("H12"),Assembly("G12"),Assembly("F12"),Assembly("E12"),Assembly("D12"),],
                [Assembly("H13"),Assembly("G13"),Assembly("F13"),Assembly("E13"),Assembly("D13"),Assembly("C13"),],
                [Assembly("H14"),Assembly("G14"),Assembly("F14"),Assembly("E14"),Assembly("D14"),Assembly("C14"),],
                [Assembly("H15"),Assembly("G15"),Assembly("F15"),Assembly("E15"),Assembly(   BL),Assembly(   BL),]]
        return core
    else:
        # default to my square microcore
        core = [[1,2,3,4,5,6],
                 [1,2,3,4,5,6],
                 [1,2,3,4,5,6],
                 [1,2,3,4,5,6],
                 [1,2,3,4,5,6],
                 [1,2,3,4,5,6]]
        core[COREWIDTH-1][COREHEIGHT-1] = BLANK
    return core

def printSwap(core, swap1, swap2):
    """ This function takes two ordinates 'swap1' & 'swap2' and returns a text description of a swap operation"""
    onex, oney = swap1
    twox, twoy = swap2
    print("Assembly: "+ALPHABETCOORDS[onex]+","+str(oney)+" has label: "+ core[oney][onex].label)
    print("Assembly: "+ALPHABETCOORDS[twox]+","+str(twoy)+" has label: "+ core[twoy][twox].label)
    print("swap: " + ALPHABETCOORDS[onex]+","+str(oney) +" with "+ ALPHABETCOORDS[twox]+","+str(twoy))

def getCoords(x, y):
    return ALPHABETCOORDS[COREWIDTH-x-1]+str(y+1)

def printRotate(core, rot1, direction):
    """ This function takes one ordinate 'rot1' and direction returns a text description of a rotation operation"""
    if(CORE_TYPE == "Full" or CORE_TYPE == "BEAVRS"):  # this only works if COREWIDTH==COREHEIGHT
        assert COREWIDTH == COREHEIGHT
        onex, oney = rot1
        twox, twoy = COREWIDTH-oney-1, onex
        threex, threey = COREWIDTH-onex-1, COREHEIGHT-oney-1
        fourx, foury = oney, COREHEIGHT - onex-1
        if direction == 1:
            print("Assembly: "+getCoords(onex,oney)+" has label: "+ core[oney][onex].label)
            print("Assembly: "+getCoords(twox, twoy)+" has label: "+ core[twoy][twox].label)
            print("Assembly: "+getCoords(threex, threey)+" has label: "+ core[threey][threex].label)
            print("Assembly: "+getCoords(fourx, foury)+" has label: "+ core[foury][fourx].label)
            print("clockwise-rotate: " + getCoords(onex,oney) +" to "+ getCoords(twox, twoy)+". "+ \
                    getCoords(twox, twoy)    +" to "+ getCoords(threex, threey)+". "+\
                    getCoords(threex, threey)+" to "+ getCoords(fourx, foury)+". "+\
                    getCoords(fourx, foury)  +" to "+ getCoords(onex,oney) )
        else:
            print("Assembly: "+getCoords(onex,oney)+" has label: "+ core[oney][onex].label)
            print("Assembly: "+getCoords(twox, twoy)+" has label: "+ core[twoy][twox].label)
            print("Assembly: "+getCoords(threex, threey)+" has label: "+ core[threey][threex].label)
            print("Assembly: "+getCoords(fourx, foury)+" has label: "+ core[foury][fourx].label)
            print("aclckwise-rotate: " + getCoords(onex,oney) +" to "+ getCoords(fourx, foury)+". "+ \
                    getCoords(twox, twoy)   +" to "+ getCoords(onex,oney)+". " + \
                    getCoords(threex, threey)+" to "+ getCoords(twox, twoy)+". "+ \
                    getCoords(fourx, foury) +" to "+ getCoords(threex, threey) )
    else:
        print("unimplemented Core rotation")
        random.choice(NA_SOUND_LIST).play()
        #exit()

def makeRotate(core, rot1, direction):
    """Carries out a rotation operation on the 'core' data"""
    if(CORE_TYPE == "Full" or CORE_TYPE == "BEAVRS"):  # this only works if COREWIDTH==COREHEIGHT
        assert COREWIDTH == COREHEIGHT
        onex, oney = rot1
        twox, twoy = COREWIDTH-oney-1, onex
        threex, threey = COREWIDTH-onex-1, COREHEIGHT-oney-1
        fourx, foury = oney, COREHEIGHT - onex-1
        core[oney][onex].moved = True
        core[twoy][twox].moved = True
        core[threey][threex].moved = True
        core[foury][fourx].moved = True
        if direction == 1:
            core[oney][onex], core[twoy][twox], core[threey][threex], core[foury][fourx] = core[foury][fourx], core[oney][onex], core[twoy][twox], core[threey][threex]
        else:
            core[oney][onex], core[twoy][twox], core[threey][threex], core[foury][fourx] = core[twoy][twox], core[threey][threex], core[foury][fourx], core[oney][onex]
    else:
        print("unimplemented Core rotation")
        random.choice(NA_SOUND_LIST).play()
        #exit()

def makeSwap(core, swap1, swap2):
    """Carries out a swap operation on the core data"""
    # This function does not check if the move is valid.
    onex, oney = swap1
    twox, twoy = swap2
    core[oney][onex].moved = True
    core[twoy][twox].moved = True
    core[oney][onex], core[twoy][twox] = core[twoy][twox], core[oney][onex]

def makeLoad(core, loadCoords, inventoryID):
    """Carries out a 'load' operation from the inventory global variable to the core data"""
    print(inventoryID)
    print(len(STORED_INVENTORY.inventoryList))
    assy = STORED_INVENTORY.removeInventoryItem(inventoryID)
    if core[loadCoords[1]][loadCoords[0]].label != "Empty":
        #retiredAssembly = copy.deepcopy(core[loadCoords[1]][loadCoords[0]])
        retiredAssemblyIdx = makeRemove(core, loadCoords)
        core[loadCoords[1]][loadCoords[0]] = assy
        core[loadCoords[1]][loadCoords[0]].moved = True;
        return ["remove", loadCoords, retiredAssemblyIdx]
    core[loadCoords[1]][loadCoords[0]] = assy
    core[loadCoords[1]][loadCoords[0]].moved = True;
    return["noMove",0,0]

def makeRemove(core, removeCoords):
    """Carries out a 'remove' operation from the core to the STORED_INVENTORY global"""
    retiredAssembly = copy.deepcopy(core[removeCoords[1]][removeCoords[0]])
    core[removeCoords[1]][removeCoords[0]]=Assembly("Empty")
    return STORED_INVENTORY.addInventoryItem(retiredAssembly, 1, EXTRACTED_ASSEMBLY_MSG +str(getCoords(removeCoords[0],removeCoords[1])))

def isValidSwap(core, swap1, swap2):
    """ Function to check if a swap operation can be carried out"""
    """ TODO: Improve this implementation - currently it just checks for blanks"""
    try:
        if core[swap1[0]][swap1[1]].label == BLANK and core[swap2[0]][swap2[1]].label == BLANK:
            pass
    except IndexError:
        return False
    if core[swap1[0]][swap1[1]].label == BLANK:
        return False
    elif core[swap2[0]][swap2[1]].label == BLANK:
        return False
    else:
        return True

def getLeftTopOfTile(tileX, tileY, coreImage="Main"):
    """ Gets the screen coordinates from the assembly coordinates for cores or inventory"""
    if coreImage == "Main":
        left = XMAIN_MARGIN + (tileX * TILESIZE) + (tileX - 1)
        top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
        return (left, top)
    elif coreImage == "Start":
        left = XSTART_MARGIN + (tileX * TILESIZE) + (tileX - 1)
        top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
        return (left, top)
    elif coreImage == "Inventory":
        left = 2*XSTART_MARGIN + (tileX * TILESIZE) + (tileX - 1) + ( (tileY//TILE_PER_COLUMN_INVENTORY) * INVENTORY_COLUMN_SIZE)
        top = 5 + YMARGIN + ((COREHEIGHT+2) * TILESIZE)  + ((tileY%TILE_PER_COLUMN_INVENTORY) * TILESIZE+2)
        return (left, top)
    else:
        print("Unknown core position requested!")
        exit()

def getSpotClicked(core, x, y, coreImage="Main"):
    """ Gets the position clicked by the mouse in assembly coordinates for a given core or inventory"""
    if coreImage == "Main":
        # from the x & y pixel coordinates, get the x & y core coordinates
        for  tileY, row in enumerate(core):
            for tileX, column in enumerate(row):
                left, top = getLeftTopOfTile(tileX, tileY, coreImage)
                tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
                if tileRect.collidepoint(x, y):
                    return (tileX, tileY)
    elif coreImage == "Inventory":
        for i, item in enumerate(STORED_INVENTORY.inventoryList):
            left, top = getLeftTopOfTile(0, i, coreImage=coreImage)
            tileRect = pygame.Rect(left, top,TILESIZE,TILESIZE)
            if tileRect.collidepoint(x, y):
                return (0, i)
    return (None, None)

def drawTile(tilex, tiley, label, adjx=0, adjy=0, color=TILECOLOR, outline=BGCOLOR, coreImage="Main"):
    """Draw an assembly in assembly coordinates tilex, tiley.  adjx and adjy are used in animations"""
    # draw a tile at core coordinates tilex and tiley, optionally a few
    # pixels over (determined by adjx and adjy)
    if len(color) == 4:
        left, top = getLeftTopOfTile(tilex, tiley, coreImage)
        pygame.draw.rect(DISPLAYSURF, outline, (left + adjx-1, top + adjy-1, TILESIZE+2, TILESIZE+2))
        pygame.draw.rect(DISPLAYSURF, color[0], (left + adjx, top + adjy, TILESIZE, TILESIZE))
        pygame.draw.rect(DISPLAYSURF, color[1], (left + adjx+TILESIZE/2, top + adjy, TILESIZE/2, TILESIZE/2))
        pygame.draw.rect(DISPLAYSURF, color[2], (left + adjx, top + adjy + TILESIZE/2, TILESIZE/2, TILESIZE/2))
        pygame.draw.rect(DISPLAYSURF, color[3], (left + adjx+TILESIZE/2, top + adjy+TILESIZE/2, TILESIZE/2, TILESIZE/2))
        textSurf = LABELFONT.render(str(label), True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)
    else:
        left, top = getLeftTopOfTile(tilex, tiley, coreImage)
        pygame.draw.rect(DISPLAYSURF, outline, (left + adjx-1, top + adjy-1, TILESIZE+2, TILESIZE+2))
        pygame.draw.rect(DISPLAYSURF, color, (left + adjx, top + adjy, TILESIZE, TILESIZE))
        textSurf = LABELFONT.render(str(label), True, TEXTCOLOR)
        textRect = textSurf.get_rect()
        textRect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
        DISPLAYSURF.blit(textSurf, textRect)

def makeText(text, color, bgcolor, top, left):
    """ A function that returns rendered text"""
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

def makeText2(text, color, bgcolor, top, left):
    """ This function differs from makeText because the Rect is fixed """
    """FIXME: Not implemented completely"""
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    #textRect = textSurf.get_rect()
    textRectwidthheight = (WINDOWWIDTH-RIGHT_MENU_POS-50, BASICFONTSIZE+6)
    #textRect.topleft = (top-3, left-3)
    textRect = Rect((top-3, left-3), textRectwidthheight)
    return (textSurf, textRect)

def drawCoreLayout(core, coreImage="Main"):
    """Given a coreImage this function renders the core data passed to it.  N.B. core must be othe type denoted by coreImage"""
    if coreImage == "Inventory":
        for i, invItem in enumerate(core.inventoryList):
            drawTile(0, i, invItem.assembly.label, 0,0, invItem.assembly.quadColor, coreImage=coreImage)
            textSurf = LABELFONT.render("x"+str(invItem.quantity)+" "+str(invItem.description), True, TEXTCOLOR)
            textRect = textSurf.get_rect()
            left, top = getLeftTopOfTile(0, i, coreImage=coreImage)
            textRect.topleft = (left + TILESIZE + XSTART_MARGIN/3 , top)
            DISPLAYSURF.blit(textSurf, textRect)
    else:
        maxX=0
        maxY=len(core)
        for  tiley, row in enumerate(core):
            maxX = len(row) if len(row)>maxX else maxX
            for tilex, column in enumerate(row):
                if core[tiley][tilex].label != BLANK and core[tiley][tilex].label != "Empty":
                    if core[tiley][tilex].moved:
                        drawTile(tilex, tiley, core[tiley][tilex].label, 0,0, core[tiley][tilex].quadColor, outline=TILEOUTLINE, coreImage=coreImage)
                    else:
                        drawTile(tilex, tiley, core[tiley][tilex].label, 0,0, core[tiley][tilex].quadColor, coreImage=coreImage)
        for tilex in range(maxX):
            drawTile(maxX -tilex-1, -1, ALPHABETCOORDS[tilex], 0, 0, BGCOLOR, coreImage=coreImage)
        for tiley in range(maxY):
            drawTile(-1, tiley, str(tiley+NUMCOORD_START_OFFSET), 0, 0, BGCOLOR, coreImage=coreImage)

        left, top = getLeftTopOfTile(0, 0, coreImage=coreImage)
        width = COREWIDTH * (TILESIZE+1)
        height = COREHEIGHT * (TILESIZE+1)
        margin = 5
        linethickness=4
        pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left-margin, top-margin, width + margin+linethickness, height + margin+linethickness), linethickness)


def drawGUI(core, startCore, inventory, message):
    """ This function draws the GUI and cores """
    DISPLAYSURF.fill(BGCOLOR)
    if message:
        textSurf, textRect = makeText(message, MESSAGECOLOR, BGCOLOR, 8, 8)
        DISPLAYSURF.blit(textSurf, textRect)
    #reload core loading
    coreTxt = BASICFONT.render(CORE_SHUFFLE_MSG, 1, DARKTEXT)
    DISPLAYSURF.blit(coreTxt, coreTxt.get_rect(bottomleft = getLeftTopOfTile(2,-1)))
    drawCoreLayout(core)
    # Discharge core loading
    exitTxt = BASICFONT.render(EXIT_LOADING_MSG, 1, DARKTEXT)
    DISPLAYSURF.blit(exitTxt, exitTxt.get_rect(bottomleft = getLeftTopOfTile(2,-1, coreImage="Start")))
    drawCoreLayout(startCore, coreImage="Start")
    #Fuel Inventory
    #box
    left, top = getLeftTopOfTile(0,COREHEIGHT+2, coreImage="Start")
    width = RIGHT_MENU_POS - 4*25#(2*COREWIDTH+2) * (TILESIZE+1) +1
    height = WINDOWHEIGHT/4.75#COREHEIGHT* (TILESIZE+1)/3.5
    margin = 5
    linethickness=4
    rect = Rect((0,0), (width + margin+linethickness, height + margin+linethickness))
    rect.bottomleft = (25, WINDOWHEIGHT-25)
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, rect, linethickness)
    #Label
    invenTxt = BASICFONT.render(INVENTORY_MSG, 1, DARKTEXT)
    DISPLAYSURF.blit(invenTxt, invenTxt.get_rect(bottomleft = rect.topleft))#   getLeftTopOfTile(2,COREHEIGHT+2, coreImage="Start")))
    drawCoreLayout(inventory, coreImage="Inventory")

    #the Checkboxes for symmetry functions
    symmetryTitle = LABELFONT.render(SYM_CHECKBOX_MSG, 1, DARKTEXT)
    DISPLAYSURF.blit(symmetryTitle, symmetryTitle.get_rect(bottomleft = SYMMETRY_LIST[0].rect.topleft))
    for box in SYMMETRY_LIST:
        box.render_checkbox()
    #dropdownbox for display symmetry
    DROPDOWNMENU.draw(DISPLAYSURF)
    DISPLAYSURF.blit(BURN_SURF, BURN_RECT)
    DISPLAYSURF.blit(REDO_SURF, REDO_RECT)
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEW_SURF, NEW_RECT)
    DISPLAYSURF.blit(SOLVE_SURF, SOLVE_RECT)

    DISPLAYSURF.blit(LOAD_INPUTS_SURF, LOAD_INPUTS_RECT)
    DISPLAYSURF.blit(LOAD_INVENT_SURF, LOAD_INVENT_RECT)
    DISPLAYSURF.blit(SAVE_SURF, SAVE_RECT)

def rotateAnimation(core, startCore, inventory, one, direction, message, animationSpeedSeconds):
    """Animate the effective rotation of assemblies. by moving quadrant"""
    animationSpeed = int(FPS/animationSpeedSeconds)
    # Note: This function does not check if the move is valid.
    #print(CORE_TYPE)
    if not(CORE_TYPE == "Full" or CORE_TYPE =="BEAVRS"):
        print("Not implemented for "+str(CORE_TYPE))
        random.choice(NA_SOUND_LIST).play()
    else:
        # four swaps = 1 rotation...
        onex, oney = one
        twox, twoy = COREWIDTH-oney-1, onex
        threex, threey = COREWIDTH-onex-1, COREHEIGHT-oney-1
        fourx, foury = oney, COREHEIGHT - onex-1

        # prepare the base surface
        drawGUI(core, startCore, inventory, message)
        baseSurf = DISPLAYSURF.copy()
        # draw a blank space over the moving tile on the baseSurf Surface.
        oneLeft, oneTop = getLeftTopOfTile(onex, oney)
        twoLeft, twoTop = getLeftTopOfTile(twox, twoy)
        threeLeft, threeTop = getLeftTopOfTile(threex, threey)
        fourLeft, fourTop = getLeftTopOfTile(fourx, foury)

        pygame.draw.rect(baseSurf, BGCOLOR, (oneLeft, oneTop, TILESIZE, TILESIZE))
        pygame.draw.rect(baseSurf, BGCOLOR, (twoLeft, twoTop, TILESIZE, TILESIZE))
        pygame.draw.rect(baseSurf, BGCOLOR, (threeLeft, threeTop, TILESIZE, TILESIZE))
        pygame.draw.rect(baseSurf, BGCOLOR, (fourLeft, fourTop, TILESIZE, TILESIZE))

        xdist = abs(onex-twox)
        ydist = abs(oney-twoy)
        dist = sqrt(xdist**2 + ydist**2) # not needed
        xdir = -(onex-twox)/dist if xdist !=0 else 0
        ydir = -(oney-twoy)/dist if ydist !=0 else 0
        frames_required = animationSpeed
        for j in range(0, int(frames_required)):
            i = j#dist * j/frames_required#dist* (j/frames_required)
            # animate the tile sliding over
            adjx = (xdir*i*dist*TILESIZE)/frames_required if xdist !=0 else 0
            adjy = (ydir*i*dist*TILESIZE)/frames_required if ydist !=0 else 0
            checkForQuit()
            DISPLAYSURF.blit(baseSurf, (0, 0))
            #
            if direction == 1:
                if core[oney][onex].label != "Empty":
                    drawTile(onex, oney, core[oney][onex].label, adjx, adjy, color=core[oney][onex].quadColor)
                if core[twoy][twox].label != "Empty":
                    drawTile(twox, twoy, core[twoy][twox].label, -1*adjy, adjx, color=core[twoy][twox].quadColor)
                if core[threey][threex].label != "Empty":
                    drawTile(threex, threey, core[threey][threex].label, -1*adjx, -1*adjy, color=core[threey][threex].quadColor)
                if core[foury][fourx].label != "Empty":
                    drawTile(fourx, foury, core[foury][fourx].label, adjy, -1*adjx, color=core[foury][fourx].quadColor)
            else:
                if core[oney][onex].label != "Empty":
                    drawTile(onex, oney, core[oney][onex].label, -1*adjy, adjx, color=core[oney][onex].quadColor)
                if core[twoy][twox].label != "Empty":
                    drawTile(twox, twoy, core[twoy][twox].label, -1*adjx, -1*adjy, color=core[twoy][twox].quadColor)
                if core[threey][threex].label != "Empty":
                    drawTile(threex, threey, core[threey][threex].label, adjy, -1*adjx, color=core[threey][threex].quadColor)
                if core[foury][fourx].label != "Empty":
                    drawTile(fourx, foury, core[foury][fourx].label, adjx, adjy, color=core[foury][fourx].quadColor)

            pygame.display.update()
            FPSCLOCK.tick(FPS)

def swapAnimation(core, startCore, inventory, one, two, message, animationSpeedSeconds):
    """Animate the swapping of assemblies from one location to another.  This can be in the core or in the inventory"""
    animationSpeed = int(FPS*animationSpeedSeconds)
    # Note: This function does not check if the move is valid.
    onex, oney = one
    twox, twoy = two
    # prepare the base surface
    drawGUI(core, startCore, inventory, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface.
    if onex == -1:
        oneLeft, oneTop = getLeftTopOfTile(onex, oney, coreImage= "Inventory")
        #convert onex and oney into approximations of screen coordinates in assembly positions..
        posOneX = -17
        posOneY = 17 + oney
    else:
        oneLeft, oneTop = getLeftTopOfTile(onex, oney)
        posOneX = onex
        posOneY = oney
    if twox == -1:
        twoLeft, twoTop = getLeftTopOfTile(twox, twoy, coreImage= "Inventory")
        posTwoX = -17
        posTwoY = 17 +twoy
    else:
        twoLeft, twoTop = getLeftTopOfTile(twox, twoy)
        posTwoX = twox
        posTwoY = twoy

    pygame.draw.rect(baseSurf, BGCOLOR, (oneLeft, oneTop, TILESIZE, TILESIZE))
    pygame.draw.rect(baseSurf, BGCOLOR, (twoLeft, twoTop, TILESIZE, TILESIZE))

    xdist = abs(posOneX-posTwoX)
    ydist = abs(posOneY-posTwoY)
    dist = sqrt(xdist**2 + ydist**2) # not needed
    xdir = -(posOneX-posTwoX)/dist if xdist !=0 else 0 # should be +/- 1 for x direction
    ydir = -(posOneY-posTwoY)/dist if ydist !=0 else 0 # should be +/- 1 for y direction
    frames_required = animationSpeed
    #print(animationSpeed)
    for j in range(0, int(frames_required)):
        i = j#dist * j/frames_required#dist* (j/frames_required)
        # animate the tile sliding over

        adjx = (xdir*i*dist*TILESIZE)/frames_required if xdist !=0 else 0
        adjy = (ydir*i*dist*TILESIZE)/frames_required if ydist !=0 else 0
        checkForQuit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        #
        if core[oney][onex].label != "Empty":
            drawTile(posOneX, posOneY, core[oney][onex].label, adjx, adjy, color=core[oney][onex].quadColor)
        if core[twoy][twox].label != "Empty":
            drawTile(posTwoX, posTwoY, core[twoy][twox].label, -1*adjx, -1*adjy, color=core[twoy][twox].quadColor)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def generateInventory(inventoryString):
    """ This function generates an invenotry object"""
    """ TODO: Enable the loading of data into this function"""
    listOfAssemblies = [Assembly("3.2",3.2),Assembly("2.4",2.4),Assembly("1.6", 1.6)]
    listOfQuantities = [30, 45, 25]
    listOfDescriptions = ["Fresh Uniform 3.2 wt/o U235","Fresh Uniform 2.4 wt/o U235","Fresh Uniform 1.6 wt/o U235"]
    if inventoryString == "Example":
        return StoredInventory(listOfAssemblies, listOfQuantities, listOfDescriptions)
    else:
        print("Error unkonwn inventory import")
        exit()

def generateNewPattern(coreString):
    """Reset the core data """
    global CORE_TYPE
    global STORED_INVENTORY
    setCoreType(coreString)
    #CORE_TYPE = coreString
    sequence = []
    core = getStartingCore()
    start = copy.deepcopy(core)
    inventory = STORED_INVENTORY
    drawGUI(core, start, inventory, '')
    pygame.display.update()
    lastMove = None
    return (core, start, sequence)

def doBurnup(mainCore, startCore, moves):
    """Burnup the core"""
    """TODO: link this code into PANTHER or other modelling programs"""
    global CYCLE_MOVE_LIST
    proceed = True
    message = ""
    for  tiley, row in enumerate(mainCore):
        for tilex, column in enumerate(row):
            if mainCore[tiley][tilex].label == "Empty":
                proceed = False
                message = EMPTY_ASSEMBLY_MSG
    if proceed:
        CYCLE_MOVE_LIST.append(moves)
        dist = 0
        maxdist =0
        for  tiley, row in enumerate(mainCore):
            #print ("dist= "+str(dist) +"max "+str(maxdist))
            for tilex, column in enumerate(row):
                if mainCore[tiley][tilex].label != BLANK and mainCore[tiley][tilex].label != "Empty":
                    posy = -2*tiley + 15.5
                    posx = -2*tilex + 15.5
                    dist = 10 * sqrt(posy*posy + posx*posx)
                    maxdist = dist if dist>maxdist else maxdist
                    r,g,b = mainCore[tiley][tilex].quadColor[0]
                    mainCore[tiley][tilex].quadColor[0]= (min(255, r + 255-dist), g*0.7, b)
                    dist = 10 * sqrt(posy*posy + (posx+1)*(posx+1))
                    r,g,b = mainCore[tiley][tilex].quadColor[1]
                    mainCore[tiley][tilex].quadColor[1]=(min(255, r + 255-dist), g*0.7, b)
                    dist = 10 * sqrt((posy+1)*(posy+1) + posx*posx)
                    r,g,b = mainCore[tiley][tilex].quadColor[2]
                    mainCore[tiley][tilex].quadColor[2]=(min(255, r + 255-dist), g*0.7, b)
                    dist = 10 * sqrt((posy+1)*(posy+1) + (posx+1)*(posx+1))
                    r,g,b = mainCore[tiley][tilex].quadColor[3]
                    mainCore[tiley][tilex].quadColor[3]=(min(255, r + 255-dist), g*0.7, b)
                    mainCore[tiley][tilex].moved = False
        exportMovesList(mainCore, moves)
        moves = []
        startCore = copy.deepcopy(mainCore)
    return mainCore, startCore, moves, message

def exportMovesList(core, moves):
    """ export a list of moves to a text file"""
    original_stdout = sys.stdout
    with open('./fuel_move_list.txt', 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print('#To reload the Core:')
        for move in moves:
            if move[0] == "swap":
                printSwap(core, move[1], move[2])
                print("swap: " )
            elif move[0] == "rotate":
                printRotate(core, move[1], move[2])
            else:
                print("unknown command in history")
    sys.stdout = original_stdout # Reset the standard output to its original value

def resetAnimation(core, startCore, moves, reverse=True):
    """Carry out moves in the moves list of moves.  This can reset the core if the 'reverse' variable is true, or can 'redo' if it is false..."""
    global STORED_INVENTORY
    # make all of the moves in allMoves in reverse
    revAllMoves = moves[:] # gets a copy of the list
    print("move list:")
    print(moves)
    if reverse:
        revAllMoves.reverse()
        rotationDir = -1
    else:
        rotationDir = 1
    print("reversed:")
    print(revAllMoves)
    for move in revAllMoves:
        if move[0] == "swap":
            swapAnimation(core, startCore, STORED_INVENTORY, move[1], move[2], RESET_MSG, animationSpeedSeconds=0.45)
            makeSwap(core, move[1], move[2])
        elif move[0] == "rotate":
            rotateAnimation(core, startCore, STORED_INVENTORY, move[1], rotationDir*move[2], RESET_MSG, animationSpeedSeconds=0.45)
            makeRotate(core, move[1], rotationDir*move[2])
        elif move[0] == "remove":
            removed = makeLoad(core, move[1], move[2])

        elif move[0] == "load":
            removedIdx = makeRemove(core, move[1])
            #print(removedIdx)
            #print(move[2])
            assert STORED_INVENTORY.inventoryList[removedIdx].assembly.isSame(STORED_INVENTORY.inventoryList[move[2]].assembly)
            STORED_INVENTORY.inventoryList[move[2]].quantity +=1
            del STORED_INVENTORY.inventoryList[removedIdx]
        else:
            print("unknown command in history")
    assert core
    if reverse:
        moves =[]
        for i, row in enumerate(core):
            for j, assy in enumerate(row):
                assy.moved = False
                #print(assy.label)
                #print(startCore[i][j].label)
                assert assy.label == startCore[i][j].label
    moves = switchLoadRemoveOrder(moves)
    return moves

def switchLoadRemoveOrder(moves):
    """Not implemented yet, function to fix the fact that a load to  location
    that already contains an assembly results in a remove then a load, this
    needs to be switched in order in the record when the reverse is kept..."""
    #TODO: implement this function - understand why things break
    pass

    return moves

if __name__ == '__main__':
    main()
