# filename: plot_sine_wave.py
import matplotlib.pyplot as plt
import numpy as np

# Generate a sequence of x values from 0 to 2 * pi
x = np.linspace(0, 2 * np.pi, 1000)

# Calculate the sine of x
y = np.sin(x)

# Create the plot
plt.figure(figsize=(10, 5))
plt.plot(x, y)

# Title and labels
plt.title('Sine Wave')
plt.xlabel('Radians')
plt.ylabel('Amplitude')

# Save the plot as a PNG file
plt.savefig('sine_wave.png')

print('Sine wave plot saved as sine_wave.png')