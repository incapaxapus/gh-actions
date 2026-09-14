import os
import requests

# Pull data securely from your GitHub Secrets
NATION_NAME = os.environ.get("NS_NATION_NAME")
CONTACT_INFO = os.environ.get("NS_CONTACT_INFO")

if not NATION_NAME or not CONTACT_INFO:
    print("Error: Missing environmental variables. Check your GitHub Secrets.")
    exit(1)

# Format the nation name correctly for the URL layout
formatted_name = NATION_NAME.strip().lower().replace(" ", "_")

# Setting the mandatory user agent per NationStates API rules
USER_AGENT = f"Weekly Ping Script, operated by {CONTACT_INFO} (Automated weekly activity ping)"

def ping_nation():
    # Targets the exact public browser view address you requested
    url = f"https://nationstates.net{formatted_name}/"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print(f"Success! The page for '{NATION_NAME}' was successfully loaded and accessed.")
        elif response.status_code == 404:
            print(f"Error 404: Nation '{NATION_NAME}' was not found. Check the name in your GitHub Secrets.")
        else:
            print(f"Failed to load page. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred while connecting: {e}")

if __name__ == "__main__":
    ping_nation()
