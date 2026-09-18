import os
import requests

# Hello! Welcome to ns_country_ping.py!

# Get some data from your GitHub Secrets
# Make sure to create a secret with the name NS_NATION_NAME. Example: country_name
# Make sure to create a secret with the name NS_CONTACT_INFO (For ping API). Example: country_name OR example@gmail.com
# Make sure to create a secret with the name NS_PASSWORD.
NATION_NAME = os.environ.get("NS_NATION_NAME")
CONTACT_INFO = os.environ.get("NS_CONTACT_INFO")
PASSWORD = os.environ.get("NS_PASSWORD")

if not NATION_NAME or not CONTACT_INFO or not PASSWORD:
    print("Error: Missing environmental variables. Check your GitHub Secrets.")
    exit(1)

# Format the nation name correctly for the URL layout (In case of idiocy)
formatted_name = NATION_NAME.strip().lower().replace(" ", "_")

# Setting the user agent per NationStates API rules (why we need contact info)
USER_AGENT = f"Weekly Ping Script, operated by {CONTACT_INFO} (Automated weekly activity ping)"

def ping_nation():
    # Sets the URL for use by script
    url = "https://www.nationstates.net/cgi-bin/api.cgi"

    params = {
        "nation": formatted_name,
        "q": "ping"
    }

    headers = {
        "User-Agent": USER_AGENT,
        "X-Password": PASSWORD
    }
    
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"Success! The page for '{NATION_NAME}' was successfully loaded and accessed.")
        elif response.status_code == 404:
            print(f"Error 404: Nation '{NATION_NAME}' was not found. Check the name in your GitHub Secrets.")
        elif response.status_code == 403:
            print("Error 403: Authentication failed. Check NS_PASSWORD.")
        else:
            print(f"Failed to load page. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred while connecting: {e}")

if __name__ == "__main__":
    ping_nation()
