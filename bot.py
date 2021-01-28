import numpy as np
from PIL import ImageGrab
import cv2
import time
import pyautogui
from directKeys import moveMouseTo, mouseUp, mousePress, queryMousePosition, click
import keyboard
1.2021
ballImg = cv2.imread('ball.png', cv2.IMREAD_GRAYSCALE)
ballImg = cv2.Canny(ballImg, threshold1=50, threshold2=50)

basketImg = cv2.imread('basket.png', cv2.IMREAD_GRAYSCALE)
basketImg = cv2.Canny(basketImg, threshold1=50, threshold2=50)

restartImg = cv2.imread('restart.png', cv2.IMREAD_GRAYSCALE)
restartImg = cv2.Canny(restartImg, threshold1=50, threshold2=50)

gameCoords = [847, 264, 1265, 1002]

top = 675
top = (gameCoords[3] + gameCoords[1])//2
def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
    processed_img = cv2.Canny(processed_img, threshold1=50, threshold2=50)
    vertices = np.array([[0,0],[0,800],[850,800],[850,0]
                         ], np.int32)
    processed_img = roi(processed_img, [vertices])
    # lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, 20, 15)
    return processed_img

def draw_lines(img,lines):
    for line in lines:
        coords = line[0]
        cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], 3)

def roi(img, vertices):
    #blank mask:
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

method = cv2.TM_SQDIFF_NORMED

ballX, ballY = 0, 0

while True:
    #time.sleep(5)
    queryMousePosition()
    screen = np.array(ImageGrab.grab(bbox=gameCoords))
    new_screen = process_img(screen)

    result = cv2.matchTemplate(ballImg, new_screen, method)

    mn, _, mnLoc, _ = cv2.minMaxLoc(result)

    MPx, MPy = mnLoc

    trows, tcols = ballImg.shape[:2]
    if MPy > 0:
        ballX = MPx
        ballY = MPy
        ballX = gameCoords[0] + ballX + tcols//2
        ballY = gameCoords[1] + ballY + trows//2
        cv2.rectangle(new_screen, (MPx, MPy), (MPx + tcols, MPy + trows), (255, 0, 0), 2)
    if keyboard.is_pressed('shift') == False:
        moveMouseTo(gameCoords[0], gameCoords[1])
        result = cv2.matchTemplate(basketImg, new_screen, method)

        mn, _, mnLoc, _ = cv2.minMaxLoc(result)

        MPx, MPy = mnLoc

        trows, tcols = basketImg.shape[:2]

        cv2.rectangle(new_screen, (MPx, MPy), (MPx + tcols, MPy + trows), (255, 0, 0), 2)
        if MPy > 0 and ballY > 0:
            basketYField = MPy + trows//2
            basketX = gameCoords[0] + MPx + tcols//2
            basketY = gameCoords[1] + MPy + trows//2

            moveMouseTo(ballX, ballY)
            time.sleep(0.1)
            mousePress()
            time.sleep(0.1)
            moveMouseTo((basketX + ballX)//2, int(top - basketYField//1.85))
            time.sleep(0.1)
            mouseUp()
            time.sleep(0.1)
            ballY = 0

        result = cv2.matchTemplate(restartImg, new_screen, method)

        mn, _, mnLoc, _ = cv2.minMaxLoc(result)

        MPx, MPy = mnLoc

        trows, tcols = ballImg.shape[:2]

        if MPy > 0:
            resX = gameCoords[0] + MPx + tcols // 2
            resY = gameCoords[1] + MPy + trows // 2
            click(resX, resY)

    cv2.imshow('window', new_screen)



    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break