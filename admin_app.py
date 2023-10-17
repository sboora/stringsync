import streamlit as st

import env
from UserRepository import UserRepository
from TenantRepository import TenantRepository
from OrganizationRepository import OrganizationRepository


def main():
    env.set_env()
    # Streamlit app
    st.title("Admin Portal")

    # Initialize repositories
    user_repo = UserRepository()
    tenant_repo = TenantRepository()
    org_repo = OrganizationRepository()

    # Admin login
    st.subheader("Admin Login")
    if st.button("Login"):
        admin_username = st.text_input("Username")
        admin_password = st.text_input("Password", type="password")
        success, admin_id, org_id = user_repo.authenticate_user(admin_username, admin_password)
        if success:
            st.success("Logged in successfully.")

            # Tenant Id
            success, organization = org_repo.get_organization_by_id(org_id)

            if success:
                tenant_id = organization['tenant_id']
            else:
                print("Organization not found.")
                return

            # School registration
            st.subheader("Register a School")
            name = st.text_input("Name")
            description = st.text_input("Description")

            if st.button("Register School"):
                success, org_id, join_code, message = org_repo.register_organization(tenant_id, name, description,
                                                                                     False)
                if success:
                    st.success(message)
                else:
                    st.error(message)

            # List of schools
            st.subheader("List of Schools")
            # Fetch and display the list of schools linked to this admin (tenant)
            schools = org_repo.get_organizations_by_tenant_id(tenant_id)
            for school in schools:
                st.write(school)
        else:
            st.error("Invalid username or password.")


if __name__ == "__main__":
    main()
