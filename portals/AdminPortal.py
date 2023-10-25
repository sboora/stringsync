from abc import ABC

import streamlit as st

from portals.BasePortal import BasePortal
from enums.UserType import UserType


class AdminPortal(BasePortal, ABC):
    def __init__(self):
        super().__init__()

    def get_title(self):
        return "MelodyMaster Admin Portal"

    def get_icon(self):
        return "🛠"

    def get_tab_dict(self):
        return {
            "🏫 Register a School": self.register_school,
            "🏢 List Schools": self.list_schools,
            "👩‍🏫 Register a Tutor": self.register_tutor,
            "👨‍🏫 List Tutors": self.list_tutors,
            "📝 Assign Tutor to School": self.assign_tutor,
            "📋 List Tutor Assignments": self.list_tutor_assignments
        }

    def show_introduction(self):
        st.write("""
            ### Welcome to the **Administrative Portal**!!

            **Your Comprehensive Dashboard for Educational Management**
            
            This portal is designed to provide a centralized platform for seamless administration of your educational organization. Here are the core functionalities you can leverage:
            - 🏫 **Register Schools**: Incorporate new educational institutions into your organizational network, complete with unique identifiers and profiles.
            - 👩‍🏫 **Register Tutors**: Facilitate the onboarding process for new tutors, allowing you to collect essential information and credentials.
            - 📝 **Assign Tutors to Schools**: Efficiently allocate tutors to specific schools, ensuring optimal resource distribution and academic excellence.

            Navigate through the tabs to perform these operations and more. Your effective management is just a few clicks away.
        """)

    def register_school(self):
        form_key = 'register_school'
        field_names = ['Name', 'Description']
        button_label = 'Register School'
        button, form_data = self.build_form(
            form_key, field_names, button_label)

        if button:
            success, org_id, join_code, message = self.org_repo.register_organization(
                self.get_tenant_id(), form_data['Name'], form_data['Description'], False)
            if success:
                # Create the folder structure in GCS after successful registration
                tenant_id = self.get_tenant_id()

                # Create the required folders
                self.storage_repo.create_folder(f'{tenant_id}/{org_id}/tracks')
                self.storage_repo.create_folder(f'{tenant_id}/{org_id}/recordings')
                self.storage_repo.create_folder(f'{tenant_id}/logo')
                self.storage_repo.create_folder(f'{tenant_id}/badges')

                st.success(message)
            else:
                st.error(message)

    def register_tutor(self):
        form_key = 'register_tutor'
        field_names = ['Name', 'Username', 'Email', 'Password']
        button_label = 'Register Tutor'
        button, form_data = self.build_form(form_key, field_names, button_label)

        if button:
            success, message = self.user_repo.register_user(
                name=form_data['Name'],
                username=form_data['Username'],
                email=form_data['Email'],
                password=form_data['Password'],
                org_id=self.get_org_id(),
                user_type=UserType.TEACHER.value
            )
            if success:
                st.success(message)
            else:
                st.error(message)

    def assign_tutor(self):
        school_options = {school['name']: school['id'] for school in
                          self.org_repo.get_organizations_by_tenant_id(self.get_tenant_id())}
        tutor_options = {tutor['username']: tutor['id'] for tutor in
                         self.portal_repo.get_users_by_tenant_id_and_type(self.get_tenant_id(), UserType.TEACHER.value)}

        assign_tutor_button, form_data = self.build_form_with_select_boxes(
            'assign_tutor', {"School": school_options, "Tutor": tutor_options}, 'Assign Tutor')

        if assign_tutor_button:
            selected_school = form_data["School"]
            selected_tutor = form_data["Tutor"]

            # Validate selections
            if selected_school == '--Select a School--' or selected_tutor == '--Select a Tutor--':
                st.error("Please select both a tutor and a school.")
                return

            success, message = self.user_repo.assign_user_to_org(tutor_options[selected_tutor],
                                                                 school_options[selected_school])

            if success:
                st.success(f"Tutor {selected_tutor} has been assigned to {selected_school}")
            else:
                st.error(f"Failed to assign tutor: {message}")

    def list_schools(self):
        # Fetch and display the list of schools linked to this admin (tenant)
        schools = self.org_repo.get_organizations_by_tenant_id(self.get_tenant_id())

        # Create the header for the table
        self.build_header(["Organization Name", "Organization Description", "Join Code"])

        # Loop through each school and create a table row
        for school in schools:
            self.build_row({
                "Organization Name": school['name'],
                "Organization Description": school['description'],
                "Join Code": school['join_code']
            })

    def list_tutors(self):
        # Fetch and display the list of tutors linked to this org group
        tutors = self.portal_repo.get_users_by_tenant_id_and_type(self.get_tenant_id(), UserType.TEACHER.value)

        # Create the header for the table
        self.build_header(["Name", "Username", "Email"])

        # Loop through each tutor and create a table row
        for tutor in tutors:
            self.build_row({
                "Name": tutor['name'],
                "Username": tutor['username'],
                "Email": tutor['email']
            })

    def list_tutor_assignments(self):
        # Fetch and display the list of tutor assignments
        tutor_assignments = self.portal_repo.list_tutor_assignments(self.get_tenant_id())

        # Create the header for the table
        self.build_header(["Tutor Name", "Tutor Username", "School Name", "School Description"])

        # Loop through each tutor assignment and create a table row
        for assignment in tutor_assignments:
            self.build_row({
                "Tutor Name": assignment['tutor_name'],
                "Tutor Username": assignment['tutor_username'],
                "School Name": assignment['school_name'],
                "School Description": assignment['school_description']
            })

