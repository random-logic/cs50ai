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
    #Check to see if there is one more X marker compared to the O marker
    #Precondition: X always goes first and players alternates turns
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
    #Get all empty available spaces
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
    #Copy old board onto new board
    new_board = initial_state()

    for row in range(len(board)):
        for col in range(len(board[row])):
            new_board[row][col] = board[row][col]

    #Do the action on the new board
    if not board[action[0]][action[1]] == EMPTY:
        raise DisplayError("Action is not valid")

    new_board[action[0]][action[1]] = player(board)

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    #Get winner from utility
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
    #Check to see if board is filled
    board_filled = True

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                board_filled = False

    #Game is over if board is filled or there is a winner
    return board_filled or not utility(board) == 0


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    #Define what makes winning set
    winning_sets = [{(0, 0),(0, 1),(0, 2)}, {(1, 0),(1, 1),(1, 2)}, {(2, 0),(2, 1),(2, 2)},
                    {(0, 0),(1, 0),(2, 0)}, {(0, 1),(1, 1),(2, 1)}, {(0, 2),(1, 2),(2, 2)},
                    {(0, 0),(1, 1),(2, 2)}, {(0, 2),(1, 1),(2, 0)}]
    
    #Add all of the X and O marked spaces to the X and O sets
    X_set = set()
    O_set = set()

    for row in range(len(board)):
        for col in range(len(board[row])):
            if (board[row][col] == X):
                X_set.add((row, col))
            elif (board[row][col] == O):
                O_set.add((row, col))

    #Check to see if any has winning set
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

    #No optimal move if is terminal state
    if terminal(board):
        return None

    #get player move
    player_move = player(board)

    best_action = None
    best_possible_number = None

    #X wants to maximize
    if player_move == X:
        #initialize the best possible number to the worst until it is known that a better one is present
        best_possible_number = -1

        for action in actions(board):
            #get the board state after the action
            result_state = result(board, action)

            util = None

            #get winner if game is over
            if terminal(result_state):
                util = utility(result_state)
            #check what would happen after the action
            else:
                util = minimaxUtil(result_state, best_possible_number)

            #Update the best possible number and action if it applies
            if util > best_possible_number:
                best_action = action
                best_possible_number = util
    #O wants to minimize
    else:
        #initialize the best possible number to the worst until it is known that a better one is present
        best_possible_number = 1

        for action in actions(board):
            #get the board state after the action
            result_state = result(board, action)

            util = None

            #get winner if game is over
            if terminal(result_state):
                util = utility(result_state)
            #check what would happen after the action
            else:
                util = minimaxUtil(result_state, best_possible_number)

            #Update the best possible number and action if it applies
            if util < best_possible_number:
                best_action = action
                best_possible_number = util

    return best_action

#returns maximum possible value for X or minimum possible value for O
def minimaxUtil(board, parent_best_number):
    #get player move
    player_move = player(board)

    best_possible_number = None
    
    #X wants to maximize
    if player_move == X:
        #initialize the best possible number to the worst until it is known that a better one is present
        best_possible_number = -1

        for action in actions(board):
            #get the board state after the action
            result_state = result(board, action)

            util = None

            #get winner if game is over
            if terminal(result_state):
                util = utility(result_state)
            #check what would happen after the action
            else:
                util = minimaxUtil(result_state, best_possible_number)
            
            #Update the best possible number if it applies
            if util > best_possible_number:
                best_possible_number = util

                #If the parent already knows this option will end worst, it is known that the parent will NOT choose this option
                #So no need to check further
                if best_possible_number > parent_best_number:
                    break
    #O wants to minimize
    else:
        #initialize the best possible number to the worst until it is known that a better one is present
        best_possible_number = 1
        for action in actions(board):
            #get the board state after the action
            result_state = result(board, action)

            util = None

            #get winner if game is over
            if terminal(result_state):
                util = utility(result_state)
            #check what would happen after the action
            else:
                util = minimaxUtil(result_state, best_possible_number)
            
            #Update the best possible number if it applies
            if util < best_possible_number:
                best_possible_number = util
                #If the parent already knows this option will end worst, it is known that the parent will NOT choose this option
                #So no need to check further
                if best_possible_number < parent_best_number:
                    break

    return best_possible_number