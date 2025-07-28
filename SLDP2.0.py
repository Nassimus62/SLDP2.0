import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import pandas as pd
import os
from datetime import datetime, timedelta
import numpy as np
import random
import customtkinter as ctk
from PIL import Image, ImageTk
import io
import threading
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def monte_carlo_interpolation(value1, value2, num_simulations=1000):
    base_value = (value1 + value2) / 2
    std_dev = abs(value2 - value1) * 0.1
    simulations = np.random.normal(base_value, std_dev, num_simulations)
    return float(np.mean(simulations))

def process_sea_level_data(input_file_path, output_folder, status_box, progress_bar=None, progress_label=None, start_button=None):
    def update_progress(value, text):
        if progress_bar:
            progress_bar.set(value)
        if progress_label:
            progress_label.configure(text=text)
    
    try:
        status_box.insert(tk.END, "Treatment started...\n", "info")
        status_box.see(tk.END)
        status_box.update()
        update_progress(0.05, "Loading data...")
        
        data = pd.read_csv(input_file_path, sep='\t', header=None, names=['timestamp', 'sea_level'])
        status_box.insert(tk.END, f"Data loaded successfully. Found {len(data)} data points.\n", "success")
        status_box.see(tk.END)
        status_box.update()
        update_progress(0.15, "Processing timestamps...")
        
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['check'] = 'OK'
        update_progress(0.25, "Checking for time gaps...")
        
        new_rows = []
        status_box.insert(tk.END, "Checking for time gaps and interpolating using Monte Carlo method...\n", "info")
        status_box.see(tk.END)
        status_box.update()
        
        total_rows = len(data) - 1
        for i in range(total_rows):
            if i % max(1, int(total_rows/20)) == 0:
                update_progress(0.25 + (i/total_rows*0.35), f"Interpolating: {i}/{total_rows}")
                
            current_time = data.iloc[i]['timestamp']
            next_time = data.iloc[i + 1]['timestamp']

            if next_time - current_time == timedelta(minutes=2):
                missing_time = current_time + timedelta(minutes=1)
                interpolated_level = monte_carlo_interpolation(
                    data.iloc[i]['sea_level'], 
                    data.iloc[i + 1]['sea_level']
                )
                new_rows.append({'timestamp': missing_time, 'sea_level': interpolated_level, 'check': 'Interpolated'})

        data = pd.concat([data, pd.DataFrame(new_rows)], ignore_index=True)
        data = data.sort_values('timestamp')
        status_box.insert(tk.END, f"Interpolated {len(new_rows)} data points using Monte Carlo simulation.\n", "success")
        status_box.see(tk.END)
        status_box.update()
        update_progress(0.65, "Identifying segments...")
        
        segments = []
        current_segment = [data.iloc[0]]
        status_box.insert(tk.END, "Identifying segments...\n", "info")
        status_box.see(tk.END)
        status_box.update()

        for i in range(1, len(data)):
            if data.iloc[i]['timestamp'] - data.iloc[i - 1]['timestamp'] > timedelta(minutes=2):
                segments.append(pd.DataFrame(current_segment))
                current_segment = []
            current_segment.append(data.iloc[i])

        if current_segment:
            segments.append(pd.DataFrame(current_segment))

        status_box.insert(tk.END, f"Identified {len(segments)} segments.\n", "success")
        status_box.see(tk.END)
        status_box.update()
        update_progress(0.75, "Saving segments...")
        
        for i, segment in enumerate(segments):
            update_progress(0.75 + ((i+1)/len(segments)*0.2), f"Saving segment {i+1}/{len(segments)}")
            
            output_file = os.path.join(output_folder, f"segment_{i + 1}.xlsx")
            segment.to_excel(output_file, index=False)
            message = f"Saved segment {i + 1} with {len(segment)} data points to {output_file}\n"
            status_box.insert(tk.END, message, "success")
            status_box.see(tk.END)
            status_box.update()
        
        status_box.insert(tk.END, "Treatment completed successfully!\n", "complete")
        status_box.see(tk.END)
        status_box.update()
        update_progress(1.0, "Completed")
        
        animate_completion(status_box)
        
    except Exception as e:
        status_box.insert(tk.END, f"Error during processing: {str(e)}\n", "error")
        status_box.see(tk.END)
        status_box.update()
        update_progress(0, "Failed")
    
    finally:
        if start_button:
            start_button.configure(state="normal")

def animate_completion(status_box):
    completion_frames = [
        "🌊 ░░░░░░░░░░ 🌊",
        "🌊 ▓░░░░░░░░░ 🌊",
        "🌊 ▓▓░░░░░░░░ 🌊",
        "🌊 ▓▓▓░░░░░░░ 🌊",
        "🌊 ▓▓▓▓░░░░░░ 🌊",
        "🌊 ▓▓▓▓▓░░░░░ 🌊",
        "🌊 ▓▓▓▓▓▓░░░░ 🌊",
        "🌊 ▓▓▓▓▓▓▓░░░ 🌊",
        "🌊 ▓▓▓▓▓▓▓▓░░ 🌊",
        "🌊 ▓▓▓▓▓▓▓▓▓░ 🌊",
        "🌊 ▓▓▓▓▓▓▓▓▓▓ 🌊",
        "✨ COMPLETED ✨"
    ]
    
    for frame in completion_frames:
        status_box.insert(tk.END, f"\r{frame}", "complete")
        status_box.see(tk.END)
        status_box.update()
        time.sleep(0.12)
        if frame != completion_frames[-1]:
            status_box.delete("end-2c linestart", "end-1c")

def create_gui():
    root = ctk.CTk()
    root.title("Sea Level Data Processor")
    root.attributes('-fullscreen', True)
    root.bind("<Escape>", lambda event: root.attributes('-fullscreen', False))
    
    try:
        icon = tk.PhotoImage(data=b'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
        root.iconphoto(True, icon)
    except:
        pass
    
    ACCENT_COLOR = "#3a7ebf"
    SUCCESS_COLOR = "#2e8b57"
    ERROR_COLOR = "#b22222"
    WARNING_COLOR = "#ff8c00"
    
    is_dark_mode = tk.BooleanVar(value=True)
    input_path = tk.StringVar()
    output_path = tk.StringVar()
    
    def animate_theme_transition(from_dark, to_dark):
        steps = 10
        duration = 0.3
        step_time = duration / steps
        
        for i in range(steps + 1):
            progress = i / steps
            if from_dark and not to_dark:  # Dark to Light
                opacity = 1 - progress
            else:  # Light to Dark
                opacity = progress
                
            root.update()
            time.sleep(step_time)
    
    def toggle_theme():
        current_is_dark = is_dark_mode.get()
        
        if current_is_dark:
            ctk.set_appearance_mode("dark")
            status_box.configure(bg="#1e1e1e", fg="#e0e0e0")
            status_box.tag_configure("maker", foreground="#fc8c2b")
            status_box.tag_configure("info", foreground="#ffffff")
            status_box.tag_configure("success", foreground="#6bc46b")
            status_box.tag_configure("warning", foreground="#ffc107")
            status_box.tag_configure("error", foreground="#ff5252")
            status_box.tag_configure("complete", foreground="#7fff7f", font=("Consolas", 10, "bold"))
            
            theme_btn.configure(fg_color="#2d2d2d")
            theme_icon.configure(text="", text_color="#ffe680")
            theme_label.configure(text="Dark Mode \u263E", text_color="#FFFF00")
        else:
            ctk.set_appearance_mode("light")
            status_box.configure(bg="#f5f5f5", fg="#212121")
            status_box.tag_configure("maker", foreground="#07008a")
            status_box.tag_configure("info", foreground="#000000")
            status_box.tag_configure("success", foreground="#006e08")
            status_box.tag_configure("warning", foreground="#ff8c00")
            status_box.tag_configure("error", foreground="#b22222")
            status_box.tag_configure("complete", foreground="#2e8b57", font=("Consolas", 10, "bold"))
            
            theme_btn.configure(fg_color="#f0f0f0")
            theme_icon.configure(text="", text_color="#ff9d00")
            theme_label.configure(text="Light Mode \u2600", text_color="#370040")
    
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
    top_frame = ctk.CTkFrame(main_frame, corner_radius=15, fg_color=ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"])
    top_frame.pack(fill=tk.X, pady=(0, 20))
    
    logo_label = ctk.CTkLabel(top_frame, text="🌊", font=ctk.CTkFont(size=36))
    logo_label.pack(side=tk.LEFT, padx=20, pady=10)
    
    title_label = ctk.CTkLabel(
        top_frame, 
        text="Sea Level Data Processor V2.0",
        font=ctk.CTkFont(family="Helvetica", size=28, weight="bold")
    )
    title_label.pack(side=tk.LEFT, padx=0, pady=10)
    
    version_label = ctk.CTkLabel(
        top_frame, 
        text="", 
        font=ctk.CTkFont(size=14),
        text_color="#888888"
    )
    version_label.pack(side=tk.LEFT, padx=10, pady=10, anchor="s")
    
    theme_btn = ctk.CTkFrame(
        top_frame,
        width=140,
        height=40,
        corner_radius=20,
        fg_color="#2d2d2d"
    )
    theme_btn.pack(side=tk.RIGHT, padx=15, pady=15)
    
    theme_icon = ctk.CTkLabel(
        theme_btn,
        text="",
        font=ctk.CTkFont(size=20),
        text_color="#ffe680"
    )
    theme_icon.pack(side=tk.LEFT, padx=(15, 5))
    
    theme_label = ctk.CTkLabel(
        theme_btn,
        text="Dark Mode",
        font=ctk.CTkFont(size=14),
        text_color="#ffe680"
    )
    theme_label.pack(side=tk.LEFT, padx=(0, 15))
    
    def theme_button_click(event):
        is_dark_mode.set(not is_dark_mode.get())
        animate_theme_transition(is_dark_mode.get(), not is_dark_mode.get())
        toggle_theme()
    
    theme_btn.bind("<Button-1>", theme_button_click)
    theme_icon.bind("<Button-1>", theme_button_click)
    theme_label.bind("<Button-1>", theme_button_click)
    
    def show_help():
        help_window = ctk.CTkToplevel(root)
        help_window.title("Help & About")
        help_window.geometry("1600x800")
        help_window.grab_set()
        
        help_frame = ctk.CTkFrame(help_window)
        help_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        help_title = ctk.CTkLabel(
            help_frame, 
            text="Sea Level Data Processor V2.0 - Help",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        help_title.pack(pady=(0, 10))
        
        help_text = ctk.CTkTextbox(help_frame, width=560, height=380)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
        Sea Level Data Processor V2.0
        
        This application processes sea level data files from "SEA LEVEL STATION MONITORING FACILITY" website and identifies missing gaps as well as segmenting each file with continuous measurements.
        
        - How to use :
        
        1. Click 'Browse' to select your input data file (text file)

        IMPORTANT! : Make sure the text file doesn't have a title at the start and only contain two columns (Date | Sea Level)

        2. Select an output directory for the processed segments
        3. Click 'Begin Treatment' to start processing
        
        - Features :
        
        - Interpolates missing data points using Monte Carlo simulation
        - Identifies segments with continuous measurements
        - Exports segments as separate Excel files
        - Provides detailed processing status
        
        - Credits :
        
        - Made By : Nassim Mechat
        - Original Idea : Mouad Hebik
        - GUI : Enhanced by Claude AI
        
        Version: 2.0
        © M1 GMIC USTHB 2024/2025
        """
        
        help_text.insert("1.0", help_content)
        help_text.configure(state="disabled")
        
        close_btn = ctk.CTkButton(
            help_frame,
            text="Close",
            command=help_window.destroy,
            width=100
        )
        close_btn.pack(pady=10)
    
    help_btn = ctk.CTkButton(
        top_frame,
        text="Help",
        font=ctk.CTkFont(size=20),
        width=40,
        height=40,
        corner_radius=20,
        fg_color=ACCENT_COLOR,
        hover_color="#555555",
        command=show_help
    )
    help_btn.pack(side=tk.RIGHT, padx=5, pady=15)
    
    # Create main content area
    content_frame = ctk.CTkFrame(main_frame)
    content_frame.pack(fill=tk.BOTH, expand=True)
    
    # File selection container with glass effect
    selection_frame = ctk.CTkFrame(content_frame, corner_radius=15)
    selection_frame.pack(fill=tk.X, pady=(0, 20), padx=10)
    
    # Section title for file selection
    section_title = ctk.CTkLabel(
        selection_frame, 
        text="Data File Configuration",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    section_title.pack(fill=tk.X, padx=15, pady=(15, 10))
    
    # Separator
    separator = ctk.CTkFrame(selection_frame, height=1, fg_color=ACCENT_COLOR)
    separator.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    # Input file selection with icon
    input_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
    input_frame.pack(fill=tk.X, padx=15, pady=(5, 5))
    
    input_label = ctk.CTkLabel(
        input_frame, 
        text="Input File:", 
        font=ctk.CTkFont(size=14, weight="bold"),
        width=120,
        anchor="w"
    )
    input_label.pack(side=tk.LEFT, padx=(5, 10))
    
    input_entry = ctk.CTkEntry(
        input_frame, 
        textvariable=input_path, 
        height=38,
        placeholder_text="Select input data file (.txt)"
    )
    input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    def browse_input():
        filename = filedialog.askopenfilename(
            title="Select Input File", 
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            input_path.set(filename)
            status_box.insert(tk.END, f"Input file selected: {filename}\n", "info")
            status_box.see(tk.END)
    
    input_button = ctk.CTkButton(
        input_frame, 
        text="Browse", 
        width=100, 
        height=38, 
        command=browse_input,
        fg_color=ACCENT_COLOR
    )
    input_button.pack(side=tk.RIGHT)
    
    # Output directory selection
    output_frame = ctk.CTkFrame(selection_frame, fg_color="transparent")
    output_frame.pack(fill=tk.X, padx=15, pady=(5, 15))
    
    output_label = ctk.CTkLabel(
        output_frame, 
        text="Output Directory:", 
        font=ctk.CTkFont(size=14, weight="bold"),
        width=120,
        anchor="w"
    )
    output_label.pack(side=tk.LEFT, padx=(5, 10))
    
    output_entry = ctk.CTkEntry(
        output_frame, 
        textvariable=output_path, 
        height=38,
        placeholder_text="Select destination folder for processed files"
    )
    output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
    def browse_output():
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            output_path.set(directory)
            status_box.insert(tk.END, f"Output directory selected: {directory}\n", "info")
            status_box.see(tk.END)
    
    output_button = ctk.CTkButton(
        output_frame, 
        text="Browse", 
        width=100, 
        height=38, 
        command=browse_output,
        fg_color=ACCENT_COLOR
    )
    output_button.pack(side=tk.RIGHT)
    
    # Status and output section
    status_frame = ctk.CTkFrame(content_frame, corner_radius=15)
    status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    # Status section title
    status_title = ctk.CTkLabel(
        status_frame,
        text="Processing Status",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    status_title.pack(fill=tk.X, padx=15, pady=(15, 10))
    
    # Separator
    status_separator = ctk.CTkFrame(status_frame, height=1, fg_color=ACCENT_COLOR)
    status_separator.pack(fill=tk.X, padx=15, pady=(0, 10))
    
    # Status box with improved styling
    status_box_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
    status_box_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
    
    # Standard tkinter scrolledtext widget wrapped in CTkFrame
    status_box = scrolledtext.ScrolledText(
        status_box_frame, 
        height=15, 
        font=("Consolas", 10),
        bd=0,
        relief="flat",
        padx=10,
        pady=10
    )
    status_box.pack(fill=tk.BOTH, expand=True)
    
    # Configure text tags for colored output
    status_box.tag_configure("maker", foreground="#6a9eda")
    status_box.tag_configure("info", foreground="#001475")
    status_box.tag_configure("success", foreground="#6bc46b")
    status_box.tag_configure("warning", foreground="#ffc107")
    status_box.tag_configure("error", foreground="#ff5252")
    status_box.tag_configure("complete", foreground="#7fff7f", font=("Consolas", 10, "bold"))
    
    status_box.insert(tk.END, "Ready to start!\n" , "success")
    status_box.insert(tk.END, "Please select the input file and output directory to begin processing \u21D1\n", "info")
    
    # Progress section
    progress_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    progress_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
    
    progress_label = ctk.CTkLabel(progress_frame, text="Ready", width=100, anchor="e")
    progress_label.pack(side=tk.RIGHT, padx=(10, 0))
    
    progress = ctk.CTkProgressBar(progress_frame, height=15, corner_radius=5)
    progress.pack(side=tk.LEFT, fill=tk.X, expand=True)
    progress.set(0)  # Initial state (0%)
    
    # Button frame with improved layout
    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(fill=tk.X, pady=(10, 0), padx=10)
    
    def start_processing():
        in_path = input_path.get()
        out_path = output_path.get()
        
        if not in_path:
            status_box.insert(tk.END, "Error: Please select an input file.\n", "error")
            status_box.see(tk.END)
            return
        
        if not out_path:
            status_box.insert(tk.END, "Error: Please select an output directory.\n", "error")
            status_box.see(tk.END)
            return
        
        # Update UI to show processing state
        start_button.configure(state="disabled")
        progress.set(0)  # Reset progress
        progress_label.configure(text="Starting...")
        
        if not os.path.exists(out_path):
            try:
                os.makedirs(out_path)
                status_box.insert(tk.END, f"Created output directory: {out_path}\n", "info")
                status_box.see(tk.END)
            except Exception as e:
                status_box.insert(tk.END, f"Error creating output directory: {str(e)}\n", "error")
                status_box.see(tk.END)
                progress_label.configure(text="Failed")
                start_button.configure(state="normal")
                return
        
        # Use threading to prevent UI freezing during processing
        processing_thread = threading.Thread(
            target=process_sea_level_data,
            args=(in_path, out_path, status_box, progress, progress_label, start_button)
        )
        processing_thread.daemon = True
        processing_thread.start()
    
    # Create a stylish Start button with pulsating animation
    start_button = ctk.CTkButton(
        button_frame, 
        text="Begin Treatment", 
        font=ctk.CTkFont(size=15, weight="bold"),
        height=45,
        corner_radius=10,
        command=start_processing,
        fg_color=SUCCESS_COLOR,
        hover_color="#1e6e46"
    )
    start_button.pack(side=tk.LEFT, padx=5)
    
    # Clear log button
    def clear_log():
        status_box.delete(1.0, tk.END)
        status_box.insert(tk.END, "█▓▒░ Sea Level Data Processor ░▒▓█\n\n", "maker")
        status_box.insert(tk.END, "Made By Nassim Mechat - Original Idea By Mouad Hebik - GUI Enhanced By Claude AI\n\n", "maker")
        status_box.insert(tk.END, "Log cleared.\n", "info")
    
    clear_button = ctk.CTkButton(
        button_frame, 
        text="Clear Log", 
        font=ctk.CTkFont(size=15),
        height=45,
        corner_radius=10,
        command=clear_log,
        fg_color="#555555",
        hover_color="#444444"
    )
    clear_button.pack(side=tk.LEFT, padx=5)
    
    # Exit button
    exit_button = ctk.CTkButton(
        button_frame, 
        text="Exit", 
        font=ctk.CTkFont(size=15),
        height=45,
        corner_radius=10,
        command=root.destroy,
        fg_color=ERROR_COLOR,
        hover_color="#8b0000"
    )
    exit_button.pack(side=tk.RIGHT, padx=5)
    
    # Footer with version info
    footer_frame = ctk.CTkFrame(root, fg_color="transparent", height=30)
    footer_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
    
    version_footer = ctk.CTkLabel(
        footer_frame, 
        text="M1 GMIC USTHB 2024/2025", 
        font=ctk.CTkFont(size=14),
        text_color="#888888"
    )
    version_footer.pack(side=tk.RIGHT)
    
    # Initialize the theme (should be dark mode by default)
    toggle_theme()
    
    # Start pulsating animation for start button
    def pulse_button():
        colors = [SUCCESS_COLOR, "#38a169", "#2e8b57", "#38a169"]
        i = 0
        
        def update_color():
            nonlocal i
            if start_button.cget("state") == "normal":
                start_button.configure(fg_color=colors[i % len(colors)])
                i += 1
                root.after(800, update_color)
            else:
                start_button.configure(fg_color=SUCCESS_COLOR)
                i = 0
        
        update_color()
    
    # Start the pulsating effect
    pulse_button()
    
    # Center the window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    root.mainloop()

# Run the application
if __name__ == "__main__":
    create_gui()