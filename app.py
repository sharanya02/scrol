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


def circle(image, x, y, roudness, color):
    cv2.circle(image, (int(x), int(y)), roudness, color,
               thickness=5, lineType=cv2.LINE_8, shift=0)


def calculate_distance(l1, l2):
    v = np.array([l1[0], l1[1]])-np.array([l2[0], l2[1]])
    distance = np.linalg.norm(v)
    return distance


def calculate_moving_average(landmark, ran, LiT):   
    while len(LiT) < ran:               
        LiT.append(landmark)
    LiT.append(landmark)                
    if len(LiT) > ran:                  
        LiT.pop(0)
    return sum(LiT)/ran


def main(cap_device, mode, snstivty):
    dis = 0.7                           
    preX, preY = 0, 0
    nowCli, preCli = 0, 0               # previous left click state
    norCli, prrCli = 0, 0               # prev right click state
    douCli = 0                          # double click
    i, k, h = 0, 0, 0
    LiTx, LiTy, list0x, list0y, list1x, list1y, list4x, list4y, list6x, list6y, list8x, list8y, list12x, list12y = [
    ], [], [], [], [], [], [], [], [], [], [], [], [], []   # moving average ka list
    nowUgo = 1
    cap_width = 1280
    cap_height = 720
    start, c_start = float('inf'), float('inf')
    c_text = 0
    # webcam input settings
    window_name = 'Scrol'
    cv2.namedWindow(window_name)
    cap = cv2.VideoCapture(cap_device)
    cfps = int(cap.get(cv2.CAP_PROP_FPS))
    if cfps < 30:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
        cfps = int(cap.get(cv2.CAP_PROP_FPS))
    # smoothing amt
    ran = max(int(cfps/10), 1)
    hands = mp_hands.Hands(
        min_detection_confidence=0.8,   # detection reliability 
        min_tracking_confidence=0.8,    # tracking reilability
        max_num_hands=1                 # max numb of detections
    )
