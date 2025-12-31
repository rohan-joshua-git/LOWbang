# IMPORTS
import streamlit as st
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from math import sqrt

################################################

def get_iv(ticker):
    ticker_website = f"https://optioncharts.io/options/{ticker}"
    driver = webdriver.Chrome()
    driver.get(ticker_website)

    implied_vol = None

    try:
        # Scrape for IV
        iv_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "highcharts-text-outline"))
        )
        # Clean the text before converting to float
        implied_vol_text = iv_element.text.replace('%', '').strip("IV")
        implied_vol = float(implied_vol_text)

    except ValueError as e:
        st.write("Could not convert implied volatility to a float.")
        st.write(f"Error: {e}")
        
    except Exception as e:
        st.write("Could not retrieve implied volatility.")
        st.write(f"Error: {e}")
        
    finally:
        driver.quit()

    return implied_vol

# Get Intrinsic Value
def get_intrinsic_value(ticker):
    ticker_website = f"https://www.alphaspread.com/security/nyse/{ticker}/summary"
    driver = webdriver.Chrome()
    driver.get(ticker_website)

    intrinsic_value = None

    try:
        # Wait for the body of the page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Use a CSS selector to scrape for Intrinsic Value
        intrinsic_value_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".ui.intrinsic-value-color.no-margin.valuation-scenario-value.header.restriction-sensitive-data"))
        )
        
        # Extract and clean the text
        intrinsic_value_text = intrinsic_value_element.text.strip("USD").replace('"', '').strip()
        
        if not intrinsic_value_text:
            st.write("Intrinsic value element is empty.")
            return None
        
        intrinsic_value = float(intrinsic_value_text)

    except ValueError as e:
        st.write("Could not convert intrinsic value to a float.")
        st.write(f"Error: {e}")
        st.write(f"Element text was: '{intrinsic_value_text}'") 
        
    except Exception as e:
        st.write("Could not retrieve intrinsic value.")
        st.write(f"Error: {e}")
        
    finally:
        driver.quit()

    return intrinsic_value

#Get previous close
def get_previous_close(ticker):
    ticker_website = f"https://sg.finance.yahoo.com/quote/{ticker}/"
    driver = webdriver.Chrome()
    driver.get(ticker_website)

    previous_close = None

    try:
        # Wait for the body of the page to load
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Use a CSS selector to scrape for previous close
        previous_close_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "fin-streamer[data-field='regularMarketPreviousClose']"))
        )
        
        # Extract and clean the text
        previous_close_text = previous_close_element.text.strip()
        
        if not previous_close_text:
            st.write("Previous close element is empty.")
            return None
        
        previous_close = float(previous_close_text.replace(',', ''))

    except ValueError as e:
        st.write("Could not convert previous close to a float.")
        st.write(f"Error: {e}")
        st.write(f"Element text was: '{previous_close}'")  # Debugging output
        
    except Exception as e:
        st.write("Could not retrieve previous close.")
        st.write(f"Error: {e}")
        
    finally:
        driver.quit()

    return previous_close
    
## MAIN
st.title("Welcome to Lowbang!")
ticker = st.text_input("Enter the ticker symbol of the stock you would like to analyse:")
validity = r"^[A-Z]{1,5}(-[A-Z]{1,2})?$"

# Check ticker validity + logic flow
if st.button("Analyse Stock"):
    if re.match(validity, ticker):
        st.write("Ticker is valid. Continuing to scrape website...")
        
        # Fetch Implied Volatility
        implied_volatility = get_iv(ticker)
        if implied_volatility is not None:
            st.write(f"The 30-Day implied volatility for {ticker} is {implied_volatility}%")
            implied_volatility = implied_volatility / 100    
        else:
            st.write("Implied volatility could not be retrieved.")
        
        # Fetch Intrinsic Value
        intrinsic_value = get_intrinsic_value(ticker)
        if intrinsic_value is not None:
            st.write(f"The Intrinsic Value for {ticker} is ${intrinsic_value: .2f}")
        else:
            st.write("Intrinsic Value could not be retrieved.")
            
        #Get previous close
        previous_close = get_previous_close(ticker) 
        if previous_close is not None:
            st.write(f"The Previous Close for {ticker} is ${previous_close}")
        else:
            st.write("Previous Close could not be retrieved.")
            
        margin_of_safety_price = intrinsic_value * 0.8
        adjusted_price = margin_of_safety_price - (intrinsic_value * implied_volatility * 0.5)
        daily_implied_volatility = implied_volatility / (sqrt(30))
        lower_bound_volatility = previous_close * (1 - daily_implied_volatility)
        upper_bound_volatility = previous_close * (1 + daily_implied_volatility)

        # Calculate the entry range based on intrinsic value
        margin_of_safety_price = intrinsic_value * 0.8
        adjusted_price = margin_of_safety_price - (intrinsic_value * (daily_implied_volatility * 0.5))

        # Present both ranges
        # Present both ranges without unnecessary whitespace
        st.write(f"Entry target range within the next 30 days based on daily volatility would be from: ${lower_bound_volatility:.2f} to ${upper_bound_volatility:.2f}")
        st.write(f"Entry target range within the next 30 days based on intrinsic value would be from: ${adjusted_price:.2f} to ${margin_of_safety_price:.2f}")


        # Suggest a realistic entry price considering both methods
        realistic_entry_price = min(upper_bound_volatility, margin_of_safety_price) * 1.35 
        st.write(f"A suggested realistic entry price if a market correction were to happen could be around: ${realistic_entry_price:.2f} or lower.")

    else:
        st.write("Ticker symbol does not seem valid. Try again.")

#Reflections
#1. Better UI 
#2. Calculate myself Vs trust third party
#3. Limitation - Caclulations done for the volatility entry range done using prev close not current
#4. Assumption - margin of safety always assumed to be 20%, entry price considering both methods use 115%, adjusted price 0.5 --> By applying the 0.5 factor, you reduce 
# the effect of volatility on your calculations, which can help avoid overly aggressive price targets. This is particularly important for investment strategies that emphasize safety 
# and risk management, such as value investing. Markets are not perfectly efficient, and stock prices do not move in a straight line. By halving the impact of implied volatility, you’re accounting for the fact that while prices may fluctuate, 
# these fluctuations often do not correspond directly to the full implied volatility as calculated over longer periods (like 30 days).