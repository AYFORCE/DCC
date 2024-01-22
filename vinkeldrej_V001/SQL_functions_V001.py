import pypyodbc as odbc
from recover_V001 import CSV
import pandas as pd


DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'sqlDbMaaleteknik.ft.corp'
DATABASE_NAME = 'MaaleTeknik'

connection_string = f"""
    DRIVER={{{DRIVER_NAME}}};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trust_Connection=yes;
    uid=MaaleTeknik_Admin;
    pwd=45455TDTHTDFTHig7973412;
"""

path = r"C:\Users\AY\Desktop\vinkeldrej"

class write_ND287_SQL():

    def __init__(self, measurements, equipment, costumer_equipment, task_number):

        CSV.recover_CSV(equipment, measurements, costumer_equipment, task_number)
        for a in measurements:
            for b in measurements[a]:
                for c in measurements[a][b]:
                    for d in measurements[a][b][c]:
                        self.write_ND_287(equipment,a,b,c,d,measurements[a][b][c][d], costumer_equipment, task_number)
        CSV.destroy(path, False)


    def write_ND_287(self, equipment, direction, testnumber, rise_fall, goal, measured, costumer_equipment, task_number):

        conn = odbc.connect(connection_string)

        nextID=general_functions().find_next_ID("w_vinkeldrej_test", conn)

        header=["ID", "direction", "measurement_number", "rising_or_falling", "analytical_value", "attempted_value", "measured_value", "date", "equipment", "costumer_equipment", "task_number"]
        insertion=[nextID, direction, testnumber, rise_fall, goal, measured[1], measured[0], measured[2], equipment, costumer_equipment, task_number]

        header, insertion = general_functions().make_config(header, insertion)

        curser=conn.cursor()

        query=f"insert into w_vinkeldrej_test ({header}) values ({nextID}, '{direction}', {testnumber}, '{rise_fall}', '{goal}', '{measured[1]}', '{measured[0]}', '{measured[2]}', '{equipment}', '{costumer_equipment}', '{task_number}')"
        with conn:
            curser=conn.cursor()
            curser.execute(query)


class general_functions():

    def find_next_ID(self, table_name, conn):

        curser=conn.cursor()

        query="select max(ID) from " + table_name

        curser.execute(query)
        data = curser.fetchall()

        for row in data:
            number = row[0]
            if number == None:
                number=0

        return number+1

    def make_config(self, header, insertion):

        headers=[]
        insertions=[]
        for a,b in zip(header,insertion):
            headers.append(a)
            insertions.append(str(b))
        header=", ".join(headers)
        insertion=", ".join(insertions)

        return [header, insertion]
    
class Read_SQL():
    
    def read_specific(query, need):

        conn = odbc.connect(connection_string)
        curser=conn.cursor()

        curser.execute(query)
        data = list(curser.fetchall())

        return pd.DataFrame(data, columns=need.split(", "))

class upload():

    def upload_vinkeldrej(kill):
        top = ""

        df = pd.read_csv(CSV.txts(path))
        for count, header in enumerate(df.columns):
            if count == 0: top = "ID, " + header
            else:
                top = f'{top}, {header}'

        conn = odbc.connect(connection_string)

        nextID=general_functions().find_next_ID("w_vinkeldrej_test", conn)

        for count, a in enumerate(df.values):
            values = f"{count+nextID}, '{a[0]}', {a[1]}"
            for b in a[-(len(a)-2):]:
                values = f"{values}, '{b}'"

            conn = odbc.connect(connection_string)
            
            curser=conn.cursor()

            query=f"insert into w_vinkeldrej_test ({top}) values ({values})"
            with conn:
                curser=conn.cursor()
                curser.execute(query)

        CSV.destroy(path, kill)