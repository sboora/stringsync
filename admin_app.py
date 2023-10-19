import streamlit as st

import env
from UserRepository import UserRepository
from TenantRepository import TenantRepository
from OrganizationRepository import OrganizationRepository
from UserType import UserType
from StringSyncRepository import StringSyncRepository

env.set_env()

# Initialize repositories
tenant_repo = TenantRepository()
org_repo = OrganizationRepository()
user_repo = UserRepository()
stringsync_repo = StringSyncRepository()


def main():
    init_session()
    set_app_layout()
    show_introduction()

    # Sidebar for login
    if not user_logged_in():
        login_user()
    else:
        # Welcome message
        st.success(f"Welcome {get_username()}!")
        # Tabs
        register_school_tab, list_schools_tab, register_tutor_tab, list_tutors_tab, assign_tutor_tab, \
        list_tutor_assignments_tab = \
            st.tabs([
                "🏫 Register a School",
                "🏢 List Schools",
                "👩‍🏫 Register a Tutor",
                "👨‍🏫 List Tutors",
                "📝 Assign Tutor to School",
                "📋 List Tutor Assignments"
            ])

        # Register school
        with register_school_tab:
            register_school()
        # List schools
        with list_schools_tab:
            list_schools()
        # Register tutor
        with register_tutor_tab:
            add_tutor()
        # List tutors
        with list_tutors_tab:
            list_tutors()
        # Assign tutor to school
        with assign_tutor_tab:
            assign_tutor()
        # List tutor assignments
        with list_tutor_assignments_tab:
            list_tutor_assignments()

    show_copyright()


def set_app_layout():
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
        show_app_header()
    with col2:
        if user_logged_in():
            show_user_menu()


def show_app_header():
    st.markdown("<h1 style='margin-bottom:0px;'>StringSync</h1>", unsafe_allow_html=True)


def show_introduction():
    st.write("""
            Welcome to the **Admin Portal**! This is your one-stop solution for managing your educational organization. 
            Here's what you can do:

            - **Register Schools**: Register a new school under your organization.
            - **Register Tutors**: register a new tutor to your organization.
            - **Assign Tutors to Schools**: Assign tutors to specific schools within your organization.
            """)


def login_user():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    admin_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login", type='primary'):
        if not username or not admin_password:
            st.sidebar.error("Both username and password are required.")
            return
        success, user_id, org_id = user_repo.authenticate_user(username, admin_password)
        if success:
            set_session_state(user_id, org_id, username)
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")


def show_user_menu():
    col2_1, col2_2 = st.columns([1, 3])  # Adjust the ratio as needed
    with col2_2:
        user_options = st.selectbox("", ["", "Settings", "Logout"], index=0,
                                    format_func=lambda x: f"👤\u2003{get_username()}" if x == "" else x)

        if user_options == "Logout":
            st.session_state["user_logged_in"] = False
            st.rerun()
        elif user_options == "Settings":
            # Navigate to settings page or open settings dialog
            pass


def register_school():
    # Custom CSS to remove form border and adjust padding and margin
    css = r'''
        <style>
            [data-testid="stForm"] {
                border: 0px;
                padding: 0px;
                margin: 0px;
            }
        </style>
    '''

    st.markdown(css, unsafe_allow_html=True)

    with st.form(key='register_school', clear_on_submit=True):
        name = st.text_input("Name")
        description = st.text_input("Description")

        # Create a submit button inside the form
        register_button = st.form_submit_button(label='Register School', type="primary")

    if register_button:
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
    # Custom CSS to remove form border and adjust padding and margin
    css = r'''
            <style>
                [data-testid="stForm"] {
                    border: 0px;
                    padding: 0px;
                    margin: 0px;
                }
            </style>
        '''

    st.markdown(css, unsafe_allow_html=True)
    with st.form(key='register_tutor', clear_on_submit=True):
        name = st.text_input("Name", key="tutor_name")
        username = st.text_input("Username", key="tutor_username")
        email = st.text_input("Email", key="tutor_email")
        password = st.text_input("Password", type="password", key="tutor_password")

        # Create a submit button inside the form
        register_button = st.form_submit_button(label='Register Tutor', type="primary")

    if register_button:
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
    tutors = stringsync_repo.get_users_by_tenant_id_and_type(get_tenant_id(), UserType.TEACHER.value)

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
    # Fetch the list of schools and tutors
    schools = org_repo.get_organizations_by_tenant_id(get_tenant_id())
    tutors = stringsync_repo.get_users_by_tenant_id_and_type(get_tenant_id(), UserType.TEACHER.value)

    # Create dropdowns for selecting a school and a tutor
    school_options = {school['name']: school['id'] for school in schools}
    tutor_options = {tutor['username']: tutor['id'] for tutor in tutors}

    css = r'''
            <style>
                [data-testid="stForm"] {
                    border: 0px;
                    padding: 0px;
                    margin: 0px;
                }
            </style>
        '''

    st.markdown(css, unsafe_allow_html=True)

    with st.form(key='assign_tutor'):
        selected_school_name = st.selectbox("Select School", ['--Select a School--'] + list(school_options.keys()))
        selected_tutor_name = st.selectbox("Select Tutor", ['--Select a Tutor--'] + list(tutor_options.keys()))

        # Create a submit button inside the form
        assign_tutor_button = st.form_submit_button(label='Assign Tutor', type="primary")

    if assign_tutor_button:
        # Validate that both a tutor and a school have been selected
        if selected_school_name == '--Select a School--' or selected_tutor_name == '--Select a Tutor--':
            st.error("Please select both a tutor and a school.")
            return

        selected_school_id = school_options[selected_school_name]
        selected_tutor_id = tutor_options[selected_tutor_name]

        success, message = user_repo.assign_user_to_org(selected_tutor_id, selected_school_id)

        if success:
            st.success(f"Tutor {selected_tutor_name} has been assigned to {selected_school_name}")
        else:
            st.error(f"Failed to assign tutor: {message}")


def list_tutor_assignments():
    # Fetch and display the list of tutor assignments
    tutor_assignments = stringsync_repo.list_tutor_assignments()

    # Create the header for the table
    header_html = """
        <div style='background-color:lightgrey;padding:5px;border-radius:3px;border:1px solid black;'>
            <div style='display:inline-block;width:20%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Tutor Name</p>
            </div>
            <div style='display:inline-block;width:20%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Tutor Username</p>
            </div>
            <div style='display:inline-block;width:20%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>School Name</p>
            </div>
            <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>School Description</p>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Loop through each tutor assignment and create a table row
    for assignment in tutor_assignments:
        row_html = f"""
            <div style='padding:5px;border-bottom:1px solid lightgrey;'>
                <div style='display:inline-block;width:20%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{assignment['tutor_name']}</p>
                </div>
                <div style='display:inline-block;width:20%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{assignment['tutor_username']}</p>
                </div>
                <div style='display:inline-block;width:20%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{assignment['school_name']}</p>
                </div>
                <div style='display:inline-block;width:30%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{assignment['school_description']}</p>
                </div>
            </div>
        """
        st.markdown(row_html, unsafe_allow_html=True)


def init_session():
    if 'user_logged_in' not in st.session_state:
        st.session_state['user_logged_in'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'org_id' not in st.session_state:
        st.session_state['org_id'] = None
    if 'tenant_id' not in st.session_state:
        st.session_state['tenant_id'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None


def user_logged_in():
    return st.session_state['user_logged_in']


def set_session_state(user_id, org_id, username):
    st.session_state['user_logged_in'] = True
    st.session_state['user_id'] = user_id
    st.session_state['org_id'] = org_id
    st.session_state['username'] = username
    success, organization = org_repo.get_organization_by_id(org_id)
    if success:
        st.session_state['tenant_id'] = organization['tenant_id']


def clear_session_state():
    st.session_state['user_logged_in'] = False
    st.session_state['user_id'] = None
    st.session_state['org_id'] = None
    st.session_state['tenant_id'] = None
    st.session_state['username'] = None


def get_org_id():
    return st.session_state['org_id']


def get_username():
    return st.session_state['username']


def get_tenant_id():
    return st.session_state['tenant_id']


def show_copyright():
    st.write("")
    st.write("")
    st.write("")
    footer_html = """
        <div style="text-align: center; color: gray;">
            <p style="font-size: 14px;">© 2023 KA Academy of Indian Music and Dance. All rights reserved.</p>
        </div>
        """
    st.markdown(footer_html, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
