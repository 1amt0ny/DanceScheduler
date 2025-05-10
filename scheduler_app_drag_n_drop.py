import os
import io
import csv
import threading
import traceback
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
from scheduler import Song, DanceClassScheduler

# Add macOS-specific fixes at the start
if os.name == 'posix':
    # Ensure the app appears in the Dock
    from Foundation import NSBundle
    bundle = NSBundle.mainBundle()
    if bundle:
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        if info:
            info['LSUIElement'] = False

log_path = os.path.expanduser("~/dancescheduler_log.txt")

def show_output_window(output_text):

    window = tk.Toplevel()
    window.title("Schedule Output")

    # Scrollable text area
    text_widget = tk.Text(window, wrap=tk.WORD, font=("Courier", 10))
    text_widget.insert("1.0", output_text)
    text_widget.pack(expand=True, fill=tk.BOTH)

    # Save button
    def save_to_file():
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")]
        )
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(output_text)
            messagebox.showinfo("Saved", f"Output saved to:\n{filepath}")

    save_button = tk.Button(window, text="💾 Save as File", command=save_to_file)
    save_button.pack(pady=5)


def decimal_minutes_to_minutes_seconds(decimal_minutes):
    minutes = int(decimal_minutes)
    seconds = int((decimal_minutes - minutes) * 60)
    return minutes, seconds


# Main Processing Function
def process_csv(input_filename):
    # Read & Parse CSV
    sample_songs = []
    with open(input_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                title = row["曲名"].strip()
                time_parts = row["时长"].strip().split(":")
                if len(time_parts) == 3:
                    minutes, seconds, _ = map(int, time_parts)
                elif len(time_parts) == 2:
                    minutes, seconds = map(int, time_parts)
                else:
                    raise ValueError("Invalid time format")
                duration = round(minutes + seconds / 60, 2)
                familiarity = int(row["熟悉度"])
                sample_songs.append(Song(title, duration, familiarity))
            except Exception as e:
                print(f"⚠️ Skipping row due to error: {row} ({e})")

    # Run the Scheduler
    scheduler = DanceClassScheduler(sample_songs)
    scheduler.generate_schedule() # Reuses your scheduler logic to create the schedule.

    buffer = io.StringIO()
    original_stdout = os.sys.stdout
    os.sys.stdout = buffer

    scheduler.print_schedule()
    print("\n📊 Summary of Song Play Counts:")
    for song in sample_songs:
        print(f"{song.title}: played {len(song.assigned_days)} times (desired: {song.desired_plays})")

    if scheduler.unassigned_songs:
        print("\n⚠️ Songs That Didn't Get Assigned:")
        for title, desired, assigned in scheduler.unassigned_songs:
            print(f"  - {title}: assigned {assigned} out of {desired} desired plays")

    os.sys.stdout = original_stdout
    return buffer.getvalue()


def handle_file_drop(event, status_var):
    filepath = event.data.strip('{}')  # Handles spaces in filenames on Windows
    if filepath.endswith(".csv"):
        threading.Thread(target=process_file, args=(filepath, status_var)).start()
    else:
        messagebox.showerror("Invalid File", "Please drop a valid .csv file.")


def choose_file(status_var):
    from tkinter import filedialog
    filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if filepath:
        threading.Thread(target=process_file, args=(filepath, status_var)).start()
        
# use popup
def process_file(filepath, status_var):
    try:
        status_var.set("Processing...")
        output_text = process_csv(filepath)
        show_output_window(output_text)
        status_var.set("✅ Done! Schedule is displayed.")
    except Exception as e:
        status_var.set("❌ Error!")
        messagebox.showerror("Processing Error", str(e))

# App GUI Setup
def run_app():
    root = TkinterDnD.Tk()
    
    # macOS specific configurations
    if os.name == 'posix':
        try:
            # Make the app appear in the Dock properly
            root.tk.call('tk::mac::useCompatibilityMenu', '0')
            root.createcommand('::tk::mac::Quit', root.quit)
            
            # Create a minimal menu
            menubar = tk.Menu(root)
            appmenu = tk.Menu(menubar, name='apple')
            menubar.add_cascade(menu=appmenu)
            root['menu'] = menubar
            
            # Add basic menu items
            appmenu.add_command(label='About Dance Scheduler')
            appmenu.add_separator()
            
            # Set the app icon (alternative method)
            img = tk.PhotoImage(file='app_icon.png')
            root.tk.call('wm', 'iconphoto', root._w, img)
        except Exception as e:
            print(f"macOS specific setup failed: {e}")
    
    
    root.title("Dance Scheduler App")
    root.geometry("500x250")
    root.configure(bg="white")

    status_var = tk.StringVar()
    status_var.set("Drop a CSV file or click 'Select CSV File'")

    label = tk.Label(root, text="🎵 Drag and drop your playlist CSV file below:", font=("Arial", 12), bg="white")
    label.pack(pady=10)

    drop_frame = tk.Frame(root, width=400, height=80, relief="ridge", bd=2, bg="#f0f0f0")
    drop_frame.pack(pady=10)
    drop_frame.pack_propagate(False)

    drop_label = tk.Label(drop_frame, text="Drop your file here", bg="#f0f0f0")
    drop_label.pack(expand=True)

    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", lambda e: handle_file_drop(e, status_var))

    button = tk.Button(root, text="Or Select a CSV File", command=lambda: choose_file(status_var))
    button.pack(pady=10)

    status_label = tk.Label(root, textvariable=status_var, fg="blue", bg="white", font=("Arial", 10))
    status_label.pack(pady=5)
    
    root.mainloop()

# Run the GUI When Launched
if __name__ == "__main__":
    try:
        run_app()
    except Exception as e:
        with open(log_path, "w") as f:
            f.write(traceback.format_exc())
        # raise # Also raise it for terminal testing
        messagebox.showerror("Fatal Error", f"The application encountered an error:\n\n{str(e)}")
