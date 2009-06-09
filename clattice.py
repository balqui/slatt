#! /usr/bin/python

"""
Project: Slatt
Package: clattice
Programmers: JLB

Purpose: implement a lattice by lists of antecedents among closed itsets

Note: 
this version should always know the dataset size; however, previous versions
did not, and unknown dataset sizes were represented as size zero in field nrtr;
this, together with the test to add the empty set as a closure, is relevant 
for the correct handling of the empty set in package allattice.

Offers:
.init from dataset, but checks for existence of closure file to see if can spare the apriori call
.computing closure op
.to string method
.scale: to use ints instead of floats for support/confidence bounds
..and also for conf/width/block factor bounds in other classes
..allows one to index already-computed bases or cuts
..and also to handle the choices [0,1]-float versus percent-float transparently

ToDo:
.URGENT: THINK ABOUT mns AND mxs FOR EXTREME CASES SUCH AS EMPTYSET OR BOTTOM OR TOPS OR...
.handle the call to Borgelt's apriori on Linux
.avoid calling Borgelt's apriori if closures file already available
.be able to load only a part of the closures in the available file if desired support is higher than in the file
.review the ticking rates
..for instance: if mxs zero, option is conservative estimate minsupp-1
.is it possible to save time somehow using immpreds to compute mxn/mns?
.should become a set of closures? 
"""

from verbosity import verbosity
from slanode import slanode, str2node, set2node, auxitset
from subprocess import call
from platform import system
from math import floor

class clattice:
    """
    Lattice implemented as explicit list of closures with lists of predecessors
    Lists include all the predecessors (transitive closure)
    Initialization is from Borgelt's apriori v5 output:
      ./apriori.exe -tc -sSUPPORT -u0 -l1 -v" /%a" TRANSFILE.txt CLOSFILE.txt
    Closures expected ordered in the list (option -l1)
    CLOSFILE checked for existence under name TRANSFILE_clSUPPORTs.txt
    where SUPPORT is the integer indicating existing minimum absolute support
    Fields:
    Scale to avoid floats in supp/conf/etc
    Universe set U
    Number of closures card
    List of closures closeds
    Dictionary of closed predecessors for each closure
    Maximum and minimum supports seen (absolute integers)
    supp_percent, float in [0,100] actually used for the mining
    (may be strictly lower than minsupp actually seen)
    Number of transactions in the original dataset nrtr
    Number of different items in the original dataset nrits
    Number of item occurrences in the original dataset nrocc
    Verbosity v own or received at init
    """

    def __init__(self,supp,datasetfile="",v=None):
        "float supp in [0,1] - read from clos file or create it from dataset"
        if v==None:
            self.v = verbosity()
        else:
            self.v = v
        self.U = set([])
        self.scale = 100000
        self.closeds = []
        self.mustsort = False
        self.v.inimessg("Initializing lattice") 
        if datasetfile == "":
            self.v.messg(" with just a bottom empty closure.")
            self.addempty(0)
            self.nrocc = 0
            self.nrtr = 0
            self.nrits = 0
            self.supp_percent = 0.0
            self.card = 0
            self.maxsupp = 0
            self.minsupp = 0
            self.preds = {}
        else:
          try:
            dataset = file("%s.txt" % datasetfile)
            self.v.zero(250)
            self.v.messg("from file "+datasetfile+".txt... computing some parameters...")
            self.nrocc = 0
            self.nrtr = 0
            uset = set([])
            for line in dataset:
                self.v.tick()
                self.nrtr += 1
                for el in line.strip().split():
                    if len(el)>0:
                        self.nrocc += 1
                        uset.add(el)
            self.nrits = len(uset)
            if supp == 0:
                "apriori implementation might not work with support zero"
                self.supp_percent = 0.001
            else:
                "there remains a scale issue to look at in the clfile name"
                self.supp_percent = self.topercent(supp)
            self.v.messg("platform appears to be "+system()+"...")
            clfile = "%s_cl%2.3fs.txt" % (datasetfile,self.supp_percent)
            cmmnd = ('./apriori.exe -tc -l1 -u0 -v" /%%a" -s%2.3f %s.txt ' % (self.supp_percent,datasetfile)) + clfile
            if False:
                "ToDo: avoid calling apriori if closures file already available"
                pass
            elif system()=="Linux":
                "ToDo: make this case work - maybe try uncommenting the next line"
##                call(cmmnd,shell=True)
                self.v.errmessg("Platform "+system()+" not handled yet, sorry")
            elif system()=="Windows":
                self.v.messg("computing closures by: \n        "+cmmnd+"\n")
                call(cmmnd)
            elif system()=="CYGWIN_NT-5.1":
                self.v.messg("computing closures by: \n        "+cmmnd+"\n")
                call(cmmnd,shell=True)
            else:
                "unhandled platform - hack: artificially raise exception to go to the except clause"
                self.v.errmessg("Platform "+system()+" not handled yet, sorry")
                ff = file("NonexistentFileToRaiseAnExceptionDueToUnhandledSystem")
            self.card = 0
            self.maxsupp = 0
            self.minsupp = self.nrtr+1
            self.preds = {}
            self.v.zero(250)
            for line in file(clfile):
                "ToDo: maybe the file has lower support than desired and we do not want all closures there"
                self.v.tick()
                newnode = self.newclosure(line)
                if newnode.supp > self.maxsupp:
                    self.maxsupp = newnode.supp
                if newnode.supp != 0 and newnode.supp < self.minsupp:
                    self.minsupp = newnode.supp
            self.v.messg("...done;")
            if self.maxsupp < self.nrtr:
                "no bottom itemset, common to all transactions - hence add emtpy"
                self.addempty(self.nrtr)
                self.v.messg("adding emptyset as bottom closure;")
            if self.mustsort:
                self.v.messg("sorting...")
                self.closeds.sort()
            self.v.messg(str(self.card)+" closures found;") 
            self.v.messg("max support is "+str(self.maxsupp))
            self.v.messg("and effective absolute support threshold is "+str(self.minsupp)+
                      (", equivalent to %2.3f" % (float(self.minsupp*100)/self.nrtr)) +
                         "% of " + str(self.nrtr) + " transactions.")
          except:
            "ToDo: refine, now the catch-all makes debugging difficult"
            self.v.errmessg("Please check file " + datasetfile + ".txt is there, platform is handled, and everything else.")

    def newclosure(self,st):
        """
        append new node from string st to self.closeds
        return new node itself
        initialize its mxs and mns according to nodes already existing
        update mxs and mns values of predecessors and successors
        update the lists of predecessors of its successors
        """
        node = str2node(st)
        node.mxs = 0
        node.mns = self.nrtr
        above = []
        below = []
        for e in self.closeds:
            "list existing nodes above and below, break if a duplicate is found"
            if node < e:
                "a superset found"
                above.append(e)
                if e.supp > node.mxs: node.mxs = e.supp
            elif e < node:
                "a subset found"
                below.append(e)
                if e.supp < node.mns: 
                    node.mns = e.supp
            elif e == node:
                "repeated closure! don't return node, causes error in init"
                self.v.errmessg("Itemset from "+str(st)+" duplicated.")
                break
        else:
            "not found, correct nonduplicate node: add to closeds and to preds lists above"
            self.closeds.append(node)
            self.U.update(node)
            self.card += 1
            self.preds[node] = []
            if len(above)>0:
                "closures in file not in order"
                self.v.errmessg("[Warning] Closure "+st+" is a predecessor of earlier nodes")
                self.mustsort = True
                if len(above)==1:
                    self.v.messg("("+str(above[0])+")\n")
            for e in above:
                self.preds[e].append(node)
                if e.mns > node.supp: e.mns = node.supp
            for e in below:
                self.preds[node].append(e)
                if node.supp > e.mxs: e.mxs = node.supp
            return node

    def addempty(self,nrtr):
        """
        add emptyset as closure, with nrtr as support
        (pushed into the front, not appended)
        mns for emptyset nrtr for today, somewhat unclear
        (kills down to 1 the width of empty-antecedent rules, maybe rightly so)
        """
        node = str2node()
        node.setsupp(nrtr)
        self.preds[node] = []
        node.mns = nrtr
        node.mxs = 0
        for e in self.closeds:
            self.preds[e].append(node)
            if e.mns > node.supp: e.mns = node.supp
            if e.supp > node.mxs: node.mxs= e.supp
        self.card += 1
        self.closeds.insert(0,node)

    def topercent(self,anysupp):
        """
        anysupp expected in [0,1], eg a support bound
        gets translated into percent and truncated according to scale
        (e.g. for scale 100000 means three decimal places)
        """
        return 100.0*floor(self.scale*anysupp)/self.scale

    def __str__(self):
        s = ""
        for e in sorted(self.closeds):
            s += str(e) + "\n"
        return s

    def close(self,st):
        "closure of set st according to current closures list - slow for now"
        over = [ e for e in self.closeds if st <= e ]
        if len(over)>0:
            e = over[0]
        else:
            "CAREFUL: what if st is not included in self.U?"
            e = itset(self.U)
        for e1 in over:
            if e1 < e:
                e = e1
        return e

    def isclosed(self,st):
        "test closedness of set st according to current closures list"
        return st in self.closeds

if __name__=="__main__":
    "ToDo: use messg instead of print?"

    fnm = "e13"

    la = clattice(0,fnm)

    la.v.inimessg("Module clattice running as test on file "+fnm+".txt.")

    print "\nLattice read in:"
    print la
    print "Closure of ac:", la.close(set2node(auxitset("a c")))
    print "Closure of ab:", la.close(str2node("a b"))
    print "Is ac closed?", la.isclosed(str2node("a c"))
    print "Is ab closed?", la.isclosed(str2node("a b"))
    print "Is ac with support closed?", la.isclosed(str2node("a c / 7777"))
    print "Is ab with support and noise closed?", la.isclosed(str2node("a b(  (  ( /   3456)"))

    
