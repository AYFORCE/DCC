import csv
from datetime import datetime as dt
import os

class CSV():

    def recover_CSV_vinkeldrej(equipment, measurements, costumer_equipment, task_number):

        datestuff = f'{dt.now().year}{dt.now().month}{dt.now().day}{dt.now().hour}{dt.now().minute}{dt.now().second}'

        file = open(f'recovery_CSV_for_{equipment}_{datestuff}.txt', 'a', newline="")
        w=csv.writer(file)
        header=["ID", "udgangspunkt", "direction", "measurement_number", "rising_or_falling", "analytical_value", "attempted_value", "measured_value", "date", "equipment", "costumer_equipment", "task_number"]
        w.writerow(header[-(len(header)-1):])
        for udgangspunkt in range(len(measurements)):
            for direction in measurements[udgangspunkt]:
                for testnumber in measurements[udgangspunkt][direction]:
                    for rise_fall in measurements[udgangspunkt][direction][testnumber]:
                        for goal in measurements[udgangspunkt][direction][testnumber][rise_fall]:
                            if goal == 0:
                                stringting=(udgangspunkt,direction,testnumber,"None",goal,measurements[udgangspunkt][direction][testnumber][rise_fall][goal][1],measurements[udgangspunkt][direction][testnumber][rise_fall][goal][0],measurements[udgangspunkt][direction][testnumber][rise_fall][goal][2],equipment,costumer_equipment,task_number)
                            else:
                                stringting=(udgangspunkt,direction,testnumber,rise_fall,goal,measurements[udgangspunkt][direction][testnumber][rise_fall][goal][1],measurements[udgangspunkt][direction][testnumber][rise_fall][goal][0],measurements[udgangspunkt][direction][testnumber][rise_fall][goal][2],equipment,costumer_equipment,task_number)
                            w.writerow(stringting)
        file.close()

    def txts(path):

        import glob, os
        os.chdir(path+r"\python")
        for file in glob.glob("recovery*.txt"):
            pass
        return file
    
    def destroy(path, kill):
        if kill:
            os.remove(CSV.txts(path))