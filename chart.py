import os
from typing import Dict

import requests
from dotenv import load_dotenv

load_dotenv()

resp = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": """
            {
                viewer {
                    repositories(first: 100) {
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
print(language_counts, language_colours)
