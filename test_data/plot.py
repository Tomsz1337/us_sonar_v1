import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import pyqtgraph.exporters
import csv
import sys
import os

# =========================
# PARAMETRY KONFIGURACJI
# =========================
CSV_FILENAME = 'recorded_data_003.csv'
NUM_SAMPLES = 1000
MAX_COLS = 300
SAMPLE_TIME = 20e-6  # 20 µs
SPEED_OF_SOUND = 1480  # m/s
SAMPLE_RESOLUTION = (SPEED_OF_SOUND * SAMPLE_TIME) / 2  

COLOR_LEVEL_MIN = 0
COLOR_LEVEL_MAX = 2000



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
    
    gain_vector = np.linspace(1.0, gain_factor, data.shape[0])
    return data * gain_vector[:, np.newaxis]

# =========================
# SET Y TICKS
# =========================
def update_image_yticks(axis, num_ticks):
    yticks = [(i * SAMPLE_RESOLUTION, f'{i * SAMPLE_RESOLUTION:.1f}')
              for i in range(0, num_ticks, 35)]
    axis.setTicks([yticks])


# =========================
# UPDATE MARKER
# =========================
def update_image_marker_label():
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
    
    levelLO = slider_rangeL.value()
    levelHI = slider_rangeH.value()

    gain_val = slider_tvg.value() / 10.0  # np. 20 → 2.0x
    data2 = apply_tvg(data.T, gain_val).T

    visible_samples = slider_y.value()
    view_data = data2[start:end]

    if view_data.shape[0] < MAX_COLS:
        padding = np.zeros((MAX_COLS - view_data.shape[0], NUM_SAMPLES))
        view_data = np.vstack((padding, view_data))

    view_data = view_data[:, :visible_samples]

    img.setImage(view_data, autoLevels=False)
    img.setLevels([levelLO, levelHI])
    num_visible_samples = view_data.shape[1]
    img.setRect(QtCore.QRectF(0, 0, MAX_COLS, num_visible_samples * SAMPLE_RESOLUTION))
    update_image_yticks(plot.getAxis('left'), visible_samples)
    update_image_marker_label()

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
xticks = [(i, str(i - MAX_COLS)) for i in range(0, MAX_COLS + 1, 50)]
plot.getAxis('bottom').setTicks([xticks])
plot.invertY(True)
plot.setLabel('bottom', 'Time (Frames)')
plot.setLabel('left', 'Distance (m)')

# add image
img = pg.ImageItem()
cmap = pg.colormap.get('viridis')
img.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))
img.setLevels([COLOR_LEVEL_MIN, COLOR_LEVEL_MAX])
plot.addItem(img)

# =========================
# MARKER
# =========================
marker = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=1))
label = pg.TextItem(color='r', anchor=(1, 1))
plot.addItem(marker)
plot.addItem(label)
marker.sigPositionChanged.connect(update_image_marker_label)

# Sliders
slider_x_layout = QtWidgets.QHBoxLayout()

slider_x = QtWidgets.QSlider(QtCore.Qt.Horizontal)
slider_x.setMinimum(0)
slider_x.setMaximum(max(0, data.shape[0] - MAX_COLS))
slider_x.setValue(0)
slider_x.valueChanged.connect(update_image)
slider_x_layout.addWidget(slider_x)
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

slider_y.valueChanged.connect(update_image)

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

slider_rangeH.valueChanged.connect(update_image)

slider_rangeH_layout.addWidget(slider_rangeH_label)
slider_rangeH_layout.addWidget(slider_rangeH)


slider_rangeL_layout = QtWidgets.QVBoxLayout()
slider_rangeL_label = QtWidgets.QLabel("Level\nLO")
slider_rangeL_label.setAlignment(QtCore.Qt.AlignCenter)

slider_rangeL = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_rangeL.setMinimum(COLOR_LEVEL_MIN)
slider_rangeL.setMaximum(int(COLOR_LEVEL_MAX / 2))
slider_rangeL.setValue(COLOR_LEVEL_MIN)

slider_rangeL.valueChanged.connect(update_image)

slider_rangeL_layout.addWidget(slider_rangeL_label)
slider_rangeL_layout.addWidget(slider_rangeL)

# =========================
# TVG SLIDER
# =========================
slider_tvg_layout = QtWidgets.QVBoxLayout()
slider_tvg_label = QtWidgets.QLabel("TVG")
slider_tvg_label.setAlignment(QtCore.Qt.AlignCenter)

slider_tvg = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_tvg.setMinimum(10)
slider_tvg.setMaximum(30)
slider_tvg.setValue(10)

slider_tvg.valueChanged.connect(update_image)

slider_tvg_layout.addWidget(slider_tvg_label)
slider_tvg_layout.addWidget(slider_tvg)

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
hlayout.addWidget(save_button)
vlayout = QtWidgets.QVBoxLayout()
vlayout.addLayout(slider_x_layout)

main_layout.addLayout(hlayout)
main_layout.addLayout(vlayout)


# window settings
main_win.setWindowTitle("Waterfall plot")

main_win.show()

# initial values
marker.setValue(0.0)
update_image()

# app start
sys.exit(app.exec())
