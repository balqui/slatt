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

    def run(self,basis,conf=0.66,cblt=1.1):
        """
        the run method receives
          basis, must be always B* for now
          confidence threshold in [0,1],
          cblt threshold for cboost, clift, clev in [1,infty)
        """
        boost = cblt
        if basis == "B*":
            basis2 = "Bstar" # for filenames
            if self.brulatt is None:
                self.brulatt = brulattice(self.supp,self.datasetfilename,xmlinput=True)
            self.brulatt.xmlize()
            self.brulatt.v.verb = self.verb
            latt = self.brulatt
            rules = self.brulatt.mineBstar(self.supp,conf) ##,cboobd=boost) 
            cb = cboost(rules)
            res = cb.add_eval(latt)
            outfilename = self.datasetfilename + "_" + basis2 
            outfilename += ("_c%2.3f"%conf) 
            outfilename += ("_s%2.3f"%self.supp)
            outfilename += ("_l%2.3f"%cblt) + ".txt"
            outfile = open(outfilename,"w")
            outfile.write("num\tconf\tclift\tclev\tantec\t\tconseq\n")
            count = 0
            for c in res.keys():
                for (a,i,e) in res[c]:
                    count += 1
                    r = slarule(a,c)
                    outfile.write(str(count) + " ")
                    outfile.write(("%2.3f" % r.conf()) + " ")
                    outfile.write(("%2.3f" % i) + " ")
                    outfile.write(("%2.3f" % e) + " ")
                    outfile.write(str(a) + " --> ")
                    outfile.write(str(c) + "\n")
            outfile.close()
            print "\n\n", count, "rules written on file", outfilename
        else:
            print("Basis must be B*.")
            aaaa = raw_input("Press return.")
            exit(-1)

if __name__=="__main__":

    testjob = job("e13",1/13.01)
    testjob.run("B*",conf=0.6,show=True)
    testjob.run("B*",conf=0.55,show=False)
    testjob.run("RR",conf=0.55,show=False)

