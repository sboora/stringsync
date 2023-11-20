from abc import ABC

from core.ListBuilder import ListBuilder
from enums.Features import Features
from enums.Settings import Portal
from enums.UserType import UserType
from portals.BasePortal import BasePortal
import streamlit as st
import streamlit_toggle as tog
import os


class TenantPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()

    def get_portal(self):
        return Portal.TENANT

    def get_title(self):
        return f"{self.get_app_name()} Tenant Portal"

    def get_icon(self):
        return "🏠"

    def show_introduction(self):
        st.write("""
            ### **Tenant Management Portal**

            **Your Centralized Platform for Multi-Organization Educational Oversight**

            This portal is  designed to offer you a streamlined experience in managing multiple educational organizations. Here are the core functionalities you can leverage:
            - 🏢 **Register New Tenants**: Seamlessly integrate new educational organizations into your existing network, complete with all essential details and administrative credentials.
            - 📋 **List All Tenants**: Gain a holistic view of all the educational organizations under your purview, including their administrative contacts and root organizations.

            Please log in to unlock the full range of management capabilities tailored to meet your organizational needs.
        """)

    def get_tab_dict(self):
        return {
            "🏢 Register a Tenant": self.register_tenant,
            "📋 List Tenants": self.list_tenants,
            "⚙️ Feature Toggles": self.feature_toggles  # Add this line
        }

    def register_tenant(self):
        # Build form
        form_key = 'register_form'
        field_names = ['Name', 'Description', 'Address', 'Email']
        button_label = 'Register'
        register_button, form_data = self.build_form(form_key, field_names, button_label)

        # Process form data
        name = form_data['Name']
        description = form_data['Description']
        address = form_data['Address']
        email = form_data['Email']
        if register_button:
            if not name or not description or not address or not email:
                st.error("All fields are mandatory. Please fill in all the details.")
                return

            success, message, tenant_id = self.tenant_repo.register_tenant(name)
            if success:
                success, org_id, join_code, org_message = self.org_repo.register_organization(
                    tenant_id, name, description, is_root=True)
                if not success:
                    st.error(org_message)
                    return

                username = f"{name.replace(' ', '').lower()}-admin"
                password = os.environ["ADMIN_PASSWORD"]

                user_success, user_message, user_id = self.user_repo.register_user(
                    name=f"{tenant_id}_admin",
                    username=username,
                    email=email,
                    password=password,
                    org_id=org_id,
                    user_type=UserType.ADMIN.value
                )
                if user_success:
                    st.success(f"{message}, {org_message}, and {user_message}")
                else:
                    st.error(user_message)
            else:
                st.error(message)

    def list_tenants(self):
        tenants = self.tenant_repo.get_all_tenants()
        column_names = ["Name", "Id", "Root Organization", "Admin"]
        list_builder = ListBuilder(column_widths = [25, 25, 25, 25])
        list_builder.build_header(column_names=column_names)

        for tenant in tenants:
            tenant_name = tenant.get('name', 'Not Found')
            tenant_id = tenant.get('id', 'Not Found')

            root_org = self.org_repo.get_root_organization_by_tenant_id(tenant['id'])
            root_org_name = root_org.get('name', 'Not Found') if root_org else 'Not Found'

            admin_users = self.user_repo.get_admin_users_by_org_id(root_org.get('id', None))
            admin_username = admin_users[0].get('username', 'Not Found') if admin_users else 'Not Found'

            row_data = {
                "Name": tenant_name,
                "Id": tenant_id,
                "Root Organization": root_org_name,
                "Admin": admin_username
            }
            list_builder.build_row(row_data=row_data)

    def feature_toggles(self):
        features = self.feature_repo.get_all_features()

        if features:
            for feature in features:
                feature_enum_name = feature.get('feature_name', 'Unknown')
                is_enabled = feature.get('is_enabled', False)

                # Map the enum name to its value
                feature_display_value = Features[
                    feature_enum_name].value if feature_enum_name != 'Unknown' else 'Unknown'

                # Create columns with padding
                col1, col2, padding = st.columns([1, 1, 4])

                # Display feature value
                with col1:
                    print(feature_display_value)
                    st.write(feature_display_value)

                # Display on/off switch using st_toggles
                with col2:
                    current_status = st.toggle(
                        "", value=is_enabled, key=f"toggle_{feature_display_value}")

                # If toggle button is clicked
                if current_status != is_enabled:
                    self.feature_repo.toggle_feature(feature_enum_name)
        else:
            st.info("No features available.")