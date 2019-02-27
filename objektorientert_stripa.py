"""

 Objekter:
 1) personer:
    radius
    masse=1
    posisjon
    fart
    "goal velocity"
    "ladning" (for kaffestands)
    venner?
    kraft
    naboer
  medlemsfunksjoner:
    soner/vektorfelt (regner ut hvilken sone personen befinner seg i)
 2) kaffestands:
    posisjon
 3) soner: (kanskje)
    posisjon
 4) vegger:
    lengde
    startpunkt
    sluttpunkt
    vertikal/horisontal (boolsk variabel?)

 Krefter:
 1) Hardsphere
 2) Avoidance
 3) Viljekraft
 4) Stokastisk kraft
 5) "Vennekraft"
 6) "Kaffekraft"





Spørsmål:
Hvordan skal krefter oppdateres? Som hardsphere (som oppdaterer alle personene), eller som avoidance som oppdaterer par?


 """


import random as rnd
from tkinter import *
import time
from math import sin, cos, sqrt, exp
import numpy as np
import os

num = 6  # number of agents
s = 10  # environment size in meters
rad = 0.1 # radius

# Agent Parameters (play with these)
k = 1.5 # Kræsjing: Liten k gir liten følsomhet, stor k gir stor følsomhet, k er konstanten i energiuttrykket
m = 2.0 # Liten m gir liten følsomhet for kræsjing, det ser også ut som den røde sirkelen akselererer raskere
t0 = 3
sight = 1  # Neighbor search range
maxF = 5  # Maximum force/acceleration
dt = 0.02 # Time step in Forward Euler
pixelsize = 500
#walls  = np.zeros((4*pixelsize-4, 2)) # koordinatene til veggene
framedelay = 30
drawVels = True
#randomness_factor = 4 # Stor faktor gir store tilfeldigheter i retningen til personene
win = Tk()
canvas = Canvas(win, width=pixelsize+10, height=pixelsize+10, background="#444")
canvas.pack()


# Initalized variables
ittr = 0
c = []  # center of agent
v = []  # velocity
gv = np.zeros(2)  # goal velocity
nbr = []  # neighbour list
nd = []  # neighbour distance list
QUIT = False
paused = True
step = False

circles = []
velLines = []
gvLines = []

class Person:
    def __init__(self, pos_x = 0, pos_y = 0, vel_x = 0, vel_y = 0, gv_x = 0, gv_y = 0):
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.rad = rad
        self.gv_x = gv_x
        self.gv_y = gv_y
        #self.coffeeCharge =
        self.neighbors = []




def initSim():
    global rad, c, v, gv

    print("")
    print("Agents avoid collisions using prinicples based on the laws of anticipation seen in human pedestrians.")
    print("Agents are white circles, Red agent moves faster.")
    print("Green Arrow is Goal Velocity, Red Arrow is Current Velocity")
    print("SPACE to pause, 'S' to step frame-by-frame, 'V' to turn the velocity display on/off.")
    print("")

    for i in range(num):

        #print(np.array(c).shape)

        circles.append(canvas.create_oval(0, 0, rad, rad, fill="white"))
        velLines.append(canvas.create_line(0, 0, 10, 10, fill="red"))
        gvLines.append(canvas.create_line(0, 0, 10, 10, fill="green"))
        """
        c = np.vstack((np.zeros(2), c))
        v = np.vstack((np.zeros(2),v))
        gv = np.vstack((np.zeros(2), gv))
        c[0][0] = rnd.uniform(0, s)
        c[0][1] = rnd.uniform(2*s/5, 3*s/5)

        ang = rnd.uniform(0, 2 * 3.141592)
        v[0][0] = np.random.normal(1, 1)*cos(ang)
        v[0][1] = np.random.normal(0.1, 1)*sin(ang)
        #gv[0] = 1.5 * np.array(v[0][0],v[0][1])
        gv[0] = np.array([np.random.normal(0,1),0])
        """

    c = np.vstack((np.zeros((num,2)), c))
    v = np.vstack((np.zeros((num,2)),v))

    for i in range(int(num/2)):
        c[i][0] = 3
        c[i][1] = 2*s/5+s*(i+1)/20
        c[i+int(num/2)][0] = 7
        c[i+int(num/2)][1] = 2*s/5+s*(i+1)/20

        v[i][0] = 1
        v[i][1] = 0
        v[i+int(num/2)][0] = -1
        v[i+int(num/2)][1] = 0

    gv = np.copy(v)

    np.delete(gv,-1)
    for i in range(num, len(c)):
        circles.append(canvas.create_oval(0, 0, s/(2*pixelsize), s/(2*pixelsize), fill="black"))
    c = np.array(c)


def findNeighbors():
    global nbr, nd, c, v

    nbr = []
    nd = []
    for i in range(num):
        vel_angle = np.arctan2(v[i][1], v[i][0])
        nbr.append([])
        nd.append([])
        for j in range(len(c)):
            if i == j: continue;
            d = c[i] - c[j]
            d_angle = np.arctan2(d[1], d[0])

            # if d[0] > s / 2.: d[0] = s - d[0]
            # if d[1] > s / 2.: d[1] = s - d[1]
            # if d[0] < -s / 2.: d[0] = d[0] + s
            # if d[1] < -s / 2.: d[1] = d[1] + s
            l2 = d.dot(d)
            s2 = sight ** 2
            # print("d_angle:", d_angle)
            # print("vel_angle:", vel_angle)
            if l2 < s2 and abs(d_angle - vel_angle) > np.pi / 2:
                nbr[i].append(j)
                nd[i].append(sqrt(l2))
        # for k in range(len(walls[0])):
        #    d = c[i] - walls[k]
        #    l2 = d.dot(d)
        ##    s2 = sight ** 2
        #    if l2 < s2:
        #        nbr[i].append(j)
        #        nd[i].append(sqrt(l2))




def drawWorld():
    global rad, s
    for i in range(len(c)):
        scale = pixelsize / s
        canvas.coords(circles[i], scale * (c[i][0] - rad), scale * (c[i][1] - rad), scale * (c[i][0] + rad),
                      scale * (c[i][1] + rad))

    for i in range(num):
        scale = pixelsize / s
        canvas.coords(velLines[i], scale * c[i][0], scale * c[i][1], scale * (c[i][0] + 1. * rad * v[i][0]),
                      scale * (c[i][1] + 1. * rad * v[i][1]))
        canvas.coords(gvLines[i], scale * c[i][0], scale * c[i][1], scale * (c[i][0] + 1. * rad * gv[i][0]),
                      scale * (c[i][1] + 1. * rad * gv[i][1]))
        if drawVels:
            canvas.itemconfigure(velLines[i], state="normal")
            canvas.itemconfigure(gvLines[i], state="normal")
        else:
            canvas.itemconfigure(velLines[i], state="hidden")
            canvas.itemconfigure(gvLines[i], state="hidden")

        double = False
        newX = c[i][0]
        newY = c[i][1] # Hva skjer hvis vi fjerner dette?

        if c[i][0] < rad:
            newX += s
            double = True
        if c[i][0] > s - rad:
            newX -= s
            double = True
        if c[i][1] < rad:
            newY += s
            double = True
        if c[i][1] > s - rad:
            newY -= s
            double = True
        if double:
            pass
            # canvas.coords(circles[i],scale*(newX-rad),scale*(newY-rad),scale*(newX+rad),scale*(newY+rad))

        # indicate velocity and goal velocities

