import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore
import csv
import sys

# --- Parametry
csv_filename = 'test4.csv'
num_samples = 1000
max_cols = 150
sample_time = 20e-6  # 20 µs
speed_of_sound = 1430  # m/s
sample_resolution = (speed_of_sound * sample_time ) / 2 

data = []
with open(csv_filename, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        if len(row) == num_samples:
            data.append([int(val) for val in row])
data = np.array(data)

app = QtWidgets.QApplication(sys.argv)
main_win = QtWidgets.QMainWindow()
central_widget = QtWidgets.QWidget()
layout = QtWidgets.QVBoxLayout()
central_widget.setLayout(layout)
main_win.setCentralWidget(central_widget)

graphics_layout = pg.GraphicsLayoutWidget()
plot = graphics_layout.addPlot()
img = pg.ImageItem()
plot.addItem(img)
plot.invertY(True)
plot.setLabel('bottom', 'Frames')
plot.setLabel('left', 'Distance (m)')

yticks = [(i * sample_resolution, f'{i * sample_resolution:.1f}') for i in range(0, num_samples, 35)]
plot.getAxis('left').setTicks([yticks])

cmap = pg.colormap.get('viridis')
img.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256))

slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
slider.setMinimum(0)
slider.setMaximum(max(0, data.shape[0] - max_cols))
slider.setValue(0)

marker = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=1))
plot.addItem(marker)
label = pg.TextItem(color='r', anchor=(1, 1))
plot.addItem(label)

def update_marker_label():
    y_val = marker.value()
    label.setText(f"Y = {y_val:.2f} m")
    label.setPos(max_cols, y_val)

marker.sigPositionChanged.connect(update_marker_label)

def update_image():
    start = slider.value()
    end = start + max_cols
    if end > data.shape[0]:
        end = data.shape[0]
        start = max(0, end - max_cols)
    view_data = data[start:end]
    if view_data.shape[0] < max_cols:
        padding = np.zeros((max_cols - view_data.shape[0], num_samples))
        view_data = np.vstack((padding, view_data))
    img.setImage(view_data, autoLevels=False)
    img.setLevels([np.min(data), np.max(data)])
    img.setRect(QtCore.QRectF(0, 0, max_cols, num_samples * sample_resolution))
    update_marker_label()  
    
slider.valueChanged.connect(update_image)

layout.addWidget(graphics_layout)
layout.addWidget(slider)

main_win.setWindowTitle("Waterfall plot")
main_win.resize(1000, 500)
main_win.show()

marker.setValue(0.0)
update_image()

sys.exit(app.exec())
