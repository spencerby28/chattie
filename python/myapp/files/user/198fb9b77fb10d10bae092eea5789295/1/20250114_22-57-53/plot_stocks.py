# filename: plot_stocks.py
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

# Check if the current date is in 2023, if not, we will fetch the data up to the current date.
current_year = datetime.now().year
end_date = '2023-12-31' if current_year > 2023 else datetime.now().strftime('%Y-%m-%d')

# Fetch stock price data for NVDA and TESLA for 2023
nvda_data = yf.download('NVDA', start='2023-01-01', end=end_date)
tesla_data = yf.download('TSLA', start='2023-01-01', end=end_date)

# Plot the closing prices of NVDA and TESLA
plt.figure(figsize=(14, 7))
plt.plot(nvda_data['Close'], label='NVDA')
plt.plot(tesla_data['Close'], label='TESLA')

# Add title and labels
plt.title('NVDA and TESLA Stock Prices for 2023')
plt.xlabel('Date')
plt.ylabel('Stock Price (USD)')

# Add legend
plt.legend()

# Save the plot to a file
plt.savefig('nvda_tesla.png')
print('The chart has been saved as nvda_tesla.png')

# Show the plot
plt.show()