import streamlit as st # type: ignore

st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
st.selectbox("Select View",("Current"))
with st.container(border=True):
    con_col1, con_col2 = st.columns(2)
    con_col1.write("Last Activity")
    con_col2.write("2024-10-21")
with st.container(border=True):
    st.markdown("<h5 style='text-align: center;'>Current Sprint: from 2024-10-21 to 2024-10-27</h5>", unsafe_allow_html=True)    
    con_col1, con_col2 = st.columns(2)
    con_col1.write("Stories")
    con_col1.text("1/3")
    con_col2.write("Tasks")    
    con_col2.text("4/12")   
with st.container(border=True):
    st.markdown("<h5 style='text-align: center;'>Current Sprint: from 2024-10-21 to 2024-10-27</h5>", unsafe_allow_html=True)    
    con_col1, con_col2 = st.columns(2,)
    con_col1.text("Story 1")
    con_col2.text("1/4")    
    con_col1.text("Story 2")
    con_col2.text("4/12")
    con_col1.text("Story 3")
    con_col2.text("0/3")      
    