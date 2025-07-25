import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import csv
import sys

# =========================
# PARAMETRY KONFIGURACJI
# =========================
CSV_FILENAME = 'test4.csv'
NUM_SAMPLES = 1000
MAX_COLS = 150
SAMPLE_TIME = 20e-6  # 20 µs
SPEED_OF_SOUND = 1430  # m/s
SAMPLE_RESOLUTION = (SPEED_OF_SOUND * SAMPLE_TIME) / 2  # Metry / próbkę


# =========================
# FUNKCJA: Wczytaj dane z CSV
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
# FUNKCJA: Ustaw znaczniki Y
# =========================
def update_yticks(axis, num_ticks):
    yticks = [(i * SAMPLE_RESOLUTION, f'{i * SAMPLE_RESOLUTION:.1f}')
              for i in range(0, num_ticks, 35)]
    axis.setTicks([yticks])


# =========================
# FUNKCJA: Aktualizacja markera
# =========================
def update_marker_label():
    y_val = marker.value()
    label.setText(f"Y = {y_val:.2f} m")
    label.setPos(MAX_COLS, y_val)


# =========================
# FUNKCJA: Aktualizacja obrazu
# =========================
def update_image():
    start = slider_x.value()
    end = start + MAX_COLS
    end = min(end, data.shape[0])
    start = max(0, end - MAX_COLS)

    visible_samples = slider_y.value()
    view_data = data[start:end]

    if view_data.shape[0] < MAX_COLS:
        padding = np.zeros((MAX_COLS - view_data.shape[0], NUM_SAMPLES))
        view_data = np.vstack((padding, view_data))

    view_data = view_data[:, :visible_samples]

    img.setImage(view_data, autoLevels=False)
    img.setLevels([np.min(data), np.max(data)])
    img.setRect(QtCore.QRectF(0, 0, MAX_COLS, visible_samples * SAMPLE_RESOLUTION))

    update_yticks(plot.getAxis('left'), visible_samples)
    update_marker_label()


# =========================
# GŁÓWNA CZĘŚĆ APLIKACJI
# =========================
# Wczytaj dane
data = load_data(CSV_FILENAME, NUM_SAMPLES)

# Inicjalizacja aplikacji
app = QtWidgets.QApplication(sys.argv)
main_win = QtWidgets.QMainWindow()
central_widget = QtWidgets.QWidget()
main_layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(main_layout)
main_win.setCentralWidget(central_widget)

# Tworzenie wykresu
graphics_layout = pg.GraphicsLayoutWidget()
plot = graphics_layout.addPlot()
plot.invertY(True)
plot.setLabel('bottom', 'Time (Frames)')
plot.setLabel('left', 'Distance (m)')

# Dodaj obraz
img = pg.ImageItem()
cmap = pg.colormap.get('viridis')
img.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))
plot.addItem(img)

# Marker + etykieta
marker = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=1))
label = pg.TextItem(color='r', anchor=(1, 1))
plot.addItem(marker)
plot.addItem(label)
marker.sigPositionChanged.connect(update_marker_label)

# Slidery
slider_x = QtWidgets.QSlider(QtCore.Qt.Horizontal)
slider_x.setMinimum(0)
slider_x.setMaximum(max(0, data.shape[0] - MAX_COLS))
slider_x.setValue(0)

slider_y = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_y.setMinimum(10)
slider_y.setMaximum(NUM_SAMPLES)
slider_y.setValue(NUM_SAMPLES)

slider_x.valueChanged.connect(update_image)
slider_y.valueChanged.connect(update_image)

# Layout wykresu i sliderów
hlayout = QtWidgets.QHBoxLayout()
vlayout = QtWidgets.QVBoxLayout()
vlayout.addWidget(graphics_layout)
vlayout.addWidget(slider_x)
hlayout.addLayout(vlayout)
hlayout.addWidget(slider_y)
main_layout.addLayout(hlayout)

# Ustawienia okna
main_win.setWindowTitle("Waterfall plot")
main_win.resize(1000, 500)
main_win.show()

# Początkowe wartości
marker.setValue(0.0)
update_image()

# Start aplikacji
sys.exit(app.exec())
