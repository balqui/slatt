#! /usr/bin/python

"""
Subproject: Slatt
Package: brulattice
Programmers: JLB

Inherits from slattice, which brings cuts, mingens, and GDgens

But mingens not necessary except for GDgens, which may be again unnecessary

Offers:

.hist_Bstar: dict mapping each supp/conf thresholds tried
  to the repr rules basis constructed according to that method
.mineBstar to compute the B* basis from positive cuts
  via corr tightening

Notes/ToDo:
.want to be able to use it on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
..due to an inappropriate closures file, or due to the fact that indeed there
..are no closed sets in the dataset in between both supports (careful with
..their different scales); set reliable_support_bound to true if you are
..sure that the closures you are working with are correct

ToDo:
.revise and enlarge the local testing
.revise ticking rates
"""

from corr import corr
from clattice import clattice

class brulattice(clattice):

    def __init__(self,supp,datasetfile="",v=None):
        clattice.__init__(self,supp,datasetfile,v)
        self.hist_Bstar = {}

    def dump_hist_Bstar(self):
        "prints out all the Bstar bases computed so far"
        for e in self.hist_Bstar.keys():
            print "At support", (e[0]+0.0)/self.scale,
            print "and confidence", (e[1]+0.0)/self.scale
            print self.hist_Bstar[e]


    def mineBstar(self,suppthr,confthr,forget=False):
        """
        compute the Bstar basis for the given confidence;
        thresholds in [0,1], rescaled into [0,self.x.scale] inside
        TODO: CHECK SUPPTHR COMPATIBLE WITH X.SUPPTHR
        NOW THIS IS BEING DONE ELSEWHERE BUT MAYBE SHOULD BE HERE
        """
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_Bstar.keys():
            return self.hist_Bstar[sthr,cthr]
        self.v.zero(100)
        self.v.inimessg("Computing B* basis;")
        yesants = self.setcuts(sthr,cthr,forget)[0]
        self.v.messg("validating minimal antecedents at confidence "+str(confthr)+"...")
        yesants.tighten(self.v)
        if not forget: self.hist_Bstar[sthr,cthr] = yesants
        self.v.messg("...done.\n")
        return yesants


##    def mineBstar(self,suppthr,confthr,forget=False): OOOLLLLLDDDDD
##        """
##        compute the Bstar basis for the given confidence;
##        thresholds in [0,1], rescaled into [0,self.x.scale] inside
##        comments inherited from mineRR:
##        TODO: CHECK SUPPTHR COMPATIBLE WITH X.SUPPTHR
##        NOW THIS IS BEING DONE ELSEWHERE BUT MAYBE SHOULD BE HERE
##        """
##        sthr = int(self.scale*suppthr)
##        cthr = int(self.scale*confthr)
##        if (sthr,cthr) in self.hist_Bstar.keys():
##            return self.hist_Bstar[sthr,cthr]
##        self.v.zero(100)
##        self.v.inimessg("Computing B* basis;")
##        yesants = self._setcuts(sthr,cthr,forget)[0]
##        self.v.messg("validating minimal antecedents at confidence "+str(confthr)+"...")
##        yesants.tighten(self.v)
##        out = implattice()
##        out.nrtr = self.cl.nrtr
##        self.v.zero()
##        self.v.messg("...computing B* basis at confidence "+str(confthr)+"...")
##        for nod in yesants.keys():
##            "must check support additionally?"
##            self.v.tick()
##            for an in yesants[nod]:
##                "is it guaranteed that an < nod?"
##                out.newrule(slarule(an,nod))
##        if not forget: self.hist_Bstar[sthr,cthr] = out
##        self.v.messg("...done; "+str(out.nrimpls)+" rules found.\n")
##        return out
##
####        for st in self.cl.closeds:
####            "CHECK! this we do just for iceberg above suppth - IS THE SCALE RIGHT?"
####            if st.supp>=sthr:
####                self._validate(st)
####        out = implattice()
####        out.nrtr = self.cl.nrtr
####        self.x.zero()
####        self.x.messg("...computing B* basis at confidence "+str(confthr))
####
######        for st in self.cl.closeds: CHECK!
####
####            if st.supp>=suppth:
####                for an in st.validants:
####                    if an < st:
####                        self.newimpl(an,st)
####
####
####
####    def _validate(self,n):
####        "sift ants to leave only valid ones - all ants at whole lattice known"
####        n.validants = []
####        for g in n.ants:
####            for c in self.cl.closeds:
####                if n < c and g in c.ants:
####                    break
####            else:
####                n.validants.append(g)

if __name__ == "__main__":

    from slarule import printrules

    from trNS import tradNS

##    forget = True
    forget = False

##    filename = "pumsb_star"
##    filename = "cmc_eindh4"
##    supp = 70.0/1473

    filename = "e13"
    supp = 1.0/13

    rl = brulattice(supp,filename)
    
##    print printrules(rl.mingens,rl.nrtr,file(filename+"_IFrl70s.txt","w")), "rules in the iteration free basis."
##
##    rl.findGDgens()
##
##    print printrules(rl.GDgens,rl.nrtr,file(filename+"_GDrl70s.txt","w"),tradNS), "rules in the GD basis."

    BSants = rl.mineBstar(supp,0.83)

    print printrules(BSants,rl.nrtr,file(filename+"_BS83c30s.txt","w")), "B* rules found at conf 0.83."

