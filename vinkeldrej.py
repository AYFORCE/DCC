import time
from tkinter import messagebox

from com_ports import ND287

class ND_287():

    fortegn=0
    enhed=0
    wanted_bits=[a for a in range(10,20)]

    ser = ND287.__init__()

    print(ser.name)

    def convert_to_deg(self, numb, unit):
        if unit == "G":
            return round(numb,4)
        else:
            messagebox.showerror("error", "Your \"ND-287\" is set up to measure something other than degrees")
            return numb

    def read_display(self):
        a=0
        HEIDENHAIN=[]
        while 1:
            x = str(self.ser.read())
            a+=1
            if a in self.wanted_bits:
                HEIDENHAIN.append(x[2])
            if a == 9:
                fortegn=float(x[2]+"1")
            if a == 21:
                enhed=x[2]
            if a == 27:
                b=fortegn*float(''.join(HEIDENHAIN))
                deg=self.convert_to_deg(b, enhed)
                a=0
                HEIDENHAIN=[]
                return deg

    def remove_func_bytes(self, answer):
        data=""
        for count, a in enumerate(answer):
            if not count == 0 and not count == len(answer)-1:
                data = data+a.decode("utf-8")
        return data

    def recieve_data(self):
        info=[]
        while info==[] or not info[len(info)-1]==bytes([13]):
            info.append(self.ser.read())
        trash=self.ser.read()
        data_package=self.remove_func_bytes(info)
        return data_package

    def request_data(self, streng):
        self.ser.write(ND287.string_to_bytes(streng))
        if streng=="A0000":
            for a in range(3):
                data=self.recieve_data()
                print(data)
        else:
            data=self.recieve_data()
            print(data)


    def get_data_display(self, streng):
        self.ser.write(ND287.string_to_bytes(streng))
        display = self.read_display()
        return display

    def set_to_zero(self):
        messagebox.showinfo(title="zero", message="When 'OK' is pressed the ND-287 is reset")
#        for a in range(5):
#            self.send_command("T0100")
#            time.sleep(0.1)
        self.send_command("T0000")
        time.sleep(0.1)
        self.send_command("T0104")

    def print_ND(self):
        print_string="F0002"
        return self.get_data_display(print_string)

    def send_command(self, streng):
        if streng.upper() in ["C","BACK"]:
            streng="T0100"
        self.ser.write(ND287.string_to_bytes(streng))
        trash=self.ser.read()

    def lock_keyboard(self):
        self.send_command("S0001")

    def open_keyboard(self):
        self.send_command("S0002")