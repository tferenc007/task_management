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

        st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
        st.selectbox("Select View",["Current"])
        with st.sidebar:
            self.export_db()
        sprint_id = st.selectbox('Select Sprint', taskm.dic_sprint.keys(),index=taskm.get_current_sprint_id('index'))
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
                # tooltip = "list of tasks"
                # col[0].markdown(f'<div title="{tooltip}">{story_name.name}</div>', unsafe_allow_html=True)

                col[0].markdown(f'({story_name.story_point}){story_name.name}',help=tooltip)
                col[1].markdown(f'{story_name.task_count(True)}/{story_name.task_count()}')
    def export_db(self):
        # with open('data/database.db', 'rb') as f:
        #     st.download_button(
        #         label="Download Database",
        #         data=f,
        #         file_name='database.db',
        #         mime='application/octet-stream'
        # )
        if st.button("Synch database"):
            be.find_latest_email_and_save_attachment()
  
    
taskm = tm.TaskManagement()
page_veiw = View()