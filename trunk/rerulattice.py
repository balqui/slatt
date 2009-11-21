#! /usr/bin/python

"""
Subproject: Slatt
Package: rerulattice
Programmers: JLB

Inherits from slattice, which brings cuts, mingens, and GDgens

Offers:
.hist_RR:  dict mapping each supp/conf thresholds tried
  to the repr rules basis constructed according to that method
.mineRR to compute the representative rules for a given confidence using
  corr tightening of transversals of the negative cuts
SOON
.mineKrRR to compute a subset of representative rules by Kryszkiewicz heuristic, hist_KrRR
.mineBCRR to compute a representative rules by our method, hist_BCRR

.CAREFUL: method mineBstar to compute the B* basis from positive cuts
  via corr tightening NOT here for the time being (guess only needs clattice,
  and not slattice, except for the GD basis - could be considerably faster)

Notes/ToDo:
.want to be able to use it on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
..due to an inappropriate closures file, or due to the fact that indeed there
..are no closed sets in the dataset in between both supports (careful with
..their different scales); set reliable_support_bound to true if you are
..sure that the closures you are working with are correct
.mingens at a given confidence need also their mns - three options:
..compute set mingens via transversal and find the rest by linear search in mingens
..compute set mingens via transversal and have the rest accessible in a dict
...somewhere else
..compute directly complete mingens through linear search in mingens
.revise and enlarge the local testing
.revise ticking rates
"""

from slattice import slattice
from slarule import slarule
from corr import corr

class rerulattice(slattice):

    def __init__(self,supp,datasetfile="",v=None):
        "call slattice to get the closures and minimal generators"
        slattice.__init__(self,supp,datasetfile,v)
        self.hist_RR = {}
        self.hist_KrRR = {}

    def dump_hist_RR(self):
        "prints out all the representative bases computed so far"
        for e in self.hist_RR.keys():
            print "At support", (e[0]+0.0)/self.scale,
            print "and confidence", (e[1]+0.0)/self.scale
            print self.hist_RR[e]

## OPEN THIS UP WHEN THE Kr HEURISTIC MINING IS READY
##    def dump_hist_KrRR(self):
##        "prints out all the bases computed so far"
##        for e in self.hist_KrRR.keys():
##            print "At support", (e[0]+0.0)/self.scale,
##            print "and confidence", (e[1]+0.0)/self.scale
##            print self.hist_KrRR[e]

    def mineRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        """
        if confthr == 1:
            return self.mingens(suppthr)
        sthr = int(self.scale*suppthr)
# PENDING: EXTRA CHECK THAT THE SUPPORT IN THE CL FILE IS SUFFICIENT - THIS ONE IS NOT REALLY GOOD
#        if sthr < self.scale*self.cl.minsupp/self.cl.nrtr:
#            self.v.errmessg("Support "+str(suppthr)+" not available.")
#            return None
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_RR.keys():
            return self.hist_RR[sthr,cthr]
        self.v.zero(100)
        self.v.inimessg("Direct computation of representative rules;")
        nonants = self.setcuts(sthr,cthr,forget)[1]
        ants = corr()
        self.v.messg("computing potential antecedents at confidence "+str(confthr)+"...")
        for nod in self.closeds:
            """
            careful, assuming nodes ordered by size here
            find all free noncl antecs as cut transv
            get associated data by search on mingens
            alternative algorithms exist to avoid the
            slow call to _findiinmingens - must try them
            """
            self.v.tick()
            if True:
                "to add here the support constraint if convenient"
##            if self.scale*nod.supp >= sthr*self.nrtr:
                ants[nod] = []
                for m in self._faces(nod,nonants[nod]).transv().hyedges:
                    if m < nod:
                        mm = self._findinmingens(nod,m)
                        if mm==None: print m, "not found at", nod
                        ants[nod].append(mm)
        self.v.zero(500)
        self.v.messg("...checking valid antecedents...")
        ants.tighten(self.v)
        self.v.messg("...done.\n")
        return ants

##    def mineKrRR(self,suppthr,confthr,forget=False):
##        """
##        ditto, just that here we use the incomplete Krysz IDA 2001 heuristic
##        must ensure that mineW and setmns have been called
##        seems that this version does not find empty antecedents
##        """
##        sthr = int(self.scale*suppthr)
###        if sthr < self.scale*self.cl.minsupp/self.cl.nrtr:
###            self.v.errmessg("Support "+str(suppthr)+" not available.")
###            return None
##        cthr = int(self.scale*confthr)
##        if (sthr,cthr) in self.hist_KrRR.keys():
##            return self.hist_KrRR[sthr,cthr]
##        self.mineW()
##        self.setmns()
##        self.v.zero(100)
##        self.v.inimessg("K-variant computation of representative rules;")
##        out = implattice()
##        out.nrtr = self.cl.nrtr
##        for nod in self.cl.closeds:
##            """
##            """
##            self.v.tick()
##            closants = []
##            if self.scale*nod.supp >= sthr*self.cl.nrtr and \
##                self.scale*nod.supp >= cthr*nod.mns and \
##                self.scale*nod.mxs < cthr*nod.mns:
##                "that was the test of Property 9"
##                for m in self.cl.preds[nod]:
##                    if self.scale*nod.supp >= cthr*m.supp and \
##                        self.scale*nod.mxs < cthr*m.supp:
##                        closants.append(m)
##                for m in closants:
##                    for an in self.Wants[m]:
##                        if self.scale*nod.supp < cthr*an.mns and an < nod:
##                            out.newrule(slarule(an,nod))
##        if not forget: self.hist_KrRR[sthr,cthr] = out
##        self.v.messg("...done; "+str(out.nrimpls)+" rules found.\n")
##        return out

## OLD THINGS JUST IN CASE
####        self.v.messg("computing potential antecedents at confidence "+str(confthr)+"...")
##
####            if self.scale*nod.supp >= sthr*self.cl.nrtr:
####                ants[nod] = []
####                for m in self._faces(nod,nonants[nod]).transv().hyedges:
####                    if m < nod:
####                        mm = self._findinmingens(m)
####                        mm.clos = nod
####                        ants[nod].append(mm)
####        self.v.zero(500)
####        self.v.messg("...checking valid antecedents...")
####        ants.tighten(cnt)
####
####        self.v.zero()
####        self.v.messg("...computing representative rules at confidence "+str(confthr)+"...")
####        for nod in ants.keys():
####            self.v.tick()
####            for an in ants[nod]:
####                out.newrule(slarule(an,nod))

if __name__ == "__main__":

    from slarule import printrules

#    from trNS import tradNS

##    forget = True
    forget = False

##    filename = "pumsb_star"
##    filename = "cmc_eindh4"
##    supp = 70.0/1473

    filename = "e13"
    supp = 1.0/13

    rl = rerulattice(supp,filename+".txt")
    
    print printrules(rl.mingens,rl.nrtr,file(filename+"_IFrl30s.txt","w")), "rules in the iteration free basis."

    rl.findGDgens()

#    print printrules(rl.GDgens,rl.nrtr,file(filename+"_GDrl30s.txt","w"),tradNS), "rules in the GD basis."

    RRants = rl.mineRR(supp,0.95)

    print printrules(RRants,rl.nrtr,file(filename+"_RR95c30s.txt","w")), "repr rules found at conf 0.95."

## dataset info: filename or closfile (.txt), nr trans, nr items, nr occurrences
## filename = "pumsb_star"
##  nrtr = 49046
##  nrits = 2088
##  nrocc = 2475947
##  closfile = "pumsb_star_cl0.30s"
##
##  supp = 0.3

##    closname = "e13tr1s"
##    filename = "e13"
##    nrtr = 13
##    nrits = 3
##    nroccs = 27
##
##    supp = 1.0/13
  
