
# utils/secrets.py
import os
from typing import Any, Optional
import streamlit as st

def get_secret(
    key: str,
    section: Optional[str] = None,
    default: Optional[Any] = None,
    cast: Optional[type] = None,
) -> Any:
    """
    Pobiera sekret wg kolejności:
      1) st.secrets[section][key] lub st.secrets[key]
      2) os.environ[f"{section}_{key}"] (jeśli section podane) lub os.environ[key]
      3) default
    Opcjonalnie rzutuje wynik na typ (cast=int/bool/float itp.).
    """
    # 1) Streamlit Cloud / lokalny secrets.toml (jeśli istnieje)
    try:
        if section:
            if section in st.secrets and key in st.secrets[section]:
                value = st.secrets[section][key]
                return cast(value) if (cast and value is not None) else value
        else:
            if key in st.secrets:
                value = st.secrets[key]
                return cast(value) if (cast and value is not None) else value
    except Exception:
        # st.secrets może nie być dostępne poza kontekstem Streamlit – ignorujemy
        pass

    # 2) ENV (próba z prefiksem section_key, potem bez)
    env_key = f"{section}_{key}".upper() if section else key.upper()
    value = os.getenv(env_key)
    if value is None and not section:
        # opcjonalny fallback na oryginalną nazwę, gdyby była w innej konwencji
        value = os.getenv(key)

    if value is not None:
        return cast(value) if cast else value

    # 3) default
    if default is not None:
        return default

    # Jeżeli brak i brak default → podnieś czytelny wyjątek
    raise KeyError(f"Secret '{section}.{key}' nie znaleziony w st.secrets ani w ENV")
