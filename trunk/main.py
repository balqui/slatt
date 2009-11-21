from job import job

# CAVEAT: CHARACTER '/' IS ASSUMED NOT TO OCCUR AT ALL IN THE DATASET

# EXAMPLES OF USE OF THE job CLASS FOR RUNNING SLATT

todayjob = job("pumsb_star",supp=0.6)

# GD basis for conf 1
todayjob.run("GD")

# B* basis, write the rules into a file 
todayjob.run("B*",0.75,outrules=True)

# to see the rules - can combine with outrules as well
# rules come labeled with width, confidence, and support 
todayjob.run("RR",0.75,show=True,outrules=True)

#to apply confidence boost filter at level 1.2 to RR
todayjob.run("RR",0.75,boost=1.2,show=True)

#now at boost 1.05, and reducing a bit the output verbosity
todayjob.run("RR",0.75,boost=1.05,outrules=True,verbose=False)

#can reduce a bit verbosity for whole job, not just run - still a bit verbose
#also, items are strings, not just numbers
anotherjob = job("lenses_recoded",0.99/24,verbose=False)

anotherjob.run("GD")

anotherjob.run("B*",0.8,show=True)


#programming a sequence of experiments to create a plot

confs = [ 0.75, 0.85, 0.95 ]

resultsRR = {}

resultsBstar = {}

for conf in confs:
    "representative rules"
    resultsRR[conf] = todayjob.run("RR",conf)
    resultsBstar[conf] = todayjob.run("B*",conf)

print "\n\n  Data to plot:\n"

print "Representative rules:"
print "conf num.rul"
for c in sorted(resultsRR.keys()):
    print c, resultsRR[c]

print "B* basis:"
print "conf num.rul"
for c in sorted(resultsRR.keys()):
    print c, resultsBstar[c]

