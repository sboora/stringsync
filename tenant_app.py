import streamlit as st
import secrets
import string

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
    # Streamlit app
    st.set_page_config(layout="centered")
    st.title("Tenant Registration")

    # Welcome message and introduction
    st.markdown("""
        ## Welcome!! 🎉

        This page allows you to register a new tenant for the **StringSync** platform. 
        Each tenant can represent an organization, school, or any other entity.

        ### How it Works:
        1. **Fill in the Details**: Provide the name, description, address, and email for the tenant.
        2. **Register**: Click the 'Register' button to complete the registration.
        3. **Admin Account**: Upon successful registration, an admin account will be automatically created for the tenant.

        Ready to get started? Just fill in the form below!
    """)

    # Form
    name = st.text_input("Name")
    description = st.text_input("Description")
    address = st.text_input("Address")
    email = st.text_input("Email")

    if st.button("Register", type="primary"):
        # Validation
        if not name or not description or not address or not email:
            st.error("All fields are mandatory. Please fill in all the details.")
            return

        # Create tenant
        success, message, tenant_id = tenant_repo.register_tenant(name)
        if success:
            # Create root organization for the tenant
            success, org_id, join_code, org_message = org_repo.register_organization(tenant_id, name, description,
                                                                                     is_root=True)
            if not success:
                st.error(org_message)
                return

            password = 'Pass1234!'

            # Create an admin user for the tenant and assign to root organization
            user_success, user_message = user_repo.register_user(
                name=f"{tenant_id}_admin",
                username=f"{tenant_id}admin",
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

    display_tenants_and_admins()


def display_tenants_and_admins():
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


if __name__ == "__main__":
    main()
