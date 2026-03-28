# schema_generator/__init__.py

from .infer import infer_sql_types
from .generator import generate_ddl

__version__ = "0.1.0"
__all__ = ["infer_sql_types", "generate_ddl"]