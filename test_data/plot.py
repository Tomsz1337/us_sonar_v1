import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import csv
import sys

# =========================
# PARAMETRY KONFIGURACJI
# =========================
CSV_FILENAME = 'recorded_data_003.csv'
NUM_SAMPLES = 1000
MAX_COLS = 300
SAMPLE_TIME = 20e-6  # 20 µs
SPEED_OF_SOUND = 1480  # m/s
SAMPLE_RESOLUTION = (SPEED_OF_SOUND * SAMPLE_TIME) / 2  # Metry / próbkę


# =========================
# READ CSV DATA
# =========================
def load_data(filename, expected_length):
    data = []
    with open(filename, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) == expected_length:
                data.append([int(val) for val in row])
    return np.array(data)

# =========================
# FUNCTION: Apply TVG
# =========================
def apply_tvg(data, gain_factor=1.0):
    # Create a gain vector that increases linearly with depth (sample index)
    gain_vector = np.linspace(1.0, gain_factor, data.shape[0])
    return data * gain_vector[:, np.newaxis]

# =========================
# SET Y TICKS
# =========================
def update_yticks(axis, num_ticks):
    yticks = [(i * SAMPLE_RESOLUTION, f'{i * SAMPLE_RESOLUTION:.1f}')
              for i in range(0, num_ticks, 35)]
    axis.setTicks([yticks])


# =========================
# UPDATE MARKER
# =========================
def update_marker_label():
    y_val = marker.value()
    label.setText(f"Y = {y_val:.2f} m")
    label.setPos(MAX_COLS, y_val)


# =========================
# UPDATE IMAGE
# =========================
def update_image():
    start = slider_x.value()
    end = start + MAX_COLS
    end = min(end, data.shape[0])
    start = max(0, end - MAX_COLS)
    
    gain_val = slider_tvg.value() / 10.0  # np. 20 → 2.0x
    data2 = apply_tvg(data.T, gain_val).T

    visible_samples = slider_y.value()
    view_data = data2[start:end]

    if view_data.shape[0] < MAX_COLS:
        padding = np.zeros((MAX_COLS - view_data.shape[0], NUM_SAMPLES))
        view_data = np.vstack((padding, view_data))

    view_data = view_data[:, :visible_samples]

    img.setImage(view_data, autoLevels=False)
    img.setLevels([np.min(data), np.max(data)])
    num_visible_samples = view_data.shape[1]
    img.setRect(QtCore.QRectF(0, 0, MAX_COLS, num_visible_samples * SAMPLE_RESOLUTION))
    update_yticks(plot.getAxis('left'), visible_samples)
    update_marker_label()


# =========================
# MAIN APP
# =========================
# Read data
data = load_data(CSV_FILENAME, NUM_SAMPLES)

# app init
app = QtWidgets.QApplication(sys.argv)
main_win = QtWidgets.QMainWindow()
central_widget = QtWidgets.QWidget()
main_layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(main_layout)
main_win.setCentralWidget(central_widget)

#  plot
graphics_layout = pg.GraphicsLayoutWidget()
plot = graphics_layout.addPlot()
plot.invertY(True)
plot.setLabel('bottom', 'Time (Frames)')
plot.setLabel('left', 'Distance (m)')

# add image
img = pg.ImageItem()
cmap = pg.colormap.get('viridis')
img.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))
img.setLevels([0, 2000])
plot.addItem(img)

# Marker + label
marker = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=1))
label = pg.TextItem(color='r', anchor=(1, 1))
plot.addItem(marker)
plot.addItem(label)
marker.sigPositionChanged.connect(update_marker_label)

# Sliders
slider_x = QtWidgets.QSlider(QtCore.Qt.Horizontal)
slider_x.setMinimum(0)
slider_x.setMaximum(max(0, data.shape[0] - MAX_COLS))
slider_x.setValue(0)

slider_y = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_y.setMinimum(10)
slider_y.setMaximum(NUM_SAMPLES)
slider_y.setValue(NUM_SAMPLES)

slider_tvg = QtWidgets.QSlider(QtCore.Qt.Horizontal)
slider_tvg.setMinimum(10)   # 1.0x (10 / 10)
slider_tvg.setMaximum(50)   # 5.0x (50 / 10)
slider_tvg.setValue(20)     # Domyślnie 2.0x

slider_x.valueChanged.connect(update_image)
slider_y.valueChanged.connect(update_image)
slider_tvg.valueChanged.connect(update_image)

# Buttons
tvg_lin_button = QtWidgets.QPushButton('test')


# Plot and marker layout
hlayout = QtWidgets.QHBoxLayout()
vlayout = QtWidgets.QVBoxLayout()
vlayout.addWidget(graphics_layout)
vlayout.addWidget(slider_x)
hlayout.addLayout(vlayout)
hlayout.addWidget(slider_y)
main_layout.addLayout(hlayout)
main_layout.addWidget(QtWidgets.QLabel("TVG Gain"))
main_layout.addWidget(slider_tvg)
main_layout.addWidget(tvg_lin_button)

# window settings
main_win.setWindowTitle("Waterfall plot")

main_win.show()

# initial values
marker.setValue(0.0)
update_image()

# app start
sys.exit(app.exec())
