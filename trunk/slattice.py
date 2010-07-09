"""
Project: Slatt
Package: slattice
Programmers: JLB

Purpose: basic implication mining, that is, minimal generators and GD basis

Inherits from clattice; use clattice when only closures are needed,
like in brulattice, and slattice when the minimal generators of each
closure are also needed, as in rerulattice.

Fields: 
.hist_trnsl: all transversals computed so far, so that they are not recomputed
.mingens: a corr maintaining the nontrivial minimal generators for each closure
..antecedents of the iteration-free basis of Wild, Pfaltz-Taylor, Pasquier-Bastide, Zaki...
.GDmingens: a corr with the antecedents of the GD basis

Methods available:
.findmingens: to compute the minimal generators of all closures via
  transversals of immediate predecessors obtained as negative cuts
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

class slattice(clattice):

    def __init__(self,supp,datasetfile="",v=None,xmlinput=False,externalminer=True):
        "get the closures, find minimal generators, set their mns"
        clattice.__init__(self,supp,datasetfile,v,xmlinput=xmlinput,externalminer=externalminer)
        self.mingens = corr()
        self.GDgens = None # upon computing it, will be a corr()
        self.hist_cuts = {}
        self.hist_trnsl = {}
        self.findmingens()
        self.setmns()


    def _faces(self,itst,listpred):
        "listpred assumed immediate preds of itst - make hypergraph of differences"
        itst = set(itst)
        return hypergraph(itst,[ itst - e for e in listpred ])

    def _findinmingens(self,upbd,st):
        """
        must be a set that appears in mingen as itset with extra info
        WHAT IF NOT FOUND?
        THIS PART HAS TO BE RETHOUGHT AGAIN...
        """
        for m in self.mingens[upbd]:
            if m <= st and st <= m:
                return m
        for nd in self.preds[upbd]:
            for m in self.mingens[nd]:
                if m <= st and st <= m:
                    break
            else:
                continue
            return m
        return None

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
        if len(self.mingens)>0:
            return self.mingens
        self.v.inimessg("Computing cuts for minimal generators...")
        nonants = self.setcuts(sthr,self.scale,False)[1]
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
        if self.GDgens: return
        self.GDgens = corr()
        if True:
            sthr = self.scale*self.minsupp/self.nrtr
        self.v.zero(250)
        self.v.inimessg("Filtering minimal generators to obtain the Guigues-Duquenne basis...")
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
        self.v.messg("...done.\n")


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
    from slanode import str2node
    
## CHOOSE A DATASET:
    filename = "e13"

#    filename = "lenses_recoded"
    supp = 1.0/14

##    filename = "pumsb_star"
##    filename = "mvotes"
##    filename = "toyGD"
##    filename = "cmc_eindh4"
    

## CHOOSE A SUPPORT CONSTRAINT:
## forty percent (recommended for pumsb_star):
##    supp = 0.4
## twenty percent (recommended for mvotes):
##    supp = 0.2
## one-tenth percent (not recommended):
##    supp = 0.001
## other figures (recommended for toys e13 and toyGD):
##    supp = 1.0/13
##    supp = 0
##    supp = 70.0/1473

## CHOOSE WHAT TO SEE (recommended: see lattice only on toys):

    see_whole_lattice = True
    
## (recommended: first, just count them; see them only after you know how big they are)
    see_it_free_basis = True
    count_it_free_basis = True

    see_GD_basis = True
    count_GD_basis = True


## NOW DO ALL THAT

    la = slattice(supp,filename)

    if see_whole_lattice: print la

    print "Test _findinmingens:", la._findinmingens(la.closeds[6],str2node("a b"))

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

    

