
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time

tasktm = tm.TaskManagement()


class Objectives():
    def __init__(self):

        st.title("Add New Objective")

        sorted_unique_pi_ids = tasktm.sorted_unique_pi_ids()
        current_pi_index = sorted_unique_pi_ids.index(tasktm.get_current_sprint_pi_id(sprint_pi='pi'))
        objective_due_date = st.selectbox("Select PI", sorted_unique_pi_ids, index=current_pi_index)

        objectives_list = tasktm.objectives_to_list('objective_name', filter_by=f'due_pi=="{objective_due_date}"')
        objectives_list.insert(0, 'New')
        picked_objective = st.selectbox("Select Objective",objectives_list)

        life_goals = tasktm.objectives_to_list('objective_name', filter_by='is_life_goal=="yes"')
        if picked_objective == 'New':
            def_objective_name = ''
            def_objective_description = ''
            def_life_goals_index = 0
            def_assigned_objectives = []
            def_label = 'Add Objective'
            def_ac_score=0
            def_ac_type='task'
        else:
            picked_objective_obj = tasktm.get_objective_by_name(picked_objective)
            parent_id = picked_objective_obj['parent_object'].tolist()[0]
            picked_objective_obj_parent = tasktm.objectives_to_list('objective_name', filter_by=f'objective_id=="{parent_id}"')[0]
            def_objective_name = picked_objective_obj['objective_name'].tolist()[0]
            def_objective_description = picked_objective_obj['objective_description'].tolist()[0]
            
            def_life_goals_index =  life_goals.index(picked_objective_obj_parent)
            def_assigned_objectives = tasktm.get_stories_assigned_to_obj(picked_objective)
            def_label = 'Edit Objective'
            def_ac_score=int(picked_objective_obj['acceptance_criteria_score'].tolist()[0])
            def_ac_type=picked_objective_obj['acceptance_criteria_type'].tolist()[0]



        with st.container(border=True):   
            objective_name = st.text_input("Objective Name", value=def_objective_name)
            objective_description = st.text_area("Objective Description" , value=def_objective_description)
            
            if st.checkbox("Is this a life objective?", value=False):
                is_life_goal = True
                life_goal = None
                objective_due_date = None
                selected_stories = None
            else:
                life_goal = st.selectbox("Select Life Objective Category", life_goals, index=def_life_goals_index)

                is_only_objective_non_assigned = st.checkbox("Show only stories not assigned to any objective", value=False)
                sprint_list = [item[0] for item in tasktm.sprint_dic.items() if item[1]["pi_id"] == objective_due_date]
                sprint_list_str = '", "'.join(sprint_list)
                filter_query = f'sprint_id in  ("{sprint_list_str}")'
                if is_only_objective_non_assigned:
                    if picked_objective == 'New':
                        filter_query += ' and objective_id == "0"'
                    else:
                        filter_query += ' and (objective_id == "0" or objective_id == "' + picked_objective_obj['objective_id'].tolist()[0] + '")'
                story_from_pi = tasktm.stories_to_list('both', filter_by=filter_query)

                selected_stories = st.multiselect('Assign story:', story_from_pi, default=def_assigned_objectives)
                selected_stories_id = [tasktm.get_story_id_by_name(story) for story in selected_stories]
                ac_score = str(st.number_input("Acceptance Criteria Score", value=def_ac_score))
                ac_type = st.selectbox("Acceptance Criteria Type", ['task', 'story'], index=1 if def_ac_type == 'story' else 0)
                is_life_goal = False
            submit_button = st.button(label=def_label)
            if picked_objective != 'New':
                delete_button = st.button(label='Delete Objective')
                if delete_button:
                    tasktm.delete_objective(picked_objective_obj['objective_id'].tolist()[0])
                    tasktm.send_backup_if_prod()
                    st.success("Objective deleted successfully!")
                    time.sleep(1)
                    st.rerun()

            if submit_button:
                if picked_objective == 'New':
                    tasktm.add_objective(objective_name=objective_name, objective_description=objective_description, objective_due_date=objective_due_date, 
                                         is_life_goal=is_life_goal, life_goal=life_goal, 
                                         selected_stories=selected_stories_id, ac_score=ac_score, ac_type=ac_type)
                    tasktm.send_backup_if_prod()
                    st.success("Objective added successfully!")
                else:
                    tasktm.edit_objective(picked_objective_obj['objective_id'].tolist()[0], objective_name, objective_description, objective_due_date, is_life_goal, 
                                          ac_score, ac_type, life_goal, selected_stories_id)
                    tasktm.send_backup_if_prod()
                    st.success("Objective updated successfully")
                time.sleep(1)
                st.rerun()



page_view = Objectives()

