import numpy as np
from collections import defaultdict
from datetime import datetime as dt

from SQL_functions_V001 import write_ND287_SQL
from vinkeldrej_V001 import ND_287

class run_ND287():

    def __init__(self, cw, ccw, lavest, højest, målepunkter, steps, equipment, costumer_equipment, task_number):
        turn={"cw":cw, "ccw":ccw}

        if len(målepunkter) == 0:
            test_points=np.linspace(lavest, højest, num=steps)
        else:
            test_points=np.array(målepunkter)

        measurements={"cw":[],"ccw":[]}

        measurements["cw"]=defaultdict(dict)
        measurements["ccw"]=defaultdict(dict)

        self.complete_test(turn, test_points, measurements, equipment, costumer_equipment, task_number)

    def complete_test(self, turn, test_points, measurements, equipment, costumer_equipment, task_number):

        for rotation in turn:
            skipped = False
            for testnumber in range(self.find_max(turn)):
                ND=ND_287()
                ND.set_to_zero()
                measurements[rotation][testnumber+1]["rising"]=defaultdict(dict)
                measurements[rotation][testnumber+1]["falling"]=defaultdict(dict)
                if turn[rotation]["rising"]>0:
                    #self.preload(test_points.max(), rotation)
                    for count, angle in enumerate(test_points):
                        if count == 0: self.complete_procedure(0, rotation, measurements, testnumber, "rising")
                        self.complete_procedure(angle, rotation, measurements, testnumber, "rising")
                else:
                    skipped=True
                    #self.preload_fall(test_points.max()*1.1, rotation)
                if turn[rotation]["falling"]>0:
                    turn[rotation]["falling"]-=1
                    for count, angle in enumerate(reversed(test_points[:len(test_points)-(not skipped)])):
                        if count == 0 and turn[rotation]["rising"]==0: self.complete_procedure(0, rotation, measurements, testnumber, "falling")
                        if count == 0 and turn[rotation]["rising"]>0: turn[rotation]["rising"]-=1
                        self.complete_procedure(angle, rotation, measurements, testnumber, "falling")
        write_ND287_SQL(measurements, equipment, costumer_equipment, task_number)

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
        for a in turn:
            for b in turn[a]:
                højest.append(turn[a][b])
        return max(højest)

    def complete_procedure(self, angle, rotation, measurements, testnumber, streng):
        self.set_turn(angle, rotation)
        curtime=dt.now()
        self.receive(measurements, rotation, testnumber, angle, curtime, streng)

    def receive(self, measurements, rotation, testnumber, angle, curtime, streng):
        if rotation=="ccw":
            angle*=-1
        print(angle)
        measurements[rotation][testnumber+1][streng][angle]=[input(), ND_287().print_ND(), f"{curtime.year:04}{curtime.month:02}{curtime.day:02} {curtime.hour:02}:{curtime.minute:02}:{curtime.second}.{int(float(dt.now().microsecond/1000))}"]