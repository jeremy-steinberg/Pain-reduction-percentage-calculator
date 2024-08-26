import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PainTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Pain Tracker")
        master.geometry("850x900")
        
        self.master.bind("<Delete>", self.on_delete_key)
        self.pain0 = tk.IntVar()
        self.current_pain = tk.IntVar()
        self.time_point = 0
        self.target_pain_score = 0
        self.use_minutes = tk.BooleanVar(value=True)
        self.show_actual_pain = tk.BooleanVar(value=True)
        self.show_comments = tk.BooleanVar(value=True)
        self.show_80_percent_line = tk.BooleanVar(value=False)
        self.custom_time = tk.IntVar(value=30)

        self.create_widgets()
        self.create_graph()

    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        pain_frame = ttk.LabelFrame(main_frame, text="Pain Score Entry", padding="10")
        pain_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        ttk.Label(pain_frame, text="Starting pain score (0-100):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(pain_frame, textvariable=self.pain0, width=10).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(pain_frame, text="Start", command=self.start_tracking).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(pain_frame, text="Current pain score (0-100):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(pain_frame, textvariable=self.current_pain, width=10).grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(pain_frame, text="Time post last entry:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.custom_time_entry = ttk.Entry(pain_frame, textvariable=self.custom_time, width=10)
        self.custom_time_entry.grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(pain_frame, text="Add", command=self.add_pain_score).grid(row=1, column=4, padx=5, pady=5)

        time_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        time_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        options = [
            ("Use Minutes (triggers restart)", self.use_minutes, self.toggle_time_display),
            ("Show Actual Pain Scores on Graph", self.show_actual_pain, self.update_graph),
            ("Show Comments", self.show_comments, self.update_graph),
            ("Show 80% Reduction Line", self.show_80_percent_line, self.update_graph)  # New option
        ]
        for i, (text, var, cmd) in enumerate(options):
            ttk.Checkbutton(time_frame, text=text, variable=var, command=cmd).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table_frame, columns=("Time", "Pain Score", "Reduction", "Comment"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", self.add_edit_comment)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        buttons = [
            ("Delete Selected", self.delete_selected),
            ("Add/Edit Comment", self.add_edit_comment),
            ("Copy to Clipboard", self.copy_to_clipboard),
            ("Restart", self.restart),
            ("Quit", self.master.quit)
        ]
        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=cmd).grid(row=0, column=i, padx=5, pady=15)

    def create_graph(self):
        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Pain Score")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 1)
        self.ax.set_yticks(np.arange(0, 101, 10))
        self.ax.text(0.5, 50, "No data yet", ha='center', va='center')

        self.canvas = FigureCanvasTkAgg(self.figure, self.master)
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=5, padx=5, pady=5)

    def update_graph(self):
        time_points, pain_scores, comments = self.get_graph_data()
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_yticks(np.arange(0, 101, 10))

        if pain_scores:
            self.ax.plot(time_points, pain_scores, marker='o', linestyle='-', color='blue')
            
            # Check if there's only one data point
            if len(time_points) == 1:
                # Expand the xlim slightly to avoid the singular transformation warning
                self.ax.set_xlim(time_points[0] - 0.5, time_points[0] + 0.5)
            else:
                self.ax.set_xlim(min(time_points), max(time_points))
            
            if self.show_actual_pain.get():
                for x, y in zip(time_points, pain_scores):
                    self.ax.text(x, y + 2, f"{y}", ha='center', va='bottom', fontsize=9)
            if self.show_comments.get():
                for x, y, comment in zip(time_points, pain_scores, comments):
                    if comment:
                        self.ax.annotate(comment, (x, y), xytext=(0, 20), textcoords="offset points", ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="b", lw=1, alpha=0.8))
        
            if self.show_80_percent_line.get():  # Draw the 80% reduction line
                self.ax.axhline(y=self.target_pain_score, color='red', linestyle='--', label='80% Reduction')
                self.ax.legend()

        else:
            self.ax.set_xlim(0, 1)
            self.ax.text(0.5, 50, "No data yet", ha='center', va='center')

        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time" if not self.use_minutes.get() else "Minutes")
        self.ax.set_ylabel("Pain Score")
        self.canvas.draw()

    def get_graph_data(self):
        time_points, pain_scores, comments = [], [], []
        for child in self.tree.get_children():
            item = self.tree.item(child)["values"]
            time_points.append(int(item[0].split()[0] if self.use_minutes.get() else item[0].split()[1]))
            pain_scores.append(int(item[1]))
            comments.append(item[3])
        return time_points, pain_scores, comments

    def toggle_time_display(self):
        self.restart()
        self.update_time_display()

    def update_time_display(self):
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            new_time = self.get_time_display(int(values[0].split()[0] if self.use_minutes.get() else values[0].split()[1]))
            self.tree.item(item, values=(new_time, values[1], values[2], values[3]))

    def get_time_display(self, time_point):
        return f"{time_point} min" if self.use_minutes.get() else f"Time {time_point}"

    def start_tracking(self):
        try:
            initial_pain = self.pain0.get()
            if 0 <= initial_pain <= 100:
                self.target_pain_score = initial_pain * 20 // 100
                self.tree.delete(*self.tree.get_children())
                self.tree.insert("", "end", values=(self.get_time_display(0), f"{initial_pain:3d}", f"N/A - Target for 80% Reduction: {self.target_pain_score}", ""))
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
                self.time_point += self.custom_time.get() if self.use_minutes.get() else 1
                reduction_percentage = ((self.pain0.get() - current_pain) * 100) // self.pain0.get()
                self.tree.insert("", "end", values=(self.get_time_display(self.time_point), f"{current_pain:3d}", f"{reduction_percentage}%", ""))
                self.update_graph()
            else:
                messagebox.showerror("Error", "Pain score must be between 0 and 100.")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter a valid number for the current pain score.")

    def delete_selected(self):
        for item in self.tree.selection():
            self.tree.delete(item)
        self.renumber_time_points()
        self.update_graph()

    def on_delete_key(self, event):
        self.delete_selected()

    def renumber_time_points(self):
        if not self.tree.get_children():
            return  # Exit if there are no items

        # Initialize values to ensure it's defined
        values = None

        for index, item in enumerate(self.tree.get_children()):
            if index == 0:
                continue
            values = self.tree.item(item)['values']
            new_time = self.get_time_display(int(values[0].split()[0] if self.use_minutes.get() else values[0].split()[1]))
            self.tree.item(item, values=(new_time, values[1], values[2], values[3]))

        # Ensure self.time_point is assigned only if there are items
        if values:
            self.time_point = int(values[0].split()[0])
        else:
            self.time_point = 0


    def restart(self):
        self.pain0.set(0)
        self.current_pain.set(0)
        self.time_point = 0
        self.target_pain_score = 0
        self.tree.delete(*self.tree.get_children())
        self.update_graph()

    def copy_to_clipboard(self):
        headers = "Time\tPain\tReduction\tComment\n"
        table_data = headers + "\n".join("\t".join(str(val) for val in self.tree.item(child)["values"]) for child in self.tree.get_children())
        self.master.clipboard_clear()
        self.master.clipboard_append(table_data)
        messagebox.showinfo("Copied", "Table data has been copied to clipboard.")

    def add_edit_comment(self, event=None):
        item = self.tree.selection()[0] if not event else self.tree.identify_row(event.y) if self.tree.identify_column(event.x) == "#4" else None
        if not item:
            messagebox.showinfo("Info", "Please select a row to add/edit a comment.")
            return

        values = self.tree.item(item, "values")
        new_comment = simpledialog.askstring("Add/Edit Comment", "Enter your comment:", initialvalue=values[3])
        if new_comment is not None:
            self.tree.item(item, values=(values[0], values[1], values[2], new_comment))
            self.update_graph()

if __name__ == "__main__":
    root = tk.Tk()
    app = PainTrackerApp(root)
    root.mainloop()
