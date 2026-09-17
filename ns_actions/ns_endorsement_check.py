import os
import html
import time
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

NATION_NAME = os.environ["NS_NATION_NAME"].strip()
CONTACT_INFO = os.environ["NS_CONTACT_INFO"].strip()

NATION_SLUG = NATION_NAME.lower().replace(" ", "_")

API = "https://www.nationstates.net/cgi-bin/api.cgi"

HEADERS = {
    "User-Agent": (
        f"Daily Endorsement Checker, operated by {CONTACT_INFO}"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


def normalize(name):
    return name.strip().lower().replace(" ", "_")


def parse_nations(text):
    text = text.replace(":", ",")

    return {
        normalize(x)
        for x in text.split(",")
        if x.strip()
    }


def api_request(params):
    response = session.get(
        API,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    if not response.text.strip():
        raise RuntimeError(
            "NationStates returned an empty response."
        )

    return response.text


def get_region():
    xml = api_request({
        "nation": NATION_SLUG,
        "q": "region"
    })

    root = ET.fromstring(xml)

    region = root.findtext(
        "REGION",
        ""
    ).strip()

    if not region:
        raise RuntimeError(
            "Could not determine your region."
        )

    return region


def get_region_nations(region):
    xml = api_request({
        "region": normalize(region),
        "q": "nations"
    })

    root = ET.fromstring(xml)

    nations = set()

    for element in root.iter():
        if element.tag.upper() == "NATIONS":
            nations.update(
                parse_nations(
                    element.text or ""
                )
            )

    if not nations:
        raise RuntimeError(
            "NationStates returned no regional nations."
        )

    return nations


def get_wa_members():
    xml = api_request({
        "wa": "3",
        "q": "members"
    })

    root = ET.fromstring(xml)

    members = set()

    for element in root.iter():
        if element.tag.upper() == "MEMBERS":
            members.update(
                parse_nations(
                    element.text or ""
                )
            )

    if not members:
        raise RuntimeError(
            "NationStates returned no WA members."
        )

    return members


def endorses_me(nation):
    xml = api_request({
        "nation": nation,
        "q": "endorsements"
    })

    root = ET.fromstring(xml)

    endorsements = parse_nations(
        root.findtext(
            "ENDORSEMENTS",
            ""
        )
    )

    return NATION_SLUG in endorsements


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

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    entries = []

    for nation in sorted(nations):
        display_name = nation.replace(
            "_",
            " "
        )

        safe_name = html.escape(
            display_name
        )

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
    const input =
        document.getElementById("nationInput");

    const name = input.value.trim();

    if (!name) return;

    const slug =
        name.toLowerCase().replace(/ /g, "_");

    const div =
        document.createElement("div");

    div.className = "nation";

    const link =
        document.createElement("a");

    link.href =
        "https://www.nationstates.net/nation="
        + slug;

    link.target = "_blank";
    link.textContent = name;

    link.onclick = function() {{
        setTimeout(function() {{
            div.remove();
        }}, 100);
    }};

    const button =
        document.createElement("button");

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
{"".join(entries)}
</div>

</body>
</html>
"""

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(page)

    return output_file


def main():
    region = get_region()

    region_nations = get_region_nations(
        region
    )

    wa_members = get_wa_members()

    wa_in_region = (
        region_nations & wa_members
    )

    wa_in_region.discard(
        NATION_SLUG
    )

    endorsed = set()
    unendorsed = set()

    total = len(wa_in_region)

    print(f"Region: {region}")
    print(
        f"Region nations found: "
        f"{len(region_nations)}"
    )
    print(
        f"WA members found: "
        f"{len(wa_members)}"
    )
    print(
        f"WA nations in region: "
        f"{total}"
    )

    for index, nation in enumerate(
        sorted(wa_in_region),
        start=1
    ):
        try:
            if endorses_me(nation):
                endorsed.add(nation)
            else:
                unendorsed.add(nation)

        except Exception as error:
            print(
                f"Error checking {nation}: "
                f"{error}"
            )

            unendorsed.add(nation)

        if index % 25 == 0 or index == total:
            print(
                f"Checked {index}/{total}"
            )

        time.sleep(1)

    output = generate_html(
        unendorsed
    )

    print(
        f"Already endorsed: "
        f"{len(endorsed)}"
    )

    print(
        f"Unendorsed WA nations: "
        f"{len(unendorsed)}"
    )

    print(
        f"Generated: {output}"
    )


if __name__ == "__main__":
    main()
