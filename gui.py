import socket
import struct
import numpy as np
import csv
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

# Parametry UDP
UDP_IP = "0.0.0.0"
UDP_PORT = 5005

# Parametry wykresu
num_samples = 1000    # liczba próbek na ramkę
max_cols = 300        # liczba ramek na osi X wykresu
speed_of_sound = 340  # m/s
sample_time = 20e-6   # 20 us
sample_resolution = (speed_of_sound * sample_time) / 2

# Inicjalizacja danych
data = np.zeros((num_samples, max_cols), dtype=np.uint16)

# Inicjalizacja wykresu
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(title="Waterfall Live")
win.show()

win.addLabel("Waterfall Live - Sample Resolution: {:.2f} cm".format(sample_resolution * 100), col=0, colspan=1)

plot = win.addPlot()
img = pg.ImageItem()
plot.addItem(img)

plot.setLabel('bottom', 'Frame')
plot.setLabel('left', 'Distance (m)')

# Kolory i zakres
img.setLookupTable(pg.colormap.get('viridis').getLookupTable(0.0, 1.0, 256))
img.setLevels([0, 2000])

# Oś Y: odległości
yticks = [(i, f'{i * sample_resolution:.1f}') for i in range(0, num_samples, 35)]
plot.getAxis('left').setTicks([yticks])
plot.invertY(True)

# Inicjalizacja gniazda
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)
print(f"Listening on UDP port {UDP_PORT}...")

buffer = b""
recording = False

# CSV
csvfile = open("pomiar_adc.csv", "w", newline="")
writer = csv.writer(csvfile)

# Timer do aktualizacji
def update():
    global buffer, recording, data
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

                img.setImage(data.T, autoLevels=False)

            elif recording:
                buffer += data_in

    except BlockingIOError:
        pass

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(30)

# Zamknięcie
def close_event():
    csvfile.close()
    sock.close()
    print("Socket i plik CSV zamknięte.")

app.aboutToQuit.connect(close_event)

# Start aplikacji
QtWidgets.QApplication.instance().exec_()