The significant code in this directory is the documentation, and the 
contents of ./cp/traceprinter. Both are released under the GNU Affero 
General Public License, versions 3 or later. See LICENSE or visit:
http://www.gnu.org/licenses/agpl.html

cp
==
Contains the traceprinter package from David Pritchard's repository: 
https://github.com/daveagp/java_jail

java
====
Contains files from oracle.com: 
http://download.oracle.com/otn-pub/java/jdk/8u20-b26/jdk-8u20-linux-x64.tar.gz

jsonFilter.py
=============
This is a Python version of the jsonFilter.java, except the jsonFilter.py contains different functionality and is much closer to a complete program. jsonFilter.py has capabilities to read in a .java file and produce filtered execution traces that were specified by the OpenDSA backend developer. 

This file does 3 things: 

1. Reads in the backend j-unit test file 

2. Generates a json trace from the entire j-unit test file. This trace is a string that consists of over 60,000 characters in the case of the normal j-unit test from OpenDSA exercises. 

3. Filters the backend json trace down to about 2,000 characters and outputs the results into a formatted JavaScript file. TODO: This file format may not be transferable from the backend to the frontend in the existing OpenDSA infrastructure. Rather than printing out to a file, place the contents into a string that can be retrieved programmatically by frontend. (This has been done!!! There is in example at the end of the jsonFilter.py file.) 

This program was developed to isolate certain lines of code to be visualized by the Java version of Philip Guo's Online Python Tutor. This file utilizes the traceprinter package from David Pritchard's repository https://github.com/daveagp/java_jail/tree/master/cp to run the shell command to produce the backend json trace. The backend json trace is a string consisting of over 10,000 characters (in most cases) that is used to visualize java code. The jsonFilter.py locates the execution points that are specified using the startTraceNow() and endTraceNow() functions, which are dummy functions inserted into the j-unit test in the OpenDSA backend that wrap the code presented to the student and the student's code, both intended for visualization.   

filteredJSON.js
===============
Is an example of the final product of the trace of the user's code and the necessary javaScript code, contained in a string named printToFile, produced by the jsonFilter.py

filteredJSON.js has the ExecutionVisualizer function used to create a div that is then included in the html file for visualization. 

test.java
=========
This is an example of a junit test from the backend of an OpenDSA pointers exercise... Should I take this down....? The junit test is sent to the jsonFilter and turned into a json object for visualization.  
