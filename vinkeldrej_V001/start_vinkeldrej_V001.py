from run_vinkeldrej_V001 import run_ND287

# hvis målepunkterne ikke er "evenly spaced" fra minimum til maksimum, skal "højest" og "lavest" sættes lig 0,
# og de valgte målepunkter skal sættes ind kommasepereret i "målepunkter"

cw={"rising":3,"falling":0}
ccw={"rising":3,"falling":0}
lavest=0.5
højest=7200
steps=10
målepunkter=[0.5, 90, 180, 270, 360, 3590]
equipment="ROQ437"
costumer_equipment="AN1250464"
task_number="122.06870.01"

run_ND287(cw, ccw, lavest, højest, målepunkter, steps, equipment, costumer_equipment, task_number)