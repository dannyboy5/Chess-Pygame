import pygame as p
import ChessEngine, ChessAI

width = height = 512
dimension = 8
sq_size = width // dimension
radius = sq_size // 2
cir_a = int(sq_size // 7.1)
cir_c = int(sq_size // 6.4)
max_fps = 15
images = {}

def loadImages():
    pieces = ["wp", "wr", "wn", "wb", "wq", "wk", "bp", "br", "bn", "bb", "bq", "bk"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("Chess/images/" + piece + ".png"), (sq_size, sq_size))

def main():
    p.init()
    p.display.set_caption("Chess") #sets window caption
    gameIcon = p.image.load("Chess/images/chessicon.png") #icon made by dinosoftlabs
    p.display.set_icon(gameIcon) #sets window icon
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    soundCap = p.mixer.Sound("Chess/images/PieceCapture.mp3")
    soundMov = p.mixer.Sound("Chess/images/PieceMove.mp3")
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when a move is animated
    loadImages()
    running = True
    sqSelected = () #initialize selected square
    playerClicks = [] #initialize player clicks list
    rightClicks = []
    PGN = [] #initialize PGN list
    moveList = [] #initialize list of moves for stockfish
    autoPromote = True #flag variable for pawn promotions to automatically turn to queens
    showLegalMoves = True #flag variable for showing all legal moves for the selected piece
    gameOver = False #flag variable for when the game is over
    soundOn = True #plays sounds if true
    flipBoard = False #flips board across the horizontal axis if true (False = white on bottom//True = black on bottom)
    playerW = True #if a human is playing white, set true. If AI, then false
    playerB = True #if a human is playing black, set true. If AI, then false

    while running:
        humanTurn = (gs.whiteToMove and playerW) or (not gs.whiteToMove and playerB)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if e.button == 1 or e.button == 2: #left or middle click
                    if not gameOver and humanTurn:
                        location = p.mouse.get_pos()
                        col = location[0]//sq_size
                        row = location[1]//sq_size
                        rightClicks = []
                        if sqSelected == (row, col): #user clicked same square twice
                            sqSelected = () #deselect
                            playerClicks = [] #clear player clicks
                        else:
                            sqSelected = (row, col)
                            playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                        if len(playerClicks) == 2: #after 2nd click
                            move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    '''
                                    gs.insufficientMaterial()
                                    '''
                                    if soundOn:
                                        if move.pieceCaptured == '--':
                                            p.mixer.Sound.play(soundMov)
                                        else:
                                            p.mixer.Sound.play(soundCap)
                                    rightClicks = []
                                    moveMade = True
                                    animate = True
                                    moveList.append(move.getLastMovement()) #adds last move to the moveList to be understood by stockfish api
                                    ChessAI.setStockfishPosition(moveList) #sends the movelist to Stockfish
                                    inCheck, inMate = gs.opponentCheckOrMate() #checks if the last move ended in a check or mate
                                    if inCheck:
                                        PGN.append(move.getChessNotation(check=True)) #adds last move to the PGN list with check
                                    elif inMate:
                                        PGN.append(move.getChessNotation(mate=True)) #adds last move to the PGN list with mate
                                    else:
                                        PGN.append(move.getChessNotation()) #adds last move to the PGN list
                                    #print(moveList)
                                    #print(PGN)
                                    sqSelected = () #resets user clicks
                                    playerClicks = []
                            if not moveMade:
                                playerClicks = [sqSelected]
                if e.button == 3: #right click
                    location = p.mouse.get_pos()
                    col = location[0]//sq_size
                    row = location[1]//sq_size
                    sqSelected = ()
                    sqPlan = (row, col)
                    if sqPlan in rightClicks: #user clicked square already
                        rightClicks.remove(sqPlan)
                    else:
                        rightClicks.append(sqPlan) #append click

            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE: #Pressing the "Esc" key will exit the program
                    running = False

                if e.key == p.K_h: #Pressing the "H" key will give you a list of key commands
                    print('KEY COMMANDS:\n1: Toggles the controller of WHITE between Human/Computer\n2: Toggles the controller of BLACK between Human/Computer\nQ: Auto-Promote to Queen (WIP)\nL: Show Legal Moves\nB: Print Board State\nS: Best Move from Stockfish\nP: Print PGN (WIP)\nF: Print FEN\nM: Toggle Sound\nZ: Undo Move (Works best with 2 human players)\nR: New Game\nEsc: Exit Game\n\nFor help press "H"')

                if e.key == p.K_z: #Pressing the "Z" key will undo your last move
                    if playerW and playerB: #in a 2-player game Z undoes 1 move
                        gs.undoMove()
                        rightClicks = []
                        moveMade = True
                        animate = False
                        gameOver = False
                        if PGN: #make sure there is a move to delete
                            del PGN[-1] #remove last move from the PGN list when a move is undone
                        if moveList: #make sure there is a move to delete
                            del moveList[-1] #remove last move from the PGN list when a move is undone

                if e.key == p.K_r: #reset the board when the 'R' key is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    rightClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                    gs.moveLog = []
                    PGN = []
                    moveList = []

                if e.key == p.K_s: #Pressing the "S" key will find the best move using stockfish
                    if not gameOver:
                        ChessAI.findBestStockfishMove(moveList)

                if e.key == p.K_b: #Pressing the "B" key will output an ASCII board state
                    ChessAI.outputBoard()
                
                if e.key == p.K_p: #Pressing the "P" key will output the Portable Game Notation (PGN)
                    if PGN:
                        print('PGN:')
                        print(PGN)
                
                if e.key == p.K_f: #Pressing the "F" key will output the Forsyth-Edwards Notation (FEN)
                    print('FEN:')
                    ChessAI.outputFEN()
                
                if e.key == p.K_m: #Pressing the "M" key will toggle SFX
                    soundOn = not soundOn
                    if soundOn:
                        print('Sound: ON')
                    else:
                        print('Sound: OFF')

                if e.key == p.K_1: #Pressing the "1" key will toggle the controller of White's pieces between human/AI
                    playerW = not playerW
                    if playerW:
                        print('White is now a HUMAN player')
                    else:
                        print('White is now a COMPUTER player')

                if e.key == p.K_2: #Pressing the "2" key will toggle the controller of Black's pieces between human/AI
                    playerB = not playerB
                    if playerB:
                        print('Black is now a HUMAN player')
                    else:
                        print('Black is now a COMPUTER player')

                if e.key == p.K_q: #Pressing the "Q" key will toggle the autoPromote flag off/on
                    autoPromote = not autoPromote
                    if autoPromote:
                        print('Auto-Promotion to Queen is now ON')
                    else:
                        print('Auto-Promotion to Queen is now OFF (DOESNT DO ANYTHING RIGHT NOW)')

                if e.key == p.K_l: #Pressing the "L" key will toggle the showLegalMoves flag off/on
                    showLegalMoves = not showLegalMoves
                    if showLegalMoves:
                        print('Show Legal Moves is now ON')
                    else:
                        print('Show Legal Moves is now OFF')
                
                if e.key == p.K_d: #Pressing the "D" key will let you change the stockfish difficulty
                    if not playerB or not playerW:
                        sd = int(input('Enter a number between 0 and 20: '))
                        ChessAI.changeStockfishDifficulty(sd)
                
                if e.key == p.K_u:
                    flipBoard = not flipBoard
                    print('Board flipped! WIP')


        #AI move finder
        if not gameOver and not humanTurn:
            #AIMove = ChessAI.findBestMove(gs, validMoves)
            #AIMove = ChessAI.findStockfishMove(gs, validMoves, moveList) #stockfish implementation WIP
            sf = ChessAI.stockfishMove()
            AIMove = ChessEngine.Move(sf[0], sf[1], gs.board)
            for i in range(len(validMoves)):
                if AIMove == validMoves[i]:
                    gs.makeMove(validMoves[i])
            if AIMove is None: #I think this should be 'if not AIMove:' because we are looking for an empty list
                print('no stockfish move found')
                AIMove = ChessAI.findRandomMove(validMoves)
                gs.makeMove(AIMove)
            inCheck, inMate = gs.opponentCheckOrMate() #checks if the last move ended in a check or mate
            if inCheck:
                PGN.append(AIMove.getChessNotation(check=True)) #adds last move to the PGN list with check
            elif inMate:
                PGN.append(AIMove.getChessNotation(mate=True)) #adds last move to the PGN list with mate
            else:
                PGN.append(AIMove.getChessNotation()) #adds last move to the PGN list
            moveList.append(AIMove.getLastMovement()) #adds last move to the moveList to be understood by stockfish api
            ChessAI.setStockfishPosition(moveList) #sends the movelist to Stockfish
            rightClicks = []
            moveMade = True
            animate = True

        if moveMade:
            if animate and gs.moveLog:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, validMoves, sqSelected, gs.moveLog, rightClicks, showLegalMoves)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            drawEndGameText(screen, 'Draw by stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate')

        clock.tick(max_fps)
        p.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected, moveLog, rightClicks, showLegalMoves=False):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected, moveLog, rightClicks, showLegalMoves)
    drawPieces(screen, gs.board) #draw pieces on top of those squares

def drawBoard(screen):
    global colors
    colors = [p.Color("bisque3"), p.Color("burlywood4")]
    for r in range(dimension):
        for c in range(dimension):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

def highlightSquares(screen, gs, validMoves, sqSelected, moveLog, rightClicks, showLegalMoves=False):
    #highlight recent move
    if moveLog:
        r1 = moveLog[-1].startRow
        r2 = moveLog[-1].endRow
        c1 = moveLog[-1].startCol
        c2 = moveLog[-1].endCol
        rec = p.Surface((sq_size, sq_size))
        rec.set_alpha(100) #transparency value: 0 is transparent 255 is opaque
        rec.fill(p.Color('goldenrod'))
        screen.blit(rec, (c1*sq_size, r1*sq_size))
        screen.blit(rec, (c2*sq_size, r2*sq_size))

    #Left click highlights
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #highlight selected square
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(100) #transparency value: 0 is transparent 255 is opaque
            s.fill(p.Color('goldenrod'))
            screen.blit(s, (c*sq_size, r*sq_size))
            #show valid moves
            if showLegalMoves:
                #advance squares
                adv = p.Surface((sq_size, sq_size)) #create a new black surface to draw circle on
                adv.set_colorkey('black') #everything that is 'black' is now completely transparent
                p.draw.circle(adv, 'gray25', (radius,radius), cir_a) #draw circle
                adv.set_alpha(65)
                #capture squares
                cap = p.Surface((sq_size, sq_size))
                cap.set_colorkey('black')
                p.draw.circle(cap, 'gray25', (radius,radius), radius, cir_c)
                cap.set_alpha(65)

                #blit all legal moves of the selected piece
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        if move.pieceCaptured != '--':
                            screen.blit(cap, (move.endCol*sq_size, move.endRow*sq_size))
                        else:
                            screen.blit(adv, (move.endCol*sq_size, move.endRow*sq_size))

    #right click highlights
    if rightClicks:
        for square in rightClicks:
            r, c = square
            planColors = [p.Color("salmon"), p.Color((250, 111, 96, 255))] #salmon and darkishsalmon?
            bcolor = planColors[((r+c) % 2)]
            p.draw.rect(screen, bcolor, p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

def drawPieces(screen, board):
    for r in range(dimension):
        for c in range(dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))

def animateMove(move, screen, board, clock):
    coords = [] # list of coords
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    #framesPerSquare = 5
    #frameCount = (abs(dR) + abs(dC)) * framesPerSquare #uncomment these two lines for uniform piece travel speed (animation time of moving Ra1 to Ra8 will take 7 times longer than Ra1 to Ra2)
    frameCount = 8 #uniform animation speed (animation time of moving Ra1 to Ra8 will take the same amount of time as Ra1 to Ra2)
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*sq_size, move.endRow*sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.enPassant: #enpassant moves have a different animation
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol*sq_size, enPassantRow*sq_size, sq_size, sq_size)
            screen.blit(images[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(images[move.pieceMoved], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.Font('Chess/images/coolvetica.ttf', radius)
    textObject = font.render(text, 0, p.Color('black'))
    textLocation = textObject.get_rect(center=(width/2, height/2))
    textBackground = p.Surface((textObject.get_rect().width+radius, textObject.get_rect().height+radius))
    textBackground.fill(p.Color('steelblue4')) #comment out if desired color is black (goods ones are steelblue4, olivedrab4, navyblue, darkolivegreen)
    textBackground.set_alpha(120)
    screen.blit(textBackground, textBackground.get_rect(center=(width/2, height/2)))
    textObject.set_alpha(180)
    screen.blit(textObject, textLocation)
    textObject.set_alpha(255)
    textObject = font.render(text, 0, p.Color('white'))
    screen.blit(textObject, textLocation.move(0,-3))

if __name__ == "__main__":
    main()