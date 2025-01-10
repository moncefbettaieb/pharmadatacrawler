cut -d',' -f1 /Users/mbettaieb/Downloads/open4goods-gtin-dataset.csv > gtin.csv

cut -d',' -f1 /Users/mbettaieb/Downloads/open4goods-isbn-dataset.csv > isbn.csv

pharma_go_api=# \copy gtin FROM '/Users/mbettaieb/Downloads/gtin.csv' CSV HEADER

pharma_go_api=# \copy isbn FROM '/Users/mbettaieb/Downloads/isbn.csv' CSV HEADER