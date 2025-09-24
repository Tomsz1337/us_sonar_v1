import socket
import struct
import numpy as np
import csv
import os
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore, QtWidgets

# Parametry UDP
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# Parametry wykresu
num_samples = 1000    # liczba próbek na ramkę
max_cols = 300        # liczba ramek na osi X wykresu
speed_of_sound = 340  # m/s
offset = 0e-6
sample_time = 20e-6 + offset  # 20 us
sample_resolution = (speed_of_sound * sample_time) / 2

# Inicjalizacja danych
data = np.zeros((num_samples, max_cols), dtype=np.uint16)

# Inicjalizacja wykresu
app = QtWidgets.QApplication([])
main_widget = QtWidgets.QWidget()
main_layout = QtWidgets.QHBoxLayout()
main_widget.setLayout(main_layout)
win = pg.GraphicsLayoutWidget(title="Waterfall Live")
main_layout.addWidget(win)

win.addLabel("Waterfall Live - Sample Resolution: {:.2f} cm".format(sample_resolution * 100), col=0, colspan=1)

plot = win.addPlot()
img = pg.ImageItem()
plot.addItem(img)

plot.setLabel('bottom', 'Time (Frames)')
plot.setLabel('left', 'Distance (m)')

# Kolory i zakres
img.setLookupTable(pg.colormap.get('viridis').getLookupTable(0.0, 1.0, 256))
img.setLevels([0, 2000])

# Oś Y: odległości
yticks = [(i, f'{i * sample_resolution:.1f}') for i in range(0, num_samples, 35)]
plot.getAxis('left').setTicks([yticks])
plot.invertY(True)

# slider
slider_y = QtWidgets.QSlider(QtCore.Qt.Vertical)
slider_y.setMinimum(10)
slider_y.setMaximum(num_samples)
slider_y.setValue(num_samples)

# marker
def update_marker_label():
    y_idx = marker.value()
    y_meters = y_idx * sample_resolution
    label.setText(f"Y = {y_meters:.2f} m")
    label.setPos(max_cols, y_idx)


marker = pg.InfiniteLine(angle=0, movable=True, pen=pg.mkPen('r', width=1))
label = pg.TextItem(color='r', anchor=(1, 1))
plot.addItem(marker)
plot.addItem(label)
marker.sigPositionChanged.connect(update_marker_label)

# przycisk do zapisu png
save_button = QtWidgets.QPushButton("Save PNG")

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

# Inicjalizacja gniazda
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)
print(f"Listening on UDP port {UDP_PORT}...")

buffer = b""
recording = False

# CSV
def csv_filename():
    base_name = "recorded_data"
    ext = ".csv"
    i = 1

    while True:
        filename = f"{base_name}_{i:03d}{ext}"
        if not os.path.exists(filename):
            break
        i += 1
    return filename

csvfile = open(csv_filename(), "w", newline="")
writer = csv.writer(csvfile)

# aktualizacja obrazu
def update():
    global buffer, recording, data
    visible_samples = slider_y.value()

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
                if num_samples_recv != num_samples:
                    print(f"Warning: expected {num_samples}, got {num_samples_recv}")
                    continue

                samples = struct.unpack(f"<{num_samples}H", buffer)

                # Zapis do CSV
                writer.writerow(samples)
                csvfile.flush()
                print(f"Wrote {num_samples_recv} samples to CSV")

                # Aktualizacja danych
                frame = np.array(samples, dtype=np.uint16)
                data = np.roll(data, -1, axis=1)
                data[:, -1] = frame
                
                view_data = data.T[:, :visible_samples]
                img.setImage(view_data, autoLevels=False)
                update_marker_label()

            elif recording:
                buffer += data_in
            
    except BlockingIOError:
        pass

marker.setValue(0.0)
slider_y.valueChanged.connect(update)
save_button.clicked.connect(save_image)
main_layout.addWidget(slider_y)
main_layout.addWidget(save_button)
main_widget.show()

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(30)

# Zamknięcie
def close_event():
    csvfile.close()
    sock.close()
    print("Socket and CSV file closed.")

app.aboutToQuit.connect(close_event)

# Start aplikacji
QtWidgets.QApplication.instance().exec_()