import os
import threading
from pyrsistent import l
import serial
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import time

os.system('echo 216 > /sys/class/gpio/export')
os.system('echo out > /sys/class/gpio/gpio216/direction')
os.system('echo 0 > /sys/class/gpio/gpio216/value')

current_speed = 0.1
current_steering = 0
lidar_distances = []

plt.ion()

x = []
y = []

figure, ax = plt.subplots(subplot_kw={'projection': 'polar'})

line1, = ax.plot(x, y)
line2, = ax.plot(x, y)
line3, = ax.plot(x, y)
line4, = ax.plot(x, y)
plt.ylim([0, 500])


def send_run(left, right):
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    data = "r,{0},{1}\n".format(int(left), int(right))
    print('Sending data', data)
    ser.write(data.encode('ascii'))
    #print(ser.readline())
    ser.close()


def interpret_data(data):
    speed = 0.2
    offset = 3
    global line1
    global figure
    global x
    global y
    x.clear()
    y.clear()    
    r = 0    
    l = 0
    b = []
    c = []
    d = [0]   
    theta = [np.deg2rad(90)] 
    avg = np.average(data)
    right_avg = np.average(data[0:379])
    left_avg = np.average(data[381:761])

    d.append(np.abs(left_avg - right_avg))
    argmin = np.argmin(data) 
    if argmin < 380 and argmin > 20:
        winkel = ((np.argmin(data)) * 0.25 - 95) + 180
    elif argmin > 380 and argmin < 740:
        winkel = ((np.argmin(data)) * 0.25 - 95)
    else:
        winkel = 90
    # winkel = ((np.argmin(data)) * 0.25 - 95) + 90
    # print(str(np.argmin(data)) + "  --  " + str(winkel))
    theta.append(np.deg2rad(winkel))

    for i in range(len(data)):
        rad = np.deg2rad((i * 0.25 - 95) + 90)
        x.append(rad)
        y.append(data[i])
        c.append(avg)
        if i < 380:
            b.append(right_avg)
        elif i > 380:
            b.append(left_avg)
        else:
            b.append(0)
        
    line1.set_xdata(x)
    line1.set_ydata(y)
    line2.set_xdata(x)
    line2.set_ydata(b)
    line3.set_xdata(x)
    line3.set_ydata(c)
    line4.set_xdata(theta)
    line4.set_ydata(d)
    figure.canvas.draw()
    figure.canvas.flush_events()

    steering_factor = np.round((winkel - 90) / 90, 2)
    steering_correction = d[1] / avg
    
    print("steering: " + str(steering_factor))
    if steering_factor < 0:        
        left = (127 * speed * steering_correction)
        right = ((1 - abs(steering_factor)) * (127+offset)) * speed
    elif steering_factor > 0:
        left = ((1 - abs(steering_factor)) * 127) * speed
        right = ((127+offset) * speed * steering_correction)
    else:
        left = 127 * speed
        right = 127 * speed  
    left = np.floor(left)
    right = np.floor(right)
    print("Right: " + str(right) + " Left: " + str(left))
    send_run(left, right)


def parse_data(bytes):
    global lidar_distances

    distanceBytes = bytes[14:-2]

    lidar_distances.clear()
    for i in range(761):
        currentBytes = distanceBytes[i*2:i*2+2]
        currentDistance = int.from_bytes(currentBytes, 'little')&0x1fff
        lidar_distances.append(currentDistance)
    interpret_data(lidar_distances)
    


def read_data():
    ser =serial.Serial('/dev/ttyTHS1',38400)
    while (True):
        # Find header
        header = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0x04, 0xff, 0x07]
        headerIndex = 0
        while (headerIndex < 10):
            byte = ser.read()
            number = int.from_bytes(byte, byteorder='big')

            if (number == header[headerIndex]):
                headerIndex += 1
            else:
                headerIndex = 0

        bytes = ser.read(1538)
        parse_data(bytes)


thread_lidar = threading.Thread(target=read_data, args=())
thread_lidar.start()
