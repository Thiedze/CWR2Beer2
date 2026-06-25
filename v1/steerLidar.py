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
line5, = ax.plot(x, y)
plt.ylim([0, 500])


def send_run(left, right):
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    data = "r,{0},{1}\n".format(int(left), int(right))
    print('Sending data', data)
    ser.write(data.encode('ascii'))
    ser.close()

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def visualise_data(data, avg_left, avg_right, avg, theta, distance):
    global figure
    phi = []
    signal = []
    avgList1 = []
    avgList2 = []
    phi2 = [0]
    phi2.append(theta)
    dis = [0]
    dis.append(distance)
    for i in range(len(data)):
        rad = np.deg2rad((i * 0.25 - 95) + 90)
        phi.append(rad)
        signal.append(data[i])
        avgList1.append(avg)
        if i < 380:
            avgList2.append(avg_right)
        elif i > 380:
            avgList2.append(avg_left)
        else:
            avgList2.append(0)
    line1.set_xdata(phi)
    line1.set_ydata(signal)
    line2.set_xdata(phi)
    line2.set_ydata(avgList1)
    line3.set_xdata(phi)
    line3.set_ydata(avgList2)
    line4.set_xdata(phi2)
    line4.set_ydata(dis)
    line5.set_xdata(phi)
    line5.set_ydata(smooth(data, 10))
    figure.canvas.draw()
    figure.canvas.flush_events()

def interpret_data(data):
    speed = 0.2
    offset = 3
    global line1
    global figure
    global x
    global y
    x.clear()
    y.clear()
    avg = np.average(data)
    right_avg = np.average(data[0:379])
    left_avg = np.average(data[381:761])
    argmax = np.argmax(data)
    winkel = (argmax * 0.25 - 95) + 90
    theta = (np.deg2rad(winkel))
    d = (np.abs(left_avg - right_avg))

    steering_factor = np.round((winkel - 90) / 90, 2)
    steering_correction = d / avg

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
    visualise_data(data, left_avg, right_avg, avg, theta, d)


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
    ser = serial.Serial('/dev/ttyTHS1', 38400)
    while (True):
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
