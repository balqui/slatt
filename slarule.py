"""
Project: Slatt
Package: slarule
Creation: december 4th, 2008, deeply revised since
Programmers: JLB

Purpose: handle operations on rules, mainly printing them out

Notes:
.rules are slanode itset pairs, antecedent -> consequent
.plus parameters: conf, thr, width...
.values are correct only if antecedent subset of consequent
.slanodes may not be actually closed itemsets (hence may not be lattice nodes)
..but need to have their supp and mns and mxs values anyway
.neg initial values to know easily whether correct values already computed

ToDo:
.think whether scale should play a role
.more exhaustive testing necessary
"""


from slanode import slanode, str2node
from verbosity import verbosity

class slarule:
    "itset pair to be used as a rule or implication"

    def __init__(self,a,c,vb=None):
        """
        vb verbosity object for errmessg's
        """
        if vb != None:
            self.v = vb
        else:
            self.v = verbosity()
        self.an = a
        self.cn = c
        self.widthval = -1
        self.wdn = -1
        self.wup = -1
        self.apprwidthval = -1
        self.confval = -1

    def supp(self,nrtr=0):
        if nrtr == 0:
            return self.cn.supp
        return float(self.cn.supp)/nrtr

    def sets(self):
        return (self.an,self.cn)

    def conf(self):
        """"
        recall: antec must be a subset of conseq
        returns float in [0,1] for today
        an.supp should be always defined and nonzero now
        (leave purposedly unhandled zero-division exception)
        """
        if self.confval >= 0:
            return self.confval
        if self.an.supp == 0:
            "will raise shortly a zero-division exception"
            self.v.errmessg("Unexpected zero support for"+str(self.an))
        self.confval = float(self.cn.supp)/self.an.supp
        return self.confval

    def width(self,nrtr=0):
        """
        compute upper, lower, and min width, floats in [0,1] for now
        uses mxs of cn and mns of an
        must see what happens to undefined widths (also wrt support bound)
        an.supp should be always defined and nonzero now
        (leave purposedly unhandled zero-division exception)
        """
        if self.widthval >= 0:
            return self.widthval
        self.wdn = 0
        self.wup = 0
        self.widthval = 0
        if self.an.supp == 0:
            "will raise shortly a zero-division exception"
            self.v.errmessg("Unexpected zero support for"+str(self.an))
        if self.an.supp < nrtr or nrtr==0:
            "must rethink this part"
            self.wdn = float(self.an.mns)/self.an.supp
            self.widthval = self.wdn
        if self.cn.mxs != 0:
            self.wup = float(self.cn.supp)/self.cn.mxs
            if self.widthval == 0:
                self.widthval = self.wup
            else:
                self.widthval = min(self.wup,self.wdn)
        return self.widthval
        
    def __str__(self,trad={}):
        s = ""
        for el in sorted(self.an):
            "rest of element is item class and promotion code"
            if el.split('.')[0] in trad.keys(): el = trad[el.split('.')[0]]+el.split('.')[2]
            s += el + " "
        s += "=>"
        for el in sorted(self.cn):
            if not el in self.an:
                if el.split('.')[0] in trad.keys(): el = trad[el.split('.')[0]]+el.split('.')[2]
                s += " " + el
        return s

    def outstr(self,nrtr,trad={}):
        "extended version of __str__ with conf, supp"
        nothing = ""
        out = "["
        out += " c: " + ("%3.3f" % self.conf())
        if self.supp(nrtr) < 0.1: nothing = " "
        out += " s: " + nothing + ("%3.3f%%" % (100.0*self.supp(nrtr)))
        out += " ] "
        out += self.__str__(trad)
        return out

def printrules(dic,nrtr,outfile=None,trad={},reflex=False,confbound=0.0,doprint=True):
        """
        auxiliary method, outside the class!
        dic, a dict mapping consequents to antecedents
        nrtr, dataset size
        outfile, filename for the output
        trad, dict mapping item translations
        reflex at True forces to write rules with empty rhs
        """
        cnt = 0
        for cn in dic.keys():
            for an in dic[cn]:
                if an < cn or reflex:
                    r = slarule(an,cn)
                    if r.conf() >= confbound:
                        cnt += 1
                        if doprint:
                            if not outfile: print r.outstr(nrtr,trad)
                            else: outfile.write(r.outstr(nrtr,trad)+"\n")
# OPTION: NO SUPP/CONF VALUES:
#                            else: outfile.write(str(r)+"\n")
        return cnt


if __name__=="__main__":

    print "slatt module slarule called as main and running as test..."

    an = slanode(["a","b"])

    cn = slanode(["a","b","c","d"])

    an.supp = 5

    an.mns = 6
    
    cn.supp = 4

    cn.mxs = 3


    r = slarule(an,cn)

    print r, ";   s:%3d,  c:%2.2f,  w:%2.2f" % (r.supp(),r.conf(),r.width())


