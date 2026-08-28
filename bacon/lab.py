"""
6.101 Lab:
Bacon Number
"""

#!/usr/bin/env python3

import pickle
# import typing # optional import
# import pprint # optional import

# NO ADDITIONAL IMPORTS ALLOWED!


def transform_data(raw_data):
    '''
    Given: a list of 3 element tuples containing(actor1,actor2,film),
    Return: a tuple of a dictionary of every actor's id mapping to a set containing
    all of the actors they have acted with, and a dictionary of every film's id 
    mapping to a set of all the actors that acted in it.
    '''
    act_dict = {}
    film_dict = {}
    for (x,y,film) in raw_data:
        #if x or y not in the dictionary already, add a new key
        #if they are, just add to the set it maps to
        if x not in act_dict:
            act_dict[x] = {y}
        else:
            act_dict[x].add(y)
        if y not in act_dict:
            act_dict[y] = {x}
        else:
            act_dict[y].add(x)
        if film not in film_dict:
            film_dict[film] = {x,y}
        else:
            film_dict[film].add(x)
            film_dict[film].add(y)
    return (act_dict,film_dict)



def acted_together(transformed_data, actor_id_1, actor_id_2):
    '''
    Given: 
    Transformed_data: a tuple of a dictionary of every actor's id mapping to a 
    set containing all of the actors they have acted with, and a dictionary of 
    every film's id mapping to a set of all the actors that acted in it.
    actor_id_1 and actor_id_2: the ids of 2 actors

    Return True if they have acted with each other and False otherwise.
    '''
    #checks if actor2 is in actor1's set or if they are the same actor
    if actor_id_2 in transformed_data[0].get(actor_id_1,set()):
        return True
    if actor_id_1 == actor_id_2:
        return True
    return False


def actors_with_bacon_number(transformed_data, n):
    '''
    Given: 
    Transformed_data: a tuple of a dictionary of every actor's id mapping to a 
    set containing all of the actors they have acted with, and a dictionary of 
    every film's id mapping to a set of all the actors that acted in it.
    n: an int describing a bacon number

    Return a set of all the actor ids that have that bacon number n.
    '''
    seen_actors = {4724}
    if n == 0:
        return seen_actors
    else:
        bacon_set = set()
        # adds all actors with bacon number 1...n-1 to seen_actors
        # and bacon_set
        for _ in range(n-1):
            for a in seen_actors:
                bacon_set.update(transformed_data[0][a])
            #if they are the same without updating seen_actors
            #with bacon set, end the loop and return empty set
            if bacon_set == seen_actors:
                return set()
            seen_actors.update(bacon_set)
        #add actors with bacon number n to bacon_set
        for b in seen_actors:
            bacon_set.update(transformed_data[0][b])
        #returns the set difference of bacon_set containing actors with
        # bacon numbers 1...n
        #and seen_actors containing actors with bacon numbers 1...n-1,
        #resulting in a set with only actors of bacon number n
        return bacon_set-seen_actors


def bacon_path(transformed_data, actor_id):
    """
    Given: 
    Transformed_data: a tuple of a dictionary of every actor's id mapping to a 
    set containing all of the actors they have acted with, and a dictionary of 
    every film's id mapping to a set of all the actors that acted in it.
    actor_id: an actor we're trying to find a path to bacon to

    Return: a list of actor ids, in order, from bacon to the given actor_id. 
    """
    found = False
    bacon_number = -1
    #find bacon number of actor_id
    while found is not True:
        bacon_number+=1
        actors = actors_with_bacon_number(transformed_data,bacon_number)
        if len(actors) == 0:
            return None
        if actor_id in actors:
            found = True
    #create a bacon_path
    path = [actor_id]
    #for bacon_number-1...0, find a connection between last appended actor
    #to the path and an actor with that bacon number
    for i in reversed(range(0,bacon_number)):
        connect = actors_with_bacon_number(transformed_data,i)
        before_len = len(path)
        for a in connect:
            if path[-1] in transformed_data[0][a]:
                path.append(a)
                break
        #if nothing was appended to bacon path, no path exists
        if len(path)==before_len:
            return None
    #reverse the order of the list
    path.reverse()
    return path



def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Given: 
    Transformed_data: a tuple of a dictionary of every actor's id mapping to a 
    set containing all of the actors they have acted with, and a dictionary of 
    every film's id mapping to a set of all the actors that acted in it.
    actor_id_1: an actor we're starting at
    actor_id_2: an actor we're ending at

    Return:
    a list of actor ids connecting actor 1 with actor 2
    """
    if actor_id_1 not in transformed_data[0] or actor_id_2 not in transformed_data[0]:
        return None
    if actor_id_1==actor_id_2:
        return [actor_id_1]
    #implement path finding like in floodfill
    to_visit = [[actor_id_1]] #a list of paths to visit
    visited = {actor_id_1} #a set of all visited actors
    while to_visit:
        path = to_visit.pop(0) #current path
        current = path[-1] #current actor
        actors = transformed_data[0][current]
        if current == actor_id_2:
            return path
        for a in actors-visited:
            to_visit.append(path+[a])
            visited.add(a)
    #return path or None if actor 2 was never added to the dictionary,
    #meaning a valid path doesn't exist
    return None

def movie_path(raw_data,movie_dict,actor_1,actor_2):
    """
    Given: 
    raw data: raw data containing a list of all (a1,a2,m) where a1 is an actor, 
    a2 is another actor, and m is a movie they acted in.
    movie dict: a dictionary mapping all the movies in the database to
    their id numbers
    actor_1: the actor we start at
    actor_2: the actor we're trying to get to

    Return:
    a list of movie names that connects the two actors
    """
    #generate a path from the first actor to the second actor
    path = actor_to_actor_path(transform_data(raw_data)[0],actor_1,actor_2)
    movie_ids = []
    #going through the raw data, add a movie the i person in the list acted in
    # with the i+1 person
    for i in range(len(path)-1):
        for (a1,a2,m) in raw_data:
            if (a1 == path[i] and a2 == path[i+1]) or (a1==path[i+1] and a2 == path[i]):
                movie_ids.append(m)
                break
    movie_names = []
    #convert movie ids to movie names
    for movie in movie_ids:
        for name,m_id in zip(movie_dict.keys(),movie_dict.values()):
            if movie == m_id:
                movie_names.append(name)
    return movie_names




def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Given:
    Transformed_data: a tuple of a dictionary of every actor's id mapping to a 
    set containing all of the actors they have acted with, and a dictionary of 
    every film's id mapping to a set of all the actors that acted in it.
    actor_id_1: an actor we're starting at
    goal_test_function: a function that returns True if the actor is a valid
    ending for the path, and False otherwise

    Return:
    The shortest possible path connecting actor_id_1 to an actor that passes
    goal_test_function. Return None if one doesn't exist
    """
    #if actor 1 passes the goal test function, return itself
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    to_visit = [[actor_id_1]] #a list of paths to visit
    visited = {actor_id_1} #a set of all visited actors
    while to_visit:
        path = to_visit.pop(0) #current path
        current = path[-1] #current actor
        actors = transformed_data[0][current]
        if goal_test_function(current):
            return path
        #append all actors that we haven't visited
        #to to_visit
        for a in actors-visited:
            to_visit.append(path+[a])
            visited.add(a)
    return None


def actors_connecting_films(transformed_data, film1, film2):
    """
    Given:
    Transformed_data: a tuple of a dictionary of every actor's id mapping to a 
    set containing all of the actors they have acted with, and a dictionary of 
    every film's id mapping to a set of all the actors that acted in it.
    film1: the film to start with
    film2: the film to end with

    Return:
    a list of actors connecting the two films
    """
    film_dict = transformed_data[1]
    if film1 not in film_dict or film2 not in film_dict:
        return None
    #add a "random actor" that didn't exist in the dict before(so negative key)
    #mapping to a set of all actors that acted in film1
    transformed_data[0][-10] = film_dict[film1]
    #create function to check if actor acted in film2
    def acted_in_film2(actor):
        return actor in transformed_data[1][film2]
    #call actor path with that function, starting from the random actor
    #we created
    path = actor_path(transformed_data,-10,acted_in_film2)
    #remove the random actor from the list
    if path:
        path.pop(0)
    return path


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)
    with open("resources/names.pickle","rb") as f:
        names = pickle.load(f)
    with open("resources/tiny.pickle","rb") as f:
        tinydb = pickle.load(f)
    with open("resources/large.pickle","rb") as f:
        largedb = pickle.load(f)
    with open("resources/movies.pickle","rb") as f:
        movies = pickle.load(f)

    # print(tinydb)

    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.

    #2.2 names database
    # print(names)
    # print(names['Sisqo'])
    # print({key for key, val in zip(names.keys(),names.values()) if val == 1186515})

    #questions for acted together
    # print(acted_together(transform_data(smalldb),
    # names['Andre Wilms'],names['Richard Joseph Paul']))
    # print(acted_together(transform_data(smalldb),
    # names['Christopher Showerman'],names['Jonathan Sanders']))

    #questions for bacon number
    # bacon_6 = actors_with_bacon_number(transform_data(largedb),6)
    # print({key for key,val in zip(names.keys(),names.values()) if val in bacon_6})

    #questions for bacon path
    # path = bacon_path(transform_data(largedb),names["Alma Rayford"])
    # name_path = []
    # for a in path:
    #     for key,val in zip(names.keys(),names.values()):
    #         if val == a:
    #             name_path.append(key)
    # print(name_path)

    #questions for actor to actor path:
    # path = actor_to_actor_path(transform_data(largedb),
    # names['Winifred Westover'],names['Scarlett Johansson'])
    # name_path = []
    # for a in path:
    #     for key,val in zip(names.keys(),names.values()):
    #         if val == a:
    #             name_path.append(key)
    # print(name_path)

    #qs for movie path
    # print(movie_path(largedb,movies,names["Sean Gunn"],names["Vjeran Tin Turk"]))
