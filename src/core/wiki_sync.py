import json
import requests

from bs4 import BeautifulSoup

from pathlib import Path



class WikiSync:

    def __init__(self):

        self.base_url = (
            "https://supermarkettogether.wiki.gg"
        )

        self.data_path = (
            Path(__file__).resolve().parent.parent
            / "data"
        )

    def sync_categories(self):

        url = (
            f"{self.base_url}"
            "/wiki/Product_Categories"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        content = soup.select_one(
            "#mw-content-text"
        )

        if content is None:

            raise RuntimeError(
                "Impossible de trouver "
                "le contenu principal du wiki."
            )

        links = content.select(
            "a[href]"
        )

        categories = []

        for link in links:

            name = link.get_text(
                " ",
                strip=True
            )

            href = link.get(
                "href",
                ""
            )

            # Les catégories principales sont
            # les ancres numérotées du sommaire :
            # "1 Basic Products", "2 Dairy Products", etc.
            if not href.startswith("#"):
                continue

            parts = name.split(
                " ",
                1
            )

            if (
                len(parts) != 2
                or not parts[0].isdigit()
            ):
                continue

            category_name = parts[1]

            category_id = (
                href
                .removeprefix("#")
                .lower()
            )

            categories.append({
                "id": category_id,
                "name": category_name,
                "anchor": href,
            })

        print(
            f"[wiki] {len(categories)} "
            f"catégorie(s) détectée(s)."
        )

        for category in categories:

            print(
                f"[wiki] "
                f"{category['id']} -> "
                f"{category['name']}"
            )

        # -------------------------
        # Sauvegarde du cache
        # -------------------------

        categories_path = (
            self.data_path
            / "categories.json"
        )

        categories_data = {
            "categories": categories
        }

        with open(
            categories_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                categories_data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"[wiki] Cache catégories sauvegardé : "
            f"{categories_path}"
        )

        return categories

        print(
            "[wiki] Page catégories récupérée."
        )

        return response.text


wiki_sync = WikiSync()