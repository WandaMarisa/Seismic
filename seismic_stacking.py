import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import matplotlib.pyplot as plt
from obspy import read

# Function to read SEG-Y files
def read_segy_file(filename):
    try:
        segy_data = read(filename, format="SEGY")
        traces = np.array([trace.data for trace in segy_data.traces])
        return traces
    except Exception as e:
        messagebox.showerror("File Error", f"Error reading {filename}: {e}")
        return None

# Function to process and stack selected SEG-Y files
def process_files(filepaths, before_frame, after_frame):
    all_traces = [read_segy_file(file) for file in filepaths if read_segy_file(file) is not None]

    if not all_traces:
        messagebox.showinfo("No Data", "No valid SEG-Y files found.")
        return

    # Display each file's data before stacking
    display_before_stacking(all_traces, before_frame)

    # Find the max number of traces and samples
    max_traces = max(trace.shape[0] for trace in all_traces)
    max_samples = max(trace.shape[1] for trace in all_traces)

    # Pad or truncate traces to ensure uniform shape
    padded_traces = []
    for trace_data in all_traces:
        padded_trace = np.zeros((max_traces, max_samples))
        trace_shape = trace_data.shape
        padded_trace[:trace_shape[0], :trace_shape[1]] = trace_data
        padded_traces.append(padded_trace)

    # Stack traces by averaging each trace
    stacked_trace = np.mean(np.array(padded_traces), axis=0)

    # Display the stacked result
    display_after_stacking(stacked_trace, after_frame)

# Function to display each SEG-Y file data before stacking
def display_before_stacking(all_traces, before_frame):
    # Clear previous plots
    for widget in before_frame.winfo_children():
        widget.destroy()

    # Label for "Before Stacking"
    ttk.Label(before_frame, text="Data Before Stacking", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)

    # Create individual plots for each SEG-Y file
    for i, trace_data in enumerate(all_traces):
        fig, ax = plt.subplots(figsize=(4, 3))
        cax = ax.imshow(trace_data.T, cmap='seismic', aspect='auto', interpolation='nearest')
        ax.set_title(f'SEG-Y File {i+1}')
        ax.set_xlabel('Trace Number')
        ax.set_ylabel('Time Samples')
        fig.colorbar(cax, ax=ax, label='Amplitude')

        # Display in tkinter window
        canvas = FigureCanvasTkAgg(fig, master=before_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=(i // 2) + 1, column=i % 2, padx=5, pady=5)

# Function to display stacked data after stacking
def display_after_stacking(stacked_trace, after_frame):
    # Clear previous plots
    for widget in after_frame.winfo_children():
        widget.destroy()

    # Label for "After Stacking"
    ttk.Label(after_frame, text="Data After Stacking", font=("Arial", 12, "bold")).grid(row=0, column=0, pady=5)

    # Line plot for average amplitude
    fig1, ax1 = plt.subplots(figsize=(4, 3))
    ax1.plot(stacked_trace.mean(axis=0), color='blue')
    ax1.set_title('Average Amplitude')
    ax1.set_xlabel('Time Samples')
    ax1.set_ylabel('Amplitude')

    # Display line plot in tkinter window
    canvas1 = FigureCanvasTkAgg(fig1, master=after_frame)
    canvas1.draw()
    canvas1.get_tk_widget().grid(row=1, column=0, padx=5, pady=5)

    # Heatmap for stacked seismic data
    fig2, ax2 = plt.subplots(figsize=(4, 3))
    cax = ax2.imshow(stacked_trace.T, cmap='seismic', aspect='auto', interpolation='nearest')
    ax2.set_title('Stacked Heatmap')
    ax2.set_xlabel('Trace Number')
    ax2.set_ylabel('Time Samples')
    fig2.colorbar(cax, ax=ax2, label='Amplitude')

    # Display heatmap in tkinter window
    canvas2 = FigureCanvasTkAgg(fig2, master=after_frame)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=1, column=1, padx=5, pady=5)

# Function to select SEG-Y files
def select_files(before_frame, after_frame):
    filepaths = filedialog.askopenfilenames(title="Select SEG-Y files", filetypes=[("SEG-Y files", "*.sgy *.segy")])
    if filepaths:
        process_files(filepaths, before_frame, after_frame)

# Setting up the main GUI
root = tk.Tk()
root.title("SEG-Y Stacker")
root.geometry("1000x800")

# Use ttk for modern widgets
style = ttk.Style()
style.configure("TLabel", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10))

# Main frame
main_frame = ttk.Frame(root, padding="11")
main_frame.pack(fill=tk.BOTH, expand=True)

# Header Label
header_label = ttk.Label(main_frame, text="SEG-Y Stacker", font=("Arial", 16, "bold"))
header_label.pack(pady=10)

# Button to select files
select_button = ttk.Button(main_frame, text="Select SEG-Y Files", command=lambda: select_files(before_frame, after_frame))
select_button.pack(pady=10)

# Frames for before and after stacking
plot_frame = ttk.Frame(main_frame)
plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

before_frame = ttk.LabelFrame(plot_frame, text="Data Before Stacking", padding="10")
before_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

after_frame = ttk.LabelFrame(plot_frame, text="Data After Stacking", padding="10")
after_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

plot_frame.columnconfigure(0, weight=1)
plot_frame.columnconfigure(1, weight=1)

# Run the application
root.mainloop()
