
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time

tasktm = tm.TaskManagement()


class AddActivity():
    def __init__(self, tasktm):
    # Create 5 buttons and corresponding forms
        self.tasktm = tasktm
        self.is_button_clicked = False

        st.set_page_config(layout="wide")
        st.markdown("<h1 style='text-align: center;'>Add Activity</h1>", unsafe_allow_html=True)
        # Filters section

        if 'epic_list' not in st.session_state:
            # st.session_state.epic_list = []
            st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
        if 'header_success' not in st.session_state:
            st.session_state.header_success = False

        if st.session_state.header_success:
            st.success("Task has been completed")
            time.sleep(2)
            st.session_state.header_success = False
            st.rerun()

        e_cols = st.columns(len(self.tasktm.epics))
        

        if st.button('All Filters',use_container_width=True, key='all filters'):
            st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
            self.is_button_clicked = True
        for i, epic in enumerate(self.tasktm.epics):
            if e_cols[i].button(epic.name,use_container_width=True, key=epic.id):
                st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
                st.session_state.epic_list = [e for e in st.session_state.epic_list if e == epic.id]
                self.is_button_clicked = True
        
        stories = [story for story in self.tasktm.stories_squeeze(is_completed=False) if story.epic_id in st.session_state.epic_list]
        
        for story_frame in stories:
            with st.expander(story_frame.name, expanded=True):
                    st.write(story_frame.description)
                    s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
                    task_vertical = True
                    for task in story_frame.tasks:
                        # print (f'{task.name} - {task.is_completed}')
                        if task.is_completed == 'true':
                            task_disabled = True
                        else:
                            task_disabled = False
                        if task_vertical:
                            with s_col1:
                                if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled):
                                    st.session_state.task = task
                                    self.add_to_db()
                                    self.is_button_clicked = True
                            task_vertical = False
                        else:
                            with s_col2:
                                if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled):
                                    st.session_state.task = task
                                    self.add_to_db()
                                    self.is_button_clicked = True
                            task_vertical = True

        if not self.is_button_clicked:
            self.add_to_db()
            


    def add_to_db(self):
        if 'task' in st.session_state:
            task = st.session_state.task
            story_name =  [story.name for story in self.tasktm.stories_squeeze() if story.id==task.story_id ]
            # with st.sidebar:
            with st.container(border=True):
                # st.text(f'Story Name: {story_name[0]}')
                # st.text(f'Task Name: {task.name}')
                today = datetime.today().date()
                task_complete_date = st.date_input("date", max_value=today)
                if st.button("Complete Task") and task_complete_date <= today:
                    self.tasktm.complete_task(task, task_complete_date)
                    st.session_state.header_success = True

                    del st.session_state.task
                    self.is_button_clicked = True
                    st.rerun()      


page_view = AddActivity(tasktm)
