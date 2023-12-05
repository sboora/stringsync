class TenantRepository:
    def __init__(self, connection):
        self.connection = connection
        #self.create_tenants_table()

    def create_tenants_table(self):
        cursor = self.connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS `tenants` (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(255) UNIQUE,
                                    is_enabled BOOLEAN DEFAULT TRUE
                                ); """
        cursor.execute(create_table_query)
        self.connection.commit()

    def register_tenant(self, name):
        cursor = self.connection.cursor()

        # Check if the tenant already exists
        check_tenant_query = """SELECT COUNT(*) FROM tenants WHERE name = %s;"""
        cursor.execute(check_tenant_query, (name,))
        count = cursor.fetchone()[0]

        if count > 0:
            return False, f"A tenant with the name {name} already exists.", None

        # If the tenant doesn't exist, proceed to create it
        add_tenant_query = """INSERT INTO tenants (name) VALUES (%s);"""
        cursor.execute(add_tenant_query, (name,))
        self.connection.commit()
        last_inserted_id = cursor.lastrowid

        return True, f"Tenant {name} registered successfully with ID {last_inserted_id}.", last_inserted_id

    def get_all_tenants(self):
        cursor = self.connection.cursor()
        get_tenants_query = """SELECT id, name FROM tenants;"""
        cursor.execute(get_tenants_query)
        result = cursor.fetchall()
        tenants = [{'id': row[0], 'name': row[1]} for row in result]
        return tenants

    def get_tenant_by_name(self, name):
        cursor = self.connection.cursor()
        get_tenant_query = """SELECT id, name FROM tenants WHERE name = %s;"""
        cursor.execute(get_tenant_query, (name,))
        result = cursor.fetchone()
        if result:
            tenant = {'id': result[0], 'name': result[1]}
            return tenant
        else:
            return None
