import streamlit as st # type: ignore
import datetime
import taskmanagement as tm
import os
import backup_email as be
import pandas as pd
import altair as alt



class View():
    def __init__(self,taskm):
        if 'sidebar_visible' not in st.session_state:
            st.session_state.sidebar_visible = True

            st.session_state.sidebar_visible = False

            st.set_page_config(page_title="View")

        st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
        view_options = st.selectbox("Select View",["Current", "Objectives View"])
        if view_options == "Objectives View":
            sorted_unique_pi_ids = taskm.sorted_unique_pi_ids()
            current_pi_index = sorted_unique_pi_ids.index(taskm.get_current_sprint_pi_id(sprint_pi='pi'))
            sprint_id = st.selectbox('Select PI', sorted_unique_pi_ids, index=current_pi_index)
            current_sprint_start = taskm.get_pi_start_date(sprint_id)
            current_sprint_start= datetime.datetime.strptime(current_sprint_start, "%Y-%m-%d")
            current_sprint_end = taskm.get_pi_end_date(sprint_id)
            current_sprint_end= datetime.datetime.strptime(current_sprint_end, "%Y-%m-%d")
            
            

        elif view_options == "Current":
            sprint_id_list = list(taskm.dic_sprint.keys())
            current_sprint_index = sprint_id_list.index(taskm.get_current_sprint_pi_id())
            sprint_id = st.selectbox('Select Sprint', sprint_id_list,index=current_sprint_index)
            current_sprint_start = taskm.dic_sprint[sprint_id]["sprint_start_date"]
            current_sprint_start= datetime.datetime.strptime(current_sprint_start, "%Y-%m-%d")
            current_sprint_end = taskm.dic_sprint[sprint_id]["sprint_end_date"]
            current_sprint_end= datetime.datetime.strptime(current_sprint_end, "%Y-%m-%d")


        start_date = current_sprint_start.date()
        if view_options == "Current":
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
                story_all_sp = taskm.story_count(start_date, end_date, options='all_sp')
                story_completed = taskm.story_count(start_date, end_date, options='all_completed_cnt')
                story_completed_sp = taskm.story_count(start_date, end_date, options='all_completed_sp')
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
        elif view_options == "Objectives View":
            # Group by 'story_id' and count completed and all tasks
            st.markdown(f'PI Dates: **:green[{current_sprint_start.date()} - {current_sprint_end.date()}]** ')
            task_summary = taskm.tasks_df.groupby('story_id').agg(
                all_task=('story_id', 'count'),
                completed_task=('is_completed', lambda x: (x == 'true').sum())
            ).reset_index()

            story_df = pd.merge(
                task_summary,
                taskm.stories_df[['id','objective_id','story_point']],
                left_on='story_id',
                right_on='id',
                how='left'
            )[['objective_id','story_id','story_point','all_task','completed_task']]
            story_df['completed_sp'] = story_df['story_point'].apply(pd.to_numeric) * (story_df['completed_task'].apply(pd.to_numeric)/ story_df['all_task'].apply(pd.to_numeric))
            story_df['story_point'] = story_df['story_point'].apply(pd.to_numeric)
            story_summary = story_df.groupby('objective_id').agg(
                all_task=('all_task', 'sum'),
                completed_task=('completed_task', 'sum'),
                all_sp=('story_point', 'sum'),
                completed_sp=('completed_sp', 'sum')
            ).reset_index()
            story_summary = story_summary.loc[story_summary['objective_id'] != '0']

           

            # Merge the task summary back with the objectives and stories data
            objective_summary = pd.merge(
                taskm.objectives_df,
                story_summary,
                on="objective_id",
                how="left"
            )
            objective_summary['goal'] = objective_summary.apply(
                lambda row: row['all_sp'] if row['acceptance_criteria_type'] == 'story' else row['all_task'], axis=1
            )
            objective_summary['completed'] = objective_summary.apply(
                lambda row: row['completed_sp'] if row['acceptance_criteria_type'] == 'story' else row['completed_task'], axis=1
            )
            objective_summary['remaining'] = objective_summary['goal'].apply(pd.to_numeric) - objective_summary['completed']
           

       


            objective_summary['pi_days'] = (current_sprint_end-current_sprint_start).days #need to get this from the sprint
            objective_summary['current_day_of_pi'] =  (datetime.date.today() - current_sprint_start.date() ).days
            objective_summary['remaining_days_in_pi'] = objective_summary['pi_days'].apply(pd.to_numeric) - objective_summary['current_day_of_pi'].apply(pd.to_numeric)
            objective_summary['p_completed'] = objective_summary['completed'].apply(pd.to_numeric) / objective_summary['goal'].apply(pd.to_numeric)
            objective_summary['p_remaining'] = 1 - objective_summary['p_completed']

            # objective_summary = objective_summary[['due_pi','objective_name', 'goal', 'value', 'pi_days', 'current_day_of_pi', 'remaining_days_in_pi', 'p_value_0', 'p_value', 'acceptance_criteria_type']]
            
            objective_completed = objective_summary.copy()

            objective_completed ['Type'] = 'Completed'
            objective_completed['p_value'] = objective_completed['p_completed']
            objective_completed['value'] = objective_completed['p_value'] * objective_completed['pi_days'].apply(pd.to_numeric)

            objective_remaining = objective_summary.copy()
            objective_remaining ['Type'] = 'Remaining'
            objective_remaining['p_value'] = objective_remaining['p_remaining']
            objective_remaining['value'] = objective_remaining['pi_days'].apply(pd.to_numeric) - objective_completed['value']
            
            
            objective_final = pd.concat([objective_completed, objective_remaining], ignore_index=True)
            objective_final = objective_final.loc[objective_final['due_pi'] == sprint_id]
          



            # Create the DataFrame
            source = objective_final

            # Define custom colors
            color_scale = alt.Scale(domain=["Completed", "Remaining"], range=["#77dd77", "#ff6961"])

            # Create the bar chart
            chart = alt.Chart(source).mark_bar().encode(
                x=alt.X('value', axis=alt.Axis(title=None, labels=False)),
                y=alt.Y('objective_name', axis=alt.Axis(title=None)),
                color=alt.Color('Type', scale=color_scale),
                tooltip=['objective_name', 
                         alt.Tooltip('pi_days', title='Days in PI'),
                         alt.Tooltip('remaining_days_in_pi', title='Remaining Days'),
                         alt.Tooltip('p_value', title='Complitation %', format='.0%'),
                        #  alt.Tooltip('value', title='Completed tasks/stories'),
                         alt.Tooltip('goal', title='Remaining tasks/stories'),
                         alt.Tooltip('acceptance_criteria_type', title='Criteria type')]
                         
                
            ).properties(
                width='container'

            )

            # Create a vertical rule (note: this is symbolic, as p_value is not a date)
            rule = alt.Chart(source).mark_rule(color='black',size=2).encode(
                x='current_day_of_pi:Q'
            )

            # Combine and configure
            final_chart = alt.layer(chart, rule).configure_axis(
                labelFont='sans-serif'
            ).configure_legend(
                disable=True
            )

            # Display the chart
            st.altair_chart(final_chart, use_container_width=True)

         
if 'tasktm' not in st.session_state:
         st.session_state.tasktm =  tm.TaskManagement()
page_veiw = View(st.session_state.tasktm)