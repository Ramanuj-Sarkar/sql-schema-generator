# CLI entry point

import typer
import pandas as pd
from schema_generator.infer import infer_sql_types
from schema_generator.generator import generate_ddl

app = typer.Typer()

@app.command()
def generate(
    input: str = typer.Argument(..., help="Path to CSV or JSON file"),
    table: str = typer.Option("my_table", help="Table name"),
    primary_key: str = typer.Option(None, help="Column to use as PRIMARY KEY"),
    output: str = typer.Option(None, help="Write SQL to file instead of stdout"),
):
    if input.endswith(".csv"):
        df = pd.read_csv(input)
    elif input.endswith(".json"):
        df = pd.read_json(input)
    else:
        typer.echo("Unsupported format. Use CSV or JSON.")
        raise typer.Exit(1)

    schema = infer_sql_types(df)
    ddl = generate_ddl(table, schema, primary_key)

    if output:
        with open(output, "w") as f:
            f.write(ddl)
        typer.echo(f"Schema written to {output}")
    else:
        typer.echo(ddl)

if __name__ == "__main__":
    app()