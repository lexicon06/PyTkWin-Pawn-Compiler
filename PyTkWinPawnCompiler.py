"""

PyTkWin Pawn Compiler is a versatile and user-friendly application designed for Windows environments. 
Developed using Python and Tkinter, this tool serves as an efficient compiler and file manager specifically tailored for SourcePawn scripting. 
The application allows users to seamlessly compile their SourcePawn scripts, sort files by various attributes, and open files directly in Visual Studio Code.

By PabloSan
"""

import os
import subprocess
from tkinter import messagebox, filedialog
import tkinter as tk
from datetime import datetime

class PawnCompilerApp:
    def __init__(self, root):
        """Initialize the main application."""
        self.root = root
        self.root.title("PyTkWin Pawn Compiler Beta v1.0")
        self.root.geometry("800x400")

        # Configuration file to save the directory path
        self.config_file = 'config.txt'
        
        # Load the directory from the config file or use the script's directory by default
        self.directory = self.load_directory() or os.path.dirname(os.path.abspath(__file__))
        self.compiled_directory = os.path.join(self.directory, "compiled")

        # Prompt for directory if not already set
        if not self.directory:
            self.prompt_for_directory()

        # Search functionality
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)

        self.search_entry = tk.Entry(root, textvariable=self.search_var, width=50, font=("Helvetica", 14))
        self.search_entry.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        self.file_listbox = tk.Listbox(root, width=50, font=("Helvetica", 14))
        self.file_listbox.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

        # I have decided to use emojis for the buttons instead of vanilla text for better readability/accessibility
        self.compile_button = tk.Button(root, text="🔧 Compile", font=("Helvetica", 14), command=self.compile_file)
        self.compile_button.grid(row=1, column=3, padx=10, pady=10)

        self.open_vscode_button = tk.Button(root, text="📝 Open with VS Code", font=("Helvetica", 14), command=self.open_with_vscode)
        self.open_vscode_button.grid(row=2, column=3, padx=10, pady=5)

        self.sort_name_button = tk.Button(root, text="🔤 Sort by Name", font=("Helvetica", 14), command=self.sort_by_name)
        self.sort_name_button.grid(row=2, column=0, padx=10, pady=5)

        self.sort_date_button = tk.Button(root, text="📅 Sort by Date", font=("Helvetica", 14), command=self.sort_by_date)
        self.sort_date_button.grid(row=2, column=1, padx=10, pady=5)

        self.sort_size_button = tk.Button(root, text="📏 Sort by Size", font=("Helvetica", 14), command=self.sort_by_size)
        self.sort_size_button.grid(row=2, column=2, padx=10, pady=5)

        self.change_path_button = tk.Button(root, text="📂 Change Path", font=("Helvetica", 14), command=self.change_path)
        self.change_path_button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        # Update the file list
        self.update_files()

    def prompt_for_directory(self):
        """Prompt the user to select the SourcePawn scripting directory."""
        self.directory = filedialog.askdirectory(title="Select Your SourcePawn Scripting Directory")
        if not self.directory:
            self.directory = os.path.dirname(os.path.abspath(__file__))
        self.compiled_directory = os.path.join(self.directory, "compiled")
        self.save_directory()

    def change_path(self):
        """Allow the user to change the SourcePawn scripting directory."""
        self.directory = filedialog.askdirectory(title="Select New SourcePawn Scripting Directory")
        if self.directory:
            self.compiled_directory = os.path.join(self.directory, "compiled")
            self.save_directory()
            self.update_files()

    def save_directory(self):
        """Save the current directory to a config file."""
        with open(self.config_file, 'w') as file:
            file.write(self.directory)

    def load_directory(self):
        """Load the directory path from the config file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as file:
                return file.read().strip()
        return None

    def update_files(self):
        """Update the list of SourcePawn files in the selected directory."""
        self.files = [file for file in os.listdir(self.directory) if file.endswith('.sp')]
        self.sort_by_date()

    def update_list(self, *args):
        """Update the listbox with files matching the search term."""
        search_term = self.search_var.get().lower()
        self.file_listbox.delete(0, tk.END)
        for file in self.files:
            if search_term in file.lower():
                self.file_listbox.insert(tk.END, file)

    def compile_file(self):
        """Compile the selected SourcePawn file."""
        selected_file = self.file_listbox.get(tk.ACTIVE)
        if selected_file:
            compiled_file = os.path.join(self.compiled_directory, selected_file.replace('.sp', '.smx'))
            if os.path.exists(compiled_file):
                #TODO: Complete this feature.
                response = messagebox.askyesno("File Exists", f"The file {compiled_file} already exists. Do you want to override it?")
                if not response:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    new_compiled_file = compiled_file.replace('.smx', f'_old_{timestamp}.smx')
                    os.rename(compiled_file, new_compiled_file)
            try:
                compiler_path = rf"{self.directory}\compiler.exe"
                file_path = os.path.join(self.directory, selected_file)
                subprocess.run([compiler_path, file_path], check=True)
                messagebox.showinfo("Success", f"Compiled {selected_file} successfully!")
                os.startfile(self.compiled_directory)  # Open the compiled folder
            except subprocess.CalledProcessError as e:
                messagebox.showerror("Error", f"Failed to compile {selected_file}.\n{e}")
        else:
            messagebox.showwarning("Warning", "Please select a file to compile.")

    def open_with_vscode(self):
        """Open the selected SourcePawn file with Visual Studio Code."""
        selected_file = self.file_listbox.get(tk.ACTIVE)
        if selected_file:
            file_path = os.path.join(self.directory, selected_file)
            subprocess.run(["code", file_path])
        else:
            messagebox.showwarning("Warning", "Please select a file to open with Visual Studio Code.")

    def sort_by_name(self):
        """Sort the files by name."""
        self.files.sort(key=lambda x: x.lower())
        self.update_list()

    def sort_by_date(self):
        """Sort the files by date."""
        self.files.sort(key=lambda x: os.path.getmtime(os.path.join(self.directory, x)), reverse=True)
        self.update_list()

    def sort_by_size(self):
        """Sort the files by size."""
        self.files.sort(key=lambda x: os.path.getsize(os.path.join(self.directory, x)), reverse=True)
        self.update_list()

if __name__ == "__main__":
    """Hello Pawn!"""
    root = tk.Tk()
    app = PawnCompilerApp(root)
    root.mainloop()
