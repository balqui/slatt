"""
Subproject: Slatt
Package: brulattice
Programmers: JLB

Compute B* basis - inherits from clattice

Offers:

.hist_Bstar: dict mapping each supp/conf thresholds tried
  to the B* rules basis constructed according to that method
.mineBstar to compute the B* basis from positive cuts
  via corr tightening

Notes/ToDo:
.want to be able to use it on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
..due to an inappropriate closures file, or due to the fact that indeed there
..are no closed sets in the dataset in between both supports (careful with
..their different scales).

other ToDo:
.revise and enlarge the local testing
.revise ticking rates
"""

from corr import corr
from clattice import clattice

class brulattice(clattice):

    def __init__(self,supp,datasetfile="",v=None,xmlinput=False,externalminer=True):
        clattice.__init__(self,supp,datasetfile,v,xmlinput=xmlinput,externalminer=externalminer)
        self.hist_Bstar = {}

    def dump_hist_Bstar(self):
        "prints out all the Bstar bases computed so far"
        for e in self.hist_Bstar.keys():
            print "At support", (e[0]+0.0)/self.scale,
            print "and confidence", (e[1]+0.0)/self.scale
            print self.hist_Bstar[e]

    def mineBstar(self,suppthr,confthr,forget=False,cboobd=0):
        """
        compute the Bstar basis for the given confidence and, possibly,
        conf boost; if present, use cboost bound to spare exploring some
        closures (but tgat might not work now);
        thresholds in [0,1], rescaled into [0,self.x.scale] inside
        TODO: CHECK SUPPTHR COMPATIBLE WITH X.SUPPTHR
        NOW THIS IS BEING DONE ELSEWHERE BUT MAYBE SHOULD BE HERE
        """
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        yesants = None
        if (sthr,cthr) in self.hist_Bstar.keys():
            yesants = self.hist_Bstar[sthr,cthr]
            if cboobd == 0: return yesants
        self.v.zero(100)
        self.v.inimessg("Computing B* basis at confidence "+str(confthr))
        if cboobd != 0:
            self.v.messg(" and confidence boost "+str(cboobd))
        if yesants is None:
            yesants = self.setcuts(sthr,cthr,forget,skip,cboobd)[0]
            self.v.messg("validating minimal antecedents...")
            yesants.tighten(self.v)
        if not forget: self.hist_Bstar[sthr,cthr] = yesants
        if cboobd > 0:
            "filter according to boost bound"
            filt = self.mineBstar(suppthr,confthr/cboobd,forget)
            outcome = corr()
            for cn in yesants:
                "check if any antecedent leaves a rule to cn - BRUTE FORCE ALGORITHM"
                outcome[cn] = []
                for an in yesants[cn]:
                    goodsofar = True
                    conf1 = float(cn.supp)/an.supp
                    for cn2 in filt:
                        for an2 in filt[cn2]:
                            if cn.difference(an) <= cn2 and an2 <= an:
                                totry = allsubsets(set(an.difference(an2)))
                                for ss in totry:
                                    an3 = self.close(ss.union(an2))
                                    if an3 < an:
                                        cn3 = cn.difference(an).union(an3)
                                        conf2 = float(self.close(cn3).supp)/an3.supp
                                        if conf1 <= conf2*cboobd:
                                            goodsofar = False
                                            break   # breaks for ss and skips else
                                else:
                                    for elem in cn2.difference(cn):
                                        cn3 = set([elem]).union(cn)
                                        conf2 = float(self.close(cn3).supp)/an.supp
                                        if conf1 <= conf2*cboobd:
                                            goodsofar = False
                                            break   # breaks for elem
                            if not goodsofar: break # breaks for an2
                        if not goodsofar: break     # breaks for cn2
                    if goodsofar:
                        outcome[cn].append(an)
        else:
            outcome = yesants
        return outcome


def skip(nod,cb,scale):
    "what nodes to skip at setcuts - need scale?"
    return nod.supp <= cb * nod.mxs

## allsubsets is being moved s/w else - remove from here

def allsubsets(givenset):
    "construct powerset of aset, list of all subsets"
    aset = givenset.copy()
    for e in aset:
        aset.remove(e)
        p = allsubsets(aset)
        q = []
        for st in p:
            s = st.copy()
            s.add(e)
            q.append(s)
        return p+q
    return [ set([]) ]

if __name__ == "__main__":

    from slarule import printrules

##    forget = True
    forget = False

##    filename = "pumsb_star"
##    supp = 0.4

    filename = "e13"
    supp = 1.0/13

    rl = brulattice(supp,filename)
    
##    rl.v.verb = False

    ccc = 0.7
    cbb = 1.05
    b = rl.mineBstar(supp,ccc,cboobd=cbb)
    print "\n", printrules(b,rl.nrtr)

    
##    for ccc in [0.7,0.75,0.8]:
##        for cbb in [1,1.05,1.1,1.15,1.2,1.25,1.3,1.35,1.4,1.45,1.5]:
##            b = rl.mineBstar(supp,ccc,cboobd=cbb)
##            print printrules(b,rl.nrtr,doprint=False), "B* rules found at conf", ccc, "boost", cbb
    

