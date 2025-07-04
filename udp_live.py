import socket
import struct
import numpy as np
import matplotlib.pyplot as plt
import csv

# Parametry UDP
UDP_IP = "0.0.0.0"     # nasłuchiwanie na wszystkich interfejsach
UDP_PORT = 5005        # port zgodny z Pico W

# Parametry wykresu
num_samples = 1000
max_cols = 150
speed_of_sound = 340
sample_time = 20e-6
sample_resolution = (speed_of_sound * sample_time * 100) / 2  # cm

# Inicjalizacja danych
data = np.zeros((num_samples, max_cols))

# Konfiguracja wykresu
plt.ion()
fig, ax = plt.subplots()
im = ax.imshow(data, aspect='auto', cmap='viridis', vmin=0, vmax=2000)
plt.colorbar(im, ax=ax)

ax.invert_yaxis()
tick_step = 50
ax.set_yticks(np.arange(0, num_samples, tick_step)[::-1])
ax.set_yticklabels([f'{dist:.2f}' for dist in np.arange(0, num_samples, tick_step)[::-1] * sample_resolution])
ax.set_xlabel('Elapsed Time (frames)')
ax.set_ylabel('Distance (cm)')

# Inicjalizacja gniazda
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
print(f"Listening for UDP packets on port {UDP_PORT}...")

buffer = b""
recording = False

# Otwórz plik CSV do zapisu
with open("pomiar_adc.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    try:
        while True:
            data_in, addr = sock.recvfrom(2048)

            if data_in.startswith(b"sp\n"):
                buffer = b""
                recording = True
                continue

            if data_in.endswith(b"\n") and recording:
                buffer += data_in[:-1]  # usuń końcowy \n
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

                # Aktualizacja wykresu
                frame = np.array(samples)
                data = np.roll(data, -1, axis=1)
                data[:, -1] = frame

                im.set_data(data)
                ax.set_title(f'Waterfall Live\nSample Resolution: {sample_resolution:.2f} cm')
                fig.canvas.draw()
                fig.canvas.flush_events()

            elif recording:
                buffer += data_in

    except KeyboardInterrupt:
        print("Zakończono przez użytkownika.")

    finally:
        sock.close()
        print("Socket zamknięty.")
