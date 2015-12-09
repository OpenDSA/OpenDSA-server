#Author: Kyle Reinholt
#Date: 6/25/15
#Program: Json Filter
#Purpose: To extract execution points from the json trace produced from InMemory.java that are intended for visualization
#Documentation: There is an example at the very end of this file. The in-code documentation for this filter is not very extravagent.
#The seperateAndFilterTrace() function contain a flow-explanation of what is happening in this program. 
import sys
import subprocess

def generateBackendTrace(jUnitTestFile, filesPath, peruserFilesPath, studentfilename): 

        
	#filesPath = ""
	#jUnitTestFile = "test.java"
	
	TestFile = open(filesPath+jUnitTestFile , 'r')
	raw_code = TestFile.read()

	raw_code = raw_code.replace("\n","\\n" + "\n")
	raw_code = raw_code.replace("\t","\\t")

	lines = raw_code.split("\n"); 
	jUnitTest = ""

	for line in lines:
    		jUnitTest = jUnitTest + line


	jUnitTest = jUnitTest.replace("\"", "\\" + "\"")
	#print jUnitTest

	#peruserFilesPath = "/Your/Path/To/cp/traceprinter/" 
	#studentfilename = "output.txt"

	generateTrace = open(peruserFilesPath+studentfilename, 'w')
	generateTrace.write("{" + "\n" + '"' + "usercode" + '"' + ':' + '"' + jUnitTest + '"' + ',' + "\n" + '"' + "options" + '"' + ':' + '{' + '}' + ',' + "\n" + '"' + "args" 		+ '"' + ':' + '[' + ']' + ',' + "\n" + '"' + "stdin" + '"' + ':' + '"' + '"' + "\n" + '}')
	generateTrace.close()

	#This shell command should work after the paths for the java tools and
	# traceprinter packages have been correctly modified. 
	
	command = "/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/bin/java -cp .:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/lib:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp/javax.json-1.0.jar:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp/javax.json-1.0.4.jar:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/lib/:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/lib/tools.jar:/vagrant/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp/traceprinter traceprinter.InMemory < /vagrant/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/Medhaa"
	#command = "/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/bin/java -cp .:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/lib:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp/javax.json-1.0.jar:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp/javax.json-1.0.4.jar:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/lib/:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/java/lib/tools.jar:/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/javavisualizer/frontAndBackendFiles/backendFiles/cp/traceprinter traceprinter.InMemory < /vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/Medhaa"
	
	process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)

	#Launch the shell command:
	output = process.communicate()

	backend_trace = output[0]
	return backend_trace

#This function calls the functions necessary to completely execute the program. 
def seperateAndFilterTrace(jUnitTestFile, filesPath, peruserFilesPath, studentfilename):

        #This takes the .java file from the OpenDSA backend, formats the file into a json object,
        # inserts the json object into the traceprinter to generate the 50,000 character+ json object
        codeAndTrace = generateBackendTrace(jUnitTestFile, filesPath, peruserFilesPath, studentfilename)
        print codeAndTrace
		#After the trace is generated, it is split into two pieces, the code section and trace section of the json
        # object.
        splitter = '"' + "trace" + '"' + ':'        
        userCode, wholeTrace = codeAndTrace.split(splitter)
        #print wholeTrace

        #The first character is removed from the trace section because the bracket at the beginning of the trace
        # was causing problems in the execution point locater function. 
        wholeTrace = wholeTrace[1:]        
        #Finally, the two pieces of the json object are anaylyzed by means of extracting all unwanted code
        # and execution traces. There is functionality within the codeAnalyzer that outputs the results to
        # a "ready-to-go" javaScript file. "ready-to-go" meaning you just have to include the <div> in
        # html file to display the executionVisualizer! 
        entireJSFile = codeAnalyzer(userCode, wholeTrace)
        

        return entireJSFile	
	
class Event(object):
    
    def __init__(self):
        self.trace = ""
        self.lineNumber = 0

    def set_Event(self, trace):
        self.trace = trace

    def set_Line(self, lineNumber):
        self.lineNumber = lineNumber
    
    def get_Event():
        return self.trace

    def get_Line():
        return self.lineNumber

    
class EventManager(object):
    
    def __init__(self):
        self.listOfEvents = []
        self.filteredEvents = []

    def get_Line_Number(self, index):
        if is_empty(self.listOfEvents) == True:
            print("list is empty")
        else:
            tempEvent = self.listOfEvents[index]
            return tempEvent.lineNumber

    def set_Event(self, index, event):
        self.filteredEvents[index] = event
    
    def get_Event(index):
        return self.filteredEvents[index]

    def add_Event(self, event):
        self.listOfEvents.append(event)

    def trace_List(self):
        myList = []
        for x in range(0,len(self.filteredEvents)):
            temp = Event()
            temp = self.filteredEvents[x]
            myList.append(temp.trace)

        return myList

    def print_Events(self):
        if (len(self.filteredEvents) == 0):
            print("List of events is empty")
        else:
            for x in range(0, len(self.filteredEvents)):
                tempEvent = self.filteredEvents[x]                

    def verify_Events(self):
        currentLine = 0
        nextLine = 0
        eventCounter = 0
        counter = 1
        
        originalLineNum = self.get_Line_Number(0)
        currentLine = originalLineNum

        length = len(self.listOfEvents) - 1
    
        while counter < length+1:
            nextLine = self.get_Line_Number(counter)

            if (currentLine+1 == nextLine and nextLine > originalLineNum) or (currentLine+2 == nextLine and nextLine > originalLineNum) or (currentLine+3 == nextLine and nextLine > originalLineNum) or (currentLine+4 == nextLine and nextLine > originalLineNum) or (currentLine+5 == nextLine and nextLine > originalLineNum):
                self.filteredEvents.append(self.listOfEvents[eventCounter])
                eventCounter = eventCounter + 1
                currentLine = nextLine
                counter = counter + 1
            else:
                currentLine = nextLine
                eventCounter = eventCounter + 1
                counter = counter + 1

        
        self.filteredEvents.append(self.listOfEvents[length])

    def modify_Lines(self, code):
        lineNumber = 0
        eventNumber = 0

        #while lineNumber != len(code):
        while lineNumber != len(self.filteredEvents):
            modify = Event()
            tempString = ""
            tempLine = 0                        
            modify = self.filteredEvents[eventNumber]            
            tempString = modify.trace
            tempLine = modify.lineNumber

            if(code[lineNumber] == "newline"):
                lineNumber = lineNumber + 1
            elif(code[lineNumber] == "\\t"):
                lineNumber = lineNumber + 1
            else:
                originalLine = str(tempLine)
                newLine = str(lineNumber+1)
                tempString = tempString.replace(originalLine,newLine)
                modifiedEvent = Event()
                modifiedEvent.set_Event(tempString)
                modifiedEvent.set_Line(lineNumber+1)
                self.filteredEvents[eventNumber] = modifiedEvent

                eventNumber = eventNumber + 1
                lineNumber = lineNumber + 1

        lastEvent = Event()
        if 0 <= eventNumber < len(self.filteredEvents):
           lastEvent = self.filteredEvents[eventNumber]
        lastEvent = self.filteredEvents[eventNumber-1]
        tempLine = lastEvent.lineNumber
        tempString = lastEvent.trace

        oldLine = str(tempLine)

        secondTLEvent = Event()
        secondTLEvent = self.filteredEvents[eventNumber-1]
        otherLine = secondTLEvent.lineNumber

        newLine = str(otherLine)

        tempString = tempString.replace(oldLine,newLine)
        
        modifiedEvent = Event()
        modifiedEvent.set_Event(tempString)
        modifiedEvent.set_Line(otherLine)
        if 0 <= eventNumber < len(self.filteredEvents):
		  self.filteredEvents[eventNumber-1] = modifiedEvent
		  
		  

def modifySelectedEventList(eventList,userCodeLen):
    newList = []
	#for inde x in range(0, userCodeLen)
    newList.append(eventList[0])
    newList.append(eventList[0])
    newList.append(eventList[0])
    newList.append(eventList[1])
	
    return newList

def modifyStack(myList):

    oldStack = []
    curlyStack = []
    listOfStackPoints = []
    
    for x in range(0,len(myList)):
        curEvent = myList[x].split("stack_to_render\":[")
        stacks = curEvent[1].split("],\"globals\"")

        stackToRender = stacks[0]
        oldStack.append(stacks[0])

        stackPoint = "" 

        for i in stackToRender:
            stackPoint = stackPoint + i
            if i == '{':
                curlyStack.append(i)
            elif i == '}':
                topSymbol = curlyStack.pop()
                if len(curlyStack) == 0:
                    listOfStackPoints.append(stackPoint)
                    stackPoint = ""
                else:
                    continue

    main = ""
    main = "main:" 

    newStack = []
    
    for x in range(0, len(listOfStackPoints)):
        if main in listOfStackPoints[x]:
            #Do nothing
            continue
        else:
            newStack.append(listOfStackPoints[x])

    for x in range(0, len(myList)):
        myList[x] = myList[x].replace(oldStack[x],newStack[x])

    return myList
            
    
	
class TraceAnalyzer(object):

    def __init__(self): 
        self.eventManager = EventManager()

    def handleEverything(self, userCode, inTrace):
        filterPoints = self.exe_Point_Finder
        filterPoints(inTrace)
        
        filteredEvents = self.eventManager.verify_Events
        filteredEvents()
        modifyLines = self.eventManager.modify_Lines(userCode) 

        raw_events = []
        raw_events = self.eventManager.trace_List()

        clean_Events = modifyStack(raw_events)
        consistent_events = clean_Events
		# making the exceutable events consistent with user code text.
        #consistent_events = modifySelectedEventList(clean_Events,4)

	#At this point, everything is ready for output. The printToFile string 
	# contains all of the information necessary for the javaScript file. 
        # Its about 20 lines down
        orig_stdout = sys.stdout
        f = file('filteredJSON.js', 'w')
        sys.stdout = f

        first = "var testvisualizerTrace = {\"code\":\""

        code = ""
        
        for x in range (0,len(userCode)):
            if userCode[x] == "newline":
                code = code + "\\n" + " "
            else:
                code = code + userCode[x] + "\\n"
        second = "\",\"trace\":["

        trace = ""
        for y in range(0,len(consistent_events)):
            if y == len(consistent_events)-1:
                tempString = consistent_events[y]
                tempString = tempString[:-1]
                trace = trace + tempString
                trace = trace + "],\"userlog\":\"Debugger VM maxMemory: 807M \\n \"}"
                trace = trace + "\n" + "$(document).ready(function() { \n \n \t var testvisualizer = new ExecutionVisualizer('testvisualizerDiv', testvisualizerTrace,{embeddedMode: false, lang: 'java', heightChangeCallback: redrawAllVisualizerArrows}); \n \n \tfunction redrawAllVisualizerArrows() { \n \n \t \t if (testvisualizer) testvisualizer.redrawConnectors(); \n \t } \n \n $(window).resize(redrawAllVisualizerArrows); \n});"
            else: 
                tempString = consistent_events[y]
                trace = trace + tempString + "\n"
        
	#String that contains everything for the javascript file 
	# Maybe just send string to front end and write to file in 
	# a directory accessible by the OpenDSA frontend?         
        printToFile = first + code + second + trace       
        
        sys.stdout = orig_stdout
        f.close()
	
        return printToFile
        
        
    def is_empty(self, any_structure):
        if any_structure:
            return False
        else:
            return True    

    def extract_Line_Num(self, string):

        line = string.replace('"'," ")
        line = line.replace('{'," ")
        line = line.replace(':'," ")
        line = line.replace(','," ")
        line = line.replace('['," ")
        line = line.replace('('," ")
        line = line.replace(']'," ")
        line = line.replace('}'," ")
        line = line.replace(')'," ")
        
        line = [int(s) for s in line.split() if s.isdigit()]
        
        return line[0]

    def verify_Exe_Point(self, on, off, inPoint):
        
        addExePoint = False
        exeTrace = Event()

        if on == True and off == False:
            exeTrace.set_Event(inPoint)
            exeTrace.set_Line(self.extract_Line_Num(inPoint))
            self.eventManager.add_Event(exeTrace)
            addExePoint = True
            
        elif on == False and off == False:
            addExePoint = False
        else:
            addExePoint = False

        return addExePoint

    def exe_Point_Finder(self, trace): #This is really messy. Sorry. I will definitely need to refactor in the future
        symbolStack = []
        exePointList = []
        otherList = []
        currentSymbol = ''
        topSymbol = ''
        exe = ""
        exePoint = " "
        on = False
        off = False
        counter = 0
        
        for i in trace:
            currentSymbol = i
            exePoint = exePoint + currentSymbol
            if i == '{' or i == '[' or i == '(':
                symbolStack.append(i)
            elif i == '}' or i == ')' or i == ']':
                if self.is_empty(symbolStack) == False:
                    topSymbol = symbolStack.pop()
                    if i == '}' and topSymbol != '{':
                        continue
            elif i == ',':
                otherList.append(exePoint)
                if len(symbolStack) == 0:
                    for thing in otherList:
                        exe = exe + thing                                                
                    if "startTraceNow" in exe:
                        on = True
                        exe = ""
                        exePoint = ""
                        otherList = []
                    elif "endTraceNow" in exe:
                        off = True
                        return
                    else:
                        flag = self.verify_Exe_Point(on, off, exe)
                        if flag == True:
                            exe = ""
                            exePoint = ""
                            otherList = []
                        else:
                            on = False
                            exe = ""
                            exePoint = ""
                            otherList = []
                else:
                    exePoint = ""
            else:
                continue

def is_empty(structure):
    if structure:
        return False
    else:
        return True

def codeSplitter(code):

    studentCode = []

    code = code.split("startTraceNow();")    
    newCode = code[1].split("endTraceNow();")

    executedCode = newCode[0]    
    exeCodeList = executedCode.split(";")

    flag = False
    counter = 0 
    
    while flag != True:
        if exeCodeList[counter] == "" or exeCodeList[counter] == " ":
            flag = False
            counter = counter + 1
        elif exeCodeList[counter] != "":
            flag = True

    for x in range(counter, len(exeCodeList)):
        temp = exeCodeList[x]
        temp = "".join(temp.split())

        if is_empty(temp):
            studentCode.append("newline")
        else:
            studentCode.append(exeCodeList[x])

    #print studentCode
    return studentCode


def codeAnalyzer(code, firstTrace):
    
    codeToViz = []    
    codeToViz = codeSplitter(code)

    traceAnalyzer = TraceAnalyzer()
    
    execute = traceAnalyzer.handleEverything(codeToViz, firstTrace)

    return execute
    
#This is an example of how to use the seperateAndFilterTrace() function. This 
#function initiates everything. Include this in your python code with the proper 
#parameters to get expected results. myTest is a string that contains the entire js file contents for visualizing code.
#Send this string to the correct frontend directory, make a javaScript file and only containing myTest, then include the
# proper links and scripts in the html page and you should be good to go. 

#myTest = seperateAndFilterTrace("studentpntrequalspntrPROG.java", "/vagrant/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/Medha/", "/vagrant/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/", "Medha")
#for local debugging
#myTest = seperateAndFilterTrace("studentpntrequalspntrPROG.java", "/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/Medha/", "/vagrant/OpenDSA-DevStack/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/", "Medhaa")
#filterJson.close()
#myTest = seperateAndFilterTrace("studentpntrequalspntrPROG.java", "/vagrant/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/Medha/", "/vagrant/OpenDSA-server/ODSA-django/openpop/build/pntrtest/pntrequalspntrPROG/", "Medhaa")
#print myTest
