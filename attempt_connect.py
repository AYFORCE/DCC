import serial
import time

ser = serial.Serial(
    port='COM10',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

ser.write(b'\r*IDN?\n')
time.sleep(0.1)

response = ser.readline()
print("Response:", response.decode('utf-8'))  # Assuming the response is a UTF-8 encoded string

#bytes([27])+bytes([ord(a) for a in print_string])+bytes([13])