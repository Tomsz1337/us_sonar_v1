import csv
import matplotlib.pyplot as plt
import numpy as np
#from scipy.signal import butter, filtfilt

row_index = 2000
result = None


with open("max_depth.csv", newline="") as f:
    reader = csv.reader(f)
    
    for i, row in enumerate(reader):
        if i == row_index:
            result = [float(x) *3.3 / 4096 for x in row]
            break

data = np.array(result, dtype=float)
x = np.arange(len(data)) * 0.02

plt.plot(x,data, '-')
plt.xlabel("Time [ms]")
plt.ylabel("Amplitude [V]")
plt.grid(True)
plt.show()
#print(rows)