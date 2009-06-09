#! /usr/bin/python

"""
Subproject: slatt
Versions: 0.1.5 onwards
Package: rulattice
Creation: March 15th, 2009, on the basis of existing mirerulattice
Programmers: JLB
Last revision: April 26th, 2009

Purpose: implement rule mining from a clattice, to obtain an implattice,
according to several methods. Added in Bangkok support for calling wc
and apriori from inside (but only works for linux/cygwin platforms).

Fields: 
cl: clattice - does not bring cut method anymore
mingens: list of all free sets, created upon calling mineW()
scale: a local field here
Wants: a corr maintaining the nontrivial Wild-antecedents for each closure
hist_RR:  dict mapping each supp/conf thresholds tried with repr rules basis,
likewise for other hist_ fields (no hist_ for Wild basis because they are
a particular case of repr rules)

Methods available:
.dumps for the hist_ fields
.mineW to compute the iteration-free basis of Wild et al using 
  transversals of immediate predecessors obtained as negative cuts,
  also initializes the mingens list with all the free sets
  (note that no tightening is necessary) and repeats them all
  along with the closure they generate (if different) in corr Wants
.setmns to initialize the mns's of the free sets after mingens created
.mineGD to refine the iteration-free basis into the Guigues-Duquenne basis
.mineRR to compute the representative rules for a given confidence using
  corr tightening of transversals of the negative cuts
.mineKrRR to compute a subset of representative rules by Kryszkiewicz heuristic
.mineBstar to compute the B* basis from positive cuts via corr tightening

Auxiliary local methods:
._cut to make a cut for a given node and a threshold
._setcuts to compute all the cuts
._faces to compute faces (differences) to apply the transversal

Notes:
.can be used on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
..due to an inappropriate closures file, or due to the fact that indeed there
..are no closed sets in the dataset in between both supports (careful with
..their different scales); set reliable_support_bound to true if you are
..sure that the closures you are working with are correct

ToDo:
.revise and enlarge the local testing
.revise ticking rates
.rethink the scale, now 10000 means two decimal places for percentages
"""

from verbosity import verbosity
from itset import itset, itsetset, itsetstr
from slarule import slarule
from corr import corr
from clattice import clattice
from implattice import implattice
from hypergraph import hypergraph

class rulattice:

    def __init__(self,nrtr,clfile,verb=True):
        self.v = verbosity(verb)
        self.cl = clattice(nrtr,clfile,self.v)
        self.scale = 10000
        self.mingens = []
        self.Wants = corr()
        self.hist_cuts = {}
        self.hist_trnsl = {}
        self.hist_RR = {}
        self.hist_KrRR = {}
        self.hist_Bstar = {}
        self.hist_GD = {}
##        sthr = float(self.cl.minsupp)/self.cl.nrtr

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

    def dump_hist_RR(self):
        "prints out all the representative bases computed so far"
        for e in self.hist_RR.keys():
            print "At support", (e[0]+0.0)/self.scale,
            print "and confidence", (e[1]+0.0)/self.scale
            print self.hist_RR[e]

    def dump_hist_KrRR(self):
        "prints out all the bases computed so far"
        for e in self.hist_KrRR.keys():
            print "At support", (e[0]+0.0)/self.scale,
            print "and confidence", (e[1]+0.0)/self.scale
            print self.hist_KrRR[e]

    def dump_hist_Bstar(self):
        "prints out all the Bstar bases computed so far"
        for e in self.hist_Bstar.keys():
            print "At support", (e[0]+0.0)/self.scale,
            print "and confidence", (e[1]+0.0)/self.scale
            print self.hist_Bstar[e]

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
        """
        if (scsthr,sccthr) in self.hist_cuts.keys():
            return self.hist_cuts[scsthr,sccthr]
        cpos = corr()
        cneg = corr()
        self.v.zero(500)
        self.v.messg("...computing (non-)antecedents...")
        for nod in self.cl.closeds:
            "review carefully and document this loop"
            self.v.tick()
            if self.scale*nod.supp >= self.cl.nrtr*scsthr:
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
        for m in self.cl.preds[node]:
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

    def _findinmingens(self,st):
        "must be a set that appears in mingen as itset with extra info - WHAT IF NOT FOUND?"
        for m in self.mingens:
            if m <= st and st <= m:
                break
        else:
            self.v.errmessg("Set "+str(st)+" expected in list of free sets but not found there.")
            return None
        return m

    def mineW(self,suppthr=-1):
        """
        compute Wild's iteration-free basis by
        doing the same as mineRR for confidence 1
        just that besides we will compute the list mingens
        of all the free sets, whether closed or not
        optional suppthr in [0,1] to impose an extra level of iceberg
        if not present, use the support found in closures file
        DO WE ALSO SET THE RIGHT VALUES FOR mns OF FREE SETS?
        URGENT: THE SUPPORT CHECK DOES NOT WORK, MAYBE MINSUPP
        ACTUALLY MUCH HIGHER THAN MINED AT
        """
        if suppthr < 0:
            sthr = self.scale*self.cl.minsupp/self.cl.nrtr
        else:
            sthr = int(self.scale*suppthr)
#            if sthr < self.scale*self.cl.minsupp/self.cl.nrtr:
# raise exception by returning None
#                self.v.errmessg("[mineW] Support "+str(suppthr)+" not available.")
#                return None
        if (sthr,self.scale) in self.hist_RR.keys():
            return self.hist_RR[sthr,self.scale]
        self.v.inimessg("Computing info for minimal generators and iteration-free basis...")
        nonants = self._setcuts(sthr,self.scale,False)[1]
        self.v.zero()
        self.v.messg("computing transversal antecedents...")
        self.Wants = corr()
        for nod in self.cl.closeds:
            "careful, assuming nodes ordered by size here - find all free sets"
            self.v.tick()
            self.Wants[nod] = []
            for m in self._faces(nod,nonants[nod]).transv().hyedges:
                mm = itsetset(m)
                mm.setsupp(nod.supp)
                mm.clos = nod
                self.mingens.append(mm)
                self.Wants[nod].append(mm)
        self.v.messg("...done;")
        out = implattice()
        out.nrtr = self.cl.nrtr
        self.v.zero()
        self.v.messg("storing the iteration-free basis...")
        for nod in self.Wants.keys():
            self.v.tick()
            for an in self.Wants[nod]:
                if an < nod:
                    "only nonclosed free ants yield a rule"
                    out.newrule(slarule(an,nod))
        self.hist_RR[sthr,self.scale] = out
        self.v.messg("...done; "+str(out.nrimpls)+" implications found.\n")
        return out

    def mineGD(self,suppthr=-1):
        """
        compute the GD basis out of a fresh '*1' copy of it-free
        optional suppthr in [0,1] to impose an extra level of iceberg
        if not present, use the support found in closures file
        """
        if suppthr < 0:
            sthr = self.scale*self.cl.minsupp/self.cl.nrtr
        else:
            sthr = int(self.scale*suppthr)
            if sthr < self.scale*self.cl.minsupp/self.cl.nrtr:
                self.v.errmessg("Support "+str(suppthr)+" not available.")
                return None
        if sthr in self.hist_GD.keys():
            return self.hist_GD[sthr]
        Wb = self.mineW(suppthr).impls * 1
        local = implattice()
        local.nrtr = self.cl.nrtr
        self.v.zero(25)
        self.v.inimessg("Filtering rules to obtain Guigues-Duquenne basis...")
        while len(Wb)>0:
            self.v.tick()
            Wb.sort()
            nrul = Wb[0]
            nrul.an.supp = nrul.cn.supp
            local.newrule(nrul)
            closeants = []
            for r in Wb:
                "aan mutable set, rest of fields using revise"
                aan = set(r.an)
                aaan = r.an.revise(local.close(aan))
                closeants.append(slarule(aaan,r.cn))
            Wb = []
            for r in closeants:
                if r.an < r.cn:
                    Wb.append(r)
        self.v.messg("...done; "+str(local.nrimpls)+" implications found.\n")
        self.hist_GD[sthr] = local
        return local

    def mineRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        URGENT: THE SUPPORT CHECK DOES NOT WORK, MAYBE MINSUPP
        ACTUALLY MUCH HIGHER THAN MINED AT
        """
        if confthr == 1:
            return self.mineW(suppthr)
        sthr = int(self.scale*suppthr)
#        if sthr < self.scale*self.cl.minsupp/self.cl.nrtr:
#            self.v.errmessg("Support "+str(suppthr)+" not available.")
#            return None
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_RR.keys():
            return self.hist_RR[sthr,cthr]
        self.v.zero(100)
        self.v.inimessg("Direct computation of representative rules;")
        nonants = self._setcuts(sthr,cthr,forget)[1]
        ants = corr()
        self.v.messg("computing potential antecedents at confidence "+str(confthr)+"...")
        for nod in self.cl.closeds:
            """
            careful, assuming nodes ordered by size here (?)
            find all free noncl antecs as cut transv
            get associated data by search on mingens
            maybe a quadratic search might avoid the transversal computation
            """
            self.v.tick()
            if self.scale*nod.supp >= sthr*self.cl.nrtr:
                ants[nod] = []
                for m in self._faces(nod,nonants[nod]).transv().hyedges:
                    if m < nod:
                        mm = self._findinmingens(m)
                        mm.clos = nod
                        ants[nod].append(mm)
        self.v.zero(500)
        self.v.messg("...checking valid antecedents...")
        ants.tighten(self.v)
        out = implattice()
        out.nrtr = self.cl.nrtr
        self.v.zero()
        self.v.messg("...computing representative rules at confidence "+str(confthr)+"...")
        for nod in ants.keys():
            self.v.tick()
            for an in ants[nod]:
                out.newrule(slarule(an,nod))
        if not forget: self.hist_RR[sthr,cthr] = out
        self.v.messg("...done; "+str(out.nrimpls)+" rules found.\n")
        return out

    def mineKrRR(self,suppthr,confthr,forget=False):
        """
        ditto, just that here we use the incomplete Krysz IDA 2001 heuristic
        must ensure that mineW and setmns have been called
        seems that this version does not find empty antecedents
        URGENT: THE SUPPORT CHECK DOES NOT WORK, MAYBE MINSUPP
        ACTUALLY MUCH HIGHER THAN MINED AT
        """
        sthr = int(self.scale*suppthr)
#        if sthr < self.scale*self.cl.minsupp/self.cl.nrtr:
#            self.v.errmessg("Support "+str(suppthr)+" not available.")
#            return None
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_KrRR.keys():
            return self.hist_KrRR[sthr,cthr]
        self.mineW()
        self.setmns()
        self.v.zero(100)
        self.v.inimessg("K-variant computation of representative rules;")
        out = implattice()
        out.nrtr = self.cl.nrtr
        for nod in self.cl.closeds:
            """
            """
            self.v.tick()
            closants = []
            if self.scale*nod.supp >= sthr*self.cl.nrtr and \
                self.scale*nod.supp >= cthr*nod.mns and \
                self.scale*nod.mxs < cthr*nod.mns:
                "that was the test of Property 9"
                for m in self.cl.preds[nod]:
                    if self.scale*nod.supp >= cthr*m.supp and \
                        self.scale*nod.mxs < cthr*m.supp:
                        closants.append(m)
                for m in closants:
                    for an in self.Wants[m]:
                        if self.scale*nod.supp < cthr*an.mns and an < nod:
                            out.newrule(slarule(an,nod))
        if not forget: self.hist_KrRR[sthr,cthr] = out
        self.v.messg("...done; "+str(out.nrimpls)+" rules found.\n")
        return out
                
##        self.v.messg("computing potential antecedents at confidence "+str(confthr)+"...")

##            if self.scale*nod.supp >= sthr*self.cl.nrtr:
##                ants[nod] = []
##                for m in self._faces(nod,nonants[nod]).transv().hyedges:
##                    if m < nod:
##                        mm = self._findinmingens(m)
##                        mm.clos = nod
##                        ants[nod].append(mm)
##        self.v.zero(500)
##        self.v.messg("...checking valid antecedents...")
##        ants.tighten(cnt)
##
##        self.v.zero()
##        self.v.messg("...computing representative rules at confidence "+str(confthr)+"...")
##        for nod in ants.keys():
##            self.v.tick()
##            for an in ants[nod]:
##                out.newrule(slarule(an,nod))

    def mineBstar(self,suppthr,confthr,forget=False):
        """
        compute the Bstar basis for the given confidence;
        thresholds in [0,1], rescaled into [0,self.x.scale] inside
        comments inherited from mineRR:
        TODO: CHECK SUPPTHR COMPATIBLE WITH X.SUPPTHR
        NOW THIS IS BEING DONE ELSEWHERE BUT MAYBE SHOULD BE HERE
        """
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_Bstar.keys():
            return self.hist_Bstar[sthr,cthr]
        self.v.zero(100)
        self.v.inimessg("Computing B* basis;")
        yesants = self._setcuts(sthr,cthr,forget)[0]
        self.v.messg("validating minimal antecedents at confidence "+str(confthr)+"...")
        yesants.tighten(self.v)
        out = implattice()
        out.nrtr = self.cl.nrtr
        self.v.zero()
        self.v.messg("...computing B* basis at confidence "+str(confthr)+"...")
        for nod in yesants.keys():
            "must check support additionally?"
            self.v.tick()
            for an in yesants[nod]:
                "is it guaranteed that an < nod?"
                out.newrule(slarule(an,nod))
        if not forget: self.hist_Bstar[sthr,cthr] = out
        self.v.messg("...done; "+str(out.nrimpls)+" rules found.\n")
        return out

##        for st in self.cl.closeds:
##            "CHECK! this we do just for iceberg above suppth - IS THE SCALE RIGHT?"
##            if st.supp>=sthr:
##                self._validate(st)
##        out = implattice()
##        out.nrtr = self.cl.nrtr
##        self.x.zero()
##        self.x.messg("...computing B* basis at confidence "+str(confthr))
##
####        for st in self.cl.closeds: CHECK!
##
##            if st.supp>=suppth:
##                for an in st.validants:
##                    if an < st:
##                        self.newimpl(an,st)
##
##
##
##    def _validate(self,n):
##        "sift ants to leave only valid ones - all ants at whole lattice known"
##        n.validants = []
##        for g in n.ants:
##            for c in self.cl.closeds:
##                if n < c and g in c.ants:
##                    break
##            else:
##                n.validants.append(g)

    def setmns(self):
        """
        set itset.mns for free itsets in mingens list
        if not ready yet, initialized via a call to mineW
        hopefully this will add the field also to the antecedents in Wants
        """
        if self.mingens == []:
            self.mineW()
        for n in self.mingens:
            if n.mns <= 0:
                n.mns = self.cl.nrtr
        self.v.zero()
        self.v.inimessg("Initializing min supp below free sets...")
        for nd in self.mingens:
            "do I need to check also self.cl.closeds?"
            self.v.tick()
            for n in self.mingens:
                " "
                if nd < n and nd.supp < n.mns:
                    n.mns = nd.supp
        self.v.messg("...done.")

if __name__ == "__main__":

    from showlatt import showlatt

#    from math import floor

##  from subprocess import call

##    forget = True
    forget = False

##  filename = "before1any"

## arm: association rule miner object
    arm = None

## dataset info: filename or closfile (.txt), nr trans, nr items, nr occurrences
## filename = "pumsb_star"
##  nrtr = 49046
##  nrits = 2088
##  nrocc = 2475947
##  closfile = "pumsb_star_cl0.30s"
##
##  supp = 0.3

    closname = "e13tr1s"
    filename = "e13"
    nrtr = 13
    nrits = 3
    nroccs = 27

    supp = 1.0/13
  
## support must be truncated according to scale but scale not available here
## here 100.0 is actually float(scale)/100.0

    supp = floor(100.0*supp)/100

## is that support truly supported by the closures file? Usually it is
    reliable_support_bound = True

    arm = rulattice(nrtr,"%s_cl%2.2fs.txt" % (filename,supp))
    arm.mineW()

    arm.setmns()

    sh = showlatt(arm.scale,arm.v)
    sh.setRR()

##  print "\n[Slatt] It-free rules:", sh.filtercount(arm.mineW(),arm.cl.nrtr,filename+"RRitf.out",supp,1.0)

## do the printing via messg's, and compute the GD basis, and reorganize a bit
  
    if arm == None:
        print "[Slatt] No dataset specified!"
    elif nrtr >= supp*nrtr >= arm.cl.minsupp or reliable_support_bound:
        conf = 0.7
        sh.widththr = 1.3
        arm.mineRR(supp,conf)
        sh.filtercount(arm.mineRR(supp,conf),arm.cl.nrtr,filename+"RRw.out",supp,conf)
        arm.v.messg("Width-sorted representative rules in file "+filename+"RRw.out")
    else:
        arm.v.errmessg("[Main] Closures file may not support value %2.3f; please check out." % supp)
    

## Examples of things to do and how to do them

##        print conf, supp

##
##    print arm.mineKrRR(sup,0.6)
##    print
##    print arm.mineW()
##    print
##    print arm.mineBstar(sup,0.6)
##    print
##    print arm.mineRR(sup,0.6)
##    print
##    print arm.mineGD()

##    arm.mineKrRR(sup,conf)
##    arm.mineW()
##    arm.mineBstar(sup,conf)
##    arm.mineRR(sup,conf)
##    arm.mineGD()

##    sh = showlatt(arm.scale,arm.v)
##    sh.setRR()

##    for sc in arm.hist_Bstar.keys():
##        flnm = "ntest"+closname+str(sc)+"Bstar.txt"
##        print sh.filtercount(arm.hist_Bstar[sc],arm.cl.nrtr,flnm,sup,conf)
    
#    for sc in arm.hist_RR.keys():
#        flnm = "ntest"+closname+str(sc)+"RR.txt"
#        print sh.filtercount(arm.hist_RR[sc],arm.cl.nrtr,flnm,sup,conf)
    
##  closname = "apptoycl12tr1s"
##  nrtr = 12
  
##  closname = "bef1any7118tr8s"
##  nrtr = 7118
  
##  arm = rulattice(nrtr,closname+".txt")

##    conf = 0.75
##    sup = float(arm.cl.minsupp)/arm.cl.nrtr
####    sup = 0.0011



##    (y,n) = la.cut(la.close(itset("a")),1000)
##    print "cutting at threshold", 1000.0/la.x.scale
##    print "pos cut at a:", y
##    print "neg cut at a:", n
##    print "cutting all nodes now at threshold", 7500.0/la.x.scale
##    for nd in la.closeds:
##        print
##        print "At:", nd
##        print "  mxs:", nd.mxs, "mns:", nd.mns
##        (y,n) = la.cut(nd,7500)
##        print "pos cut:",
##        for st in y: print st,
##        print
##        print "neg cut:",
##        for st in n: print st,
##        print
