from corr import corr
from slarule import slarule
from slanode import str2node

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
                        if cn.difference(an) <= cn2 and an2 <= an:
                            totry = allsubsets(set(an.difference(an2)))
                            for ss in totry:
                                an3 = ss.union(an2)
                                if an3 < an:
                                    cn3 = cn.difference(an).union(an3)
                                    conf2 = float(clatt.close(cn3).supp)/clatt.close(an3).supp
                                    if conf1 <= conf2*boost:
                                        goodsofar = False
                                        break   # breaks for ss and skips else
                            else:
                                for elem in cn2.difference(cn):
                                    cn3 = set([elem]).union(cn)
                                    conf2 = float(clatt.close(cn3).supp)/an.supp
                                    if conf1 <= conf2*boost:
                                        goodsofar = False
                                        break   # breaks for elem
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

    rl = rerulattice(supp,filename)

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
