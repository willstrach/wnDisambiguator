from memory import *
from corpusAnalyser import *
from nltk.corpus import brown as corpus
from nltk.corpus import wordnet as wn
import random
import math

# All models to be varied will exist in this module. This makes it easier to vary
# them during experimentation


### ACTIVATION MODELS ###
def basicActivation(activation, constant):
    # Increments activation, and returns the result
    # constant is taken as input, only to prevent no. of argument errors
    # during experimentation
    return (activation + 1)

def variableActivation(activation, constant):
    # Adds constant to activation, and returns the result
    return (activation + constant)



### FORGETTING MODELS ###
def basicForget(activation, constant):
    # Decrements activation (bounded at zero), and returns the result
    # constant is taken as input, only to prevent no. of argument errors
    # during experimentation
    if activation > constant:
        return (activation - 1)
    else:
        return 0

def variableForget(activation, constant):
    # Subtracts constant from activation, and returns the result
    return (activation - constant)



### HYPERNYM MODELS ###
def basicHypernym(synset, depth, memoryController, constant):
    memoryController.activateSynset(synset, constant)
    if depth > 0:
        for hypernym in synset.hypernyms():
            basicHypernym(hypernym, depth-1, memoryController, constant)
        return
    else:
        return


def logHypernym(x, base, a, b):
    returnNum = math.log((a*(x+0.001)), base)
    returnNum = 0 - returnNum
    returnNum *= b
    return returnNum

def variableHypernym(synset, depth, memoryController):
    activationModifier = logHypernym(depth, 10, (2), (0.5))
    memoryController.activateSynset(synset, activationModifier)
    if activationModifier < 0:
        return
    else:
        for hypernym in synset.hypernyms():
            variableHypernym(hypernym, depth+1, memoryController)
        return



### DISABIGUATION MODELS ###
def hyponymSearch(synsetList, searchItem):
    # Given a list of synsets, and an item to be searched, the function traverses
    # all hyponyms of the searchItem, and returns None, if the synset can't be found,
    # else, returns the synset
    hyponymList = searchItem.hyponyms()
    if len(hyponymList) == 0:
        return None
    for item in hyponymList:
        if item in synsetList:
            return item
    for item in hyponymList:
        returnedItem = hyponymSearch(synsetList, item)
        if returnedItem is not None:
            return returnedItem
    return None

def hypernymSearch(synsetList, searchItem):
    for synset in synsetList:
        common_hypernym = synset.lowest_common_hypernyms(searchItem)[0]
        if common_hypernym.min_depth() > 4:
            return synset

def synsetFrequency(synset):
    # Given a synset, thee function sums the frequency over all its lemmas,
    # and returns the value
    outputFrequency = 0
    for lemma in synset.lemmas():
        outputFrequency += lemma.count()
    return outputFrequency

def mostLikelySynset(synsetList, blackList):
    # Given a list of synsets, this function calculates the most likely one
    # and returns it
    outputSynset = synsetList[0]
    for synset in synsetList:
        if synset in blackList:
            continue
        elif synsetFrequency(outputSynset) < synsetFrequency(synset):
            outputSynset = synset
    return outputSynset

def disambiguate(synsetList, memoryController, blackList):
    # Given the list of synsets for a word, and the memoryController,
    # disambiguate will return a single synset whichitbelieves to be correct
    # print "disambiguate"
    if len(synsetList) == 0:
        return None, False

    # Check if synset exists directly in STM
    for item in memoryController.stm.getContents():
        if item.getSynset() in blackList:
            continue
        elif item.getSynset() in synsetList:
            return item.getSynset(), True

    # Use hypernym/hypernym model for disambiguation
    for item in memoryController.stm.getContents():
        returnedSynset = hyponymSearch(synsetList, item.getSynset())
        if returnedSynset is not None:
            if returnedSynset in blackList:
                continue
            else:
                return returnedSynset, False

    # Use frequency for disambiguation
    outputSynset = mostLikelySynset(synsetList, blackList)
    if outputSynset is not None:
        return mostLikelySynset(synsetList, blackList), False
    else:
        return mostLikelySynset(synsetList, []), False
