
import streamlit as st
import taskmanagement as tm

tasktm = tm.TaskManagement()






class AddActivity():
    def __init__(self, tasktm):
    # Create 5 buttons and corresponding forms
        self.tasktm = tasktm

        st.set_page_config(layout="wide")
        st.markdown("<h1 style='text-align: center;'>Add Activity</h1>", unsafe_allow_html=True)
        # Filters section
        if 'first_run' not in st.session_state:
            st.session_state.first_run = False

        
        e_cols = st.columns(len(self.tasktm.epics))
        for i, epic in enumerate(self.tasktm.epics):
            e_cols[i].button(epic.name,use_container_width=True, key=epic.id)
        

        for story_frame in self.tasktm.stories_squeeze():
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
                            task_vertical = False
                        else:
                            with s_col2:
                                if st.button(task.name,use_container_width=False,key=f'task_button{task.id}', disabled=task_disabled):
                                    st.session_state.task = task
                            task_vertical = True
        self.SideProperty()
    def SideProperty(self):
        if 'task' in st.session_state:
            task = st.session_state.task
            story_name =  [story.name for story in self.tasktm.stories_squeeze() if story.id==task.story_id ]
            with st.sidebar:
                with st.container(border=True):
                    st.text(f"{story_name[0]} > {task.name}")
                    task_complete_date = st.date_input("date")
                    if st.button("Complete Task"):
                        st.text("Task has beend added")
                        self.tasktm.complete_task(task, task_complete_date)
                        del st.session_state.task
                        st.rerun()

                   

page_view = AddActivity(tasktm)
