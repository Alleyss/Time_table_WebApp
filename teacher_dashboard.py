import streamlit as st
from database import fetch_one, fetch_data
import pandas as pd
def render_page(user):
    st.title("Teacher Dashboard")
    st.write(f"Welcome, {user[4]}!")

def render_profile_page(user):
    st.title("Teacher Profile")
    teacher = fetch_one("""SELECT u.name, u.contact_info, sub.subject_name, u.availability 
        FROM users u
        INNER JOIN subjects sub ON u.subject_id = sub.subject_id
        WHERE u.user_id = ?""", (user[0],))
    if teacher:
        st.write(f"**Name:** {teacher[0]}")
        st.write(f"**Contact Info:** {teacher[1]}")
        st.write(f"**Subject Expertise:** {teacher[2]}")
        st.write(f"**Availability:** {teacher[3]}")
    else:
        st.write("No teacher profile found")


def render_schedule_page(user):
    st.title("My Schedule")
    teacher_id = user[0]
    schedule_data = fetch_data("""SELECT 
        t.day_of_week, 
        t.start_time, 
        t.end_time, 
        sub.subject_name, 
        t.division,
        g.grade_name
    FROM timetable t
    INNER JOIN subjects sub ON t.subject_id = sub.subject_id
    INNER JOIN grades g ON t.grade_id = g.grade_id
    WHERE t.teacher_id = ?
    ORDER BY t.day_of_week""", (teacher_id,))
    if schedule_data:
        days_of_week = [ "Mon", "Tue", "Wed", "Thu", "Fri"]
        for session in schedule_data:
            if len(session) == 6:
                st.write(f"**Grade:** {session[5]}")
                st.write(f"**Division:** {session[4]}")
                st.write(f"**Day:** {days_of_week[session[0]]}")
                st.write(f"**Subject:** {session[3]}")
                st.write(f"**Time:** {session[1]} - {session[2]}")
                st.write("---")
            else:
                st.write(f"Invalid session data : {session}")
    else:
        st.write("No schedule found for the teacher")

def render_leave_page(user):
    st.write("Leave Form")
    teacher_leave_form(user)

import streamlit as st
from database import insert_data, get_all_data, fetch_data, fetch_one, update_data, delete_data
import datetime



def teacher_leave_form(user):
    st.subheader("Apply for Leave")

    teacher_id = user[0]
    if not teacher_id:
        st.error("Could not identify the current teacher. Please log in again.")
        return

    col1, col2 = st.columns(2)
    start_date = col1.date_input("Start Date")
    end_date = col2.date_input("End Date")
    reason = st.text_area("Reason for Leave")

    if st.button("Submit Leave Request"):
        if start_date and end_date and reason:
            if start_date <= end_date:
                leave_data = {
                    "teacher_id": teacher_id,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d"),
                    "reason": reason,
                    "status": "Pending",
                    "applied_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                insert_data("leave_requests", leave_data)
                st.success("Leave request submitted successfully!")
            else:
                st.error("End date must be after start date.")
        else:
            st.warning("Please fill in all the fields.")

    with st.expander("View Your Existing Leave Requests"):
        existing_requests = fetch_data(
            "SELECT leave_id, start_date, end_date, reason, status, applied_date "
            "FROM leave_requests WHERE teacher_id = ?",
            (teacher_id,)
        )
        if existing_requests:
            df_data = []
            for request in existing_requests:
                df_data.append({
                    "Leave ID": request[0],
                    "Start Date": request[1],
                    "End Date": request[2],
                    "Reason": request[3],
                    "Status": request[4],
                    "Applied Date": request[5]
                })
            st.dataframe(pd.DataFrame(df_data))
        else:
            st.info("No leave requests found.")
