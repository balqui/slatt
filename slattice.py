#! /usr/bin/python

"""
Project: Slatt
Package: slattice
Programmers: JLB

Purpose: basic implication mining, that is, minimal generators and GD basis

Inherits from clattice; use clattice when only closures are needed,
and slattice when the minimal generators of each closure are also needed.

Fields: 
hist_cuts: all cuts computed so far, so that they are not recomputed
hist_trnsl: all transversals computed so far, so that they are not recomputed
mingens: a corr maintaining the nontrivial minimal generators for each closure
.antecedents of the iteration-free basis of Wild, Pfaltz-Taylor, Pasquier-Bastide, Zaki...
GDmingens: a corr with the antecedents of the GD basis

Methods available:
.dump_hist_cuts
.findmingens: to compute the minimal generators of all closures via
  transversals of immediate predecessors obtained as negative cuts,
  (note that no tightening is necessary)
.setmns to initialize the mns's of the free sets after mingens created
.findGD to refine the iteration-free basis into the Guigues-Duquenne basis

Auxiliary local methods:
._cut to make a cut for a given node and a threshold
._setcuts to compute all the cuts
._faces to compute faces (differences) to apply the transversal

ToDo:
.revise and enlarge the local testing, particularly the cuts
.revise ticking rates
.rethink the scale, now 10000 means two decimal places for percentages
.some day it can be used on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
..due to an inappropriate closures file, or due to the fact that indeed there
..are no closed sets in the dataset in between both supports (careful with
..their different scales), all this is to be clarified
"""

from clattice import clattice
from slanode import set2node
from hypergraph import hypergraph
from corr import corr

##from verbosity import verbosity
##from itset import itset, itsetset, itsetstr
##from slarule import slarule
##from implattice import implattice

#from math import floor


class slattice(clattice):

    def __init__(self,supp,datasetfile="",v=None):
        "get the closures, find minimal generators, set their mns"
        clattice.__init__(self,supp,datasetfile,v)
        self.mingens = {}
        self.GDgens = {}
        self.hist_cuts = {}
        self.hist_trnsl = {}
        self.findmingens()
        self.setmns()

    def dump_hist_cuts(self):
        "prints out all the cuts so far - useful mostly for testing"
        for e in self.hist_cuts.keys():
            print "\nMinimal closed antecedents at conf thr", e
            pos = self.hist_cuts[e][0]
            for ee in pos.keys():
                print ee, ":",
                for eee in pos[ee]: print eee,
                print
            print "Maximal closed nonantecedents at conf thr", e
            neg = self.hist_cuts[e][1]
            for ee in neg.keys():
                print ee, ":",
                for eee in neg[ee]: print eee,
                print

    def _faces(self,itst,listpred):
        "listpred assumed immediate preds of itst - make hypergraph of differences"
        itst = set(itst)
        return hypergraph(itst,[ itst - e for e in listpred ])

    def _setcuts(self,scsthr,sccthr,forget=False):
        """
        supp/conf already scaled thrs in [0,self.scale]
        computes all cuts for that supp/conf thresholds, if not computed yet;
        keeps them in hist_cuts to avoid duplicate computation (unless forget);
        the cut for each node consists of two corrs, pos and neg border:
        hist_cuts : supp/conf thr -> (pos,neg)
        pos : node -> min ants,  neg : node -> max nonants
        UNCLEAR WHETHER IT WORKS FOR A SUPPORT DIFFERENT FROM self.minsupp
        """
        if (scsthr,sccthr) in self.hist_cuts.keys():
            return self.hist_cuts[scsthr,sccthr]
        cpos = corr()
        cneg = corr()
        self.v.zero(500)
        self.v.messg("...computing (non-)antecedents...")
        for nod in self.closeds:
            "review carefully and document this loop"
            self.v.tick()
            if self.scale*nod.supp >= self.nrtr*scsthr:
                pos, neg = self._cut(nod,sccthr) 
                cpos[nod] = pos
                cneg[nod] = neg
        if not forget: self.hist_cuts[scsthr,sccthr] = cpos, cneg
        self.v.messg("...done;")
        return cpos, cneg

    def _cut(self,node,thr):
        """
        splits preds of node at cut given by
        min thr-antecedents and max non-thr-antecedents
        think about alternative algorithmics
        thr expected scaled according to self.scale
        """
        yesants = []
        notants = []
        for m in self.preds[node]:
            "there must be a better way of doing all this!"
            if self.scale*node.supp >= thr*m.supp:
                yesants.append(m)
            else:
                notants.append(m)
        minants = []
        for m in yesants:
            "keep only minimal antecedents - candidate to separate program?"
            for mm in yesants:
                if mm < m:
                    break
            else:
                minants.append(m)
        maxnonants = []
        for m in notants:
            "keep only maximal nonantecedents"
            for mm in notants:
                if m < mm:
                    break
            else:
                maxnonants.append(m)
        return (minants,maxnonants)

## method _findmingens hopefully unnecessary from now on

##    def _findinmingens(self,st):
##        "must be a set that appears in mingen as itset with extra info - WHAT IF NOT FOUND?"
##        for m in self.mingens:
##            if m <= st and st <= m:
##                break
##        else:
##            self.v.errmessg("Set "+str(st)+" expected in list of free sets but not found there.")
##            return None
##        return m

    def findmingens(self,suppthr=-1):
        """
        compute the minimal generators for each closure;
        nontrivial pairs conform Wild's iteration-free basis;
        algorithm is the same as mineRR for confidence 1;
        optional suppthr in [0,1] to impose an extra level of iceberg
        but this optional value is currently ignored
        because maybe minsupp actually much higher than mined at
        use the support found in closures file
        when other supports handled, remember to memorize computed ones
        """
        if suppthr < 0:
            "ToDo: find out how to use integer division"
            sthr = int(self.scale*self.minsupp/self.nrtr)
        else:
            "ToDo: remove this assignment and do it the right way"
            sthr = int(self.scale*self.minsupp/self.nrtr)
#            sthr = floor(self.scale*suppthr)
#            if sthr < self.scale*self.minsupp/self.nrtr:
# raise exception by returning None - BUT THIS PART DOES NOT REALLY WORK
#                self.v.errmessg("[mineW] Support "+str(suppthr)+" not available.")
#                return None
        if len(self.mingens)>0:
            return self.mingens
        self.v.inimessg("Computing cuts for minimal generators...")
        nonants = self._setcuts(sthr,self.scale,False)[1]
        self.v.zero(250)
        self.v.messg("computing transversal antecedents...")
        for nod in self.closeds:
            "careful, assuming nodes ordered by size here - find all free sets"
            self.v.tick()
            self.mingens[nod] = []
            for m in self._faces(nod,nonants[nod]).transv().hyedges:
                mm = set2node(m)
                mm.setsupp(nod.supp)
                mm.clos = nod
                self.mingens[nod].append(mm)
        self.v.messg("...done;")
        return self.mingens

    def findGDgens(self,suppthr=-1):
        """
        compute the GD antecedents - only proper antecedents returned
        ToDo: as in findmingens,
        optional suppthr in [0,1] to impose an extra level of iceberg
        if not present, use the support found in closures file
        check sthr in self.hist_GD.keys() before computing it
        when other supports handled, remember to memorize computed ones
        """
        if True:
            sthr = self.scale*self.minsupp/self.nrtr
##        if sthr in self.hist_GD.keys():
##            return self.hist_GD[sthr]
        self.v.zero(250)
        self.v.inimessg("Filtering minimal generators to obtain Guigues-Duquenne basis...")
        for c1 in self.closeds:
            self.v.tick()
            self.GDgens[c1] = set([])
            for g1 in self.mingens[c1]:
                g1new = set(g1)
                changed = True
                while changed:
                    changed = False
                    for c2 in self.preds[c1]:
                        for g2 in self.mingens[c2]:
                            if g2 < g1new and not c2 <= g1new:
                                g1new.update(c2)
                                changed = True
                g1new = g1.copy().revise(g1new)
                if not c1 <= g1new:
                    "skip it if subsumed or if equal to closure"
                    for g3 in self.GDgens[c1]:
                        if g3 <= g1new: break
                    else:
                        "else of for: not subsumed"
                        self.GDgens[c1].add(g1new)


    def setmns(self):
        """
        set slanode.mns for free sets in mingens lists
        findmingens() assumed to have been invoked already
        maybe it is possible to accelerate this computation
        """
        self.v.zero(250)
        self.v.inimessg("Initializing min supp below free sets...")
        for c1 in self.closeds:
            for m1 in self.mingens[c1]:
                self.v.tick()
                if m1.mns <= 0:
                    m1.mns = self.nrtr
                    for c2 in self.preds[c1]:
                        if c2.supp < m1.mns:
                            for m2 in self.mingens[c2]:
                                if m2 < m1:
                                    m1.mns = c2.supp
        self.v.messg("...done.\n")

if __name__ == "__main__":

    from slarule import slarule

## CHOOSE A DATASET:
##    filename = "pumsb_star"
    filename = "e13"
##    filename = "mvotes"
##    filename = "toyGD"

## CHOOSE A SUPPORT CONSTRAINT:
# forty percent (recommended for pumsb_star):
##    supp = 0.4
# twenty percent (recommended for mvotes):
##    supp = 0.2
# one-tenth percent (not recommended):
##    supp = 0.001
# other figures (recommended for toys e13 and toyGD):
    supp = 1.0/13
##    supp = 0

## CHOOSE WHAT TO SEE (recommended: see lattice and test cuts only on toys):

    see_whole_lattice = True
    
    test_cut_on_a = True
    test_all_cuts = True

## (recommended: first, just count them; see them only after you know how big they are)
    see_it_free_basis = True
    count_it_free_basis = True

    see_GD_basis = True
    count_GD_basis = True


## NOW DO ALL THAT

    la = slattice(supp,filename)

    if see_whole_lattice: print la

    if test_cut_on_a:
        (y,n) = la._cut(la.close(set2node("a")),int(0.1*la.scale))
        print "cutting at threshold", 0.1
        print "pos cut at a:", y
        print "neg cut at a:", n

    if test_all_cuts:
        print "cutting all nodes now at threshold", 0.75
        for nd in la.closeds:
            print
            print "At:", nd
            print "  mxs:", nd.mxs, "mns:", nd.mns
            (y,n) = la._cut(nd,int(0.75*la.scale))
            print "pos cut:",
            for st in y: print st,
            print
            print "neg cut:",
            for st in n: print st,
            print

    if count_it_free_basis or see_it_free_basis:

        if see_it_free_basis: print "Iteration-free basis:"
        cnt = 0
        for c in la.closeds:
            for g in la.mingens[c]:
                if g<c:
                    cnt += 1
                    r = slarule(g,c)
                    if see_it_free_basis: 
                        print r, " [c:", r.conf(), "s:", r.supp(), "w:", r.width(la.nrtr), "]"

    if count_GD_basis or see_GD_basis:

        la.findGDgens()

        if see_GD_basis: print "\nGuigues-Duquenne basis:"

        cntGD = 0
        for c in la.closeds:
            for g in la.GDgens[c]:
                cntGD += 1
                r = slarule(g,c)
                if see_GD_basis: 
                    print r, " [c:", r.conf(), "s:", r.supp(), "w:", r.width(la.nrtr), "]"

        if count_it_free_basis:
            print
            print cnt, "rules in the iteration-free basis"

        if count_GD_basis: 
            print
            print cntGD, "rules in the Guigues-Duquenne basis"
