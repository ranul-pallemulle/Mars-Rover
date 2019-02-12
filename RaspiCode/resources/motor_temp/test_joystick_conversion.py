import matplotlib.pyplot as plt
import numpy as np
import pylab as pl


x = int(input('x'))
y = int(input('y'))

xcirc = np.linspace(-100,100,200)
ycirc = np.sqrt(100**2 - np.multiply(xcirc,xcirc))

plt.plot(xcirc,ycirc,'b')
plt.plot(xcirc,-ycirc,'b')
plt.plot(x,y,'rx')
plt.grid(color = 'grey')

v_left = 0
v_right = 0

ymax = 100
xmax = 100
D = 0.1
v_avg = y / ymax
v_left = v_avg
v_right = v_avg

#Sets a R
v_left = y / ymax + 1/2 * x /xmax
v_right = y /ymax - 1/2 * x / xmax

print("v_left = ",v_left,"v_right = ", v_right)

if v_left > v_right:
    print("Turning Right")
    
elif v_left < v_right:
    print("Turning Left")
    
else:
    print("Moving Straight")
