"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None


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

    >>> player([[EMPTY, EMPTY, EMPTY],[EMPTY, EMPTY, EMPTY],[EMPTY, EMPTY, EMPTY]])
    'X'
    >>> player([[EMPTY, 'X', EMPTY],[EMPTY, EMPTY, EMPTY],[EMPTY, EMPTY, EMPTY]])
    'O'
    >>> player([[EMPTY, 'X', EMPTY],[EMPTY, 'X', 'O'],[EMPTY, 'O', EMPTY]])
    'X'
    """
    # If the number of X and O is the same, X moves first.
    # Otherwise O moves.

    number_of_XO = 0

    for each_row in board:
        number_of_XO += each_row.count(X) - each_row.count(O)

    return X if number_of_XO == 0 else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.

    >>> actions([[EMPTY, EMPTY, EMPTY],[EMPTY, EMPTY, EMPTY],[EMPTY, EMPTY, EMPTY]])
    {(0, 1), (1, 2), (2, 1), (0, 0), (1, 1), (2, 0), (0, 2), (2, 2), (1, 0)}
    >>> actions([[EMPTY, 'X', EMPTY],[EMPTY, EMPTY, EMPTY],[EMPTY, EMPTY, EMPTY]])
    {(1, 2), (2, 1), (0, 0), (1, 1), (2, 0), (0, 2), (2, 2), (1, 0)}
    >>> actions([[EMPTY, 'X', EMPTY],[EMPTY, 'X', 'O'],[EMPTY, 'O', EMPTY]])
    {(0, 0), (2, 0), (0, 2), (2, 2), (1, 0)}
    """
    # Improvements?
    result = set()
    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                result.add((i, j))

    return result


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Raise an error if the action is not a valid actions of the board.
    if action not in actions(board):
        raise ValueError("Not a valid action for current board!")

    new_board = copy.deepcopy(board)
    next_player = player(board)
    new_board[action[0]][action[1]] = next_player
    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.

    >>> winner([[EMPTY, 'X', EMPTY],[EMPTY, 'X', 'O'],[EMPTY, 'X', 'O']])
    'X'
    >>> winner([['O', 'O', 'O'],[EMPTY, 'X', 'O'],[EMPTY, 'X', EMPTY]])
    'O'
    >>> winner([['X', 'X', 'O'],['O', 'X', 'X'],['X', 'O', 'O']])

    """
    # If one of three columns, one of three rows, or two diagonal lines
    # have the same parttern, then that parttern is the winner.

    # Is there a better way to do so?
    for rows in board:
        if rows.count(X) == 3:
            return X
        elif rows.count(O) == 3:
            return O

    if [board[i][0] for i in range(3)].count(X) == 3 or [board[i][1] for i in range(3)].count(X) == 3 or [board[i][2] for i in range(3)].count(X) == 3:
        return X
    elif [board[i][0] for i in range(3)].count(O) == 3 or [board[i][1] for i in range(3)].count(O) == 3 or [board[i][2] for i in range(3)].count(O) == 3:
        return O

    if [board[0][0], board[1][1], board[2][2]].count(X) == 3 or [board[0][2], board[1][1], board[2][0]].count(X) == 3:
        return X
    elif [board[0][0], board[1][1], board[2][2]].count(O) == 3 or [board[0][2], board[1][1], board[2][0]].count(O) == 3:
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    >>> terminal([[EMPTY, 'X', EMPTY],[EMPTY, 'X', 'O'],[EMPTY, EMPTY, 'O']])
    False
    >>> terminal([['O', 'O', 'O'],[EMPTY, 'X', 'O'],[EMPTY, 'X', EMPTY]])
    True
    >>> terminal([['X', 'X', 'O'],['O', 'X', 'X'],['X', 'O', 'O']])
    True
    """
    # If there is no winner and an empty, then false.
    # Otherwise true.
    if winner(board) is None and EMPTY in [each_element for rows in board for each_element in rows]:
        return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    return 0


def max_value(board) -> tuple():
    if terminal(board):
        return utility(board), None

    value = -50
    optimal_move = None
    for action in actions(board):
        current_max = min_value(result(board, action))[0]
        if value < current_max:
            value = current_max
            optimal_move = action
            if value == 1:
                return value, optimal_move

    return value, optimal_move


def min_value(board):
    if terminal(board):
        return utility(board), None

    value = 50
    optimal_move = None
    for action in actions(board):
        current_min = max_value(result(board, action))[0]
        if value > current_min:
            value = current_min
            optimal_move = action
            if value == -1:
                return value, optimal_move
    return value, optimal_move


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None

    current_player = player(board)
    if current_player == X:
        return max_value(board)[1]
    else:
        return min_value(board)[1]
