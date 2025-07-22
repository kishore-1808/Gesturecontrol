Hand Gesture Mouse Controller 🖐️🖱️
This Python project lets you control your mouse using hand gestures detected through your webcam using MediaPipe, OpenCV, and PyAutoGUI.

✨ Features
🖱️ Move the mouse using your index finger

👆 Left click

👉 Right click

👆👆 Double click

📸 Take screenshot with audio feedback (saved in Downloads)

🔍 Zoom in/out (Ctrl + + / -)

🔃 Scroll up/down

🛠️ Libraries Used
Make sure to install the following Python libraries:

bash
Copy
Edit
pip install opencv-python mediapipe pyautogui numpy pygame pynput
Note: You must place a sound file named click_sound.mp3 in the project folder (or change the path in the code).

💡 How It Works
Your webcam tracks your hand using MediaPipe Hands.

Specific finger positions and distances are recognized as gestures.

These gestures trigger mouse actions using PyAutoGUI and pynput.

A screenshot gesture plays a sound using Pygame and saves the screenshot in your Downloads folder.

▶️ How to Run
Clone the repo or download the script.

Make sure all required libraries are installed.

Run the script:

bash
Copy
Edit
python your_script_name.py
Show your hand to the webcam and try the gestures!

📸 Screenshot Gesture
Gesture: Thumb and index finger touching tightly
Action: Screenshot is saved in Downloads/my_screenshot_<number>.png
Audio Feedback: Sound plays using pygame

🔚 Exit
Press q to exit the program.
