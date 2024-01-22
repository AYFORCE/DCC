import cv2
import os
import numpy as np

os.environ['TESSDATA_TEMP_DIR'] = r'C:\Users\AY\Documents\tester'

# Initialize camera capture
cap = cv2.VideoCapture(0)

# Set camera resolution to 4K
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

# Flag to indicate if the corners have been selected
corners_selected = False

# Selected corners
corners = []

# Mouse callback function to handle corner selection
def select_corner(event, x, y, flags, param):
    global corners_selected, corners

    if event == cv2.EVENT_LBUTTONDOWN:
        corners.append((x, y))
        cv2.circle(first_picture, (x, y), 5, (0, 0, 255), -1)

        if len(corners) == 4:
            corners_selected = True


# Capture a frame from the camera
ret, frame = cap.read()

# Create a copy of the frame for corner selection
first_picture = frame.copy()

# Create a window to display the first picture
cv2.namedWindow('First Picture')
cv2.setMouseCallback('First Picture', select_corner)

while not corners_selected:
    cv2.imshow('First Picture', first_picture)
    cv2.waitKey(1)

# Extract the corner coordinates
top_left_corner = corners[0]
top_right_corner = corners[1]
bottom_left_corner = corners[2]
bottom_right_corner = corners[3]

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    # Warp the frame using the selected corners
    src_pts = np.float32([top_left_corner, top_right_corner, bottom_left_corner, bottom_right_corner])
    dst_pts = np.float32([[0, 0], [frame.shape[1], 0], [0, frame.shape[0]], [frame.shape[1], frame.shape[0]]])
    perspective_transform = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped_frame = cv2.warpPerspective(frame, perspective_transform, (frame.shape[1], frame.shape[0]))

    # Display the original frame and the warped frame
    cv2.imshow('Frame', frame)
    cv2.imshow('Warped Frame', warped_frame)

    # Check for keyboard input
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the windows
cap.release()
cv2.destroyAllWindows()
