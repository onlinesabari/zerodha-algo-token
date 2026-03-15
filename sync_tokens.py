import os
import pandas as pd
import requests

def sync_tokens_to_api():
    print("⏳ Loading API credentials...")
    
    # Fetch API credentials from GitHub Secrets
    api_url = os.environ.get("API_URL")
    api_key = os.environ.get("API_KEY")

    if not all([api_url, api_key]):
        raise Exception("❌ API credentials missing from environment variables!")

    print("⏳ Downloading fresh instrument list from Zerodha...")
    url = "https://api.kite.trade/instruments"
    
    try:
        # Download and filter the massive CSV
        df = pd.read_csv(url)
        df = df[df['exchange'] == 'NSE']
        df = df[['instrument_token', 'tradingsymbol', 'exchange']]
        
        # Convert the DataFrame into a list of dictionaries so it can be sent as JSON
        # Output looks like: [{"instrument_token": 123, "tradingsymbol": "RELIANCE", ...}, ...]
        token_data = df.to_dict(orient='records')
        
    except Exception as e:
        raise Exception(f"❌ Failed to download or process Zerodha data: {e}")
    
    print(f"📡 Sending {len(token_data)} NSE tokens to server API at {api_url}...")
    
    # Package the data and the secret key
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {"tokens": token_data}

    # Send the POST request to your server
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            print("✅ Server successfully received and saved the data!")
            # Using .json() safely in case the server returns plain text
            try:
                print(f"Server response: {response.json()}")
            except requests.exceptions.JSONDecodeError:
                print(f"Server response (text): {response.text}")
        else:
            raise Exception(f"❌ Server rejected the data (Status {response.status_code}): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to the server API: {e}")
        exit(1)

if __name__ == "__main__":
    sync_tokens_to_api()
