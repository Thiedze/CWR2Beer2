import numpy as np
import matplotlib.pyplot as plt
import time

x = []
y = []

plt.ion()

figure, ax = plt.subplots(figsize=(8,6))
line1, = ax.plot(x, y)


while 1:
    x.clear()
    y.clear()
    for i in range(10):
        y.append(np.random.random())
        x.append(i)

    line1.set_xdata(x)
    line1.set_ydata(y)
    figure.canvas.draw()
    figure.canvas.flush_events()
    time.sleep(0.1)
