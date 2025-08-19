# collect_data.py
import requests
import json
import time
import os
import certifi # <<< CHANGE 1: Import the certifi library

# --- Configuration ---
API_KEY = '68a2090756d03bd6417bd25f' 
PLATFORM = 'instagram' # Make sure this is 'instagram' or 'x'

# --- Usernames to Scrape ---
REAL_USERNAMES = [

    
"sachin_choure_25"

]

FAKE_USERNAMES =[

]

# In collect_data.py

def fetch_profile_data(username, platform):
    """Fetches data for a single user from the ScrapingDog API."""
    print(f"Fetching data for '{username}'...")
    
    # --- FINAL FIX ---
    # The correct parameter for Instagram is 'username', not 'profile_id' or 'instagram_user'
    if platform == 'x':
        # NOTE: The parameter for X is likely 'profile_id'. Double-check on their site.
        api_url = f"https://api.scrapingdog.com/x/profile?api_key={API_KEY}&profile_id={username}"
    elif platform == 'instagram':
        # This now exactly matches your successful test code
        api_url = f"https://api.scrapingdog.com/instagram/profile?api_key={API_KEY}&username={username}"
    else:
        print(f"Invalid platform: {platform}")
        return None

    try:
        response = requests.get(api_url, timeout=30, verify=certifi.where())
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  -> Could not fetch data for {username}. Error: {e}")
        return None

def main():
    """Main function to collect and save data for all usernames."""
    output_dir = "raw_json_data"
    os.makedirs(output_dir, exist_ok=True)

    print("--- Collecting data for REAL accounts ---")
    for username in REAL_USERNAMES:
        data = fetch_profile_data(username, PLATFORM)
        if data:
            data['account_label'] = 'real'
            with open(os.path.join(output_dir, f"{username}.json"), 'w') as f:
                json.dump(data, f, indent=2)
        time.sleep(2)

    print("\n--- Collecting data for FAKE accounts ---")
    for username in FAKE_USERNAMES:
        data = fetch_profile_data(username, PLATFORM)
        if data:
            data['account_label'] = 'fake'
            with open(os.path.join(output_dir, f"{username}.json"), 'w') as f:
                json.dump(data, f, indent=2)
        time.sleep(2)

    print(f"\nData collection complete. Individual profiles saved in '{output_dir}' folder.")
    
    

if __name__ == "__main__":
    main()