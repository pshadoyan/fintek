import pandas as pd
import streamlit as st
import os
from backtest import run_backtest
from streamlit.components.v1 import html

# Function to capture HTML plot from backtesting.py's plot()
def capture_plot_html(bt_obj, filename):
    bt_obj.plot(filename=filename, open_browser=False)
    with open(filename, 'r') as file:
        html_content = file.read()
    os.remove(filename)  # Optionally remove the file after reading
    return html_content

# Title for the app
st.title("Backtesting Results")

# Dropdown for selecting the strategy
strategy_options = ["PandasMeanReversionStrategy", "OtherStrategy1", "OtherStrategy2"]  # Add more strategies as needed
selected_strategy = st.selectbox("Select a Strategy", strategy_options)

# Button to initiate backtesting
if st.button('Run Backtest'):
    # Run backtest
    bt, stats = run_backtest(selected_strategy)

    if stats:
        df = pd.DataFrame(stats)
        df = df.sort_values(by='return', ascending=False)  # Sort by profit
        st.write('Backtesting Results Ranked by Profit:')
        st.dataframe(df)  # Display as a spreadsheet
        
    # Capture the plot as HTML
    html_content = capture_plot_html(bt, "temp_plot.html")

    # Display the HTML plot in Streamlit
    html(html_content, width=700, height=500)
else:
    st.write("Click the button to run the backtest.")
