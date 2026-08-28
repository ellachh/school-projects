"""
6.101 Lab:
SAT Solver
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest
import sys

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> T, F = True, False
    >>> x = satisfying_assignment([[('a', T), ('b', F), ('c', T)]])
    >>> x.get('a', None) is T or x.get('b', None) is F or x.get('c', None) is T
    True
    >>> satisfying_assignment([[('a', T)], [('a', F)]])
    """
    #base case: formula is unsolvable
    if formula is None:
        return None
    #base case 2: the formula is solved
    if not formula:
        return {}
    #finding all unit clauses
    answer = {}
    unit = {clause[0] for clause in formula if len(clause)==1}
    #if there are unit clauses
    if unit:
        var,val = unit.pop()
        #if the opposite of the unit is also a unit, formula not possible
        if (var,not val) in unit:
            return None
        answer[var] = val
        simplified = update_formula(formula, (var,val))
        if simplified is None:
            return None
        new_answer = satisfying_assignment(simplified)
        if new_answer is None:
            return None
        answer.update(new_answer)
        return answer
    #if there are no unit clauses
    else:
        var, val = formula[0][0]
        #answer must either be the value or opposite of value(True or False)
        if_val = satisfying_assignment(update_formula(formula, (var,val)))
        #check if its the value
        if if_val is not None:
            answer[var] = val
            answer.update(if_val)
            return answer
        #check if its opposite of val
        else:
            not_val = satisfying_assignment(update_formula(formula,(var,not val)))
            if not_val is not None:
                answer[var] = not val
                answer.update(not_val)
                return answer
            return None

def update_formula(formula,literal):
    """
    Given a CNF formula, returns new formula to be when the literal is
    set to the given value.
    Returns None if formula becomes impossible
    """
    var, val = literal
    new_formula = []
    for clause in formula:
        if literal in clause:
            continue  # clause is satisfied, skip
        new_clause = [lit for lit in clause if lit != (var, not val)]
        if not new_clause:
            return None
        new_formula.append(new_clause)
    return new_formula

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    one = rule_one(student_preferences)
    two = rule_two(student_preferences,room_capacities)
    three = rule_three(student_preferences,room_capacities)
    return one+two+three

def rule_one(student_preferences):
    """
    Generates a CNF formula thet guarantees every student 
    gets a room in their preference.
    """
    formula = []
    for student in student_preferences:
        clause = []
        for room in student_preferences[student]:
            clause.append((student+'_'+room,True))
        formula.append(clause)
    return formula

def rule_two(students,rooms):
    """
    Generates a CNF formula so that each student is in at most one room.
    """
    #set of rooms already paired(to avoid repeats)
    seen_pairs = set()
    formula = []
    for room1 in rooms:
        for room2 in rooms:
            #if its the same room skip
            if room1==room2:
                continue
            #if the pair has already been counted for
            if {room1,room2} in seen_pairs:
                continue
            seen_pairs.add(frozenset({room1,room2}))
            #for each pair of rooms, each student must not be in one of them
            for student in students:
                formula.append([(student+'_'+room1,False),(student+'_'+room2,False)])
    return formula

def rule_three(students,rooms):
    """
    Generates a CNF formula so that each room is at capacity
    """
    #list of all students
    stu_list = list(students.keys())
    formula = []
    for room in rooms:
        #size of groups needed to check
        n = rooms[room]+1
        groups = all_groups(n,stu_list)
        #every group of n has to have at least 1 student not in the room
        for group in groups:
            clause = []
            for student in group:
                clause.append((student+'_'+room,False))
            formula.append(clause)
    return formula

def all_groups(size,students):
    """
    Given a list of students, find all possible groups of size, size.
    Returns a list of all size n groups of students.
    """
    #base case: return groups of size 1(just each ind student)
    if size==1:
        return [(student,) for student in students]
    #base case: students is empty(hit last student in list)
    if not students:
        return students
    combs = []
    for i,student in enumerate(students):
        rest = all_groups(size-1,students[i+1:])
        for comb in rest:
            combs.append((student,)+comb)
    return combs

if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    #helper tests
    formula = [
    [('a', True), ('b', True), ('c', True)],
    [('a', False), ('f', True)],
    [('a', False), ('f', False)],
    [('d', False), ('e', True), ('a', True), ('g', True)],
    [('h', False), ('c', True), ('a', False)],
    ]
    # print(update_formula(formula,('b', True)))
    # print(update_formula(formula,('a', False)))
    # print(update_formula(formula,('d', False)))
    # print(rule_one({'Alex': {'basement', 'penthouse'},
    #                         'Blake': {'kitchen'},
    #                         'Chris': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}}))
    # print(rule_two({'Alex': {'basement', 'penthouse'},
    #                         'Blake': {'kitchen'},
    #                         'Chris': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}},
    #                        {'basement': 1,
    #                         'kitchen': 2,
    #                         'penthouse': 4}))
    # students = {'Alex': {'basement', 'penthouse'},
    #                         'Blake': {'kitchen'},
    #                         'Chris': {'basement', 'kitchen'},
    #                         'Dana': {'kitchen', 'penthouse', 'basement'}}
    # rooms = {'basement': 1,
    #                         'kitchen': 2,
    #                         'penthouse': 4}
    # # print(all_groups(3,list(students.keys())))
    # print(rule_three(students,rooms))
