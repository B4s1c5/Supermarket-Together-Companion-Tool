class Product:

    def __init__(self, product_name, brand):

        self.product_name = product_name

        self.brand = brand

        self.translated_name = ""


    def __str__(self):

        if self.translated_name:
            return f"{self.translated_name} - {self.brand}"

        return f"{self.product_name} - {self.brand}"


    def translate(self, translated_name):

        self.translated_name = translated_name