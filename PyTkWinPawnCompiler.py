"""
PyTkWin Pawn Compiler v2.0 - 02/07/2026
Made by Pablo Santillan
Updated with modern UI, integrated console, and improved compilation handling


PyTkWin Pawn Compiler is a versatile and user-friendly application designed for Windows environments. 
Developed using Python and Tkinter, this tool serves as an efficient compiler and file manager specifically tailored for SourcePawn scripting. 
The application allows users to seamlessly compile their SourcePawn scripts with real-time output feedback, 
sort files by various attributes, and open files directly in Visual Studio Code.
"""

import os
import subprocess
from tkinter import messagebox, filedialog, ttk, scrolledtext
import tkinter as tk
from datetime import datetime
import threading

class PawnCompilerApp:
    def __init__(self, root):
        """Initialize the main application."""
        self.root = root
        self.root.title("Pawn Compiler v2.0 @ PyTkWin")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Configure modern style
        self.style = ttk.Style(root)
        self.style.theme_use('clam')
        
        # Modern color scheme
        bg_color = "#1e1e1e"
        fg_color = "#ffffff"
        accent_color = "#007acc"
        secondary_bg = "#2d2d30"
        
        self.root.configure(bg=bg_color)
        
        # Configure styles
        self.style.configure('TFrame', background=bg_color)
        self.style.configure('TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 10))
        self.style.configure('Title.TLabel', background=bg_color, foreground=fg_color, font=('Segoe UI', 16, 'bold'))
        self.style.configure('TButton', font=('Segoe UI', 10), padding=8)
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), padding=10)
        self.style.map('TButton',
                      background=[('active', accent_color)],
                      foreground=[('active', fg_color)])
        
        # Configuration file to save the directory path
        self.config_file = 'config.txt'
        
        # Load the directory from the config file or use the script's directory by default
        self.directory = self.load_directory() or os.path.dirname(os.path.abspath(__file__))
        self.compiled_directory = os.path.join(self.directory, "compiled")

        # Prompt for directory if not already set
        if not self.directory or not os.path.exists(self.directory):
            self.prompt_for_directory()

        # Create UI
        self.create_ui()
        
        # Update the file list
        self.update_files()

    def create_ui(self):
        """Create the modern UI layout."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="🔧 SourcePawn Compiler", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        path_label = ttk.Label(header_frame, text=f"📂 Directory: {self.directory}", style='TLabel')
        path_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.path_label = path_label
        
        # Search section
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        search_label = ttk.Label(search_frame, text="🔍 Search:")
        search_label.grid(row=0, column=0, padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11))
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # File list section
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Create listbox with scrollbar
        list_scroll = tk.Scrollbar(list_frame)
        list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.file_listbox = tk.Listbox(
            list_frame, 
            font=("Consolas", 11),
            bg="#252526",
            fg="#ffffff",
            selectbackground="#007acc",
            selectforeground="#ffffff",
            yscrollcommand=list_scroll.set,
            highlightthickness=0,
            borderwidth=0
        )
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        list_scroll.config(command=self.file_listbox.yview)
        
        # Bind double-click to compile
        self.file_listbox.bind('<Double-Button-1>', lambda e: self.compile_file())
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.compile_button = ttk.Button(button_frame, text="🔧 Compile", command=self.compile_file, style='Accent.TButton')
        self.compile_button.grid(row=0, column=0, padx=5)
        
        self.open_vscode_button = ttk.Button(button_frame, text="📝 Open in VS Code", command=self.open_with_vscode)
        self.open_vscode_button.grid(row=0, column=1, padx=5)
        
        self.sort_name_button = ttk.Button(button_frame, text="🔤 Name", command=self.sort_by_name)
        self.sort_name_button.grid(row=0, column=2, padx=5)
        
        self.sort_date_button = ttk.Button(button_frame, text="📅 Date", command=self.sort_by_date)
        self.sort_date_button.grid(row=0, column=3, padx=5)
        
        self.sort_size_button = ttk.Button(button_frame, text="📏 Size", command=self.sort_by_size)
        self.sort_size_button.grid(row=0, column=4, padx=5)
        
        self.refresh_button = ttk.Button(button_frame, text="🔄 Refresh", command=self.refresh_files)
        self.refresh_button.grid(row=0, column=5, padx=5)
        
        self.change_path_button = ttk.Button(button_frame, text="📂 Change Path", command=self.change_path)
        self.change_path_button.grid(row=0, column=6, padx=5)
        
        # Console section
        console_label = ttk.Label(main_frame, text="📟 Compilation Output:", style='TLabel')
        console_label.grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        
        console_frame = ttk.Frame(main_frame)
        console_frame.grid(row=5, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        self.console = scrolledtext.ScrolledText(
            console_frame,
            font=("Consolas", 9),
            bg="#1e1e1e",
            fg="#cccccc",
            insertbackground="#ffffff",
            wrap=tk.WORD,
            height=10
        )
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure console tags for colored output
        self.console.tag_config("error", foreground="#f48771")
        self.console.tag_config("warning", foreground="#dcdcaa")
        self.console.tag_config("success", foreground="#4ec9b0")
        self.console.tag_config("info", foreground="#569cd6")
        
        # Console control buttons
        console_button_frame = ttk.Frame(main_frame)
        console_button_frame.grid(row=6, column=0, sticky=tk.W, pady=(5, 0))
        
        self.clear_console_button = ttk.Button(console_button_frame, text="🗑️ Clear Console", command=self.clear_console)
        self.clear_console_button.grid(row=0, column=0, padx=5)
        
        # Initial console message
        self.log_info("PyTkWin Pawn Compiler v2.0 - Ready")
        self.log_info(f"Working directory: {self.directory}\n")

    def log_message(self, message, tag=None):
        """Log a message to the console."""
        self.console.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        if tag:
            self.console.insert(tk.END, f"[{timestamp}] ", "info")
            self.console.insert(tk.END, f"{message}\n", tag)
        else:
            self.console.insert(tk.END, f"[{timestamp}] {message}\n")
        self.console.see(tk.END)
        self.console.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def log_info(self, message):
        """Log an info message."""
        self.log_message(message, "info")

    def log_success(self, message):
        """Log a success message."""
        self.log_message(message, "success")

    def log_warning(self, message):
        """Log a warning message."""
        self.log_message(message, "warning")

    def log_error(self, message):
        """Log an error message."""
        self.log_message(message, "error")

    def clear_console(self):
        """Clear the console."""
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)

    def prompt_for_directory(self):
        """Prompt the user to select the SourcePawn scripting directory."""
        self.directory = filedialog.askdirectory(title="Select Your SourcePawn Scripting Directory")
        if not self.directory:
            self.directory = os.path.dirname(os.path.abspath(__file__))
        self.compiled_directory = os.path.join(self.directory, "compiled")
        
        # Ensure compiled directory exists
        if not os.path.exists(self.compiled_directory):
            os.makedirs(self.compiled_directory)
        
        self.save_directory()

    def change_path(self):
        """Allow the user to change the SourcePawn scripting directory."""
        new_directory = filedialog.askdirectory(title="Select New SourcePawn Scripting Directory")
        if new_directory:
            self.directory = new_directory
            self.compiled_directory = os.path.join(self.directory, "compiled")
            
            # Ensure compiled directory exists
            if not os.path.exists(self.compiled_directory):
                os.makedirs(self.compiled_directory)
            
            self.save_directory()
            self.path_label.config(text=f"📂 Directory: {self.directory}")
            self.update_files()
            self.log_info(f"Changed directory to: {self.directory}")

    def save_directory(self):
        """Save the current directory to a config file."""
        try:
            with open(self.config_file, 'w') as file:
                file.write(self.directory)
        except Exception as e:
            self.log_error(f"Failed to save directory config: {e}")

    def load_directory(self):
        """Load the directory path from the config file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as file:
                    return file.read().strip()
            except Exception as e:
                self.log_error(f"Failed to load directory config: {e}")
        return None

    def update_files(self):
        """Update the list of SourcePawn files in the selected directory."""
        try:
            self.files = [file for file in os.listdir(self.directory) if file.endswith('.sp')]
            self.sort_by_date()
            self.log_info(f"Found {len(self.files)} .sp file(s)")
        except Exception as e:
            self.log_error(f"Failed to update file list: {e}")
            self.files = []

    def update_list(self, *args):
        """Update the listbox with files matching the search term."""
        search_term = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)
        
        displayed_count = 0
        for file in self.files:
            if search_term in file.lower():
                self.file_listbox.insert(tk.END, file)
                displayed_count += 1
        
        if displayed_count == 0 and search_term:
            self.file_listbox.insert(tk.END, "No files found...")

    def compile_file(self, event=None):
        """Compile the selected SourcePawn file."""
        selection = self.file_listbox.curselection()
        if not selection:
            self.log_warning("Please select a file to compile")
            messagebox.showwarning("Warning", "Please select a file to compile.")
            return
        
        selected_file = self.file_listbox.get(selection[0])
        if selected_file == "No files found...":
            return
        
        # Check if already compiling
        if self.compile_button['state'] == 'disabled':
            self.log_warning("Compilation already in progress, please wait...")
            return
            
        self.log_info(f"Starting compilation of: {selected_file}")
        self.log_info("-" * 60)
        
        # Disable compile button during compilation
        self.compile_button.config(state='disabled')
        self.root.update_idletasks()
        
        # Run compilation in a separate thread
        thread = threading.Thread(target=self._compile_thread, args=(selected_file,))
        thread.daemon = True
        thread.start()

    def _compile_thread(self, selected_file):
        """Thread function to handle compilation."""
        try:
            compiled_file = os.path.join(self.compiled_directory, selected_file.replace('.sp', '.smx'))
            
            # Check if compiled file already exists
            if os.path.exists(compiled_file):
                self.log_warning(f"Compiled file already exists: {os.path.basename(compiled_file)}")
                
                # Create backup with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = compiled_file.replace('.smx', f'_backup_{timestamp}.smx')
                try:
                    os.rename(compiled_file, backup_file)
                    self.log_info(f"Created backup: {os.path.basename(backup_file)}")
                except Exception as e:
                    self.log_error(f"Failed to create backup: {e}")
            
            # Prepare compilation command
            compiler_path = os.path.join(self.directory, "compiler.exe")
            if not os.path.exists(compiler_path):
                self.log_error(f"Compiler not found at: {compiler_path}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Compiler not found at:\n{compiler_path}"))
                self.root.after(0, lambda: self.compile_button.config(state=tk.NORMAL))
                return
            
            file_path = os.path.join(self.directory, selected_file)
            
            self.log_info("Running compiler...")
            
            # Run the compiler and capture output with proper Windows settings
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            process = subprocess.Popen(
                [compiler_path, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Redirect stderr to stdout
                stdin=subprocess.PIPE,
                text=True,
                cwd=self.directory,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Close stdin immediately so compiler doesn't wait for Enter key
            process.stdin.close()
            
            # Read output line by line in real-time
            output_lines = []
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.rstrip()
                    output_lines.append(line)
                    if 'error' in line.lower() and 'error' not in line.lower().split(':')[0]:
                        self.log_error(line)
                    elif 'warning' in line.lower():
                        self.log_warning(line)
                    else:
                        self.log_message(line)
            
            # Get the return code
            result_returncode = process.poll()
            
            # If no output was captured, log that
            if not output_lines:
                self.log_warning("No output received from compiler")
            
            # Check compilation result
            if result_returncode == 0 and os.path.exists(compiled_file):
                self.log_info("-" * 60)
                self.log_success(f"✓ Successfully compiled: {selected_file}")
                self.log_success(f"✓ Output: {compiled_file}")
                self.log_info("-" * 60 + "\n")
                
                # Show success message and open compiled folder
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Compiled {selected_file} successfully!"))
                try:
                    os.startfile(self.compiled_directory)
                except Exception as e:
                    self.log_warning(f"Could not open compiled directory: {e}")
            else:
                self.log_info("-" * 60)
                self.log_error(f"✗ Compilation failed for: {selected_file}")
                self.log_error(f"✗ Return code: {result_returncode}")
                if not os.path.exists(compiled_file):
                    self.log_error(f"✗ Output file not created: {compiled_file}")
                self.log_info("-" * 60 + "\n")
                
                self.root.after(0, lambda: messagebox.showerror(
                    "Compilation Failed", 
                    f"Failed to compile {selected_file}.\n\nCheck the console output for details.\nReturn code: {result_returncode}"
                ))
        
        except Exception as e:
            self.log_error(f"Exception during compilation: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred:\n{str(e)}"))
        
        finally:
            # Re-enable compile button - this will ALWAYS execute
            self.root.after(0, self._enable_compile_button)
    
    def _enable_compile_button(self):
        """Re-enable the compile button."""
        self.compile_button.config(state='normal')
        self.root.update_idletasks()

    def open_with_vscode(self):
        """Open the selected SourcePawn file with Visual Studio Code."""
        selection = self.file_listbox.curselection()
        if not selection:
            self.log_warning("Please select a file to open")
            messagebox.showwarning("Warning", "Please select a file to open with Visual Studio Code.")
            return
        
        selected_file = self.file_listbox.get(selection[0])
        if selected_file == "No files found...":
            return
        
        file_path = os.path.join(self.directory, selected_file)
        try:
            subprocess.run(["code", file_path], check=True)
            self.log_info(f"Opened in VS Code: {selected_file}")
        except subprocess.CalledProcessError:
            self.log_error("VS Code not found or failed to open")
            messagebox.showerror("Error", "Failed to open VS Code.\n\nMake sure VS Code is installed and 'code' command is in PATH.")
        except Exception as e:
            self.log_error(f"Failed to open VS Code: {e}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

    def sort_by_name(self):
        """Sort the files by name."""
        self.files.sort(key=lambda x: x.lower())
        self.update_list()
        self.log_info("Sorted by name")

    def sort_by_date(self):
        """Sort the files by date (most recent first)."""
        self.files.sort(key=lambda x: os.path.getmtime(os.path.join(self.directory, x)), reverse=True)
        self.update_list()
        self.log_info("Sorted by date (newest first)")

    def sort_by_size(self):
        """Sort the files by size (largest first)."""
        self.files.sort(key=lambda x: os.path.getsize(os.path.join(self.directory, x)), reverse=True)
        self.update_list()
        self.log_info("Sorted by size (largest first)")

    def refresh_files(self):
        """Refresh the list of files in the directory."""
        self.log_info("Refreshing file list...")
        self.update_files()
        self.update_list()

if __name__ == "__main__":
    """Hello Pawn! v2.0"""
    root = tk.Tk()
    app = PawnCompilerApp(root)
    
    # Try to set icon if compiler.exe exists
    try:
        icon_path = os.path.join(app.directory, "compiler.exe")
        if os.path.exists(icon_path):
            root.iconbitmap(icon_path)
    except:
        pass
    
    root.mainloop()
