
# FullTradeReporter Readme

## Overview

FullTradeReporter is a tool designed to parse and analyze trading performance data exported from NinjaTrader. Follow the steps below to export your trading data from NinjaTrader, save it in the appropriate directory, and run the analysis script.

## Prerequisites

-   NinjaTrader installed
-   Python 3.x installed

## Steps to Export Data from NinjaTrader

1.  **Open Trade Performance:**
    
    -   Go to `New` -> `Trade Performance`.
2.  **Adjust the Summary View:**
    
    -   Under the `Summary` tab, switch to `Trades`.
3.  **Modify Properties:**
    
    -   Right-click in the middle of the window and select `Properties`.
    -   Change `PnL` to `Points` if it's not already set to this.
4.  **Export Data:**
    
    -   Right-click again and choose `Export as .csv`.
    -   Ensure the file format is `.csv` and not `.xlsx`.
    -   Save the `.csv` file in the following directory:
        
        bash
        
        Copy code
        
        `fulltradereporter/parser/NinjaTrader/data/TradingPerformance` 
        

## Running the Analysis Script

1.  Open a terminal or command prompt.
2.  Navigate to the project directory where `main.py` is located.
3.  Run the following command:
    
    arduino
    
    Copy code
    
    `python run main.py` 
    

## Additional Information

-   Ensure that the `.csv` file exported from NinjaTrader is correctly placed in the `data/TradingPerformance` directory before running the script.
-   If you encounter any issues, verify the directory structure and file format.
