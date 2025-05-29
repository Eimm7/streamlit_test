import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(page_title="Convert My Money App", layout="centered")

# Title and subtitle
st.title('💱 Convert My Money App !!')
st.markdown('### Welcome, start converting your money NOW with style and ease!')

# Custom message widget
with st.expander("💬 Add a custom message"):
    widgetuser_input = st.text_input('Enter your message:', 'Hello, Streamlit!')
    st.info(f'You said: **{widgetuser_input}**')

# API call
response = requests.get('https://api.vatcomply.com/rates?base=MYR')

if response.status_code == 200:
    data = response.json()
    rates = data.get("rates", {})
    date = data.get("date")

    # Sidebar for input
    st.sidebar.header("Conversion Settings")
    currency_list = sorted(rates.keys())
    selected_currency = st.sidebar.selectbox("Choose currency to convert MYR to:", currency_list)
    amount_myr = st.sidebar.number_input("Enter amount in MYR:", min_value=0.0, value=100.0, step=1.0)

    # Perform conversion
    if selected_currency in rates:
        rate = rates[selected_currency]
        converted_amount = amount_myr * rate
        st.metric(label=f"💵 {amount_myr:.2f} MYR in {selected_currency}", value=f"{converted_amount:.2f} {selected_currency}", delta=f"Rate: {rate:.4f}")
    else:
        st.warning("Selected currency not found in rates.")

    # Show all rates in a table
    with st.expander("📊 View all exchange rates"):
        rates_df = pd.DataFrame(rates.items(), columns=["Currency", "Rate"])
        st.dataframe(rates_df.sort_values(by="Currency").reset_index(drop=True))

    # Plot a chart of top N exchange rates using native Streamlit chart
    with st.expander("📈 Visualize top 10 exchange rates"):
        top_rates_df = rates_df.sort_values(by="Rate", ascending=False).head(10).set_index("Currency")
        st.bar_chart(top_rates_df)

    # Footer with update time
    st.caption(f"Exchange rates last updated on: {date}")
else:
    st.error(f"API call failed with status code: {response.status_code}")



