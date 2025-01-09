import streamlit as st
from database import fetch_one  # Import functions from database.py
import school_setup
import admin_dashboard
import manage_teachers
import manage_users
import manage_subjects
import timetable_management

# --- Helper Functions ---
def hash_password(password):
    """Hashes the password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(input_password, hashed_password):
    """Verifies input password matches stored hashed password"""
    return hash_password(input_password) == hashed_password

# --- Session State Initialisation ---
if "user" not in st.session_state:
    st.session_state["user"] = None

# --- Page Setup ---
st.set_page_config(
    page_title="School Timetable App",
    page_icon="🏫",
    layout="wide",
)

# --- Login ---
def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username and password:
           user = fetch_one("SELECT user_id,username, password_hash, role FROM users WHERE username = ?", (username,))
           if user and password == user[2]:
              st.session_state["user"] = user
              st.success("Logged in successfully")
              st.rerun()
           else:
               st.error("Invalid Username or Password")
        else:
            st.error("Please enter username and password")


# --- Main App Logic ---

if st.session_state["user"] is None:
    login_page()
else:
    user = st.session_state["user"]
    # --- Navigation Bar ---
    st.sidebar.title("Navigation")
    if user[3] == "admin":
       page = st.sidebar.radio("Go to", ["Admin Dashboard","Manage Teachers","Manage Users","School Details","Manage Subjects and Grades", "Timetable Management"])
    else:
        page = st.sidebar.radio("Go to", ["Teacher Dashboard", "Teacher Profile"])

    if st.sidebar.button("Logout"):
       st.session_state["user"] = None
       st.rerun() # reruns the current app

    # --- Page Layout ---
    if user[3] == "admin": # Check for Admin
       if page == "Admin Dashboard":
           admin_dashboard.render_page() # render the admin dashboard
       elif page == "Manage Teachers":
         manage_teachers.render_page() # render manage teachers page
       elif page == "Manage Users":
            manage_users.render_page() # render manage users page
       elif page == "School Details":
            school_setup.render_page() #render the school setup page
       elif page == "Manage Subjects and Grades":
            manage_subjects.render_page() #render manage subjects and grades page
       elif page == "Timetable Management":
            timetable_management.render_page() #render the timetable management page
    elif user[3] == "teacher": # Check for Teacher
      if page == "Teacher Dashboard":
         st.title("Teacher Dashboard")
         st.write("View your schedule and manage your profile here.")
      elif page == "Teacher Profile":
            st.title("Teacher Profile")
            st.write("Here you can see your profile")