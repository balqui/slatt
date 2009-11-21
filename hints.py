#! /usr/bin/python

#datasetfile = "../data/Sligro_data_EHV.data"

datasetfile = None

if datasetfile == None:
    datasetfile = raw_input("Dataset File Name? ")

dataset = file("%s.txt" % datasetfile)
nrocc = 0
nrtr = 0
uset = set([])
for line in dataset:
    nrtr += 1
    for el in line.strip().split():
        if len(el)>0:
            nrocc += 1
            uset.add(el)
nrits = len(uset)

print "Found", nrtr, "transactions;", nrits, "items;", nrocc, "occurrences."

print "Suggested supports in percent and absolute value, based on confidence:"
q = 0.05
for s in range(0,8):
    sp = 4.0*q*nrocc/(nrtr*nrits)
    print "%2.2f: %2.3f %d" % (1-q,100*sp,int(sp*nrtr))
    q += 0.05
