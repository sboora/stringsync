import streamlit as st

import env
from UserRepository import UserRepository
from TenantRepository import TenantRepository
from OrganizationRepository import OrganizationRepository
from UserType import UserType

env.set_env()

# Initialize repositories
tenant_repo = TenantRepository()
org_repo = OrganizationRepository()
user_repo = UserRepository()


def main():
    # Initialize session state
    init_session()
    st.set_page_config(
        layout='wide'
    )
    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}   
            </style>

            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Create columns for header and logout button
    col1, col2 = st.columns([8.5, 1.5])  # Adjust the ratio as needed

    with col1:
        st.markdown("<h1 style='margin-bottom:0px;'>StringSync - Admin Portal</h1>", unsafe_allow_html=True)

    with col2:
        if user_logged_in():
            col2_1, col2_2 = st.columns([1, 3])  # Adjust the ratio as needed
            with col2_2:
                user_options = st.selectbox("", ["", "Settings", "Logout"], index=0,
                                            format_func=lambda x: f"👤\u2003{get_admin_username()}" if x == "" else x)

                if user_options == "Logout":
                    st.session_state["user_logged_in"] = False
                    st.rerun()
                elif user_options == "Settings":
                    # Navigate to settings page or open settings dialog
                    pass

    st.write("""
            Welcome to the Admin Portal! This is your one-stop solution for managing your educational organization. Here's what you can do:

            - **Register Schools**: Register a new school under your organization.
            - **Register Tutors**: register a new tutor to your organization.
            - **Assign Tutors to Schools**: Assign tutors to specific schools within your organization.
            """)

    # Sidebar for login
    if not user_logged_in():
        st.sidebar.header("Login")
        admin_username = st.sidebar.text_input("Username")
        admin_password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login", type='primary'):
            if not admin_username or not admin_password:
                st.sidebar.error("Both username and password are required.")
                return
            success, admin_id, org_id = user_repo.authenticate_user(admin_username, admin_password)
            if success:
                set_session_state(admin_id, org_id, admin_username)
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password.")
    else:
        if user_logged_in():
            st.success(f"Welcome {get_admin_username()}!")

            add_school_tab, add_tutor_tab, assign_tutor_tab = \
                st.tabs(["🏫 Register a School", "👩‍🏫 Register a Tutor", "📝 Assign Tutor to School"])

            with add_school_tab:
                add_school()
                list_schools()

            with add_tutor_tab:
                add_tutor()
                list_tutors()

            with assign_tutor_tab:
                assign_tutor()
                list_tutor_assignments()


def add_school():
    st.subheader("Register School")
    name = st.text_input("Name", key="school_name")
    description = st.text_input("Description", key="school_description")

    if st.button("Register", key="register_school", type='primary'):
        success, org_id, join_code, message = org_repo.register_organization(
            get_tenant_id(), name, description, False)
        if success:
            st.success(message)
        else:
            st.error(message)


def list_schools():
    # Fetch and display the list of schools linked to this admin (tenant)
    schools = org_repo.get_organizations_by_tenant_id(get_tenant_id())

    # Create the header for the table
    header_html = """
        <div style='background-color:lightgrey;padding:5px;border-radius:3px;border:1px solid black;'>
            <div style='display:inline-block;width:32%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Organization Name</p>
            </div>
            <div style='display:inline-block;width:32%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Organization Description</p>
            </div>
            <div style='display:inline-block;width:32%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Join Code</p>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Loop through each school and create a table row
    for school in schools:
        row_html = f"""
            <div style='padding:5px;border-bottom:1px solid lightgrey;'>
                <div style='display:inline-block;width:32%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{school['name']}</p>
                </div>
                <div style='display:inline-block;width:32%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{school['description']}</p>
                </div>
                <div style='display:inline-block;width:32%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{school['join_code']}</p>
                </div>
            </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)


def add_tutor():
    st.subheader("Register Tutor")
    name = st.text_input("Name", key="tutor_name")
    username = st.text_input("Username", key="tutor_username")
    email = st.text_input("Email", key="tutor_email")
    password = st.text_input("Password", type="password", key="tutor_password")

    if st.button("Register", key="register_tutor", type='primary'):
        # Using the register_user function from user_repo to add a tutor
        success, message = user_repo.register_user(
            name=name,
            username=username,
            email=email,
            password=password,
            org_id=get_org_id(),
            user_type=UserType.TEACHER.value
        )
        if success:
            st.success(message)
        else:
            st.error(message)


def list_tutors():
    # Fetch and display the list of tutors linked to this org group
    tutors = user_repo.get_users_by_org_id_and_type(get_org_id(), UserType.TEACHER.value)

    # Create the header for the table
    header_html = """
        <div style='background-color:lightgrey;padding:5px;border-radius:3px;border:1px solid black;'>
            <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Name</p>
            </div>
            <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Username</p>
            </div>
            <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Email</p>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Loop through each tutor and create a table row
    for tutor in tutors:
        row_html = f"""
            <div style='padding:5px;border-bottom:1px solid lightgrey;'>
                <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{tutor['name']}</p>
                </div>
                <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{tutor['username']}</p>
                </div>
                <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{tutor['email']}</p>
                </div>
            </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)


def assign_tutor():
    st.subheader("Assign Tutor to School")

    # Fetch the list of schools and tutors
    schools = org_repo.get_organizations_by_tenant_id(get_tenant_id())
    tutors = user_repo.get_users_by_org_id_and_type(get_org_id(), UserType.TEACHER.value)

    # Create dropdowns for selecting a school and a tutor
    school_options = {school['name']: school['id'] for school in schools}
    tutor_options = {tutor['username']: tutor['id'] for tutor in tutors}

    selected_school_name = st.selectbox("Select School", ['--Select a School--'] + list(school_options.keys()))
    selected_tutor_name = st.selectbox("Select Tutor", ['--Select a Tutor--'] + list(tutor_options.keys()))

    if st.button("Assign", key="assign_tutor", type='primary'):
        # Validate that both a tutor and a school have been selected
        if selected_school_name == '--Select a School--' or selected_tutor_name == '--Select a Tutor--':
            st.error("Please select both a tutor and a school.")
            return

        selected_school_id = school_options[selected_school_name]
        selected_tutor_id = tutor_options[selected_tutor_name]

        # Assume you have a function like this in your repository
        success, message = user_repo.assign_user_to_org(selected_tutor_id, selected_school_id)

        if success:
            st.success(f"Tutor {selected_tutor_name} has been assigned to {selected_school_name}")
        else:
            st.error(f"Failed to assign tutor: {message}")


def list_tutor_assignments():
    pass


def init_session():
    if 'user_logged_in' not in st.session_state:
        st.session_state['user_logged_in'] = False
    if 'admin_id' not in st.session_state:
        st.session_state['admin_id'] = None
    if 'org_id' not in st.session_state:
        st.session_state['org_id'] = None
    if 'tenant_id' not in st.session_state:
        st.session_state['tenant_id'] = None
    if 'admin_username' not in st.session_state:
        st.session_state['admin_username'] = None


def user_logged_in():
    return st.session_state['user_logged_in']


def set_session_state(admin_id, org_id, admin_username):
    st.session_state['user_logged_in'] = True
    st.session_state['admin_id'] = admin_id
    st.session_state['org_id'] = org_id
    st.session_state['admin_username'] = admin_username
    success, organization = org_repo.get_organization_by_id(org_id)
    if success:
        st.session_state['tenant_id'] = organization['tenant_id']


def clear_session_state():
    st.session_state['user_logged_in'] = False
    st.session_state['admin_id'] = None
    st.session_state['org_id'] = None
    st.session_state['tenant_id'] = None
    st.session_state['admin_username'] = None


def get_org_id():
    return st.session_state['org_id']


def get_admin_username():
    return st.session_state['admin_username']


def get_tenant_id():
    return st.session_state['tenant_id']


if __name__ == "__main__":
    main()
