f = open("../data/artikqpf_raw.txt","r")

d=dict()
for line in f:
    t=line.split(",")

    d[t[0].strip('. ')]=t[1].strip('" \t.\n'+chr(10))

f.close()
