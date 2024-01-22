import copy
import numpy as np
import time
from collections import defaultdict
from datetime import datetime as dt

from Calibration_GUI import CalibrationGUI, OverviewWindow
from vinkeldrej import ND_287

class run_ND287():

    def __init__(self, udgangspunkter, cw, ccw, lavest, højest, målepunkter, steps, meass, secs):

        turn = []
        
        for _ in range(udgangspunkter):
            turn.append({"cw": copy.deepcopy(cw), "ccw": copy.deepcopy(ccw)})

        if len(målepunkter) == 0:
            test_points=np.linspace(lavest, højest, num=steps)
        else:
            test_points=np.array(målepunkter)

        self.measurements = [{ "cw": defaultdict(dict), "ccw": defaultdict(dict) } for _ in range(udgangspunkter)]

        self.overview_window = OverviewWindow(self.measurements)
        self.overview_window.start()

        self.complete_test(turn, test_points, meass, secs)

    def complete_test(self, turn, test_points, meass, secs):

        for udgangspunkt in range(len(turn)):
            for rotation in turn[udgangspunkt]:
                skipped = False
                for testnumber in range(self.find_max(turn[udgangspunkt][rotation])):
                    ND=ND_287()
                    ND.set_to_zero() 
                    self.measurements[udgangspunkt][rotation][testnumber+1]["rising"]=defaultdict(dict)
                    self.measurements[udgangspunkt][rotation][testnumber+1]["falling"]=defaultdict(dict)
                    if turn[udgangspunkt][rotation]["rising"]>0:
                        #self.preload(test_points.max(), rotation)
                        for count, angle in enumerate(test_points):
                            if count == 0: self.complete_procedure(0, udgangspunkt, rotation, testnumber, "rising", meass, secs)
                            self.complete_procedure(angle, udgangspunkt, rotation, testnumber, "rising", meass, secs)
                    else:
                        skipped=True
                        #self.preload_fall(test_points.max()*1.1, rotation)
                    if turn[udgangspunkt][rotation]["falling"]>0:
                        turn[udgangspunkt][rotation]["falling"]-=1
                        for count, angle in enumerate(reversed(test_points[:len(test_points)-(not skipped)])):
                            if count == 0 and turn[udgangspunkt][rotation]["rising"]==0: self.complete_procedure(0, udgangspunkt, rotation, testnumber, "falling", meass, secs)
                            if count == 0 and turn[udgangspunkt][rotation]["rising"]>0: turn[udgangspunkt][rotation]["rising"]-=1
                            self.complete_procedure(angle, udgangspunkt, rotation, testnumber, "falling", meass, secs)
    
    def return_measurements(self):
        return self.measurements

    def preload_fall(self, highest, rotation):
        if rotation == "ccw":
            highest*=-1

        pass

    def preload(self, highest, rotation):
        if rotation == "ccw":
            highest*=-1
        
        pass

    def set_turn(self, angle, rotation):
        if rotation == "ccw":
            angle*=-1
        
        pass

    def find_max(self, turn):
        højest=[]
        for c in turn:
            højest.append(turn[c])
        return max(højest)

    def complete_procedure(self, angle, udgangspunkt, rotation, testnumber, streng, meass, secs):
        self.set_turn(angle, rotation)
        curtime=dt.now()
        self.receive(udgangspunkt, rotation, testnumber, angle, curtime, streng, meass, secs)

    def receive(self, udgangspunkt, rotation, testnumber, angle, curtime, streng, meass, secs):
        if rotation == "ccw":
            angle *= -1

        results = round(self.get_average(meass, secs), 3)

        gui = CalibrationGUI(results, angle)
        gui.run()

        while gui.repeat_flag:
            results = round(self.get_average(meass, secs), 3)
            gui = CalibrationGUI(results, angle)  # Create a new instance of the CalibrationGUI class
            gui.run()

        self.measurements[udgangspunkt][rotation][testnumber + 1][streng][angle] = [float(gui.user_input), results, f"{curtime.year:04}{curtime.month:02}{curtime.day:02} {curtime.hour:02}:{curtime.minute:02}:{curtime.second}.{int(float(dt.now().microsecond / 1000))}"]
        self.overview_window.update_measurements(self.measurements)

    def get_average(self, meass, secs):
        measurements2 = []
        for a in range(meass): 
            measurements2.append(ND_287().print_ND())
            time.sleep(secs)
        return sum(measurements2)/len(measurements2)