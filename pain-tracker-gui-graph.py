import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class PainTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Pain Tracker")
        master.geometry("850x900")  # Increased width to accommodate new column

        self.pain0 = tk.IntVar()
        self.current_pain = tk.IntVar()
        self.time_point = 0
        self.target_pain_score = 0
        self.pain_table = []
        self.use_minutes = tk.BooleanVar(value=True)
        self.show_actual_pain = tk.BooleanVar(value=True)
        self.show_comments = tk.BooleanVar(value=True)
        self.custom_time = tk.IntVar(value=30)

        self.create_widgets()
        self.create_graph()

    def create_widgets(self):
        # Main frame to hold all widgets
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Pain score entry frame
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
        self.custom_time_entry.config(state='normal')
        ttk.Button(pain_frame, text="Add", command=self.add_pain_score).grid(row=1, column=4, padx=5, pady=5)

        # Options frame
        time_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        time_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Checkbutton(time_frame, text="Use Minutes (triggers restart)", variable=self.use_minutes, command=self.toggle_time_display).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(time_frame, text="Show Actual Pain Scores on Graph", variable=self.show_actual_pain, command=self.update_graph).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(time_frame, text="Show Comments", variable=self.show_comments, command=self.update_graph).grid(row=0, column=2, padx=5, pady=5, sticky="w")

        # Table frame
        table_frame = ttk.Frame(main_frame)
        table_frame.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.tree = ttk.Treeview(table_frame, columns=("Time", "Pain Score", "Reduction", "Comment"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Pain Score", text="Pain Score")
        self.tree.heading("Reduction", text="Reduction Percentage")
        self.tree.heading("Comment", text="Comment")
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, padx=5, pady=5, sticky="ew")
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).grid(row=0, column=0, padx=5, pady=15)
        ttk.Button(button_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).grid(row=0, column=1, padx=5, pady=15)
        ttk.Button(button_frame, text="Add Comment", command=self.add_comment).grid(row=0, column=2, padx=15, pady=5)
        ttk.Button(button_frame, text="Restart", command=self.restart).grid(row=0, column=3, padx=5, pady=15)
        ttk.Button(button_frame, text="Quit", command=self.master.quit).grid(row=0, column=4, padx=5, pady=15)

        # Configure grid weights
        for i in range(4):
            main_frame.columnconfigure(i, weight=1)
        for i in range(4):
            main_frame.rowconfigure(i, weight=1)

    def create_graph(self):
        self.figure = Figure(figsize=(7, 4), dpi=100)
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
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=5, padx=5, pady=5)

    def update_graph(self):
        if self.use_minutes.get():
            time_points = [int(self.tree.item(child)["values"][0].split()[0]) for child in self.tree.get_children()]
        else:
            time_points = [int(self.tree.item(child)["values"][0].split()[1]) for child in self.tree.get_children()]

        pain_scores = [int(self.tree.item(child)["values"][1]) for child in self.tree.get_children()]
        comments = [self.tree.item(child)["values"][3] for child in self.tree.get_children()]

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
            
            # Display pain scores on the graph if the toggle is on
            if self.show_actual_pain.get():
                for i, (x, y) in enumerate(zip(time_points, pain_scores)):
                    self.ax.text(x, y + 2, f"{y}", ha='center', va='bottom', fontsize=9)

            # Only show comments if the toggle is on
            if self.show_comments.get():
                for i, (x, y, comment) in enumerate(zip(time_points, pain_scores, comments)):
                    if comment:
                        self.ax.annotate(comment, (x, y), xytext=(0, 20), textcoords="offset points", ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="b", lw=1, alpha=0.8))
        else:
            self.ax.set_xlim(0, 1)
            self.ax.text(0.5, 50, "No data yet", ha='center', va='center')
        
        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time" if not self.use_minutes.get() else "Minutes")
        self.ax.set_ylabel("Pain Score")
        self.canvas.draw()

    def get_time_value(self, time_point):
        return time_point

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
        self.restart()
        self.update_time_display()
        self.update_graph()

    def update_time_display(self):
        for index, item in enumerate(self.tree.get_children()):
            values = self.tree.item(item)['values']
            new_time = self.get_time_display(int(values[0].split()[0] if self.use_minutes.get() else values[0].split()[1]))
            new_values = (new_time, values[1], values[2], values[3])
            self.tree.item(item, values=new_values)

    def start_tracking(self):
        try:
            initial_pain = self.pain0.get()
            if 0 <= initial_pain <= 100:
                self.target_pain_score = initial_pain * 20 // 100
                self.tree.delete(*self.tree.get_children())
                initial_time = self.get_time_display(0)
                self.tree.insert("", "end", values=(initial_time, f"{initial_pain:3d}", f"N/A - Target for 80% Reduction: {self.target_pain_score}", ""))
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
                self.tree.insert("", "end", values=(time_display, f"{current_pain:3d}", f"{reduction_percentage}%", ""))
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
            new_values = (new_time, values[1], values[2], values[3])
            self.tree.item(item, values=new_values)
        self.time_point = int(values[0].split()[0])

    def restart(self):
        self.pain0.set(0)
        self.current_pain.set(0)
        self.time_point = 0
        self.target_pain_score = 0
        self.tree.delete(*self.tree.get_children())
        self.update_graph()

    def copy_to_clipboard(self):
        headers = "Time\tPain\tReduction\tComment\n"
        table_data = headers
        for child in self.tree.get_children():
            row = self.tree.item(child)["values"]
            row_data = "\t".join(str(value) for value in row)
            table_data += row_data + "\n"

        self.master.clipboard_clear()
        self.master.clipboard_append(table_data)
        messagebox.showinfo("Copied", "Table data has been copied to clipboard.")

    def add_comment(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showinfo("Info", "Please select a row to add a comment.")
            return

        comment = simpledialog.askstring("Add Comment", "Enter your comment:")
        if comment:
            for item in selected_items:
                values = list(self.tree.item(item)["values"])
                values[3] = comment
                self.tree.item(item, values=values)
        
        self.update_graph()

if __name__ == "__main__":
    root = tk.Tk()
    app = PainTrackerApp(root)
    root.mainloop()
