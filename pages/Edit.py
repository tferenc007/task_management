
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time

tasktm = tm.TaskManagement()

class Edit():
    def __init__(self, tasktm):
        self.tasktm = tasktm
        st.markdown("<h1 style='text-align: center;'>Add/Edit</h1>", unsafe_allow_html=True)

        epic_col = st.columns([0.02, 0.98])

        with epic_col[1].expander("Edit Epic"):
            new_epic_name = self.edit_epic()
        with epic_col[1].expander("Add/Edit New Story"):
            self.add_new_story()

        story_col = st.columns([0.02, 0.98]) 

        with story_col[1].expander("Add/Edit Task"):
            self.add_edit_task()
            

       

    def edit_epic(self):
        selected_epic = st.selectbox("Select Epic",self.tasktm.epics_to_list('name'), key='edit_epic')       
        new_epic_name = st.text_input("Name",value=selected_epic)
        if st.button("Save Epic"):

            if selected_epic!=new_epic_name:

                for ep in self.tasktm.epics:
                    if ep.name == selected_epic:

                        ep.name = new_epic_name
                        self.tasktm.save()
                        st.rerun()


    def add_new_story(self):
        epic_list_origin = tasktm.epics_to_list('name')
        epic_list = epic_list_origin.copy()
        epic_list.insert(0,'All Epics')
        ep_id = None
        selected_epic = st.selectbox("Select Epic",epic_list, key='edit_story')
        if selected_epic!='All Epics':

            ep = tasktm.epic_by_name(selected_epic)
            ep_id = ep.id
            story_list = tasktm.stories_to_list('name',ep_id)
    
        else:
            story_list = tasktm.stories_to_list('name')       
        story_list.insert(0,'Add new story')
      
        picked_story = st.selectbox("Pick the story",story_list) 
        st.write('-------------------')
        if picked_story=='Add new story':
            epic_name = st.selectbox("Epic Name",epic_list_origin, key='edit_story_epic_name')
            story_name = st.text_input("Name")
            story_description = st.text_input("Description")
            sprint_id = st.selectbox("Sprint", tasktm.dic_sprint.keys() )
            sprint_start_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_start_date'], "%Y-%m-%d")
            story_points = st.selectbox("Story Points",["1",'3','5','8','13','21'])
            sprint_end_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_end_date'], "%Y-%m-%d")
            story_est_start_date = st.date_input("Est Start Date",value=sprint_start_date, disabled=True)
            story_est_end_date = st.date_input("Est End Date", value=sprint_end_date, disabled=True)
            objective_list = tasktm.objectives_to_list('objective_name', filter_by='is_life_goal=="no"')
            objective_list.insert(0, 'No objective')
            objective_id = st.selectbox("Objective", objective_list)
        else:
            picked_story_obj =  [story for story in tasktm.stories_squeeze() if story.name == picked_story][0]
            ep_id = picked_story_obj.epic_id
            epic = tasktm.epic_by_id(ep_id)
            st_id = picked_story_obj.id

            epic_name = st.selectbox("Epic Name",epic_list_origin, key='edit_story_epic_name', index=epic.epic_index)
            story_name = st.text_input("Name",value=picked_story_obj.name)
            story_description = st.text_input("Description",value=picked_story_obj.description)
            sprint_id = st.selectbox("Sprint", tasktm.dic_sprint.keys(), index=list(tasktm.dic_sprint.keys()).index(picked_story_obj.sprint_id))

   

            sprint_start_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_start_date'], "%Y-%m-%d")
            sprint_end_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_end_date'], "%Y-%m-%d")
            story_points = st.selectbox("Story Points", ["1",'3','5','8','13','21'], index=picked_story_obj.story_point_index)
            story_est_start_date = st.date_input("Est Start Date",value=sprint_start_date, disabled=True)
            story_est_end_date = st.date_input("Est End Date", value=sprint_end_date, disabled=True)
            objective_list = tasktm.objectives_to_list('objective_name', filter_by='is_life_goal=="no"')
            objective_list.insert(0, 'No objective')
            objective_id = st.selectbox("Objective", objective_list, index=int(picked_story_obj.objective_id))
            if objective_id=='No objective':
                objective_id = '0'
            else:
                 objective_id = tasktm.objective_id_by_name(objective_id)
            if st.button('Delete Story'):
                for ep in tasktm.epics:
                    ep.stories[:] = [sto for sto in ep.stories if sto.id != st_id]
                tasktm.save()
                st.success("Story was deleted")
                time.sleep(1)
                st.rerun()

        if st.button("Add / Edit Story"):
            validation_text = self.story_validation(story_name, story_est_start_date, story_est_end_date)

            if validation_text=='Success':
                if picked_story=='Add new story':
                    tasktm.add_story(story_name, story_description, str(sprint_id), tasktm.epic_by_name(epic_name).id,
                                      str(story_points), objective_id =objective_id)
                else:
                    if tasktm.edit_story(story_id=st_id, story_name=story_name, story_description=story_description,
                                       sprint_id=str(sprint_id), epic_id=tasktm.epic_by_name(epic_name).id, story_point=str(story_points),
                                         objective_id = objective_id):
                        tasktm.save()
                st.success("Story was added")
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"Adding new story has been failed - {validation_text}")

    def story_validation(self, story_name, story_est_start_date, story_est_end_date):
        return 'Success'
    

    def add_edit_task(self): 

        epic_list = tasktm.epics_to_list('name')
        epic_list.insert(0,'All Epics')
        selected_epic = st.selectbox("Select Epic",epic_list, key='edit_taskss')

        if selected_epic!='All Epics':

            ep = tasktm.epic_by_name(selected_epic)
            ep_id = ep.id
            story_list = tasktm.stories_to_list('name',ep_id)
    
        else:
            story_list = tasktm.stories_to_list('name')       
        story_list.insert(0,'All Stories')

        if len(story_list)>0:
            selected_story = st.selectbox("Pick the story", story_list, key='costum_key')
            if selected_epic=='All Epics':
                if selected_story=='All Stories':
                    st_ = tasktm.tasks_squeeze()
                    tasks = st_
                    task_list = [task.name for task in st_]
                else:
                    st_ = []
                    st_.append(tasktm.story_by_name(selected_story))
                    tasks = st_[0].tasks
                    task_list = [task.name for task in tasks]
            else:
                if selected_story=='All Stories':
                    st_ = tasktm.stories_squeeze()

                    story_filterd = [story for story in st_ if story.epic_id==ep_id]
                    tasks = []
                    for story in story_filterd:
                        for task in story.tasks:
                            tasks.append(task)

                    task_list = [task.name for task in tasks]
                else:
                    st_ = []
                    st_.append(tasktm.story_by_name(selected_story))
                    tasks = st_[0].tasks
                    task_list = [task.name for task in tasks]


            task_list.insert(0,'Add new task')
            picked_task = st.selectbox('Pick the task',task_list) 


            if picked_task=='Add new task':
                task_name = st.text_input("Task Name")
                task_estimation_date = st.date_input("Estimate Date", value=None)
                task_description  = st.text_input("Desclription ")
                task_is_completed = st.checkbox("Is completed", value=False)
                if task_is_completed:
                    task_complitation_date = st.date_input("Complitation date")
                task_is_cancelled= st.checkbox("Is cancelled", value=False)

            else:
                picked_task_obj = [task for task in tasks if task.name == picked_task][0]
                st_id = picked_task_obj.story_id
                task_name = st.text_input("Task Name", value=picked_task_obj.name)
                task_estimation_date = st.date_input("Estimate Date", value=picked_task_obj.estimate_date)
                task_description  = st.text_input("Desclription", value=picked_task_obj.description )
                if picked_task_obj.is_completed=='true':
                    complitation_date = datetime.strptime(picked_task_obj.complitation_date, "%Y-%m-%d")
                    task_is_completed = st.checkbox("Is completed", value=True)
                    task_complitation_date = st.date_input("Complitation date", value=complitation_date)
                else:
                    task_is_completed = st.checkbox("Is completed", value=False)
                    if task_is_completed:
                        task_complitation_date = st.date_input("Complitation date")

                if picked_task_obj.is_cancelled=='true':
                    task_is_cancelled= st.checkbox("Is cancelled", value=True)

                else:
                    task_is_cancelled= st.checkbox("Is cancelled", value=False)

            if st.button('Delete Task'):
                for ep in tasktm.epics:
                    for sto in ep.stories:
                        sto.tasks[:] = [task for task in sto.tasks if task.id != picked_task_obj.id]

                tasktm.save()
                st.success("Task was deleted")
                time.sleep(1)
                st.rerun()
            task_validation = self.task_validation()
            if st.button("Save / Add"):
                if task_validation=='Success':
                    if picked_task=='Add new task':
                        for ep in tasktm.epics:
                            for sto in ep.stories:
                                if sto.id==st_id:

                                    new_task = tm.Task(df=tasktm.df_tasks)

                                    new_task.name = task_name
                                    new_task.story_id = str(st_id)
                                    new_task.description = task_description
                                    new_task.estimate_date = str(task_estimation_date)
  
                                    if task_is_completed:
                                        new_task.complitation_date = str(task_complitation_date)
                                    else:
                                        new_task.complitation_date = None
                                    if task_is_cancelled:
                                        new_task.is_cancelled = 'true'
                                    else:
                                        new_task.is_cancelled = 'false'
                                    sto.tasks.append(new_task)
                                    tasktm.save()
                                    break

                    else:
                        for ep in tasktm.epics:
                            for sto in ep.stories:
                                if sto.id==st_id:
                                    for tas in sto.tasks:
                                        if tas.id==picked_task_obj.id:

                                            tas.name = task_name
                                            tas.story_id = str(st_id)
                                            tas.description = task_description
                                            tas.estimate_date = str(task_estimation_date)
                                            if task_is_completed:
                                                tas.complitation_date = str(task_complitation_date)
                                            else:
                                                tas.complitation_date = None
                                            if task_is_cancelled:
                                                tas.is_cancelled = 'true'
                                            else:
                                                tas.is_cancelled = 'false'
                                            tasktm.save()
                                            break

                    st.success("Story was added")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"Adding new story has been failed - {task_validation}")


    def task_validation(self):
        return 'Success'
start = Edit(tasktm)