from brulattice import brulattice
from rerulattice import rerulattice
from cboost import cboost
from slarule import printrules

class job:

    def __init__(self,datasetfilename,supp,verbose=True):
        """
        duplicate lattice to be simplified (but first attempt failed)
        job consists of 
          dataset file name, extension ".txt" explicitly added
          support threshold in [0,1],
        """
        self.verb = verbose
        self.datasetfilename = datasetfilename
        self.supp = supp
        self.brulatt = None
        self.rerulatt = None

    def run(self,basis,conf=1.0,boost=0.0,show=False,outrules=False,verbose=True):
        """
        the run method consists of
          target basis ("B*", "RR", or "GD")
          confidence threshold in [0,1],
          confidence boost threshold in [1,infty] recommended in [1,2], say 1.1
          show: whether rules will be shown interactively
          outrules: whether rules will be stored in a file
        """
        basis2 = basis
        if basis == "B*":
            basis2 = "Bstar" # for filenames
            if self.brulatt is None:
                self.brulatt = brulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.brulatt.xmlize()
            self.brulatt.v.verb = verbose and self.verb
            latt = self.brulatt
            rules = self.brulatt.mineBstar(self.supp,conf,cboobd=boost) # careful here
            secondminer = self.brulatt.mineBstar
        elif basis == "RR":
            if self.rerulatt is None:
                self.rerulatt = rerulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.rerulatt.xmlize()
            self.rerulatt.v.verb = verbose and self.verb 
            latt = self.rerulatt
            rules = self.rerulatt.mineRR(self.supp,conf)
            secondminer = self.rerulatt.mineRR
        elif basis == "GD":
            conf = 1.0
            if self.rerulatt is None:
                self.rerulatt = rerulattice(self.supp,self.datasetfilename)
            self.rerulatt.v.verb = verbose and self.verb 
            latt = self.rerulatt
            self.rerulatt.findGDgens(self.supp)
            rules = self.rerulatt.GDgens
            secondminer = self.rerulatt.mineRR
        else:
            "a print because there may be no lattice and no verbosity - to correct soon"
            print "Basis unavailable; options: B*, RR, GD"
            return 0
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
        print warn+basis+" basis on "+self.datasetfilename+".txt has ", count, "rules of confidence at least", conf
        return count

if __name__=="__main__":

    testjob = job("e13",1/13.01)
    testjob.run("B*",conf=0.6,show=True)
    testjob.run("B*",conf=0.55,show=False)
    testjob.run("GD")
    testjob.run("GD",outrules=True)
    cnt = testjob.run("RR",conf=0.6,show=True)
    print cnt
