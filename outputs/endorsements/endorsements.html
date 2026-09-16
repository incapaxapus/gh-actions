import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from html import escape

NATION_NAME = os.environ.get("NS_NATION_NAME")
CONTACT_INFO = os.environ.get("NS_CONTACT_INFO")

if not NATION_NAME:
    raise RuntimeError("NS_NATION_NAME GitHub Secret is missing.")

if not CONTACT_INFO:
    raise RuntimeError("NS_CONTACT_INFO GitHub Secret is missing.")

HEADERS = {
    "User-Agent": (
        f"Daily Endorsement Checker, operated by {CONTACT_INFO} "
        "(Daily region check)"
    )
}

API_URL = "https://www.nationstates.net/cgi-bin/api.cgi"

OUTPUT_DIR = os.path.join(
    "outputs",
    "endorsements"
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "endorsements.html"
)


def api_request(params):
    response = requests.get(
        API_URL,
        params=params,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


def get_nation_info():
    return api_request({
        "nation": NATION_NAME,
        "q": "region+endorsements+wa"
    })


def get_region_nations(region):
    return api_request({
        "region": region,
        "q": "wanations"
    })


def nation_slug(name):
    return (
        name
        .strip()
        .lower()
        .replace(" ", "_")
    )


def create_html(nations):
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    items = []

    for nation in nations:
        slug = nation_slug(nation)

        url = (
            "https://www.nationstates.net/nation="
            + quote_plus(slug)
        )

        items.append(
            f"""
<div class="nation" data-slug="{escape(slug)}">
    <a href="{escape(url)}"
       target="_blank"
       rel="noopener noreferrer"
       onclick="markClicked('{escape(slug)}')">
        {escape(url)}
    </a>
    <button onclick="removeNation('{escape(slug)}')">
        Delete
    </button>
</div>
"""
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NationStates Endorsements</title>

<style>
body {{
    font-family: Arial, sans-serif;
    margin: 20px;
}}

.nation {{
    margin-bottom: 8px;
}}

.nation a {{
    margin-right: 8px;
}}

button {{
    cursor: pointer;
}}

#add-section {{
    margin-bottom: 20px;
}}

#nation-input {{
    width: 350px;
    max-width: 90%;
}}
</style>
</head>

<body>

<div id="add-section">
    <input
        id="nation-input"
        type="text"
        placeholder="Nation name or URL"
    >
    <button onclick="addNation()">Add Nation</button>
</div>

<div id="nations">
{''.join(items)}
</div>

<script>

function normalizeNation(value) {{
    value = value.trim();

    if (!value) {{
        return "";
    }}

    if (value.includes("nation=")) {{
        value = value.split("nation=")[1];
    }}

    value = value.split("&")[0];
    value = value.split("#")[0];

    return value
        .toLowerCase()
        .replace(/ /g, "_");
}}

function nationURL(slug) {{
    return (
        "https://www.nationstates.net/nation="
        + encodeURIComponent(slug)
    );
}}

function markClicked(slug) {{
    const element = document.querySelector(
        '[data-slug="' + CSS.escape(slug) + '"]'
    );

    if (element) {{
        element.remove();
    }}
}}

function removeNation(slug) {{
    const element = document.querySelector(
        '[data-slug="' + CSS.escape(slug) + '"]'
    );

    if (element) {{
        element.remove();
    }}
}}

function addNation() {{
    const input = document.getElementById(
        "nation-input"
    );

    const slug = normalizeNation(
        input.value
    );

    if (!slug) {{
        return;
    }}

    const existing = document.querySelector(
        '[data-slug="' + CSS.escape(slug) + '"]'
    );

    if (existing) {{
        input.value = "";
        return;
    }}

    const container = document.getElementById(
        "nations"
    );

    const div = document.createElement("div");

    div.className = "nation";
    div.dataset.slug = slug;

    const link = document.createElement("a");

    link.href = nationURL(slug);
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = nationURL(slug);

    link.onclick = function() {{
        markClicked(slug);
    }};

    const button = document.createElement("button");

    button.textContent = "Delete";

    button.onclick = function() {{
        removeNation(slug);
    }};

    div.appendChild(link);
    div.appendChild(button);

    container.appendChild(div);

    input.value = "";
}}

</script>

</body>
</html>
"""

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(html)


def main():
    nation_xml = get_nation_info()

    nation_root = ET.fromstring(
        nation_xml
    )

    region_element = nation_root.find(
        "REGION"
    )

    if region_element is None:
        raise RuntimeError(
            "Could not determine your region."
        )

    region = region_element.text.strip()

    endorsements_element = nation_root.find(
        "ENDORSEMENTS"
    )

    endorsed = set()

    if endorsements_element is not None:
        if endorsements_element.text:
            endorsed = {
                nation_slug(nation)
                for nation in
                endorsements_element.text.split(",")
                if nation.strip()
            }

    region_xml = get_region_nations(
        region
    )

    region_root = ET.fromstring(
        region_xml
    )

    wanations_element = region_root.find(
        "WANATIONS"
    )

    wa_nations = []

    if wanations_element is not None:
        if wanations_element.text:
            wa_nations = [
                nation.strip()
                for nation in
                wanations_element.text.split(",")
                if nation.strip()
            ]

    missing = []

    own_slug = nation_slug(
        NATION_NAME
    )

    for nation in wa_nations:
        slug = nation_slug(nation)

        if slug == own_slug:
            continue

        if slug not in endorsed:
            missing.append(nation)

    missing.sort(
        key=str.lower
    )

    create_html(
        missing
    )

    print(
        f"Region: {region}"
    )

    print(
        f"WA nations found: {len(wa_nations)}"
    )

    print(
        f"Unendorsed WA nations: {len(missing)}"
    )

    print(
        f"Generated: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
