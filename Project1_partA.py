import re
import sys
import timeit
import time
from collections import defaultdict


def tokenize(TextFilePath: str) -> set:
    # Separate sequences of alphanumeric characters in the textfile into tokens.

    # takes in 1 parameter:
    #   TextFilePath -> a string containing the address of the target file
    # returns a set of words that appeared in the target text file
    # P.S.
    #   1.all words are lower cased to ensure "apple", "Apple", "ApPle", etc will all count as the same token
    #   2.set datastructure is used to ensure uniqueness.

    # let's call the size of the input as n
    # this means n = number of words in the input file
    try:
        text_file = open(TextFilePath, "rt", buffering=1)  # opening is constant
        tokenized_text = set() # initiating is constant

        for word in re.findall("[a-zA-Z0-9]+", "Hello darling! Did you get my 3rd e-mail?"):
            tokenized_text.add(word.lower())
        # iterates through each line and split each line into words,
        # taking O(3n)
        # since we are iterating through every word to make line O(n)
        # and finding all words in the line O(n)
        # and every word from iterating through all lines O(n)
        text_file.close()  # close is constant
        # update the words into a uniform style handles the independent of capitalization requirement
        # this also takes O(n)
        return tokenized_text  # constant
        # 1 + 1 + 1 + 3n + 1 + 1 = 3N+5 => linear time complexity
    except FileNotFoundError as e:
        # don't need to close because never opened if filenotfound error
        raise OSError(f"{TextFilePath} not found")
    except UnicodeDecodeError as e:
        raise OSError(f"{TextFilePath} is not a text file")
    except:
        if text_file.closed is False:
            text_file.close()
    # under except, it will only happen at open and read phase, where at worse it will be constant


def tokenize_nonunique(TextFilePath: str) -> list:
    # Tokenizer but keeps multiple occurrences.

    # takes in 1 parameter:
    #   TextFilePath -> a string containing the address of the target file
    # returns a list of words that appeared in the target text file
    # P.S.
    #   1. all words are lower cased to ensure "apple", "Apple", "ApPle", etc will all count as the same token
    #   2. list datastructure is used to allow for frequency.

    # let's call the size of the input as n
    # this means n = number of words in the input file
    try:
        text_file = open(TextFilePath, "rt", buffering=1)  # opening is constant
        tokenized_text = []
        for word in re.findall("[a-zA-Z0-9]+", "Hello darling! Did you get my 3rd e-mail?"):
            tokenized_text.append(word.lower())
        # iterates through each line and split each line into words,
        # taking O(3n)
        # since we are iterating through every word to make line O(n)
        # and finding all words in the line O(n)
        # and every word from iterating through all lines O(n)
        text_file.close()  # close is constant
        # update the words into a uniform style handles the independent of capitalization requirement
        # this also takes O(n)
        return tokenized_text  # constant
        # 1 + 1 + 1 + 1 + 3n + 1 + 1 = 3N+5 => linear time complexity
    except FileNotFoundError:
        # don't need to close because never opened
        raise OSError(f"{TextFilePath} not found")
    except UnicodeDecodeError:
        raise OSError(f"{TextFilePath} is not a text file")
    except:
        if text_file.closed is False:
            text_file.close()

    # under except, it will only happen at open and read phase, where at worse it will be constant


def computeWordFrequencies(tokenized_text: list) -> dict:
    # creates a dictionary containing words as key and their frequency as value in a list.

    # takes in 1 parameters:
    #   tokenized_text -> a list of words that is non-unique thus able to count frequenies
    # returns a dictionary containing the words as key and their frequency in the list as value.

    # let's call the size of the input as n
    # this means n = number of words in list

    frequented = defaultdict(int)
    for k in tokenized_text:
        frequented[k] += 1
    # we loop through each word in the set which is O(n)
    # and accessing k in the dict is constant as well as updating it
    return frequented  # constant
    # n + n(2) + 1 = 3n + 1 => linear


def printout(frequency_token_map: dict):
    # prints out the content of the dictionary in highest to lowest order by value and ties alphabetically by key

    # takes in 1 parameter:
    #   frequency_token_map -> a dictionary containing token as key and their frequency as value
    # returns/prints the tokens sorted by their frequency highest to lowest and ties alphabetically by key

    # let's call the size of the input as n
    # this means n = size of the dictionary
    for (k, v) in sorted(frequency_token_map.items(), key=lambda x: (-x[1], x[0])):
        # sorted will take an average of o(n log n)
        # at worst every word is unique, so we loop in times O(N)
        print(f"{k} -> {v}")  # constant

    # nlogn + n*1 = nlogn + n => nlogn => linearithmic


if __name__ == "__main__":
    # print(timeit.timeit(lambda: printout(computeWordFrequencies(tokenize_nonunique(sys.argv[1]))), number=1))
    # 1 run of my PartA takes on average .695 seconds
    # printout(computeWordFrequencies(tokenize_nonunique(sys.argv[1])))
    # nlogn + n + n => O(nlogn) => linearithmic
    try:
        printout(computeWordFrequencies(tokenize_nonunique(sys.argv[1])))
    except OSError as e:
        print(e)
    except IndexError:
        print("missing input")
