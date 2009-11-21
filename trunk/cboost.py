from corr import corr
from slarule import slarule
from slanode import str2node

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

class cboost:

    def __init__(self,ants):
        "ants is RR given as a corr mapping each closure to its list of mingens"
        self.ants = ants

    def filt(self,boost,clatt,rrseconf):
        "return corr with surviving rules under the boost filtering - must organize differently"
        self.outcome = corr()
        for cn in self.ants.keys():
            "check if any antecedent leaves a rule to cn - BRUTE FORCE ALGORITHM"
            self.outcome[cn] = []
            for an in self.ants[cn]:
                goodsofar = True
                conf1 = float(cn.supp)/an.supp
                for cn2 in rrseconf.keys():
                    for an2 in rrseconf[cn2]:
                        if cn.difference(an) <= cn2 and \
                        (an2 < an or (an2==an and cn2!=cn)):
                            totry = allsubsets(set(an.intersection(cn2.difference(an2))))
                            for ss in totry:
                                an3 = ss.union(an2)
                                cn3 = an3.union(cn.difference(an))
                                conf2 = float(clatt.close(cn3).supp)/clatt.close(an3).supp
                                if conf1/conf2 <= boost:
                                    goodsofar = False
                                    break       # breaks for ss 
                        if not goodsofar: break # breaks for an2
                    if not goodsofar: break     # breaks for cn2
                if goodsofar:
                    self.outcome[cn].append(an)
        return self.outcome

if __name__=="__main__":

    from rerulattice import rerulattice
    from slarule import printrules

    filename = "e13"
    supp = 0.99/13 #was 24 but...

    rl = rerulattice(supp,filename+".txt")

    print "Iteration-free basis:"

    print printrules(rl.mingens,rl.nrtr)

    conf = 0.75

    RR = rl.mineRR(supp,conf)

    print "At confidence", conf

    print printrules(RR,rl.nrtr)

    cb = cboost(RR)

    boost = 1.05

    seconf = conf/boost

    RR2 = rl.mineRR(supp,seconf)

    print "At confidence", seconf

    print printrules(RR2,rl.nrtr)

    print "At cboost", boost

    a0 = cb.filt(1.4,rl,RR2)

    print printrules(a0,rl.nrtr)
