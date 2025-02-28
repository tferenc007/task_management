
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time




class Objectives():
    def __init__(self):
        st.title("Add New Objective")
        with st.container(border=True):   
            objective_name = st.text_input("Objective Name")
            objective_description = st.text_area("Objective Description")
            objective_due_date = st.selectbox("Select PI", ["P1", "P2", "P3", "P4"])

            if st.checkbox("Is this a life objective?", value=False):
                pass
            else:
                st.selectbox("Select Life Objective Category", ["fdsa", "Career", "Personal Development", "Relationships"])
            submit_button = st.button(label='Add Objective')

            if submit_button:
                
                st.success("Objective added successfully!")




    


page_view = Objectives()
