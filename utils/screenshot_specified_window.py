import cv2 as cv
import pydirectinput
import opencv_utils as utils

if __name__ == '__main__':
    window_name = "Clash Of Clans"
    window = utils.get_windows(window_name)[0]
    screenshot = utils.get_image(window)

    cv.imshow(window_name, screenshot)
    cv.waitKey(0)
    cv.imwrite("screenshot.png", screenshot)
    cv.destroyAllWindows()