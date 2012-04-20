from job2012 import job

bgdsname = "lenses_recoded"

## len, pvotes at 0.3, pumsb_star at 0.4, toyNouRay at 0, e13 at 0.99/13

bgsupp = 0.001

print("Computing closures on dataset %s at support %d..." % (bgdsname,bgsupp))

todayjob = job(bgdsname,bgsupp)

print("Computing B* basis at 0.75, no show, no write...")

todayjob.run("B*",0.65)

aaaa = raw_input("Press return to close the window.")
exit(0)

