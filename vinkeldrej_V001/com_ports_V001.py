import serial
import serial.tools.list_ports
from tkinter import messagebox

ports_long=[a for a in serial.tools.list_ports.comports()]
ports=[a.name for a in ports_long]

def serial_port_ND287():

    return find_ND287_port(ports)

def find_ND287_port(ports):
    for port in ports:
        ser=comm(port)
        if ser[0]:
            return ser[1]
    messagebox.showerror("Error", "Your \"ND-287\" is not connected. Use RS-232 to USB-interface to connect your \"ND-287\"")
    exit()

def string_to_bytes(print_string):
    return bytes([27])+bytes([ord(a) for a in print_string])+bytes([13])

def comm(port):
    ser = serial.Serial(
    port=port,
    baudrate=115200,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.SEVENBITS,
    timeout=0.2
    )
    ser.write(string_to_bytes("A0000"))
    answer=ser.read(999)
    if b'ND-287' in answer:
        return [True, ser]
    else:
        return [False, ser]