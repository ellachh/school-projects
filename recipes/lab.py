"""
6.101 Lab:
Recipes
"""

import pickle
import sys
# import typing # optional import
# import pprint # optional import

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary mapping each atomic food name to its cost.
    """
    atomic_dict = {}
    for type,item,amt in recipes_db:
        if type=='atomic':
            atomic_dict[item] = amt
    return atomic_dict


def compound_ingredient_possibilities(recipes_db):
    """
    Given a recipes database, a list containing compound and atomic food tuples,
    make and return a dictionary that maps each compound food name to a
    list of all the ingredient lists associated with that name.
    """
    comp_dict = {}
    for type,item,list in recipes_db:
        if type=='compound':
            comp_dict[item] = comp_dict.get(item,[])+[list]
    return comp_dict


def lowest_cost(recipes_db, food_name,forbidden = None):
    """
    Given a recipes database and the name of a food (str), return the lowest
    cost of a full recipe for the given food item or None if there is no way
    to make the food_item.
    """
    atomic = atomic_ingredient_costs(recipes_db)
    comp = compound_ingredient_possibilities(recipes_db)
    #removes forbidden ingeredients from recipe dictionaries
    if forbidden is not None:
        for forbid in forbidden:
            if forbid in atomic:
                del atomic[forbid]
            if forbid in comp:
                del comp[forbid]
    #recursive function
    def get_cost(food):
        #base case: the food is atomic
        if food in atomic:
            return atomic[food]
        #recursive step: food is made of multiple ingredients
        elif food in comp:
            costs = []
            #goes through each possible recipe in the comp food
            for recipe in comp[food]:
                sum = 0
                for item, amt in recipe:
                    cost = get_cost(item)
                    #adds item cost to sum if exists, else the whole recipe
                    #is impossible, so breaks the loop
                    if cost is not None:
                        sum+=cost*amt
                    else:
                        sum = 0
                        break
                #if recipe is possible, add its cost to list of recipe costs
                if sum!=0:
                    costs.append(sum)
            #return cheapest cost
            if costs:
                return min(costs)
            #if there are none, no recipes for this food are possible
            return None
        else:
            return None
    return get_cost(food_name)





def scaled_recipe(recipe_dict, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    return {ing:amt*n for ing,amt in recipe_dict.items()}


def add_recipes(recipe_dicts):
    """
    Given a list of recipe dictionaries that map food items to quantities,
    return a new dictionary that maps each ingredient name
    to the sum of its quantities across the given recipe dictionaries.

    For example,
        add_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    sum_recipe = {}
    for recipe in recipe_dicts:
        for ing,amt in recipe.items():
            if ing in sum_recipe:
                sum_recipe[ing]+=amt
            else:
                sum_recipe[ing] = amt
    return sum_recipe


def cheapest_flat_recipe(recipes_db, food_name,forbidden = None):
    """
    Given a recipes database and the name of a food (str), return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    atomic = atomic_ingredient_costs(recipes_db)
    comp = compound_ingredient_possibilities(recipes_db)
    #removes forbidden ingeredients from recipe dictionaries
    if forbidden is not None:
        for forbid in forbidden:
            if forbid in atomic:
                del atomic[forbid]
            if forbid in comp:
                del comp[forbid]
    #recursive function
    def get_recipe(food):
        #base case: the food is atomic
        if food in atomic:
            return {food:1}
        #recursive step: food is made of multiple ingredients
        elif food in comp:
            min_price = float('inf')
            recipes = []
            #goes through each possible recipe in the food's recipes
            for possible_rec in comp[food]:
                recipe = {}
                price = 0
                for ing,amt in possible_rec:
                    new_recipe = get_recipe(ing)
                    #if the ing exists, add its flat recipe scaled by amount to
                    #the existing recipe otherwise, move on to next ingredient
                    if new_recipe is not None:
                        recipe = add_recipes([recipe,scaled_recipe(new_recipe,amt)])
                    else:
                        recipe = {}
                        break
                #if the current recipe is possible, calculate price. if price
                #is less than min_price add it to recipes
                if recipe:
                    for item,amount in recipe.items():
                        price+=atomic[item]*amount
                    if price < min_price:
                        recipes.append(recipe)
                        min_price = price
            #if the food is able to be made with ingredients, take the cheapest
            #recipe, which will be the most recently added one.
            if recipes:
                return recipes[-1]
            return None
        else:
            return None
    return get_recipe(food_name)


def combine_recipes(nested_recipes):
    """
    Given a list of lists of recipe dictionaries, where each inner list
    represents all the recipes for a certain ingredient, compute and return a
    list of recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """
    #product takes a list of lists and returns a list of all combinations
    #of each element of each list, so that each combination has one element
    #from each list in the original input
    def product(lists):
        if not lists:
            return [[]]
        rest_product = product(lists[1:])
        return [[item] + rest for item in lists[0] for rest in rest_product]
    combinations = product(nested_recipes)
    all_combs=[]
    for comb in combinations:
        all_combs.append(add_recipes(comb))
    return all_combs

def all_flat_recipes(recipes_db, food_name,forbidden = None):
    """
    Given a recipes database, the name of a food (str), produce a list (in any
    order) of all possible flat recipe dictionaries for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic = atomic_ingredient_costs(recipes_db)
    comp = compound_ingredient_possibilities(recipes_db)
    #removes forbidden ingeredients from recipe dictionaries
    if forbidden is not None:
        for forbid in forbidden:
            if forbid in atomic:
                del atomic[forbid]
            if forbid in comp:
                del comp[forbid]
    #recursive function
    def get_recipes(food):
        #base case: the food is atomic
        if food in atomic:
            return [{food:1}]
        #recursive step: food is made of multiple ingredients
        elif food in comp:
            all_combs = []
            for recipe in comp[food]:
                #list of all ingredients that make up food
                nested = []
                for ing, amt in recipe:
                    sub_recipes = get_recipes(ing)  # get all possible recipes for this ingredient
                    scaled = [scaled_recipe(sub_recipe, amt) for sub_recipe in sub_recipes]
                    nested.append(scaled)
                # generate all combinations of these ingredient choices
                all_combs.extend(combine_recipes(nested))
            return all_combs
        else:
            return []
    return get_recipes(food_name)


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes_db = pickle.load(f)
    dairy_recipes_db2 = [
    ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'time', 10000),
    ]
    # you are free to add additional testing code here!
    # print(atomic_ingredient_costs(example_recipes_db))
    # print()
    # print(compound_ingredient_possibilities(example_recipes_db))
    # print(lowest_cost(dairy_recipes_db2, 'cheese'))
    # soup = {"carrots": 5, "celery": 3, "broth": 2,
    # "noodles": 1, "chicken": 3, "salt": 10}
    # # print(scaled_recipe(soup,3))
    # carrot_cake = {"carrots": 5, "flour": 8, "sugar": 10, "oil": 5,
    # "eggs": 4, "salt": 3}
    # bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    # recipe_dicts = [soup, carrot_cake, bread]
    # print(add_recipes(recipe_dicts))
    # cake_recipes = [{"cake": 1}, {"gluten free cake": 1}]
    # icing_recipes = [{"vanilla icing": 1}, {"cream cheese icing": 1,"sprinkles":10}]
    # topping_recipes = [{"sprinkles": 20}]
    # print(combine_recipes([cake_recipes,icing_recipes,topping_recipes]))
    # cookie_recipes_db = [
    # ('compound', 'cookie sandwich', [('cookie', 2), ('ice cream scoop', 3)]),
    # ('compound', 'cookie', [('chocolate chips', 3)]),
    # ('compound', 'cookie', [('sugar', 10)]),
    # ('atomic', 'chocolate chips', 200),
    # ('atomic', 'sugar', 5),
    # ('compound', 'ice cream scoop', [('vanilla ice cream', 1)]),
    # ('compound', 'ice cream scoop', [('chocolate ice cream', 1)]),
    # ('atomic', 'vanilla ice cream', 20),
    # ('atomic', 'chocolate ice cream', 30),
    # ]
    # print(all_flat_recipes(cookie_recipes_db, 'cookie sandwich'))
