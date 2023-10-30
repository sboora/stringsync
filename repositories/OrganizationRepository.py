import random
import string


class OrganizationRepository:
    def __init__(self, connection):
        self.connection = connection
        self.create_organization_table()

    def create_organization_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `organizations` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    tenant_id INT,
                                    name VARCHAR(255),
                                    description TEXT,
                                    is_root BOOLEAN DEFAULT FALSE,
                                    join_code VARCHAR(10) UNIQUE,  
                                    FOREIGN KEY (tenant_id) REFERENCES `tenants`(id)
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def generate_unique_join_code(self):
        while True:
            join_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM organizations WHERE join_code = %s", (join_code,))
            count = cursor.fetchone()[0]
            if count == 0:
                return join_code

    def register_organization(self, tenant_id, org_name, description, is_root=False):
        cursor = self.connection.cursor()

        # Validate organization name
        if not org_name or len(org_name.strip()) == 0:
            return False, -1, -1, "Organization name cannot be empty."

        # Validate organization description
        if not description or len(description.strip()) == 0:
            return False, -1, -1, "Organization description cannot be empty."

        join_code = self.generate_unique_join_code()  # Generate a unique join code

        # Check if an organization with the same name already exists for this tenant
        check_name_query = """SELECT COUNT(*) FROM organizations WHERE name = %s AND tenant_id = %s;"""
        cursor.execute(check_name_query, (org_name, tenant_id))
        count_name = cursor.fetchone()[0]
        if count_name > 0:
            return False, -1, -1, f"An organization with the name {org_name} already exists for this tenant."

        # Check if a root organization already exists for this tenant
        if is_root:
            check_root_query = """SELECT COUNT(*) FROM organizations WHERE is_root = TRUE AND tenant_id = %s;"""
            cursor.execute(check_root_query, (tenant_id,))
            count_root = cursor.fetchone()[0]
            if count_root > 0:
                return False, -1, -1, "A root organization already exists for this tenant."

        add_org_query = """INSERT INTO organizations (tenant_id, name, description, is_root, join_code) 
                           VALUES (%s, %s, %s, %s, %s);"""
        cursor.execute(add_org_query, (tenant_id, org_name, description, is_root, join_code))
        self.connection.commit()
        org_id = cursor.lastrowid
        return True, org_id, join_code, f"School {org_name} registered successfully with join code {join_code}."

    def get_root_organization_by_tenant_id(self, tenant_id):
        cursor = self.connection.cursor()
        get_root_org_query = """SELECT id, name FROM organizations WHERE tenant_id = %s AND is_root = 1;"""
        cursor.execute(get_root_org_query, (tenant_id,))
        result = cursor.fetchone()
        if result:
            return {'id': result[0], 'name': result[1]}
        else:
            return None

    def get_organizations_by_tenant_id(self, tenant_id):
        cursor = self.connection.cursor()
        get_schools_query = """SELECT id, name, description, join_code FROM organizations WHERE tenant_id = %s AND 
        is_root = 0; """
        cursor.execute(get_schools_query, (tenant_id,))
        result = cursor.fetchall()
        organizations = [{'id': row[0], 'name': row[1], 'description': row[2], 'join_code': row[3]} for row in result]
        return organizations

    def get_organization_by_id(self, org_id):
        cursor = self.connection.cursor()
        get_org_query = """SELECT id, tenant_id, name, description, is_root, join_code 
                           FROM organizations WHERE id = %s;"""
        cursor.execute(get_org_query, (org_id,))
        result = cursor.fetchone()
        if result:
            organization = {
                'id': result[0],
                'tenant_id': result[1],
                'name': result[2],
                'description': result[3],
                'is_root': result[4],
                'join_code': result[5]
            }
            return True, organization
        else:
            return False, "Organization not found."

    def get_org_id_by_join_code(self, join_code):
        cursor = self.connection.cursor()
        get_org_query = """SELECT id FROM organizations WHERE join_code = %s;"""
        cursor.execute(get_org_query, (join_code,))
        result = cursor.fetchone()
        if result:
            return True, result[0]
        else:
            return False, "Organization not found."

