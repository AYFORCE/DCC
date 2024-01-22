import cv2
import pytesseract
import os

os.environ['TESSDATA_TEMP_DIR'] = r'C:\Users\AY\Documents\tester'

# Initialize camera capture
cap = cv2.VideoCapture(0)

# Set up Tesseract OCR engine
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\AY\AppData\Local\Programs\Tesseract-OCR"

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()
    
    cv2.imshow('pic', frame)
    cv2.waitKey(1)

    ## VIRKER IKKE!!!
    # get color_scheme
    select_pic = cv2.selectROI("pic", frame)

    cv2.imshow('selection', select_pic)
    cv2.waitKey(1)
    ##

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply a threshold to the grayscale image to make it binary
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    cv2.imshow('grey', thresh)
    cv2.waitKey(1)

    # Use Tesseract OCR engine to detect text in the image
    text = pytesseract.image_to_string(thresh)#, config='--psm 11')
    
    # Check if the text contains a number
    if any(char.isdigit() for char in text):
        print(text)
    
    # Display the frame
    cv2.imshow('frame', frame)
    
    # Check for keyboard input
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
