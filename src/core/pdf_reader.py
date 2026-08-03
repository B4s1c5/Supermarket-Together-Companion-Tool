import pdfplumber

from core.product import Product


class PDFReader:

    def __init__(self):
        pass

    def read(self, pdf_path):

        products = []
        table_data = []

        with pdfplumber.open(pdf_path) as pdf:

            for page in pdf.pages:

                table = page.extract_table()

                if table:

                    table_data.extend(table)

        # -----------------------------------------
        # Suppression des en-têtes PDF répétés
        # -----------------------------------------

        cleaned_data = []
        header_found = False

        for row in table_data:

            if not row:
                continue

            normalized_row = [
                str(value).strip().upper()
                if value is not None
                else ""
                for value in row
            ]

            is_header = (
                "PRODUCT" in normalized_row
                and "LICENSE" in normalized_row
                and "DISP" in normalized_row
            )

            if is_header:

                if header_found:
                    # En-tête répété d'une nouvelle page
                    continue

                # Premier en-tête : on le conserve
                header_found = True

            cleaned_data.append(row)

        table_data = cleaned_data

        # -----------------------------------------
        # Création des produits
        # -----------------------------------------

        for row in table_data:

            if not row:
                continue

            if len(row) <= 4:
                continue

            product_text = row[4]

            if not product_text:
                continue

            product_text = product_text.replace("\n", " ")

            if " - " not in product_text:
                continue

            product_name, brand = product_text.rsplit(" - ", 1)

            product = Product(product_name, brand)

            products.append(product)

        return products, table_data