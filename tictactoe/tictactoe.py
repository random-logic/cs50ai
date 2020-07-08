"""
Tic Tac Toe Player
"""

import math

X = "X"
O = "O"
EMPTY = None


class DisplayError(Exception):
    def __init__(self, message):
        self.message = message


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    X_count = 0
    O_count = 0

    for row in board:
        for col in row:
            if col == X:
                X_count += 1
            elif col == O:
                O_count += 1
    
    if X_count - O_count == 1:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    act = set()

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                act.add((row, col))

    return act


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = initial_state()

    for row in range(len(board)):
        for col in range(len(board[row])):
            new_board[row][col] = board[row][col]

    if not board[action[0]][action[1]] == EMPTY:
        raise DisplayError("Action is not valid")

    new_board[action[0]][action[1]] = player(board)
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    
    util = utility(board)

    if util == 1:
        return X
    elif util == -1:
        return O
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    board_filled = True

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                board_filled = False

    return board_filled or not utility(board) == 0


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    winning_sets = [{(0, 0),(0, 1),(0, 2)}, {(1, 0),(1, 1),(1, 2)}, {(2, 0),(2, 1),(2, 2)},
                    {(0, 0),(1, 0),(2, 0)}, {(0, 1),(1, 1),(2, 1)}, {(0, 2),(1, 2),(2, 2)},
                    {(0, 0),(1, 1),(2, 2)}, {(0, 2),(1, 1),(2, 0)}]
    X_set = set()
    O_set = set()

    for row in range(len(board)):
        for col in range(len(board[row])):
            if (board[row][col] == X):
                X_set.add((row, col))
            elif (board[row][col] == O):
                O_set.add((row, col))

    for winning_set in winning_sets:
        if winning_set.issubset(X_set):
            return 1
        elif winning_set.issubset(O_set):
            return -1

    return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if terminal(board):
        return None

    player_move = player(board)

    best_action = None
    best_possible_number = None

    #X is maximum
    if player_move == X:
        best_possible_number = -1
        for action in actions(board):
            result_state = result(board, action)
            if terminal(result_state):
                util = utility(result_state)
            else:
                util = minimaxUtil(result_state)
            #print(util)
            if util >= best_possible_number:
                #print("util >= best possible number")
                best_action = action
                best_possible_number = util
    #O is minimum
    else:
        best_possible_number = 1
        for action in actions(board):
            result_state = result(board, action)
            if terminal(result_state):
                util = utility(result_state)
            else:
                util = minimaxUtil(result_state)
            #print(util)
            if util <= best_possible_number:
                #print("util <= best possible number")
                best_action = action
                best_possible_number = util

    return best_action

#returns maximum possible value for X or minimum possible value for O
def minimaxUtil(board):
    player_move = player(board)
    best_possible_number = None
    
    #X is maximum
    if player_move == X:
        best_possible_number = -1
        for action in actions(board):
            result_state = result(board, action)
            util = None
            if terminal(result_state):
                print(result_state[0])
                print(result_state[1])
                print(result_state[2])
                util = utility(result_state)
                print(util)
                print()
            else:
                util = minimaxUtil(result_state)
            #print(util)
            if util > best_possible_number:
                best_possible_number = util
    #O is minimum
    else:
        best_possible_number = 1
        for action in actions(board):
            result_state = result(board, action)
            util = None
            if terminal(result_state):
                print(result_state[0])
                print(result_state[1])
                print(result_state[2])
                util = utility(result_state)
                print(util)
                print()
            else:
                util = minimaxUtil(result_state)
            #print(util)
            if util < best_possible_number:
                best_possible_number = util

    return best_possible_number


#DELETE and add comments to above code
"""
PSUEDOCODE

minimax

return none if terminal board

#theory: try to make the best number the best possible
Set best_number to be 1 for X or -1 for O

foreach possible action:
    determine the best action for the other player
    if terminal state:
        determine the utility score
        if utility score is worse than the best number
            update the best number
        if best number is worst for above tree
            quit

"""


"""print(terminal([['O', 'X', 'O'],
                ['O', 'X', None],
                ['X', 'O', 'X']]))

print(actions([['O', 'X', 'O'],
                ['O', 'X', None],
                ['X', 'O', 'X']]))
"""