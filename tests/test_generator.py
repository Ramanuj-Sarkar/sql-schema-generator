# tests/test_generator.py

import pytest
import pandas as pd
from schema_generator.infer import infer_sql_types
from schema_generator.generator import generate_ddl


# ── Fixtures ────────────────────────────────────────────────

@pytest.fixture
def basic_df():
    return pd.DataFrame({
        "lot_number": ["BMR-001", "BMR-002"],
        "batch_size": [500.0, 750.5],
        "quantity": [100, 200],
        "approved": [True, False],
        "notes": [None, "Passed QC"],
    })


@pytest.fixture
def basic_schema(basic_df):
    return infer_sql_types(basic_df)


# ── infer_sql_types tests ────────────────────────────────────

def test_infers_float(basic_schema):
    assert basic_schema["batch_size"]["sql_type"] == "FLOAT"


def test_infers_integer(basic_schema):
    assert basic_schema["quantity"]["sql_type"] == "INTEGER"


def test_infers_boolean(basic_schema):
    assert basic_schema["approved"]["sql_type"] == "BOOLEAN"


def test_infers_text(basic_schema):
    assert basic_schema["lot_number"]["sql_type"] == "TEXT"


def test_nullable_column_detected(basic_schema):
    assert basic_schema["notes"]["nullable"] is True


def test_non_nullable_column_detected(basic_schema):
    assert basic_schema["batch_size"]["nullable"] is False


def test_max_len_computed_for_text(basic_schema):
    # "BMR-001" and "BMR-002" are both 7 chars
    assert basic_schema["lot_number"]["max_len"] == 7


def test_max_len_none_for_non_text(basic_schema):
    assert basic_schema["quantity"]["max_len"] is None


def test_datetime_inference():
    df = pd.DataFrame({"created_at": pd.to_datetime(["2024-01-01", "2024-06-15"])})
    schema = infer_sql_types(df)
    assert schema["created_at"]["sql_type"] == "TIMESTAMP"


def test_empty_dataframe_returns_empty_schema():
    df = pd.DataFrame()
    schema = infer_sql_types(df)
    assert schema == {}


# ── generate_ddl tests ───────────────────────────────────────

def test_ddl_contains_table_name(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema)
    assert "CREATE TABLE batch_records" in ddl


def test_ddl_contains_all_columns(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema)
    for col in ["lot_number", "batch_size", "quantity", "approved", "notes"]:
        assert col in ddl


def test_ddl_nullable_column_has_null(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema)
    # notes is nullable
    assert "notes" in ddl
    # find the notes line and check it says NULL not NOT NULL
    notes_line = [l for l in ddl.splitlines() if "notes" in l][0]
    assert "NOT NULL" not in notes_line


def test_ddl_non_nullable_has_not_null(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema)
    qty_line = [l for l in ddl.splitlines() if "quantity" in l][0]
    assert "NOT NULL" in qty_line


def test_primary_key_applied(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema, primary_key="lot_number")
    pk_line = [l for l in ddl.splitlines() if "lot_number" in l][0]
    assert "PRIMARY KEY" in pk_line


def test_no_primary_key_by_default(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema)
    assert "PRIMARY KEY" not in ddl


def test_short_text_uses_varchar(basic_schema):
    # lot_number max_len=7, so should become VARCHAR not TEXT
    ddl = generate_ddl("batch_records", basic_schema)
    lot_line = [l for l in ddl.splitlines() if "lot_number" in l][0]
    assert "VARCHAR" in lot_line


def test_ddl_is_valid_sql_structure(basic_schema):
    ddl = generate_ddl("batch_records", basic_schema)
    assert ddl.startswith("CREATE TABLE")
    assert ddl.strip().endswith(";")
    assert "(" in ddl and ")" in ddl
