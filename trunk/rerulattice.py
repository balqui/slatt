"""
Subproject: Slatt
Package: rerulattice
Programmers: JLB

Inherits from slattice, which brings cuts, mingens, and GDgens

Offers:
.mineRR to compute the representative rules for a given confidence using
  corr tightening of transversals of the negative cuts
.hist_RR: dict mapping each supp/conf thresholds tried
  to the repr rules basis constructed according to that method
.mineKrRR (ongoing) to compute a subset of representative rules
  by Kryszkiewicz heuristic,
.hist_KrRR, corresponding dict
.mineBCRR (planned) to compute a representative rules by our
  alternative complete method to Kryszkiewicz
.hist_BCRR, corresponding dict

Notes/ToDo:
.want to be able to use it on file containing larger-support closures
.note: sometimes the supp is lower than what minsupp indicates; this may be
  due to an inappropriate closures file, or due to the fact that indeed there
  are no closed sets in the dataset in between both supports (careful with
  their different scales)
.mingens at a given confidence need also their mns - what is the best way?
.revise and enlarge the local testing
.revise ticking rates
"""

from slattice import slattice
from slarule import slarule
from corr import corr

class rerulattice(slattice):

    def __init__(self,supp,datasetfile="",v=None,xmlinput=False,externalminer=True):
        "call slattice to get the closures and minimal generators"
        slattice.__init__(self,supp,datasetfile,v,xmlinput=xmlinput,externalminer=externalminer)
        self.hist_RR = {}
        self.hist_KrRR = {}

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

    def mineRR(self,suppthr,confthr,forget=False):
        """
        compute the representative rules for the given confidence;
        will provide the iteration-free basis if called with conf 1
        thresholds expected in [0,1] to rescale here
        """
        if confthr == 1:
            return self.findmingens(suppthr)
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_RR.keys():
            return self.hist_RR[sthr,cthr]
        self.v.zero(100)
        self.v.inimessg("Computing representative rules at confidence "+str(confthr)+"...")
        nonants = self.setcuts(sthr,cthr,forget)[1]
        ants = corr()
        self.v.messg("computing potential antecedents...")
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
                ants[nod] = []
                for m in self._faces(nod,nonants[nod]).transv().hyedges:
                    if m < nod:
                        mm = self._findinmingens(nod,m)
                        if mm==None:
                            self.v.errmessg(str(m)+" not found among mingens at "+str(nod))
                        ants[nod].append(mm)
        self.v.zero(500)
        self.v.messg("...checking valid antecedents...")
        ants.tighten(self.v)
        self.v.messg("...done.\n")
        return ants

    def mineKrRR(self,suppthr,confthr,forget=False):
        """
        ditto, just that here we use the incomplete Krysz IDA 2001 heuristic
        check whether this version finds empty antecedents
        """
        sthr = int(self.scale*suppthr)
        cthr = int(self.scale*confthr)
        if (sthr,cthr) in self.hist_KrRR.keys():
            return self.hist_KrRR[sthr,cthr]
        self.v.zero(100)
        self.v.inimessg("Computing representative rules at confidence "+str(confthr)+" using Kryszkiewicz's incomplete heuristic...")
        nonants = self.setcuts(sthr,cthr,forget,skip,cthr)[1]
        ants = corr()
        self.v.messg("computing potential antecedents...")
        for nod in self.closeds:
            """
            see comments same place in mine RR - here using Kr Property 9
            I had here a test self.scale*nod.supp >= sthr*self.cl.nrtr
            """
            self.v.tick()
            if  self.scale*nod.supp >= cthr*nod.mns and \
                self.scale*nod.mxs < cthr*nod.mns:
                "that was the test of Prop 9 - might add here supp constraint"
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

def skip(nod,cthr,scale):
    "what nodes not to skip at setcuts - is scale OK?"
    return scale*nod.supp < cthr*nod.mns or \
       scale*nod.mxs >= cthr*nod.mns

if __name__ == "__main__":

    from slarule import printrules

##    forget = True
    forget = False

##    filename = "pumsb_star"
##    supp = 0.4

    filename = "e13"
    supp = 1.0/13

    rl = rerulattice(supp,filename)
    
##    print printrules(rl.mingens,rl.nrtr,file(filename+"_IFrl30s.txt","w")), "rules in the iteration free basis."
    print printrules(rl.mingens,rl.nrtr), "rules in the iteration free basis."

    rl.findGDgens()

##    print printrules(rl.GDgens,rl.nrtr,file(filename+"_GDrl30s.txt","w")), "rules in the GD basis."
    print printrules(rl.GDgens,rl.nrtr), "rules in the GD basis."

    ccc = 0.81
    
    KrRRants = rl.mineKrRR(supp,ccc)

    print printrules(KrRRants,rl.nrtr), "repr rules found with Kr at conf", ccc

    RRants = rl.mineRR(supp,ccc)

##    print printrules(RRants,rl.nrtr,file(filename+"_RR"+str(ccc)+"c30s.txt","w")), "repr rules found at conf..."
    print printrules(RRants,rl.nrtr), "repr rules found at conf", ccc
