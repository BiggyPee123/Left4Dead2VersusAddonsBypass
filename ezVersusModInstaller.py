import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import webbrowser
import requests
from bs4 import BeautifulSoup
import ctypes

script_dir = os.path.dirname(os.path.abspath(__file__))

workshop_path = ""
left4dead2_root_path = ""
left4dead2_sub_path = ""
selected_ids = []
title_cache = {}

def fetch_workshop_title(file_id):
    if file_id in title_cache:
        return title_cache[file_id]
    url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={file_id}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title_div = soup.find("div", class_="game_area_purchase_game")
            if title_div:
                title = title_div.find("h1").text.strip()
                if title.startswith("Subscribe to download"):
                    title = title.replace("Subscribe to download", "").strip()
                title_cache[file_id] = title
                return title
        return "Title not found"
    except Exception as e:
        print(f"Error fetching title for ID {file_id}: {e}")
        return "Title not found"

def truncate_text(text, max_length):
    if len(text) > max_length:
        return text[:max_length - 3] + "..."
    return text

def check_directory():
    global workshop_path, left4dead2_root_path, left4dead2_sub_path
    workshop_path = r"C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2\left4dead2\addons\workshop"
    left4dead2_root_path = r"C:\Program Files (x86)\Steam\steamapps\common\Left 4 Dead 2"
    left4dead2_sub_path = os.path.join(left4dead2_root_path, "left4dead2")
    if os.path.exists(workshop_path) and os.path.exists(left4dead2_root_path) and os.path.exists(left4dead2_sub_path):
        messagebox.showinfo("Loading", "The Program will take a Minute to load all Addons!")
        process_workshop_files()
        locate_button.pack_forget()
    else:
        messagebox.showwarning("Directory Not Found", 
                            "Left 4 Dead 2 directory not found at default location.\n"
                            "Please click 'Find Directory' to locate it manually.")
        locate_button.pack(fill=tk.X, pady=2)

def locate_directory():
    global workshop_path, left4dead2_root_path, left4dead2_sub_path
    folder_selected = filedialog.askdirectory(title="Select Left 4 Dead 2 Directory")
    if folder_selected:
        workshop_path = os.path.join(folder_selected, "left4dead2", "addons", "workshop")
        left4dead2_root_path = folder_selected
        left4dead2_sub_path = os.path.join(folder_selected, "left4dead2")
        if os.path.exists(workshop_path) and os.path.exists(left4dead2_root_path) and os.path.exists(left4dead2_sub_path):
            messagebox.showinfo("Loading", "The Program will take a Minute to load all Addons!")
            process_workshop_files()
            locate_button.pack_forget()
        else:
            messagebox.showwarning("Invalid Directory", 
                                 "The selected directory does not contain the required folders.\n"
                                 "Please select the main Left 4 Dead 2 folder containing the 'left4dead2' subfolder.")

def process_workshop_files(search_term=None):
    for widget in inner_frame.winfo_children():
        widget.destroy()
    try:
        image_files = [f for f in os.listdir(workshop_path) if f.endswith(".jpg")]
    except FileNotFoundError:
        messagebox.showwarning("Workshop Not Found", "Workshop directory not found. Please locate your Left 4 Dead 2 directory.")
        return

    existing_mods = check_gameinfo_for_mods()
    addons_with_mods = []
    addons_without_mods = []
    for image_file in image_files:
        file_id = os.path.splitext(image_file)[0]
        title = fetch_workshop_title(file_id)
        if file_id in existing_mods:
            addons_with_mods.append((file_id, image_file, title))
        else:
            addons_without_mods.append((file_id, image_file, title))
    if search_term:
        addons_with_mods = [addon for addon in addons_with_mods if search_term.lower() in addon[2].lower()]
        addons_without_mods = [addon for addon in addons_without_mods if search_term.lower() in addon[2].lower()]
    for file_id, image_file, _ in addons_with_mods:
        display_image_and_id(file_id, image_file, True)
    for file_id, image_file, _ in addons_without_mods:
        display_image_and_id(file_id, image_file, False)
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def check_gameinfo_for_mods():
    existing_mods = set()
    gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
    if os.path.exists(gameinfo_path):
        try:
            with open(gameinfo_path, "r") as file:
                lines = file.readlines()
            unique_lines = []
            seen_ids = set()
            for line in lines:
                if "Game				mods_" in line:
                    mods_id = line.strip().split("mods_")[-1]
                    if mods_id not in seen_ids:
                        seen_ids.add(mods_id)
                        unique_lines.append(line)
                    else:
                        continue
                else:
                    unique_lines.append(line)
            with open(gameinfo_path, "w") as file:
                file.writelines(unique_lines)
            existing_mods = seen_ids
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read gameinfo.txt: {e}")
    return existing_mods

def display_image_and_id(file_id, image_file, is_checked):
    image_path = os.path.join(workshop_path, image_file)
    try:
        image = Image.open(image_path)
        image_box = Image.new("RGB", (100, 100), (31, 31, 31))
        image.thumbnail((100, 100))
        image_box.paste(image, ((100 - image.width) // 2, (100 - image.height) // 2))
        photo = ImageTk.PhotoImage(image_box)
        frame = tk.Frame(inner_frame, bg="#181818", bd=0)
        frame.pack(fill=tk.X, pady=5)
        image_label = tk.Label(frame, image=photo, bg="#181818", bd=0)
        image_label.image = photo
        image_label.pack(side=tk.LEFT, padx=5)
        text_frame = tk.Frame(frame, bg="#181818", bd=0)
        text_frame.pack(side=tk.LEFT, padx=5)
        title = fetch_workshop_title(file_id)
        truncated_title = truncate_text(title, 40)
        id_label = tk.Label(text_frame, text=f"ID: {file_id} - {truncated_title}", font=("Arial", 12), bg="#181818", fg="white", bd=0)
        id_label.grid(row=0, column=0, columnspan=2, sticky="w")
        steam_link = f"https://steamcommunity.com/sharedfiles/filedetails/?id={file_id}"
        link_label = tk.Label(text_frame, text="Open in Steam", fg="lightblue", cursor="hand2", font=("Arial", 12), bg="#181818", bd=0)
        link_label.grid(row=1, column=0, sticky="w", padx=(0, 10))
        link_label.bind("<Button-1>", lambda e, url=steam_link: webbrowser.open(url))
        if file_id in check_gameinfo_for_mods():
            bypassed_label = tk.Label(text_frame, text="Already Bypassed", font=("Arial", 10), fg="orange", bg="#181818", bd=0)
            bypassed_label.grid(row=2, column=0, columnspan=2, sticky="w")
        var = tk.BooleanVar(value=is_checked)
        if is_checked and file_id not in selected_ids:
            selected_ids.append(file_id)
        checkbox = tk.Checkbutton(text_frame, text="Select", variable=var, command=lambda id=file_id: toggle_selection(id, var), bg="#181818", fg="white", selectcolor="#181818", bd=0)
        checkbox.grid(row=3, column=0, sticky="w", padx=(0, 10))
        checkbox.var = var
        checkbox.id = file_id
    except Exception as e:
        print(f"Error loading image {image_file}: {e}")

def toggle_selection(file_id, var):
    if var.get():
        if file_id not in selected_ids:
            selected_ids.append(file_id)
    else:
        if file_id in selected_ids:
            selected_ids.remove(file_id)

def apply_bypass():
    existing_mods = check_gameinfo_for_mods()
    if not selected_ids:
        for file_id in existing_mods:
            gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
            try:
                with open(gameinfo_path, "r") as file:
                    lines = file.readlines()
                lines = [line for line in lines if f"Game				mods_{file_id}" not in line]
                with open(gameinfo_path, "w") as file:
                    file.writelines(lines)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to modify gameinfo.txt: {e}")
                return
            mods_folder = os.path.join(left4dead2_root_path, f"mods_{file_id}")
            if os.path.exists(mods_folder):
                try:
                    shutil.rmtree(mods_folder)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove mods folder: {e}")
                    return
        messagebox.showinfo("Success", "All bypasses removed successfully!")
        selected_ids.clear()
        process_workshop_files()
        return

    for file_id in existing_mods:
        if file_id not in selected_ids:
            gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
            try:
                with open(gameinfo_path, "r") as file:
                    lines = file.readlines()
                lines = [line for line in lines if f"Game				mods_{file_id}" not in line]
                with open(gameinfo_path, "w") as file:
                    file.writelines(lines)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to modify gameinfo.txt: {e}")
                return
            mods_folder = os.path.join(left4dead2_root_path, f"mods_{file_id}")
            if os.path.exists(mods_folder):
                try:
                    shutil.rmtree(mods_folder)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove mods folder: {e}")
                    return

    for file_id in selected_ids:
        if file_id in existing_mods:
            continue
        vpk_file = os.path.join(workshop_path, f"{file_id}.vpk")
        if not os.path.exists(vpk_file):
            messagebox.showwarning("File Not Found", f"File {file_id}.vpk not found!")
            continue
        mods_folder = os.path.join(left4dead2_root_path, f"mods_{file_id}")
        os.makedirs(mods_folder, exist_ok=True)
        new_vpk_path = os.path.join(mods_folder, "pak01_dir.vpk")
        shutil.copy(vpk_file, new_vpk_path)
        gameinfo_path = os.path.join(left4dead2_sub_path, "gameinfo.txt")
        try:
            with open(gameinfo_path, "r") as file:
                lines = file.readlines()
            update_index = next(i for i, line in enumerate(lines) if "Game				update" in line)
            lines.insert(update_index, f"			Game				mods_{file_id}\n")
            with open(gameinfo_path, "w") as file:
                file.writelines(lines)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify gameinfo.txt: {e}")
            return

    messagebox.showinfo("Success", "Bypass applied successfully!")
    process_workshop_files()

def move_selected_to_top():
    for widget in inner_frame.winfo_children():
        widget.destroy()
    try:
        image_files = [f for f in os.listdir(workshop_path) if f.endswith(".jpg")]
    except FileNotFoundError:
        messagebox.showwarning("Workshop Not Found", "Workshop directory not found. Please locate your Left 4 Dead 2 directory.")
        return

    existing_mods = check_gameinfo_for_mods()
    selected_addons = []
    unselected_addons = []
    for image_file in image_files:
        file_id = os.path.splitext(image_file)[0]
        if file_id in selected_ids:
            selected_addons.append((file_id, image_file))
        else:
            unselected_addons.append((file_id, image_file))
    for file_id, image_file in selected_addons:
        display_image_and_id(file_id, image_file, True)
    for file_id, image_file in unselected_addons:
        display_image_and_id(file_id, image_file, False)
    canvas.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def search_addons(event=None):
    search_term = search_entry.get().strip()
    if search_term:
        process_workshop_files(search_term)
    else:
        process_workshop_files()

def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

root = tk.Tk()

try:
    root.iconbitmap(os.path.join(script_dir, 'Versus.ico'))
except tk.TclError:
    pass

try:
    myappid = 'BiggyPee123.West.Version1.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    print(f"Error setting application ID: {e}")

root.title("Versus Addon Bypasser")
root.geometry("700x600")
root.configure(bg="#181818")

def create_rounded_button(parent, text, command, font_size=9):
    button = tk.Button(
        parent,
        text=text,
        command=command,
        bg="#3a3a3a",
        fg="white",
        bd=1,
        highlightthickness=1,
        highlightbackground="white",
        highlightcolor="white",
        relief="flat",
        font=("Arial", font_size, "bold"),
        padx=10,
        pady=5,
        borderwidth=0,
        activebackground="#505050",
        activeforeground="white",
    )
    button.bind("<Enter>", lambda e: button.config(bg="#505050", highlightbackground="gray"))
    button.bind("<Leave>", lambda e: button.config(bg="#3a3a3a", highlightbackground="white"))
    return button

def open_west_link(event):
    webbrowser.open("https://www.youtube.com/@Zhytec")

def open_biggypee_link(event):
    webbrowser.open("https://www.youtube.com/@BGP475/videos")

# Create credit labels with hover effects
credit_label = tk.Label(root, text="Made by West/ZX using the DeepSeek AI", 
                       font=("Arial", 10), fg="white", bg="#181818", cursor="hand2")
credit_label.pack(side=tk.TOP, pady=(5, 0))
credit_label.bind("<Button-1>", open_west_link)

repackaged_label = tk.Label(root, text="Published by BiggyPee123 to the Github", 
                           font=("Arial", 10), fg="red", bg="#181818", cursor="hand2")
repackaged_label.pack(side=tk.TOP, pady=(0, 10))
repackaged_label.bind("<Button-1>", open_biggypee_link)

# Hover effects for credit labels
def on_enter_credit(e):
    e.widget.config(font=("Arial", 10, "underline"))

def on_leave_credit(e):
    e.widget.config(font=("Arial", 10))

credit_label.bind("<Enter>", on_enter_credit)
credit_label.bind("<Leave>", on_leave_credit)

repackaged_label.bind("<Enter>", on_enter_credit)
repackaged_label.bind("<Leave>", on_leave_credit)

label = tk.Label(root, text="Versus Addon Bypasser", font=("Arial", 14), bg="#181818", fg="white")
label.pack(pady=10)

search_frame = tk.Frame(root, bg="#181818")
search_frame.pack(fill=tk.X, padx=10, pady=5)

search_entry = tk.Entry(search_frame, font=("Arial", 12), bg="#242424", fg="white", insertbackground="white")
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

search_button = create_rounded_button(search_frame, "Search", search_addons)
search_button.pack(side=tk.LEFT)

search_entry.bind("<Return>", search_addons)

canvas = tk.Canvas(root, bg="#181818", bd=0, highlightthickness=0)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

style = ttk.Style()
style.theme_use("clam")
style.configure("Vertical.TScrollbar", background="#303030", troughcolor="#181818", bordercolor="#181818", arrowcolor="white")

canvas.config(yscrollcommand=scrollbar.set)

inner_frame = tk.Frame(canvas, bg="#181818", bd=0)
canvas.create_window((0, 0), window=inner_frame, anchor="nw")

bottom_bar = tk.Frame(root, bg="#181818")
bottom_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

locate_button = create_rounded_button(bottom_bar, "Find Directory", locate_directory, font_size=8)
apply_button = create_rounded_button(bottom_bar, "Apply", apply_bypass)
move_to_top_button = create_rounded_button(bottom_bar, "Move to Top", move_selected_to_top)

locate_button.pack(fill=tk.X, pady=2)
apply_button.pack(fill=tk.X, pady=2)
move_to_top_button.pack(fill=tk.X, pady=2)

canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.bind_all("<MouseWheel>", on_mouse_wheel)

check_directory()

root.mainloop()
