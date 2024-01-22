from run_vinkeldrej import run_ND287
from SQL_functions import write_ND287_SQL
from recover import CSV

# hvis målepunkterne ikke er "evenly spaced" fra minimum til maksimum, skal "højest" og "lavest" sættes lig 0,
# og de valgte målepunkter skal sættes ind kommasepereret i "målepunkter"

po_nummer="7300599838" # Til kalibrering 13-07-2023
temperatur=[24.6, 24.9, 25.3]

udgangspunkter=1

cw={"rising":1,"falling":0}
ccw={"rising":1,"falling":0}

lavest=0.5
højest=3590

steps=20
#tallet 0 er forbudt at tage med, da det følger med automatisk
målepunkter=[0.5, 36, 72, 90, 108, 144, 180, 216, 252, 270, 288, 324, 360, 540, 3420, 3590]

equipment="ROQ437"
costumer_equipment="AN1183180"
task_number="???"

no_of_measurements = 5
seconds_between = 0.01

path = r"C:\Users\AY\Desktop\vinkeldrej"

measurements = run_ND287(udgangspunkter, cw, ccw, lavest, højest, målepunkter, steps, 
                         no_of_measurements, seconds_between).return_measurements()

CSV.recover_CSV_vinkeldrej(equipment, measurements, costumer_equipment, task_number)

try:
    write_ND287_SQL(measurements, equipment, costumer_equipment, task_number)
    CSV.destroy(path, False)
except:
    pass
