import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
import plotly.graph_objs as go
import seaborn as sns
from scipy.stats import norm
import requests
import re
import streamlit as st
import yfinance as yf

class BlackScholes:
    def __init__(self, r, s, k, t, sigma):
        self.r = r          # Risk-free rate
        self.k = k          # Strike price
        self.s = s          # Stock price
        self.t = t          # Time to expiration
        self.sigma = sigma  # Volatility

    def calculate_df(self):
        try:
            d1 = (np.log(self.s / self.k) + (self.r + 0.5 * self.sigma**2) * self.t) / (self.sigma * np.sqrt(self.t))
            d2 = d1 - self.sigma * np.sqrt(self.t)
            return d1, d2
        except ZeroDivisionError:
            raise ValueError("Enter time value greater than 0")

    def option(self, option_type='Call'):
        d1, d2 = self.calculate_df()
        option_type = option_type.capitalize()
        try:
            if option_type == "Call":
                price = (self.s * norm.cdf(d1)) - (self.k * np.exp(-self.r * self.t) * norm.cdf(d2))
            elif option_type == "Put":
                price = (self.k * np.exp(-self.r * self.t) * norm.cdf(-d2)) - (self.s * norm.cdf(-d1))
            else:
                raise ValueError('Invalid input. Please enter "Call" or "Put"')

            return round(price, 2)
        except Exception as e:
            raise RuntimeError(f"Error calculating option price: {e}")

    def greeks(self, option_type):
        d1, d2 = self.calculate_df()
    
        try:
            pdf_d1 = norm.pdf(d1)
            cdf_d1 = norm.cdf(d1)
            cdf_neg_d1 = norm.cdf(-d1)
            cdf_d2 = norm.cdf(d2)
            cdf_neg_d2 = norm.cdf(-d2)
            sqrt_T = np.sqrt(self.t)
            exp_neg_rt = np.exp(-self.r * self.t)

            gamma = pdf_d1 / (self.s * self.sigma * sqrt_T)
            vega = self.s * pdf_d1 * sqrt_T 
            if option_type == "Call":
                delta = cdf_d1
                theta = (-self.s * pdf_d1 * self.sigma / (2 * sqrt_T)) - (self.r * self.k * exp_neg_rt * cdf_d2)
                rho = self.k * self.t * exp_neg_rt * cdf_d2
            elif option_type == "Put":
                delta = -cdf_neg_d1
                theta = (-self.s * pdf_d1 * self.sigma / (2 * sqrt_T)) + (self.r * self.k * exp_neg_rt * cdf_neg_d2)
                rho = -self.k * self.t * exp_neg_rt * cdf_neg_d2
            else:
                raise ValueError("Invalid option type. Must be 'Call' or 'Put'.")
        
            return {
                'delta': round(delta, 3),
                'gamma': round(gamma, 6),
                'theta': round(theta / 365, 6),  # Convert theta to per-day format
                'vega': round(vega * 0.01, 6),  # Vega is multiplied by 0.01 to adjust for percentage format
                'rho': round(rho * 0.01, 6)     # Rho in percentage format
            }

        except ZeroDivisionError:
            return "Error: Division by zero encountered in Greek calculations."
        except ValueError as e:
            return f"Error: {e}"

    def greek_visualisation(self, option_type, greek):
        fig = go.Figure()
    
        line_color = '#FA7070' if option_type == 'Call' else '#799351'
        min_s = self.s * 0.92
        max_s = self.s * 1.09
        spot_values = np.linspace(min_s, max_s, 200)

        greek_values = [BlackScholes(self.r, s, self.k, self.t, self.sigma).greeks(option_type)[greek] for s in spot_values]
        current_greek_value = BlackScholes(self.r, self.s, self.k, self.t, self.sigma).greeks(option_type)[greek]
        fig.add_trace(go.Scatter(x=spot_values, y=greek_values, mode='lines', name=greek.capitalize(), line=dict(color=line_color, width=3)))
        fig.add_trace(go.Scatter(x=[self.s], y=[current_greek_value], mode='markers', name=f'Current {greek.capitalize()}', marker=dict(color='black', size=7)))
        fig.update_layout(title=f'{greek.capitalize()} vs Spot Price ({option_type})', xaxis_title='Spot Price', yaxis_title=greek.capitalize())
        
        return fig

    def monte_carlo_pricing(self, num_simulations=10000):
        Z = np.random.standard_normal(num_simulations)
        ST = self.s * np.exp((self.r - 0.5 * self.sigma**2) * self.t + self.sigma * np.sqrt(self.t) * Z)
        payoffs = np.maximum(ST - self.k, 0)  # Call options
        option_price = np.exp(-self.r * self.t) * np.mean(payoffs)
        return option_price

    def american_option_pricing(self, s, k, t, r, n, sigma, option_type='call'):
        n = int(n)
        dt = t / n
        u = np.exp(sigma * np.sqrt(dt)) 
        d = 1 / u                       
        p = (np.exp(r * dt) - d) / (u - d)  

        stock_price = np.zeros((n + 1, n + 1))
        option_value = np.zeros((n + 1, n + 1))

        for i in range(n + 1):
            stock_price[i, n] = s * (u ** i) * (d ** (n - i))

        if option_type == 'call':
            for i in range(n + 1):
                option_value[i, n] = max(0, stock_price[i, n] - k)
        elif option_type == 'put':
            for i in range(n + 1):
                option_value[i, n] = max(0, k - stock_price[i, n])
        else:
            raise ValueError("option_type should be 'call' or 'put'")
    
        for j in range(n - 1, -1, -1):
            for i in range(j + 1):
                option_value[i, j] = np.exp(-r * dt) * (p * option_value[i, j + 1] + (1 - p) * option_value[i + 1, j + 1])
           
                if option_type == 'call':
                    option_value[i, j] = max(option_value[i, j], stock_price[i, j] - k)
                elif option_type == 'put':
                    option_value[i, j] = max(option_value[i, j], k - stock_price[i, j])
            
                stock_price[i, j] = stock_price[i, j + 1] * d

        return option_value[0, 0]



def monte_carlo_pricing_visualization(option_value, strike_price, time_to_expiry, volatility, risk_free_rate, num_simulations=1000, num_steps=252):
    dt = time_to_expiry / num_steps
    asset_paths = np.zeros((num_steps, num_simulations))
    asset_paths[0] = option_value

    for t in range(1, num_steps):
        rand = np.random.standard_normal(num_simulations)
        asset_paths[t] = asset_paths[t - 1] * np.exp((risk_free_rate - 0.5 * volatility ** 2) * dt + volatility * np.sqrt(dt) * rand)

    fig = go.Figure()
    
    for i in range(num_simulations):
        fig.add_trace(go.Scatter(x=np.linspace(0, time_to_expiry, num_steps), y=asset_paths[:, i], mode='lines', line=dict(width=1)))
    
    fig.update_layout(title="Asset Price Paths", xaxis_title="Time (Years)", yaxis_title="Asset Price", showlegend=False)

    return fig


def binomial_pricing_visualization(spot_price, strike_price, time_to_expiry, volatility, risk_free_rate, num_steps, option_type='Call'):
    dt = time_to_expiry / num_steps  
    u = np.exp(volatility * np.sqrt(dt))
    d = 1 / u 
    p = (np.exp(risk_free_rate * dt) - d) / (u - d)  

    asset_prices = np.zeros((num_steps + 1, num_steps + 1))

    for i in range(num_steps + 1):
        for j in range(i + 1):
            asset_prices[j, i] = spot_price * (u ** (i - j)) * (d ** j)

    fig = go.Figure()

    for i in range(num_steps + 1):
        for j in range(i + 1):
            fig.add_trace(go.Scatter(x=[i], y=[asset_prices[j, i]],mode='markers+text',marker=dict(size=10, color='blue'),text=f"{asset_prices[j, i]:.2f}",textposition='top center',showlegend=False))

    for i in range(num_steps):
        for j in range(i + 1):
            fig.add_trace(go.Scatter(x=[i, i + 1], y=[asset_prices[j, i], asset_prices[j, i + 1]],mode='lines', line=dict(color='gray', dash='dash'),showlegend=False))
            fig.add_trace(go.Scatter(x=[i, i + 1], y=[asset_prices[j, i], asset_prices[j + 1, i + 1]],mode='lines', line=dict(color='gray', dash='dash'),showlegend=False))
    fig.update_layout(title=f"Binomial Tree for {option_type} Option Pricing",xaxis_title="Step",yaxis_title="Asset Price",xaxis=dict(tickmode='linear', tick0=0, dtick=1),yaxis=dict(tickmode='linear'),showlegend=False,height=600,width=800)
 
    return fig

def fetch_data(selected_index):
    try:
        nifty_latest = yf.download(selected_index, interval = '1m', period = '1d')
        nifty_latest = round(nifty_latest.Close.iloc[-1], 1)
        return nifty_latest
    except:
        return 25000.0 
    
def fetch_expiry_dates(selected_index):
    """Fetches expiry dates for the selected index if available."""
    try:
        ticker = yf.Ticker(selected_index)
        options = ticker.options
        if options:
            return options
        else:
            return ["No options available"]
    except Exception as e:
        st.sidebar.write(f"Error fetching options for {selected_index}: {e}")
        return ["Error fetching options"]

def calculate_time_to_expiry(expiration_date):
    """Calculates time to expiry in years from today's date to the expiration date."""
    today = datetime.now().date()
    expiry_date = datetime.strptime(expiration_date, "%Y-%m-%d").date()
    days_to_expiry = (expiry_date - today).days
    return days_to_expiry / 365.0

def main():
    indices_names = {'AAPL': 'Apple Inc.', 'NVDA': 'NVIDIA Corporation', '^RUT': 'Russell 2000 Index', '^VIX': 'CBOE Volatility Index (VIX)',
        'IWM': 'iShares Russell 2000 ETF', 'TSLA': 'Tesla, Inc.', 'QQQ': 'Invesco QQQ Trust', '^SPX': 'S&P 500 Index'}

    st.sidebar.header("Select an Index")
    selected_index = st.sidebar.selectbox(
        "Select an underlying asset", 
        options=list(indices_names.keys()), 
        key='underlying_asset'
    )
    st.sidebar.write(f"Selected asset: **{indices_names[selected_index]}**")

    # Fetching and displaying available expirations for the selected index
    expirations = fetch_expiry_dates(selected_index)
    expiration_date = st.sidebar.selectbox(
        "Select Expiration Date", 
        options=expirations, 
        key='expiration_date'
    )
    
    st.sidebar.write(f"Selected expiration: **{expiration_date}**")

    # Fetching the current price for the selected index
    nifty_price = fetch_data(selected_index)

    # selected_index = st.sidebar.selectbox("Select an underlying asset", options=list(indices_names.keys()), key='underlying_asset')
    # st.sidebar.write(f"Selected asset: **{indices_names[selected_index]}**")

    # # Fetching the current price for the selected index
    # spot_price = yf.download(selected_index, interval='1d', period='1d')['Close'].iloc[-1]

    # nifty_price = fetch_data(selected_index)

    strike_price = 25000.0
    time_to_expiry = calculate_time_to_expiry(expiration_date)
    option_type = 'Call'
    spot_price = nifty_price
    volatility = 20.0
    risk_free_rate = 5.0
    num_steps=10.0

    option = st.sidebar.selectbox("Pick a strategy", ['Black Scholes Pricing', 'Monte Carlo Simulation', 'Binomial Tree Forecasting'], key='option_strategy')

    if option == 'Black Scholes Pricing':
        st.title("Black-Scholes Option Pricing and Greek Visualizations")
        st.sidebar.header("Inputs")
        spot_price = st.sidebar.number_input('Stock Price', min_value=1.0, max_value=40000.0, value=nifty_price, step=5.0, key='spot_price')
        strike_price = st.sidebar.number_input("Strike Price", value=25000.0, min_value=1.0, max_value=40000.0, key='strike_price')
        time_to_expiry = st.sidebar.number_input("Time to Expiry (Years)", value=1.0, key='time_to_expiry')
        option_type = st.selectbox("Option Type", ['Call', 'Put'], key='option_type')
        volatility = st.sidebar.number_input('Volatility (%)', min_value=1.0, max_value=100.0, value=20.0, step=0.25, key='volatility')
        risk_free_rate = st.sidebar.number_input('Risk Free Rate (%)', min_value=0.0, max_value=20.0, value=5.0, step=0.01, key='risk_free_rate')
        
        st.sidebar.header("Inputs for Black Scholes")
        bs_model = BlackScholes(r=risk_free_rate / 100, s=spot_price, k=strike_price, t=time_to_expiry, sigma=volatility / 100)
        option_price = bs_model.option(option_type)
        
        st.subheader("Greek Visualizations")

        if st.sidebar.button("Run"): 
            st.sidebar.write(f"Option Price: {option_price}")
            greek_types = ['delta', 'gamma', 'theta', 'vega', 'rho']
            for greek in greek_types:
                fig = bs_model.greek_visualisation(option_type, greek)
                st.plotly_chart(fig)

    elif option == 'Monte Carlo Simulation':
        st.title("Monte Carlo Simulation Option Pricing and Simulating Asset prices")
        st.sidebar.header("Inputs")
        num_steps = st.sidebar.number_input("Number of Steps", value=252, min_value=1, key='num_steps_mc')
        num_simulations = st.sidebar.number_input("Number of Simulations", value=1000, min_value=500, max_value=2000, step=100, key='num_simulations')
        spot_price = st.sidebar.number_input('Stock Price', min_value=1.0, max_value=40000.0, value=nifty_price, step=5.0, key='spot_price')
        strike_price = st.sidebar.number_input("Strike Price", value=25000.0, min_value=1.0, max_value=40000.0, key='strike_price')
        time_to_expiry = st.sidebar.number_input("Time to Expiry (Years)", value=1.0, key='time_to_expiry')
        volatility = st.sidebar.number_input('Volatility (%)', min_value=1.0, max_value=100.0, value=20.0, step=0.25, key='volatility')
        risk_free_rate = st.sidebar.number_input('Risk Free Rate (%)', min_value=0.0, max_value=20.0, value=5.0, step=0.01, key='risk_free_rate')
        
        bs_model = BlackScholes(r=risk_free_rate / 100, s=spot_price, k=strike_price, t=time_to_expiry, sigma=volatility / 100)
        monte_carlo_price = bs_model.monte_carlo_pricing(num_simulations=int(num_simulations))
        if st.sidebar.button("Run"):
            st.sidebar.write(f"Monte Carlo Option Price: {monte_carlo_price}")
            simulation_fig = monte_carlo_pricing_visualization(spot_price, strike_price, time_to_expiry, volatility / 100, risk_free_rate / 100, num_simulations, int(num_steps))
            st.plotly_chart(simulation_fig)
            
    else:
        st.sidebar.header("Inputs")
        st.title("Binomial Option Pricing and Forecasting Asset Prices")

        option_type = st.selectbox("Option Type", ['Call', 'Put'], key='option_type')
        spot_price = st.sidebar.number_input("Stock Price", min_value=0.0, max_value=40000.0, value=24975.0, step=5.0)
        strike_price = st.sidebar.number_input("Strike Price", value=25000.0, min_value=1.0, max_value=40000.0, key='strike_price')
        time_to_expiry = st.sidebar.number_input("Time to Expiry (Years)", min_value=0.01, max_value=1.0, value=1.0, step=0.01)
        volatility = st.sidebar.number_input("Volatility (%)", min_value=0.0, max_value=100.0, value=20.0) / 100
        risk_free_rate = st.sidebar.number_input("Risk Free Rate (%)", min_value=0.0, max_value=20.0, value=5.0) / 100
        num_steps = st.sidebar.number_input("Number of Steps", value=10, min_value=10, max_value=50, step=10)

        bs = BlackScholes(risk_free_rate, spot_price, strike_price, time_to_expiry, volatility)

        option_price = bs.american_option_pricing(spot_price, strike_price, time_to_expiry, risk_free_rate, num_steps, volatility, option_type.lower())

        if st.sidebar.button('Run'):
            st.sidebar.write(f"The calculated option value is: **{option_price:.2f}**")
            binomial_tree_fig = binomial_pricing_visualization(spot_price, strike_price, time_to_expiry, volatility, risk_free_rate, num_steps, option_type)
            st.plotly_chart(binomial_tree_fig)

if __name__ == "__main__":
    main()

st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")
st.sidebar.text("")
col1, col2 = st.sidebar.columns(2)
col1.text("Linkedin:")
col1.page_link("https://www.linkedin.com/in/kushalgowdagv/",label="Kushal Gowda G V")
