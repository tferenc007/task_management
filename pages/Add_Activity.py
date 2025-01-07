
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

        if 'current_sprint_selected' not in st.session_state:
            st.session_state.current_sprint_selected = self.tasktm.get_current_sprint_id()

        if st.session_state.header_success:
            st.success("Task has been completed")
            st.session_state.header_success = False
        sprint_lists = self.tasktm.dic_sprint.keys()
        sprint_lists = list(sprint_lists)
        sprint_lists.insert(0, "All")
        st.session_state.current_sprint_selected = st.selectbox('Select Sprint', sprint_lists,index=self.tasktm.get_current_sprint_id('index')+1)

        e_cols = st.columns(len(self.tasktm.epics))
        
        if st.button('All Filters',use_container_width=True, key='all filters'):
            st.session_state.epic_list = self.tasktm.epics_to_list('id')
            # self.is_button_clicked = True
        for i, epic in enumerate(self.tasktm.epics):
            if e_cols[i].button(epic.name,use_container_width=True, key=epic.id):
                st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
                st.session_state.epic_list = [e for e in st.session_state.epic_list if e == epic.id]
                # self.is_button_clicked = True
        
        if st.button("(*)", key='add_story_button'):
            if st.session_state.button_clicked == 'Add new story':
                st.session_state.button_clicked = ''
            else:
                st.session_state.button_clicked = 'Add new story'

        if st.session_state.button_clicked == 'Add new story':
            st.write("Add new story")
            epic_selected = st.selectbox('Select Epic', [epic.name for epic in self.tasktm.epics])
            story_name = st.text_input("Story Name")
            story_description = st.text_area("Story Description")
            story_points = st.selectbox("Story Points", ["1",'3','5','8','13','21'])
            epic_id = self.tasktm.epic_by_name(epic_selected).id
            if st.button("Add Story"):
                self.tasktm.add_story(story_name=story_name, story_description=story_description, sprint_id=st.session_state.current_sprint_selected
                                        , epic_id=epic_id, story_point=story_points)
                st.session_state.button_clicked = ''
                st.rerun()

  

        if st.session_state.current_sprint_selected=='All':
            stories = [story for story in self.tasktm.stories_squeeze() if story.epic_id in st.session_state.epic_list]
        else:
            stories = [story for story in self.tasktm.stories_squeeze() if story.epic_id in st.session_state.epic_list
                       and story.sprint_id==st.session_state.current_sprint_selected]
        if 'story_frame_status' not in st.session_state:
            st.session_state.story_frame_status = {}
            for story in stories:
                st.session_state.story_frame_status[f"frame_key_{story.id}"] = False

        for story_frame in stories:
            frame_bool = st.session_state.story_frame_status[f"frame_key_{story_frame.id}"]
            with st.expander(story_frame.name, expanded=False):
                    st.write(story_frame.description)
                    s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
                    task_vertical = True
                    for task in story_frame.tasks:
                        if task.is_completed == 'true':
                            task_disabled = True
                            tick_mark = 'done'
                            tooltip = f"Complitation date: {task.complitation_date}"
                        elif task.is_cancelled=='true':
                            tick_mark = 'cancelled'
                            task_disabled = True
                            tooltip = f"Task was cancelled"
                        else:
                            tick_mark = 'none'
                            task_disabled = False
                            tooltip = ""
                        if task_vertical:
                            with s_col1:
                                c1,c2,c_emp = st.columns([1, 0.1, 1])
                                with c1:

                                    if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled, help=tooltip):
                                        if st.session_state.button_clicked == f'task_button{task.id}':
                                            st.session_state.button_clicked = ''
                                        else:
                                            st.session_state.button_clicked = f'task_button{task.id}'
                                        st.rerun()
                                if  st.session_state.button_clicked==f'task_button{task.id}':
                                    st.session_state.task = task
                                    self.add_to_db({task.id})
                                    # self.is_button_clicked = True
                                with c2:
                                    if tick_mark=='done':
                                        st.write("✅")
                                    if tick_mark=='cancelled':
                                        st.write("❌")
                                task_vertical = False
                        else:
                            with s_col2:
                                c3,c4,c2_emp = st.columns([1, 0.1, 1])
                                with c3:
                                
                                    if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled, help=tooltip):
                                        if st.session_state.button_clicked == f'task_button{task.id}':
                                            st.session_state.button_clicked = ''
                                        else:
                                            st.session_state.button_clicked = f'task_button{task.id}'
                                        st.rerun()
                                if st.session_state.button_clicked==f'task_button{task.id}':
                                    st.session_state.task = task
                                    self.add_to_db({task.id})
                                    # self.is_button_clicked = True
                                with c4:
                                    if tick_mark=='done':
                                        st.write("✅")
                                    if tick_mark=='cancelled':
                                        st.write("❌")
                            task_vertical = True
                    if st.button("(+)", key=f'add_task_button{story_frame.id}'):
                        if st.session_state.button_clicked ==  f'add_task_button{story_frame.id}':
                            st.session_state.button_clicked = ''
                        else:
                            st.session_state.button_clicked =  f'add_task_button{story_frame.id}'

                    if st.session_state.button_clicked == f'add_task_button{story_frame.id}':
                        task_name = st.text_input("Task Name", key=f'task_name{story_frame.id}')
                        task_est = st.date_input("Estimate Date", key=f'task_estimate{story_frame.id}', value=None)
                        if st.button("Add Task", key=f'add_task_button_to_story{story_frame.id}'):
                            self.tasktm.add_task(task_name, story_frame.id, task_est)
                            st.session_state.button_clicked = ''
                            st.rerun()
                          

        # if not self.is_button_clicked:
        #     print(" clicked")
        #     #self.add_to_db()
            


    def add_to_db(self, task_id):
        if 'task' in st.session_state:
            task = st.session_state.task
            with st.container(border=True):
                today = datetime.today().date()
                # print(task.estimate_date)
                est_date =str(task.estimate_date)
                st.text(f"Estimate Date: {est_date}")
                task_complete_date = st.date_input("Date", key=f'task_date{task.id}', max_value=today)
                # print(f'task_date{task.id}')
                if st.button("Complete Task", key=f'task_complete_button{task.id}') and task_complete_date <= today:
                    self.tasktm.complete_task(task, task_complete_date)
                    st.session_state.header_success = True
                    st.session_state.button_clicked=''
                    del st.session_state.task
                    st.rerun()      
                if st.button("Cancel Task", key=f'task_cancel_button{task.id}') and task_complete_date <= today:
                    self.tasktm.complete_task(task, task_complete_date)
                    st.session_state.header_success = True
                    st.session_state.button_clicked=''
                    del st.session_state.task
                    st.rerun()      
                    


page_view = AddActivity(tasktm)
