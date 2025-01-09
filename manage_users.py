import streamlit as st
from database import insert_data, get_all_data, update_data, delete_data, fetch_one, fetch_data,get_by_id

def render_page():
    st.title("Manage Admins")
    st.write("Add, edit, and remove admin details.")

    with st.form("add_admin_form"):
       st.subheader("Add an Admin")
       username = st.text_input("Username", key = "add_admin_username")
       password = st.text_input("Password", type = "password", key = "add_admin_password")
       name = st.text_input("Name", key = "add_admin_name")
       contact_info = st.text_input("Contact Information", key = "add_admin_contact_info")
       add_button = st.form_submit_button("Add Admin")

    if add_button:
       if not username or not password or not name or not contact_info:
            st.error("Please fill out all fields to add admin.")
       elif fetch_one("SELECT user_id FROM users WHERE username = ?", (username,)):
          st.error("User with same username exists")
       else:
            admin_data = {
               "username": username,
               "password_hash": password, # store password in plain text. MUST add hashing functionality in the future
               "role": "admin",
                "name": name,
               "contact_info": contact_info,
           }
            insert_data("users",admin_data)
            st.success("Admin added successfully!")
            st.rerun()


    st.subheader("Admin Details")
    all_admins = fetch_data("SELECT * FROM users where role = 'admin'") #fetch all admins only
    if all_admins:
        for admin in all_admins:
           with st.expander(f"Admin : {admin[1]}"):
              st.write(f"**Username:** {admin[1]}")
              st.write(f"**Name:** {admin[4]}")
              st.write(f"**Contact:** {admin[5]}")

              col1, col2= st.columns(2)
              with col1:
                  if st.button("Edit", key = f"edit_admin_{admin[0]}"):
                       st.session_state["edit_admin_id"] = admin[0] #set session state
                       st.rerun()
              with col2:
                 if st.button("Delete", key = f"delete_admin_{admin[0]}"):
                        delete_data("users", "user_id = ?", (admin[0],))
                        st.success("Admin deleted")
                        st.rerun()
    else:
      st.write("No admin details found.")

    if "edit_admin_id" in st.session_state:
        with st.form("edit_admin_form"):
            st.subheader("Edit Admin Details")
            admin = get_by_id("users","user_id",st.session_state["edit_admin_id"])
            username = st.text_input("Username", value = admin[1])
            name = st.text_input("Name", value = admin[4])
            contact_info = st.text_input("Contact Information", value = admin[5])
            update_button = st.form_submit_button("Update")
        if update_button:
            admin_data = {
               "username": username,
               "name": name,
                "contact_info": contact_info,
           }
            update_data("users", admin_data, "user_id = ?", (st.session_state["edit_admin_id"],))
            st.success("Admin Updated")
            del st.session_state["edit_admin_id"] # delete from session
            st.rerun()