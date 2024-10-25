import streamlit as st # type: ignore
import datetime
import taskmanagement as tm

taskm = tm.TaskManagement()



current_sprint_start= datetime.date(2024, 10, 21)
start_date = current_sprint_start
current_sprint_end= datetime.date(2024, 11, 3)
end_date = current_sprint_end

st.markdown("<h1 style='text-align: center;'>View</h1>", unsafe_allow_html=True)
st.selectbox("Select View",("Current"))
with st.sidebar:
    with st.container(border=True):
        start_date = st.date_input("Start Date", current_sprint_start)
        end_date = st.date_input("End Date", current_sprint_end)

last_activity = taskm.last_activity(start_date, end_date)
with st.container(border=True):
    con_col1, con_col2 = st.columns(2)
    con_col1.write("Last Activity")
    
    if datetime.date.today() == last_activity:
        con_col2.markdown(f'**:green[{last_activity}]** ')
    else:
        con_col2.markdown(f'**:red[{last_activity}]** ')
with st.container(border=True):
    st.markdown(f"<h5 style='text-align: center;'>Current Sprint: from {start_date} to {end_date}</h5>", unsafe_allow_html=True)    
    con_col1, con_col2 = st.columns(2)
    con_col1.write("Stories")
    con_col1.text("1/3")
    con_col2.write("Tasks")    
    con_col2.text("4/12")   
with st.container(border=True):
    st.markdown(f"<h5 style='text-align: center;'>Current Sprint: from {start_date} to {end_date}</h5>", unsafe_allow_html=True)       
    con_col1, con_col2 = st.columns(2,)
    con_col1.text("Story 1")
    con_col2.text("1/4")    
    con_col1.text("Story 2")
    con_col2.text("4/12")
    con_col1.text("Story 3")
    con_col2.text("0/3")      
    