import cv2
import mediapipe as mp
import pyautogui
import numpy as np
from pynput.mouse import Button, Controller
import pygame
import random
import os

# Initialize
mouse = Controller()
screen_width, screen_height = pyautogui.size()

# MediaPipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands()
draw = mp.solutions.drawing_utils

# Audio setup
pygame.init()
pygame.mixer.init()
sound_path = os.path.join(os.path.expanduser("~"), "Downloads", "click_sound.mp3")  # Use any mp3 you like
if not os.path.exists(sound_path):
    # Create a simple sound if not exists
    pygame.mixer.quit()  # Stop mixer if not playing anything
    pygame.quit()

# Utility functions
def get_angle(a, b, c):
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(np.degrees(radians))
    return angle

def get_distance(landmark_list):
    if len(landmark_list) < 2:
        return None
    (x1, y1), (x2, y2) = landmark_list[0], landmark_list[1]
    L = np.hypot(x2 - x1, y2 - y1)
    return np.interp(L, [0, 1], [0, 1000])

# Gesture helpers
def find_finger_tip(processed):
    if processed.multi_hand_landmarks:
        hand_landmarks = processed.multi_hand_landmarks[0]
        return hand_landmarks.landmark[mpHands.HandLandmark.INDEX_FINGER_TIP]
    return None

def move_mouse(index_finger_tip):
    if index_finger_tip is not None:
        x = int(index_finger_tip.x * screen_width)
        y = int(index_finger_tip.y * screen_height)
        pyautogui.moveTo(x, y)

def is_left_click(landmarks_list, thumb_index_dist):
    return (get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) < 50 and
            get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) > 90 and
            thumb_index_dist > 50)

def is_right_click(landmarks_list, thumb_index_dist):
    return (get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) < 50 and
            get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) > 90 and
            thumb_index_dist > 50)

def is_double_click(landmarks_list, thumb_index_dist):
    return (get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) < 50 and
            get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) < 50 and
            thumb_index_dist > 50)

def is_screenshot(landmarks_list, thumb_index_dist):
    return (get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) < 50 and
            get_angle(landmarks_list[9], landmarks_list[10], landmarks_list[12]) < 50 and
            thumb_index_dist < 50)

def is_scroll_up(landmarks_list):
    return (get_angle(landmarks_list[0], landmarks_list[4], landmarks_list[8]) < 40)

def is_scroll_down(landmarks_list):
    return (get_angle(landmarks_list[0], landmarks_list[4], landmarks_list[8]) > 150)

def is_zoom_in(landmarks_list):
    dist = get_distance([landmarks_list[4], landmarks_list[8]])
    return dist and dist > 400

def is_zoom_out(landmarks_list):
    dist = get_distance([landmarks_list[4], landmarks_list[8]])
    return dist and dist < 100

# Gesture detection
def detect_gestures(frame, landmarks_list, processed):
    if len(landmarks_list) >= 21:
        index_finger_tip = find_finger_tip(processed)
        thumb_index_dist = get_distance([landmarks_list[4], landmarks_list[5]])

        if thumb_index_dist < 50 and get_angle(landmarks_list[5], landmarks_list[6], landmarks_list[8]) > 90:
            move_mouse(index_finger_tip)

        elif is_left_click(landmarks_list, thumb_index_dist):
            mouse.press(Button.left)
            mouse.release(Button.left)
            cv2.putText(frame, "Left Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        elif is_right_click(landmarks_list, thumb_index_dist):
            mouse.press(Button.right)
            mouse.release(Button.right)
            cv2.putText(frame, "Right Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        elif is_double_click(landmarks_list, thumb_index_dist):
            pyautogui.doubleClick()
            cv2.putText(frame, "Double Click", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        elif is_screenshot(landmarks_list, thumb_index_dist):
            screenshot = pyautogui.screenshot()
            label = random.randint(1, 1000)
            path = os.path.join(os.path.expanduser("~"), "Downloads", f"my_screenshot_{label}.png")
            screenshot.save(path)
            pygame.mixer.init()
            pygame.mixer.music.load("click_sound.mp3")  # Place your sound in working dir or change path
            pygame.mixer.music.play()
            cv2.putText(frame, "Screenshot Taken", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        elif is_scroll_up(landmarks_list):
            pyautogui.scroll(20)
            cv2.putText(frame, "Scroll Up", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        elif is_scroll_down(landmarks_list):
            pyautogui.scroll(-20)
            cv2.putText(frame, "Scroll Down", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        elif is_zoom_in(landmarks_list):
            pyautogui.hotkey('ctrl', '+')
            cv2.putText(frame, "Zoom In", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

        elif is_zoom_out(landmarks_list):
            pyautogui.hotkey('ctrl', '-')
            cv2.putText(frame, "Zoom Out", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 2)

# Main function
def main():
    cap = cv2.VideoCapture(0)

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            processed = hands.process(frameRGB)

            landmarks_list = []
            if processed.multi_hand_landmarks:
                hand_landmarks = processed.multi_hand_landmarks[0]
                draw.draw_landmarks(frame, hand_landmarks, mpHands.HAND_CONNECTIONS)

                for lm in hand_landmarks.landmark:
                    landmarks_list.append((lm.x, lm.y))

            detect_gestures(frame, landmarks_list, processed)

            cv2.imshow('Hand Gesture Controller', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
