import streamlit as st
from database import insert_data, fetch_data, update_data, delete_data, fetch_one
import datetime

def render_page():
    st.title("Manage Teachers")
    st.write("Add, edit, and remove teacher details.")

    with st.form("add_teacher_form", clear_on_submit = True):
        st.subheader("Add a Teacher")
        username = st.text_input("Username", key="add_teacher_username")
        password = st.text_input("Password", type="password", key="add_teacher_password")
        name = st.text_input("Name", key="add_teacher_name")
        contact_info = st.text_input("Contact Information", key="add_teacher_contact_info")
        subject_expertise = st.text_input("Subject Expertise (comma-separated)", key="add_teacher_subject_expertise")

        # Availability Selection
        st.write("Select Availability:")
        availability_days = st.multiselect("Select Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], key="add_teacher_availability_days")
        availability_start_time = st.time_input("Start Time", key="add_teacher_start_time")
        availability_end_time = st.time_input("End Time", key="add_teacher_end_time")

        add_button = st.form_submit_button("Add Teacher")


    if add_button:
        if not username or not password or not name or not contact_info or not subject_expertise or not availability_days or not availability_start_time or not availability_end_time:
            st.error("Please fill out all fields to add a teacher.")
        elif fetch_one("SELECT user_id FROM users WHERE username = ?", (username,)):
          st.error("User with same username exists")
        else:
            # format the availability using selected day, start time and end time
            formatted_availability = ""
            for day in availability_days:
              formatted_availability += f"{day}:{availability_start_time.strftime('%H-%M')}-{availability_end_time.strftime('%H-%M')},"

            teacher_data = {
              "username": username,
              "password_hash": password, # store password in plain text
              "role": "teacher",
               "name": name,
               "contact_info": contact_info,
               "subject_expertise": subject_expertise,
               "availability": formatted_availability.rstrip(",") #strip the last ,
           }
            insert_data("users",teacher_data)
            st.success("Teacher added successfully!")
            st.rerun()


    st.subheader("Teacher Details")
    all_teachers = fetch_data("SELECT * FROM users where role = 'teacher'") #fetch all teachers only
    if all_teachers:
        for teacher in all_teachers:
           with st.expander(f"Teacher : {teacher[1]}"):
              st.write(f"**Username:** {teacher[1]}")
              st.write(f"**Name:** {teacher[4]}")
              st.write(f"**Contact:** {teacher[5]}")
              st.write(f"**Subjects:** {teacher[6]}")
              st.write(f"**Availability:** {teacher[7]}")

              col1, col2= st.columns(2)
              with col1:
                 if st.button("Edit", key = f"edit_teacher_{teacher[0]}"):
                     st.session_state["edit_teacher_id"] = teacher[0] #set session state
                     st.rerun()
              with col2:
                 if st.button("Delete", key = f"delete_teacher_{teacher[0]}"):
                        delete_data("users", "user_id = ?", (teacher[0],))
                        st.success("Teacher deleted")
                        st.rerun()
    else:
       st.write("No teacher details")

    if "edit_teacher_id" in st.session_state:
        teacher = fetch_one("SELECT * FROM users WHERE user_id = ?", (st.session_state["edit_teacher_id"],))
        if teacher:
            with st.form(key=f"edit_teacher_form_{st.session_state['edit_teacher_id']}", clear_on_submit = True): # unique key
                st.subheader("Edit Teacher Details")
                username = st.text_input("Username", value = teacher[1], key = "edit_teacher_username")
                name = st.text_input("Name", value = teacher[4], key = "edit_teacher_name")
                contact_info = st.text_input("Contact Information", value = teacher[5], key = "edit_teacher_contact_info")
                subject_expertise = st.text_input("Subject Expertise (comma-separated)", value = teacher[6], key = "edit_teacher_subject_expertise")

                 # Edit Availability Selection
                st.write("Select Availability:")
                availability_days = st.multiselect("Select Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], key = "edit_teacher_availability_days", default = get_default_availability_days(teacher[7]) if teacher else [])
                availability_start_time = st.time_input("Start Time", key = "edit_teacher_start_time", value = get_default_availability_time(teacher[7],True) if teacher else None)
                availability_end_time = st.time_input("End Time", key="edit_teacher_end_time", value = get_default_availability_time(teacher[7],False) if teacher else None)

                update_button = st.form_submit_button("Update")
            if update_button:
                formatted_availability = ""
                for day in availability_days:
                     formatted_availability += f"{day}:{availability_start_time.strftime('%H-%M')}-{availability_end_time.strftime('%H-%M')},"

                teacher_data = {
                     "username": username,
                     "name": name,
                      "contact_info": contact_info,
                      "subject_expertise": subject_expertise,
                      "availability": formatted_availability.rstrip(",")
                }
                update_data("users", teacher_data, "user_id = ?", (st.session_state["edit_teacher_id"],))
                st.success("Teacher Updated")
                del st.session_state["edit_teacher_id"] # delete from session
                st.rerun()


def get_default_availability_days(availability_string):
    """Extract the default days for multiselect input"""
    if availability_string:
        days = []
        availabilities = availability_string.split(",")
        for availability in availabilities:
           days.append(availability.split(":")[0])

        return days
    return []

def get_default_availability_time(availability_string,is_start_time):
    """Extracts the default time for time input"""
    if availability_string:
       availabilities = availability_string.split(",")
       if availabilities and len(availabilities)>0:
            time_range = availabilities[0].split(":")[1]
            time_parts = time_range.split("-")
            if is_start_time:
              time = time_parts[0]
            else:
              time = time_parts[1]
            hour,minute = map(int, time.split(":"))
            return datetime.time(hour,minute)
    return None