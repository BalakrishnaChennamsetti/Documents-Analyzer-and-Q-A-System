import pandas as pd
from backend.vectordb import store_vector
import io

def ingest_csv_file(csv_bytes):
    df = pd.read_csv(io.BytesIO(csv_bytes))
    combined_string = df.to_csv(index=False)

    store_vector(combined_string, {"type": "csv"})
