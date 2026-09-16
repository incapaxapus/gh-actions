import os
import requests
from urllib.parse import quote_plus
from html import escape

NATION_NAME = os.environ.get("NS_NATION_NAME")
CONTACT_INFO = os.environ.get("NS_CONTACT_INFO")

if not NATION_NAME:
    raise RuntimeError("NS_NATION_NAME GitHub Secret is missing.")

if not CONTACT_INFO:
    raise RuntimeError("NS_CONTACT_INFO GitHub Secret is missing.")

USER_AGENT = (
    f"Daily Endorsement Checker, operated by {CONTACT_INFO} "
    "(Daily region check)"
)

HEADERS = {
    "User-Agent": USER_AGENT
}

API_URL = "https://www.nationstates.net/cgi-bin/api.cgi"

OUTPUT_DIR = os.path.join("outputs", "endorsements")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "endorsements.html")


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
    params = {
        "nation": NATION_NAME,
        "q": "region+endorsements+wa"
    }
    return api_request(params)


def extract_xml_tag(xml, tag):
    start = xml.find(f"<{tag}>")
    end = xml.find(f"</{tag}>")

    if start == -1 or end == -1:
        return None

    start += len(tag) + 2
    return xml[start:end]


def extract_endorsements(xml):
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
        nation_start = section.find(
            "<NATION>",
            position
        )

        if nation_start == -1:
            break

        nation_end = section.find(
            "</NATION>",
            nation_start
        )

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
    params = {
        "region": region_name,
        "q": "wanations"
    }

    return api_request(params)


def extract_nations(xml, tag):
    nations = []

    start = xml.find(f"<{tag}>")

    if start == -1:
        return nations

    end = xml.find(f"</{tag}>", start)

    if end == -1:
        return nations

    section = xml[start:end]

    for nation in section.replace("\n", "").split(","):
        nation = nation.strip()

        if nation:
            nations.append(nation)

    return nations


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

    links = []

    for nation in nations:
        slug = nation_slug(nation)

        url = (
            "https://www.nationstates.net/nation="
            + quote_plus(slug)
        )

        links.append(
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

    links_html = "\n".join(links)

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
{links_html}
</div>

<script>

const STORAGE_KEY = "ns_endorsement_changes";

function getChanges() {{
    try {{
        return JSON.parse(
            localStorage.getItem(STORAGE_KEY)
        ) || {{ removed: [], added: [] }};
    }} catch {{
        return {{ removed: [], added: [] }};
    }}
}}

function saveChanges(changes) {{
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(changes)
    );
}}

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
    const changes = getChanges();

    if (!changes.removed.includes(slug)) {{
        changes.removed.push(slug);
    }}

    changes.added = changes.added.filter(
        nation => nation !== slug
    );

    saveChanges(changes);

    setTimeout(() => {{
        const element = document.querySelector(
            '[data-slug="' + CSS.escape(slug) + '"]'
        );

        if (element) {{
            element.remove();
        }}
    }}, 100);
}}

function removeNation(slug) {{
    const changes = getChanges();

    if (!changes.removed.includes(slug)) {{
        changes.removed.push(slug);
    }}

    changes.added = changes.added.filter(
        nation => nation !== slug
    );

    saveChanges(changes);

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

    const changes = getChanges();

    changes.removed = changes.removed.filter(
        nation => nation !== slug
    );

    if (!changes.added.includes(slug)) {{
        changes.added.push(slug);
    }}

    saveChanges(changes);

    addNationToPage(slug);

    input.value = "";
}}

function addNationToPage(slug) {{
    const existing = document.querySelector(
        '[data-slug="' + CSS.escape(slug) + '"]'
    );

    if (existing) {{
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
}}

function applySavedChanges() {{
    const changes = getChanges();

    for (const slug of changes.removed) {{
        const element = document.querySelector(
            '[data-slug="' + CSS.escape(slug) + '"]'
        );

        if (element) {{
            element.remove();
        }}
    }}

    for (const slug of changes.added) {{
        addNationToPage(slug);
    }}
}}

applySavedChanges();

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
    print("NationStates endorsement check")

    nation_xml = get_nation_info()

    region = extract_xml_tag(
        nation_xml,
        "REGION"
    )

    if not region:
        raise RuntimeError(
            "Could not determine your region."
        )

    endorsed = extract_endorsements(
        nation_xml
    )

    endorsed_normalized = {
        nation_slug(nation)
        for nation in endorsed
    }

    region_xml = get_region_nations(
        region
    )

    wa_nations = extract_nations(
        region_xml,
        "WANATIONS"
    )

    missing = []

    for nation in wa_nations:
        slug = nation_slug(nation)

        if slug == nation_slug(NATION_NAME):
            continue

        if slug not in endorsed_normalized:
            missing.append(nation)

    missing.sort(
        key=str.lower
    )

    create_html(missing)

    print(
        f"Generated {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
