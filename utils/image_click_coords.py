import cv2

# Mouse callback function
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Clicked at: ({x}, {y})")
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, f'({x},{y})', (x, y), font, 0.5, (255, 0, 0), 1)
        cv2.imshow('Image', img)

# Read an image
img = cv2.imread('../CoC_scripts/resources/attack_screen.png')  # Replace with your image path
if img is None:
    print("Error: Could not load image.")
    exit()

# Display the image
cv2.imshow('Image', img)

# Set the mouse callback function to our custom function
cv2.setMouseCallback('Image', click_event)

# Wait for a key press and close all windows
cv2.waitKey(0)
cv2.destroyAllWindows()