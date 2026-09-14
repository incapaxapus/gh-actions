import os
import requests
import xml.etree.ElementTree as ET

# --- CONFIGURATION FROM SECRETS ---
# The script will safely pull these variables from your private GitHub settings
NATION_NAME = os.environ.get("NS_NATION_NAME")
CONTACT_INFO = os.environ.get("NS_CONTACT_INFO")

if not NATION_NAME or not CONTACT_INFO:
    print("Error: Missing environmental variables. Check your GitHub Secrets.")
    exit(1)

USER_AGENT = f"Weekly Ping Script, operated by {CONTACT_INFO} (Automated weekly activity ping)"
# ---------------------------------

def ping_nation():
    url = f"https://nationstates.net{NATION_NAME}&q=name+motto+region"
    headers = {"User-Agent": USER_AGENT}
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            name = root.find('NAME').text if root.find('NAME') is not None else "Unknown"
            region = root.find('REGION').text if root.find('REGION') is not None else "Unknown"
            print(f"Success! Checked in on '{name}' in the region of '{region}'.")
        elif response.status_code == 429:
            print("Error: Over NationStates API rate limit.")
        elif response.status_code == 404:
            print("Error: Nation not found. Double check your NS_NATION_NAME spelling.")
        else:
            print(f"Failed to reach API. Status code: {response.status_code}")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    ping_nation()
