import streamlit as st
from database import fetch_data,fetch_one
import pandas as pd
def render_page():
    st.title("View Timetable")

    # --- Grade and section selection ---
    st.subheader("Select Class and Section")

    grades_data = fetch_data("SELECT * FROM grades")
    grade_options = [grade[1] for grade in grades_data] if grades_data else []
    if grade_options:
        selected_grade = st.selectbox("Select Grade", grade_options, key="select_grade")
    else:
        st.warning("Please add grade details first")
        selected_grade = None

    if selected_grade:
        grade_data = fetch_one("SELECT grade_id, division_count FROM grades WHERE grade_name = ?", (selected_grade,))
        if grade_data:
            division_options = [i + 1 for i in range(grade_data[1])]
            selected_division = st.selectbox("Select Division", division_options, key="select_division")
        else:
            selected_division = None
    else:
        selected_division = None

    if selected_grade and selected_division:
        st.subheader(f"Timetable for {selected_grade} - Division {selected_division}")
        display_timetable(selected_grade, selected_division)
    else:
        st.write("Please select a grade and division to view the timetable.")

def display_timetable(selected_grade, selected_division):
    grade_data = fetch_one("SELECT grade_id FROM grades WHERE grade_name = ?", (selected_grade,))
    if not grade_data:
        st.error(f"Grade '{selected_grade}' not found.")
        return

    grade_id = grade_data[0]
    timetable_data = fetch_data(
        """
        SELECT t.day_of_week, t.start_time, t.end_time, s.subject_name, u.name
        FROM timetable t
        JOIN subjects s ON t.subject_id = s.subject_id
        JOIN users u ON t.teacher_id = u.user_id
        WHERE t.grade_id = ? AND t.division = ?
        ORDER BY t.day_of_week, t.start_time
        """,
        (grade_id, selected_division)
    )

    if not timetable_data:
        st.info("No timetable available for the selected class and division.")
        return

    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = sorted(list(set([item[1] for item in timetable_data])))  # Get unique sorted time slots

    # Create a dictionary to store the timetable data for easy display
    timetable_grid = {day: {} for day in days_of_week}
    for entry in timetable_data:
        day_name = days_of_week[entry[0]]
        timetable_grid[day_name][entry[1]] = f"{entry[3]} with {entry[4]}"

    # Create a Pandas DataFrame for display
    df_data = {}
    df_data["Time"] = time_slots
    for day in days_of_week:
        df_data[day] = [timetable_grid[day].get(time, "") for time in time_slots]

    df = pd.DataFrame(df_data)
    st.dataframe(df)