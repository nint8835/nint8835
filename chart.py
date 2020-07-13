import os
from typing import Dict

import pygal
import requests
from dotenv import load_dotenv
from pygal.style import Style

load_dotenv()

resp = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": """
            {
                viewer {
                    repositories(first: 100, ownerAffiliations: [OWNER], isFork: false) {
                        nodes {
                            name
                            languages(first: 20) {
                                edges {
                                    size
                                    node {
                                        name
                                        color
                                    }
                                }
                            }
                        }
                    }
                }
            }
        """
    },
    headers={"Authorization": f"Bearer {os.environ['GITHUB_PAT']}"},
)
language_counts: Dict[str, int] = {}
language_colours: Dict[str, str] = {}

for repository in resp.json()["data"]["viewer"]["repositories"]["nodes"]:
    for language in repository["languages"]["edges"]:
        lang_name = language["node"]["name"]
        language_counts[lang_name] = (
            language_counts.get(lang_name, 0) + language["size"]
        )

        if lang_name not in language_colours:
            language_colours[lang_name] = language["node"]["color"]

for language, colour in language_colours.items():
    if colour is None:
        language_colours[language] = "#ababab"

language_counts = {
    key: language_counts[key]
    for key in sorted(language_counts, key=lambda k: language_counts[k], reverse=True)[
        :10
    ]
}
print(language_counts, language_colours)

style = Style(colors=list(language_colours[lang] for lang in language_counts))

chart = pygal.Pie(style=style)

for language, byte_count in language_counts.items():
    chart.add(language, byte_count)

chart.render_to_file("languages.svg")
