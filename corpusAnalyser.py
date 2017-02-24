from memory import *
import models
from semcorReader import *
from nltk.corpus import wordnet as wn
from tqdm import tqdm

def writeStm(stmString, sentence, outputFile):
    # Writes the contents of the stm toan output file
    stmOutputFile = open(outputFile, "a")
    stmOutputFile.write("=====================")
    stmOutputFile.write("\n")
    stmOutputFile.write(stmString)
    stmOutputFile.write("\n\n")
    for word in sentence:
        for wordForm in word.getWordForm():
            stmOutputFile.write((wordForm + " "))
    stmOutputFile.write("\n")
    stmOutputFile.write("=====================")
    stmOutputFile.close()

# The following functions deal with the analysis of the input corpus.
# They are divided into corpus, paragraph, sentence and word instead
# of just using nested loops for clarity, and so that
# the contents of the memory can be altered at each of these levels

def corpusAnalyser(inputCorpus, memoryController):
    # Takes input of a corpus, which is a list of sentences
    # and loops through all sentences
    prevSentenceOne = None
    prevSentenceTwo = None
    stmOutputFile = open("stmOutputFile.txt", "w")
    stmOutputFile.close()
    for sentence in tqdm(inputCorpus):
        sentenceAnalyser(sentence, memoryController, prevSentenceTwo)
        memoryController.stm.forgetAll()
        writeStm(str(memoryController.stm), sentence, "stmOutputFile.txt")
        prevSentenceTwo = prevSentenceOne
        prevSentenceOne = sentence
    sentenceAnalyser([], memoryController, prevSentenceOne)
    sentenceAnalyser([], memoryController, prevSentenceTwo)
    return


def sentenceAnalyser(inputSentence, memoryController, prevSentenceTwo):
    # Takes input of a sentence, which is a list of words
    # and loops through all nouns
    for word in inputSentence:
        if word.getPosTag() == "NN":
            wordAnalyser(word.getWordForm()[0], memoryController)
            # memoryController.stm.activateAll(0.1)
    if prevSentenceTwo is not None:
        for word in prevSentenceTwo:
            if word.getPosTag() == "NN":
                disambiguationOutput = models.disambiguate(wn.synsets(word.getWordForm()[0], pos="n"), memoryController)
                word.setOutputSynset(disambiguationOutput[0])
                if disambiguationOutput[1] == True:
                    word.setDirectlySeen(True)

    return

def wordAnalyser(inputWord, memoryController):
    # Takes input of a word, each with a set of senses
    # and loops through all senses
    wordSenses = wn.synsets(inputWord, pos="n")
    for sense in wordSenses:
        models.variableHypernym(sense, 0.0, memoryController)
