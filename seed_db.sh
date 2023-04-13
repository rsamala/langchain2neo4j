#!/usr/bin/env bash

pip install neo4j pandas gdown tqdm

FILE_ID="1ELuq3k1LtZZ_qt7nxe-H6PyHlyl_p3wG"
DESTINATION="movie_embeddings.csv"

# Check if the file already exists
if [ ! -f "$DESTINATION" ]; then
  # If the file doesn't exist, download it using gdown
  gdown $FILE_ID
else
  echo "File already exists: $DESTINATION"
fi

python data/import.py