import os
import gzip
import html
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus

NATION_NAME = os.environ["NS_NATION_NAME"].strip()
CONTACT_INFO = os.environ["NS_CONTACT_INFO"].strip()

NATION_SLUG = NATION_NAME.lower().replace(" ", "_")

API = "https://www.nationstates.net/cgi-bin/api.cgi"
DUMP_URL = "https://www.nationstates.net/pages/nations.xml.gz"

HEADERS = {
    "User-Agent": (
        f"Daily Endorsement Checker, operated by {CONTACT_INFO}"
    )
}

session = requests.Session()
session.headers.update(HEADERS)


def normalize(name):
    return name.strip().lower().replace(" ", "_")


def parse_list(text):
    if not text:
        return set()

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

    return normalize(region)


def get_region_nations(region):
    xml = api_request({
        "region": region,
        "q": "nations"
    })

    root = ET.fromstring(xml)

    for element in root.iter():
        if element.tag.upper() == "NATIONS":
            return parse_list(
                element.text or ""
            )

    raise RuntimeError(
        "Could not get nations in your region."
    )


def get_wa_members():
    xml = api_request({
        "wa": "3",
        "q": "members"
    })

    root = ET.fromstring(xml)

    for element in root.iter():
        if element.tag.upper() == "MEMBERS":
            return parse_list(
                element.text or ""
            )

    raise RuntimeError(
        "Could not get WA members."
    )


def download_dump():
    print("Downloading NationStates daily dump...")

    response = session.get(
        DUMP_URL,
        timeout=120
    )

    response.raise_for_status()

    print(
        f"Downloaded "
        f"{len(response.content) / 1024 / 1024:.1f} MB"
    )

    return gzip.decompress(
        response.content
    )


def get_my_endorsements(
    dump_data,
    region,
    wa_in_region
):
    print("Reading endorsement data...")

    root = ET.fromstring(dump_data)

    my_endorsements = set()

    for nation in root.findall(".//NATION"):
        name = nation.findtext(
            "NAME",
            ""
        )

        slug = normalize(name)

        if slug != NATION_SLUG:
            continue

        nation_region = normalize(
            nation.findtext(
                "REGION",
                ""
            )
        )

        if nation_region != region:
            raise RuntimeError(
                "Your nation was found in the dump, "
                "but the region did not match."
            )

        endorsements = nation.findtext(
            "ENDORSEMENTS",
            ""
        )

        my_endorsements = parse_list(
            endorsements
        )

        break

    if not my_endorsements:
        print(
            "No endorsements were found "
            "for your nation in the dump."
        )

    return my_endorsements & wa_in_region


def nation_url(nation):
    return (
        "https://www.nationstates.net/nation="
        + quote_plus(nation)
    )


def generate_html(
    unendorsed,
    region
):
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

    for nation in sorted(unendorsed):
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

    if (!name) {{
        return;
    }}

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

<p>
Region: {html.escape(region.replace("_", " "))}
</p>

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
    print("Starting endorsement checker...")

    region = get_region()

    print(
        f"Region: "
        f"{region.replace('_', ' ')}"
    )

    region_nations = get_region_nations(
        region
    )

    print(
        f"Region nations: "
        f"{len(region_nations)}"
    )

    wa_members = get_wa_members()

    print(
        f"WA members: "
        f"{len(wa_members)}"
    )

    wa_in_region = (
        region_nations & wa_members
    )

    wa_in_region.discard(
        NATION_SLUG
    )

    print(
        f"WA nations in region: "
        f"{len(wa_in_region)}"
    )

    dump_data = download_dump()

    already_endorsed = get_my_endorsements(
        dump_data,
        region,
        wa_in_region
    )

    unendorsed = (
        wa_in_region - already_endorsed
    )

    print(
        f"Already endorsed in region: "
        f"{len(already_endorsed)}"
    )

    print(
        f"Unendorsed WA nations: "
        f"{len(unendorsed)}"
    )

    output = generate_html(
        unendorsed,
        region
    )

    print(
        f"Generated: {output}"
    )


if __name__ == "__main__":
    main()
