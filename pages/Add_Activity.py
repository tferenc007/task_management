
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
            st.session_state.current_sprint_selected = self.tasktm.get_current_sprint_pi_id()

        if st.session_state.header_success:
            st.success("Task has been completed")
            st.session_state.header_success = False
        sprint_lists = self.tasktm.dic_sprint.keys()
        sprint_lists = list(sprint_lists)
        sprint_lists.insert(0, "All")
        check_if_sprint_changed = st.session_state.current_sprint_selected
        current_sprint_index = sprint_lists.index(self.tasktm.get_current_sprint_pi_id())
        st.session_state.current_sprint_selected = st.selectbox('Select Sprint', sprint_lists,index=current_sprint_index)

        if st.session_state.current_sprint_selected != check_if_sprint_changed:
            sprint_is_changed = True
        else:
            sprint_is_changed = False
            # self.is_button_clicked =

        with st.expander("Filters", expanded=False):
            e_cols = st.columns(len(self.tasktm.epics))
            for i, epic in enumerate(self.tasktm.epics):
                if e_cols[i].button(epic.name,use_container_width=True, key=epic.id):
                    st.session_state.epic_list = [epic.id for epic in self.tasktm.epics]
                    st.session_state.epic_list = [e for e in st.session_state.epic_list if e == epic.id]
            if st.button('All Filters',use_container_width=True, key='all filters'):
                st.session_state.epic_list = self.tasktm.epics_to_list('id')
        
        if st.button("(+)", key='add_story_button'):
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
            #  filter_by=f'objective_id!="{exception}"'
            current_pi_id = self.tasktm.get_current_sprint_pi_id('pi')
            filter_by=f'due_pi=="{current_pi_id}"'
            objective_list = tasktm.objectives_to_list('objective_name', filter_by=filter_by)
            objective_list.insert(0, 'No objective')
            objective_id = st.selectbox("Objective", objective_list)
            if st.button("Add Story"):
                self.tasktm.add_story(story_name=story_name, story_description=story_description, sprint_id=st.session_state.current_sprint_selected
                                        , epic_id=epic_id, story_point=story_points, objective_id=tasktm.objective_id_by_name(objective_id))
                st.session_state.button_clicked = ''
                self.__reasign_story__(st.session_state.current_sprint_selected)
                self.__story_frame_to_false__()

                st.rerun()

  
        self.__reasign_story__(st.session_state.current_sprint_selected)
            
        if 'story_frame_status' not in st.session_state or sprint_is_changed:
            st.session_state.story_frame_status = {}
            for story in st.session_state.stories:
                st.session_state.story_frame_status[f"frame_key_{story.id}"] = False

        for story_frame in  st.session_state.stories:          
            frame_bool = st.session_state.story_frame_status[f"frame_key_{story_frame.id}"]
            if story_frame.is_completed:
                formated_story_frame_name = rf"✅ :green[{story_frame.name}]"
            else :
                formated_story_frame_name = story_frame.name

            with st.expander(formated_story_frame_name, expanded=frame_bool):
                    st.write(f'Desc:{story_frame.description}')
                    objective_name = tasktm.df_objectives[tasktm.df_objectives['objective_id']==story_frame.objective_id]
                    if not objective_name.empty:
                        st.write(f'Obj: {objective_name['objective_name'].values[0]}')

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
                                            self.story_frame_status(st.session_state.stories, story_frame.id)
                                        else:
                                            st.session_state.button_clicked = f'task_button{task.id}'
                                            self.story_frame_status(st.session_state.stories, story_frame.id)
                                        st.rerun()
                                if  st.session_state.button_clicked==f'task_button{task.id}':
                                    st.session_state.task = task
                                    self.add_to_db(story_frame)
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
                                            self.story_frame_status(st.session_state.stories, story_frame.id)
                                        else:
                                            st.session_state.button_clicked = f'task_button{task.id}'
                                            self.story_frame_status(st.session_state.stories, story_frame.id)
                                        st.rerun()
                                if st.session_state.button_clicked==f'task_button{task.id}':
                                    st.session_state.task = task
                                    self.add_to_db(story_frame)
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
                            self.story_frame_status(st.session_state.stories, story_frame.id)
                        else:
                            st.session_state.button_clicked =  f'add_task_button{story_frame.id}'
                            self.story_frame_status(st.session_state.stories, story_frame.id)

                    if st.button("Change Sprint", key=f'assign_sprint_button{story_frame.id}'):
                        if st.session_state.button_clicked ==  f'assign_sprint_button{story_frame.id}':
                            st.session_state.button_clicked = ''
                            self.story_frame_status(st.session_state.stories, story_frame.id)
                        else:
                            st.session_state.button_clicked =  f'assign_sprint_button{story_frame.id}'
                            self.story_frame_status(st.session_state.stories, story_frame.id)

                    if st.session_state.button_clicked ==  f'assign_sprint_button{story_frame.id}':
                        sprint_lists = self.tasktm.dic_sprint.keys()
                        sprint_lists = list(sprint_lists)
                        sprint_index = sprint_lists.index(story_frame.sprint_id)
                        duplicate_sprint = st.checkbox("Duplicate the sprint", value=False)
                        if duplicate_sprint:
                            change_sprint_label = 'Duplicate Sprint to'
                            sprint_selected = st.multiselect('Assign story:', sprint_lists)
                        else:
                            change_sprint_label = 'Select Sprint'
                            sprint_selected = st.selectbox(change_sprint_label, sprint_lists, key="change_sprint_key", index=sprint_index)
                        
                        if sprint_selected != story_frame.sprint_id and duplicate_sprint==False:
                            self.tasktm.edit_story(story_id=story_frame.id, sprint_id=sprint_selected)
                                
                            st.session_state.button_clicked = ''
                            self.__reasign_story__(st.session_state.current_sprint_selected)
                            self.__story_frame_to_false__()
                            st.rerun()
                        elif sprint_selected != story_frame.sprint_id and duplicate_sprint==True  and st.button("Apply", key=f'apply_sprint_button{story_frame.id}'):
                            sth = self.tasktm.duplicate_story(source_story_id=story_frame.id, destination_sprint_id=sprint_selected)
                            st.session_state.button_clicked = ''
                            self.__reasign_story__(st.session_state.current_sprint_selected)
                            self.__story_frame_to_false__()
                            st.rerun()
                        pass
                    if st.session_state.button_clicked == f'add_task_button{story_frame.id}':
                        st.write("Add new task")
                        task_name = st.text_input("Task Name", key=f'task_name{story_frame.id}')
                        task_est = st.date_input("Estimate Date", key=f'task_estimate{story_frame.id}', value=None)
                        bulk_tasks = st.number_input("Number of taksks", step=1, min_value=1)
                        if st.button("Add Task", key=f'add_task_button_to_story{story_frame.id}'):
                            for i in range(1, bulk_tasks + 1):
                                print(i)
                                prefixed_task_name = f"{task_name} #{i}"
                                self.tasktm.add_task_df(prefixed_task_name, story_frame.id, task_est)
                            self.tasktm.save()
                                
                            st.session_state.button_clicked = ''
                            st.rerun()
                          

        # if not self.is_button_clicked:
        #     print(" clicked")
        #     #self.add_to_db()
    def __story_frame_to_false__(self):
        st.session_state.story_frame_status = {}
        for story in st.session_state.stories:
            st.session_state.story_frame_status[f"frame_key_{story.id}"] = False

    def __reasign_story__(self, filter):
        if filter=='All':
            st.session_state.stories = [story for story in self.tasktm.stories_squeeze() if story.epic_id in st.session_state.epic_list]
            st.session_state.stories = sorted (st.session_state.stories, key=lambda x: x.is_completed)
        else:
            st.session_state.stories = [story for story in self.tasktm.stories_squeeze() if story.epic_id in st.session_state.epic_list
            and story.sprint_id==st.session_state.current_sprint_selected]
            st.session_state.stories = sorted (st.session_state.stories, key=lambda x: x.is_completed)
    

    def story_frame_status(self, stories, story_id):
        for _st in stories:
            if _st.id == story_id:
                st.session_state.story_frame_status[f"frame_key_{_st.id}"] = True
            else:
                st.session_state.story_frame_status[f"frame_key_{_st.id}"] = False



    def add_to_db(self, story_frame):
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
                    self.tasktm.cancel_task(task)
                    st.session_state.header_success = True
                    st.session_state.button_clicked=''
                    del st.session_state.task
                    st.rerun()      
                    


page_view = AddActivity(tasktm)
