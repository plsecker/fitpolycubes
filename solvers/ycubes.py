#!/usr/bin/python3
#
#  Author: Rogelio Tomas
#


from numpy import *
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from common.algorithm_x import solve

#Define cube dimensions
side=5



##### Generating ypentacubes functions
def ypentacubesfromdirection(direction):
    y=[]
    body=[]
    zer=[]
    #put the zeros location in a list
    for i in range(3):
        if direction[i]==0:
            zer.append(i)
    # make body (4 cubes in a row pointing in direction)
    for c in range(0,4):
        body.append(direction * c)
    #make the 8 ypentacubes (add the 'arms' onto this body)   
    for izer in range(2):
        for b in [1,-1]:
            up=direction*2
            down=direction*1
            ypentup=list(body)
            ypentdown=list(body)
            up[zer[izer]]=b
            ypentup.append(array(up))
            down[zer[izer]]=b
            ypentdown.append(array(down))
            y.append(array(ypentup))
            y.append(array(ypentdown))
    return y




# Generating box  to uniquely cover later
X=set()
for i in range(side):
    for j in range(side):
        for k in range(side):
            X.add((i, j, k))

# Building Y, covering subsets
def addsubs(ypent):
    global Y, count
    maxx, maxy,maxz = ypent.max(axis=0)    
    minx, miny,minz = ypent.min(axis=0)
    
    for i in range(-minx, side-maxx):
        for j in range(-miny, side-maxy):
            for z in range(-minz, side-maxz):
                tiles=ypent+array([i,j,z])
                #print tiles.min()
                tilestuple = [tuple(map(int, tile)) for tile in tiles]
                Y[count]=tilestuple
                count=count+1
            

# Subcolections
Y= {}
count=0 # counter of subcolection
for i in range(3):
    vec=array([0,0,0])
    vec[i]=1
    ypens=ypentacubesfromdirection(vec)
    for pen in ypens:
        addsubs(pen)
        


print (count)



# Putting X in the required format for solve()
#X = {j: set() for j in X}
Z={}
for j in X:
    Z[j]=set()
X=Z

for i in Y:
    for j in Y[i]:
        X[j].add(i)

# Exact cover solver
sol=solve(X,Y)



###### Functions to mirror solutions
def flipxy(xy, case):
    if case==1:
        return tuple([longside-1-xy[0], xy[1]])
    if case ==2:
        return tuple([xy[0], smallside-1-xy[1]])
    if case ==3:
        return tuple([longside-1-xy[0], smallside-1-xy[1]])

def flip(x, case):
    fli=[]
    for e in x:
        fli.append(flipxy(array(e), case))
    return fli

def flipset(x, case):
    fli=set()
    for e in x:
        fli.add(frozenset(flip(e, case)))
    return fli

##################

# counting, finding unique and symmetric solutions and output
fname = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/solutions.dat")
f=open(fname,"w")
f.write("#Ypentacubes\n")
f.close()

c=0
for solution in sol:
    c=c+1
    print(c)
    sol_str = "".join([str(Y[p_index]) for p_index in solution])
    with open(fname, "a") as f:
        f.write(f"{c}\n{sol_str}\n")


#import pickle
#
#pickle.dump(solset, open("/afs/cern.ch/user/r/rtomas/w1/YpentaCubes/SolutionSet.pickle","w"))



