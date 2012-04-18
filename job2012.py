from brulattice import brulattice
from rerulattice import rerulattice
from cboost2012 import cboost
from slarule import printrules, slarule

class job:
    """more useful jobs in job.py
    here only specifics for paper on conditional lift and leverage
    working only on B* for the time being
    """

    def __init__(self,datasetfilename,supp,verbose=True):
        """
        job consists of 
          dataset file name, extension ".txt" explicitly added
          support threshold in [0,1],
        """
        self.verb = verbose
        self.datasetfilename = datasetfilename
        self.supp = supp
        self.brulatt = None

    def run(self,basis,conf=0.66,cblt=1.1,show=True,outrules=False,verbose=True):
        """
        the run method receives
          basis, must be always B* for now
          confidence threshold in [0,1],
          cblt threshold for cboost, clift, clev in [1,infty)
          show: whether rules will be shown interactively
          outrules: whether rules will be stored in a file
        """
        boost = cblt
        if basis == "B*":
            basis2 = "Bstar" # for filenames
            if self.brulatt is None:
                self.brulatt = brulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.brulatt.xmlize()
            self.brulatt.v.verb = verbose and self.verb
            latt = self.brulatt
            rules = self.brulatt.mineBstar(self.supp,conf) ##,cboobd=boost) 
            cb = cboost(rules)
            res = cb.add_eval(latt)
            print
            for c in res.keys():
                for (a,i,e,b,d) in res[c]:
                    print slarule(a,c)
                    print "       ", "clift:", i, "clev:", e
                    print "       due to", slarule(b,d)
##            secondminer = self.brulatt.mineBstar
        else:
            print("Basis must be B*.")
        aaaa = raw_input("Press return.")
        exit(-1)
        warn = ""
        bv = ""
        if boost>0:
            print "Filtering rules at confidence boost", boost
            warn = "Confidence-boost filtered "
            bv = "_b%2.3f"%boost
            cb = cboost(rules)
            seconf = conf/boost
            blockers = secondminer(self.supp,seconf)
            survived = cb.filt(boost,latt,blockers)
            rules = survived
        count = None
        if outrules:
            outrulesfile = file(self.datasetfilename+basis2+("_c%2.3f"%conf)+("_s%2.3f"%self.supp)+bv+".txt","w")
            count = printrules(rules,latt.nrtr,outrulesfile,doprint=True)
        if show:
            print "\n\n"
            count = printrules(rules,latt.nrtr,outfile=None,doprint=True)
        if not count:
            count = printrules(rules,latt.nrtr,outfile=None,doprint=False)
        print warn+basis2+" basis on "+self.datasetfilename+".txt has ", count, "rules of confidence at least", conf
        return count

if __name__=="__main__":

    testjob = job("e13",1/13.01)
    testjob.run("B*",conf=0.6,show=True)
    testjob.run("B*",conf=0.55,show=False)
    testjob.run("RR",conf=0.55,show=False)

