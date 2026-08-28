"""
6.1010 Lab:
Snekoban Game
"""

# import json # optional import for loading test_levels
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS!


DIRECTION_VECTOR = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def make_new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    Returns: a dictionary with the name of each object mapping to a set of locations 
    of where the objects are, as well as the rows and cols of the game board
    """
    game = {}
    rows = len(level_description)
    cols = len(level_description[0])
    walls=set()
    computers = set()
    targets = set()
    for r in range(rows):
        for c in range(cols):
            items = level_description[r][c]
            if 'wall' in items: #adds location to walls
                walls.add((r,c))
            if 'computer' in items: #adds location to computers
                computers.add((r,c))
            if 'target' in items: #adds location to targets
                targets.add((r,c))
            if 'player' in items: #adds player loc to dictionary
                game['player'] = ((r,c))
    game.update({'walls':walls,'computers':computers,
    'targets':targets,'rows':rows,'cols':cols})
    return game



def victory_check(game):
    """
    Given a game representation (of the form returned from make_new_game),
    return a Boolean: True if the given game satisfies the victory condition,
    and False otherwise.
    """
    #if no computers or targets
    if game['computers'] == set() or game['targets'] == set():
        return False
    #if there is a computer at every target
    if game['computers'] == game['targets']:
        return True
    return False




def step_game(game, direction):
    """
    Given a game representation (of the form returned from make_new_game),
    return a game representation (of that same form), representing the
    updated game after running one step of the game.  The user's input is given
    by direction, which is one of the following:
        {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    vector = DIRECTION_VECTOR[direction]
    (x,y) = game['player'] #current location of player
    new_loc = ((x+vector[0],y+vector[1])) #loc we want to move to
    if new_loc in game['walls']: #if wall is blocking
        return game
    computers = game['computers'].copy()
    #move computer if there is one
    if new_loc in computers:
        computer_loc = (x+2*vector[0],y+2*vector[1])
        #if blocked by wall or another computer don't move
        if computer_loc in game['walls'] or computer_loc in computers:
            return game
        computers.add(computer_loc)
        computers.remove(new_loc)
    #move player and update game
    return {'player':new_loc, 'walls':game['walls'],'computers':computers,
    'targets':game['targets'],'rows':game['rows'],'cols':game['cols']}




def dump_game(game):
    """
    Given a game representation (of the form returned from make_new_game),
    convert it back into a level description that would be a suitable input to
    make_new_game (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    level = []
    for r in range(game['rows']):
        row = [] #list of whats in each row
        for c in range(game['cols']):
            items = [] #list of whats in each loc
            if (r,c) in game['walls']:
                items.append('wall')
                row.append(items)
                continue #a loc w/wall can't contain any other item
            if (r,c) in game['targets']:
                items.append('target')
            if (r,c) in game['computers']:
                items.append('computer')
            if (r,c) == game['player']:
                items.append('player')
            row.append(items)
        level.append(row)
    return level




def solve_puzzle(game):
    """
    Given a game representation (of the form returned from make_new_game), find
    a solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    visited = {get_hashable(game)} #all visited games
    #a list of tuples (game,[]) where game is the last visited state in the path,
    #and the list is a list of directions ex: 'up','down' leading to that game
    #from the initial game state
    agenda = [(game,[])]
    if victory_check(game):
        return []
    while agenda:
        current, moves = agenda.pop(0) #the tuple with the game state and list
        #all possible directions = neighbor states
        for d in DIRECTION_VECTOR:
            state = step_game(current,d)
            hashable = get_hashable(state)
            if hashable in visited:
                continue
            visited.add(hashable)
            if victory_check(state):
                return moves+[d] #add the direction to moves
            if state!=current:
                agenda.append((state,moves + [d]))
    return None

#helper functions for solve_puzzle

def get_hashable(game):
    """
    Given a game representation (of the form returned from make_new_game),
    Return a hashable version of the game state so that it can be addded
    to the visited set.
    """
    computers = tuple(game['computers'])
    targets = tuple(game['computers'])
    return (game["player"], computers, targets)

if __name__ == "__main__":
    broken = [
   [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]],
   [["wall"],  [],        ["computer"],  [],                   [],       ["wall"]],
   [["wall"],  [],        [],            ["target", "player"], [],       ["wall"]],
   [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]]
    ]
    working = [
   [["wall"], ["wall"], ["wall"], ["wall"],     ["wall"],   ["wall"]],
   [["wall"], [],       [],       ["target"],   ["wall"],   ["wall"]],
   [["wall"], [],       [],       ["wall"],     ["player"], ["wall"]],
   [["wall"], [],       [],       ["computer"], [],         ["wall"]],
   [["wall"], [],       [],       [],           ["wall"],   ["wall"]],
   [["wall"], ["wall"], ["wall"], ["wall"],     ["wall"],   ["wall"]]
    ]
    complete = [
   [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]],
   [["wall"],  [],        ["computer","target"],  [],          [],       ["wall"]],
   [["wall"],  [],        [],            ["player"], [],       ["wall"]],
   [["wall"],  ["wall"],  ["wall"],      ["wall"],             ["wall"], ["wall"]]
    ]
    # print(broken)
    print((make_new_game(broken)))
    print(dump_game(make_new_game(broken)))
    print(broken == dump_game(make_new_game(broken)))
    # game = make_new_game(working)
    # print(solve_puzzle(game))
    # print(make_new_game(working))
    # print(get_hashable(make_new_game(working)))
    # print(solve_puzzle(make_new_game(complete)))
