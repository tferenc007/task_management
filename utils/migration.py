
# migrate_quick.py
import os
import sqlite3 as sq
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
from sqlalchemy.engine import URL
import streamlit as st



if __name__ == "__main__":
    PG_USER = st.secrets["db"]['PG_USER']
    PG_PASSWORD = st.secrets["db"]['PG_PASSWORD']
    PG_HOST = st.secrets["db"]['PG_HOST']
    PG_PORT = st.secrets["db"]['PG_PORT']
    PG_DB = st.secrets["db"]['PG_DB']
    PG_SCHEMA =  st.secrets["db"]['PG_SCHEMA']

    url = URL.create(
        "postgresql+psycopg2",
        username=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        query={"sslmode": "require"},
    )

    # Nie musisz tworzyć 'engine' wcześniej — przekaż URL do migrate_quick
    SQLITE_PATH = "data/database.db"
    SCHEMA = "public"

    conn = sq.connect('data/database.db')
    tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn, dtype=str)
    epic_df = pd.read_sql_query("SELECT * FROM epics", conn, dtype=str)
    stories_df = pd.read_sql_query("SELECT * FROM stories", conn, dtype=str)
    objectives_df = pd.read_sql_query("SELECT * FROM objectives", conn, dtype=str)
        

        
    conn.close()


# ... Twój kod powyżej (URL.create, wczytanie tasks_df) ...

engine = create_engine(url)

tasks_df.to_sql(
    name="tasks",
    con=engine,
    schema=PG_SCHEMA,     # lub Twój schemat
    if_exists="replace",  # "fail" | "replace" | "append"
    index=False,
    method="multi"       # batch insert (szybciej)
)

epic_df.to_sql(
    name="epics",
    con=engine,
    schema=PG_SCHEMA,     # lub Twój schemat
    if_exists="replace",  # "fail" | "replace" | "append"
    index=False,
    method="multi"       # batch insert (szybciej)
)
stories_df.to_sql(
    name="stories",
    con=engine,
    schema=PG_SCHEMA,     # lub Twój schemat
    if_exists="replace",  # "fail" | "replace" | "append"
    index=False,
    method="multi"       # batch insert (szybciej)
)
objectives_df.to_sql(
    name="objectives",
    con=engine,
    schema=PG_SCHEMA,     # lub Twój schemat
    if_exists="replace",  # "fail" | "replace" | "append"
    index=False,
    method="multi"       # batch insert (szybciej)
)
