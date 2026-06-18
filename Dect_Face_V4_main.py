import datetime as dt
import logging as log
import math
import sys
import serial
import time
from threading import Timer
from time import process_time, sleep

import cv2
import mediapipe as mp
from numpy import negative, positive

font = cv2.FONT_HERSHEY_SIMPLEX

cascPath = "./features/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

eyePath ="./features/haarcascade_eye.xml"
eye_cascade = cv2.CascadeClassifier(eyePath)


#upperBodyPath = "/home/jetbot/road_following/cw2022/DectFace-features/haarcascade_upperbody.xml"
#upperCascade = cv2.CascadeClassifier(upperBodyPath)

glassPath = "./features/haarcascade_eye_tree_eyeglasses.xml"
glass_cascade =cv2.CascadeClassifier(glassPath)


log.basicConfig(filename='webcam.log',level=log.INFO)

video_capture = cv2.VideoCapture(0)

width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

dectHistory = []

fps = video_capture.get(cv2.CAP_PROP_FPS)
print(fps)

def faceBoxHasEyes (eyes,x, y, w, h ):
    for (ex,ey,ew,eh) in eyes:
        if faceHasEyes(x, y, w, h,ex,ey,ew,eh) == 1:
            return 1
    return 0
#function to find intersection of eyeboxes in face
def faceHasEyes(fx, fy, fw, fh, ex, ey, ew, eh):
    if ex >= (fx) & ex <= (fx+fw):
        if ey >= (fy) & ey <= (fy+fh):
            return 1
    return 0 

#def findCenter(faces):
    #resultX =0
    #resultY =0
    #for (x, y, w, h) in faces:
    #    iterateX = x+(w/2)
    #return

def calcFaceDistance(w,h):
    distancei = (2*3.14 * 180)/(w+h*360)*1000 + 3
    distancei = distancei *2.54
    return math.floor(distancei)

def hello():
    print("hello world!")

def TrackNear(capture):
    # Grabbing the Holistic Model from Mediapipe and
    # Initializing the Model
    mp_holistic = mp.solutions.holistic
    holistic_model = mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    while True:
        if not video_capture.isOpened():
            print('Unable to load camera.')
            sleep(5)
            pass

        
        
        # Initializing the drawng utils for drawing the facial landmarks on image
        mp_drawing = mp.solutions.drawing_utils

        # Capture frame-by-frame
        #ret, frame = video_capture.read()
        # (0) in VideoCapture is used to connect to your compyter's default camera
        #capture = cv2.VideoCapture(0)
    
        # Initializing current time and precious time for calculating the FPS
        previousTime = 0
        currentTime = 0
    
        # Initializing Dataholder for Gesture-Recognition
        keeper = [0]
        length_array = 4

        # Initializing current time and Max-Idle Time for Idle-Breakout
        inactive_start = process_time()
        idle_time = 10

        while capture.isOpened():
            # capture frame by frame
            try:
                ret, frame = capture.read()
            except:
                capture = cv2.VideoCapture(0)
                ret, frame = capture.read()
            
            # resizing the frame for better view
            frame = cv2.resize(frame, (800, 600))
            width = 800
            height = 600
            

            # Converting the from from BGR to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Making predictions using holistic model
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            image.flags.writeable = False
            results = holistic_model.process(image)
            image.flags.writeable = True

            # Converting back the RGB image to BGR
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            # Drawing the Facial Landmarks
            mp_drawing.draw_landmarks(
              image,
              results.face_landmarks,
              mp_holistic.FACEMESH_CONTOURS,
              mp_drawing.DrawingSpec(
                color=(255, 4, 144),
                thickness=1,
                circle_radius=1
              ),
              mp_drawing.DrawingSpec(
                color=(168, 255, 4),
                thickness=1,
                circle_radius=1
              )
            )

            # Drawing Right hand Land Marks
            mp_drawing.draw_landmarks(
              image, 
              results.right_hand_landmarks, 
              mp_holistic.HAND_CONNECTIONS
            )

            # Drawing Left hand Land Marks
            mp_drawing.draw_landmarks(
              image, 
              results.left_hand_landmarks, 
              mp_holistic.HAND_CONNECTIONS
            )

            # Calculating the FPS
            currentTime = time.time()
            fps = 1 / (currentTime-previousTime)
            previousTime = currentTime

            # Read Gestures
            a = 0
            try:
                a = CheckHands(results.left_hand_landmarks)
                #print(":Left Hand")
            except:
                try:
                    a = CheckHands(results.right_hand_landmarks)
                    #print(":Right Hand")
                except:
                    #print("No Hands")
                    a = 0
            keeper.append(a)
            if(len(keeper) > length_array):
                keeper.pop(0)
            print("Keeper: " + str(keeper))

            # Displaying FPS on the image
            cv2.putText(image, str(int(fps))+" FPS", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)

            # Display the resulting image
            cv2.imshow("Video", image)

            inactive_end = process_time()

            # Exit Loop
            if cv2.waitKey(5) & keeper.count(1) == length_array:
                print("Yes Please!")
                inactive_start = process_time()

                #########################################################
                #                   Placehold für Ja!                   #
                #########################################################

                for i in range(320):
                    StearCart(-0.2,0.2)
                
                time.sleep(3)

                for i in range(320):
                    StearCart(-0.2,0.2)

                keeper.append(0)
                keeper.pop(0)

                time.sleep(3)
                return

            if cv2.waitKey(5) & keeper.count(2) == length_array:
                print("No Thanks!")

                #########################################################
                #                   Placehold für Nein!                 #
                #########################################################

                for i in range(320):
                    StearCart(-0.2,0.2)
                print("Drehung ende!")
                
                time.sleep(1)

                return

# Function to Check Hand-Landmark Positions/Gestures
# return 0 - nothing noticed
# return 1 - Thumbs Up / Yes
# return 2 - Not Thanks / No

def CheckHands(CheckHand):
    Thumb_Tip = CheckHand.landmark[4]
    Middle_Finger_Tip = CheckHand.landmark[12]
    smallest = 1
    for data_point in CheckHand.landmark:
        if(data_point.y < smallest):
            smallest = data_point.y
    if(Thumb_Tip.y == smallest):
        #print("Thumbs Up!")
        #Vollgas? StearCart(10,10)
        return 1
    if(Middle_Finger_Tip.y == smallest):
        #print("No thanks!")
        return 2
    return 0 

def StearCart(lspeed,rspeed):
    left = 127 * lspeed
    right = 127 * rspeed
    
    send_run(left, right)


def send_run(left, right):
    ser = serial.Serial('/dev/ttyUSB0', 115200)
    data = "r,{0},{1}\n".format(int(left), int(right))
    print('Sending data', data)
    ser.write(data.encode('ascii'))
    #print(ser.readline())
    ser.close()


################################################################################################
# Main:
################################################################################################

distanceihld = 100
#StearCart(1,1)

while True:
    #print("Distance Hold: " + str(distanceihld))
    if not video_capture.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    try:
        frame = cv2.resize(frame, (800, 600))
        width = 800
        height = 600
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    except:
        video_capture = cv2.VideoCapture(0)
        ret,frame = video_capture.read()
        frame = cv2.resize(frame, (800, 600))
        width = 800
        height = 600
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )
        
    deltaX = 0
    
    #StrX, Stry = findCenter(faces)
    if(distanceihld < 40):
        print("Distance Hold: " + str(distanceihld))
        TrackNear(video_capture)
        time.sleep(10)
        for i in range(10):
            ret,frame = video_capture.read()
            distanceihld = 100

        #########################################################
        #               Placehold/Nach Bedienung                #
        #########################################################

    else:
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            currentMinDistance = 5000
            deltaX = 0
            
            #Eye detection
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            
            isFirst = True
            deltaXlast = 0
            distanceilast = 5050

            #draw Boxes for Eyes
            for (ex,ey,ew,eh) in eyes:
                cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
                
                
            if faceBoxHasEyes(eyes,x, y, w, h):
                ####################################################################################
                deltaX = int(width/2) - int((x+w/2))
                if(isFirst):
                    left = 0.1
                    right = 0.1
                    deltaX = int(width/2) - int((x+w/2))
                    distanceilast = calcFaceDistance(w,h)
                    print("First DX: " + str(deltaX))

                    toleranz = 40

                    if(negative(deltaX) > toleranz or deltaX > toleranz):
                        #if(negative(deltaX) > 20 or deltaX > 20):
                        if(deltaX > toleranz):
                            StearCart(0,left)
                        else:
                            StearCart(right,0)
                    #print("Left: "+ left +" Right: " + right)
                    else:
                        for i in range(5):
                            speed = 0.1
                            speed = speed * i
                            StearCart(speed,speed)
                            distanceilast = distanceilast - 1
                    deltaXlast = deltaX
                    isFirst = False
                ################
                distancei = calcFaceDistance(w,h)
                if distancei < currentMinDistance:
                    currentMinDistance = distancei
                    deltaX = int(width/2) - int((x+w/2))
                    dXText = "DeltaX: " + str(deltaX)
                    dZText = " Distance: " + str(distancei)
                    distanceihld = distancei
                    cv2.putText(frame,dXText +dZText, (5,100),font,1,(0,0,255),2)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 242, 255), 2)
                centerX = x+(w/2)
                centerY = y+(h/2)
                print("location x:" + str(centerX) + " y:" + str(centerY) + " Distance:" + str(dZText) +  " stering value: " + str(dXText))
                sleep(50/1000)
            else:
                if(deltaXlast != 0 & distanceilast > 40):
                    deltaXlast = deltaXlast - 2
                    distanceilast = distanceilast - 2
                    left = 0.2
                    right = 0.2
                    print("First DXlast: " + str(deltaXlast))
                    if(negative(deltaXlast) > 20 or deltaXlast > 20):
                        if(deltaXlast > 20):
                            left = left/2
                        else:
                            right = right/2
                    #print("Left: "+ left +" Right: " + right)
                    StearCart(left,right)

        
        try:
            cv2.line(frame,(int(width/2),int(height/2)),(int((width/2))-deltaX,int(height/2)),(255,0,0),5)

            # Display the resulting frame
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Display the resulting frame
            cv2.imshow('Video', frame)
        except:
            video_capture = cv2.VideoCapture(0)
            ret,frame = video_capture.read()

            cv2.line(frame,(int(width/2),int(height/2)),(int((width/2))-deltaX,int(height/2)),(255,0,0),5)

            # Display the resulting frame
            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Display the resulting frame
            cv2.imshow('Video', frame)
    
        

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
