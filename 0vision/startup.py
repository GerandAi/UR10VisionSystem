import socket
import time
import keyboard

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(1)
print('Connecting...')
s.connect(('192.168.3.3', 29999))
time.sleep(0.1)
rcvd = s.recv(4096)
print(rcvd)
print('\n')

def sendCommand(cmd):
    print(cmd)
    cmd = cmd + '\n'
    s.sendall(cmd.encode())
    time.sleep(0.1)
    rcvd = s.recv(4096)
    print(rcvd)
    print('\n')

#sendCommand('power on')
#time.sleep(0.3)
sendCommand('brake release')
time.sleep(5)
sendCommand('load vision.urp')
time.sleep(3)
sendCommand('play')

while True:
    if keyboard.is_pressed('Q') :  # if key 'q' is pressed
        sendCommand('stop')
        print('You Quit the Program!')
        break  # finishing the loop

