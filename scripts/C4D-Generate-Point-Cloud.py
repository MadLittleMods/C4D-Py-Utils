# Author: Eric (EricEastwood.com)
#
# Usage:
# Create any primitive and make it editable. Go into point mode and select all points (Ctrl+A) and delete them all. 
# This object will act as our point cloud object.
# Add a XPresso tag to some object (could be your point cloud object but it doesn't matter).
# Add a `New Node->XPresso->Script->Python` node to that Xpresso tag
# Click on the node. In the options off to the side (outside the XPresso window), click `Open Python Editor`.
# On the dialog that pops up, click the `Load` button and browse for this file. Press compile. If it says "No Errors!", then it should work fine.
# Add two `link` inputs on that python script node
# Name one input as `parentObject` and the other as `pointCloud`
# Drag your point cloud object into the Xpresso window and add an `Object` output. 
# Connect it to your `pointCloud` input on the python script node
# Drag in the parent object that contains all of the objects you want to collect points/vertices from
# Add an `Object` output to the parent object node and connect it to the `parentObject` input on the python script node

import c4d
import math
# Welcome to the world of Python

# Get the next object only if it is a sibling or child of the inside of parent
def GetNextObjectOnlyDown(parent, op):
	# If the object or parent are nothing then there is nothing...
	if (op == None) or (parent == None): return None

	# If there are children, goto the first child
	if op.GetDown(): return op.GetDown()

	if op == parent: return None

	# If there is no next object and there is parent that is not the overarching parent, then goto the parent
	while not op.GetNext() and op.GetUp() and op.GetUp() != parent:
		op = op.GetUp()

	# Return the next object
	return op.GetNext()


# Get the next sibling only if inside of parent
def GetSiblingObjectOnlyDown(parent, op):
	# If the object or parent are nothing then there is nothing...
	if (op == None) or (parent == None): return None

	# If there is not `next` then go up (then try to go down) until we can. Stops at parent
	while not op.GetNext() and op.GetUp() and op.GetUp() != parent:
		op = op.GetUp()

		if(op == parent):
			return None


	if(op == parent):
		 return None

	# Return the next object
	return op.GetNext()


# Get the next object only if it is a sibling or child
def GetSiblingObject(op):
	# If the object or parent are nothing then there is nothing...
	if (op == None): return None

	# Return the next object
	return op.GetNext()



def MakeEditable(op):

	if (not op) or op.CheckType(c4d.Opolygon) or op.CheckType(c4d.Ospline): 
		return op

	doc = c4d.documents.BaseDocument()


	clone = op.GetClone()
	doc.InsertObject(clone, None, None)
	clone.SetMg(op.GetMg()) # Set the clone at the same position as the object was before


	op = c4d.utils.SendModelingCommand(
		command = c4d.MCOMMAND_MAKEEDITABLE,
		list = [clone],
		mode = c4d.MODELINGCOMMANDMODE_ALL,
		doc = doc 
	)

	if op:
		return op[0]  
	else:
		return None



def GetAllPointsFromObject(op, includeObjectMatrix = True):
	#print("Getting All points from: " + op.GetName())
	#print("--------------------------------------")

	myobject = op
	pointList = []

	while myobject:
		# do something to "myobject here"
		#print myobject.GetName() + ": " + myobject.GetTypeName()

		if(myobject.GetTypeName() == "Cloner"):
			pointList.extend(GetPointsFromCloner(myobject))
			myobject = GetSiblingObjectOnlyDown(op, myobject) # Move to the next sibling
		else:
			editable_myobject = MakeEditable(myobject)
			if(editable_myobject):
				if(isinstance(editable_myobject, c4d.PointObject)):
					# points are in given in relative local space so ask if we want to update it with the object matrix
					if(includeObjectMatrix):
						myobject_pos = editable_myobject.GetMg()
						adjusted_allpoints = [myobject_pos*x for x in editable_myobject.GetAllPoints()]
					
						pointList.extend(adjusted_allpoints)
					else:
						pointList.extend(editable_myobject.GetAllPoints())

			myobject = GetNextObjectOnlyDown(op, myobject) # Move to the next object

	#print("Number points in object: " + str(len(pointList)))

	return pointList



def GetPointsFromCloner(clonerObject):
	#print(clonerObject.GetTypeName())
	
	moData = c4d.modules.mograph.GeGetMoData(clonerObject)
	moCount = moData.GetCount()
	#print("Items in Cloner: " + str(moCount))
	moMatrixArray = moData.GetArray(c4d.MODATA_MATRIX)
	moCloneArray = moData.GetArray(c4d.MODATA_CLONE)
	#print(moCloneArray)
		
	#print(clonerObject[c4d.ID_MG_TRANSFORM_POSITION])
	#print(clonerObject[c4d.ID_MG_TRANSFORM_SCALE])
	#print(clonerObject[c4d.ID_MG_TRANSFORM_ROTATE])
	

	# ----------------------------------------
	# Assemble the a list of points for each object
	myobject = clonerObject.GetDown()
	if myobject==None: return
	
	clonePointList = []
	
	numObjectsInHierarchy = 0
	while myobject:
		# do something to "myobject here"
		#print("Cloner clone: " + myobject.GetName() + ": " + myobject.GetTypeName())

		# If clone is fixed, do not include object matrix
		fixedClone = False;
		if(clonerObject[c4d.MGCLONER_FIX_CLONES]):
			fixedClone = True;

		# Make the `Transform` tab matrix
		clonerTransormMatrix = c4d.utils.MatrixMove(clonerObject[c4d.ID_MG_TRANSFORM_POSITION]) * c4d.utils.MatrixScale(clonerObject[c4d.ID_MG_TRANSFORM_SCALE]) * c4d.utils.HPBToMatrix(clonerObject[c4d.ID_MG_TRANSFORM_ROTATE])
		# Apply the `Transform` tab matrix
		# And apply the cloner object Matrix itself
		adjusted_objectpoints = [(clonerObject.GetMg() if fixedClone else c4d.Matrix())*clonerTransormMatrix*x for x in GetAllPointsFromObject(myobject, not(fixedClone))]
		clonePointList.append(adjusted_objectpoints)
		
		numObjectsInHierarchy += 1
		myobject = GetSiblingObject(myobject)
	

	#print("Number of objects in Cloner: " + str(numObjectsInHierarchy))
	#for index, item in enumerate(clonePointList):
	#	print(str(index) + ": " + str(len(item)))



	# ----------------------------------------
	# Now we assemble the final point list
	pointList = []

	for cloneIndex in xrange(0, moCount):
		# Find what index we need from the cloner clone array to match our list of points for each object
		if(moCloneArray[cloneIndex] == 0):
			clonePointListIndex = 0
		else:
			clonePointListIndex = int(math.ceil(moCloneArray[cloneIndex]/(float(1)/numObjectsInHierarchy)))-1
		#print("clonePointListIndex: " + str(clonePointListIndex))

		# Apply the matrix that the cloner puts on this clone
		adjusted_allpoints = [moMatrixArray[cloneIndex]*x for x in clonePointList[clonePointListIndex]]

		pointList.extend(adjusted_allpoints)


	#print("Number points: " + str(len(pointList)))

	return pointList


def main():
	#print("")
	#print("----------------------------")
	#print("New Point Collector")
	#print("----------------------------")
	
	myobject = parentObject
	if myobject==None: return
 
	pointList = []
 	
 	"""
 	asdf = 0
	while myobject:
		#do something to "myobject here"
		print myobject.GetName() + ": " + myobject.GetTypeName()
		
		if(myobject.GetTypeName() == "Cloner"):
			pointList.extend(GetPointsFromCloner(myobject))
			myobject = GetSiblingObjectOnlyDown(parentObject, myobject) # Move to the next sibling
		else:
			pointList.extend(GetAllPointsFromObject(myobject, True))
		
			myobject = GetNextObjectOnlyDown(parentObject, myobject) # Move to the next object


		if(asdf > 100):
			print("Broke out after 100 iterations")
			return None

		asdf += 1
	"""

	pointList.extend(GetAllPointsFromObject(myobject, True))
		
	#print("Number points: " + str(len(pointList)))
	#print  pointCloud.GetName() + ": " + pointCloud.GetTypeName()
		
	pointCloud.ResizeObject(len(pointList))
	pointCloud.SetAllPoints(pointList)

		
