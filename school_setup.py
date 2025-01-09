import streamlit as st
from database import insert_data, get_all_data  # Import functions from database.py

def render_page():
    st.title("School Setup")

    with st.form("school_setup_form"):
        school_name = st.text_input("School Name")
        academic_year_start = st.date_input("Academic Year Start")
        academic_year_end = st.date_input("Academic Year End")
        session_duration_minutes = st.number_input("Session Duration (minutes)", min_value=1)
        break_duration_minutes = st.number_input("Break Duration (minutes)", min_value=0)

        submitted = st.form_submit_button("Submit")

    if submitted:
        if not school_name:
            st.error("School Name is required.")
            return
        if not academic_year_start:
            st.error("Academic Year Start is required.")
            return
        if not academic_year_end:
            st.error("Academic Year End is required.")
            return
        if academic_year_start >= academic_year_end:
          st.error("Academic year start date should be before the end date.")
          return
        if not session_duration_minutes:
            st.error("Session Duration is required")
            return
        if not break_duration_minutes:
           st.error("Break Duration is required")
           return


        school_data = {
            "school_name": school_name,
            "academic_year_start": academic_year_start.strftime("%Y-%m-%d"), #format the date
            "academic_year_end": academic_year_end.strftime("%Y-%m-%d"),
            "session_duration_minutes": int(session_duration_minutes),
            "break_duration_minutes": int(break_duration_minutes)
        }
        insert_data("schools", school_data)
        st.success("School setup details saved!")

    st.subheader("Current School Details")
    school_details = get_all_data("schools")
    if school_details:
        for school in school_details:
            st.write(f"**School Name**: {school[1]}")
            st.write(f"**Academic Year**: {school[2]} - {school[3]}")
            st.write(f"**Session Duration**: {school[4]} minutes")
            st.write(f"**Break Duration**: {school[5]} minutes")
    else:
       st.write("No school details saved")