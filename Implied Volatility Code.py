#working implied volatility function
# Get Implied Volatility (IV)
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

#working intrinsic value
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
        st.write(f"Element text was: '{intrinsic_value_text}'")  # Debugging output
        
    except Exception as e:
        st.write("Could not retrieve intrinsic value.")
        st.write(f"Error: {e}")
        
    finally:
        driver.quit()

    return intrinsic_value
