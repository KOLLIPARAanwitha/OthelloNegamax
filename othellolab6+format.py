import sys; args = sys.argv[1:]
# Anwitha Kollipara, Period 4
LIMIT_NM = 3
#9-20.3s, 10-57.4s, 11-325.2s
import random
import time

def getNextPlayer (board):
    numSymbols = len([1 for char in board if (char.lower() == 'x' or char.lower() == 'o')])
    if numSymbols % 2 == 0: token = 'x'
    else: token = 'o'
    return token

def convertMove(move):
    if not move[0].islower(): return int(move)
    col, row = move[0], move[1]
    colValue = ord(col)-97
    return colValue+(int(row)-1)*8

def getConstraintSets (rowLength):
    overallList = []
    for row in range(0, rowLength):
        overallList.append([ind for ind in range(row*rowLength, (row+1)*rowLength)])
    for column in range(0, rowLength):
        overallList.append ([ind*rowLength+column for ind in range (0, rowLength)])
    for diag in range(rowLength-1, -1, -1):
        overallList.append([7*num+diag for num in range(0, diag+1)])
    for num in range(rowLength*2-1, rowLength**2, rowLength):
        overallList.append([7*diag+num for diag in range(0, rowLength - (num//rowLength))])
    for diag in range(rowLength - 1, -1, -1):
        overallList.append([9 * num + diag for num in range(0, rowLength - diag)])
    for num in range(rowLength, rowLength**2-rowLength+1, rowLength):
        overallList.append([9*diag+num for diag in range(0, rowLength - (num//rowLength))])
    return overallList

def TwoDPrint(board, rowLength, possibleMoves):
    newBoard = ""
    for index in range(0, len(board)):
        if index in possibleMoves: newBoard += '*'
        else: newBoard += board[index]
    for row in range(0, rowLength):
        print (newBoard[row*rowLength:(row+1)*rowLength])

def printBoardScore(board):
    numX = len([1 for char in board if char == 'x'])
    numO = len([1 for char in board if char=='o'])
    print (f'{board} {numX}/{numO}')

def printMove(token, move):
    if move == -1: return
    print(f'{token} plays to {move}')

def makeMove(board, token, move):
    # print(f'Move:{move}')
    necConstraintSets = dIndextoConstraint[move] #list of constraintSets that pertain to my move index
    newBoard = [char for char in board]
    newBoard[move] = token
    opponentToken = 'ox'[token == 'o']
    for constraintSet in necConstraintSets:
        moveIndex = constraintSet.index(move)
        opponentIndices, tokenIndex = [], -1
        for index in range(moveIndex-1, -1, -1):
            if board[constraintSet[index]] == opponentToken: opponentIndices.append(constraintSet[index])
            elif board[constraintSet[index]] == token:
                tokenIndex = constraintSet[index]
                break
            else:
                opponentIndices=[]
                break
        if tokenIndex >= 0:
            for index in opponentIndices: newBoard[index] = token
        opponentIndices, tokenIndex = [], -1
        for index in range(moveIndex+1, len(constraintSet)):
            if board[constraintSet[index]] == opponentToken: opponentIndices.append(constraintSet[index])
            elif board[constraintSet[index]] == token:
                tokenIndex = constraintSet[index]
                break
            else:
                opponentIndices = []
                break
        if tokenIndex>=0:
            for ind in opponentIndices: newBoard[ind] = token
    newBoard = ''.join(newBoard)
    return newBoard

def findPossibleMoves(board, token, opponentToken):
    if (board,token) in findMoveDict: return findMoveDict[(board,token)]
    possibleMoves = []
    for constraintSet in constraintSets:
        myTokenIndex, blankTokenIndex, opponentTokensBetween, revopponentTokensBetween = 80, 80, 0, 0
        for index in constraintSet:
            if board[index].lower()==token:
                myTokenIndex, opponentTokensBetween = index, 0
                if revopponentTokensBetween>0:
                    if not blankTokenIndex in possibleMoves and blankTokenIndex<64: possibleMoves.append(blankTokenIndex)
                else: blankTokenIndex=80
            elif board[index].lower()==opponentToken:
                if myTokenIndex<64: opponentTokensBetween+=1
                if blankTokenIndex<64: revopponentTokensBetween+=1
            else:
                if opponentTokensBetween>0:
                    if not index in possibleMoves: possibleMoves.append(index)
                opponentTokensBetween, revopponentTokensBetween, myTokenIndex, blankTokenIndex = 0, 0, 80, index
    findMoveDict[(board, token)] = possibleMoves
    return possibleMoves

def occCorners (board, token): return ({index for index in {0,7,56,63} if board[index]==token})

def checkCorner (move): return (move==0 or move==7 or move==56 or move==63)

def safeEdge (board, move, token, opponentToken):
    if not checkEdge(move): return False
    if move in {1,2,3,4,5,6,57,58,59,60,61,62}:
        if (board[move-1]==opponentToken and board[move+1]==opponentToken): return True
    else:
        if (board[move-8]==opponentToken and board[move+8]==opponentToken):return True
    return False

def checkEdge (move): return (move in {1,2,3,4,5,6,8,16,24,32,40,48,57,58,59,60,61,62,15,23,31,39,47,55})

def CX(board, move, token):
    if (board[0]=='.' and move in {1,8,9}): return True
    if (board[7]=='.' and move in {6,15,14}): return True
    if (board[56] == '.' and move in {48, 49, 57}): return True
    if (board[63] == '.' and move in {54, 55, 62}): return True
    return False

def cornerConnect (board, myOccCorners, move, token, opponentToken):
    for corner in myOccCorners:
        relConstraintSets = dIndextoConstraint[corner]
        for constraintSet in relConstraintSets:
            if not move in constraintSet: continue
            moveIndex = constraintSet.index(move)
            flips = 0
            if move < corner:
                prevToken = token
                for i in range(moveIndex + 1, len(constraintSet) - 1):
                    currToken = board[constraintSet[i]]
                    if currToken=='.': flips+=2
                    elif currToken!= prevToken: flips+=1
                    if flips>1: break
                    prevToken = currToken
                if flips<=1: return True
            else:
                prevToken = board[corner]
                for i in range(1, moveIndex):
                    currToken = board[constraintSet[i]]
                    if currToken =='.': flips+=2
                    elif currToken != prevToken: flips+=1
                    if flips>1: break
                    prevToken = currToken
                if flips<=1: return True
    return False

def getPreferredMove (board, token, opponentToken, possibleMoves):
    myOccCorners = occCorners (board, token)
    toRet = possibleMoves[0]
    for move in possibleMoves:
        if checkCorner(move): return move
    for move in possibleMoves:
        isCX = CX (board, move, token)
        if not isCX and cornerConnect(board, myOccCorners, move, token, opponentToken): return move
        elif not isCX: toRet = move
    return toRet

def countEmpty(board): return board.count('.')

def alphabeta(myBoard, myToken, lowerBound, upperBound):
    eToken = 'ox'[myToken == 'o']
    pMoves = findPossibleMoves(myBoard, myToken, eToken)
    if len(pMoves) == 0:
        if myBoard.count('.')==0 or len(findPossibleMoves(myBoard, eToken, myToken)) == 0: return [myBoard.count(myToken) - myBoard.count(eToken)]
        else:
            ab = alphabeta(myBoard, eToken, -upperBound, -lowerBound)
            return([-ab[0]] + ab[1:] + [-1])
    if len(pMoves)==1:
        if myBoard.count('.')==1:
            myBoard = makeMove(myBoard, myToken, pMoves[0])
            # lowerBound, upperBound = -upperBound, -lowerBound
            return [(myBoard.count(myToken) - myBoard.count(eToken)), pMoves[0]]
            # score = -(tempBoard.count(eToken) - tempBoard.count(myToken))
            # lowerBound = score+1
            # if score > upperBound: return [score]
    best = [lowerBound-1]
    for mv in pMoves:
        nBoard = makeMove(myBoard, myToken, mv)
        ab = alphabeta(nBoard, eToken, -upperBound, -lowerBound)
        score = -ab[0]
        if score<lowerBound: continue
        if score>upperBound: return [score]
        best = ([score]+ab[1:]+[mv])
        lowerBound = score+1
    return best

def playGame(myTkn):
  board = '.' * 27 + "ox......xo" + '.' * 27
  enemyTkn = 'ox'[myTkn=='o']
  moveSeq = []
  possibleMoves = findPossibleMoves(board, myTkn, enemyTkn)
  stepcount = 1
  while True:
    if stepcount%2==1:
        if not possibleMoves:
            possibleMoves = findPossibleMoves(board, enemyTkn, myTkn)
            if possibleMoves:
                moveSeq.append(-1)
                stepcount += 1
                continue
            else: break
        move = getPreferredMove(board, myTkn, enemyTkn, possibleMoves)
        moveSeq.append(move)
        if countEmpty(board)<=LIMIT_NM:
            results = alphabeta(board, myTkn, -65, 65)
            # print(f'RESULT: {results}')
            move = results[-1]
            # print(f'Minimum score: {results[0]}; {results[1:]}')
        board = makeMove(board, myTkn, move)
        possibleMoves = findPossibleMoves(board, enemyTkn, myTkn)
    else:
        if not possibleMoves:
            possibleMoves = findPossibleMoves(board, myTkn, enemyTkn)
            if possibleMoves:
                moveSeq.append(-1)
                stepcount += 1
                continue
            else: break
        move = random.choice(possibleMoves)
        moveSeq.append(move)
        board = makeMove(board, enemyTkn, move)
        possibleMoves = findPossibleMoves(board, myTkn, enemyTkn)
    stepcount+=1
  # print(moveSeq)
  return [moveSeq, board.count(myTkn), 64-countEmpty(board)]

def runTournament(gameCnt):
    totalTokens, myTokens, gameResults, worstDict = 0,0, [], {}
    for gameIdx in range(gameCnt):
      result = playGame('xo'[gameIdx % 2])
      # print(f'Game result: {result[1] - (result[2]-result[1])}')
      gameResults.append(result[1] - (result[2]-result[1]))
      myTokens += result[1]
      totalTokens += result[2]
      worstDict[gameIdx+1] = (result[1] - (result[2]-result[1]), result[0])
    for i in range(0, 10):
        toPrint = ""
        for item in gameResults[i*10:(i+1)*10]: toPrint = toPrint + str(item) + " "
        print(toPrint)
    print(f'My token ct: {myTokens}')
    print(f'Total token ct: {totalTokens}')
    print(f'Score so far: {myTokens*100/totalTokens}%')
    print ('')
    worstGameOne = 1
    for item in worstDict:
        if worstDict[item][0]<worstDict[worstGameOne][0]: worstGameOne = item
    token = 'xo'[gameIdx % 2]
    trimV = (str(worstDict[worstGameOne][1])[1:-1]).replace(',','').replace(']','').replace('[','')
    print(f'Game {worstGameOne} as {token} => {worstDict[worstGameOne][0]}: {trimV}')
    del worstDict[worstGameOne]
    worstGameOne = 1
    for item in worstDict:
        if worstDict[item][0] < worstDict[worstGameOne][0]: worstGameOne = item
    trimV = (str(worstDict[worstGameOne][1])[1:-1]).replace(',', '').replace(']', '').replace('[', '')
    print(f'Game {worstGameOne} as {token} => {worstDict[worstGameOne][0]}: {trimV}')
    # print(worstGameOne)
    # print(f'WorstDict: {worstDict}')


def snapshot(myBoard, token, opponentToken, move):
    printMove(token, move)
    possibleMoves = findPossibleMoves(myBoard, token, opponentToken)
    if len(possibleMoves) == 0:
        token, opponentToken = opponentToken, token
        possibleMoves = findPossibleMoves(myBoard, token, opponentToken)
    TwoDPrint(myBoard, 8, possibleMoves)
    print("")
    printBoardScore(myBoard)
    if len(possibleMoves) == 0: print("No moves possible")
    else: print(f'Possible Moves for {token}: {possibleMoves}')

def individualMoveProcessing(myBoard, token, opponentToken, moves):
    # startTime = time.time()
    possibleMoves = findPossibleMoves(myBoard, token, opponentToken)
    if len(possibleMoves) == 0:
        token, opponentToken = opponentToken, token
        possibleMoves = findPossibleMoves(myBoard, token, opponentToken)
    TwoDPrint(myBoard, 8, possibleMoves)
    print("")
    printBoardScore(myBoard)
    if len(possibleMoves) == 0: print("No moves possible")
    else: print(f'Possible Moves for {token}: {possibleMoves}')

    mvPref = getPreferredMove(myBoard, token, opponentToken, possibleMoves)
    print(f'My preferred move is: {mvPref}')
    if countEmpty(myBoard) <= LIMIT_NM:
        results = alphabeta(myBoard, token, -65, 65)
        print(f'Minimum score: {results[0]}; {results[1:]}')
    for move in moves:
      if move > -1:
          myBoard = makeMove(myBoard, token, move)
          snapshot(myBoard, token, opponentToken, move)

      mvPref = getPreferredMove(myBoard, token, opponentToken, possibleMoves)
      print(f'My preferred move is: {mvPref}')
      if countEmpty(myBoard) <= LIMIT_NM:
          results = alphabeta(myBoard, token, -65, 65)
          print(f'Minimum score: {results[0]}; {results[1:]}')
      # print(f'Time: {round(time.time() - startTime, 1)}s')

def main():
    board, token, moves = "", "", []
    startTime = time.time()
    for argument in args:
        if len(argument) > 2: board = argument.lower()
        elif argument.lower() == 'x' or argument.lower() == 'o': token = argument.lower()
        else: moves.append(convertMove(argument.lower()))
    if len(board) == 0: board = '.' * 27 + "ox......xo" + '.' * 27
    if len(token) == 0: token = getNextPlayer(board)
    opponentToken = 'ox'[token == 'o']

    if not args:
        runTournament(100)
        print(f'Time: {round(time.time() - startTime, 1)}s')
        exit()
    else:
        individualMoveProcessing(board, token, opponentToken, moves)
        print(f'Time: {round(time.time() - startTime, 1)}s')

constraintSets = getConstraintSets(8)
dIndextoConstraint, findMoveDict = {}, {}
for index in range(0, 64):
    allSets = [constraintSet for constraintSet in constraintSets if index in constraintSet]
    dIndextoConstraint[index] = allSets
if __name__ == '__main__': main()
