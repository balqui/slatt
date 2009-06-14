from clattice import clattice

from trNS import tradNS

supp = 70.0/1473
    
cmcl = clattice(supp,"cmc_eindh4")

print cmcl.closeds[44].__str__(tradNS)

ndi = clattice(supp)

cnt = 0
for line in file("ndi_all70_ed03.txt"):
    cnt += 1
    r = ndi.newclosure(line)

ndicl = set([ cmcl.close(m) for m in ndi.closeds ])

print len(ndicl), "closures of", cnt, "ndi's"

for ee in cmcl.closeds:
    if not ee in ndicl:
        print ee.__str__(tradNS)

        

