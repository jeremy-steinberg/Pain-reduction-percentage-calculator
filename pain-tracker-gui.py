import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class PainTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Pain Tracker")
        master.geometry("600x400")

        self.pain0 = tk.IntVar()
        self.current_pain = tk.IntVar()
        self.time_point = 0
        self.target_pain_score = 0
        self.pain_table = []

        self.create_widgets()

    def create_widgets(self):
        # Initial pain score entry
        ttk.Label(self.master, text="Enter the starting pain score (0-100):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.pain0).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Start", command=self.start_tracking).grid(row=0, column=2, padx=5, pady=5)

        # Current pain score entry
        ttk.Label(self.master, text="Enter the current pain score (0-100):").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.current_pain).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Add", command=self.add_pain_score).grid(row=1, column=2, padx=5, pady=5)

        # Table
        self.tree = ttk.Treeview(self.master, columns=("Time", "Pain Score", "Reduction"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Pain Score", text="Pain Score")
        self.tree.heading("Reduction", text="Reduction Percentage")
        self.tree.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=2, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        ttk.Button(self.master, text="Delete Selected", command=self.delete_selected).grid(row=3, column=0, padx=5, pady=5)
        ttk.Button(self.master, text="Restart", command=self.restart).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Quit", command=self.master.quit).grid(row=3, column=2, padx=5, pady=5)

    def start_tracking(self):
        try:
            self.pain0.get()
            self.target_pain_score = self.pain0.get() * 20 // 100
            self.tree.delete(*self.tree.get_children())
            self.tree.insert("", "end", values=(f"Time 0", f"{self.pain0.get():3d}", f"N/A - Target for 80% Reduction: {self.target_pain_score}"))
            self.time_point = 0
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number for the starting pain score.")

    def add_pain_score(self):
        try:
            current_pain = self.current_pain.get()
            if 0 <= current_pain <= 100:
                self.time_point += 1
                reduction_percentage = ((self.pain0.get() - current_pain) * 100) // self.pain0.get()
                self.tree.insert("", "end", values=(f"Time {self.time_point}", f"{current_pain:3d}", f"{reduction_percentage}%"))
            else:
                messagebox.showerror("Error", "Pain score must be between 0 and 100.")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number for the current pain score.")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a row to delete.")
            return
        
        for item in selected_items:
            self.tree.delete(item)
        
        # Renumber the time points
        self.renumber_time_points()

    def renumber_time_points(self):
        items = self.tree.get_children()
        for index, item in enumerate(items):
            values = self.tree.item(item)['values']
            if index == 0:
                # Keep the initial row as is
                continue
            new_values = (f"Time {index}", values[1], values[2])
            self.tree.item(item, values=new_values)
        self.time_point = len(items) - 1

    def restart(self):
        self.pain0.set(0)
        self.current_pain.set(0)
        self.time_point = 0
        self.target_pain_score = 0
        self.tree.delete(*self.tree.get_children())

if __name__ == "__main__":
    root = tk.Tk()
    app = PainTrackerApp(root)
    root.mainloop()
