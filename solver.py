#!/usr/bin/env python3

## AUTHOR: James Akl
## CONTACT: `james-akl@outlook.com`

from typing import List, Set, Dict  # used here for container type annotations in Python3 v3.8 and earlier.
from string import ascii_lowercase  # used here for convenience, loads the string "abcdefghijklmnopqrstuvwxyz".
import argparse                     # used here for parsing user-specified CLI arguments.
import os.path                      # used here for parsing local paths to the lookup table stored on disk.
import pickle                       # used here for storing/loading serialized lookup tables to disk.

def main() -> None:
    """Solve the subanagram search problem for the specified input and print to the CLI the results ordered by word length.

    This is performed over four steps:
        1. Parse and store the CLI arguments.
        2. If unavailable, generate the lookup table, using the specified word list.
        3. Obtain the solutions for the input, using the lookup table.
        4. Print the solution subanagrams, ordered by word length in decreasing order (longest to shortest).
    """
    # Parse and store the CLI arguments.
    args: argparse.Namespace = parse_args()
    
    # If unavailable, generate the lookup table, using the specified word list.
    if not os.path.isfile("lookup.p"):
        generate_lookup(args.listpath)
    
    # Obtain the solutions for the input, using the lookup table.
    results_unordered: Set[str] = get_results(args.input)
    
    # Print the solution subanagrams, ordered by word length in decreasing order (longest to shortest).
    print_results(args.input, results_unordered)

# For reference, auxiliary functions are listed in alphabetical order.
def generate_lookup(wordlist_path: str) -> None:
    """Write to disk the lookup table (associated with the specified word list) containing two dictionaries: `anagrams` and `vectors`.

    The input file (the word list) is read from disk and the output file (the lookup dictionaries) is written to disk.
    The generated `anagrams` dictionary maps a sorted key to its anagrams (e.g., "acr" to ["arc", "car"]).
    The generated `vectors` dictionary maps a sorted key to its letter count (e.g., "acr" to [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0]).
    **Assumption**: When reading the word list's text file, assume one word token per line.
    """
    anagrams: Dict[str, Set[str]] = dict()
    vectors: Dict[str, List[int]] = dict()
    
    # Read (from the word list) file line by line processing all contained words.
    with open(wordlist_path, 'r', encoding='UTF-8') as wordlist_file:
        word: str
        while ( word := wordlist_file.readline().rstrip() ):
            # Sort (letter-wise) each word and store in its `sorted_word` anagram.
            sorted_word: str = ''.join( sorted(word) )
        
            if sorted_word not in anagrams:
                # Create a new anagram set for an unencountered `sorted_word` key.
                anagrams[sorted_word] = set()
                # Associate each `sorted_word` anagram key with its letter count.
                vectors[sorted_word] = vectorize_word(sorted_word)
            
            # Associate each anagram word with its `sorted_word` anagram key.
            anagrams[sorted_word].add(word)
    
    wordlist_file.close()
    
    # Serialize and write to disk the two dictionaries `anagrams` and `vectors`.
    with open("lookup.p", 'wb') as lookup_file:
        pickle.dump( ( anagrams, vectors, ), lookup_file, protocol=pickle.HIGHEST_PROTOCOL )
    
    lookup_file.close()

def get_results(search_input: str) -> Set[str]:
    """Return the set containing all valid subanagrams for the search problem input string.

    The procedure is outlined as follows:
        1. Load from disk the `anagrams` and `vectors` dictionaries.
        2. Compare the vector of each `candidate` key with that of the `search_input` (here, vector means letter count).
        3. Subanagram test: A passing `candidate` key must have a count less or equal to the `search_input` for each of 26 letters.
        4. Upon passing, include (in the solution set) all anagrams associated with that passing `candidate` key.
        5. After performing this for all candidate keys, remove (from the solution set) the word identical to `search_input`.
        6. Return the solution set.
    """
    search_input = search_input.lower()
    
    anagrams: Dict[str, Set[str]] # must map a sorted key to its anagrams (e.g., "acr" to ["arc", "car"])
    vectors: Dict[str, List[int]] # must map a sorted key to its letter count (e.g., "acr" to [1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0])
    
    # Load from disk the `anagrams` and `vectors` dictionaries.
    with open("lookup.p", 'rb') as lookup_file:
        ( anagrams, vectors, ) = pickle.load(lookup_file)
    
    input_vectorized: List[int] = vectorize_word(search_input)
    results_unordered: Set[str] = set()
    
    candidate: str
    for candidate in list( anagrams.keys() ):
        candidate_vectorized: List[int] = vectors[candidate]
        
        # Subanagram test: the `candidate` key must have a less-or-equal letter count than the `search_input` for all 26 letters.
        if all( candidate_vectorized[letter] <= input_vectorized[letter] for letter in range(26) ):
            # Include (in the solution set `results_unordered`) all anagrams associated with a passing `candidate` key.
            results_unordered = results_unordered.union( anagrams[candidate] )
    
    if search_input in results_unordered:
        results_unordered.remove(search_input)
    
    return results_unordered

def parse_args() -> argparse.Namespace:
    """Return the user-specified CLI arguments in an object of type `argparse.Namespace`.

    This helper function wraps the usage of the `argparse` module.
    It creates a parser object of type `ArgumentParser`, defines the CLI arguments with their details, and returns them. 
    """
    parser: argparse.ArgumentParser
    parser = argparse.ArgumentParser()
    
    parser.add_argument("input", type=str, 
                        help="single-word string for which subanagrams are retrieved from the word list")
    parser.add_argument("-l", "--listpath", type=str, default="corncob_lowercase.txt",
                        help="word list from which subanagrams are retrieved, default: \"corncob_lowercase.txt\"")
    
    return parser.parse_args()

def print_results(search_input: str, results_unordered: Set[str]) -> None:
    """Print to the CLI the solution subanagrams ordered by word length in decreasing order (from the longest to the shortest)."""
    results_ordered: Dict[ int, List[str] ] = dict()

    word: str
    for word in results_unordered:
        word_length: int = len(word)
        
        if word_length not in results_ordered:
            results_ordered[word_length] = list()
        
        results_ordered[word_length].append(word)
    
    length: int
    for length in range( len(search_input), 1, -1 ):
        if length in results_ordered:
            print(f"{length}-LETTER SUBANAGRAMS: ", end='\n    ')
            print(*results_ordered[length], sep=",  ", end='\n\n')

def vectorize_word(word: str) -> List[int]:
    """Return a character-count list representation of the input word.

    The outputs are vectors in the 26-dimensional vector space whose basis is the lowercase Latin alphabet.
    Example: both `"abc"` and `"cab"` map to `[1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]`.
    """
    word_vectorized: List[int] = list()

    letter: str
    for letter in ascii_lowercase:
        word_vectorized.append( word.count(letter) )
    
    return word_vectorized

if __name__ == "__main__":
    main()