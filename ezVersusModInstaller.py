import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import webbrowser

# Global variables
workshop_path = ""
left4dead2_root_path = ""
left4dead2_sub_path = ""
selected_ids = []  # List to store selected addon IDs

# Function to check if the directory exists
def check_directory():
    global workshop_path, left4dead2_root_path, left4dead2_sub_path
    workshop_path = r"C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\addons\workshop"
    left4dead2_root_path = r"C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2"
    left4dead2_sub_path = os.path.join(left4dead2_root_path, "left4dead2")
    if os.path.exists(workshop_path) and os.path.exists(left4dead2_root_path) and os.path.exists(left4dead2_sub_path):
        messagebox.showinfo("Directory Found", "The directory exists!")
        process_workshop_files()
    else:
        messagebox.showwarning("Directory Not Found", "The directory does not exist!")
        locate_button.pack(side=tk.LEFT, padx=10)  # Show the "Locate Directory" button

# Function to locate the Left 4 Dead 2 directory
def locate_directory():
    global workshop_path, left4dead2_root_path, left4dead2_sub_path
    folder_selected = filedialog.askdirectory(title="Select Left 4 Dead 2 Directory")
    if folder_selected:
        workshop_path = os.path.join(folder_selected, "left4dead2", "addons", "workshop")
        left4dead2_root_path = folder_selected
        left4dead2_sub_path = os.path.join(folder_selected, "left4dead2")
        if os.path.exists(workshop_path) and os.path.exists(left4dead2_root_path) and os.path.exists(left4dead2_sub_path):
            messagebox.showinfo("Directory Selected", f"You selected: {workshop_path}")
            process_workshop_files()
        else:
            messagebox.showerror("Invalid Directory", "The selected directory does not contain the required folders.")

# Function to process workshop files
def process_workshop_files():
    # Clear the existing content in the canvas
    for widget in inner_frame.winfo_children():
        widget.destroy()

    # Get all .jpg files in the workshop directory
    image_files = [f for f in os.listdir(workshop_path) if f.endswith(".jpg")]

    # Check gameinfo.txt for existing mods_ID entries
    existing_mods = check_gameinfo_for_mods()

    # Separate addons into two lists: those with existing mods_ID and those without
    addons_with_mods = []
    addons_without_mods = []

    for image_file in image_files:
        file_id = os.path.splitext(image_file)[0]  # Extract the file ID (number)
        if file_id in existing_mods:
            addons_with_mods.append((file_id, image_file))
        else:
            addons_without_mods.append((file_id, image_file))

    # Display addons with existing mods_ID first
    for file_id, image_file in addons_with_mods:
        display_image_and_id(file_id, image_file, True)

    # Display addons without existing mods_ID
    for file_id, image_file in addons_without_mods:
        display_image_and_id(file_id, image_file, False)

    # Update the scroll region of the canvas
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

# Function to check gameinfo.txt for existing mods_ID entries
def check_gameinfo_for_mods():
    existing_mods = set()
    gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
    if os.path.exists(gameinfo_path):
        try:
            with open(gameinfo_path, "r") as file:
                for line in file:
                    if "Game				mods_" in line:
                        mods_id = line.strip().split("mods_")[-1]
                        existing_mods.add(mods_id)
        except Exception as e:
            print(f"Error reading gameinfo.txt: {e}")
    return existing_mods

# Function to display the image, its file ID, a clickable Steam link, and a checkbox
def display_image_and_id(file_id, image_file, is_checked):
    # Load the image
    image_path = os.path.join(workshop_path, image_file)
    try:
        image = Image.open(image_path)
        image.thumbnail((100, 100))  # Resize the image to fit in the UI
        photo = ImageTk.PhotoImage(image)

        # Create a frame for each image, ID, link, and checkbox
        frame = tk.Frame(inner_frame, bg="#1f1f1f")
        frame.pack(fill=tk.X, pady=5)

        # Create a label for the image
        image_label = tk.Label(frame, image=photo, bg="#1f1f1f")
        image_label.image = photo  # Keep a reference to avoid garbage collection
        image_label.pack(side=tk.LEFT, padx=5)

        # Create a frame for the ID, link, and checkbox
        text_frame = tk.Frame(frame, bg="#1f1f1f")
        text_frame.pack(side=tk.LEFT, padx=5)

        # Create a label for the file ID
        id_label = tk.Label(text_frame, text=f"ID: {file_id}", font=("Arial", 12), bg="#1f1f1f", fg="white")
        id_label.pack()

        # Create a clickable Steam link
        steam_link = f"https://steamcommunity.com/sharedfiles/filedetails/?id={file_id}"
        link_label = tk.Label(text_frame, text="Open in Steam", fg="lightblue", cursor="hand2", font=("Arial", 12), bg="#1f1f1f")
        link_label.pack()
        link_label.bind("<Button-1>", lambda e, url=steam_link: webbrowser.open(url))

        # Create a checkbox
        var = tk.BooleanVar(value=is_checked)
        if is_checked:
            selected_ids.append(file_id)
        checkbox = tk.Checkbutton(text_frame, text="Select", variable=var, command=lambda id=file_id: toggle_selection(id, var), bg="#1f1f1f", fg="white", selectcolor="#1f1f1f")
        checkbox.pack()
    except Exception as e:
        print(f"Error loading image {image_file}: {e}")

# Function to toggle selection of an addon
def toggle_selection(file_id, var):
    if var.get():
        selected_ids.append(file_id)
    else:
        selected_ids.remove(file_id)

# Function to apply the bypass
def apply_bypass():
    # Get the list of existing mods_ID entries from gameinfo.txt
    existing_mods = check_gameinfo_for_mods()

    if not selected_ids:
        # If nothing is selected, delete all mods_ID entries and folders
        for file_id in existing_mods:
            # Remove the mods_ID entry from gameinfo.txt
            gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
            try:
                with open(gameinfo_path, "r") as file:
                    lines = file.readlines()

                # Remove the line with "Game				mods_{file_id}"
                lines = [line for line in lines if f"Game				mods_{file_id}" not in line]

                # Write the modified content back to the file
                with open(gameinfo_path, "w") as file:
                    file.writelines(lines)
            except Exception as e:
                print(f"Error removing mods_{file_id} from gameinfo.txt: {e}")

            # Remove the mods_ID folder
            mods_folder = os.path.join(left4dead2_root_path, f"mods_{file_id}")
            if os.path.exists(mods_folder):
                try:
                    shutil.rmtree(mods_folder)
                except Exception as e:
                    print(f"Error removing folder mods_{file_id}: {e}")

        messagebox.showinfo("Success", "All bypasses removed successfully!")
        return

    # Process selected addons
    for file_id in selected_ids:
        # Copy the .vpk file
        vpk_file = os.path.join(workshop_path, f"{file_id}.vpk")
        if not os.path.exists(vpk_file):
            messagebox.showerror("File Not Found", f"File {file_id}.vpk not found!")
            continue

        # Create the mods_ID folder in the root Left 4 Dead 2 directory
        mods_folder = os.path.join(left4dead2_root_path, f"mods_{file_id}")
        os.makedirs(mods_folder, exist_ok=True)

        # Copy and rename the .vpk file
        new_vpk_path = os.path.join(mods_folder, "pak01_dir.vpk")
        shutil.copy(vpk_file, new_vpk_path)

        # Modify the gameinfo.txt file in the left4dead2 subdirectory
        gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
        try:
            with open(gameinfo_path, "r") as file:
                lines = file.readlines()

            # Find the line with "Game				update"
            update_index = next(i for i, line in enumerate(lines) if "Game				update" in line)

            # Insert the mods_ID line above the "update" line
            lines.insert(update_index, f"			Game				mods_{file_id}\n")

            # Write the modified content back to the file
            with open(gameinfo_path, "w") as file:
                file.writelines(lines)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify gameinfo.txt: {e}")
            return

    # Process unselected addons (remove mods_ID entries and folders)
    for file_id in existing_mods:
        if file_id not in selected_ids:
            # Remove the mods_ID entry from gameinfo.txt
            gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
            try:
                with open(gameinfo_path, "r") as file:
                    lines = file.readlines()

                # Remove the line with "Game				mods_{file_id}"
                lines = [line for line in lines if f"Game				mods_{file_id}" not in line]

                # Write the modified content back to the file
                with open(gameinfo_path, "w") as file:
                    file.writelines(lines)
            except Exception as e:
                print(f"Error removing mods_{file_id} from gameinfo.txt: {e}")

            # Remove the mods_ID folder
            mods_folder = os.path.join(left4dead2_root_path, f"mods_{file_id}")
            if os.path.exists(mods_folder):
                try:
                    shutil.rmtree(mods_folder)
                except Exception as e:
                    print(f"Error removing folder mods_{file_id}: {e}")

    messagebox.showinfo("Success", "Bypass applied successfully!")

# Function to handle mouse wheel scrolling
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

# Create the main window
root = tk.Tk()
root.title("L4D2 Addon Bypasser")

# Set the window size to 700x600
root.geometry("700x600")

# Apply dark theme colors
root.configure(bg="#1f1f1f")  # Dark gray background

# Load and display the background image
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the script
    background_image_path = os.path.join(script_dir, "background.png")  # Path to the background image
    background_image = Image.open(background_image_path)
    background_image = background_image.resize((700, 100), Image.ANTIALIAS)  # Resize the image to fit
    background_photo = ImageTk.PhotoImage(background_image)

    background_label = tk.Label(root, image=background_photo, bg="#1f1f1f")
    background_label.image = background_photo  # Keep a reference to avoid garbage collection
    background_label.pack(side=tk.TOP, pady=10)  # Place the image at the top
except Exception as e:
    print(f"Error loading background image: {e}")

# Add the "made by West using DeepSeek ai" label below the image with a hyperlink
def open_west_link(event):
    webbrowser.open("https://www.youtube.com/@Zhytec")  # Replace with the actual link

credit_label = tk.Label(root, text="made by West using DeepSeek ai (click to view youtube channel)", font=("Arial", 10), fg="white", bg="#1f1f1f", cursor="hand2")
credit_label.pack(side=tk.TOP, pady=(5, 0))
credit_label.bind("<Button-1>", open_west_link)

# Add the "robbed by BiggyPee123" label in red below the credits with a hyperlink
def open_biggypee_link(event):
    webbrowser.open("https://www.youtube.com/@BGP475/videos")  # Replace with the actual link

repackaged_label = tk.Label(root, text="robbed by BiggyPee123 (click to view youtube channel)", font=("Arial", 10), fg="red", bg="#1f1f1f", cursor="hand2")
repackaged_label.pack(side=tk.TOP, pady=(0, 10))
repackaged_label.bind("<Button-1>", open_biggypee_link)

# Create a label
label = tk.Label(root, text="Left 4 Dead 2 Workshop Addons", font=("Arial", 14), bg="#1f1f1f", fg="white")
label.pack(pady=10)

# Create a canvas with a vertical scrollbar
canvas = tk.Canvas(root, bg="#1f1f1f")
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Add a vertical scrollbar
scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Configure the canvas to work with the scrollbar
canvas.config(yscrollcommand=scrollbar.set)

# Create a frame inside the canvas to hold the images and IDs
inner_frame = tk.Frame(canvas, bg="#1f1f1f")
canvas.create_window((0, 0), window=inner_frame, anchor="nw")

# Bind the canvas to the scrollbar
def on_canvas_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas.bind("<Configure>", on_canvas_configure)

# Bind the mouse wheel to the canvas for scrolling
canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# Create a bottom bar with the "Locate Directory" and "Apply Bypass" buttons
bottom_bar = tk.Frame(root, bg="#1f1f1f")
bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

locate_button = tk.Button(bottom_bar, text="Locate Directory", command=locate_directory, bg="#4b4b4b", fg="white")
apply_button = tk.Button(bottom_bar, text="Apply Bypass", command=apply_bypass, bg="#4b4b4b", fg="white")

# Pack the buttons initially
locate_button.pack(side=tk.LEFT, padx=10)
apply_button.pack(side=tk.RIGHT, padx=10)

# Check the directory when the program starts
check_directory()

# Start the main loop
root.mainloop()