import time

from PortalTestBase import PortalTestBase
from config import ROOT_USERNAME, ROOT_PASSWORD, TENANT_NAME, \
    TENANT_DESCRIPTION, TENANT_EMAIL, TENANT_ADDRESS


class TenantPortalTest(PortalTestBase):
    @staticmethod
    def get_url():
        return "http://localhost:8501/"

    def get_username(self):
        return ROOT_USERNAME

    def get_password(self):
        return ROOT_PASSWORD

    def verify_login_successful(self):
        self.assert_page_title("Guru Shishya Tenant Portal")
        self.assert_text_present("Welcome to")
        self.assert_text_present("Tenant Management Portal")
        self.assert_text_present("Your Centralized Platform for Multi-Organization Educational Oversight")
        self.assert_text_present("Register a Tenant")
        self.assert_text_present("List Tenants")
        self.assert_text_present("Feature Toggles")

    def verify_registration_successful(self):
        self.assert_text_present(f"Tenant {TENANT_NAME} registered successfully")

    def tenant_registration(self):
        self.delay()
        self.find_input_and_type("input[aria-label='Name']", TENANT_NAME)
        self.delay()
        self.find_input_and_type("input[aria-label='Description']", TENANT_DESCRIPTION)
        self.delay()
        self.find_input_and_type("input[aria-label='Address']", TENANT_ADDRESS)
        self.delay()
        self.find_input_and_type("input[aria-label='Email']", TENANT_EMAIL)
        self.delay()
        self.click_button('[data-testid="baseButton-primaryFormSubmit"]')
        time.sleep(3)
        self.verify_registration_successful()

    def get_test_flow_methods(self):
        return [
            self.tenant_registration
        ]

    def test_flow(self):
        self.flow()

