import multiprocessing
import time
import cv2 as cv

img = cv.imread("resources/template_stone_red_forest2.png", cv.IMREAD_GRAYSCALE)

cv.imshow("cplm", img)
cv.waitKey(0)
