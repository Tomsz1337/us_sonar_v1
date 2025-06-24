import socket
import struct
import csv

UDP_IP = "0.0.0.0"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP port {UDP_PORT}...")

buffer = b""
recording = False

# Tryb zapisu do CSV z płaskim formatem danych (zgodnym z matplotlib)
with open("pomiar_adc.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)

    while True:
        data, addr = sock.recvfrom(2048)

        # Start
        if data.startswith(b"sp\n"):
            print("Start of frame")
            buffer = b""
            recording = True

        # Koniec
        elif data.endswith(b"\n") and recording:
            print("End of frame")
            buffer += data[:-1]  # usuń końcowy \n
            num_samples = len(buffer) // 2
            samples = struct.unpack(f"<{num_samples}H", buffer)
            writer.writerow(samples)
            csvfile.flush()
            print(f"Wrote {num_samples} samples")
            buffer = b""
            recording = False

        # Środek
        elif recording:
            buffer += data
