C4D-Py-Utils
============

Cinema 4D Python scripts designed for random purposes

Scripts
========
 - **C4D-Unity-180BoneY.py:** Simple script to get your model into [Unity 3D](http://unity3d.com/) with axis pointing in the right direction. This solves the Z-axis pointing in the wrong direction issue. Does Right hand Y-up (C4D) to Left hand Y-up (Unity). 
    - Run as a stand-alone script
 - **C4D-Iterate-Hierarchy.py:** Boilerplate template to iterate over Cinema's Hierarchy.
    - Run as a stand-alone script
 - **C4D-Generate-Point-Cloud.py:** Generates and Updates an object (`pointCloud`) from another object (`parentObject`) and all of its children. Points/Vertices can be taken from primitives, editable objects, and even MoGraph cloners. Use the `pointCloud` object for whatever your needs. 
    - Run as a XPresso node to pass in both objects (see documentation at the top of the `.py` file)

How to Run
==========
Open up Cinema 4D...

##### Run a script:
`Scripts->User Scripts->Run Script...`

##### View the Output:
`Scripts->Console...`

##### Create a XPresso Script Node:
In the XPresso window, Right click: `New Node->XPresso->Script->Python`
![Adding XPresso Python Script](https://raw.github.com/MadLittleMods/C4D-Py-Utils/master/c4d-xpresso-python-script-node.png)

License
=======
You can do what you want under the condition of:
 - Leave the attribution/credit/author
 - [![CC BY](http://i.creativecommons.org/l/by/3.0/88x31.png)](https://creativecommons.org/licenses/by/3.0/)
