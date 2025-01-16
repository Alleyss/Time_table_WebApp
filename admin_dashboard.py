import streamlit as st
from database import get_all_data, fetch_data
import pandas as pd
import plotly.express as px

def render_page():
    st.title("Admin Dashboard")
    st.write("Manage school settings and timetables here.")

    # Display basic statistics
    st.subheader("Quick Statistics")

    # Count teachers
    teachers = fetch_data("SELECT * FROM users WHERE role = 'teacher'")
    if teachers:
        num_teachers = len(teachers)
    else:
        num_teachers = 0
    st.write(f"Number of Teachers: {num_teachers}")

    # Count students
    students = get_all_data("students")
    if students:
      num_students = len(students)
    else:
      num_students = 0
    st.write(f"Number of Students: {num_students}")

    # Count teachers
    admins = fetch_data("SELECT * FROM users WHERE role = 'admin'")
    if admins:
        num_admins = len(admins)
    else:
        num_admins = 0
    st.write(f"Number of Admins: {num_admins}")

    # Count Users
    users = get_all_data("users")
    if users:
        num_users = len(users)
    else:
      num_users = 0
    st.write(f"Number of Users: {num_users}")



    # --- Student Data Table ---
    st.subheader("Student Data")
    all_students = get_all_data("students")
    if all_students:
      students_df = pd.DataFrame(all_students, columns = ["student_id","student_name","grade_id"])
      st.dataframe(students_df)
    else:
      st.write("No student data available.")