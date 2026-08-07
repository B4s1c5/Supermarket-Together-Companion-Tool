import json
import requests
import sys
import time

from pathlib import Path

from bs4 import BeautifulSoup


# -------------------------
# Support lancement direct
# -------------------------

if __name__ == "__main__":

    src_path = (
        Path(__file__)
        .resolve()
        .parent
        .parent
    )

    if str(src_path) not in sys.path:

        sys.path.insert(
            0,
            str(src_path)
        )


from core.dev_console import dev_console



class WikiSync:

    def __init__(self):

        self.base_url = (
            "https://supermarkettogether.wiki.gg"
        )

        self.data_path = (
            Path(__file__).resolve().parent.parent
            / "data"
        )

        self.request_delay = 1.5

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "SMT-Companion/1.0 "
                "(Supermarket Together companion app)"
            )
        })

    def sync_categories(
            self,
            progress_callback=None,
            verbose=True
            ):

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

        # -------------------------
        # Détection des sous-catégories
        # -------------------------

        total_categories = len(
            categories
        )

        processed_categories = 0

        # -------------------------
        # Détection structurelle
        # des sous-catégories
        # -------------------------

        for category in categories:

            category[
                "sections"
            ] = []

            anchor_id = (
                category["anchor"]
                .removeprefix("#")
            )

            anchor = content.find(
                id=anchor_id
            )

            if anchor is None:

                print(
                    f"[wiki] Ancre introuvable : "
                    f"{category['name']}"
                )

                continue

            heading = anchor.find_parent(
                [
                    "h2",
                    "h3",
                    "h4",
                ]
            )

            if heading is None:

                print(
                    f"[wiki] Titre introuvable : "
                    f"{category['name']}"
                )

                continue

            current = (
                heading.next_sibling
            )

            seen_paths = set()

            while current is not None:

                if (
                    getattr(
                        current,
                        "name",
                        None
                    )
                    == "h2"
                ):
                    break

                if hasattr(
                    current,
                    "select"
                ):

                    section_links = (
                        current.select(
                            "a[href^='/wiki/']"
                        )
                    )

                    for link in section_links:

                        section_name = (
                            link.get_text(
                                " ",
                                strip=True
                            )
                        )

                        href = link.get(
                            "href",
                            ""
                        )

                        wiki_page = (
                            href.split(
                                "?",
                                1
                            )[0]
                        )

                        if not section_name:
                            continue

                        if wiki_page in seen_paths:
                            continue

                        seen_paths.add(
                            wiki_page
                        )

                        section_id = (
                            wiki_page
                            .removeprefix(
                                "/wiki/"
                            )
                            .lower()
                        )

                        category[
                            "sections"
                        ].append({
                            "id": section_id,
                            "name": section_name,
                            "wiki_path": wiki_page,
                        })

                current = (
                    current.next_sibling
                )

        # -------------------------
        # Résumé / affichage debug
        # -------------------------

        total_sections = sum(
            len(
                category.get(
                    "sections",
                    []
                )
            )
            for category in categories
        )

        if verbose:

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

                processed_categories += 1

                if progress_callback:

                    progress_callback(
                        processed_categories,
                        total_categories,
                        category["name"]
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

        if verbose:

            print(
                f"[wiki] Cache catégories sauvegardé : "
                f"{categories_path}"
            )

            # -------------------------
            # Détail des sections
            # -------------------------

            for category in categories:

                print(
                    f"\n[wiki] {category['name']}"
                )

                for section in category.get(
                    "sections",
                    []
                ):

                    print(
                        f"    -> "
                        f"{section['name']} "
                        f"({section['wiki_path']})"
                    )

        else:

            print(
                f"[wiki] "
                f"{len(categories)} categories / "
                f"{total_sections} sections detectees."
            )

        return categories
    
    def ensure_categories_cache(
        self,
        progress_callback=None
    ):

        categories_path = (
            self.data_path
            / "categories.json"
        )

        print(
            "[wiki] Verification "
            "des categories..."
        )

        # -------------------------
        # Lecture du cache actuel
        # -------------------------

        cached_categories = []

        if categories_path.exists():

            try:

                with open(
                    categories_path,
                    "r",
                    encoding="utf-8"
                ) as file:

                    cached_categories = (
                        json.load(
                            file
                        ).get(
                            "categories",
                            []
                        )
                    )

            except (
                OSError,
                json.JSONDecodeError,
            ):

                print(
                    "[wiki] Cache categories "
                    "invalide."
                )

        # -------------------------
        # Sauvegarde temporaire
        # du cache existant
        # -------------------------

        old_cache = (
            json.dumps(
                cached_categories,
                ensure_ascii=False,
                sort_keys=True
            )
        )

        # -------------------------
        # Scan du wiki
        # -------------------------

        remote_categories = (
            self.sync_categories(
                progress_callback=progress_callback,
                verbose=False
            )
        )

        new_cache = (
            json.dumps(
                remote_categories,
                ensure_ascii=False,
                sort_keys=True
            )
        )

        # -------------------------
        # Analyse des différences
        # -------------------------

        cached_by_id = {
            category["id"]: category
            for category in cached_categories
        }

        remote_by_id = {
            category["id"]: category
            for category in remote_categories
        }

        added_categories = (
            remote_by_id.keys()
            - cached_by_id.keys()
        )

        removed_categories = (
            cached_by_id.keys()
            - remote_by_id.keys()
        )

        for category_id in sorted(
            added_categories
        ):

            print(
                "[wiki] Nouvelle categorie : "
                f"{remote_by_id[category_id]['name']}"
            )

        for category_id in sorted(
            removed_categories
        ):

            print(
                "[wiki] Categorie supprimee : "
                f"{cached_by_id[category_id]['name']}"
            )

        # -------------------------
        # Comparaison des sections
        # -------------------------

        common_categories = (
            remote_by_id.keys()
            & cached_by_id.keys()
        )

        for category_id in sorted(
            common_categories
        ):

            cached_category = (
                cached_by_id[
                    category_id
                ]
            )

            remote_category = (
                remote_by_id[
                    category_id
                ]
            )

            cached_sections = {
                section["id"]: section
                for section in cached_category.get(
                    "sections",
                    []
                )
            }

            remote_sections = {
                section["id"]: section
                for section in remote_category.get(
                    "sections",
                    []
                )
            }

            added_sections = (
                remote_sections.keys()
                - cached_sections.keys()
            )

            removed_sections = (
                cached_sections.keys()
                - remote_sections.keys()
            )

            for section_id in sorted(
                added_sections
            ):

                print(
                    "[wiki] Nouvelle section : "
                    f"{remote_category['name']} > "
                    f"{remote_sections[section_id]['name']}"
                )

            for section_id in sorted(
                removed_sections
            ):

                print(
                    "[wiki] Section supprimee : "
                    f"{cached_category['name']} > "
                    f"{cached_sections[section_id]['name']}"
                )

        # -------------------------
        # Comparaison
        # -------------------------

        if old_cache == new_cache:

            print(
                "[wiki] Categories "
                "a jour."
            )

            return False

        print(
            "[wiki] Categories "
            "mises a jour."
        )

        return True

    def inspect_all_table_counts(
        self
    ):

        categories_path = (
            self.data_path
            / "categories.json"
        )

        with open(
            categories_path,
            "r",
            encoding="utf-8"
        ) as file:

            categories = json.load(
                file
            ).get(
                "categories",
                []
            )

        for category in categories:

            for section in category.get(
                "sections",
                []
            ):

                wiki_path = section.get(
                    "wiki_path"
                )

                if not wiki_path:
                    continue

                url = (
                    f"{self.base_url}"
                    f"{wiki_path}"
                )

                response = self.session.get(
                    url,
                    timeout=15
                )

                if response.status_code == 404:

                    print(
                        f"[404] "
                        f"{section['name']}"
                    )

                    continue

                response.raise_for_status()

                soup = BeautifulSoup(
                    response.text,
                    "html.parser"
                )

                content = soup.select_one(
                    "#mw-content-text"
                )

                if content is None:
                    continue

                tables = content.select(
                    "table"
                )

                if len(tables) != 1:

                    print(
                        f"[TABLES] "
                        f"{section['name']} "
                        f"-> {len(tables)}"
                    )

                time.sleep(
                    self.request_delay
                )

    def inspect_section(
        self,
        wiki_path="/wiki/Basic_Products_I"
    ):

        url = (
            f"{self.base_url}"
            f"{wiki_path}"
        )

        print(
            f"[wiki] Inspection : {url}"
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
                "le contenu de la section."
            )

        # -------------------------
        # Titres
        # -------------------------

        print(
            "\n=== TITRES ==="
        )

        for heading in content.select(
            "h1, h2, h3, h4"
        ):

            text = heading.get_text(
                " ",
                strip=True
            )

            if text:

                print(
                    f"{heading.name}: {text}"
                )

        # -------------------------
        # Tableaux
        # -------------------------

        tables = content.select(
            "table"
        )

        print(
            f"\n=== TABLEAUX : "
            f"{len(tables)} ==="
        )

        for index, table in enumerate(
            tables,
            start=1
        ):

            print(
                f"\n--- TABLE {index} ---"
            )

            rows = table.select(
                "tr"
            )

            for row in rows[:10]:

                cells = row.select(
                    "th, td"
                )

                values = [
                    cell.get_text(
                        " ",
                        strip=True
                    )
                    for cell in cells
                ]

                if values:

                    print(
                        values
                    )

    def sync_section_products(
        self,
        wiki_path
    ):

        url = (
            f"{self.base_url}"
            f"{wiki_path}"
        )

        print(
            f"[wiki] Produits : {url}"
        )

        response = None

        for attempt in range(
            4
        ):

            response = self.session.get(
                url,
                timeout=15
            )

            if response.status_code != 429:
                break

            wait_time = (
                5
                * (
                    attempt + 1
                )
            )

            print(
                f"[wiki] Limite atteinte. "
                f"Nouvel essai dans "
                f"{wait_time}s..."
            )

            time.sleep(
                wait_time
            )

        if response.status_code == 404:

            print(
                f"[wiki] Page introuvable : "
                f"{wiki_path}"
            )

            print(
                "[wiki] Section ignoree."
            )

            return []

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
                "le contenu de la section."
            )

        table = content.select_one(
            "table"
        )

        if table is None:

            print(
                "[wiki] Aucun tableau trouvé."
            )

            return []

        rows = table.select(
            "tr"
        )

        if not rows:

            return []

        # -------------------------
        # Recherche des vrais en-têtes
        # -------------------------

        headers = []
        header_index = None

        for index, row in enumerate(
            rows
        ):

            candidate_headers = [
                " ".join(
                    cell.get_text(
                        " ",
                        strip=True
                    ).split()
                )
                for cell in row.select(
                    "th, td"
                )
            ]

            if (
                "Product Name"
                in candidate_headers
                or "Name"
                in candidate_headers
            ):

                headers = (
                    candidate_headers
                )

                header_index = index

                break

        if header_index is None:

            print(
                "[wiki] En-têtes produits "
                "introuvables."
            )

            return []

        products = []

        # -------------------------
        # Produits
        # -------------------------

        for row in rows[
            header_index + 1:
        ]:

            cells = row.select(
                "th, td"
            )

            values = [
                cell.get_text(
                    " ",
                    strip=True
                )
                for cell in cells
            ]

            if len(
                values
            ) < len(
                headers
            ):

                continue

            if len(
                values
            ) > len(
                headers
            ):

                values = values[
                    :len(headers)
                ]

            data = {
                " ".join(
                    header.split()
                ): value
                for header, value in zip(
                    headers,
                    values
                )
            }

            product_name = (
                data.get(
                    "Product Name"
                )
                or data.get(
                    "Name"
                )
            )

            if not product_name:
                continue

            product = {
                "name": product_name,
                "brand": data.get(
                    "Brand Name",
                    ""
                ),
                "amount_per_box": (
                    data.get(
                        "Amt. Per Box"
                    )
                    or data.get(
                        "Max Items Per Box"
                    )
                    or ""
                ),
                "price_per_box": data.get(
                    "Starting Price per Box",
                    ""
                ),
                "price_per_unit": data.get(
                    "Starting Price per Unit",
                    ""
                ),
                "wiki_path": wiki_path,
            }

            products.append(
                product
            )

        print(
            f"[wiki] {len(products)} "
            f"produit(s) détecté(s)."
        )

        for product in products:

            print(
                f"[wiki] "
                f"{product['name']} | "
                f"{product['brand']} | "
                f"{product['price_per_unit']}"
            )

        return products

    def sync_all_products(
        self
    ):

        categories_path = (
            self.data_path
            / "categories.json"
        )

        if not categories_path.exists():

            raise RuntimeError(
                "categories.json introuvable. "
                "Lancez d'abord sync_categories()."
            )

        with open(
            categories_path,
            "r",
            encoding="utf-8"
        ) as file:

            categories_data = json.load(
                file
            )

        categories = categories_data.get(
            "categories",
            []
        )

        products = []

                # -------------------------
        # Progression globale
        # -------------------------

        total_sections = sum(
            len(
                category.get(
                    "sections",
                    []
                )
            )
            for category in categories
        )

        current_section = 0

        # -------------------------
        # Parcours des sections
        # -------------------------

        for category in categories:

            category_id = category.get(
                "id"
            )

            category_name = category.get(
                "name"
            )

            for section in category.get(
                "sections",
                []
            ):

                section_id = section.get(
                    "id"
                )

                section_name = section.get(
                    "name"
                )

                wiki_path = section.get(
                    "wiki_path"
                )

                if not wiki_path:
                    continue

                current_section += 1

                percent = int(
                    current_section
                    / total_sections
                    * 100
                )

                print(
                    "\n"
                    "========================================"
                )

                print(
                    f"[GLOBAL] "
                    f"{current_section} / "
                    f"{total_sections} "
                    f"({percent}%)"
                )

                print(
                    f"[CURRENT] "
                    f"{category_name} > "
                    f"{section_name}"
                )

                print(
                    f"[PRODUCTS] "
                    f"{len(products)} "
                    f"produit(s) recuperes"
                )

                print(
                    "========================================"
                )

                print(
                    f"\n[wiki] "
                    f"{category_name} > "
                    f"{section_name}"
                )

                section_products = (
                    self.sync_section_products(
                        wiki_path
                    )
                )

                time.sleep(
                    self.request_delay
                )

                for product in section_products:

                    product[
                        "category_id"
                    ] = category_id

                    product[
                        "section_id"
                    ] = section_id

                products.extend(
                    section_products
                )

                print(
                    f"[PRODUCTS] "
                    f"{len(products)} "
                    f"produit(s) au total"
                )

        # -------------------------
        # Sauvegarde
        # -------------------------

        products_path = (
            self.data_path
            / "products.json"
        )

        products_data = {
            "products": products
        }

        with open(
            products_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                products_data,
                file,
                ensure_ascii=False,
                indent=4
            )

        print(
            f"\n[wiki] "
            f"{len(products)} produit(s) "
            f"récupéré(s) au total."
        )

        print(
            f"[wiki] Cache produits sauvegardé : "
            f"{products_path}"
        )

        return products

    def inspect_category_anchor(
        self,
        anchor_id
    ):

        url = (
            f"{self.base_url}"
            "/wiki/Product_Categories"
        )

        response = self.session.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        anchor = soup.find(
            id=anchor_id
        )

        if anchor is None:

            print(
                f"[wiki] Ancre introuvable : "
                f"{anchor_id}"
            )

            return

        print(
            f"\n=== ANCRE : "
            f"{anchor_id} ===\n"
        )

        current = anchor

        for _ in range(
            10
        ):

            current = (
                current.find_next()
            )

            if current is None:
                break

            print(
                current.name,
                "->",
                current.get_text(
                    " ",
                    strip=True
                )[:300]
            )

    def inspect_category_links(
        self,
        category_name
    ):

        url = (
            f"{self.base_url}"
            "/wiki/Product_Categories"
        )

        response = self.session.get(
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

            print(
                "[wiki] Contenu introuvable."
            )

            return

        print(
            f"\n=== LIENS : "
            f"{category_name} ===\n"
        )

        for link in content.select(
            "a[href]"
        ):

            name = link.get_text(
                " ",
                strip=True
            )

            href = link.get(
                "href",
                ""
            )

            if (
                category_name.lower()
                in name.lower()
                or category_name.lower()
                .replace(" ", "_")
                in href.lower()
            ):

                print(
                    repr(name),
                    "->",
                    href
                )

wiki_sync = WikiSync()

def main():

    dev_console.open(
        __file__
    )

    print(
        "SMT Companion - Wiki Sync\n"
    )

    wiki_sync.sync_all_products()

    print(
        "\n[wiki] Synchronisation terminee."
    )

    input(
        "\nAppuyez sur Entree pour fermer..."
    )


if __name__ == "__main__":

    try:

        main()

    except KeyboardInterrupt:

        print(
            "\n\n[wiki] Synchronisation interrompue."
        )

        input(
            "\nAppuyez sur Entree pour fermer..."
        )

    except Exception:

        import traceback

        print(
            "\n\n"
            "========================================"
        )

        print(
            "ERREUR WIKI SYNC"
        )

        print(
            "========================================\n"
        )

        traceback.print_exc()

        input(
            "\nAppuyez sur Entree pour fermer..."
        )