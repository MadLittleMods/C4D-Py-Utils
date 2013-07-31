import c4d
from c4d import documents
 
def GetNextObject(op):
    if op==None: return None
 
    if op.GetDown(): return op.GetDown()
 
    while not op.GetNext() and op.GetUp():
        op = op.GetUp()
 
    return op.GetNext()
 
# Source: http://peranders.com/wiki/Python_Object_Iteration
def main():
    myobject = doc.GetFirstObject()
    if myobject==None: return
 
    while myobject:
        #do something to "myobject here"
		print myobject.GetName()
		myobject = GetNextObject(myobject)
 
if __name__=='__main__':
    main()