#!/usr/bin/env python

# Quine-McCluskey Calculator
# Spring 2021

import os, sys
import argparse
import math
import time

verbose = False
quiet = False

parser = argparse.ArgumentParser(description="Calculates the minimum sum-of-products and product-of-sums forms using Quine-McCluskey method for minterms and don't cares.")
parser.add_argument('-i', '--interactive', help="boot into interactive mode (default)", action="store_true")
parser.add_argument('-t', '--text', help="single logic equation to minimize, wrapped in quotes")
parser.add_argument('-f', '--file', help="read logic equations from file to minimize, equations seperated by newlines")
parser.add_argument('--verbose', help="verbose output", action="store_true")
parser.add_argument('-q', '--quiet', help="only output resulting equation", action="store_true")

def getFileContentsAsList(filename):
    try:
        file = open(filename, 'r')
    except Exception as e:
        print(e)
        exit(1)
    return list(filter(None, file.read().split('\n')))

# check if there are numbers that exist in both lists
# throw an exception with all such numbers if there are
def checkForDoubleInput(list1, list2):
    found = ""
    for i in list1:
        for j in list2:
            if i == j:
                if found == "":
                    found = str(i);
                else:
                    found += ", " + str(i)
                    if found is not None:
                        raise Exception(found + ' cannot be in both lists: ' +
                        str(list1) + ', ' + str(list2))

# parses the input text into two lists of the minterms and dont cares
# throws exceptions for incorrect formatting
def parseTextToMinterms(inText):
    origInText = inText
    minterms = []
    dontcares = []
    # remove whitespace
    inText = inText.replace(' ', '')
    # split based on plus
    inText = inText.split('+')
    # for each term, concat to correct list
    # throw exception if wrong operand in term found
    for part in inText:
        # if minterms
        if part[0] == 'm':
            if (part[1] != '(' or part[-1] != ')'):
                raise Exception('Incorrect formatting for ' +
                    origInText + ': Incorrect parenthesis for ' + part + '.')
            for i in part[2:-1].split(','):
                if int(i) < 0:
                    raise Exception('Minterms and don\'t cares must be positive: ' + str(i))
                minterms.append(int(i))
        # if dont cares
        elif part[0] == 'd':
            if (part[1] != '(' or part[-1] != ')'):
                raise Exception('Incorrect formatting for ' +
                    origInText + ': Incorrect parenthesis for ' + part + '.')
            for i in part[2:-1].split(','):
                if int(i) < 0:
                    raise Exception('Minterms and don\'t cares must be positive')
                dontcares.append(int(i))
        # throw error
        else:
            raise Exception('Incorrect formatting for ' +
                origInText + ': Unknown operand ' + part[0] + '.')
    # sort them from smallest to largest
    minterms.sort()
    dontcares.sort()
    if len(minterms) == 0:
        raise Exception('Minterms required')
    checkForDoubleInput(minterms, dontcares)
    return minterms, dontcares

# calculates the minimum number of inputs required
def calcNumInputs(list):
    return math.ceil(math.log2(max(list) + 1))

# counts the 1's in the binary representation of a number
def calcNumOnes(integer):
    return format(integer, 'b').count('1')

# converts an integer into a binary string of size numInputs
def convIntToString(integer, numInputs):
    return format(integer, str(numInputs) + 'b').replace(' ', '0')

# converts a whole list of integers into a list of strings
def convListToString(list, numInputs):
    out = []
    for i in list:
        out += [convIntToString(i, numInputs)]
    return out

# returns true if two terms differ by only one place
def differByOne(str1, str2):
    if len(str1) != len(str2):
        return False
    flag = False
    for i in range(len(str1)):
        if str1[i] != str2[i]:
            if flag:
                return False
            else:
                flag = True
    return True

# puts an 'X' in the digit shared by two terms
# returns False if they can't be combined
def combineTerms(str1, str2):
    if differByOne(str1, str2):
        out = []
        for i in range(len(str1)):
            if str1[i] != str2[i]:
                out += 'X'
            else:
                out += str1[i]
        return ''.join(out)
    return False

# given a list of terms, it will find cubes within
# the terms and returns them and a list of the
# terms not covered by the cubes
def findCubes(list):
    out = []
    unused = list.copy()
    for i in list:
        for j in list:
            result = combineTerms(i, j)
            if i < j and result != False:
                if result not in out:
                    out += [result]
                if i in unused:
                    unused.remove(i)
                if j in unused:
                    unused.remove(j)
    return out, unused

def convMintermsToMaxterms(minterms, numInputs):
    max = []
    for i in range(2**numInputs):
        max += [convIntToString(i, numInputs)]
    for i in minterms:
        if i in max:
            max.remove(i)
    return max

# returns true if a term is covered by a pi
def covered(min, pi):
    if len(min) != len(pi):
        return False
    for i in range(len(min)):
        if min[i] == '1' and pi[i] == '0':
            return False
        elif min[i] == '0' and pi[i] == '1':
            return False
    return True

# removes all terms from minterms if they're covered by a pi
def removeCovered(minterms, pis):
    uncovered = minterms.copy()
    for i in minterms:
        for j in pis:
            if covered(i, j) and i in uncovered:
                uncovered.remove(i)
    return uncovered

# converts a pi or term to sum of products form
def convPIToSOP(pi):
    out = []
    for i in range(len(pi)):
        if pi[i] == '1':
            if int(i) + 65 > 90:
                out += [chr(int(i) + 71)]
            else:
                out += [chr(int(i) + 65)]
        elif pi[i] == '0':
            if int(i) + 65 > 90:
                out += [chr(int(i) + 71) + '\'']
            else:
                out += [chr(int(i) + 65) + '\'']
    return ''.join(out)

# converts a list of pis/terms to sum of products form
# and returns a formatted string
def convListToSOP(pis):
    out = []
    for i in pis:
        out += [convPIToSOP(i)]
    if out == ['']:
        out = ['1']
    return '= ' + ' + '.join(out)

# converts a pi or term to product of sums form
def convPIToPOS(pi):
    out = []
    for i in range(len(pi)):
        if pi[i] == '1':
            if int(i) + 65 > 90:
                out += [chr(int(i) + 71) + '\'']
            else:
                out += [chr(int(i) + 65) + '\'']
        elif pi[i] == '0':
            if int(i) + 65 > 90:
                out += [chr(int(i) + 71)]
            else:
                out += [chr(int(i) + 65)]
    return ' + '.join(out)

# converts a list of pis/terms to product of sums form
# and returns a formatted string
def convListToPOS(pis):
    out = []
    for i in pis:
        out += [convPIToPOS(i)]
    if out == ['']:
        out = ['1']
    return '= (' + ')('.join(out) + ')'

# checks to see if the pis cover all the minterms,
# if not, returns the next best pi to add to the list of pis for coverage
def findLeastCost(minterms, pis):
    coverage = {}
    for i in minterms:
        current = []
        for j in pis:
            if covered(i, j) and j not in current:
                if j not in coverage:
                    coverage[j] = [i]
                else:
                    coverage[j] += [i]
    max_pi = pis[0]
    max_cost = len(coverage[pis[0]]) + pis[0].count('X')
    for i in coverage:
        if (len(coverage[i]) + i.count('X')) > max_cost:
            max_pi = i
    return max_pi

# takes in a list of minterms (as strings) and pis and returns
# the minimum number of pis with best cost to cover the minterms
def getMinimumCoverage(minterms, pis):
    essential = []
    for i in minterms:
        current = []
        for j in pis:
            if covered(i, j) and j not in current:
                current += [j]
        if len(current) == 1 and not all(item in essential for item in current):
            essential = essential + current
    uncovered = removeCovered(minterms, essential)
    uncovered_pis = [i for i in pis if i not in essential]
    while uncovered != []:
        essential += [findLeastCost(minterms, uncovered_pis)]
        uncovered_pis = [i for i in pis if i not in essential]
        uncovered = removeCovered(minterms, essential)
    return essential

# takes in a list of minterms and dontcares (as ints)
# and prints the minimized sum of product and product of sum forms
def minimize(minterms, dontcares):
    numInputs = calcNumInputs(minterms + dontcares)
    all = convListToString(minterms + dontcares, numInputs)
    all.sort()
    max = convMintermsToMaxterms(all, numInputs)
    next, unused = findCubes(all)
    pis = unused.copy()
    while next != []:
        next, unused = findCubes(next)
        pis += unused.copy()
    essential = getMinimumCoverage(convListToString(minterms, numInputs), pis)

    next_max, unused_max = findCubes(max + convListToString(dontcares, numInputs))
    pis_max = unused_max.copy()
    while next_max != []:
        next_max, unused_max = findCubes(next_max)
        pis_max += unused_max.copy()
    essential_max = getMinimumCoverage(max, pis_max)
    if (verbose):
        print("minterms:", str(convListToString(minterms, numInputs)))
        print("maxterms:", str(max))
        print("minterm essential PIs:", str(essential))
        print("maxterm essential PIs:", str(essential_max))

    print(convListToSOP(essential))
    print(convListToPOS(essential_max))
    pass

# function for handling the interactive prompt
def interactivePrompt():
    global verbose
    inText = None
    while True:
        inText = input(": ")
        if inText.lower() in ['quit', 'q', 'exit']:
            print("Goodbye!")
            exit(0)
        elif inText.lower() in ['h', 'help']:
            print("type in a logical equation made of minterms and\n"
                  "dont cares to minimize it\n"
                  "an example is: m(1,2,3,4)+d(6,7)\n"
                  "type q, quit, or exit to exit\n"
                  "type v or verbose to toggle verbose output\n")
        elif inText.lower() in ['v', 'verbose']:
            verbose = not verbose
            print("Set verbose output to", str(verbose))
        else:
            try:
                terms = parseTextToMinterms(inText)
                minimize(terms[0], terms[1])
            except Exception as e:
                print(e)
        print()

if __name__ == "__main__":
    args = parser.parse_args()

    if args.quiet:
        verbose = False
        quiet = args.quiet
    else:
        verbose = args.verbose

    if (args.interactive is False and args.text is None and args.file is None):
        args.interactive = True

    if (args.text is not None and args.file is not None):
        print("ERROR - can only parse file or text, not both")
        exit(1)

    if (not quiet):
        print('Quine-McCluskey Calculator')
        print()

    if (args.interactive):
        if (not quiet):
            print("interactive prompt")
            print()
        try:
            interactivePrompt()
        except:
            exit(0)
    elif (args.text is not None):
        if (not quiet):
            print("inline text")
            print()
            print(":", args.text)
        terms = parseTextToMinterms(args.text)
        minimize(terms[0], terms[1])
    elif (args.file is not None):
        if (not quiet):
            print("read from file")
            print()
        contents = getFileContentsAsList(args.file)
        for min in contents:
            if (not quiet):
                print(":", min)
            terms = parseTextToMinterms(min)
            minimize(terms[0], terms[1])
            print()
