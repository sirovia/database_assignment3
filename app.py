import os
from typing import Any, Dict, Iterable, List, Mapping

from flask import Flask, abort, flash, redirect, render_template, request, url_for
from sqlalchemy import MetaData, Table, create_engine, func, select
from sqlalchemy.engine import Engine, Row
from sqlalchemy.exc import SQLAlchemyError


def python_type_for(column) -> Any:
    try:
        return column.type.python_type
    except NotImplementedError:
        return str


def coerce_value(column, value: str) -> Any:
    if value == "":
        return None
    python_type = python_type_for(column)
    if python_type is bool:
        return value.lower() in {"1", "true", "yes", "on"}
    if python_type is int:
        return int(value)
    if python_type is float:
        return float(value)
    return python_type(value)


def normalize_database_url(database_url: str) -> str:
    """Ensure SQLAlchemy understands URLs from managed hosts like Render."""
    database_url = database_url.strip()
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg2://", 1)
    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"
    return database_url


def make_engine() -> Engine:
    """Create a SQLAlchemy engine using DATABASE_URL or the local default."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = "sqlite:///local.db"
    database_url = normalize_database_url(database_url)
    return create_engine(database_url, future=True)


engine = make_engine()

# Initialize database on first run
try:
    from init_db import init_database
    init_database()
except Exception as e:
    print(f"Note: Database initialization skipped: {e}")

metadata = MetaData()
metadata.reflect(bind=engine)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")
app.jinja_env.globals["python_type_for"] = python_type_for


def get_table_or_404(table_name: str) -> Table:
    table = metadata.tables.get(table_name)
    if table is None:
        abort(404, description=f"Unknown table '{table_name}'")
    return table


def build_payload(table: Table, form_data: Mapping[str, str]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for column in table.columns:
        python_type = python_type_for(column)
        if column.name not in form_data:
            if python_type is bool:
                payload[column.name] = False
            continue
        raw_value = form_data.get(column.name, "")
        if raw_value == "" and column.autoincrement:
            continue
        payload[column.name] = coerce_value(column, raw_value)
    return payload


def build_pk_filters(table: Table, source: Mapping[str, str]) -> List[Any]:
    filters = []
    for column in table.primary_key.columns:
        if column.name not in source:
            abort(400, description=f"Missing primary key field '{column.name}'")
        filters.append(column == coerce_value(column, source[column.name]))
    return filters


def rows_with_metadata(table: Table, raw_rows: Iterable[Row]) -> List[Dict[str, Any]]:
    rows = []
    pk_columns = [col.name for col in table.primary_key.columns]
    for raw in raw_rows:
        mapping = dict(raw._mapping)
        pk_values = {pk: mapping[pk] for pk in pk_columns}
        edit_url = url_for("edit_record", table_name=table.name, **pk_values)
        rows.append({"data": mapping, "pk": pk_values, "edit_url": edit_url})
    return rows


@app.route("/")
def index():
    tables = sorted(metadata.tables.values(), key=lambda t: t.name)
    counts: Dict[str, int] = {}
    with engine.connect() as conn:
        for table in tables:
            counts[table.name] = conn.execute(
                select(func.count()).select_from(table)
            ).scalar_one()
    return render_template("index.html", tables=tables, counts=counts)


@app.route("/table/<table_name>")
def view_table(table_name: str):
    table = get_table_or_404(table_name)
    with engine.connect() as conn:
        result = conn.execute(select(table))
        rows = rows_with_metadata(table, result)
    return render_template(
        "table.html",
        table=table,
        rows=rows,
    )


@app.route("/table/<table_name>/create", methods=["GET", "POST"])
def create_record(table_name: str):
    table = get_table_or_404(table_name)
    if request.method == "POST":
        payload = build_payload(table, request.form)
        try:
            with engine.begin() as conn:
                conn.execute(table.insert().values(**payload))
            flash(f"Created record in '{table_name}'.", "success")
        except SQLAlchemyError as exc:
            flash(f"Create failed: {exc}", "error")
        return redirect(url_for("view_table", table_name=table_name))

    return render_template(
        "form.html",
        table=table,
        values={},
        action="Create",
        pk_fields=[],
    )


@app.route("/table/<table_name>/edit", methods=["GET", "POST"])
def edit_record(table_name: str):
    table = get_table_or_404(table_name)
    pk_filters = build_pk_filters(table, request.values if request.method == "POST" else request.args)

    if request.method == "POST":
        payload = build_payload(table, request.form)
        try:
            with engine.begin() as conn:
                conn.execute(table.update().where(*pk_filters).values(**payload))
            flash(f"Updated record in '{table_name}'.", "success")
        except SQLAlchemyError as exc:
            flash(f"Update failed: {exc}", "error")
        return redirect(url_for("view_table", table_name=table_name))

    with engine.connect() as conn:
        row = conn.execute(select(table).where(*pk_filters)).first()
    if row is None:
        abort(404, description="Record not found")

    return render_template(
        "form.html",
        table=table,
        values=dict(row._mapping),
        action="Update",
        pk_fields=[col.name for col in table.primary_key.columns],
    )


@app.route("/table/<table_name>/delete", methods=["POST"])
def delete_record(table_name: str):
    table = get_table_or_404(table_name)
    pk_filters = build_pk_filters(table, request.form)
    try:
        with engine.begin() as conn:
            conn.execute(table.delete().where(*pk_filters))
        flash(f"Deleted record from '{table_name}'.", "success")
    except SQLAlchemyError as exc:
        flash(f"Delete failed: {exc}", "error")
    return redirect(url_for("view_table", table_name=table_name))


if __name__ == "__main__":
    app.run(debug=True)

