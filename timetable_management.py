import streamlit as st
from database import insert_data, get_all_data, update_data, delete_data, fetch_one, fetch_data
import datetime
import pandas as pd
import gemini_ai
import json
import re

st.session_state["timetable_df"] = None

def render_page():
    st.title("Timetable Management")
    st.write("Manage sessions and generate timetables.")

    # --- Grade and section selection ---
    st.subheader("Select Class and Section")

    grade_options = [grade[1] for grade in get_all_data("grades")]
    if grade_options:
        selected_grade = st.selectbox("Select Grade", grade_options, key="select_grade")
    else:
        st.warning("Please add grade details first")
        selected_grade = None

    if selected_grade:
        grade_data = fetch_one("SELECT * FROM grades WHERE grade_name = ?", (selected_grade,))
        if grade_data:
            division_options = [i + 1 for i in range(grade_data[2])]
            selected_division = st.selectbox("Select Division", division_options, key="select_division")
        else:
            selected_division = None
    else:
        selected_division = None

    if selected_grade and selected_division:
        st.subheader(f"Set Timetable for {selected_grade} - Division {selected_division}")
        school_details = fetch_one("SELECT * FROM schools")
        start_time = datetime.datetime.strptime("09:00", "%H:%M").time()
        end_time = datetime.datetime.strptime("16:00", "%H:%M").time()  # default end time. Needs to be configurable
        break_1_time = datetime.datetime.strptime("10:30", "%H:%M").time()
        lunch_break_time = datetime.datetime.strptime("12:15", "%H:%M").time()
        break_2_time = datetime.datetime.strptime("14:15", "%H:%M").time()
        session_duration = school_details[4] if school_details else 45
        time_slots = generate_time_slots(start_time, end_time, session_duration, break_1_time, lunch_break_time, break_2_time)
        st.button("Generate Timetable", on_click=generate_timetable, args=(selected_grade, selected_division))
        if "timetable_df" in st.session_state and st.session_state["timetable_df"] is not None:
            st.dataframe(st.session_state["timetable_df"])
        if "timetable_df" in st.session_state and st.session_state["timetable_df"] is not None:
            st.button("Save Timetable", on_click=store_timetable_to_db, args=(st.session_state['timetable_df'], selected_grade, selected_division))

        if "timetable_text" in st.session_state and st.session_state["timetable_text"] is not None and isinstance(st.session_state["timetable_text"], str):
            st.text(f"Gemini response: {st.session_state['timetable_text']}")
        timetable_grid(selected_grade, selected_division, time_slots, st.session_state.get("timetable_text", None) if isinstance(st.session_state.get("timetable_text", None), str) else None)
    else:
        st.write("Please select a grade and division to view timetable.")

def generate_timetable(selected_grade, selected_division):
    """Generate timetable from AI and store it in session state"""
    school_details = fetch_one("SELECT * FROM schools")
    start_time = datetime.datetime.strptime("09:00", "%H:%M").time()
    end_time = datetime.datetime.strptime("16:00", "%H:%M").time()  # default end time. Needs to be configurable
    break_1_time = datetime.datetime.strptime("10:30", "%H:%M").time()
    lunch_break_time = datetime.datetime.strptime("12:15", "%H:%M").time()
    break_2_time = datetime.datetime.strptime("14:15", "%H:%M").time()
    session_duration = school_details[4] if school_details else 45

    time_slots = generate_time_slots(start_time, end_time, session_duration, break_1_time, lunch_break_time, break_2_time)

    prompt = gemini_ai.generate_timetable_prompt(selected_grade, selected_division, time_slots)
    if prompt:
        timetable_data = gemini_ai.generate_timetable_json(prompt)
        if timetable_data:
            timetable_df = create_timetable_dataframe(timetable_data, time_slots)
            st.session_state["timetable_df"] = timetable_df
            st.session_state["timetable_text"] = None
        else:
            st.session_state["timetable_df"] = None
            st.session_state["timetable_text"] = prompt
    else:
        st.error("Error in generating prompt")
        st.session_state["timetable_df"] = None
        st.session_state["timetable_text"] = None

    st.rerun()  # force re-render after AI call

def create_timetable_dataframe(timetable_data, time_slots):
    if timetable_data:
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        grid_data = {}

        # Initialize the grid data with empty strings for each time slot
        for day in days_of_week:
            grid_data[day] = {}
            for time in time_slots:
                grid_data[day][time] = ""

        # Populate the grid data with timetable information
        for day_schedule in timetable_data:
            day = day_schedule.get("day")
            if day in grid_data:
                for session in day_schedule.get("sessions", []):
                    start_time = session.get("start_time")
                    if start_time in grid_data[day]:
                        subject_data = fetch_one("SELECT subject_name FROM subjects WHERE subject_id = ?", (session.get("subject"),))
                        teacher_data = fetch_one("SELECT name FROM users WHERE user_id = ?", (session.get("teacher"),))
                        subject_name = subject_data[0] if subject_data else 'N/A'
                        teacher_name = teacher_data[0] if teacher_data else 'N/A'
                        grid_data[day][start_time] = f"Subject: {subject_name}, Teacher: {teacher_name}"

        # Create and return a DataFrame
        timetable_df = pd.DataFrame.from_dict(grid_data, orient="index").transpose()
        st.session_state['timetable_df'] = timetable_df
        return timetable_df

    return None

def store_timetable_to_db(timetable_df, grade_name, division):
    """
    Process timetable DataFrame and store in database

    Args:
        timetable_df: pandas DataFrame containing timetable data
        grade_name: String name of the grade
        division: Integer division/section number
    """
    if timetable_df is None or timetable_df.empty:
        st.warning("No timetable data to save.")
        return

    grade_data = fetch_one("SELECT grade_id FROM grades WHERE grade_name = ?", (grade_name,))
    if not grade_data:
        st.error(f"Grade '{grade_name}' not found in database.")
        return
    grade_id = grade_data[0]

    delete_data("timetable", "grade_id = ? AND division = ?", (grade_id, division))
    day_map = {
        'Monday': 0,
        'Tuesday': 1,
        'Wednesday': 2,
        'Thursday': 3,
        'Friday': 4
    }

    def parse_cell(cell):
        if not isinstance(cell, str) or "Subject: N/A, Teacher: N/A" in cell or not cell:
            return None, None
        match = re.match(r"Subject: (.+), Teacher: (.+)", cell)
        if match:
            subject = match.group(1)
            teacher = match.group(2)
            return subject, teacher
        return None, None

    for day_name, day_index in day_map.items():
        if day_name in timetable_df.columns:
            for time_slot, cell_data in timetable_df[day_name].items():
                if time_slot not in ['10:30', '12:15', '14:15']:
                    subject, teacher = parse_cell(cell_data)
                    if subject and teacher:
                        subject_data = fetch_one('SELECT subject_id FROM subjects WHERE subject_name = ?', (subject,))
                        teacher_data = fetch_one('SELECT user_id FROM users WHERE name = ?', (teacher,))

                        if subject_data and teacher_data:
                            subject_id = subject_data[0]
                            teacher_id = teacher_data[0]

                            timetable_entry = {
                                'grade_id': grade_id,
                                'subject_id': subject_id,
                                'day_of_week': day_index,
                                'start_time': time_slot,
                                'end_time': (datetime.datetime.strptime(time_slot, "%H:%M") + datetime.timedelta(minutes=45)).strftime("%H:%M"),
                                'teacher_id': teacher_id,
                                'division': division
                            }
                            insert_data('timetable', timetable_entry)
                        else:
                            if not subject_data:
                                st.error(f"Subject '{subject}' not found in database.")
                            if not teacher_data:
                                st.error(f"Teacher '{teacher}' not found in database.")

    st.success("Timetable saved successfully")

def timetable_grid(selected_grade, selected_division, time_slots=None, timetable_text=None):
    school_details = fetch_one("SELECT * FROM schools")
    start_time = datetime.datetime.strptime("09:00", "%H:%M").time()  # default start time. Needs to be configurable
    session_duration = school_details[4] if school_details else 45
    break_duration = school_details[5] if school_details else 15

    end_time = datetime.datetime.strptime("16:00", "%H:%M").time()  # default end time. Needs to be configurable
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    break_1_time = datetime.datetime.strptime("10:30", "%H:%M").time()
    lunch_break_time = datetime.datetime.strptime("12:15", "%H:%M").time()
    break_2_time = datetime.datetime.strptime("14:15", "%H:%M").time()

    if not time_slots:
        time_slots = generate_time_slots(start_time, end_time, session_duration, break_1_time, lunch_break_time, break_2_time)

    # Create data structure for the grid
    grid_data = {}

    for day in days_of_week:
        grid_data[day] = {}
        for time in time_slots:
            grid_data[day][time] = {"subject": "", "teacher": ""}  # initialize the values, now it stores both teacher and subject

    # --- Prefill existing values ---
    grade_data = fetch_one("SELECT grade_id FROM grades WHERE grade_name = ?", (selected_grade,))
    if grade_data:
        grade_id = grade_data[0]
        all_sessions = fetch_data("SELECT t.id, t.day_of_week, t.start_time, sub.subject_name, u.name FROM timetable t INNER JOIN subjects sub ON t.subject_id = sub.subject_id INNER JOIN users u ON t.teacher_id = u.user_id WHERE t.grade_id = ? and t.division = ?", (grade_id, selected_division))
        if all_sessions:
            for session in all_sessions:
                if days_of_week[session[1]] in grid_data:
                    grid_data[days_of_week[session[1]]][session[2]] = {"subject": session[3], "teacher": session[4], "timetable_id": session[0]}

    if timetable_text and isinstance(timetable_text, str):
        timetable_data_list = []
        # use regex to extract the JSON from response
        json_match = re.search(r'(\[.*\])', timetable_text, re.DOTALL)
        if json_match:
            try:
                json_string = json_match.group(1)
                timetable_data_list = json.loads(json_string.strip())
                if timetable_data_list:
                    for day_schedule in timetable_data_list:
                        day = day_schedule.get("day")
                        if day in grid_data:
                            for session in day_schedule.get("sessions", []):
                                if session.get("start_time") in grid_data[day]:
                                    subject_data = fetch_one("SELECT subject_name FROM subjects WHERE subject_id = ?", (session.get('subject'),))
                                    teacher_data = fetch_one("SELECT name FROM users WHERE user_id = ?", (session.get('teacher'),))
                                    subject_name = subject_data[0] if subject_data else ""
                                    teacher_name = teacher_data[0] if teacher_data else ""
                                    grid_data[day][session["start_time"]] = {"subject": subject_name, "teacher": teacher_name, "timetable_id": grid_data[day].get(session.get("start_time")).get("timetable_id")}

            except Exception as e:
                st.error(f"Could not parse the json : {e}")

    with st.form("timetable_form", clear_on_submit=True):
        st.write("Edit Timetable")
        st.write(" ")
        days = st.columns(len(days_of_week) + 1)  # create an extra column for the time
        with days[0]:
            st.write("**Time**")
            for time in time_slots:
                if time == "10:30":
                    st.write(f"Snack Break")
                elif time == "12:15":
                    st.write(f"Lunch Break")
                elif time == "14:15":
                    st.write(f"Post Lunch Break")
                else:
                    st.write(" \n")
                    st.write(time)
                    st.write(" \n")
                    st.write(" ")
                    st.write(" ")
                    st.write(" ")
                    st.write(" ")
                    st.write(" ")

        for col_index, day in enumerate(days_of_week):
            with days[col_index + 1]:  # shift all the days by 1, so that 0th column is time.
                st.write(f"**{day}**")
                for time in time_slots:
                    if time not in ["10:30", "12:15", "14:15"]:
                        subject_options = [subject[1] for subject in get_all_data("subjects")]
                        default_subject_index = subject_options.index(grid_data[day].get(time).get("subject")) if grid_data[day].get(time).get("subject") in subject_options else 0
                        selected_subject = st.selectbox(f"Subject {time}", options=subject_options, key=f"subject_{day}_{time}", index=default_subject_index)  # get previous value

                        teacher_options = fetch_data("SELECT u.user_id, u.name FROM users u WHERE role = 'teacher' AND subject_id = (SELECT subject_id FROM subjects WHERE subject_name = ?)", (selected_subject,))  # teacher options
                        if teacher_options:
                            teacher_names = [teacher[1] for teacher in teacher_options]
                            default_teacher_index = teacher_names.index(grid_data[day].get(time).get("teacher")) if grid_data[day].get(time).get("teacher") in teacher_names else 0
                            selected_teacher = st.selectbox(f"Teacher {time}", options=teacher_names, key=f"teacher_{day}_{time}", index=default_teacher_index)  # get previous value
                        else:
                            st.write("No teachers available. Please add teacher details")
                            selected_teacher = None
                        grid_data[day][time] = {"subject": selected_subject, "teacher": selected_teacher, "timetable_id": grid_data[day].get(time).get("timetable_id")}  # update grid data

        save_button = st.form_submit_button("Save Timetable")
    if save_button:
        st.write("saving the timetable")
        save_timetable(grid_data, selected_grade, selected_division)

def save_timetable(grid_data, selected_grade, selected_division):
    grade_data = fetch_one("SELECT grade_id FROM grades WHERE grade_name = ?", (selected_grade,))
    if grade_data:
        grade_id = grade_data[0]
        delete_data("timetable", "grade_id = ? and division = ?", (grade_id, selected_division))
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        timetable_list = []
        for day_index, day in enumerate(days_of_week):
            for time, data in grid_data[day].items():
                if data["subject"] and data["teacher"] and time not in ["10:30", "12:15", "14:15"]:  # check if subject and teacher is selected and the time slot is not a break
                    selected_subject = fetch_one("SELECT subject_id FROM subjects WHERE subject_name = ?", (data["subject"],))
                    if selected_subject:
                        selected_subject_id = selected_subject[0]
                        selected_teacher = fetch_one("SELECT u.user_id FROM users u WHERE u.name = ?", (data["teacher"],))
                        if selected_teacher:
                            selected_teacher_id = selected_teacher[0]
                            timetable_data = {
                                "grade_id": grade_id,
                                "subject_id": selected_subject_id,
                                "teacher_id": selected_teacher_id,
                                "day_of_week": day_index,
                                "start_time": time,
                                "end_time": (datetime.datetime.strptime(time, "%H:%M") + datetime.timedelta(minutes=45)).strftime("%H:%M"),
                                "division": selected_division
                            }
                            insert_data("timetable", timetable_data)

                        else:
                            st.error(f"Teacher not found for day: {day} and time: {time}")
                    else:
                        st.error(f"Subject not found for day: {day} and time: {time}")

        if timetable_list:
            st.success("Timetable Saved")
        else:
            st.info("No timetable entries to save.")
    else:
        st.error(f"Grade '{selected_grade}' not found.")

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

def get_default_availability_time(availability_string, is_start_time):
    """Extracts the default time for time input"""
    if availability_string:
        availabilities = availability_string.split(",")
        if availabilities and len(availabilities) > 0:
            time_range = availabilities[0].split(":")[1]
            time_parts = time_range.split("-")
            if is_start_time:
                time = time_parts[0]
            else:
                time = time_parts[1]
            hour, minute = map(int, time.split(":"))
            return datetime.time(hour, minute)
    return None

def generate_time_slots(start_time, end_time, session_duration, break_1_time, lunch_break_time, break_2_time):
    """Generate a list of time intervals based on the session duration and break times"""
    periods = []
    current_time = start_time
    while current_time < end_time:
        periods.append(current_time.strftime("%H:%M"))
        current_time_dt = datetime.datetime.combine(datetime.datetime.today(), current_time)
        current_time_dt += datetime.timedelta(minutes=session_duration)
        current_time = current_time_dt.time()
        if current_time.strftime("%H:%M") == break_1_time.strftime("%H:%M"):
            periods.append(current_time.strftime("%H:%M"))
            current_time_dt = datetime.datetime.combine(datetime.datetime.today(), current_time)
            current_time_dt += datetime.timedelta(minutes=15)
            current_time = current_time_dt.time()
        elif current_time.strftime("%H:%M") == lunch_break_time.strftime("%H:%M"):
            periods.append(current_time.strftime("%H:%M"))
            current_time_dt = datetime.datetime.combine(datetime.datetime.today(), current_time)
            current_time_dt += datetime.timedelta(minutes=30)
            current_time = current_time_dt.time()
        elif current_time.strftime("%H:%M") == break_2_time.strftime("%H:%M"):
            periods.append(current_time.strftime("%H:%M"))
            current_time_dt = datetime.datetime.combine(datetime.datetime.today(), current_time)
            current_time_dt += datetime.timedelta(minutes=15)
            current_time = current_time_dt.time()

    return periods

if __name__ == "__main__":
    render_page()