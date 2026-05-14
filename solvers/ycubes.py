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
hside=int(side/2)
for i in range(-hside,hside+1):
    for j in range(-hside,hside+1):
        for k in range(-hside,hside+1):
            X.add(tuple(array([i,j,k])))

# Building Y, covering subsets
def addsubs(ypent):
    global Y, count
    maxx, maxy,maxz = ypent.max(axis=0)    
    minx, miny,minz = ypent.min(axis=0)
    
    for i in range(-hside-minx, hside+1-maxx):
        for j in range(-hside-miny, hside+1-maxy):
            for z in range(-hside-minz, hside+1-maxz):
                tiles=ypent+array([i,j,z])
                #print tiles.min()
                tilestuple=map(tuple,list(tiles))
                Y[count]=list(tilestuple)
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
f=open("solutions.dat","w")
f.write("#ypentacubes")
f.close()
c=0
cc=0
cu=0
unique=set()
uniqueflip=set()
for i in sol:
    c=c+1
    print(c)
#    solset=set()
#    f=open("solutions.dat","a")
#    f.write(format(c))
#    print(i)
#    for p in i:
#        solset.add(frozenset(Y[p]))
#        f.write(format(Y[p]))
#    f.close()
    
    #if solset not in unique and solset not in uniqueflip:
    #    s=frozenset(solset)
    #    unique.add(s)
    #    s1=frozenset(flipset(solset,1))
    #    uniqueflip.add(s1)
    #    s2=frozenset(flipset(solset,2))
    #    uniqueflip.add(s2)
    #    s3=frozenset(flipset(solset,3))
    #    uniqueflip.add(s3)
    #    cu=cu+1
    #    symlabel=""
    #    if s.issubset(s1) or s.issubset(s2) or s.issubset(s3):
    #        symlabel="Symmetric!"
    #        cc=cc+1
    #    print >> f, "#", cu
    #    for p in i:
    #        print >>f, Y[p]
        
f=open("solutions.dat","a")
f.write("Elements in Y".format(Y))
f.write("Total combinations".format(c))
f.write("Total unique".format(cu))
f.write("Total symmetric".format(cc))
f.close()


#import pickle
#
#pickle.dump(solset, open("/afs/cern.ch/user/r/rtomas/w1/YpentaCubes/SolutionSet.pickle","w"))



