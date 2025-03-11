
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time

tasktm = tm.TaskManagement()


class Objectives():
    def __init__(self):
        st.title("Add New Objective")
        life_goals = tasktm.objectives_to_list('name', is_life_goal='yes')

        sorted_unique_pi_ids = tasktm.sorted_unique_pi_ids()
        current_pi_index = sorted_unique_pi_ids.index(tasktm.get_current_sprint_pi_id(sprint_pi='pi'))

        with st.container(border=True):   
            objective_name = st.text_input("Objective Name")
            objective_description = st.text_area("Objective Description")
            
            if st.checkbox("Is this a life objective?", value=False):
                is_life_goal = True
                life_goal = None
                objective_due_date = None
            else:
                objective_due_date = st.selectbox("Select PI", sorted_unique_pi_ids, index=current_pi_index)
                life_goal = st.selectbox("Select Life Objective Category", life_goals)
                is_life_goal = False
            submit_button = st.button(label='Add Objective')

            if submit_button:
                tasktm.add_objective(objective_name, objective_description, objective_due_date, is_life_goal, life_goal)
                st.success("Objective added successfully!")



page_view = Objectives()
