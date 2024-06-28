import cv2
import numpy as np
import os
from matplotlib import pyplot as plt

def capture_image_from_camera():
    # Initialize the camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None
    
    # Capture a single frame
    ret, frame = cap.read()
    
    # Release the camera
    cap.release()
    
    if not ret:
        print("Error: Could not capture image.")
        return None
    
    return frame

def crop_face(image):
    # Load the pre-trained Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    
    if len(faces) == 0:
        print("No face detected.")
        return None
    
    # Assume the first detected face is the one we want to crop
    (x, y, w, h) = faces[0]
    
    # Crop the face region from the image
    cropped_face = image[y:y+h, x:x+w]
    
    return cropped_face

def create_passport_photo(face_image):
    if face_image is None:
        print("Error: No face image provided.")
        return None
    
    # Resize the cropped face to the standard passport photo size (e.g., 2x2 inches at 300 dpi)
    passport_photo_size = (600, 600)  # 2x2 inches at 300 dpi
    resized_face = cv2.resize(face_image, passport_photo_size)
    
    # Create a white background image
    background = np.ones((600, 600, 3), dtype=np.uint8) * 255
    
    # Calculate the position to center the resized face on the background
    x_offset = (background.shape[1] - resized_face.shape[1]) // 2
    y_offset = (background.shape[0] - resized_face.shape[0]) // 2
    
    # Place the resized face on the white background
    background[y_offset:y_offset+resized_face.shape[0], x_offset:x_offset+resized_face.shape[1]] = resized_face
    
    return background

def display_images(original_image, processed_image):
    if original_image is not None:
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.title("Original Image")
        plt.imshow(cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB))
    
    if processed_image is not None:
        plt.subplot(1, 2, 2)
        plt.title("Processed Image")
        plt.imshow(cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB))
    
    plt.show()

def save_image(image, folder_path, file_name):
    if image is not None:
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, file_name)
        cv2.imwrite(file_path, image)
        print(f"Image saved at {file_path}")
    else:
        print("Error: No image to save.")

# Main script
if __name__ == "__main__":
    original_image = capture_image_from_camera()
    cropped_face = crop_face(original_image)
    processed_image = create_passport_photo(cropped_face)
    display_images(original_image, processed_image)
    
    # Save the processed image
    save_folder = 'Resume_maker_notebook/save_folder'
    save_file_name = 'passport_photo.png'
    save_image(processed_image, save_folder, save_file_name)
