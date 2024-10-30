import streamlit as st # type: ignore
import datetime
import taskmanagement as tm



class View():
    def __init__(self):

        st.set_page_config(page_title="View")
        current_sprint_start= datetime.date(2024, 10, 21)
        start_date = current_sprint_start
        current_sprint_end= datetime.date(2024, 11, 3)
        end_date = current_sprint_end

        st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
        st.selectbox("Select View",["Current"])
        with st.sidebar:
            with st.container(border=True):
                start_date = st.date_input("Start Date", current_sprint_start)
                end_date = st.date_input("End Date", current_sprint_end)

        last_activity = taskm.last_activity(start_date, end_date)
        with st.container(border=True):          
            if datetime.date.today() == last_activity:
                st.markdown(f'Last Activity &emsp;&emsp; **:green[{last_activity}]** ')
            else:
                st.markdown(f'Last Activity &emsp;&emsp; **:red[{last_activity}]** ')
        with st.container(border=True):
            st.markdown(f"<h5 style='text-align: center;'>Current Sprint: from {start_date} to {end_date}</h5>", unsafe_allow_html=True)    

            story_all = taskm.story_count(start_date, end_date)
            story_completed = taskm.story_count(start_date, end_date,is_completed=True)
            task_all = taskm.task_count(start_date, end_date,is_completed=False)
            task_completed = taskm.task_count(start_date, end_date,is_completed=True)
            coll_1 = st.columns(2)
            coll_2 = st.columns(2)
            coll_1[0].markdown(f"Stories:")
            coll_1[1].markdown(f"{task_completed}/{task_all}")    
            coll_2[0].markdown(f"Tasks")    
            coll_2[1].markdown(f"{story_completed}/{story_all}")

        with st.container(border=True):
            st.markdown(f"<h5 style='text-align: center;'>Current Sprint: from {start_date} to {end_date}</h5>", unsafe_allow_html=True)       
  

            story_list = taskm.stories_squeeze(start_date, end_date)
            for story_name in story_list:
                col = st.columns(2)
                col[0].markdown(f'{story_name.name}')
                col[1].markdown(f'{story_name.task_count(True)}/{story_name.task_count()}')
                
  
    
taskm = tm.TaskManagement()
page_veiw = View()