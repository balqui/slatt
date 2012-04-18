from job2012 import job

bgdsname = "lenses_recoded"

## len, pvotes at 0.3, pumsb_star at 0.4, toyNouRay at 0, e13 at 0.99/13

bgsupp = 0.001

print("Computing closures on dataset %s at support %d..." % (bgdsname,bgsupp))

todayjob = job(bgdsname,bgsupp)

print("Computing B* basis at 0.75, no show, no write...")

todayjob.run("B*",0.75,show=True,outrules=False)

aaaa = raw_input("Press return to close the window.")
exit(0)

print("Computing representative rules at 0.75, show in console and write on file...")
todayjob.run("RR",0.75,show=True,outrules=True)

print("Computing GD basis for conf 1...")
todayjob.run("GD",show=True)

#to apply confidence boost filter at level 1.2 to RR
todayjob.run("RR",0.75,boost=1.1,show=True)

#now to B*, at boost 1.05, and reducing a bit the output verbosity
##todayjob.run("B*",0.75,boost=1.05,outrules=True,verbose=False)
todayjob.run("B*",0.75,boost=1.1,show=True)

## write off the closures in XML format
todayjob.brulatt.xmlize()
## clattices can be initialized from these XML files
## likewise for brulattices and rerulattices in a
## forthcoming version of slatt, but not in this one

