
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time

tasktm = tm.TaskManagement()

class Edit():
    def __init__(self, tasktm):
        self.tasktm = tasktm
        st.markdown("<h1 style='text-align: center;'>Add/Edit</h1>", unsafe_allow_html=True)


        selected_epic = st.selectbox("Select Epic",tasktm.epics_to_list('name'))
        epic_col = st.columns([0.02, 0.98])

        with epic_col[1].expander("Edit Epic"):
            new_epic_name = self.edit_epic(selected_epic)
        with epic_col[1].expander("Add New Story"):
           st.write("cos")
        st.text("--Story List--")
        story_col = st.columns([0.02, 0.98])   
        with story_col[1].expander("Story 1"):
            st.button("Edit Story")
            st.button("Add New Task")
            st.markdown("---")
            st.button("Task 1 edit/remove")
            st.button("Task 2 edit/remove")
            st.button("Task 3 edit/remove")
            

        with st.sidebar:

            st.markdown("---")
            st.write("Edit Story")
            st.text_input("Name", key="story_name")
            st.text_input("Description", key="story_description")
            st.date_input("Est Start Date")
            st.date_input("Est End Date")

            st.markdown("---")
            st.write("Task 1 Edit")
            st.text_input("Task Name",disabled=True, value="Task 1")
            st.text_input("Description")
            is_completed = st.checkbox("Is Completed")
            if is_completed:
                ic_col0, ic_col1 = st.columns([0.2,1.8])
                with ic_col1:
                    st.date_input("Complitation Date")
            st.button("Save")
            st.markdown("---")
            st.button("Remove")

    def edit_epic(self, selected_epic):       

        
        new_epic_name = st.text_input("Name",value=selected_epic)
        if st.button("Save Epic"):

            if selected_epic!=new_epic_name:

                for ep in self.tasktm.epics:
                    if ep.name == selected_epic:

                        ep.name = new_epic_name
                        self.tasktm.save()

start = Edit(tasktm)