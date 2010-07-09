from job import job
from sys import exit

# CAVEAT: CHARACTER '/' IS ASSUMED NOT TO OCCUR AT ALL IN THE DATASET

# EXAMPLES OF USE OF THE job CLASS FOR RUNNING SLATT

# use Borgelt's apriori to compute all frequent closures
# for a dataset and a support bound (in [0,1]):
# items may be strings, not just numbers
todayjob = job("lenses_recoded",0.001)
##todayjob = job("len",0.001)
##todayjob = job("pvotes",0.30)

##todayjob = job("pumsb_star",supp=0.4)
##todayjob = job("toyNouRay",supp=0)
##anotherjob = job("e13",0.99/13)


# compute B* basis, write the rules into a file 
todayjob.run("B*",0.75,show=False,outrules=False)

# compute representative rules, show in console and write on file
todayjob.run("RR",0.75,show=False,outrules=True)

# compute GD basis for conf 1
todayjob.run("GD",show=False)

#to apply confidence boost filter at level 1.2 to RR
todayjob.run("RR",0.75,boost=1.2,show=True)

#now to B*, at boost 1.05, and reducing a bit the output verbosity
##todayjob.run("B*",0.75,boost=1.05,outrules=True,verbose=False)
todayjob.run("B*",0.75,boost=1.1,show=True)

## write off the closures in XML format
todayjob.brulatt.xmlize()
## clattices can be initialized from these XML files
## likewise for brulattices and rerulattices in a
## forthcoming version of slatt, but not in this one

##next demo 
##programming a sequence of experiments to create a plot

##confs = [ 0.75, 0.85, 0.95 ]
##
##resultsRR = {}
##
##resultsBstar = {}
##
##for conf in confs:
##    "representative rules"
##    resultsRR[conf] = todayjob.run("RR",conf)
##    resultsBstar[conf] = todayjob.run("B*",conf)
##
##print "\n\n  Data to plot:\n"
##
##print "Representative rules:"
##print "conf num.rul"
##for c in sorted(resultsRR.keys()):
##    print c, resultsRR[c]
##
##print "B* basis:"
##print "conf num.rul"
##for c in sorted(resultsRR.keys()):
##    print c, resultsBstar[c]
##
##
