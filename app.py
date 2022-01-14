# importing necessary libaries
import cv2
import mediapipe as mp
import tkinter as tk
import numpy as np
import platform
import time
import keyboard
from pynput.mouse import Button, Controller

# initializing
pf = platform.system()
mouse = Controller()
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
if pf == 'Windows':
    hotkey = 'Alt'
elif pf == 'Darwin':
    hotkey = 'Command'
elif pf == 'Linux':
    hotkey = 'xxx'             
screenRes = (0, 0)

#function to lay out basic arguments for tinker
def tinkerargs():
    global screenRes
    root = tk.Tk()
    root.title("Setup")
    root.geometry("500x500")
    screenRes = (root.winfo_screenwidth(),
                 root.winfo_screenheight())  
    Val1 = tk.IntVar()
    Val2 = tk.IntVar()
    Val4 = tk.IntVar()
    Val4.set(30)                        
    
    # camera number 
    Static1 = tk.Label(text='Camera Number').grid(row=1)
    for i in range(3):
        tk.Radiobutton(root,
                       value=i,
                       variable=Val1,
                       text=f'Device{i}'
                       ).grid(row=2, column=i*2)
    St1 = tk.Label(text='     ').grid(row=3)

    # choosing where camera is placed
    Static1 = tk.Label(text='Position of Camera').grid(row=4)
    place = ['Normal', 'Above', 'Behind']
    for i in range(3):
        tk.Radiobutton(root,
                       value=i,
                       variable=Val2,
                       text=f'{place[i]}'
                       ).grid(row=5, column=i*2)
    St1 = tk.Label(text='     ').grid(row=6)

    # choosing sensitivity (fps)
    Static4 = tk.Label(text='Sensitivity').grid(row=7)
    s1 = tk.Scale(root, orient='h',
                  from_=1, to=100, variable=Val4
                  ).grid(row=8, column=2)
    St4 = tk.Label(text='     ').grid(row=9)

    # start button
    Button = tk.Button(text="Let's start!", command=root.destroy).grid(
        row=10, column=2)

    root.mainloop()

    cap_device = Val1.get()            
    mode = Val2.get()                   
    snstivty = Val4.get()/10  #fps/10       
    return cap_device, mode, snstivty
