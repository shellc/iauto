from typing import Any, Dict, Optional

import pandas as pd
import sqlalchemy

from ..loader import register


@register(name="db.create_engine", spec={
    "description": "Create a new SQLAlchemy engine instance.",
    "arguments": [
        {
            "name": "url",
            "description": "Database connection URL in the SQLAlchemy format.",
            "type": "string",
            "required": True
        }
    ]
})
def create_engine(*args, url: str, **kwargs) -> sqlalchemy.Engine:
    return sqlalchemy.create_engine(url)


@register(name="db.read", spec={
    "description": "Read data from the database into a DataFrame or a list of dictionaries.",
    "arguments": [
        {
            "name": "sql",
            "description": "SQL query string to be executed.",
            "type": "string",
            "required": True
        },
        {
            "name": "return_type",
            "description": "The format in which to return the data. Options are 'dataframe' or 'dict'. Defaults to 'dataframe'.",  # noqa: E501
            "type": "string",
            "required": False
        }
    ]
})
def read(
    *args,
    engine: sqlalchemy.Engine,
    sql: str,
    return_type: Optional[str] = None,
    **kwargs
) -> Any:
    df = pd.read_sql(sql=sql, con=engine)

    return_type = (return_type or "").lower()
    if return_type == "dataframe":
        return df
    else:
        return df.to_dict(orient='records')


@register(name="db.exec", spec={
    "description": "Execute an SQL statement.",
    "arguments": [
        {
            "name": "sql",
            "description": "SQL statement to be executed.",
            "type": "string",
            "required": True
        },
        {
            "name": "values",
            "description": "Optional dictionary of parameters to pass to the SQL statement.",
            "type": "dict",
            "required": False
        }
    ]
})
def exec(
    *args,
    engine: sqlalchemy.Engine,
    sql: str,
    values: Optional[Dict] = None,
    **kwargs
) -> Any:
    text = sqlalchemy.text(sql)

    with engine.connect() as conn:
        if values is None:
            conn.execute(text)
        else:
            conn.execute(text, values)
        conn.commit()


@register(name="db.select", spec={
    "description": "Execute a select statement and return the results.",
    "arguments": [
        {
            "name": "sql",
            "description": "SQL select query to be executed.",
            "type": "string",
            "required": True
        },
        {
            "name": "values",
            "description": "Optional dictionary of parameters to pass to the SQL select query.",
            "type": "dict",
            "required": False
        }
    ]
})
def select(
    *args,
    engine: sqlalchemy.Engine,
    sql: str,
    values: Optional[Dict] = None,
    **kwargs
) -> Any:
    text = sqlalchemy.text(sql)

    with engine.connect() as conn:
        if values is None:
            cursor = conn.execute(text)
        else:
            cursor = conn.execute(text, values)

        columns = list(cursor.keys())
        rows = cursor.all()

        if len(rows) == 0:
            return None
        elif len(rows) == 1:
            return dict(zip(columns, rows[0]))
        else:
            return [dict(zip(columns, r)) for r in rows]
