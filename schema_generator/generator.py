# SQL DDL Generation

def generate_ddl(table_name: str, schema: dict, primary_key: str = None) -> str:
    lines = []
    for col, meta in schema.items():
        sql_type = meta["sql_type"]
        if sql_type == "TEXT" and meta["max_len"] and meta["max_len"] <= 255:
            sql_type = f"VARCHAR({int(meta['max_len'] * 1.5)})"  # buffer
        null_str = "NULL" if meta["nullable"] else "NOT NULL"
        pk_str = " PRIMARY KEY" if col == primary_key else ""
        lines.append(f"    {col} {sql_type} {null_str}{pk_str}")

    cols_sql = ",\n".join(lines)
    return f"CREATE TABLE {table_name} (\n{cols_sql}\n);"