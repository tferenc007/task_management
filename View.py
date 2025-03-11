import streamlit as st # type: ignore
import datetime
import taskmanagement as tm
import os
import backup_email as be


class View():
    def __init__(self):
        if 'sidebar_visible' not in st.session_state:
            st.session_state.sidebar_visible = True

            st.session_state.sidebar_visible = False

            st.set_page_config(page_title="View")
            if os.path.isfile('local.txt')==False:
                if taskm.check_db()==False:
                    be.find_latest_email_and_save_attachment()
                    st.rerun()

        st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
        st.selectbox("Select View",["Current"])
        with st.sidebar:
            self.export_db()
        if st.checkbox("PI View",value=False):
            sorted_unique_pi_ids = taskm.sorted_unique_pi_ids()
            current_pi_index = sorted_unique_pi_ids.index(taskm.get_current_sprint_pi_id(sprint_pi='pi'))
            sprint_id = st.selectbox('Select PI', sorted_unique_pi_ids, index=current_pi_index)
            current_sprint_start = taskm.get_pi_start_date(sprint_id)
            current_sprint_start= datetime.datetime.strptime(current_sprint_start, "%Y-%m-%d")
            current_sprint_end = taskm.get_pi_end_date(sprint_id)
            current_sprint_end= datetime.datetime.strptime(current_sprint_end, "%Y-%m-%d")

        else:
            sprint_id_list = list(taskm.dic_sprint.keys())
            current_sprint_index = sprint_id_list.index(taskm.get_current_sprint_pi_id())
            sprint_id = st.selectbox('Select Sprint', sprint_id_list,index=current_sprint_index)
            current_sprint_start = taskm.dic_sprint[sprint_id]["sprint_start_date"]
            current_sprint_start= datetime.datetime.strptime(current_sprint_start, "%Y-%m-%d")
            current_sprint_end = taskm.dic_sprint[sprint_id]["sprint_end_date"]
            current_sprint_end= datetime.datetime.strptime(current_sprint_end, "%Y-%m-%d")

        start_date = current_sprint_start.date()
        end_date = current_sprint_end.date()
        last_activity = taskm.last_activity(start_date, end_date)
        with st.container(border=True):          
            if datetime.date.today() == last_activity:
                st.markdown(f'Last Activity &emsp;&emsp; **:green[{last_activity}]** ')
            else:
                st.markdown(f'Last Activity &emsp;&emsp; **:red[{last_activity}]** ')
        with st.container(border=True):
            st.markdown(f"<h5 style='text-align: center;'>From {start_date} To {end_date}</h5>", unsafe_allow_html=True)    
            story_all = taskm.story_count(start_date, end_date)
            story_all_sp = taskm.story_count(start_date, end_date, story_point=True)
            story_completed = taskm.story_count(start_date, end_date, is_completed=True)
            story_completed_sp = taskm.story_count(start_date, end_date, is_completed=True, story_point=True)
            task_all = taskm.task_count(start_date, end_date)
            task_completed = taskm.task_count(start_date, end_date,is_completed=True)
            coll_1 = st.columns(2)
            coll_2 = st.columns(2)
            coll_1[0].markdown(f"Stories:")
            coll_1[1].markdown(f"{story_completed}/{story_all} ({story_completed_sp}/{story_all_sp}  SP)")
            coll_2[0].markdown(f"Tasks")    
            coll_2[1].markdown(f"{task_completed}/{task_all}")    

        with st.container(border=True):
            st.markdown(f"<h5 style='text-align: center;'>From {start_date} To {end_date}</h5>", unsafe_allow_html=True)       
            story_list = taskm.stories_squeeze(start_date, end_date)
            for story_name in story_list:
                col = st.columns(2)

                tasks_names = [ task.name for task in story_name.tasks ]
                tooltip = ", ".join(tasks_names)   

                col[0].markdown(f'({story_name.story_point}){story_name.name}',help=tooltip)
                col[1].markdown(f'{story_name.task_count(True)}/{story_name.task_count()}')
    def export_db(self):
        if st.button("Synch database"):
            be.find_latest_email_and_save_attachment()
            if os.path.isfile('local.txt'):
                taskm.make_db_dev()
 
    
taskm = tm.TaskManagement()
page_veiw = View()