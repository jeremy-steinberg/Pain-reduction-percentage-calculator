import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PainTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Pain Tracker")
        master.geometry("600x900")  # Increased height to accommodate new widgets

        self.pain0 = tk.IntVar()
        self.current_pain = tk.IntVar()
        self.time_point = 0
        self.target_pain_score = 0
        self.pain_table = []
        self.use_minutes = tk.BooleanVar(value=True)
        self.custom_time = tk.IntVar(value=30)  # Variable to store custom time for each entry

        self.create_widgets()
        self.create_graph()

    def create_widgets(self):
        # Initial pain score entry
        ttk.Label(self.master, text="Enter the starting pain score (0-100):").grid(row=0, column=0, padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.pain0).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Start", command=self.start_tracking).grid(row=0, column=2, padx=5, pady=5)

        # Current pain score entry
        ttk.Label(self.master, text="Enter the current pain score (0-100):").grid(row=1, column=0, padx=5, pady=5)
        ttk.Entry(self.master, textvariable=self.current_pain).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.master, text="Add", command=self.add_pain_score).grid(row=1, column=2, padx=5, pady=5)

        # Time display toggle and custom time entry
        ttk.Checkbutton(self.master, text="Use Minutes", variable=self.use_minutes, command=self.toggle_time_display).grid(row=2, column=0, padx=5, pady=5)
        
        ttk.Label(self.master, text="Custom Time (min):").grid(row=3, column=0, padx=5, pady=5)
        self.custom_time_entry = ttk.Entry(self.master, textvariable=self.custom_time, width=5)
        self.custom_time_entry.grid(row=3, column=1, padx=5, pady=5)
        self.custom_time_entry.config(state='normal')  # Enable by default since use_minutes is True

        # Table
        self.tree = ttk.Treeview(self.master, columns=("Time", "Pain Score", "Reduction"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Pain Score", text="Pain Score")
        self.tree.heading("Reduction", text="Reduction Percentage")
        self.tree.grid(row=4, column=0, columnspan=3, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=4, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons
        ttk.Button(self.master, text="Delete Selected", command=self.delete_selected).grid(row=5, column=0, padx=5, pady=5)
        ttk.Button(self.master, text="Restart", command=self.restart).grid(row=5, column=1, padx=5, pady=5, sticky="w")
        ttk.Button(self.master, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=5, column=2, padx=5, pady=5, sticky="w")
        ttk.Button(self.master, text="Quit", command=self.master.quit).grid(row=6, column=2, padx=5, pady=5, sticky="w")

    def create_graph(self):
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Pain Score")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 1)
        
        y_ticks = np.arange(0, 101, 10)
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels([str(tick) for tick in y_ticks])
        
        self.ax.text(0.5, 50, "No data yet", ha='center', va='center')

        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=4, padx=5, pady=5)

    def update_graph(self):
        if self.use_minutes.get():
            time_points = [int(self.tree.item(child)["values"][0].split()[0]) for child in self.tree.get_children()]
        else:
            time_points = [int(self.tree.item(child)["values"][0].split()[1]) for child in self.tree.get_children()]

        pain_scores = [int(self.tree.item(child)["values"][1]) for child in self.tree.get_children()]

        self.ax.clear()
        self.ax.set_ylim(0, 100)
        
        y_ticks = np.arange(0, 101, 10)
        self.ax.set_yticks(y_ticks)
        self.ax.set_yticklabels([str(tick) for tick in y_ticks])
        
        if pain_scores:
            self.ax.plot(time_points, pain_scores, marker='o', linestyle='-', color='blue')
            if len(time_points) == 1:
                self.ax.set_xlim(-0.5, 0.5)
            else:
                self.ax.set_xlim(0, max(time_points))
            if self.use_minutes.get():
                self.ax.set_xticks(time_points)
                self.ax.set_xticklabels([f"{t}" for t in time_points])
            else:
                self.ax.set_xticks(range(min(time_points), max(time_points) + 1))
        else:
            self.ax.set_xlim(0, 1)
            self.ax.text(0.5, 50, "No data yet", ha='center', va='center')
        
        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time" if not self.use_minutes.get() else "Minutes")
        self.ax.set_ylabel("Pain Score")
        self.canvas.draw()

    def get_time_value(self, time_point):
        return time_point  # Use custom time directly

    def get_time_display(self, time_point):
        if self.use_minutes.get():
            return f"{time_point} min"
        else:
            return f"Time {time_point}"

    def toggle_time_display(self):
        if self.use_minutes.get():
            self.custom_time_entry.config(state='normal')
        else:
            self.custom_time_entry.config(state='disabled')
        self.restart()  # Restart when the checkbox is toggled
        self.update_time_display()
        self.update_graph()


    def update_time_display(self):
        for index, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item)['values']
            new_time = self.get_time_display(int(values[0].split()[0] if self.use_minutes.get() else values[0].split()[1]))
            new_values = (new_time, values[1], values[2])
            self.tree.item(item, values=new_values)

    def start_tracking(self):
        try:
            initial_pain = self.pain0.get()
            if 0 <= initial_pain <= 100:
                self.target_pain_score = initial_pain * 20 // 100
                self.tree.delete(*self.tree.get_children())
                initial_time = self.get_time_display(0)
                self.tree.insert("", "end", values=(initial_time, f"{initial_pain:3d}", f"N/A - Target for 80% Reduction: {self.target_pain_score}"))
                self.time_point = 0
                self.update_graph()
            else:
                messagebox.showerror("Error", "Initial pain score must be between 0 and 100.")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number for the starting pain score.")


    def add_pain_score(self):
        try:
            current_pain = self.current_pain.get()
            if 0 <= current_pain <= 100:
                if self.use_minutes.get():
                    custom_minutes = self.custom_time.get()
                    self.time_point += custom_minutes
                else:
                    self.time_point += 1

                reduction_percentage = ((self.pain0.get() - current_pain) * 100) // self.pain0.get()
                time_display = self.get_time_display(self.time_point)
                self.tree.insert("", "end", values=(time_display, f"{current_pain:3d}", f"{reduction_percentage}%"))
                self.update_graph()
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
        
        self.renumber_time_points()
        self.update_graph()

    def renumber_time_points(self):
        items = self.tree.get_children()
        for index, item in enumerate(items):
            values = self.tree.item(item)['values']
            if index == 0:
                continue
            new_time = self.get_time_display(int(values[0].split()[0] if self.use_minutes.get() else values[0].split()[1]))
            new_values = (new_time, values[1], values[2])
            self.tree.item(item, values=new_values)
        self.time_point = int(values[0].split()[0])  # Update to the last custom time point

    def restart(self):
        self.pain0.set(0)
        self.current_pain.set(0)
        self.time_point = 0
        self.target_pain_score = 0
        self.tree.delete(*self.tree.get_children())
        self.update_graph()

    def copy_to_clipboard(self):
        headers = "Time\tPain\tReduction\n"
        table_data = headers
        for child in self.tree.get_children():
            row = self.tree.item(child)["values"]
            row_data = "\t".join(str(value) for value in row)
            table_data += row_data + "\n"

        self.master.clipboard_clear()
        self.master.clipboard_append(table_data)
        messagebox.showinfo("Copied", "Table data has been copied to clipboard.")

if __name__ == "__main__":
    root = tk.Tk()
    app = PainTrackerApp(root)
    root.mainloop()
