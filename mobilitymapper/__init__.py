# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 11:02:48 2020

@author: gweiss01
"""

import sys
import numpy as np
import pandas as pd
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from .fsw import Ui_Dialog

#set up dialog window
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
app = QtWidgets.QApplication(sys.argv)
Dialog = QtWidgets.QDialog()
ui = Ui_Dialog()
ui.setupUi(Dialog)
ui.graphicsView.hideAxis('left')
Dialog.show()

class globalVar():
    experTime = 360
    startFrame = 0
    timeRemain = 0
    fps = 30
    graphArray = np.linspace(0,1,1) #creates state array with the length of the experiment in frames
    state = True
    calc = True
    slidState = False
    slidState = False
    cap = cv2.VideoCapture()
    frame = cap.read()
    fileName = "U"

gv = globalVar()

ui.lcdNumber.display(gv.experTime)
ui.timeButton.clicked.connect(lambda: changeExperTime(ui.lineEdit.text()))

def changeExperTime(newTime):
    try:
        oldTime = gv.experTime
        gv.experTime = int(newTime)
        ui.lcdNumber.display(gv.experTime)
        if oldTime > gv.experTime:
            gv.graphArray[int(gv.startFrame+(gv.experTime*gv.fps)):] = -1
        else:
            gv.graphArray[int(gv.startFrame+(oldTime*gv.fps)):int(gv.startFrame+(gv.experTime*gv.fps))] = 0
    except:
        print("Not a Valid Time")

#init video stream
def loadVid():
    gv.fileName = QtWidgets.QFileDialog.getOpenFileName()[0]
    if len(gv.fileName) < 2: return
    gv.cap = cv2.VideoCapture(gv.fileName)
    gv.fps = gv.cap.get(cv2.CAP_PROP_FPS) 
    gv.frame = gv.cap.read()
    ui.horizontalSlider.setMaximum(gv.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    timer.start() 
    gv.graphArray = np.linspace(0,gv.cap.get(cv2.CAP_PROP_FRAME_COUNT), int(gv.cap.get(cv2.CAP_PROP_FRAME_COUNT))+1)
    gv.graphArray[:] = -1
 

ui.loadButton.clicked.connect(lambda:loadVid())
timer = QtCore.QTimer()

ui.horizontalSlider.setMinimum(0)
ui.horizontalSlider.actionTriggered.connect(lambda: keyAction())
ui.horizontalSlider.sliderPressed.connect(lambda: pressedSlidState())
ui.horizontalSlider.sliderReleased.connect(lambda: releasedSlidState() )

def keyAction():
    gv.cap.set(cv2.CAP_PROP_POS_FRAMES,ui.horizontalSlider.value())
    if gv.startFrame < ui.horizontalSlider.value() < gv.startFrame+(gv.experTime*gv.fps):
        gv.state = bool(gv.graphArray[int(ui.horizontalSlider.value())])
        gv.calc = False
    

def pressedSlidState():
    gv.slidState = True

def releasedSlidState():
    gv.slidState = False
    if gv.startFrame < ui.horizontalSlider.value() < gv.startFrame+(gv.experTime*gv.fps):
        gv.state = bool(gv.graphArray[int(ui.horizontalSlider.value())])
        gv.calc = False

def loadFrame():
    timer.start(int(1000/gv.fps))#starts a timer that times out at the frequency of video fps
    ret, gv.frame = gv.cap.read()
    if not ret:
        print("Video End Reached")
        timer.stop()
        return
    else:
        cv2.imshow(gv.fileName, gv.frame)

    if gv.cap.get(cv2.CAP_PROP_POS_FRAMES)%int(gv.fps/2)==0 and not gv.slidState:
         ui.horizontalSlider.setValue(gv.cap.get(cv2.CAP_PROP_POS_FRAMES))

  
    gv.timeRemain = gv.experTime - ((gv.cap.get(cv2.CAP_PROP_POS_FRAMES) - gv.startFrame) / gv.fps)
    if not gv.slidState:
        if 0 > gv.timeRemain:
            gv.timeRemain = 0
        elif gv.timeRemain < gv.experTime:
            gv.graphArray[int(gv.cap.get(cv2.CAP_PROP_POS_FRAMES))] = gv.state
        if gv.state:
            ui.stateLabel.setText("<html><head/><body><p><span style=\" font-size:18pt;color:#55aa00;\">Mobile</span></p></body></html>")
        else:
            ui.stateLabel.setText("<html><head/><body><p><span style=\" font-size:18pt;color:#ff0000;\">Immobile</span></p></body></html>")

timer.timeout.connect(lambda: loadFrame())

def plotState():
     graphTimes = np.linspace(0, gv.cap.get(cv2.CAP_PROP_FRAME_COUNT)/(gv.fps*60), gv.graphArray.size)
     ui.graphicsView.clear()
     ui.graphicsView.plot(graphTimes,gv.graphArray)
     ui.graphicsView.setXRange(0, graphTimes[-1], padding=0)
     ui.lcdNumber.display(gv.timeRemain)

     
     
graphTimer = QtCore.QTimer()
graphTimer.timeout.connect(lambda: plotState())

     
def startExper():
    gv.calc = False
    ui.stateLabel.setText("<html><head/><body><p><span style=\" font-size:18pt;color:#55aa00;\">Mobile</span></p></body></html>") #set to Mobile as default
    gv.timeRemain = gv.experTime #set start time
    gv.startFrame = gv.cap.get(cv2.CAP_PROP_POS_FRAMES)
    gv.graphArray[:] = -1
    gv.graphArray[int(gv.startFrame)+1:int(gv.startFrame+(gv.experTime*gv.fps))] = 0
    gv.state = True
    graphTimer.start(int(1000))

ui.startExperBut.clicked.connect(lambda:startExper())

def pause():
    if timer.isActive():
        timer.stop()
    else:
        timer.start()

def change():
    gv.state = not gv.state
    
ui.stateButton.clicked.connect(lambda:change())

ui.pauseButton.clicked.connect(lambda: pause())

def endCalc():
    if gv.timeRemain <= 0 and not gv.calc:
        latency = (np.argmax(gv.graphArray==0) - np.argmax(gv.graphArray==1))/gv.fps
        ui.lcdNumber.display(0) #rounds timer to 0
        timeImmobile = np.sum(gv.graphArray == 0)/gv.fps
        print("Time Immobile:", timeImmobile, " sec")
        print("Latency to Immobility:", latency, " sec")
        ui.tableWidget.setItem(0,0,QtWidgets.QTableWidgetItem(str(round(latency,2))+" sec"))
        ui.tableWidget.setItem(0,1,QtWidgets.QTableWidgetItem(str(round(timeImmobile,2))+" sec"))
        gv.calc = True
    if timer.remainingTime()!=-1:
        timer.start(timer.remainingTime())
        
timer.timeout.connect(lambda: endCalc())

def saveExcel(mouseID):
    if "/" in mouseID or len(gv.fileName)<2:
        print("Error: File Name incompatible, CSV File not Created")
        return
    stateFrame = pd.DataFrame(gv.graphArray[:-2],columns={"State"})
    stateFrame.to_csv(gv.fileName[0:-4] + "_" + mouseID + ".csv", index_label="Frame")

ui.saveButton.clicked.connect(lambda:saveExcel(ui.lineEditMouse.text()))
ui.lineEditMouse.returnPressed.connect(lambda: saveExcel(ui.lineEditMouse.text()))

sys.exit(app.exec_())