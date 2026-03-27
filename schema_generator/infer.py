# type inference logic

import pandas as pd

TYPE_MAP = {
    "int64": "INTEGER",
    "float64": "FLOAT",
    "bool": "BOOLEAN",
    "datetime64[ns]": "TIMESTAMP",
    "object": "TEXT",
}

def infer_sql_types(df: pd.DataFrame) -> dict:
    schema = {}
    for col in df.columns:
        dtype = str(df[col].dtype)
        nullable = df[col].isnull().any()
        max_len = df[col].astype(str).str.len().max() if dtype == "object" else None
        schema[col] = {
            "sql_type": TYPE_MAP.get(dtype, "TEXT"),
            "nullable": nullable,
            "max_len": max_len,
        }
    return schema