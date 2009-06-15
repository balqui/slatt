
from rerulattice import rerulattice
from brulattice import brulattice
from slarule import slarule, printrules

## cmc-specific recoding:
#from trNS import tradNS

def make_dict():
    f = open("../data/artikqpf_raw.txt","r")

    d=dict()
    n=0
    for line in f:
        t=line.split(",")

        d[t[0].strip('. ')]=t[1].strip('" \t.\n'+chr(10))
        n+=1

    f.close()

    return d

def blocked(an,cn,dic,blck):
    "auxiliary function: whether some rule in dic blocks an->cn at that factor"
    r1 = slarule(an,cn)
    for cn2 in dic.keys():
        for an2 in dic[cn2]:
            r2 = slarule(an2,cn2)
            if an2 < an and cn - an <= cn2 and r1.conf() <= blck*r2.conf():
                return True
    return False

dd = make_dict()

## SPECIFY HERE THE FILENAME FOR THE DATASET, EXTENSION .txt WILL BE ASSUMED
## SPECIFY AS WELL PARAMETERS: support, confidence, blocking factor threshold
## FINALLY, SPECIFY WHICH TASKS TO BE PERFORMED - RECOMMEND: compute but do not
## print before knowing how big the printout is

filename = "..\data\Sligro_data_EHV.data"

## support and confidence to be given also here in the range [0,1]
## blocking factor threshold expected here as well, range [1,2] recommended
## can be computed through squint via program hints.py

supp = 0.001
conf = 0.8
blck = 1.4
##supp = 540.0/1473
##conf = 0.65

##filename = "e13"
##supp = 1.0/13
##conf = 0.83

## choose which basis to compute

compute_B_star_rules = True

print_nonblocked = True

compute_repr_rules = False

## THE REST OF THE PROGRAM WILL DO AS REQUIRED - except for small tweakings

if compute_B_star_rules:

    rlfile = "%s_Bs%2.3f%%s%2.3f%%c.txt" % (filename,100.0*supp,100.0*conf)

    rl1 = brulattice(supp,filename)
    
    BSants = rl1.mineBstar(supp,conf)

##    print printrules(BSants,rl1.nrtr,file(rlfile,"w"),tradNS), "B* rules found at supp %2.3f%% and conf %2.3f%%." % (100.0*supp,100.0*conf)

    print printrules(BSants,rl1.nrtr,file(rlfile,"w"),dd), "B* rules found at supp %2.3f%% and conf %2.3f%%." % (100.0*supp,100.0*conf)

##    print printrules(BSants,rl1.nrtr), "B* rules found at supp %2.3f%% and conf %2.3f%%." % (100.0*supp,100.0*conf)

    cnt = 0
    nonblocked = []
    for cn in BSants.keys():
        for an in BSants[cn]:
            if not blocked(an,cn,BSants,blck):
                cnt += 1
                nonblocked.append((an,cn))
    print cnt, "B* rules not blocked at threshold", blck
    
    if print_nonblocked:
        whichrules = [ slarule(a,c).outstr(rl1.nrtr,dd) for (a,c) in nonblocked ]
        for sr in sorted(whichrules,reverse=True):
            print sr 
        

if compute_repr_rules:

    rlfile = "%s_RR%2.3f%%s%2.3f%%c.txt" % (filename,100.0*supp,100.0*conf)

    gdfile = "%s_GD%2.3f%%s.txt" % (filename,100.0*supp)

    rl2 = rerulattice(supp,filename)
    
    RRants = rl2.mineRR(supp,conf)

    rl2.findGDgens()

    print printrules(rl2.GDgens,rl2.nrtr,file(gdfile,"w"),dd), "GD rules found at supp %2.3f%%." % (100.0*supp)

    print printrules(RRants,rl2.nrtr,file(rlfile,"w"),dd), "RR rules found at supp %2.3f%% and conf %2.3f%%." % (100.0*supp,100.0*conf)

    cnt = 0
    nonblocked = []
    for cn in RRants.keys():
        for an in RRants[cn]:
            if not blocked(an,cn,RRants,blck):
                cnt += 1
                nonblocked.append((an,cn))
    print cnt, "RR rules not blocked at threshold", blck
    
    if print_nonblocked:
        whichrules = [ slarule(a,c).outstr(rl1.nrtr,dd) for (a,c) in nonblocked ]
        for sr in sorted(whichrules,reverse=True):
            print sr 

    
