import streamlit as st
from database import insert_data, get_all_data, update_data, delete_data, fetch_one, fetch_data
import datetime
import pandas as pd

def render_page():
    st.title("Timetable Management")
    st.write("Manage sessions and generate timetables.")

    # --- Grade and section selection ---
    st.subheader("Select Class and Section")

    grade_options = [grade[1] for grade in get_all_data("grades")]
    if grade_options:
        selected_grade = st.selectbox("Select Grade", grade_options, key = "select_grade")
    else:
         st.warning("Please add grade details first")
         selected_grade = None

    if selected_grade:
        grade_data = fetch_one("SELECT * FROM grades WHERE grade_name = ?", (selected_grade,))
        division_options = [i+1 for i in range(grade_data[2])]
        selected_division = st.selectbox("Select Division", division_options, key = "select_division")
    else:
      selected_division = None

    if selected_grade and selected_division:
      st.subheader(f"Set Timetable for {selected_grade} - Division {selected_division}")
      timetable_grid(selected_grade, selected_division)
    else:
        st.write("Please select a grade and division to view timetable.")


def timetable_grid(selected_grade, selected_division):

  school_details = fetch_one("SELECT * FROM schools")
  start_time = datetime.datetime.strptime("08:00", "%H:%M").time() #default start time. Needs to be configurable
  session_duration = school_details[4] if school_details else 45
  break_duration = school_details[5] if school_details else 15

  end_time = datetime.datetime.strptime("16:00", "%H:%M").time()  #default end time. Needs to be configurable
  days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri"]
  break_1_time = datetime.datetime.strptime("10:00", "%H:%M").time()
  lunch_break_time = datetime.datetime.strptime("12:00", "%H:%M").time()
  break_2_time = datetime.datetime.strptime("14:30", "%H:%M").time()
  periods = []
  current_time = start_time
  while current_time < end_time:
        periods.append(current_time)
        current_time_dt = datetime.datetime.combine(datetime.datetime.today(), current_time)
        current_time_dt += datetime.timedelta(minutes=session_duration)
        current_time = current_time_dt.time()

  # Create data structure for the grid
  grid_data = {}

  for day in days_of_week:
        grid_data[day] = {}
        for period_index, period in enumerate(periods):
             time = period.strftime("%H:%M")
             grid_data[day][time] = {"subject":"", "teacher":""} # initialize the values, now it stores both teacher and subject

  # --- Prefill existing values ---
  grade_id = fetch_one("SELECT grade_id FROM grades WHERE grade_name = ?", (selected_grade,))[0]
  all_sessions = fetch_data("SELECT s.session_id, s.day_of_week, s.start_time, sub.subject_name, u.name FROM sessions s INNER JOIN subjects sub ON s.subject_id = sub.subject_id INNER JOIN users u ON s.teacher_id = u.user_id WHERE s.grade_id = ?", (grade_id,))
  if all_sessions:
      for session in all_sessions:
          if days_of_week[session[1]] in grid_data:
              grid_data[days_of_week[session[1]]][session[2]] = {"subject":session[3], "teacher":session[4], "session_id":session[0]} #prefill the subject and teacher


  with st.form("timetable_form", clear_on_submit=True):
      st.write("Edit Timetable")
      st.write(" ")
      days = st.columns(len(days_of_week) + 1 ) #create an extra column for the time
      for col_index, day in enumerate(days_of_week):
            with days[col_index + 1]: # shift all the days by 1, so that 0th column is time.
              st.write(f"**{day}**")
              for period_index, period in enumerate(periods):
                 time = period.strftime("%H:%M")
                 subject_options = [subject[1] for subject in get_all_data("subjects")]
                 selected_subject = st.selectbox(f"Subject {time}", options = subject_options, key = f"subject_{day}_{time}", index = subject_options.index(grid_data[day].get(time).get("subject")) if grid_data[day].get(time).get("subject") else 0) #get previous value

                 teacher_options = fetch_data("SELECT u.user_id, u.name FROM users u WHERE role = 'teacher'") # teacher options
                 if teacher_options:
                     teacher_names = [teacher[1] for teacher in teacher_options]
                     selected_teacher = st.selectbox(f"Teacher {time}", options = teacher_names, key = f"teacher_{day}_{time}", index = teacher_names.index(grid_data[day].get(time).get("teacher")) if grid_data[day].get(time).get("teacher") else 0 )#get previous value
                 else:
                     st.write("No teachers available. Please add teacher details")
                     selected_teacher = None
                 grid_data[day][time] = {"subject": selected_subject, "teacher": selected_teacher, "session_id": grid_data[day].get(time).get("session_id")} #update grid data

      with days[0]: #time columns
          st.write("**Time**")
          for period in periods:
              st.write(period.strftime("%H:%M"))

      save_button = st.form_submit_button("Save Timetable")
  if save_button:
      st.write("saving the timetable")
      save_timetable(grid_data,selected_grade,selected_division)
    
def save_timetable(grid_data, selected_grade, selected_division):
      grade_id = fetch_one("SELECT grade_id FROM grades WHERE grade_name = ?", (selected_grade,))[0]
      delete_data("timetables","session_id IN (SELECT session_id from sessions WHERE grade_id = ?)", (grade_id,))
      days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri"]
      for day_index, day in enumerate(days_of_week):
            for time, data in grid_data[day].items():
              if data["subject"] and data["teacher"]: # check if subject and teacher is selected
                 selected_subject = fetch_one("SELECT subject_id FROM subjects WHERE subject_name = ?", (data["subject"],))[0]
                 selected_teacher = fetch_one("SELECT u.user_id FROM users u WHERE u.name = ?", (data["teacher"],))[0]
                 existing_session = fetch_one("SELECT session_id FROM sessions WHERE grade_id = ? AND day_of_week = ? AND start_time = ?", (grade_id,day_index, time))
                 if existing_session:
                  session_id = existing_session[0] #if a session exists for a time, we use the existing session_id to map
                 else:
                   session_data = { # otherwise we insert a new session and add that new session_id to the time tables.
                       "grade_id": grade_id,
                       "subject_id": selected_subject,
                       "teacher_id": selected_teacher,
                       "day_of_week": day_index,
                       "start_time": time,
                       "end_time": (datetime.datetime.strptime(time, "%H:%M") + datetime.timedelta(minutes = 45)).strftime("%H:%M")
                     }
                   insert_data("sessions", session_data)
                   session_id = fetch_one("SELECT last_insert_rowid()")[0] # fetch newly created session id.

                 timetable_data = {
                  "session_id": session_id,
                  "teacher_id": selected_teacher,
                 }
                 insert_data("timetables", timetable_data) #create the time table entry

      st.success("Timetable Saved")
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