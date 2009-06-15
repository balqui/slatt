## to create a transactional version of the Sligro data

## second attempt, join product code, class, and promotion

f = file("Sligro_data_EHV")
##f = file("Sligro_data_EHV-test.txt")

t = file("sligro2.txt","w")

prevkey = ""
s = set([])

for line in f:
    trans = line.split(",")
    key = trans[0].strip()+trans[1].strip()
    item = trans[2].strip()+trans[3].strip()+trans[4].strip('" \n')
    if key != prevkey:
        if len(s)>0:
##            print "[",prevkey,"]"
##            for e in s:
##                print e,
##            print
            for e in s:
                t.write(str(e)+" ")
            t.write("\n")
        s = set([item])
        prevkey = key
    else:
        s.add(item)

##print "[",prevkey,"]"

for e in s:
    t.write(str(e)+" ")
t.write("\n")

##for e in s:
##    print e,
##print
    
f.close()
t.close()
