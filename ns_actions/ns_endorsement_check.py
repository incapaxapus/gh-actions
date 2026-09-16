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

    if not response.text.strip():
        raise RuntimeError("NationStates returned an empty response.")

    return response.text


def parse_nations(text):
    return {
        x.strip().lower()
        for x in text.split(",")
        if x.strip()
    }


def get_nation_info():
    xml = api_request({
        "nation": NATION_SLUG,
        "q": "region+endorsements"
    })

    root = ET.fromstring(xml)

    region = root.findtext("REGION", "").strip()
    endorsements = parse_nations(
        root.findtext("ENDORSEMENTS", "")
    )

    if not region:
        raise RuntimeError("Could not determine region.")

    return region, endorsements


def get_region_wa_nations(region):
    region_slug = region.lower().replace(" ", "_")

    xml = api_request({
        "region": region_slug,
        "q": "nations+wanations"
    })

    root = ET.fromstring(xml)

    print("Region API root:", root.tag)

    nations = set()
    wa_nations = set()

    for element in root:
        tag = element.tag.upper()
        text = element.text or ""

        if tag == "NATIONS":
            nations = parse_nations(text)

        elif tag == "WANATIONS":
            wa_nations = parse_nations(text)

        print(
            f"API field: {element.tag} "
            f"({len(text)} characters)"
        )

    if not nations:
        raise RuntimeError(
            "NationStates did not return NATIONS."
        )

    if not wa_nations:
        raise RuntimeError(
            "NationStates did not return WANATIONS."
        )

    return nations, wa_nations


def nation_url(nation):
    return (
        "https://www.nationstates.net/nation="
        + quote_plus(nation)
    )


def generate_html(nations):
    output_dir = "outputs/endorsements"
    output_file = os.path.join(
        output_dir,
        "endorsements.html"
    )

    os.makedirs(output_dir, exist_ok=True)

    entries = []

    for nation in sorted(nations):
        display_name = nation.replace("_", " ")
        safe_name = html.escape(display_name)

        entries.append(
            f"""
<div class="nation">
    <a href="{nation_url(nation)}"
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

    const slug = name.toLowerCase().replace(/ /g, "_");

    const div = document.createElement("div");
    div.className = "nation";

    const link = document.createElement("a");
    link.href =
        "https://www.nationstates.net/nation=" + slug;
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
    <input id="nationInput" placeholder="Nation name">
    <button onclick="addNation()">Add Nation</button>
</div>

<br>

<div id="nations">
{"".join(entries)}
</div>

</body>
</html>
"""

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(page)

    return output_file


def main():
    region, endorsements = get_nation_info()

    region_nations, wa_nations = (
        get_region_wa_nations(region)
    )

    wa_nations &= region_nations

    wa_nations.discard(NATION_SLUG)

    unendorsed = wa_nations - endorsements

    output = generate_html(unendorsed)

    print(f"Region: {region}")
    print(f"Region nations found: {len(region_nations)}")
    print(f"WA nations found: {len(wa_nations)}")
    print(f"Your endorsements: {len(endorsements)}")
    print(f"Unendorsed WA nations: {len(unendorsed)}")
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
