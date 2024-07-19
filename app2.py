import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import PyPDF2
import io
from PIL import Image, ImageTk
import cv2
import pygame
import threading
import time

class FileManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced File Manager")
        self.master.geometry("800x600")
        self.master.configure(bg="#f0f0f0")

        self.current_path = os.getcwd()
        self.history = [self.current_path]
        self.history_index = 0

        self.video_playing = False
        self.video_thread = None

        # pygame.init()
        # pygame.mixer.init()

        self.create_widgets()
        self.refresh_list()

    def create_widgets(self):
        # Top frame for navigation buttons, path and search
        top_frame = tk.Frame(self.master, bg="#f0f0f0")
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        back_button = ttk.Button(top_frame, text="←", command=self.go_back, width=3)
        back_button.pack(side=tk.LEFT, padx=(0, 5))

        forward_button = ttk.Button(top_frame, text="→", command=self.go_forward, width=3)
        forward_button.pack(side=tk.LEFT, padx=(0, 5))

        parent_button = ttk.Button(top_frame, text="↑", command=self.go_to_parent, width=3)
        parent_button.pack(side=tk.LEFT, padx=(0, 5))

        self.path_var = tk.StringVar()
        self.path_var.set(self.current_path)
        
        path_label = tk.Label(top_frame, text="Path:", bg="#f0f0f0")
        path_label.pack(side=tk.LEFT, padx=(5, 5))

        self.path_entry = tk.Entry(top_frame, textvariable=self.path_var, width=50)
        self.path_entry.pack(side=tk.LEFT, padx=(0, 5))

        go_button = ttk.Button(top_frame, text="Go", command=self.go_to_path)
        go_button.pack(side=tk.LEFT)

        # Frame for file list and content
        main_frame = tk.Frame(self.master, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # File list frame
        list_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(list_frame, width=40, height=20, bg="#ffffff", selectbackground="#e0e0e0")
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.file_listbox.bind('<Double-1>', self.open_item)

        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=list_scrollbar.set)

        # Content frame
        self.content_frame = tk.Frame(main_frame, bg="#ffffff", bd=1, relief=tk.SOLID)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.content_text = tk.Text(self.content_frame, wrap=tk.WORD, width=40, height=20, bg="#ffffff")
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        content_scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.content_text.yview)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=content_scrollbar.set)

        # Image label
        self.image_label = tk.Label(self.content_frame)

        # Video controls
        self.video_controls = tk.Frame(self.content_frame, bg="#ffffff")
        self.play_pause_button = ttk.Button(self.video_controls, text="Play", command=self.toggle_video)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)

        # Bottom frame for buttons
        bottom_frame = tk.Frame(self.master, bg="#f0f0f0")
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        refresh_button = ttk.Button(bottom_frame, text="Refresh", command=self.refresh_list)
        refresh_button.pack(side=tk.RIGHT)

    def refresh_list(self):
        self.file_listbox.delete(0, tk.END)
        try:
            for item in os.listdir(self.current_path):
                self.file_listbox.insert(tk.END, item)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def open_item(self, event):
        selected_item = self.file_listbox.get(self.file_listbox.curselection())
        item_path = os.path.join(self.current_path, selected_item)

        if os.path.isdir(item_path):
            self.navigate_to(item_path)
        else:
            self.display_file_content(item_path)

    def display_file_content(self, file_path):
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()

        # Clear previous content
        self.content_text.pack_forget()
        self.image_label.pack_forget()
        self.video_controls.pack_forget()
        
        if file_extension == '.pdf':
            self.display_pdf_content(file_path)
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
            self.display_image(file_path)
        elif file_extension in ['.mp4', '.avi', '.mov']:
            self.display_video(file_path)
        else:
            self.display_text_content(file_path)

    def display_pdf_content(self, pdf_path):
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n\n"
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, text)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to read PDF file: {str(e)}")

    def display_image(self, image_path):
        try:
            image = Image.open(image_path)
            image.thumbnail((700, 500))  # Resize image if it's too large
            photo = ImageTk.PhotoImage(image)
            self.image_label.config(image=photo)
            self.image_label.image = photo  # Keep a reference
            self.image_label.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to display image: {str(e)}")

    def display_video(self, video_path):
        self.video_path = video_path
        self.video_playing = False
        self.play_pause_button.config(text="Play")
        self.video_controls.pack(side=tk.BOTTOM, fill=tk.X)
        self.image_label.pack(fill=tk.BOTH, expand=True)

    def toggle_video(self):
        if self.video_playing:
            self.video_playing = False
            self.play_pause_button.config(text="Play")
        else:
            self.video_playing = True
            self.play_pause_button.config(text="Pause")
            if self.video_thread is None or not self.video_thread.is_alive():
                self.video_thread = threading.Thread(target=self.play_video)
                self.video_thread.start()

    def play_video(self):
        cap = cv2.VideoCapture(self.video_path)
        
        while self.video_playing:
            ret, frame = cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = Image.fromarray(cv2image)
                img.thumbnail((700, 500))
                imgtk = ImageTk.PhotoImage(image=img)
                self.image_label.imgtk = imgtk
                self.image_label.config(image=imgtk)
                self.master.update()
                time.sleep(0.03)  # Adjust for smoother playback
            else:
                self.video_playing = False
                self.play_pause_button.config(text="Play")
                break

        cap.release()

    def display_text_content(self, file_path):
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open file: {str(e)}")

    def go_to_path(self):
        new_path = self.path_var.get()
        if os.path.exists(new_path) and os.path.isdir(new_path):
            self.navigate_to(new_path)
        else:
            messagebox.showerror("Error", "Invalid directory path")

    def navigate_to(self, path):
        self.current_path = path
        self.path_var.set(self.current_path)
        self.refresh_list()
        
        # Update history
        self.history = self.history[:self.history_index + 1]
        self.history.append(self.current_path)
        self.history_index = len(self.history) - 1

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            self.path_var.set(self.current_path)
            self.refresh_list()

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            self.path_var.set(self.current_path)
            self.refresh_list()

    def go_to_parent(self):
        parent_path = os.path.dirname(self.current_path)
        if parent_path != self.current_path:
            self.navigate_to(parent_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManager(root)
    root.mainloop()