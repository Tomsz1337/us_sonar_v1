import socket
import struct
import numpy as np
import csv
import os
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore, QtWidgets
from scipy.signal import medfilt


# =========================
# CONFIG PARAMS
# =========================
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

NUM_SAMPLES = 1000      
MAX_COLS = 300          
SPEED_OF_SOUND = 1480  
SAMPLE_TIME = 20e-6
SAMPLE_RESOLUTION = (SPEED_OF_SOUND * SAMPLE_TIME) / 2 

COLOR_LEVEL_MIN = 0
COLOR_LEVEL_MAX = 2000

# =========================
# DATA INIT
# =========================
data = np.zeros((NUM_SAMPLES, MAX_COLS), dtype=np.uint16)
buffer = b""
recording = False


# =========================
# FUNCTION: CSV NAME CHECK
# =========================
def csv_filename():
    
    base_name = "recorded_data"
    ext = ".csv"
    i = 1
    while True:
        filename = f"{base_name}_{i:03d}{ext}"
        if not os.path.exists(filename):
            return filename
        i += 1

# =========================
# FUNCTION: SAVE IMG TO PNG
# =========================

def save_image():
    
    base_name = "img"
    ext = ".png"
    i = 1
    while True:
        filename = f"{base_name}_{i:03d}{ext}"
        if not os.path.exists(filename):
            break
        i += 1
    exporter = pg.exporters.ImageExporter(plot)
    exporter.parameters()['width'] = 1000
    exporter.export(filename)
    print(f"Saved plot as {filename}")

# =========================
# FUNCTION: Update Marker
# =========================

def update_marker_label():
    
    y_idx = marker.value()
    y_meters = y_idx * SAMPLE_RESOLUTION
    label.setText(f"Y = {y_meters:.2f} m")
    label.setPos(MAX_COLS, y_idx)

# =========================
# FUNCTION: Apply TVG
# =========================

def apply_tvg(data, gain_factor=1.0):
    log_scale = 5
    depth = np.arange(data.shape[0])
    gain_vector = 0.5 + (np.log10(1 + depth / log_scale) / np.log10(len(depth)/ log_scale)) * (gain_factor - 1.0)
    return data * gain_vector[:, np.newaxis]

# =========================
# FUNCTION: Cutoff Filter
# =========================
def cutoff_flt(data, cutoff_threshold):
    arr = np.array(data)
    arr[arr < cutoff_threshold] = 0
    return arr

# =========================
# FUNCTION: Median Filter
# =========================
def median_flt(data, size = 3):
    if(size % 2 == 0): 
        size = size + 1
    filtered = medfilt(data, kernel_size=size)
    return filtered

# =========================
# FUNCTION: UPDATE APP
# =========================

def update():
    
    global buffer, recording, data

    visible_samples = slider_y.value()
    colorLO = slider_rangeL.value()
    colorHI = slider_rangeH.value()
    gain = slider_tvg.value() / 10.0

    try:
        while True:
            data_in, address = sock.recvfrom(2048)

            if data_in.startswith(b"sp\n"):
                buffer = b""
                recording = True
                continue

            if data_in.endswith(b"\n") and recording:
                buffer += data_in[:-1]
                recording = False

                num_samples_recv = len(buffer) // 2
                if num_samples_recv != NUM_SAMPLES:
                    print(f"Warning: expected {NUM_SAMPLES}, got {num_samples_recv}")
                    continue

                samples = struct.unpack(f"<{NUM_SAMPLES}H", buffer)
                writer.writerow(samples)
                csvfile.flush()
                print(f"Wrote {num_samples_recv} samples to CSV")

                frame = np.array(samples, dtype=np.uint16)
                frame_tvg = apply_tvg(frame[:, np.newaxis], gain).flatten()
                if med_flt_but.isChecked():
                    frame_tvg = median_flt(frame_tvg)
                cut_th = slider_cut.value()
                frame_tvg[frame_tvg < cut_th] = 0
                data = np.roll(data, -1, axis=1)
                data[:, -1] = frame_tvg

                img.setLevels([colorLO, colorHI])

                view_data = data.T[:, :visible_samples]
                img.setImage(view_data, autoLevels=False)
                update_marker_label()

            elif recording:
                buffer += data_in

    except BlockingIOError:
        pass

# =========================
# FUNCTION: CLOSE APP
# =========================

def close_event():
    
    csvfile.close()
    sock.close()
    print("Socket and CSV file closed.")


# =========================
# UDP SOCKET CONFIG
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)
print(f"Listening on UDP port {UDP_PORT}...")


# =========================
# CSV FILE CREATION
# =========================
csvfile = open(csv_filename(), "w", newline="")
writer = csv.writer(csvfile)


# =========================
# QT APP INIT
# =========================
app = QtWidgets.QApplication([])
main_win = QtWidgets.QMainWindow()
central_widget = QtWidgets.QWidget()
main_layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(main_layout)
main_win.setCentralWidget(central_widget)
main_win.setWindowTitle("Echosounder GUI")


# =========================
# GRAPH INIT
# =========================
graphics_layout = pg.GraphicsLayoutWidget()
plot = graphics_layout.addPlot()
plot.setLabel('bottom', 'Time [s]')
plot.setLabel('left', 'Distance [m]')
plot.invertY(True)
xticks = [(i, str((i - MAX_COLS)*0.1)) for i in range(0, MAX_COLS + 1, 50)]
plot.getAxis('bottom').setTicks([xticks])

# image settings
img = pg.ImageItem()
cmap = pg.colormap.get('viridis')
img.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))
img.setLevels([COLOR_LEVEL_MIN, COLOR_LEVEL_MAX])
plot.addItem(img)

# Y axis ticks settings
yticks = [(i, f'{i * SAMPLE_RESOLUTION:.1f}') for i in range(0, NUM_SAMPLES, 35)]
plot.getAxis('left').setTicks([yticks])


# =========================
# MARKER
# =========================
marker = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=1))
label = pg.TextItem(color='r', anchor=(1, 1))
plot.addItem(marker)
plot.addItem(label)
marker.sigPositionChanged.connect(update_marker_label)


# =========================
# ZOOM SLIDER
# =========================
slider_y_layout = QtWidgets.QVBoxLayout()
slider_y_label = QtWidgets.QLabel("Zoom\n")
slider_y_label.setAlignment(QtCore.Qt.AlignCenter)

slider_y = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_y.setMinimum(10)
slider_y.setMaximum(NUM_SAMPLES)
slider_y.setValue(NUM_SAMPLES)

slider_y.valueChanged.connect(update)

slider_y_layout.addWidget(slider_y_label)
slider_y_layout.addWidget(slider_y)

# =========================
# COLOR RANGE SLIDERS
# =========================
slider_rangeH_layout = QtWidgets.QVBoxLayout()
slider_rangeH_label = QtWidgets.QLabel("Level\nHI")
slider_rangeH_label.setAlignment(QtCore.Qt.AlignCenter)

slider_rangeH = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_rangeH.setMinimum(int(COLOR_LEVEL_MAX / 2))
slider_rangeH.setMaximum(COLOR_LEVEL_MAX)
slider_rangeH.setValue(COLOR_LEVEL_MAX)

slider_rangeH.valueChanged.connect(update)

slider_rangeH_layout.addWidget(slider_rangeH_label)
slider_rangeH_layout.addWidget(slider_rangeH)


slider_rangeL_layout = QtWidgets.QVBoxLayout()
slider_rangeL_label = QtWidgets.QLabel("Level\nLO")
slider_rangeL_label.setAlignment(QtCore.Qt.AlignCenter)

slider_rangeL = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_rangeL.setMinimum(COLOR_LEVEL_MIN)
slider_rangeL.setMaximum(int(COLOR_LEVEL_MAX / 2))
slider_rangeL.setValue(COLOR_LEVEL_MIN)

slider_rangeL.valueChanged.connect(update)

slider_rangeL_layout.addWidget(slider_rangeL_label)
slider_rangeL_layout.addWidget(slider_rangeL)

# =========================
# TVG SLIDER
# =========================
slider_tvg_layout = QtWidgets.QVBoxLayout()
slider_tvg_label = QtWidgets.QLabel("TVG\n")
slider_tvg_label.setAlignment(QtCore.Qt.AlignCenter)

slider_tvg = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_tvg.setMinimum(10)
slider_tvg.setMaximum(30)
slider_tvg.setValue(10)

slider_tvg.valueChanged.connect(update)

slider_tvg_layout.addWidget(slider_tvg_label)
slider_tvg_layout.addWidget(slider_tvg)

# =========================
# CUTOFF SLIDER
# =========================
slider_cut_layout = QtWidgets.QVBoxLayout()
slider_cut_label = QtWidgets.QLabel("Cutoff\nfilter")
slider_cut_label.setAlignment(QtCore.Qt.AlignCenter)

slider_cut = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_cut.setMinimum(0)
slider_cut.setMaximum(600)
slider_cut.setValue(0)

slider_cut.valueChanged.connect(update)

slider_cut_layout.addWidget(slider_cut_label)
slider_cut_layout.addWidget(slider_cut)

# =========================
# MEDIAN FILTER BUTTON
# =========================
med_flt_but = QtWidgets.QPushButton("Median\nFilter")
med_flt_but.setCheckable(True)
med_flt_but.toggled.connect(update)

# =========================
# SAVE PNG BUTTON
# =========================
save_button = QtWidgets.QPushButton("Save PNG")
save_button.clicked.connect(save_image)

# =========================
# MAIN LAYOUT
# =========================
hlayout = QtWidgets.QHBoxLayout()
hlayout.addWidget(graphics_layout)
hlayout.addLayout(slider_y_layout)
hlayout.addLayout(slider_rangeH_layout)
hlayout.addLayout(slider_rangeL_layout)
hlayout.addLayout(slider_tvg_layout)
hlayout.addLayout(slider_cut_layout)
buttons_layout = QtWidgets.QVBoxLayout()
buttons_layout.addWidget(med_flt_but)
buttons_layout.addWidget(save_button)
hlayout.addLayout(buttons_layout)
main_layout.addLayout(hlayout)


# =========================
# TIMER AND CLOSE EVENT
# =========================
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)

app.aboutToQuit.connect(close_event)

marker.setValue(0.0)
update_marker_label()

# =========================
# APP START
# =========================
main_win.show()
QtWidgets.QApplication.instance().exec_()
