import streamlit as st # type: ignore

st.markdown("<h1 style='text-align: center;'>Add/Edit</h1>", unsafe_allow_html=True)


st.selectbox("Select Epic",["Sport/Health","Personal Development","Entertaiment","Home"])
st.button("Edit Epic")
st.button("Add New Story")
with st.expander("Story 1"):
    st.button("Edit Story")
    st.button("Add New Task")
    st.markdown("---")
    st.button("Task 1 edit/remove")
    st.button("Task 2 edit/remove")
    st.button("Task 3 edit/remove")
    

with st.sidebar:
    st.write("Edit Epic")
    st.text_input("Name",key="epic_text_input")
    st.text_input("Description", key="epic_description")
    st.markdown("---")
    st.write("Edit Story")
    st.text_input("Name", key="story_name")
    st.text_input("Description", key="story_description")
    st.date_input("Est Start Date")
    st.date_input("Est End Date")

    st.markdown("---")
    st.write("Task 1 Edit")
    st.text_input("Task Name",disabled=True, value="Task 1")
    st.text_input("Description")
    is_completed = st.checkbox("Is Completed")
    if is_completed:
        ic_col0, ic_col1 = st.columns([0.2,1.8])
        with ic_col1:
            st.date_input("Complitation Date")
    st.button("Save")
    st.markdown("---")
    st.button("Remove")