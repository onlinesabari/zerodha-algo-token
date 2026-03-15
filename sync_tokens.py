import os
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
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_name = os.getenv("DB_NAME")
    
    if not all([db_user, db_pass, db_host, db_name]):
        raise Exception("Database credentials missing from environment variables!")

    print(f"🔌 Connecting to remote MySQL database at {db_host}...")
    
    # Create the MySQL connection engine
    engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}")
    
    # Push the data! 'if_exists="replace"' automatically drops yesterday's table and builds a fresh one
    df.to_sql('zerodha_tokens', con=engine, if_exists='replace', index=False)
    
    print(f"✅ Success! {len(df)} NSE tokens firmly locked into phpMyAdmin.")

if __name__ == "__main__":
    sync_to_mysql()
