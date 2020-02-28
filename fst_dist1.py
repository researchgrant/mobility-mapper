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
from fsw import Ui_Dialog
import time


#set up dialog window
app = QtWidgets.QApplication(sys.argv)
Dialog = QtWidgets.QDialog()
ui = Ui_Dialog()
ui.setupUi(Dialog)
Dialog.setGeometry(300,650,590, 177)
Dialog.show()

class globalVar():
    experTime = 360
    startFrame = 0
    timeRemain = 360
    fps = 30
    stateArray = np.linspace(startFrame, startFrame + experTime*fps -1, startFrame + experTime*fps) #creates state array with the length of the experiment in frames
    graphArray = np.linspace(0,1,1) #creates state array with the length of the experiment in frames
    stateArray[:] = 1
    state = True
    calc = True
    slidState = False
    slidState = False
    cap = cv2.VideoCapture()
    frame = cap.read()
    fileName = "Unknown"
    codeTimer= time.time()

gv = globalVar()

ui.lcdNumber.display(gv.experTime)
ui.lineEdit.textEdited.connect(lambda: changeExperTime(int(ui.lineEdit.text())))

def changeExperTime(newTime):
    gv.experTime = newTime
    ui.lcdNumber.display(gv.experTime)

#init video stream
def loadVid():
    gv.fileName = QtWidgets.QFileDialog.getOpenFileName()
    gv.cap = cv2.VideoCapture(gv.fileName[0])
    gv.fps = gv.cap.get(cv2.CAP_PROP_FPS) 
    gv.frame = gv.cap.read()
    ui.horizontalSlider.setMaximum(gv.cap.get(cv2.CAP_PROP_FRAME_COUNT))
    timer.start() 
    gv.stateArray = np.linspace(int(gv.startFrame), int(gv.startFrame + gv.experTime*gv.fps -1), int(gv.startFrame + gv.experTime*gv.fps))
    gv.graphArray = np.linspace(0,gv.cap.get(cv2.CAP_PROP_FRAME_COUNT) -1, int(gv.cap.get(cv2.CAP_PROP_FRAME_COUNT)))
    gv.graphArray[:] = 0
 

ui.loadButton.clicked.connect(lambda:loadVid())
timer = QtCore.QTimer()

ui.horizontalSlider.setMinimum(0)
ui.horizontalSlider.valueChanged.connect(lambda: gv.cap.set(cv2.CAP_PROP_POS_FRAMES,ui.horizontalSlider.value()))
ui.horizontalSlider.sliderPressed.connect(lambda: pressedSlidState())
ui.horizontalSlider.sliderReleased.connect(lambda: releasedSlidState() )

def pressedSlidState():
    gv.slidState = True

def releasedSlidState():
    gv.slidState = False
    timer.start()
    if gv.startFrame < ui.horizontalSlider.value() < gv.startFrame+(gv.experTime*gv.fps):
        gv.state = bool(gv.stateArray[int(ui.horizontalSlider.value() - gv.startFrame)])
        gv.calc = False

def loadFrame():
    timer.start(int(1000/gv.fps))#starts a timer that times out at the frequency of video fps
    ret, gv.frame = gv.cap.read()
    if not ret:
        print("Video End Reached")
        timer.stop()
        return
    else:
        cv2.imshow(gv.fileName[0], gv.frame)
    
    if gv.cap.get(cv2.CAP_PROP_POS_FRAMES)%int(gv.fps)==0 and not gv.slidState:
         ui.horizontalSlider.setValue(gv.cap.get(cv2.CAP_PROP_POS_FRAMES))
  
    gv.timeRemain = gv.experTime - ((gv.cap.get(cv2.CAP_PROP_POS_FRAMES) - gv.startFrame) / gv.fps)
    if not gv.slidState:
        if 0 > gv.timeRemain:
            gv.timeRemain = 0
        elif gv.timeRemain < gv.experTime:
            gv.stateArray[-(int(gv.timeRemain*gv.fps)+1)] = gv.state
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
     ui.lcdNumber.display(gv.timeRemain)
     
     
graphTimer = QtCore.QTimer()
graphTimer.timeout.connect(lambda: plotState())

     
def startExper():
    gv.calc = False
    ui.stateLabel.setText("<html><head/><body><p><span style=\" font-size:18pt;color:#55aa00;\">Mobile</span></p></body></html>") #set to Mobile as default
    gv.timeRemain = gv.experTime #set start time
    gv.startFrame = gv.cap.get(cv2.CAP_PROP_POS_FRAMES)
    gv.graphArray[:] = 0
    gv.stateArray[:] = 0
    gv.state = True
    graphTimer.start(int(1000))

ui.startExperBut.clicked.connect(lambda:startExper())

def change():
    gv.state = not gv.state
    
ui.stateButton.clicked.connect(lambda:change())

def endCalc():
    timeImmobile = 0.0
    if gv.timeRemain <= 0 and not gv.calc:
        latency = np.nonzero(gv.stateArray==0)[0][0]
        ui.lcdNumber.display(0) #rounds timer to 0
        print(gv.stateArray)
        timeImmobile = (len(gv.stateArray) - np.sum(gv.stateArray)) / gv.fps
        print("Time Immobile:", timeImmobile)
        print("Latency to Immobility", latency/gv.fps)
        gv.calc = True
    if timer.remainingTime()!=-1:
        timer.start(timer.remainingTime())
        
timer.timeout.connect(lambda: endCalc())

def saveExcel(mouseID):
    stateFrame = pd.DataFrame(gv.stateArray[:],columns={"State"})
    stateFrame.to_csv(gv.fileName[0][0:-4] + "_" + mouseID + ".csv", index_label="Frame")

ui.saveButton.clicked.connect(lambda:saveExcel(ui.lineEditMouse.text()))
ui.lineEditMouse.returnPressed.connect(lambda: saveExcel(ui.lineEditMouse.text()))

sys.exit(app.exec_())