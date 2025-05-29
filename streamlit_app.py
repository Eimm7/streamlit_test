import streamlit as st
import requests

# Set the app title 
st.title('Convert My Money App !!') 

# Add a welcome message 
st.write('Welcome, start convert your money NOW !!') 

# Create a text input 
widgetuser_input = st.text_input('Enter a custom message:', 'Hello, Streamlit!') 

# Display the customized message 
st.write('Customized Message:', widgetuser_input)

# API call
response = requests.get('https://api.vatcomply.com/rates?base=MYR')

if response.status_code == 200:
    data = response.json()
    rates = data.get("rates", {})

    # Create a dropdown to select target currency
    currency_list = sorted(rates.keys())
    selected_currency = st.selectbox("Choose a currency to convert MYR to:", currency_list)

    # Input amount in MYR
    amount_myr = st.number_input("Enter amount in MYR:", min_value=0.0, value=1.0, step=0.5)

    # Conversion
    if selected_currency in rates:
        converted_amount = amount_myr * rates[selected_currency]
        st.write(f"{amount_myr:.2f} MYR = {converted_amount:.2f} {selected_currency}")
    else:
        st.warning("Selected currency not found in rates.")

    # Optionally show all rates
    with st.expander("Show all exchange rates"):
        st.json(rates)
else:
    st.error(f"API call failed with status code: {response.status_code}")



