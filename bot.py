import numpy as np
from PIL import ImageGrab
import cv2
import time
import pyautogui
from directKeys import moveMouseTo, mouseUp, mousePress
import keyboard

ballImg = cv2.imread('ball.png', cv2.IMREAD_GRAYSCALE)
ballImg = cv2.Canny(ballImg, threshold1=150, threshold2=200)

basketImg = cv2.imread('basket.png', cv2.IMREAD_GRAYSCALE)
basketImg = cv2.Canny(basketImg, threshold1=150, threshold2=200)

gameCoords = [847, 264, 1265, 1002]

top = 400

def process_img(original_image):
    processed_img = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(processed_img, threshold1=150, threshold2=200)
    vertices = np.array([[0,0],[0,800],[850,800],[850,0]
                         ], np.int32)
    processed_img = roi(processed_img, [vertices])
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 180, 20, 15)
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
            result = cv2.matchTemplate(basketImg, new_screen, method)

            mn, _, mnLoc, _ = cv2.minMaxLoc(result)

            MPx, MPy = mnLoc

            trows, tcols = basketImg.shape[:2]

            cv2.rectangle(new_screen, (MPx, MPy), (MPx + tcols, MPy + trows), (255, 0, 0), 2)
            if MPy > 0:
                basketX = gameCoords[0] + MPx + tcols//2
                basketY = gameCoords[1] + MPy + tcols//2

                moveMouseTo(ballX, ballY)
                time.sleep(0.5)
                mousePress()
                time.sleep(0.5)
                moveMouseTo((basketX + ballX)//2 + (basketX - ballX)//15, top)
                time.sleep(0.5)
                mouseUp()
                time.sleep(0.5)


    cv2.imshow('window', new_screen)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break