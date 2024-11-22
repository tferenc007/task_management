
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
            self.add_new_story(selected_epic)

        story_col = st.columns([0.02, 0.98]) 

        with story_col[1].expander("Add/Edit Task"):
            self.add_edit_task(selected_epic)
            

       

    def edit_epic(self, selected_epic):       
        new_epic_name = st.text_input("Name",value=selected_epic)
        if st.button("Save Epic"):

            if selected_epic!=new_epic_name:

                for ep in self.tasktm.epics:
                    if ep.name == selected_epic:

                        ep.name = new_epic_name
                        self.tasktm.save()
                        st.rerun()


    def add_new_story(self, selected_epic):
        st.selectbox("Pick the story",['Add new story','Story 1', 'Story 2', 'Story 3'])       
        story_name = st.text_input("Name",)
        story_description = st.text_input("Description", )
        story_est_start_date = st.date_input("Est Start Date")
        story_est_end_date = st.date_input("Est End Date")
        if st.button("Add New Story"):
            validation_text = self.story_validation(story_name, story_est_start_date, story_est_end_date)
            if validation_text=='Success':
                st.success("Story was added")
                time.sleep(3)
                st.rerun()
            else:
                
                st.error(f"Adding new story has been failed - {validation_text}")

    def story_validation(self, story_name, story_est_start_date, story_est_end_date):
        return 'Success'
    

    def add_edit_task(self, selected_epic):       
        st.selectbox("Pick the story", ['Story 1', 'Story 2', 'Story 3'])
        st.selectbox('Pick the task',['Add new task', 'task 2', 'task 3',]) 
        task_name = st.text_input("Task Name")
        task_description  = st.text_input("Desclription ")
        task_is_completed = st.checkbox("Is completed")
        task_complitation_date = st.date_input("Complitation date")
        task_is_cancelled= st.checkbox("Is cancelled")
        task_validation = self.task_validation()
        if st.button("Save / Add"):
            if task_validation=='Success':
                st.success("Story was added")
            else:
                st.error(f"Adding new story has been failed - {task_validation}")


    def task_validation(self):
        return 'Success'
start = Edit(tasktm)