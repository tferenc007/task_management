
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
        with epic_col[1].expander("Add/Edit New Story"):
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
        ep = tasktm.epic_by_name(selected_epic)
        ep_id = ep.id
        story_list = tasktm.stories_to_list('name',ep_id)
        story_list.insert(0,'Add new story')
        picked_story = st.selectbox("Pick the story",story_list) 
        if picked_story=='Add new story':
            story_name = st.text_input("Name")
            story_description = st.text_input("Description")
            sprint_id = st.selectbox("Sprint", tasktm.dic_sprint.keys() )
            sprint_start_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_start_date'], "%Y-%m-%d")
            sprint_end_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_end_date'], "%Y-%m-%d")
            story_est_start_date = st.date_input("Est Start Date",value=sprint_start_date, disabled=True)
            story_est_end_date = st.date_input("Est End Date", value=sprint_end_date, disabled=True)
        else:
            picked_story_obj =   [story for story in ep.stories if story.name == picked_story][0]
            st_id = picked_story_obj.id

            
            story_name = st.text_input("Name",value=picked_story_obj.name)
            story_description = st.text_input("Description",value=picked_story_obj.description)
            sprint_id = st.selectbox("Sprint", tasktm.dic_sprint.keys(), index=picked_story_obj.story_index)
            sprint_start_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_start_date'], "%Y-%m-%d")
            sprint_end_date = datetime.strptime(tasktm.dic_sprint[sprint_id]['sprint_end_date'], "%Y-%m-%d")
            
            story_est_start_date = st.date_input("Est Start Date",value=sprint_start_date, disabled=True)
            story_est_end_date = st.date_input("Est End Date", value=sprint_end_date, disabled=True)
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
                    for ep in tasktm.epics:
                         if ep.id == ep_id:
                            new_story = tm.Story(df=tasktm.df_stories)
                            new_story.name = story_name
                            new_story.epic_id = ep_id
                            new_story.description = story_description
                            new_story.est_start_date = str(story_est_start_date)
                            new_story.est_end_date = str(story_est_end_date)
                            new_story.sprint_id = str(sprint_id)
                            ep.stories.append(new_story)
                            tasktm.save()
                            break

                else:
                     for ep in tasktm.epics:
                         if ep.id == ep_id:
                             for sto in ep.stories:
                                 if sto.id== st_id:
                                    sto.name = story_name
                                    sto.est_start_date = picked_story_obj.est_start_date
                                    sto.est_end_date = picked_story_obj.est_end_date
                                    sto.description = story_description
                                    sto.sprint_id = str(sprint_id)
                                    tasktm.save()
                                    break

                st.success("Story was added")
                time.sleep(2)
                st.rerun()
            else:
                
                st.error(f"Adding new story has been failed - {validation_text}")

    def story_validation(self, story_name, story_est_start_date, story_est_end_date):
        return 'Success'
    

    def add_edit_task(self, selected_epic): 
        ep = tasktm.epic_by_name(selected_epic)
        ep_id = ep.id
        story_list = tasktm.stories_to_list('name',ep_id) 
        selected_story = st.selectbox("Pick the story", story_list)
        st_ = tasktm.story_by_name(selected_story,selected_epic) 
        st_id = st_.id
        task_list = tasktm.tasks_to_list('name',st_id)
        task_list.insert(0,'Add new task')
        picked_task = st.selectbox('Pick the task',task_list) 


        if picked_task=='Add new task':
            task_name = st.text_input("Task Name")
            task_description  = st.text_input("Desclription ")
            task_is_completed = st.checkbox("Is completed", value=False)
            if task_is_completed:
                task_complitation_date = st.date_input("Complitation date")
            task_is_cancelled= st.checkbox("Is cancelled", value=False)

        else:
            picked_task_obj =   [task for task in st_.tasks if task.name == picked_task][0]
            task_name = st.text_input("Task Name", value=picked_task_obj.name)
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
                         if ep.id == ep_id:
                            for sto in ep.stories:
                                if sto.id==st_id:
                                    new_task = tm.Task(df=tasktm.df_tasks)

                                    new_task.name = task_name
                                    new_task.story_id = str(st_id)
                                    new_task.description = task_description
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
                         if ep.id == ep_id:
                             for sto in ep.stories:
                                 if sto.id==st_id:
                                    for tas in sto.tasks:
                                        if tas.id==picked_task_obj.id:

                                            tas.name = task_name
                                            tas.story_id = str(st_id)
                                            tas.description = task_description
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