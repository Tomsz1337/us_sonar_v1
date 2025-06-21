import socket

UDP_IP = "0.0.0.0"      # nasłuchuj na wszystkich interfejsach
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"Listening on UDP port {UDP_PORT}...")
while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received from {addr}: {data.decode(errors='ignore')}")
