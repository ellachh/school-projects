#!/usr/bin/env python3
"""
6.101 Lab:
Mice-sleeper
"""

# import typing  # optional import
# import pprint  # optional import
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game, all_keys=False):
    """
    Prints a human-readable version of a game (provided as a dictionary)

    By default uses only "board", "dimensions", "state", "visible" keys (used
    by doctests). Setting all_keys=True shows all game keys.
    """
    if all_keys:
        keys = sorted(game)
    else:
        keys = ("board", "dimensions", "state", "visible")
        # Use only default game keys. If you modify this you will need
        # to update the docstrings in other functions!

    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mice):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mice (list): List of mouse locations as (row, column) tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows,ncolumns),mice)


def reveal_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mice (including diagonally), then recursively reveal its eight
    neighbors.  Return an integer indicating how many new squares were revealed
    in total, including neighbors, and neighbors of neighbors, and so on.

    The state of the game should be changed to 'lost' when at least one mouse
    is visible on the board, 'won' when all safe squares (squares that do not
    contain a mouse) and no mice are visible, and 'ongoing' otherwise.

    If the game is not ongoing, or if the given square has already been
    revealed, reveal_2d should not reveal any squares.

    Parameters:
       game (dict): Game state
       row (int): Where to start revealing cells (row)
       col (int): Where to start revealing cells (col)

    Returns:
       int: the number of new squares revealed

    >>> game = new_game_2d(2, 4, [(0,0), (1, 0), (1, 1)])
    >>> reveal_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, True, True]
        [False, False, True, True]
    >>> reveal_2d(game, 0, 1)
    1
    >>> dump(game)
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: won
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = new_game_2d(2, 4, [(0,0), (1, 0), (1, 1)])  # restart game
    >>> reveal_2d(game, 0, 3)
    4
    >>> reveal_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['m', 3, 1, 0]
        ['m', 'm', 1, 0]
    dimensions: (2, 4)
    state: lost
    visible:
        [True, False, True, True]
        [False, False, True, True]
    """
    return reveal_nd(game,(row,col))


def render_2d(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    'm' (mice), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mice).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored and
    all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = new_game_2d(2, 4, [(0,0), (1, 0), (1, 1)])
    >>> render_2d(game, False)
    [['_', '_', '_', '_'], ['_', '_', '_', '_']]
    >>> render_2d(game, True)
    [['m', '3', '1', ' '], ['m', 'm', '1', ' ']]
    >>> reveal_2d(game, 0, 3)
    4
    >>> render_2d(game, False)
    [['_', '_', '1', ' '], ['_', '_', '1', ' ']]
    """
    return render_nd(game,all_visible)


# N-D IMPLEMENTATION


def new_game_nd(dimensions, mice):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       dimensions (tuple): Dimensions of the board
       mice (list): mouse locations as a list of tuples, each an
                    N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, 'm'], [3, 3], [1, 1], [0, 0]]
        [['m', 3], [3, 'm'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    board = create_game_board(dimensions,mice)
    visible = create_nd_array(dimensions,False)
    return {
        'board':board,'visible':visible,'dimensions':dimensions,
        'state':'ongoing','mice':mice,'moves':0,'beds':set()
    }


#helper functions
def create_game_board(dimensions,mice):
    """
    Given game board dimensions and a list of mice, return
    a game board
    """
    board = create_nd_array(dimensions,0)
    for mouse in mice:
        set_value_nd(board,mouse,'m')
        neighbors = get_nd_neighbors(dimensions,mouse)
        for neigh in neighbors:
            num = get_value_nd(board,neigh)
            if num!='m':
                num+=1
            set_value_nd(board,neigh,num)
    return board

def create_nd_array(dimensions,value):
    """
    Given a tuple of an arbitrary number n of dimensions, create an
    nd array where every element in the array has value of the parameter
    value.
    """
    size = len(dimensions)-1
    def recurse_nd_board(dim):
        row = []
        #base case: we've reached dimension depth
        if dim==size:
            for _ in range(dimensions[dim]):
                row.append(value)
            return row
        #add the previous row to the current row dimension
        for _ in range(dimensions[dim]):
            row.append(recurse_nd_board(dim+1))
        return row
    return recurse_nd_board(0)

def get_nd_neighbors(dimensions,coordinate):
    """
    Given the dimensions of the game board(n dimension tuple) and a 
    coordinate(n dimension tuple), return a list of all neighboring
    coordinates that are in bounds.
    """
    size = len(coordinate)-1
    def recurse_neighbors(dim):
        neighbors = set()
        #base case: we've reached the nth dimension
        if dim==size:
            neighbors.add(coordinate)
            new_coord = list(coordinate)
            new_coord[dim]+=1
            #if they're in bounds, add neighbors that are +-1 of last element
            #in coordinate
            if 0<= new_coord[dim] < dimensions[dim]:
                neighbors.add(tuple(new_coord))
            new_coord[dim]-=2
            if 0<= new_coord[dim] < dimensions[dim]:
                neighbors.add(tuple(new_coord))
            return neighbors
        potentials = recurse_neighbors(dim+1)
        for coord in potentials:
            #add all +-1 of potential numbers to neighbors
            coord = list(coord)
            coord[dim]+=1
            if 0<= coord[dim] < dimensions[dim]:
                neighbors.add(tuple(coord))
            coord[dim]-=2
            if 0<= coord[dim] < dimensions[dim]:
                neighbors.add(tuple(coord))
        #also have to add back the potential neighbors to neighbors set
        return neighbors|potentials
    neighbors_list = list((recurse_neighbors(0)))
    neighbors_list.remove(coordinate)
    return neighbors_list

def get_value_nd(nd_array,coordinate):
    """
    given an N-dimensional array and a coordinate, 
    returns the value at that coordinate in the array
    """
    #board starts as the nd array
    board = nd_array
    #for each element coordinate, unpacks list at that coordinate, resets back to board
    for x in coordinate:
        board = board[x]
    return board

def set_value_nd(nd_array,coordinate,value):
    """
    given an N-dimensional array, a coordinate, and a value, 
    replaces the value at that coordinate in the array with the given value.
    """
    size = len(coordinate)-1
    def set_recurse(row,dim):
        if dim==size:
            row[coordinate[dim]] = value
            return None
        return set_recurse(row[coordinate[dim]],dim+1)
    return set_recurse(nd_array,0)

def all_coordinates(dimensions):
    """
    Given dimensions of a board(tuple), 
    returns all possible coordinates in a given board.
    """
    size = len(dimensions)-1
    def recurse_coords(dim):
        if dim==size:
            for i in range(dimensions[dim]):
                yield (i,)
        else:
            potentials = recurse_coords(dim+1)
            for coord in potentials:
                for i in range(dimensions[dim]):
                    yield (i,)+coord
    return recurse_coords(0)

#end helper functions

def reveal_nd(game, coordinates):
    """
    Recursively reveal square at coords and neighboring squares.

    Update the visible to reveal square at the given coordinates; then
    recursively reveal its neighbors, as long as coords does not contain and is
    not adjacent to a mouse.  Return a number indicating how many squares were
    revealed.  No action should be taken (and 0 should be returned) if the
    incoming state of the game is not 'ongoing', or if the given square has
    already been revealed.

    The updated state is 'lost' when at least one mouse is visible on the
    board, 'won' when all safe squares (squares that do not contain a mouse)
    and no mice are visible, and 'ongoing' otherwise.

    Parameters:
       coordinates (tuple): Where to start revealing squares

    Returns:
       int: number of squares revealed

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> reveal_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, 'm'], [3, 3], [1, 1], [0, 0]]
        [['m', 3], [3, 'm'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> reveal_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, 'm'], [3, 3], [1, 1], [0, 0]]
        [['m', 3], [3, 'm'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: lost
    visible:
        [[False, True], [False, False], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    """
    def reveal_square(coordinate):
        if coordinate in game['beds']:
            return 0
        game['moves']+=1
        #base case: stop playing if game isn't ongoing or already clicked the square
        if game['state']!='ongoing' or get_value_nd(game['visible'],coordinate):
            return 0
        #check if it's the first move and revealed square is a mouse
        if game['moves']==1 and get_value_nd(game['board'],coordinate)!=0:
            neighbors = set(get_nd_neighbors(game['dimensions'],coordinate))
            neighbors.add(coordinate)
            mice = set(game['mice'])
            random_g = random_coordinates(game['dimensions'])
            to_move = neighbors & mice #every mouse that is in neighbors/coord itself
            new_mice = list(game['mice'])
            for mouse in to_move:
                random = next(random_g)
                #keeps generating random numbers until it is a valid coordinate
                while random in neighbors or random in mice:
                    random = next(random_g)
                #remove old location and append new location
                new_mice.remove(mouse)
                new_mice.append(random)
            #create a new game board with new mice
            new_board = create_game_board(game['dimensions'],new_mice)
            game['board'] = new_board
        set_value_nd(game['visible'],coordinate,True)
        #2nd base case: revealed square is mouse: game lost
        if get_value_nd(game['board'],coordinate)=='m':
            game['state'] = 'lost'
            return 1
        revealed = 1
        #if it has no adjacent mice
        if get_value_nd(game['board'], coordinate) == 0:
            for neighbor in get_nd_neighbors(game['dimensions'], coordinate):
                if not get_value_nd(game['visible'], neighbor):
                    revealed += reveal_square(neighbor)
        #check if we have won
        if game['state']=='ongoing':
            all_coords = all_coordinates(game['dimensions'])
            won = True
            for c in all_coords:
                if get_value_nd(game['board'],c)!='m' and not get_value_nd(game['visible'],c):
                    won = False
                    break
            if won:
                game['state'] = 'won'
        return revealed
    return reveal_square(coordinates)

def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), 'm'
    (mice), ' ' (empty squares), or '1', '2', etc. (squares neighboring mice).
    The game['visible'] array indicates which squares should be visible.  If
    all_visible is True (the default is False), the game['visible'] array is
    ignored and all cells are shown.

    Parameters:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> reveal_nd(g, (0, 3, 0))
    8
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', 'm'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['m', '3'], ['3', 'm'], ['1', '1'], [' ', ' ']]]
    """
    vis = game['visible']
    board = create_nd_array(game['dimensions'],'_')
    all_coords = all_coordinates(game['dimensions'])
    for coord in all_coords:
        #render beds as b
        if not all_visible:
            if coord in game['beds']:
                set_value_nd(board,coord,'B')
                continue
        if all_visible or get_value_nd(vis,coord):
            value = get_value_nd(game['board'],coord)
            if value=='m':
                set_value_nd(board,coord,value)
            elif value > 0:
                set_value_nd(board,coord,str(value))
            else:
                set_value_nd(board,coord,' ')
    return board
#toggle beds
def toggle_bed_2d(game, row, col):
    """
    Given a square, if there is not a bed on that square, adds a bed to that square. 
    If there was a bed on a square, the toggle_bed functions should remove that bed.
    Returns True if the bed was toggled to be on, False if the bed was toggled to be off, 
    and None if the operation was attempted on an unvalid square
    """
    return toggle_bed_nd(game,(row,col))

def toggle_bed_nd(game, coordinates):
    """
    Given a square, if there is not a bed on that square, adds a bed to that square. 
    If there was a bed on a square, the toggle_bed functions should remove that bed.
    Returns True if the bed was toggled to be on, False if the bed was toggled to be off, 
    and None if the operation was attempted on an unvalid square
    """
    if game['state']!='ongoing':
        return None
    if get_value_nd(game['visible'],coordinates):
        return None
    if coordinates in game['beds']:
        game['beds'].remove(coordinates)
        return False
    game['beds'].add(coordinates)
    return True

def random_coordinates(dimensions):
    """
    Given a tuple representing the dimensions of a game board, return an
    infinite generator that yields pseudo-random coordinates within the board.
    For a given tuple of dimensions, the output sequence will always be the
    same.
    """

    def prng(state):
        # see https://en.wikipedia.org/wiki/Lehmer_random_number_generator
        while True:
            yield (state := state * 48271 % 0x7FFFFFFF) / 0x7FFFFFFF

    prng_gen = prng(sum(dimensions) + 61016101)
    for _ in zip(range(1), prng_gen):
        pass
    while True:
        yield tuple(int(dim * val) for val, dim in zip(prng_gen, dimensions))


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d or any other function you might want.  To do so,
    # comment out the above line, and uncomment the below line of code.  This
    # may be useful as you write/debug individual doctests or functions.  Also,
    # the verbose flag can be set to True to see all test results, including
    # those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # game = new_game_2d(2, 4, [(0,0), (1, 0), (1, 1)])
    # dump(game)
    # print(reveal_2d(game, 0, 3))
    # dump(game)
    # boo = create_nd_array((4,3,2),False)
    # # print(get_nd_neighbors((10, 20,3),(5, 13,0)))
    # # g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # # dump(g)
    # set_value_nd(boo,(0,0,0),True)
    # print(get_value_nd(boo,(0,0,0)))
    # g= all_coordinates((3,3,3))
    # print(len(list(g)))
    # for i in g:
    #     print(i)
    # g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # print(reveal_nd(g, (0, 3, 0)))
