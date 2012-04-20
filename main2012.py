from job2012 import job

#bgdsname = "lenses_recoded" # supp 0.001

#bgdsname = "data/votesTr" # supp 0.4, 25 B* rules of high everything

# bgdsname = "data/supermarketTr" # supp 0.2, 467 B* rules, half high; 0.4, 16 between 1.05 and 1.15 aprox; 0.3, 79, some 20 above 1.10 clift; careful bread&cake no clift

## len, pvotes at 0.3, pumsb_star at 0.4, toyNouRay at 0, e13 at 0.99/13

# bgdsname = "data/papers" # supp 0.05 ??

bgdsname = "data/adultrain" # supp 0.1, 184 B* rules, 19 over 1.10 clift + 4 infty

bgsupp = 0.1

print("Computing closures on dataset %s at support %d..." % (bgdsname,bgsupp))

todayjob = job(bgdsname,bgsupp)

print("Computing B* basis at 0.75, no show, no write...")

todayjob.run("B*",0.65)

aaaa = raw_input("Press return to close the window.")
exit(0)

