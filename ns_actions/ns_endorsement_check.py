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


def split_nations(text):
    return {
        name.strip().lower().replace(" ", "_")
        for name in text.split(",")
        if name.strip()
    }


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
    )

    endorsements = split_nations(endorsements_text)

    return region, endorsements


def get_region_nations(region):
    region_slug = region.lower().replace(" ", "_")

    xml = api_request({
        "region": region_slug,
        "q": "nations"
    })

    root = ET.fromstring(xml)

    nations = set()

    for element in root.iter():
        if element.tag.upper() == "NATIONS":
            nations.update(split_nations(element.text or ""))

        if element.tag.upper() == "UNNATIONS":
            nations.update(split_nations(element.text or ""))

    return nations


def get_wa_members():
    xml = api_request({
        "wa": "1",
        "q": "members"
    })

    root = ET.fromstring(xml)

    members = set()

    for element in root.iter():
        if element.tag.upper() in {
            "NATIONS",
            "MEMBERS",
            "WAMEMBERS"
        }:
            members.update(
                split_nations(element.text or "")
            )

    return members


def nation_url(slug):
    return (
        "https://www.nationstates.net/nation="
        + quote_plus(slug)
    )


def generate_html(nations):
    output_dir = "outputs/endorsements"
    output_file = os.path.join(
        output_dir,
        "endorsements.html"
    )

    os.makedirs(output_dir, exist_ok=True)

    nation_lines = []

    for nation in sorted(nations):
        display_name = nation.replace("_", " ")
        safe_name = html.escape(display_name)
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

    const slug = name
        .toLowerCase()
        .replace(/ /g, "_");

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

    document
        .getElementById("nations")
        .appendChild(div);

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

    with open(output_file, "w", encoding="utf-8") as file:
        file.write(page)

    return output_file


def main():
    region, endorsements = get_nation_info()

    region_nations = get_region_nations(region)
    wa_members = get_wa_members()

    wa_in_region = region_nations.intersection(
        wa_members
    )

    missing = wa_in_region - endorsements

    missing.discard(NATION_SLUG)

    output = generate_html(missing)

    print(f"Region: {region}")
    print(f"Region nations found: {len(region_nations)}")
    print(f"WA members found: {len(wa_members)}")
    print(f"WA nations in region: {len(wa_in_region)}")
    print(f"Your endorsements: {len(endorsements)}")
    print(f"Unendorsed WA nations: {len(missing)}")
    print(f"Generated: {output}")


if __name__ == "__main__":
    main()
