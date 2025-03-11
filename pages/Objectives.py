
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
                selected_stories = None
            else:
                objective_due_date = st.selectbox("Select PI", sorted_unique_pi_ids, index=current_pi_index)
                life_goal = st.selectbox("Select Life Objective Category", life_goals)

                is_only_objective_non_assigned = st.checkbox("Show only stories not assigned to any objective", value=False)
                sprint_list = [item[0] for item in tasktm.sprint_dic.items() if item[1]["pi_id"] == objective_due_date]
                sprint_list_str = '", "'.join(sprint_list)
                filter_query = f'sprint_id in  ("{sprint_list_str}")'
                if is_only_objective_non_assigned:
                    filter_query += ' and objective_id == "0"'
                story_from_pi = tasktm.stories_to_list('name', filter_by=filter_query)
                selected_stories = st.multiselect('Assign story:', story_from_pi)
                is_life_goal = False
            submit_button = st.button(label='Add Objective')

            if submit_button:
                tasktm.add_objective(objective_name, objective_description, objective_due_date, is_life_goal, life_goal, selected_stories)
                tasktm.send_backup_if_prod()
                st.success("Objective added successfully!")
                time.sleep(1)
                st.rerun()



page_view = Objectives()
