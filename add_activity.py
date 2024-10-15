
import streamlit as st # type: ignore
import pandas as pd # type: ignore

st.set_page_config(layout="wide")
 
col1, col2 = st.columns(2)

with col1:
    st.title("Place holder")

with col2:
    st.title("Tomasz Ferenc")
    content = """
    Hi, I am Tomek! A highly skilled professional with a background in Management and Production Engineering, specializing in Logistics.
    Possesses extensive experience in business intelligence development, data analysis, and process improvement.
    Currently expanding expertise by learning Python, alongside advanced SQL skills, data warehousing, and data engineering techniques.
    Proficient in SQL (MS SQL Server, Snowflake) and DBT, with advanced proficiency in Git for version control. Additionally, holds advanced proficiency in Tableau (First level of certification) and Alteryx Designer (Core and Advanced Certification), enabling the creation of sophisticated analytical solutions. Adept at collaborating with stakeholders to gather requirements and deliver tailored solutions. Demonstrated ability to thrive in international environments and effectively address business challenges.
    """
    st.info(content)
content2 = """
Below you can find some of the apps I have built in Python. Feel free to contact me!
"""
st.write(content2)

col3, empty_col, col4 = st.columns([1.5, 0.5, 1.5])

