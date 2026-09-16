import os
import requests
from urllib.parse import quote_plus


# NationStates Daily Endorsement Checker
# ============ ===== =========== =======


NATION_NAME = os.environ.get("NS_NATION_NAME")
CONTACT_INFO = os.environ.get("NS_CONTACT_INFO")

if not NATION_NAME:
    raise RuntimeError("NS_NATION_NAME GitHub Secret is missing.")

if not CONTACT_INFO:
    raise RuntimeError("NS_CONTACT_INFO GitHub Secret is missing.")

# NationStates asks scripts to identify themselves with a
# meaningful User-Agent.
USER_AGENT = (
    f"Daily Endorsement Checker, operated by {CONTACT_INFO} "
    "(Checks nations in my region that I have not endorsed)"
)

HEADERS = {
    "User-Agent": USER_AGENT
}

API_URL = "https://www.nationstates.net/cgi-bin/api.cgi"


def api_request(params):
    """Make a NationStates API request."""
    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    return response.text


def get_nation_info():
    """Get the nation's region and current endorsements."""
    params = {
        "nation": NATION_NAME,
        "q": "region+endorsements+wa"
    }

    return api_request(params)


def extract_xml_tag(xml, tag):
    """Extract the contents of a simple XML tag."""
    start = xml.find(f"<{tag}>")
    end = xml.find(f"</{tag}>")

    if start == -1 or end == -1:
        return None

    start += len(tag) + 2

    return xml[start:end]


def extract_endorsements(xml):
    """Extract endorsed nation names from the ENDORSEMENTS shard."""
    endorsements = []

    start = xml.find("<ENDORSEMENTS>")

    if start == -1:
        return endorsements

    end = xml.find("</ENDORSEMENTS>", start)

    if end == -1:
        return endorsements

    section = xml[start:end]
    position = 0

    while True:
        nation_start = section.find("<NATION>", position)

        if nation_start == -1:
            break

        nation_end = section.find("</NATION>", nation_start)

        if nation_end == -1:
            break

        nation = section[
            nation_start + len("<NATION>"):
            nation_end
        ]

        endorsements.append(nation.strip())

        position = nation_end + len("</NATION>")

    return endorsements


def get_region_nations(region_name):
    """Get all nations in the region."""
    params = {
        "region": region_name,
        "q": "nations+wanations"
    }

    return api_request(params)


def extract_nations(xml, tag):
    """Extract nations from a <NATIONS> or <WANATIONS> section."""
    nations = []

    start = xml.find(f"<{tag}>")

    if start == -1:
        return nations

    end = xml.find(f"</{tag}>", start)

    if end == -1:
        return nations

    section = xml[start:end]

    # Region API normally returns nations separated by commas.
    for nation in section.replace("\n", "").split(","):
        nation = nation.strip()

        if nation:
            nations.append(nation)

    return nations


def nation_slug(name):
    """Convert a NationStates nation name into a URL slug."""
    return name.strip().lower().replace(" ", "_")


def main():
    print("=" * 60)
    print("NationStates Daily Endorsement Checker")
    print("=" * 60)

    print(f"Nation: {NATION_NAME}")
    print()

    
    # Get your nation information
    

    nation_xml = get_nation_info()

    region = extract_xml_tag(nation_xml, "REGION")

    if not region:
        raise RuntimeError(
            "Could not determine your region from the NationStates API."
        )

    print(f"Region: {region}")
    print()

    
    # Get current endorsements
    

    endorsed = extract_endorsements(nation_xml)

    endorsed_normalized = {
        nation_slug(nation)
        for nation in endorsed
    }

    print(f"Currently endorsed: {len(endorsed)}")
    print()

   
    # Get WA nations in the region
    
    region_xml = get_region_nations(region)

    wa_nations = extract_nations(
        region_xml,
        "WANATIONS"
    )
  
    # Find nations we haven't endorsed

    missing = []

    for nation in wa_nations:
        slug = nation_slug(nation)

        # Don't list ourselves.
        if slug == nation_slug(NATION_NAME):
            continue

        if slug not in endorsed_normalized:
            missing.append(nation)

    missing.sort(key=str.lower)

    # --------------------------------------------------------
    # Print results
    # --------------------------------------------------------

    print("-" * 60)

    if not missing:
        print(
            "You have endorsed every WA nation in your region."
        )

        print("-" * 60)
        return

    print(
        f"Nations you haven't endorsed yet: {len(missing)}"
    )

    print()

    for number, nation in enumerate(missing, start=1):
        slug = nation_slug(nation)

        print(f"{number}. {nation}")

        print(
            f"   https://www.nationstates.net/nation={quote_plus(slug)}"
        )

        print()

    print("-" * 60)

    print("This script only generates the list.")
    print("Endorsements must be made manually.")

    print("-" * 60)


if __name__ == "__main__":
    main()
