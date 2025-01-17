CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    cip_code BIGINT NOT NULL,
    title TEXT,
    brand TEXT,
    short_desc TEXT,
    long_desc TEXT,
    composition TEXT,
    posologie TEXT,
    contre_indication TEXT,
    conditionnement TEXT,
    categorie TEXT,
    sous_categorie_1 TEXT,
    sous_categorie_2 TEXT,
    price TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS images (
    id SERIAL PRIMARY KEY,
    cip_code BIGINT REFERENCES products(cip_code),
    image_url TEXT NOT NULL,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
