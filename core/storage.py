import os
import duckdb
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from urllib.request import urlopen

# Local Data Paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEAN_DIR = os.path.join(DATA_DIR, "clean")
DB_PATH = os.path.join(DATA_DIR, "healthcare.duckdb")

class MinioStorage:
    def __init__(self, endpoint="localhost:9000", access_key="admin", secret_key="password", secure=False):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket = "raw-data"
        self._ensure_bucket()

    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as err:
            print(f"Minio Error: {err}")

    def save_raw_data(self, object_name: str, data: bytes):
        """Save raw bytes to MinIO"""
        try:
            self.client.put_object(
                self.bucket, object_name, BytesIO(data), length=len(data)
            )
            print(f"Saved {object_name} to MinIO bucket '{self.bucket}'.")
        except S3Error as err:
            print(f"Failed to save {object_name}: {err}")

class DuckDBStorage:
    def __init__(self, db_path=DB_PATH):
        # We ensure parent dir exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = duckdb.connect(db_path)

    def execute(self, query: str):
        return self.conn.execute(query).df()

    def load_parquet(self, table_name: str, parquet_path: str):
        query = f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM read_parquet('{parquet_path}');"
        self.conn.execute(query)
        print(f"Loaded {parquet_path} into table {table_name}")

    def close(self):
        self.conn.close()

# For local MVP without MinIO running, we can also use file system fallback
def save_raw_local(filename: str, data: bytes):
    os.makedirs(RAW_DIR, exist_ok=True)
    filepath = os.path.join(RAW_DIR, filename)
    with open(filepath, 'wb') as f:
        f.write(data)
    print(f"Saved local raw file: {filepath}")
    return filepath
