import re
import subprocess
import threading
import tkinter as tk

class PingApp:
    def __init__(self, master):
        self.master = master
        master.title("Pings")

        # Create a label and entry for the command input
        self.command_label = tk.Label(master, text="Polecenie:")
        self.command_label.pack(side=tk.TOP)
        self.command_entry = tk.Entry(master, width=25)
        self.command_entry.pack(side=tk.TOP)
        self.command_entry.insert(0, "ping")

        # Create a button to start the command
        self.button = tk.Button(master, text="Wyślij polecenie", command=self.start_command)
        self.button.pack()

        # Create a text widget to display the output
        self.text = tk.Text(master, height=40, width=25)
        self.text.pack()

        # Create a flag to stop the monitoring thread
        self.stop_flag = False

        # Add color tags for the text widget
        self.text.tag_config('orange', foreground='orange')
        self.add_color_tags()

        # Create a checkbox to control the 'stay on top' behavior
        self.stay_on_top_var = tk.BooleanVar(value=False)
        self.stay_on_top_checkbox = tk.Checkbutton(master, text="AOT", variable=self.stay_on_top_var, command=self.toggle_stay_on_top)
        self.stay_on_top_checkbox.pack()

    def toggle_stay_on_top(self):
        # Toggle the 'stay on top' behavior based on the checkbox value
        if self.stay_on_top_var.get():
            self.master.attributes('-topmost', True)
        else:
            self.master.attributes('-topmost', False)

    def start_command(self):
        # Get the command from the entry widget
        command = self.command_entry.get()

        # Start the command as a background process
        self.process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)

        # Start a thread to monitor the process output
        self.monitor_thread = threading.Thread(target=self.monitor_output)
        self.monitor_thread.start()

    def monitor_output(self):
        # Use a loop to read the output in real-time and update the text widget
        ping_count = 0
        while not self.stop_flag:
            output = self.process.stdout.readline().decode('utf-8')

            if not output:
                break

            # Use regular expressions to extract the time value
            match = re.search(r'time=(\d+)ms', output)

            # If a match is found, extract the time value and update the text widget
            if match:
                ping_count += 1
                time_value = int(match.group(1))

                # Determine the text color based on the ping value
                if time_value > 50:
                    color = "red"
                elif time_value > 30:
                    color = "orange"
                else:
                    color = "black"

                # Insert the text with a color tag
                self.text.insert(tk.END, f"{ping_count}: Time: {time_value}ms\n", color)
                self.text.see(tk.END)

                # Send a signal to update the GUI
                self.master.event_generate("<<UpdateGUI>>", when="tail")

        # Close the process
        self.process.terminate()

    def add_color_tags(self):
        self.text.tag_configure("black", foreground="black")
        self.text.tag_configure("yellow", foreground="yellow")
        self.text.tag_configure("red", foreground="red")

    def stop_command(self):
        self.stop_flag = True


# Create a new Tkinter window and run the application
root = tk.Tk()
root.geometry("200x750+{}+{}".format(root.winfo_screenwidth() - 210, root.winfo_screenheight() - 830))
app = PingApp(root)

# Add an event listener to update the GUI
root.bind("<<UpdateGUI>>", lambda event: root.update())

root.mainloop()
