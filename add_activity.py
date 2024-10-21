
import streamlit as st
# Function to create collapsible forms
def create_form(form_name):
    with st.expander(form_name, expanded=True):
        st.write("stories description")
        s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
        with s_col1:
            st.button("Task 1",use_container_width=False,key="task_button_id")
            st.button("Task 3")

        with s_col2:
            st.button("Task 2",use_container_width=False)
            st.button("Task 4")
            
def create_form2(form_name):
    with st.expander(form_name, expanded=True):
        s_col1,empty_col, s_col2 = st.columns([1.5, 0.5, 1.5],)
        with s_col1:
            st.button("Task 9",use_container_width=False)
            st.button("Task 99")

        with s_col2:
            st.button("Task 45",use_container_width=False)
            st.button("Task 65")

# Create 5 buttons and corresponding forms

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>Add Activity</h1>", unsafe_allow_html=True)
# Filters section
e_col_1, e_col_2, e_col_3 = st.columns(3)
e_col_1.button("Epic 1",use_container_width=True)
e_col_2.button("Epic 2",use_container_width=True)
e_col_3.button("Epic 3",use_container_width=True)
# Create 3 columns



with st.sidebar:
    with st.container(border=True):
        st.text("Story 1 > Task 1")
        st.date_input("date")
        st.button("Complete Task")

# Display the input text when the submit button is clicked
# if submit_button:
#     st.write("You entered:", user_input)

create_form("Story 1")
create_form2("Story 2")


# create_form("Story 2")


# col1, col2, col3 = st.columns(3)
# with col1:

#     if st.button("Task 1"):
#         create_form("Form 1")

#     if st.button("Task 2"):
#         create_form("Form 2")

# with col2:
#     if st.button("Task 3"):
#         create_form("Form 3")

#     if st.button("Task 4"):
#         create_form("Form 4")
# with col3:
#     if st.button("Task 5"):
#         create_form("Form 5")



# for i in range(1, 6):
#     create_form(f"Form {i}")



# col1, col2 = st.columns(2)

# with col1:
#     st.title("Place holder")

# with col2:
#     st.title("Tomasz Ferenc")
#     content = """
#     Hi, I am Tomek! A highly skilled professional with a background in Management and Production Engineering, specializing in Logistics.
#     Possesses extensive experience in business intelligence development, data analysis, and process improvement.
#     Currently expanding expertise by learning Python, alongside advanced SQL skills, data warehousing, and data engineering techniques.
#     Proficient in SQL (MS SQL Server, Snowflake) and DBT, with advanced proficiency in Git for version control. Additionally, holds advanced proficiency in Tableau (First level of certification) and Alteryx Designer (Core and Advanced Certification), enabling the creation of sophisticated analytical solutions. Adept at collaborating with stakeholders to gather requirements and deliver tailored solutions. Demonstrated ability to thrive in international environments and effectively address business challenges.
#     """
#     st.info(content)
# content2 = """
# Below you can find some of the apps I have built in Python. Feel free to contact me!
# """
# st.write(content2)

# col3, empty_col, col4 = st.columns([1.5, 0.5, 1.5])

