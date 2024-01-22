import serial
import serial.tools.list_ports
from tkinter import messagebox

ports_long=[a for a in serial.tools.list_ports.comports()]
ports=[a.name for a in ports_long]

class ND287():
    start_byte = bytes([27])
    end_byte = bytes([13])

    def __init__():
        for port in ports:
            ser=ND287.comm(port)
            if ser[0]:
                return ser[1]
        messagebox.showerror("Error", "Your \"ND-287\" is not connected. Use RS-232 to USB-interface to connect your \"ND-287\"")
        exit()

    def string_to_bytes(print_string):
        return ND287.start_byte+bytes([ord(a) for a in print_string])+ND287.end_byte

    def comm(port):
        ser = serial.Serial(
        port=port,
        baudrate=115200,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.SEVENBITS,
        timeout=0.2
        )
        ser.write(ND287.string_to_bytes("A0000"))
        answer=ser.read(999)
        if b'ND-287' in answer:
            return [True, ser]
        else:
            return [False, ser]

