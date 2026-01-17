
# migrate_quick.py
import os
import sqlite3 as sq
import pandas as pd
from sqlalchemy import create_engine, text
from tqdm import tqdm
from sqlalchemy.engine import URL
import streamlit as st
from utils.secrets import get_secret

PG_HOST = get_secret("PG_HOST", section="db")  # najpierw st.secrets["db"]["PG_HOST"], potem ENV: DB_PG_HOST
PG_PORT = get_secret("PG_PORT", section="db", default=5432, cast=int)
PG_USER = get_secret("PG_USER", section="db")
PG_PASSWORD = get_secret("PG_PASSWORD", section="db")
PG_DB = get_secret("PG_DB", section="db")
PG_SCHEMA = get_secret("PG_SCHEMA", section="db")


def schema():
    return PG_SCHEMA
def pg_conn():
    url = URL.create(
        "postgresql+psycopg2",
        username=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
        query={"sslmode": "require"},
    )
    return create_engine(url)

if __name__ == "__main__":
    pass