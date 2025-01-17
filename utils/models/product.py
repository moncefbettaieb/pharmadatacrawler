class Product:
    def __init__(self, cip_code, name=None, description=None, image_links=None):
        self.cip_code = cip_code
        self.name = name
        self.description = description
        self.image_links = image_links or []

    def __repr__(self):
        return f"Product(cip_code={self.cip_code}, name={self.name})"