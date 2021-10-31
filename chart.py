import os
from typing import Dict

import pygal
import requests
from dotenv import load_dotenv
from pygal.style import Style

load_dotenv()

# Colours to be used for languages lacking their own colour.
# Selected from https://github.com/ozh/github-colors from the languages that were
# deemed unlikely to ever appear in this graph.
FILLER_COLOURS = ["#E8274B", "#64C800", "#9DC3FF", "#a957b0", "#cd6400"]

resp = requests.post(
    "https://api.github.com/graphql",
    json={
        "query": """
            {
                viewer {
                    repositories(first: 100, ownerAffiliations: [OWNER], isFork: false, orderBy: {field: UPDATED_AT, direction: DESC}) {
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
                            repositoryTopics(first: 10) {
                                nodes {
                                    topic {
                                        name
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
language_colours: Dict[str, str] = {"Other": FILLER_COLOURS.pop()}

for repository in resp.json()["data"]["viewer"]["repositories"]["nodes"]:
    if any(topic["name"] == "language-stats-ignored" for topic in repository["repositoryTopics"]["nodes"]):
        continue
    for language in repository["languages"]["edges"]:
        lang_name = language["node"]["name"]
        language_counts[lang_name] = (
            language_counts.get(lang_name, 0) + language["size"]
        )

        if lang_name not in language_colours:
            language_colours[lang_name] = language["node"]["color"]

for language, colour in language_colours.items():
    if colour is None:
        language_colours[language] = FILLER_COLOURS.pop()

sorted_languages = sorted(language_counts, key=lambda k: language_counts[k], reverse=True)

top_language_counts = {
    key: language_counts[key]
    for key in sorted_languages[
        :10
    ]
}
top_language_counts["Other"] = sum(language_counts[key] for key in sorted_languages[10:])

style = Style(colors=list(language_colours[lang] for lang in top_language_counts))

chart = pygal.Pie(style=style)

for language, byte_count in top_language_counts.items():
    chart.add(language, byte_count)

chart.render_to_file("languages.svg")
