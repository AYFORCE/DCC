#from run_vinkeldrej import run_ND287
import tkinter as tk
import threading

class CalibrationGUI:
    def __init__(self, results, angle):
        self.root = tk.Tk()
        self.root.title("Calibration")

        self.repeat_flag = False
        self.user_input = ""
        self.result_label = None

        self.create_widgets(results, angle)

    def create_widgets(self, results, angle):
        # Result label
        self.result_label = tk.Label(self.root, text=f"I got the result {results}, I should hit {angle}. should I repeat my measurement?", pady=10)
        self.result_label.pack()

        # Label and text field
        label = tk.Label(self.root, text="DUT-measurement")
        label.pack()

        self.entry = tk.Entry(self.root)
        self.entry.pack()

        # Set focus to the text field
        self.entry.focus_set()

        # Repeat button
        repeat_button = tk.Button(self.root, text="Repeat", command=self.repeat_measurement)
        repeat_button.pack()

        # OK button
        ok_button = tk.Button(self.root, text="OK", command=self.accept_input)
        ok_button.pack()

        # Bind the Enter key to trigger the OK button functionality
        self.root.bind('<Return>', lambda event: self.accept_input())

    def repeat_measurement(self):
        self.repeat_flag = True
        self.root.destroy()

    def accept_input(self):
        self.user_input = self.entry.get()
        self.root.destroy()

    def run(self):
        self.root.mainloop()

class OverviewWindow:
    def __init__(self, measurements):
        self.measurements = measurements
        self.thread = threading.Thread(target=self.create_widgets)

    def create_widgets(self):
        self.root = tk.Tk()
        self.root.title("Overview")

        # Create a text widget to display the measurements
        self.text_widget = tk.Text(self.root)
        self.text_widget.pack()

        # Start the main loop
        self.root.mainloop()

    def update_measurements(self, measurements):
        self.measurements = measurements

        # Clear the text widget
        self.text_widget.delete("1.0", tk.END)

        # Insert the updated measurements into the text widget
        self.insert_measurements(self.text_widget, self.measurements)

    def insert_measurements(self, text_widget, measurements):
        # Convert measurements to a formatted string
        measurements_str = self.format_measurements(measurements)

        # Insert the measurements into the text widget
        text_widget.insert(tk.END, measurements_str)

    def format_measurements(self, measurements):
        measurements_str = ""

        for i, measurement in enumerate(measurements):
            measurements_str += f"Measurement {i + 1}:\n"

            # Call a recursive helper function to format the measurements
            measurements_str = self.format_measurements_recursive(measurement, measurements_str, 1)

            measurements_str += "\n"

        return measurements_str

    def format_measurements_recursive(self, measurements, measurements_str, indent_level):
        indent = "    " * indent_level

        for key, value in measurements.items():
            if isinstance(value, dict):
                measurements_str += f"{indent}{key}:\n"
                measurements_str = self.format_measurements_recursive(value, measurements_str, indent_level + 1)
            else:
                measurements_str += f"{indent}    {key}:\n"
                for a in value:
                    if ":" not in str(a):
                        measurements_str += f"{indent}        {a}\n"
                    else:
                        measurements_str += "\n"

        return measurements_str

    def start(self):
        self.thread.start()