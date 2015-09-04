# trendy module
import csv
from collections import defaultdict
from decimal import Decimal
from datetime import datetime

class trendyset:
    def __init__(self, data=None, node='default'):
        self.nodes = dict()
        if data:
            self.nodes[node] = trendynode(data) # if data is supplied...
            
    

    # function to add to an existing trendyset:
    def addMore(self, data):
        with open(data, 'rt') as csvfile:
            getRows = csv.DictReader(csvfile)
            fieldCheck = getRows.fieldnames
            if fieldCheck == self.fieldnames:
                for row in getRows:
                    for name in self.fieldnames:
                        self.databox[name].append(row[name])
            else:
                print('this isn\'t the same data. Start a new trendyset or add a new node')
    
    # This function creates nodes from a dataset using unique identifiers in a given column 
    # basically, the nodes are groups based on the given column
    def autoNode(self, field, data):
        with open(data, 'rt') as csvfile:
            getRows = csv.DictReader(csvfile)
            nameList = []
            thesenames = getRows.fieldnames
            for name in thesenames:
                if name != field:
                    nameList.append(name) # we will set each node's fieldnames to the given fields, excepting the grouping field
            for row in getRows:
                if row[field] not in self.nodes:
                    self.nodes[row[field]] = trendynode() # create a new node
                for name in nameList:
                    self.nodes[row[field]].databox[name].append(row[name])

    # Node by Date:
    def nodeByDate(self, field, data, interval='Month'):
        with open(data, 'rt') as csvfile:
            getRows = csv.DictReader(csvfile)
            if interval == 'Month':
                for row in getRows:
                    epoch = datetime.strptime(row[field], '%m/%d/%Y') # this assumes the date is formatted m/d/yyyy
                    if epoch.strftime('%b%y') not in self.nodes:
                        # Create a new node:
                        self.nodes[epoch.strftime('%b%y')] = trendynode()
                        self.nodes[epoch.strftime('%b%y')].fieldnames = getRows.fieldnames
                    for name in getRows.fieldnames:
                        self.nodes[epoch.strftime('%b%y')].databox[name].append(row[name])
                        
    # the mega command: run an analysis across all nodes (I'll need to add arg's as the available analysis grow)
    def allNodes(self, command, arg1=None, arg2=None):
        if command == 'getPhrases':
            # find frequency of phrases in ALL nodes:
            pass
        elif command == 'getKeywords':
            # search for keywords in ALL nodes and return matches:
            pass
        elif command == 'linearRegression':
            # regression analysis on ALL nodes:
            pass
        else:
            print(command + ' is not a valid analysis')
            return None
                    
#-------------------------------trendynode------------------------------#
class trendynode(trendyset):
    def __init__(self, data=None):
        self.fieldnames = []
        self.databox = defaultdict(list)
        if data:
            with open(data, 'rt') as csvfile:
                getRows = csv.DictReader(csvfile)
                self.fieldnames = getRows.fieldnames
                for row in getRows:
                    for name in self.fieldnames:
                        self.databox[name].append(row[name])

    # simple functions:
    def getCount(self):
        return len(self.databox[self.fieldnames[0]])

    # get a count of the number of records grouped by a given field:
    def getGroupFrequency(self, field):
        groups = dict()
        for thing in self.databox[field]:
            if thing in groups:
                groups[thing] += 1
            else:
                groups[thing] = 1
        return groups
                    
# this function finds the frequency of multiword phrases for the given node and field where l is the number of words in the phrase
# BUG: this seems to fail for data points with only one or two words...
    def getPhrases(self, field, l = 1):
        phrases = dict()
        prev = []
        for i in range(0,l):
            prev.append('') # initialize
        
        for thing in self.databox[field]:
            k = 0
            for i in range(0,l):
                prev[i] = '' # reset
            for stuff in thing.lower().split():
                # multiword phrases:
                for i in range(2,l):
                    if k > i:
                        phrase = stuff
                        for j in range(0,i-1):
                            phrase = prev[j] + ' ' + phrase
                        if phrase in phrases:
                            phrases[phrase] += 1
                        else:
                            phrases[phrase] = 1
                k += 1
                for j in range(l-1,-1,-1):
                    if j==0:
                        prev[j] = stuff
                    else:
                        prev[j] = prev[j-1]
        return phrases
    
    # Returns a list of keywords
    def getKeywords(self, field, ignoreON=True):
        keywords = dict()        
        if ignoreON == True:
            self.setIgnore()
            blind = self.ignore
        else:
            blind = []
        for thing in self.databox[field]:
            for stuff in thing.lower().split():
                if stuff not in blind:
                    # keywords (one word phrases)
                    if stuff in keywords:
                        keywords[stuff] += 1
                    else:
                        keywords[stuff] = 1                
        return keywords
    
    # when called, creates a list of keywords to ignore in the getPhrases function
    def setIgnore(self):
        self.ignore = ['the', 'is', 'are', 'a', 'to', 'do', 'and', 'that', 'as', 'this', 'does', '-', 'in', 'for', \
          'of', 'on', 'be', 'i', 'have', 'if', 'it', 'no', 'with', 'what', 'not', 'an', 'you', 'or', 'can', \
          'we', 'how', 'only', 'has', 'no,', 'new', 'there', 'must', 'will', 'meet', 'which', 'by', 'would', \
          'where', 'no.', 'at']                

    # returns a histogram distribution of a given field
    def getHisto(self, field, bincount=2):
        bins = dict() # this will contain the bins and frequencies such that [midpoint: frequency]
        hi = max(map(float, self.databox[field]))
        lo = min(map(float, self.databox[field]))
        dx = (hi - lo)/bincount
        for i in range(1,bincount+1):
            bins[(2*lo + dx*(2*i-1))/2] = 0
        brange = dx/2
        #  now we start to find frequencies:
        for thing in map(float, self.databox[field]):
            for stuff in bins:
                if (stuff-brange) <= thing < (stuff+brange):
                    bins[stuff] += 1
                elif thing == (stuff + brange):
                    bins[stuff] += 1
        return bins

    # Simple Linear Regression:
    def linearRegression(self, dependent, independent):
        count = len(self.databox[dependent])
        # map both variables as floats:
        dep = list(map(float, self.databox[dependent]))
        indep = list(map(float, self.databox[independent]))
        # setting up:
        sum_dep = sum(dep)
        sum_indep = sum(indep)
        sum_indep_squared = sum(map(lambda a: a * a, indep))
        sum_of_products = 0
        for i in range(count):
            sum_of_products += dep[i] * indep[i]
        # finding coefficients of y = bx + a
        a = (sum_of_products - (sum_indep * sum_dep) / count) / (sum_indep_squared - ((sum_indep ** 2) / count))
        b = (sum_dep - a * sum_indep) / count
        return a, b
        
    
