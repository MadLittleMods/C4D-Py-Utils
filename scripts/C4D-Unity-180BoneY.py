import c4d
from c4d import documents
# Welcome to the world of Python
# ****** See notes and description above the "main" function ******

# Get the next Object in the hierarchy
def GetNextObject(op):
    if op == None: return None
 
    if op.GetDown(): return op.GetDown()
 
    while not op.GetNext() and op.GetUp():
        op = op.GetUp()
 
    return op.GetNext()

# Get the next object only if it is a sibling or child
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

	
def UpdateOnlyObject(object, newMatrix):
	if object == None: return
	
	
	# Save the childrens positions before we muck with the parent
	myobject = object.GetDown()
	if myobject != None:
		prevObjectTransformList = {}
		while myobject:
		
			prevObjectTransformList[str(myobject.GetGUID())] = {"trans": myobject.GetAbsPos(), "rot": myobject.GetAbsRot(), "matrix": myobject.GetMg()}
			
			myobject = GetNextObjectOnlyDown(object, myobject)
		
		
	#print "Parent: " + object.GetName()
	# Update the parent transform
	doc.AddUndo(c4d.UNDOTYPE_CHANGE, object)
	object.SetMg(newMatrix)
	
	# Re-apply positions
	myobject = object.GetDown()
	if myobject != None:
		while myobject:
		
			#print "Child: " + myobject.GetName()
			doc.AddUndo(c4d.UNDOTYPE_CHANGE, myobject)
			myobject.SetMg(prevObjectTransformList[str(myobject.GetGUID())]['matrix'])
			#myobject.SetAbsPos(prevObjectTransformList[str(myobject.GetGUID())]['trans'])
			#myobject.SetAbsRot(prevObjectTransformList[str(myobject.GetGUID())]['rot'])
			
			myobject = GetNextObjectOnlyDown(object, myobject)
		
	c4d.EventAdd();
	

# Enable or Disable all skin objects in the document
# enableMap is optional and is used if you want to save and reinstiatate the state of skins
def SetAllSkinEnable(enable, enableMap = {}):
	myobject = doc.GetFirstObject()
	if myobject == None: return

	prevObjectEnableList = {}
	while myobject:
		
	
		#do something to "myobject here"
		if myobject.CheckType(c4d.Oskin):
			print ("Activating" if enable else "Deactivating") + " Skin object, parent is: " + myobject.GetUp().GetName()
			
			
			prevObjectEnableList[str(myobject.GetGUID())] = myobject[c4d.ID_BASEOBJECT_GENERATOR_FLAG]
			
			doc.AddUndo(c4d.UNDOTYPE_CHANGE, myobject)
			#myobject[c4d.ID_BASEOBJECT_GENERATOR_FLAG] = enable
			#myobject[c4d.ID_BASEOBJECT_GENERATOR_FLAG] = prevObjectEnableList[str(myobject.GetGUID())]
			myobject[c4d.ID_BASEOBJECT_GENERATOR_FLAG] = enableMap.get(str(myobject.GetGUID()), enable)
			
			c4d.EventAdd()
			
		myobject = GetNextObject(myobject)
		
	print "----------------------------------"
	
	return prevObjectEnableList
	
	
	
# Author: MLM (VisualPulse.net)
#
# Summary: 
# The perfect script to get your Cinema 4D rigged models into Unity
# 
# Note:
# 	- If your object does not need to be rigged, still rig the whole model
# 	to one bone and use this script to get the axis correct.
# 	- To get correct results, make sure there is a null around each bone structure
#
# Coordinate Systems
# Cinema 4D: 	Right Handed Y-up
# Unity: 		Left Handed Y-up
#
# What the code does:
# First we deactivate all the skin objects
# Then we rotate the joints 180 degrees without effecting the children
# Then we set the bind pose on all weight tags
# Then we reactivate the skin objects
# Finally we rotate the null 180 degrees holding the bones/joints and then put the axis back
def main():
	
	print
	print "======================================================================="
	print "Starting Coordinate System (Right to Left Y-up) Conversion"
	print "======================================================================="
	
	#Grab the active document
	doc = c4d.documents.GetActiveDocument()
	
	doc.StartUndo()
	
	
	# Disable all skin objects
	skinEnableMap = SetAllSkinEnable(False)

	
	# Move the joints to their new positions
	myobject = doc.GetFirstObject()
	if myobject == None: return

	while myobject:
	
		if myobject.CheckType(c4d.Ojoint):
			
			myobject.SetAbsRot(c4d.Vector(myobject.GetRelRot().x + c4d.utils.Rad(180), -myobject.GetRelRot().y, -myobject.GetRelRot().z)) # needs to be Radians
			newMatrix = myobject.GetMg()
			myobject.SetAbsRot(c4d.Vector(myobject.GetRelRot().x - c4d.utils.Rad(180), -myobject.GetRelRot().y, -myobject.GetRelRot().z)) # needs to be Radians
			
			print "Updating: " + myobject.GetName() + ", while freezing children"
			UpdateOnlyObject(myobject, newMatrix)
	
		myobject = GetNextObject(myobject)
		
	print "----------------------------------"
	
	
	
	
	# Set bind pose on all weight tags
	myobject = doc.GetFirstObject()
	if myobject == None: return

	while myobject:
		
		# Loop through all tags on object
		for tag in myobject.GetTags():
			# If we find a weigth tag
			if isinstance(tag, c4d.modules.character.CAWeightTag):
				print "Set bind pose of " + myobject.GetName()
				# Emulate a button click of "Set Bind Pose" on the Weight tag
				doc.AddUndo(c4d.UNDOTYPE_CHANGE, myobject)
				c4d.CallButton(tag, c4d.ID_CA_WEIGHT_TAG_SET)
				
		
		myobject = GetNextObject(myobject)
		
	print "----------------------------------"
	
	
	
	
	# Re-enable all skin objects that were enabled in the first place
	SetAllSkinEnable(True, skinEnableMap)
	
	
	
	
	
	# TODO: Now we rotate the null around the bones 180 degrees
	# Then put the axis back in place
	rootBoneObject = doc.GetFirstObject()
	if rootBoneObject == None: return

	while rootBoneObject:
		if rootBoneObject.CheckType(c4d.Onull) and rootBoneObject.GetDown().CheckType(c4d.Ojoint):
			print "Rotating All Bones via " + rootBoneObject.GetName()
		
			rootBoneObject.SetAbsRot(c4d.Vector(rootBoneObject.GetRelRot().x + c4d.utils.Rad(180), -rootBoneObject.GetRelRot().y, -rootBoneObject.GetRelRot().z)) # needs to be Radians
			newMatrix = rootBoneObject.GetMg()
			rootBoneObject.SetAbsRot(c4d.Vector(rootBoneObject.GetRelRot().x - c4d.utils.Rad(180), -rootBoneObject.GetRelRot().y, -rootBoneObject.GetRelRot().z)) # needs to be Radians
					
			# Rotate the matrix for this object
			UpdateOnlyObject(rootBoneObject, newMatrix)
			
			# Now that the axis is rotated, go back to normal
			doc.AddUndo(c4d.UNDOTYPE_CHANGE, rootBoneObject)
			rootBoneObject.SetAbsRot(c4d.Vector(rootBoneObject.GetRelRot().x + c4d.utils.Rad(180), -rootBoneObject.GetRelRot().y, -rootBoneObject.GetRelRot().z)) # needs to be Radians
			
		
		rootBoneObject = GetNextObject(rootBoneObject)
		
	print "----------------------------------"
	
	
	
	
	
	
	doc.EndUndo()
	c4d.EventAdd()
		
	print "Done..."

# =======================================================================
if __name__ == "__main__":
	main()
