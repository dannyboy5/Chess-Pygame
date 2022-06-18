import random
from stockfish import Stockfish

stockfish = Stockfish("Chess/stockfish13.exe")
stockfish._start_new_game()

pieceScore = {'k': 0, 'q': 9, 'r': 5, 'b': 3, 'n': 3, 'p': 1}
checkmate = 1000
stalemate = 0
max_depth = 3

ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                "5": 3, "6": 2, "7": 1, "8": 0}
filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                "e": 4, "f": 5, "g": 6, "h": 7}

def stockfishMove():
    move = []
    sf = stockfish.get_best_move()
    coord = list(sf)
    startPOS = (ranksToRows[coord[1]], filesToCols[coord[0]])
    endPOS = (ranksToRows[coord[3]], filesToCols[coord[2]])
    move.append(startPOS)
    move.append(endPOS)
    
    return move

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

def findBestMove(gs, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    #findMoveMinMax(gs, validMoves, max_depth, gs.whiteToMove) #old minmax engine
    findMoveNegaMaxAlphaBeta(gs, validMoves, max_depth, -checkmate, checkmate, 1 if gs.whiteToMove else -1) #current best bestmove algorithm (besides stockfish)

    return nextMove

def findStockfishMove(gs, validMoves, moveList):
    global nextMove
    nextMove = None
    stockfish.set_position(moveList)
    #for move in validMoves:
    #    print(move)

    findMoveNegaMaxAlphaBeta(gs, validMoves, max_depth, -checkmate, checkmate, 1 if gs.whiteToMove else -1)
    return nextMove

def findBestStockfishMove(movelist):
    bm = stockfish.get_best_move()
    print('Best move: ' + bm)
    evaluation = stockfish.get_evaluation()
    if evaluation.get('type') == 'mate':
        print('Mate in ' + str(evaluation.get('value')))

def setStockfishPosition(movelist):
    stockfish.set_position(movelist)

def outputFEN():
    print(stockfish.get_fen_position())

def outputBoard():
    print(stockfish.get_board_visual())

def changeStockfishDifficulty(difficulty):
    if difficulty >= 0 and difficulty <= 20:
        stockfish.set_skill_level(difficulty)
        print('Difficulty set to level ' + str(difficulty))
    else:
        print('Invalid input')

def findMoveNegaMaxAlphaBeta(gs, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreboard(gs)

    #implement move ordering for efficience
    maxScore = -checkmate
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gs, nextMoves, depth-1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == max_depth:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha:
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

def scoreboard(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -checkmate
        else:
            return checkmate
    elif gs.stalemate:
        return stalemate

    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    return score

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score