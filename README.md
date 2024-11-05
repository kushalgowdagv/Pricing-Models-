# Option Pricing and Strategy Simulation - README

## Project Overview
This project is designed to provide an interactive web application for option pricing, option Greek visualization, and asset price simulation. The platform leverages various option pricing models, including Black-Scholes, Monte Carlo Simulation, and Binomial Tree methods, to simulate and price financial derivatives like options. 

The application also provides a dynamic and interactive visualization of option Greeks, enabling users to understand how key parameters like Delta, Gamma, Theta, Vega, and others evolve with respect to changes in underlying asset prices.

## Key Features
1. **Option Pricing Models**:
   - **Black-Scholes Model**: Calculate the price of European call and put options using the Black-Scholes formula.
   - **Monte Carlo Simulation**: Simulate multiple asset price paths to estimate option prices through the Monte Carlo method.
   - **Binomial Tree Model**: Provides pricing for American and European options using a binomial tree structure.

2. **Greeks Visualization**:
   - Visualize key option Greeks such as Delta, Gamma, Theta, Vega, Rho, and secondary Greeks (Vanna, Vomma, Charm, Zomma).
   - Plot how these Greeks vary with changes in the underlying asset price, offering insight into an option’s risk sensitivity.

3. **Simulation of Asset Prices**:
   - Perform Monte Carlo simulations for asset price paths over time.
   - Visualize potential future asset price movements under different assumptions about volatility and risk-free rates.

4. **Binomial Option Pricing Visualization**:
   - Visualize a binomial tree representing asset price evolution over time.
   - Plot potential option values at different nodes of the binomial tree to understand the payoff evolution.

5. **User-friendly Interface**:
   - Built with Streamlit, offering a sidebar for parameter selection and real-time updates to calculations and visualizations.

## Prerequisites

To run the project, you will need:

1. Python 3.x installed
2. Required libraries, which can be installed via `pip`:
    ```bash
    pip install numpy pandas plotly yfinance streamlit scipy
    ```

## How to Run the Project

1. Clone this repository:
    ```bash
    git clone https://github.com/your-repo/option-pricing-simulation.git
    ```

2. Navigate to the project directory:
    ```bash
    cd option-pricing-simulation
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

5. Access the web application in your browser via the URL provided by Streamlit.

## File Structure
- `app.py`: The main application file containing the Streamlit-based interface and all the logic for option pricing and visualizations.
- `black_scholes.py`: Contains the `BlackScholes` class that handles option pricing using the Black-Scholes model, calculates Greeks, and performs visualizations.
- `monte_carlo.py`: Implements Monte Carlo simulations for asset price evolution and option pricing.
- `binomial_tree.py`: Contains the code for binomial tree pricing and visualizations.
- `requirements.txt`: Lists the required dependencies for the project.

## Instructions for Use

1. **Selecting an Asset**: In the sidebar, select an underlying asset (e.g., Apple, Tesla) from the dropdown menu.
   
2. **Choose Expiration Date**: Choose an expiration date for the options contract.

3. **Strike Price**: The system automatically fetches the current price of the selected asset and the strike prices available. Select the strike price that is closest to the spot price of the underlying asset.

4. **Choose Option Pricing Model**: Select the desired pricing model (Black-Scholes, Monte Carlo, or Binomial Tree) to price the option.

5. **Visualizing Greeks**: For the Black-Scholes model, you can visualize the Greeks for the selected option by hitting the "Run" button.

6. **Simulating Asset Prices**: If Monte Carlo Simulation is selected, the system will simulate potential future price paths of the asset and display the results.

7. **Binomial Tree**: For American options, the binomial tree provides step-by-step asset price evolution, helping you understand the decision-making process for early exercise.

## Future Enhancements

This platform can be further expanded to support more advanced financial strategies and arbitrage opportunities. Some potential enhancements include:

1. **Option Strategies**:
   - The system can be extended to create popular multi-leg option strategies like straddles, strangles, and butterflies.
   - Implementing P&L visualizations for these strategies based on user-selected parameters.

2. **Butterfly Arbitrage Opportunities**:
   - Incorporating a module to identify butterfly arbitrage opportunities based on discrepancies in option prices and volatility.

3. **Volatility Term Structure**:
   - Visualize the volatility term structure and explore how changing market conditions affect volatility and option prices.
   - Use this information to identify arbitrage opportunities, especially in multi-leg option trades.

4. **Implied Volatility Calculation**:
   - Implement an implied volatility calculator that can reverse engineer the volatility implied by observed market prices for options.

5. **Sensitivity Analysis**:
   - Add more detailed sensitivity analysis for option prices and Greeks based on various input parameters like volatility and interest rates.

## Contact

For further questions or contributions, please reach out to the project owner or visit the [LinkedIn](https://www.linkedin.com/in/kushalgowdagv/) page of the developer.

