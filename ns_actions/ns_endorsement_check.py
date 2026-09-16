import os
import html
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

NATION_NAME = os.environ["NS_NATION_NAME"].strip()
CONTACT_INFO = os.environ["NS_CONTACT_INFO"].strip()

NATION_SLUG = NATION_NAME.lower().replace(" ", "_")

API = "https://www.nationstates.net/cgi-bin/api.cgi"

HEADERS = {
    "User-Agent": f"Daily Endorsement Checker, operated by {CONTACT_INFO}"
}


def api_request(params):
    response = requests.get(
        API,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()
    return response.text


def get_nation_info():
    xml = api_request({
        "nation": NATION_SLUG,
        "q": "region+endorsements"
    })

    root = ET.fromstring(xml)

    region = root.findtext(".//REGION", "").strip()

    endorsements_text = root.findtext(
        ".//ENDORSEMENTS",
        ""
    ).strip()

    endorsements = {
        x.strip().lower().replace(" ", "_")
        for x in endorsements_text.split(",")
        if x.strip()
    }

    return region, endorsements


def get_wa_nations(region):
    region_slug = region.lower().replace(" ", "_")

    xml = api_request({
        "region": region_slug,
        "q": "wanations+numwanations"
    })

    root = ET.fromstring(xml)

    print("Region API root:", root.tag)

    wa_nations = set()
    number = None

    for element in root.iter():
        tag = element.tag.upper()
        text = (element.text or "").strip()

        if tag == "WANATIONS":
            print("WANATIONS raw length:", len(text))

            for nation in text.split(","):
                nation = nation.strip()

                if nation:
                    wa_nations.add(nation)

        elif tag == "NUMWANATIONS":
            number = text

    print("API numwanations:", number)
    print("API WANATIONS entries parsed:", len(wa_nations))

    return wa_nations

def nation_url(name):
    slug = name.lower().replace(" ", "_")
    return f"https://www.nationstates.net/nation={quote_plus(slug)}"


def generate_html(nations):
    output_dir = "outputs/endorsements"
    output_file = os.path.join(
        output_dir,
        "endorsements.html"
    )

    os.makedirs(output_dir, exist_ok=True)

    nation_lines = []

    for nation in sorted(nations, key=str.lower):
        safe_name = html.escape(nation)
        url = nation_url(nation)

        nation_lines.append(
            f"""
            <div class="nation">
                <a href="{url}"
                   target="_blank"
                   onclick="removeNation(this)">
                    {safe_name}
                </a>
                <button onclick="deleteNation(this)">
                    Delete
                </button>
            </div>
            """
        )

    page = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Unendorsed WA Nations</title>

<style>
body {{
    font-family: Arial, sans-serif;
    margin: 30px;
}}

.nation {{
    margin: 8px 0;
}}

.nation a {{
    margin-right: 10px;
}}

button {{
    cursor: pointer;
}}
</style>

<script>
function removeNation(link) {{
    setTimeout(function() {{
        link.parentElement.remove();
    }}, 100);
}}

function deleteNation(button) {{
    button.parentElement.remove();
}}

function addNation() {{
    const input = document.getElementById("nationInput");
    const name = input.value.trim();

    if (!name) return;

    const div = document.createElement("div");
    div.className = "nation";

    const link = document.createElement("a");

    link.href =
        "https://www.nationstates.net/nation=" +
        name.toLowerCase().replace(/ /g, "_");

    link.target = "_blank";
    link.textContent = name;

    link.onclick = function() {{
        setTimeout(function() {{
            div.remove();
        }}, 100);
    }};

    const button = document.createElement("button");
    button.textContent = "Delete";

    button.onclick = function() {{
        div.remove();
    }};

    div.appendChild(link);
    div.appendChild(button);

    document.getElementById("nations").appendChild(div);

    input.value = "";
}}
</script>

</head>

<body>

<h1>Unendorsed WA Nations</h1>

<div>
    <input
        id="nationInput"
        placeholder="Nation name"
    >

    <button onclick="addNation()">
        Add Nation
    </button>
</div>

<br>

<div id="nations">
{"".join(nation_lines)}
</div>

</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(page)

    return output_file


def main():
    region, endorsements = get_nation_info()

    wa_nations = get_wa_nations(region)

    my_nation = NATION_SLUG.lower()

    missing = {
        nation
        for nation in wa_nations
        if nation.lower().replace(" ", "_") != my_nation
        and nation.lower().replace(" ", "_") not in endorsements
    }

    output = generate_html(missing)

    print()
    print(f"Region: {region}")
    print(f"WA nations found: {len(wa_nations)}")
    print(f"Your endorsements: {len(endorsements)}")
    print(f"Unendorsed WA nations: {len(missing)}")
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
