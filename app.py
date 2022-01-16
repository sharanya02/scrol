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
   
    while cap.isOpened():
        p_s = time.perf_counter()
        success, image = cap.read()
        if not success:
            continue
        if mode == 1:                   # Mouse
            image = cv2.flip(image, 0)  # flip upside down
        elif mode == 2:                 # Touch
            image = cv2.flip(image, 1)  # flip horizontal

        # now we gotta invert the image horizontally and convert img from bgr to rgb
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False   
        results = hands.process(image)  # processing mediapipe
        image.flags.writeable = True    # drawing the hand annotations on imgs
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        image_height, image_width, _ = image.shape

        if results.multi_hand_landmarks:
            # drawing the skeletal structure of the hand
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if pf == 'Linux':           # In linux no key needs to be pressed
                can = 1
                c_text = 0
            else:                       # if not linux we gotta accept input from keyboard
                if keyboard.is_pressed(hotkey):  
                    can = 1
                    c_text = 0          
                else:                   # it wont work unless key is pressed
                    can = 0
                    c_text = 1          
                   
            if can == 1:
                # print(hand_landmarks.landmark[0])
                # now we substitute the current mouse position for preX and preY 
                if i == 0:
                    preX = hand_landmarks.landmark[8].x
                    preY = hand_landmarks.landmark[8].y
                    i += 1

                # moving average calculation of the landmark coordinates
                landmark0 = [calculate_moving_average(hand_landmarks.landmark[0].x, ran, list0x), calculate_moving_average(
                    hand_landmarks.landmark[0].y, ran, list0y)]
                landmark1 = [calculate_moving_average(hand_landmarks.landmark[1].x, ran, list1x), calculate_moving_average(
                    hand_landmarks.landmark[1].y, ran, list1y)]
                landmark4 = [calculate_moving_average(hand_landmarks.landmark[4].x, ran, list4x), calculate_moving_average(
                    hand_landmarks.landmark[4].y, ran, list4y)]
                landmark6 = [calculate_moving_average(hand_landmarks.landmark[6].x, ran, list6x), calculate_moving_average(
                    hand_landmarks.landmark[6].y, ran, list6y)]
                landmark8 = [calculate_moving_average(hand_landmarks.landmark[8].x, ran, list8x), calculate_moving_average(
                    hand_landmarks.landmark[8].y, ran, list8y)]
                landmark12 = [calculate_moving_average(hand_landmarks.landmark[12].x, ran, list12x), calculate_moving_average(
                    hand_landmarks.landmark[12].y, ran, list12y)]

                # now we divide the reference distance of the finger's relative coordinates, and then the distance obtained from the mediapipe, by this value
                absKij = calculate_distance(landmark0, landmark1)
                # calculating the euclidean distance between the tip of the index finger and the tip of the middle finger
                absUgo = calculate_distance(landmark8, landmark12) / absKij
                # now the euclidean distance between the second joint of the index finger and the tip of the thumb
                absCli = calculate_distance(landmark4, landmark6) / absKij

                posx, posy = mouse.position

                # now the tip of the index finger is the cursor
                # converting the camera coordinates to mouse movements
                nowX = calculate_moving_average(
                    hand_landmarks.landmark[8].x, ran, LiTx)
                nowY = calculate_moving_average(
                    hand_landmarks.landmark[8].y, ran, LiTy)

                dx = snstivty * (nowX - preX) * image_width
                dy = snstivty * (nowY - preY) * image_height

                if pf == 'Windows' or pf == 'Linux':     # for windows and linux we are adding 0.5  to mouse movements
                    dx = dx+0.5
                    dy = dy+0.5
                preX = nowX
                preY = nowY
               
                if posx+dx < 0:  
                    dx = -posx
                elif posx+dx > screenRes[0]:
                    dx = screenRes[0]-posx
                if posy+dy < 0:
                    dy = -posy
                elif posy+dy > screenRes[1]:
                    dy = screenRes[1]-posy


                if absCli < dis:
                    nowCli = 1          # nowCli is the left click state
                    circle(image, hand_landmarks.landmark[8].x * image_width,
                                hand_landmarks.landmark[8].y * image_height, 20, (0, 250, 250))
                elif absCli >= dis:
                    nowCli = 0
                if np.abs(dx) > 7 and np.abs(dy) > 7:
                    k = 0                           
               
                if nowCli == 1 and np.abs(dx) < 7 and np.abs(dy) < 7:
                    if k == 0:          
                        start = time.perf_counter()
                        k += 1
                    end = time.perf_counter()
                    if end-start > 1.5:
                        norCli = 1
                        circle(image, hand_landmarks.landmark[8].x * image_width,
                                    hand_landmarks.landmark[8].y * image_height, 20, (0, 0, 250))
                else:
                    norCli = 0

                # cursor
                if absUgo >= dis and nowUgo == 1:
                    mouse.move(dx, dy)
                    circle(image, hand_landmarks.landmark[8].x * image_width,
                                hand_landmarks.landmark[8].y * image_height, 8, (250, 0, 0))
                # left click
                if nowCli == 1 and nowCli != preCli:
                    if h == 1:                                  
                        h = 0
                    elif h == 0:                                # normal condition
                        mouse.press(Button.left)
                    # print('Click')
                # left click release
                if nowCli == 0 and nowCli != preCli:
                    mouse.release(Button.left)
                    k = 0
                    # print('Release')
                    if douCli == 0:                             # after the first click we are timing it
                        c_start = time.perf_counter()
                        douCli += 1
                    c_end = time.perf_counter()
                    if 10*(c_end-c_start) > 5 and douCli == 1:  # double click if u click again within 0.5 secs
                        mouse.click(Button.left, 2)             # double click
                        douCli = 0
                # right click
                if norCli == 1 and norCli != prrCli:
                    # mouse.release(Button.left)                
                    mouse.press(Button.right)
                    mouse.release(Button.right)
                    h = 1                                       
                    # print("right click")
                # scroll
                if hand_landmarks.landmark[8].y-hand_landmarks.landmark[5].y > -0.06:
                    mouse.scroll(0, -dy/50)                     # decreasing the scroll sensitivity
                    circle(image, hand_landmarks.landmark[8].x * image_width,
                                hand_landmarks.landmark[8].y * image_height, 20, (0, 0, 0))
                    nowUgo = 0
                else:
                    nowUgo = 1

                preCli = nowCli
                prrCli = norCli

        if c_text == 1:
            cv2.putText(image, f"Push {hotkey}", (20, 450),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        cv2.putText(image, "cameraFPS:"+str(cfps), (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        p_e = time.perf_counter()
        fps = str(int(1/(float(p_e)-float(p_s))))
        cv2.putText(image, "FPS:"+fps, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        dst = cv2.resize(image, dsize=None, fx=0.4,
                         fy=0.4)        
        cv2.imshow(window_name, dst)
        if (cv2.waitKey(1) & 0xFF == 27) or (cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) == 0):
            break
    cap.release()


if __name__ == "__main__":
    cap_device, mode, snstivty = tinkerargs()
    main(cap_device, mode, snstivty)
