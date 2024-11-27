
import streamlit as st
import taskmanagement as tm
from datetime import datetime
import time

tasktm = tm.TaskManagement()


class AddActivity():
    def __init__(self, tasktm):
    # Create 5 buttons and corresponding forms
        self.tasktm = tasktm
        # self.is_button_clicked = False

        st.set_page_config(layout="wide")
        st.markdown("<h1 style='text-align: center;'>Add Activity</h1>", unsafe_allow_html=True)
        # Filters section

        if 'epic_list' not in st.session_state:
            # st.session_state.epic_list = []
            st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
        if 'button_clicked' not in st.session_state:
            # st.session_state.epic_list = []
           st.session_state.button_clicked  = ''

        if 'header_success' not in st.session_state:
            st.session_state.header_success = False

        if 'current_sprint_flag' not in st.session_state:
            st.session_state.current_sprint_flag = True

        if st.session_state.header_success:
            st.success("Task has been completed")
            st.session_state.header_success = False
        print(st.session_state.button_clicked)
        current_sprint_flag = st.checkbox("Current Sprint", value=st.session_state.current_sprint_flag)
        e_cols = st.columns(len(self.tasktm.epics))
        
        if st.button('All Filters',use_container_width=True, key='all filters'):
            st.session_state.epic_list = self.tasktm.epics_to_list('id')
            # self.is_button_clicked = True
        for i, epic in enumerate(self.tasktm.epics):
            if e_cols[i].button(epic.name,use_container_width=True, key=epic.id):
                st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
                st.session_state.epic_list = [e for e in st.session_state.epic_list if e == epic.id]
                # self.is_button_clicked = True
        
        if current_sprint_flag:
            cs = tasktm.get_current_sprint_id()
            stories = [story for story in self.tasktm.stories_squeeze(is_completed=False) if story.epic_id in st.session_state.epic_list and story.sprint_id==cs]
        else:
            stories = [story for story in self.tasktm.stories_squeeze(is_completed=False) if story.epic_id in st.session_state.epic_list]
        for story_frame in stories:
            with st.expander(story_frame.name, expanded=True):
                    st.write(story_frame.description)
                    s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
                    task_vertical = True
                    for task in story_frame.tasks:
                        if task.is_completed == 'true':
                            task_disabled = True
                        else:
                            task_disabled = False
                        if task_vertical:
                            with s_col1:
                                if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled):
                                    st.session_state.button_clicked = f'task_button{task.id}'
                                    st.rerun()
                                if  st.session_state.button_clicked==f'task_button{task.id}':
                                    st.session_state.task = task
                                    self.add_to_db({task.id})
                                    # self.is_button_clicked = True
                            task_vertical = False
                        else:
                            with s_col2:
                                if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled):
                                    st.session_state.button_clicked = f'task_button{task.id}'
                                    st.rerun()
                                if st.session_state.button_clicked==f'task_button{task.id}':
                                    st.session_state.task = task
                                    self.add_to_db({task.id})
                                   # self.is_button_clicked = True
                            task_vertical = True

        # if not self.is_button_clicked:
        #     print(" clicked")
        #     #self.add_to_db()
            


    def add_to_db(self, task_id):
        if 'task' in st.session_state:
            task = st.session_state.task
            with st.container(border=True):
                today = datetime.today().date()
                task_complete_date = st.date_input("date", key=f'task_date{task.id}', max_value=today)
                # print(f'task_date{task.id}')
                if st.button("Complete Task", key=f'task_complete_button{task.id}') and task_complete_date <= today:
                    self.tasktm.complete_task(task, task_complete_date)
                    st.session_state.header_success = True
                    st.session_state.button_clicked=''
                    del st.session_state.task
                    st.rerun()      


page_view = AddActivity(tasktm)
