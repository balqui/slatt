"""
Project: Slatt
Package: verbosity
Created: Apr 16th, 2009, on the basis of a lot of previous work, then revised
Programmers: JLB

Offers:
.handling of verbosity including messages and progress reporting
.please use this class for ALL terminal output in the project

ToDo:
.add some testing in the __main__
.some day it will become a GUI
"""

class verbosity:
    """
    Offers messaging of what is ongoing and ascii-based progress report
    Everything can be put off through the verbosity level
    """

    def __init__(self,verb=True):
        """
        verbosity;
        lim and count for the progress-reporting ticks;
        """
        self.verb = verb
        self.lim = 0
        self.count = 0

    def messg(self,s):
        if not self.verb:
            return
        print s,

    def inimessg(self,s):
        "initiates a sequence of related messg's"
        if not self.verb:
            return
        print "\n[Slatt] "+s,

    def errmessg(self,s):
        print "\n[Slatt] Something is wrong! "+s

    def zero(self,newlim=0):
        self.count = 0
        if newlim>0: self.lim = newlim

    def tick(self):
        if not self.verb:
            return
        self.count += 1
        if self.count == self.lim:
            print '.',
            self.count = 0

    def __str__(self):
        s = ""
        s += ("Verbosity: " + str(self.verb))
        s += ("\nLimit: " + str(self.lim))
        s += ("\nCount: " + str(self.count))
        return s+"\n"

if __name__=="__main__":
    pass

##    print "slatt module verbosity called as main and running as test..."
