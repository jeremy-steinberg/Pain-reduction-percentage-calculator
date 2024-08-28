import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph
import numpy as np

class PainTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Pain Tracker")
        master.geometry("1650x750")

        self.track_two_areas = tk.BooleanVar(value=False)
        self.master.bind("<Delete>", self.on_delete_key)
        self.pain0_1 = tk.IntVar()
        self.current_pain_1 = tk.IntVar()
        self.pain0_2 = tk.IntVar()
        self.current_pain_2 = tk.IntVar()
        self.time_point = 0
        self.target_pain_score_1 = 0
        self.target_pain_score_2 = 0
        self.use_minutes = tk.BooleanVar(value=True)
        self.show_actual_pain = tk.BooleanVar(value=True)
        self.show_comments = tk.BooleanVar(value=True)
        self.show_80_percent_line = tk.BooleanVar(value=False)
        self.custom_time = tk.IntVar(value=30)

        # Patient details variables
        self.patient_name = tk.StringVar()
        self.patient_nhi = tk.StringVar()
        self.procedure_date = tk.StringVar()
        self.procedure_name = tk.StringVar()
        self.pain_area_1 = tk.StringVar(value="Area 1")
        self.pain_area_2 = tk.StringVar(value="Area 2")

        self.create_widgets()


    def create_widgets(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Left side frame for controls and table
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(5, weight=1)  # Make the table expandable

        # Pain Score Entry
        pain_frame = ttk.LabelFrame(left_frame, text="Pain Score Entry", padding="10")
        pain_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Checkbutton(pain_frame, text="Track Two Pain Areas", variable=self.track_two_areas, command=self.toggle_second_area).grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky="w")

        ttk.Label(pain_frame, text="Area 1:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.pain_area_1_entry = ttk.Entry(pain_frame, textvariable=self.pain_area_1, width=10)
        self.pain_area_1_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(pain_frame, text="Starting pain (0-100):").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.pain0_1_entry = ttk.Entry(pain_frame, textvariable=self.pain0_1, width=10)
        self.pain0_1_entry.grid(row=1, column=3, padx=5, pady=5)
        ttk.Label(pain_frame, text="Current pain (0-100):").grid(row=1, column=4, padx=5, pady=5, sticky="e")
        self.current_pain_1_entry = ttk.Entry(pain_frame, textvariable=self.current_pain_1, width=10)
        self.current_pain_1_entry.grid(row=1, column=5, padx=5, pady=5)

        self.area2_widgets = []
        ttk.Label(pain_frame, text="Area 2:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.pain_area_2_entry = ttk.Entry(pain_frame, textvariable=self.pain_area_2, width=10)
        self.pain_area_2_entry.grid(row=2, column=1, padx=5, pady=5)
        self.area2_widgets.append(self.pain_area_2_entry)
        ttk.Label(pain_frame, text="Starting pain (0-100):").grid(row=2, column=2, padx=5, pady=5, sticky="e")
        self.pain0_2_entry = ttk.Entry(pain_frame, textvariable=self.pain0_2, width=10)
        self.pain0_2_entry.grid(row=2, column=3, padx=5, pady=5)
        self.area2_widgets.append(self.pain0_2_entry)
        ttk.Label(pain_frame, text="Current pain (0-100):").grid(row=2, column=4, padx=5, pady=5, sticky="e")
        self.current_pain_2_entry = ttk.Entry(pain_frame, textvariable=self.current_pain_2, width=10)
        self.current_pain_2_entry.grid(row=2, column=5, padx=5, pady=5)
        self.area2_widgets.append(self.current_pain_2_entry)


        ttk.Label(pain_frame, text="Time post last entry:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.custom_time_entry = ttk.Entry(pain_frame, textvariable=self.custom_time, width=10)
        self.custom_time_entry.grid(row=3, column=1, padx=5, pady=5)
        self.start_button = ttk.Button(pain_frame, text="Start", command=self.start_tracking)
        self.start_button.grid(row=3, column=2, padx=5, pady=5)
        ttk.Button(pain_frame, text="Add", command=self.add_pain_score).grid(row=3, column=3, padx=5, pady=5)

        self.toggle_second_area()  # Initially hide Area 2 widgets

        self.current_pain_1_entry.config(state="disabled")
        self.current_pain_2_entry.config(state="disabled")
        self.custom_time_entry.config(state="disabled")

        # Options Frame
        time_frame = ttk.LabelFrame(left_frame, text="Options", padding="10")
        time_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        options = [
            ("Use Minutes (triggers restart)", self.use_minutes, self.toggle_time_display),
            ("Show Actual Pain Scores on Graph", self.show_actual_pain, self.update_graph),
            ("Show Comments", self.show_comments, self.update_graph),
            ("Show 80% Reduction Line", self.show_80_percent_line, self.update_graph)  # New option
        ]
        for i, (text, var, cmd) in enumerate(options):
            ttk.Checkbutton(time_frame, text=text, variable=var, command=cmd).grid(row=0, column=i, padx=5, pady=5, sticky="w")

        # Patient details section
        patient_frame = ttk.LabelFrame(left_frame, text="Patient Details", padding="10")
        patient_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        # First row
        ttk.Label(patient_frame, text="Patient Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(patient_frame, textvariable=self.patient_name, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(patient_frame, text="Patient NHI:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(patient_frame, textvariable=self.patient_nhi, width=20).grid(row=0, column=3, padx=5, pady=5, sticky="w")

        # Second row
        ttk.Label(patient_frame, text="Procedure Date (DD-MM-YYYY):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Entry(patient_frame, textvariable=self.procedure_date, width=30).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(patient_frame, text="Procedure Name:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        ttk.Entry(patient_frame, textvariable=self.procedure_name, width=20).grid(row=1, column=3, padx=5, pady=5, sticky="w")

        # Table
        table_frame = ttk.Frame(left_frame)
        table_frame.grid(row=3, column=0, padx=2, pady=0, sticky="nsew")
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=("Time", "Pain Score 1", "Reduction 1", "Pain Score 2", "Reduction 2", "Comment"), show="headings", height=15)
        
        # Setting specific widths for each column
        column_widths = {
            "Time": 80,
            "Pain Score 1": 80,
            "Reduction 1": 200,
            "Pain Score 2": 80,
            "Reduction 2": 200,
            "Comment": 180,
        }
        for col, width in column_widths.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, stretch=tk.YES)  # Fixed width and prevent stretching

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind("<Double-1>", self.add_edit_comment)

        # Buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=4, column=0, padx=2, pady=0, sticky="ew")
        buttons = [
            ("Delete Selected", self.delete_selected),
            ("Add/Edit Comment", self.add_edit_comment),
            ("Copy to Clipboard", self.copy_to_clipboard),
            ("Export to PDF", self.export_to_pdf),
            ("Restart", self.restart),
            ("Quit", self.master.quit)
        ]
        for i, (text, cmd) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=cmd).grid(row=0, column=i, padx=5, pady=5, sticky="ew")

        # Right side frame for graph
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.create_graph(right_frame)

    def toggle_second_area(self):
        if self.track_two_areas.get():
            for widget in self.area2_widgets:
                widget.grid()
        else:
            for widget in self.area2_widgets:
                widget.grid_remove()
        
        # Only restart if the Treeview widget (self.tree) is fully initialized
        if hasattr(self, 'tree'):
            self.restart()



    def create_graph(self, parent):
        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Pain Score")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 1)
        self.ax.set_yticks(np.arange(0, 101, 10))
        self.ax.text(0.5, 50, "No data yet", ha='center', va='center')

        self.canvas = FigureCanvasTkAgg(self.figure, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def update_graph(self):
        time_points, pain_scores_1, pain_scores_2, comments = self.get_graph_data()
        self.ax.clear()
        self.ax.set_ylim(0, 100)
        self.ax.set_yticks(np.arange(0, 101, 10))

        if pain_scores_1:
            self.ax.plot(time_points, pain_scores_1, marker='o', linestyle='-', color='blue', label=self.pain_area_1.get())
            if self.track_two_areas.get() and pain_scores_2:
                self.ax.plot(time_points, pain_scores_2, marker='s', linestyle='-', color='red', label=self.pain_area_2.get())

            if len(time_points) == 1:
                self.ax.set_xlim(time_points[0] - 0.5, time_points[0] + 0.5)
            else:
                self.ax.set_xlim(min(time_points), max(time_points))

            if self.show_actual_pain.get():
                for x, y1 in zip(time_points, pain_scores_1):
                    self.ax.text(x, y1 + 2, f"{y1}", ha='center', va='bottom', fontsize=9, color='blue')
                if self.track_two_areas.get():
                    for x, y2 in zip(time_points, pain_scores_2):
                        self.ax.text(x, y2 + 2, f"{y2}", ha='center', va='bottom', fontsize=9, color='red')

            if self.show_comments.get():
                for i, comment in enumerate(comments):
                    if comment:
                        y = pain_scores_1[i] if not self.track_two_areas.get() else max(pain_scores_1[i], pain_scores_2[i] if pain_scores_2 else 0)
                        self.ax.annotate(comment, (time_points[i], y), xytext=(0, 30), textcoords="offset points", ha='center', va='bottom', bbox=dict(boxstyle="round,pad=0.3", fc="yellow", ec="b", lw=1, alpha=0.8))

            if self.show_80_percent_line.get():
                self.ax.axhline(y=self.target_pain_score_1, color='blue', linestyle='--', label=f'80% Reduction ({self.pain_area_1.get()})')
                if self.track_two_areas.get():
                    self.ax.axhline(y=self.target_pain_score_2, color='red', linestyle='--', label=f'80% Reduction ({self.pain_area_2.get()})')

            self.ax.legend()

        else:
            self.ax.set_xlim(0, 1)
            self.ax.text(0.5, 50, "No data yet", ha='center', va='center')

        self.ax.set_title("Pain Graph")
        self.ax.set_xlabel("Time" if not self.use_minutes.get() else "Minutes")
        self.ax.set_ylabel("Pain Score")
        self.canvas.draw()



    def get_graph_data(self):
        time_points, pain_scores_1, pain_scores_2, comments = [], [], [], []
        for child in self.tree.get_children():
            item = self.tree.item(child)["values"]
            
            # Extract the time point (first column)
            time_points.append(int(item[0].split()[0] if self.use_minutes.get() else item[0].split()[1]))
            
            # Extract Pain Score 1 from the second column
            pain_scores_1.append(int(item[1]) if item[1] != 'N/A' else None)
            
            if self.track_two_areas.get():
                # Extract Pain Score 2 from the fourth column (if tracking two areas)
                pain_scores_2.append(int(item[3]) if item[3] != 'N/A' else None)
                # Extract the comment from the sixth column
                comments.append(item[5] if len(item) > 5 else "")
            else:
                # Extract the comment from the correct column when only one area is tracked
                comments.append(item[5] if len(item) > 5 else "")
                pain_scores_2 = []  # Ensure this remains empty when not tracking the second area
                
        return time_points, pain_scores_1, pain_scores_2, comments





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
            initial_pain_1 = self.pain0_1.get()
            if 0 <= initial_pain_1 <= 100:
                self.target_pain_score_1 = initial_pain_1 * 20 // 100
                self.tree.delete(*self.tree.get_children())
                values = [self.get_time_display(0), f"{initial_pain_1:3d}", f"N/A - Target for 80% Reduction: {self.target_pain_score_1}"]
                
                # Disable entries for Area 1 and Area 2
                self.disable_entries()

                if self.track_two_areas.get():
                    initial_pain_2 = self.pain0_2.get()
                    if 0 <= initial_pain_2 <= 100:
                        self.target_pain_score_2 = initial_pain_2 * 20 // 100
                        values.extend([f"{initial_pain_2:3d}", f"N/A - Target for 80% Reduction: {self.target_pain_score_2}"])
                    else:
                        messagebox.showerror("Error", "Initial pain scores must be between 0 and 100.")
                        self.enable_entries()  # Re-enable if there's an error
                        return
                
                values.append("")  # For comment
                self.tree.insert("", "end", values=tuple(values))
                self.time_point = 0
                self.update_graph()
                self.current_pain_1_entry.config(state="normal")
                self.current_pain_2_entry.config(state="normal")
                self.custom_time_entry.config(state="normal")
            else:
                messagebox.showerror("Error", "Initial pain scores must be between 0 and 100.")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers for the starting pain scores.")
            self.enable_entries()  # Re-enable if there's an error



    def add_pain_score(self):
        try:
            current_pain_1 = self.current_pain_1.get()
            if 0 <= current_pain_1 <= 100:
                self.time_point += self.custom_time.get() if self.use_minutes.get() else 1
                reduction_percentage_1 = ((self.pain0_1.get() - current_pain_1) * 100) // self.pain0_1.get() if self.pain0_1.get() != 0 else 'N/A'
                values = [self.get_time_display(self.time_point), f"{current_pain_1:3d}", f"{reduction_percentage_1}%"]
                
                if self.track_two_areas.get():
                    current_pain_2 = self.current_pain_2.get()
                    if 0 <= current_pain_2 <= 100:
                        reduction_percentage_2 = ((self.pain0_2.get() - current_pain_2) * 100) // self.pain0_2.get() if self.pain0_2.get() != 0 else 'N/A'
                        values.extend([f"{current_pain_2:3d}", f"{reduction_percentage_2}%"])
                    else:
                        messagebox.showerror("Error", "Pain scores must be between 0 and 100.")
                        return
                else:
                    # Fill with "N/A" for the untracked area
                    values.extend(["N/A", "N/A"])
                
                values.append("")  # For comment
                self.tree.insert("", "end", values=tuple(values))
                self.update_graph()
            else:
                messagebox.showerror("Error", "Pain scores must be between 0 and 100.")
        except tk.TclError:
            messagebox.showerror("Error", "Please enter valid numbers for the current pain scores.")



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
        self.pain0_1.set(0)
        self.pain0_2.set(0)
        self.current_pain_1.set(0)
        self.current_pain_2.set(0)
        self.time_point = 0
        self.target_pain_score_1 = 0
        self.target_pain_score_2 = 0
        self.tree.delete(*self.tree.get_children())
        self.update_graph()
        
        # Re-enable the entries for Area 1 and Area 2
        self.enable_entries()

    def copy_to_clipboard(self):
        headers = "Time\tPain\tReduction\tComment\n"
        table_data = headers + "\n".join("\t".join(str(val) for val in self.tree.item(child)["values"]) for child in self.tree.get_children())
        self.master.clipboard_clear()
        self.master.clipboard_append(table_data)
        messagebox.showinfo("Copied", "Table data has been copied to clipboard.")

    def add_edit_comment(self, event=None):
        item = self.tree.selection()[0] if not event else self.tree.identify_row(event.y) if self.tree.identify_column(event.x) == "#6" else None
        if not item:
            messagebox.showinfo("Info", "Please select a row to add/edit a comment.")
            return

        values = self.tree.item(item, "values")
        new_comment = simpledialog.askstring("Add/Edit Comment", "Enter your comment:", initialvalue=values[5])
        if new_comment is not None:
            self.tree.item(item, values=(values[0], values[1], values[2], values[3], values[4], new_comment))
            self.update_graph()

    def export_to_pdf(self):
        # Use the entered patient details
        patient_name = self.patient_name.get()
        patient_nhi = self.patient_nhi.get()
        procedure_date = self.procedure_date.get()
        procedure_name = self.procedure_name.get()

        # Validate patient details
        if not all([patient_name, patient_nhi, procedure_date, procedure_name]):
            messagebox.showerror("Error", "All patient details must be filled in.")
            return

        # Ask user where to save the file
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not file_path:
            return

        # Save the current figure (graph) as an image
        graph_image_path = "graph.png"
        self.figure.savefig(graph_image_path, format='png')

        # Create a PDF document
        pdf = SimpleDocTemplate(file_path, pagesize=letter)

        # Prepare patient details to be printed at the top of the PDF
        styles = getSampleStyleSheet()
        patient_details = Paragraph(f"<strong>Patient Name</strong>: {patient_name}<br/><strong>Patient NHI</strong>: {patient_nhi}<br/><strong>Procedure Date</strong>: {procedure_date}<br/><strong>Procedure Name</strong>: {procedure_name}<br/><br/>", styles["Normal"])

        # Prepare data for the table
        data = [["Time", f"{self.pain_area_1.get()} Pain", f"{self.pain_area_1.get()} Reduction", f"{self.pain_area_2.get()} Pain", f"{self.pain_area_2.get()} Reduction", "Comment"]]
        for child in self.tree.get_children():
            item = self.tree.item(child)["values"]
            data.append(item)

        # Create the table with the data
        table = Table(data)

        # Add some style to the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        table.setStyle(style)

        # Create an image object from the saved graph
        graph_image = Image(graph_image_path)

        # Set the image width and height, adjusting to fit the page
        graph_image.drawHeight = 5 * 72  # 4 inches
        graph_image.drawWidth = 7 * 72  # 7 inches

        # Build the PDF with the patient details, graph, and the table
        elements = [patient_details, graph_image, table]
        pdf.build(elements)

        messagebox.showinfo("Exported", f"Pain Tracker data has been exported to {file_path}.")

    def disable_entries(self):
        # Disable entries for Area 1 and Area 2
        self.pain_area_1_entry.config(state="disabled")
        self.pain_area_2_entry.config(state="disabled")
        self.pain0_1_entry.config(state="disabled")
        self.pain0_2_entry.config(state="disabled")
        self.start_button.config(state="disabled")


    def enable_entries(self):
        # Re-enable entries for Area 1 and Area 2
        self.pain_area_1_entry.config(state="normal")
        self.pain_area_2_entry.config(state="normal")
        self.pain0_1_entry.config(state="normal")
        self.pain0_2_entry.config(state="normal")
        self.start_button.config(state="normal")
        #self.current_pain_1_entry.config(state="normal")
        #self.current_pain_2_entry.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = PainTrackerApp(root)
    root.mainloop()
