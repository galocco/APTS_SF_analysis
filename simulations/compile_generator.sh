#!/bin/bash 
cp -r EventGenerator /opt/corryvreckan/src/modules/EventGenerator
cp EventGenerator/EventGenerator.cpp /opt/corryvreckan/src/modules/EventGenerator/EventGenerator.cpp
cp EventGenerator/EventGenerator.h /opt/corryvreckan/src/modules/EventGenerator/EventGenerator.h
cp EventGenerator/CMakeLists.txt /opt/corryvreckan/src/modules/EventGenerator/CMakeLists.txt
cp CMakeListsModules.txt /opt/corryvreckan/src/modules/CMakeLists.txt 
cd /opt/corryvreckan/build/ && make install -j12 && cd /local