import streamlit as st
from database import insert_data, get_all_data, update_data, delete_data, fetch_one

def render_page():
    st.title("Manage Subjects and Grades")
    st.write("Manage subjects and grades.")

    # --- Subject Management ---
    st.subheader("Manage Subjects")
    with st.form("add_subject_form", clear_on_submit = True):
        st.write("Add a Subject")
        subject_name = st.text_input("Subject Name", key = "add_subject_name")
        subject_description = st.text_area("Subject Description", key = "add_subject_description")
        add_subject_button = st.form_submit_button("Add Subject")

    if add_subject_button:
        if not subject_name:
            st.error("Subject Name is required")
        else:
            subject_data = {
              "subject_name": subject_name,
              "description": subject_description
           }
            insert_data("subjects",subject_data)
            st.success("Subject added successfully!")
            st.rerun()

    st.subheader("Subjects")
    all_subjects = get_all_data("subjects")
    if all_subjects:
        for subject in all_subjects:
           with st.expander(f"Subject : {subject[1]}"):
             st.write(f"**Subject Name:** {subject[1]}")
             st.write(f"**Description:** {subject[2]}")
             col1, col2= st.columns(2)
             with col1:
                  if st.button("Edit", key = f"edit_subject_{subject[0]}"):
                       st.session_state["edit_subject_id"] = subject[0] #set session state
                       st.rerun()
             with col2:
                 if st.button("Delete", key = f"delete_subject_{subject[0]}"):
                        delete_data("subjects", "subject_id = ?", (subject[0],))
                        st.success("Subject deleted")
                        st.rerun()
    else:
        st.write("No Subject Found.")

    if "edit_subject_id" in st.session_state:
        subject = fetch_one("SELECT * FROM subjects WHERE subject_id = ?", (st.session_state["edit_subject_id"],))
        if subject:
            with st.form(key=f"edit_subject_form_{st.session_state['edit_subject_id']}", clear_on_submit = True):
                st.subheader("Edit Subject Details")
                subject_name = st.text_input("Subject Name", value = subject[1], key = "edit_subject_name")
                subject_description = st.text_area("Subject Description", value = subject[2], key="edit_subject_description")

                update_button = st.form_submit_button("Update")
            if update_button:
                 subject_data = {
                    "subject_name": subject_name,
                    "description": subject_description
                 }
                 update_data("subjects", subject_data, "subject_id = ?", (st.session_state["edit_subject_id"],))
                 st.success("Subject updated")
                 del st.session_state["edit_subject_id"] # delete from session
                 st.rerun()


    # --- Grade Management ---
    st.subheader("Manage Grades")
    with st.form("add_grade_form", clear_on_submit = True):
      st.write("Add a Grade")
      grade_name = st.text_input("Grade Name", key = "add_grade_name")
      division_count = st.number_input("Number of divisions", min_value = 1, key = "add_division_count")
      add_grade_button = st.form_submit_button("Add Grade")

    if add_grade_button:
        if not grade_name:
            st.error("Grade Name is required")
        else:
            grade_data = {
               "grade_name": grade_name,
               "division_count": int(division_count)
            }
            insert_data("grades", grade_data)
            st.success("Grade added successfully!")
            st.rerun()

    st.subheader("Grades")
    all_grades = get_all_data("grades")
    if all_grades:
        for grade in all_grades:
            with st.expander(f"Grade : {grade[1]}"):
               st.write(f"**Grade Name:** {grade[1]}")
               st.write(f"**Number of Divisions:** {grade[2]}")
               col1, col2 = st.columns(2)
               with col1:
                   if st.button("Edit", key = f"edit_grade_{grade[0]}"):
                         st.session_state["edit_grade_id"] = grade[0]
                         st.rerun()
               with col2:
                   if st.button("Delete", key = f"delete_grade_{grade[0]}"):
                         delete_data("grades", "grade_id = ?", (grade[0],))
                         st.success("Grade deleted")
                         st.rerun()
    else:
        st.write("No Grades Found.")

    if "edit_grade_id" in st.session_state:
        grade = fetch_one("SELECT * FROM grades WHERE grade_id = ?", (st.session_state["edit_grade_id"],))
        if grade:
            with st.form(key = f"edit_grade_form_{st.session_state['edit_grade_id']}", clear_on_submit = True):
                st.subheader("Edit Grade Details")
                grade_name = st.text_input("Grade Name", value = grade[1], key = "edit_grade_name")
                division_count = st.number_input("Number of divisions", value = grade[2], min_value = 1, key = "edit_division_count")

                update_button = st.form_submit_button("Update")
            if update_button:
                grade_data = {
                   "grade_name": grade_name,
                   "division_count": int(division_count)
                }
                update_data("grades", grade_data, "grade_id = ?", (st.session_state["edit_grade_id"],))
                st.success("Grade Updated")
                del st.session_state["edit_grade_id"]
                st.rerun()