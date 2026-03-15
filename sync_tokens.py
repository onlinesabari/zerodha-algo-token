import os

# This safely prints the names of the variables Python can see, 
# WITHOUT printing your actual password.
print("Available Environment Variables:")
for key in os.environ.keys():
    if key.startswith("DB_"):
        print(f"Found: {key}")
        
import pandas as pd
from sqlalchemy import create_engine

def sync_to_mysql():
    print("⏳ Downloading fresh instrument list from Zerodha...")
    url = "https://api.kite.trade/instruments"
    
    # Download and filter the massive CSV
    df = pd.read_csv(url)
    df = df[df['exchange'] == 'NSE']
    df = df[['instrument_token', 'tradingsymbol', 'exchange']]
    
    # Grab the database credentials from GitHub Secrets
    db_host = os.environ.get("DB_HOST")
    db_user = os.environ.get("DB_USER")
    db_password = os.environ.get("DB_PASSWORD")
    db_name = os.environ.get("DB_NAME")

    # This will print True if it has a value, and False if it is blank
    print(f"DB_HOST is loaded: {bool(db_host)}")
    print(f"DB_USER is loaded: {bool(db_user)}")
    print(f"DB_PASSWORD is loaded: {bool(db_password)}")
    print(f"DB_NAME is loaded: {bool(db_name)}")

    if not all([db_host, db_user, db_password, db_name]):
        raise Exception("Database credentials missing from environment variables!")

    print(f"🔌 Connecting to remote MySQL database at {db_host}...")
    
    # Create the MySQL connection engine
    engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}")
    
    # Push the data! 'if_exists="replace"' automatically drops yesterday's table and builds a fresh one
    df.to_sql('zerodha_tokens', con=engine, if_exists='replace', index=False)
    
    print(f"✅ Success! {len(df)} NSE tokens firmly locked into phpMyAdmin.")

if __name__ == "__main__":
    sync_to_mysql()
