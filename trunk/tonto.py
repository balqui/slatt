print "SANDBOX FILE FOR THE PROJECT"

print "This file can be run and changed to see the Subversion thing at work"

for i in range(10):
    for j in range(10):
        if (i,j) == (5,5):
            print "at (5,5)"
            break
    else:
        print "at inner else with", i, j
        continue

    print "after inner else with", i, j
    break

else:
    print "at outer else - I should not be here!", i, j

print "after outer else with", i, j




        
