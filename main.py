import os
import random
import cv2
import pygame
from cvzone.FaceMeshModule import FaceMeshDetector
import cvzone
import time

# Initialize pygame for audio
pygame.mixer.init()

# Load background music
background_music = pygame.mixer.Sound('src/music/background.mp3')  # replace with your background music file
end_game_music = pygame.mixer.Sound('src/music/end.wav')

# Set the countdown time
countdown_time = 60  # 60 seconds for 1 minute


cap = cv2.VideoCapture(0)
cap.set(3, 1920)
cap.set(4, 1080)

detector = FaceMeshDetector(maxFaces=1)
idList = [0, 17, 78, 292]

# import images
folderEatable = 'src/eatable'
listEatable = os.listdir(folderEatable)
eatables = []
for object in listEatable:
    eatables.append(cv2.imread(f'{folderEatable}/{object}', cv2.IMREAD_UNCHANGED))

folderNonEatable = 'src/nonEatable'
listNonEatable = os.listdir(folderNonEatable)
nonEatables = []
for object in listNonEatable:
    nonEatables.append(cv2.imread(f'{folderNonEatable}/{object}', cv2.IMREAD_UNCHANGED))

currentObject = eatables[0]
pos = [300, 0]
speed = 20
count = 0
global isEatable
isEatable = True
gameOver = False
# Load the background image
background_image = cv2.imread('src/background.png', cv2.IMREAD_UNCHANGED)  # replace with your background image file
background_image = cv2.resize(background_image, (1280, 200)) 

background_music.play(-1)

def resetObject():
    global isEatable
    pos[0] = random.randint(100, 1180)
    pos[1] = 0
    randNo = random.randint(1, 2)  # change the ratio of eatables/ non-eatables
    if randNo == 0:
        currentObject = nonEatables[random.randint(0, 3)]
        isEatable = False
    else:
        currentObject = eatables[random.randint(0, 4)]
        isEatable = True

    return currentObject


# Get the current time
start_time = time.time()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = cvzone.overlayPNG(img, background_image, [0 , 0])
    current_time = time.time()
    elapsed_time = current_time - start_time
    remaining_time = max(0, countdown_time - int(elapsed_time))
    if gameOver is False:
        cv2.putText(img, str(count), (1100, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 5)
        cv2.putText(img, f"Time: {remaining_time}s", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1.5, (235, 137, 52), 2)

        if remaining_time == 0:
            gameOver = True
            end_game_music.play()
            start_time = time.time()
            elapsed_time = current_time - start_time
            remaining_time = max(0, countdown_time - int(elapsed_time))
        img, faces = detector.findFaceMesh(img, draw=False)
        # img, faces = detector.findFaceMesh(img, draw=True)
        img = cvzone.overlayPNG(img, currentObject, pos)
        pos[1] += speed

        if pos[1] > 720:
            currentObject = resetObject()

        if faces:
            face = faces[0]
            # for idNo,point in enumerate(face):
            #     cv2.putText(img,str(idNo),point,cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),1)

            up = face[idList[0]]
            down = face[idList[1]]

            for id in idList:
                cv2.circle(img, face[id], 5, (255, 0, 255), 5)
            # cv2.line(img, up, down, (0, 255, 0), 3)
            # cv2.line(img, face[idList[2]], face[idList[3]], (0, 255, 0), 3)

            upDown, _ = detector.findDistance(face[idList[0]], face[idList[1]])
            leftRight, _ = detector.findDistance(face[idList[2]], face[idList[3]])

            ## Distance of the Object
            cx, cy = (up[0] + down[0]) // 2, (up[1] + down[1]) // 2
            # cv2.line(img, (cx, cy), (pos[0] + 50, pos[1] + 50), (0, 255, 0), 3)
            distMouthObject, _ = detector.findDistance((cx, cy), (pos[0] + 50, pos[1] + 50))
            # print(distMouthObject)

            # Lip opened or closed
            ratio = int((upDown / leftRight) * 100)
            # print(ratio)
            if ratio > 60:
                mouthStatus = "Open"
            else:
                mouthStatus = "Closed"
            cv2.putText(img, mouthStatus, (50, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (235, 143, 52), 2)

            if distMouthObject < 100 and ratio > 60:
                if isEatable:
                    currentObject = resetObject()
                    count += 1
                    pygame.mixer.Sound('src/music/score.wav').play()
                else:
                    gameOver = True
                    end_game_music.play()
        cv2.putText(img, str(count), (1100, 50), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 5)
    else:
        cv2.putText(img,"Score: "+ str(count), (450, 300), cv2.FONT_HERSHEY_COMPLEX, 2, (235, 143, 52), 5)
        cv2.putText(img, "Game Over", (300, 400), cv2.FONT_HERSHEY_PLAIN, 7, (255, 0, 255), 10)
    cv2.imshow("Image", img)
    key = cv2.waitKey(1)

    if key == ord('r'):
        resetObject()
        gameOver = False
        start_time = time.time()
        elapsed_time = current_time - start_time
        remaining_time = max(0, countdown_time - int(elapsed_time))
        count = 0
        currentObject = eatables[0]
        isEatable = True
    elif key == ord('q'):
        break  # Exit the loop and terminate the program

# Release the capture and close the window when done
cap.release()
cv2.destroyAllWindows()

