#!/bin/bash

cd /home/OpenDSA-server/ODSA-django/openpop/build/TreeLeafTest/javaSource/
javac studentpreordertest.java 2> /home/OpenDSA-server/ODSA-django/openpop/build/TreeLeafTest/javaSource/compilationerrors.out
timeout 5 java  studentpreordertest 2> /home/OpenDSA-server/ODSA-django/openpop/build/TreeLeafTest/javaSource/runerrors.out
echo "timed out"