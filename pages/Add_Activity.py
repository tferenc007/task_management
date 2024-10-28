
import streamlit as st
# Function to create collapsible forms
def create_form(form_name):
    with st.expander(form_name, expanded=True):
        st.write("stories description")
        s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
        with s_col1:
            st.button("Task 1",use_container_width=False,key="task_button_id")
            st.button("Task 3")

        with s_col2:
            st.button("Task 2",use_container_width=False)
            st.button("Task 4")
            
def create_form2(form_name):
    with st.expander(form_name, expanded=True):
        s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
        with s_col1:
            st.button("Task 9",use_container_width=False)
            st.button("Task 99")

        with s_col2:
            st.button("Task 45",use_container_width=False)
            st.button("Task 65")
class AddActivity():
    def __init__(self):
    # Create 5 buttons and corresponding forms

        st.set_page_config(layout="wide")
        st.markdown("<h1 style='text-align: center;'>Add Activity</h1>", unsafe_allow_html=True)
        # Filters section
        e_col_1, e_col_2, e_col_3 = st.columns(3)
        e_col_1.button("Epic 1",use_container_width=True)
        e_col_2.button("Epic 2",use_container_width=True)
        e_col_3.button("Epic 3",use_container_width=True)
        # Create 3 columns

        with st.sidebar:
            with st.container(border=True):
                st.text("Story 1 > Task 1")
                st.date_input("date")
                st.button("Complete Task")



        create_form("Story 1")
        create_form2("Story 2")


page_view = AddActivity()