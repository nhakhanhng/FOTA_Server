import os
import shutil
import customtkinter as ctk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
from utils.Cloud_COM.Cloud_COM import Cloud_COM

UPLOAD_DIR = "uploaded_files"

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Function to set background image for login screen
def set_background(root, image_path):
    bg_image = Image.open(image_path)
    bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg_image)
    bg_label = ctk.CTkLabel(root, image=bg_image, text="")
    bg_label.image = bg_image  # keep a reference!
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    return bg_label

# Create login window
class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("600x360")
        self.root.attributes("-topmost", True)
        
        set_background(self.root, "./Station_background.jpg")  # Set the background image

        self.frame = ctk.CTkFrame(root, bg_color="transparent")
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.username_label = ctk.CTkLabel(self.frame, text="Username", bg_color="transparent", text_color="white", font=("MS Sans Serif", 14))
        self.username_label.pack(pady=5)
        
        self.username_entry = ctk.CTkEntry(self.frame)
        self.username_entry.pack(pady=5)
        
        self.password_label = ctk.CTkLabel(self.frame, text="Password", bg_color="transparent", text_color="white", font=("MS Sans Serif", 14))
        self.password_label.pack(pady=5)
        
        self.password_entry = ctk.CTkEntry(self.frame, show="*")
        self.password_entry.pack(pady=5)
        
        self.login_button = ctk.CTkButton(self.frame, text="Login", command=self.check_login, fg_color="#1DB954", text_color="white", font=("MS Sans Serif", 12, "bold"))
        self.login_button.pack(pady=10)
    
    def check_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        # Check username and password
        if username == "admin" and password == "admin@@":
            self.root.destroy()
            main_window = ctk.CTk()
            HomeWindow(main_window)
            main_window.mainloop()
        else:
            messagebox.showerror("Error", "Incorrect username or password")

# Create home window without background image
class HomeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("FOTA-CBDS_Station")
        self.root.geometry("600x480")

        self.Cloud = Cloud_COM()

        self.header_frame = ctk.CTkFrame(root, height=80, fg_color="transparent")
        self.header_frame.pack(fill=ctk.X)

        self.header_label = ctk.CTkLabel(self.header_frame, text="Home", text_color="white", font=("MS Sans Serif", 24, "bold"))
        self.header_label.pack(pady=20)
        
        self.content_frame = ctk.CTkFrame(root, fg_color="transparent")
        self.content_frame.pack(expand=True, fill=ctk.BOTH)
        
        self.welcome_label = ctk.CTkLabel(self.content_frame, text="Welcome to CBDS-FOTA Uploader!", bg_color="transparent", text_color="white", font=("MS Sans Serif", 18))
        self.welcome_label.pack(pady=50)
        
        self.open_file_button = ctk.CTkButton(self.content_frame, text="Open File", command=self.open_file, fg_color="#1DB954", text_color="white", font=("MS Sans Serif", 12, "bold"))
        self.open_file_button.pack(pady=10)
        
        self.view_files_button = ctk.CTkButton(self.content_frame, text="View Uploaded Files", command=self.view_files, fg_color="#1DB954", text_color="white", font=("MS Sans Serif", 12, "bold"))
        self.view_files_button.pack(pady=10)
    
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
        if file_path:
            self.Cloud.SendSW(file_path)
            self.save_file(file_path)   
    
    def save_file(self, file_path):
        filename = os.path.basename(file_path)
        dest_path = os.path.join(UPLOAD_DIR, filename)
        shutil.copy(file_path, dest_path)
        messagebox.showinfo("Success", f"File {filename} has been uploaded successfully")
        self.view_files()
    
    def view_files(self):
        files_window = ctk.CTkToplevel(self.root)
        files_window.title("Uploaded Files")
        files_window.geometry("400x300")
        files_window.attributes("-topmost", True)
        files_window.config(bg="#2C2F33")

        tree = ttk.Treeview(files_window, columns=("File Name", "Path"), show="headings", height=10)
        tree.heading("File Name", text="File Name")
        tree.heading("Path", text="Path")
        tree.pack(expand=True, fill=ctk.BOTH, padx=10, pady=10)

        for filename in os.listdir(UPLOAD_DIR):
            filepath = os.path.join(UPLOAD_DIR, filename)
            tree.insert("", ctk.END, values=(filename, filepath))

        close_button = ctk.CTkButton(files_window, text="Close", command=files_window.destroy, fg_color="#1DB954", text_color="white", font=("MS Sans Serif", 12, "bold"))
        close_button.pack(pady=10)

# Run application
if __name__ == "__main__":
    ctk.set_appearance_mode("dark")  # Modes: "system" (default), "light", "dark"
    ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (default), "dark-blue", "green"

    root = ctk.CTk()
    app = LoginWindow(root)
    root.mainloop()
