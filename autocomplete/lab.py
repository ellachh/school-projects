"""
6.101 Lab:
Autocomplete
"""

# NO ADDITIONAL IMPORTS!

# import string # optional import
# import pprint # optional import
# import typing # optional import
import doctest
from text_tokenize import tokenize_sentences


class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError("key is not a string!")
        tree = self
        for letter in key:
            if letter not in tree.children:
                tree.children[letter] = PrefixTree()
            tree = tree.children[letter]
        tree.value = value

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError("key is not a string!")
        tree = self
        for letter in key:
            if letter not in tree.children:
                raise KeyError("key is not in prefix tree!")
            tree = tree.children[letter]
        if tree.value == None:
            raise KeyError("key doesn't have value")
        return tree.value

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        try:
            _ = self[key]
            return True
        except KeyError:
            return False

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        agenda = [('',self)]
        while agenda:
            key,tree = agenda.pop(0)
            if tree.value is not None:
                yield (key,tree.value)
            for letter, child in tree.children.items():
                agenda.append((key+letter,child))

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError
        if key not in self:
            raise KeyError
        self[key] = None

def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    sentences = tokenize_sentences(text)
    tree = PrefixTree()
    seen = set()
    for sentence in sentences:
        words = sentence.split()
        for word in words:
            if word not in seen:
                seen.add(word)
                tree[word] = 1
            else:
                tree[word]+=1
    return tree

def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix, str):
        raise TypeError("prefix is not a string")
    # traverse to the subtree at the prefix
    node = tree
    for letter in prefix:
        if letter not in node.children:
            return []
        node = node.children[letter]
    # collect all (suffix, value) from the subtree
    matches = [(prefix + suffix, value) for suffix, value in node]
    #sort by frequency(high to low)
    matches.sort(key=lambda x: x[1], reverse=True)
    #extract just the keys
    words = [word for word, _ in matches]
    #limit to max_count if given
    return words if max_count is None else words[:max_count]

def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    completions = autocomplete(tree, prefix, max_count)
    #if we already have enough
    if max_count is not None and len(completions) >= max_count:
        return completions[:max_count]
    suggestions = set(completions)
    edits = make_edits(tree,prefix,suggestions)
    #sort edits by frequency
    edits_freq = [(word, tree[word]) for word in edits]
    edits_sorted = sorted(edits_freq, key=lambda x: x[1], reverse=True)
    edits_only = [word for word, _ in edits_sorted]
    #combine edits with autocomplete and return correct number
    all_results = completions + edits_only
    if max_count is None:
        return all_results
    else:
        return all_results[:max_count]

def make_edits(tree,prefix,suggestions):
    edits = set()
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(prefix)):
        for c in alphabet:
            #insert
            insert = prefix[:i] + c + prefix[i:]
            if insert in tree and insert not in suggestions:
                edits.add(insert)
            #replace
            if c != prefix[i]:
                replace = prefix[:i] + c + prefix[i+1:]
                if replace in tree and replace not in suggestions:
                    edits.add(replace)
        #delete
        delete = prefix[:i] + prefix[i+1:]
        if delete in tree and delete not in suggestions:
            edits.add(delete)
        #transpose
        if i < len(prefix) - 1:
            transpose = prefix[:i]+prefix[i+1]+prefix[i]+prefix[i+2:]
            if transpose in tree and transpose not in suggestions:
                edits.add(transpose)
    return edits

def word_filter(tree, pattern):
    """
    Return set of (word, value) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    if '?' not in pattern and '*' not in pattern:
        try:
            return {(pattern,tree[pattern])}
        except:
            return set()
    results = set()
    #node is current node we're on, i is index in pattern string, and
    #word is the word we're trying to match
    def dfs(node, i, word):
        if i == len(pattern):
            #base case: we matched the entire pattern
            if node.value is not None:
                results.add((word, node.value))
            return None
        char = pattern[i]
        if char == '?':
            #match any single character — try each child
            for c, child in node.children.items():
                dfs(child, i + 1, word + c)
        elif char == '*':
            #match 0 characters; move to next pattern char
            dfs(node, i + 1, word)
            #match >=1 characters; try each child
            for c, child in node.children.items():
                dfs(child, i, word + c)
        else:
            #match specific character
            if char in node.children:
                dfs(node.children[char], i + 1, word + char)
    #start DFS from root of tree and index 0 in pattern
    dfs(tree, 0, '')
    return results

if __name__ == "__main__":
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests
    # doctest.run_docstring_examples( # runs doctests for one function
    #    PrefixTree.__getitem__,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=True
    # )
    # t = PrefixTree()
    # print(t.children)
    # t['bat'] = 7
    # print(t.children)
    with open("cities.txt", encoding="utf-8") as f:
        cities = f.read()
    with open("alice.txt", encoding="utf-8") as f:
        alice = f.read()
    with open("dracula.txt", encoding="utf-8") as f:
        dracula = f.read()
    with open("pride.txt", encoding="utf-8") as f:
        pride = f.read()
    with open("meta.txt", encoding="utf-8") as f:
        meta = f.read()
    # meta_tree = word_frequencies(meta)
    # print(autocomplete(meta_tree,'gre',6))
    # print(word_filter(meta_tree,"c*h"))
    # cities_tree = word_frequencies(cities)
    # print(word_filter(cities_tree,"r?c*t"))
    # alice_tree = word_frequencies(alice)
    # print(autocorrect(alice_tree,'hear',12))
    # pride_tree = word_frequencies(pride)
    # print(autocorrect(pride_tree,"hear"))
    dracula_tree = word_frequencies(dracula)
    length = 0
    sum = 0
    for _,val in dracula_tree:
        length+=1
        sum+=val
    print(length)
    print(sum)