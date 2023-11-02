# -*- coding: utf-8 -*-
"""
Created on Sat Jun  3 14:44:27 2023

@author: mkravche



Modified
"""

__author__ = "Mikhail Kravchenko"
__contact__="mkravche@vt.edu"
__license__="GPLv3"

import gmsh
import sys

import numpy as np


DEBUG_VIEW=True

MODEL_NAME = "cantilever_3P_20230701"
# scale = 1e-6
# CLen = 20*scale
# CWidth = 4*scale
# CHeight=1*scale
scale = 1e-6
CLen = 4*scale
CWidth = 4*scale
CHeight=0.2*scale
CPortExtrude = 1*scale
CPortGap = 0.5*scale

inFeedWidth=3*scale
inMarginBudget = CWidth - inFeedWidth
inMargin_1=0.5*inMarginBudget
inMargin_2=0.5*inMarginBudget
inExtrude=CPortExtrude

bodyLength=CLen

outExtrude=CPortExtrude
P1_SpoutWidth=2*scale
P2_SpoutWidth=1*scale
outGap=0.5*scale
outMarginBudget = CWidth - P1_SpoutWidth - P2_SpoutWidth - outGap
outMargin_1=0.5*outMarginBudget
outMargin_2=0.5*outMarginBudget



checksum1 = inMargin_1 + inMargin_2 + inFeedWidth
checksum2 = outMargin_1 + outMargin_2 + outGap + P1_SpoutWidth + P2_SpoutWidth

assert checksum1 == checksum2 
assert checksum1 == CWidth

if checksum1 == checksum2 and checksum1 == CWidth:
    pass
else:
    #Error
    raise Exception("Boundary length checksum failed. Bad parameters.")


#gmsh parameters
lc = 2e-7 #Point mesh tolerance



gmsh.initialize()
gmsh.model.add(MODEL_NAME)

points = []

X=0
Y=0
Z=0
P = lambda : points.append((X,Y,Z))


X+=inExtrude;P()
Y-=inMargin_1;P()
X-=inExtrude;P()
Y-=inFeedWidth;P()
X+=inExtrude;P()
Y-=inMargin_2;P()

#print
# x1,y1 = X, Y

X+=bodyLength ;P()

# #print
# x2,y2 = X, Y
# print(f"location {x1, y1=}   {x2, y2=}  center {(x1+x2)/2, y1/2 =}")

Y+=outMargin_1 ;P()
X+=outExtrude ;P()
Y+=P1_SpoutWidth ;P()
X-=outExtrude ;P()
Y+=outGap ;P()
X+=outExtrude ;P()
Y+=P2_SpoutWidth ;P()
X-=outExtrude ;P()
Y+=outMargin_2 ;P()
#X-=bodyLength ;P();

PointID = 1
for x,y,z in points:
    gmsh.model.geo.addPoint(x,y,z,lc,PointID)
    PointID +=1
    
LineID=1
lines = [(i+1,i+2) for i in range(len(points)-1)]
lines.append((len(points),1))
for a,b in lines:
    gmsh.model.geo.addLine(a,b,LineID)
    LineID+=1
    
loop = [i+1 for i in range(LineID-1)]

SurfaceID = 1
gmsh.model.geo.addCurveLoop(loop,SurfaceID) # Surface ID is representing loop id.
gmsh.model.geo.addPlaneSurface([SurfaceID],SurfaceID)

gmsh.model.geo.synchronize()
gmsh.model.mesh.generate(2)

#generate the 2D mesh

#output mesh file and check

# gmsh.write(MODEL_NAME+"2Dplane.msh")

# exit()

#

# EXTRUDE MESH   from tutorial 

    #  BUT here, instead of only extruding the geometry, we also want to extrude the
    # 2D mesh. This is done with the same `extrude()' function, but by
    # specifying element 'Layers' (2 layers in this case, the first one with 8
    # subdivisions and the second one with 2 subdivisions, both with a height of
    # h/2). The number of elements for each layer and the (end) height of each
    # layer are specified in two vectors:
    ###  h = 0.1
    ###  ov = gmsh.model.geo.extrude([(2, 1)], 0, 0, h, [8, 2], [0.5, 1])


#a vector of (dim, tag) pairs,  then x,y,z 


#calculating the laryer information

refN = np.ceil(CHeight/lc + 1)
h0 = CHeight/refN

gmsh.model.geo.extrude([(2,1)],0,0,CHeight, [refN], [1])



# How to punch holes with open cascade
#cylinder = gmsh.model.occ.addCylinder(0.5, 0,0.2,0, B, 0, r)
#fluid = gmsh.model.occ.cut([(3, channel)], [(3, cylinder)])

gmsh.model.geo.synchronize()

#Volume
gmsh.model.addPhysicalGroup(3,[1],name="domain1")
# Clamped surface
gmsh.model.addPhysicalGroup(2,[45],name="clamp")
# gmsh.model.addPhysicalGroup(2,[1,2,3,5,7,8,10],name="free")
gmsh.model.addPhysicalGroup(2,[69],name="PortA")
gmsh.model.addPhysicalGroup(2,[85],name="PortB")


if '-nomesh' not in sys.argv:
    gmsh.model.mesh.generate(3)


gmsh.write(MODEL_NAME+".msh")

if DEBUG_VIEW and '-nopopup' not in sys.argv:
    gmsh.fltk.run()
    
gmsh.finalize()