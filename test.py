import easyocr
import cv2
# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])  # English language

# Load and crop the image (skip the icon on the left)
image = cv2.imread("CoC_scripts/resources/test_img.png")
h, w = image.shape[:2]
cropped = image[0:h, int(w * 0.2):w]

cv2.imshow("cropped", cropped)
cv2.waitKey(0)
# Run OCR
results = reader.readtext(cropped, detail=0)

# Join parts and filter out non-digit characters
text = " ".join(results)
digits_only = ''.join(char for char in text if char.isdigit() or char == ' ')

print("Raw OCR Output:", results)
print("Extracted Digits:", digits_only)
