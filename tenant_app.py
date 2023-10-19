import os

import streamlit as st

import env
from UserRepository import UserRepository
from TenantRepository import TenantRepository
from OrganizationRepository import OrganizationRepository

env.set_env()

# Initialize repositories
tenant_repo = TenantRepository()
org_repo = OrganizationRepository()
user_repo = UserRepository()


# Tenant registration form
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
        register_tenant_tab, list_tenants_tab = \
            st.tabs(["🏢 Register a Tenant", "📋 List Tenants"])

        with register_tenant_tab:
            register_tenant()
        with list_tenants_tab:
            list_tenants()

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


def show_introduction():
    st.write("""
            Welcome to the **Tenant Portal**! This is your centralized hub for overseeing multiple educational organizations. 
            Here's what you can accomplish:

            - **Register New Tenants**: Add new educational organizations to expand your network.
            - **List All Tenants**: View a comprehensive list of all registered educational organizations.

            This portal is designed to make the management of multiple organizations as seamless as possible. 
            Navigate through the sidebar to explore all the functionalities available to you.
            """)


def login_user():
    st.sidebar.header("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login", type='primary'):
        if not username or not password:
            st.sidebar.error("Both username and password are required.")
            return
        success, user_id, org_id = user_repo.authenticate_user(username, password)
        if success:
            set_session_state(user_id, org_id, username)
            st.rerun()
        else:
            st.sidebar.error("Invalid username or password.")


def register_tenant():
    # Custom CSS to make form border darker
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

    with st.form(key='register_form'):
        name = st.text_input("Name")
        description = st.text_input("Description")
        address = st.text_input("Address")
        email = st.text_input("Email")

        # Create a submit button inside the form
        register_button = st.form_submit_button(label='Register', type="primary")

    # Logic to handle form submission
    if register_button:
        # Validation
        if not name or not description or not address or not email:
            st.error("All fields are mandatory. Please fill in all the details.")
            return

        # Create tenant
        success, message, tenant_id = tenant_repo.register_tenant(name)
        if success:
            # Create root organization for the tenant
            success, org_id, join_code, org_message = org_repo.register_organization(
                tenant_id, name, description, is_root=True)
            if not success:
                st.error(org_message)
                return

            username = f"{tenant_id}admin"
            password = os.environ["ADMIN_PASSWORD"]

            # Create an admin user for the tenant and assign to root organization
            user_success, user_message = user_repo.register_user(
                name=f"{tenant_id}_admin",
                username=username,
                email=email,
                password=password,
                org_id=org_id,
                user_type="admin"
            )
            if user_success:
                st.success(f"{message}, {org_message}, and {user_message}")
            else:
                st.error(user_message)
        else:
            st.error(message)


def list_tenants():
    tenants = tenant_repo.get_all_tenants()

    # Create column headers
    # Create column headers
    header_html = """
        <div style='background-color:lightgrey;padding:5px;border-radius:3px;border:1px solid black;'>
            <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Name</p>
            </div>
            <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Id</p>
            </div>
            <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Root Org</p>
            </div>
            <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                <p style='color:black;margin:0;font-size:15px;font-weight:bold;'>Admin</p>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    for tenant in tenants:
        tenant_name = tenant['name']
        tenant_id = tenant['id']

        # Fetch and get root organization for this tenant
        root_org = org_repo.get_root_organization_by_tenant_id(tenant['id'])
        if root_org:
            root_org_name = root_org['name']
        else:
            root_org_name = "Not Found"

        # Fetch and get admin users for this tenant
        admin_users = user_repo.get_admin_users_by_org_id(root_org['id'])
        if admin_users:
            admin_username = admin_users[0]['username']
        else:
            admin_username = "Not Found"

        # Create a row for each tenant using HTML
        # Create a row for each tenant using HTML
        row_html = f"""
            <div style='padding:5px;border-radius:3px;border:1px solid black;'>
                <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{tenant_name}</p>
                </div>
                <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{tenant_id}</p>
                </div>
                <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{root_org_name}</p>
                </div>
                <div style='display:inline-block;width:24%;text-align:left;box-sizing: border-box;'>
                    <p style='color:black;margin:0;font-size:14px;'>{admin_username}</p>
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


def get_username():
    return st.session_state['username']


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
