import csv
from datetime import datetime as dt
import os

class CSV():

    def recover_CSV(equipment, measurements, costumer_equipment, task_number):
        datestuff = f'{dt.now().year}{dt.now().month}{dt.now().day}{dt.now().hour}{dt.now().minute}{dt.now().second}'
        file = open(f'recovery_CSV_for_{equipment}_{datestuff}.txt', 'a', newline="")
        w=csv.writer(file)
        header=["ID", "direction", "measurement_number", "rising_or_falling", "analytical_value", "attempted_value", "measured_value", "date", "equipment", "costumer_equipment", "task_number"]
        w.writerow(header[-(len(header)-1):])
        for direction in measurements:
            for testnumber in measurements[direction]:
                for rise_fall in measurements[direction][testnumber]:
                    for goal in measurements[direction][testnumber][rise_fall]:
                        stringting=(direction,testnumber,rise_fall,goal,measurements[direction][testnumber][rise_fall][goal][1],measurements[direction][testnumber][rise_fall][goal][0],measurements[direction][testnumber][rise_fall][goal][2],equipment,costumer_equipment,task_number)
                        w.writerow(stringting)
        file.close()

    def txts(path):

        import glob, os
        os.chdir(path+r"\python")
        for file in glob.glob("*.txt"):
            pass
        return file
    
    def destroy(path, kill):
        if kill:
            os.remove(CSV.txts(path))