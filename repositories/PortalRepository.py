class PortalRepository:
    def __init__(self, connection):
        self.connection = connection

    def list_tutor_assignments(self, tenant_id):
        cursor = self.connection.cursor()
        query = """
        SELECT u.id AS tutor_id, u.name AS tutor_name, u.username AS tutor_username, 
               o.id AS school_id, o.name AS school_name, o.description AS school_description
        FROM users u
        JOIN organizations o ON u.org_id = o.id
        WHERE u.user_type = 'teacher' AND o.is_root = 0 AND o.tenant_id = %s;
        """

        cursor.execute(query, (tenant_id,))
        results = cursor.fetchall()

        tutor_assignments = [
            {
                'tutor_id': row[0],
                'tutor_name': row[1],
                'tutor_username': row[2],
                'school_id': row[3],
                'school_name': row[4],
                'school_description': row[5]
            }
            for row in results
        ]

        return tutor_assignments

    def get_users_by_tenant_id_and_type(self, tenant_id, user_type):
        cursor = self.connection.cursor()
        query = """
        SELECT u.id, u.name, u.username, u.email
        FROM users u
        JOIN organizations o ON u.org_id = o.id
        WHERE o.tenant_id = %s AND u.user_type = %s;
        """

        cursor.execute(query, (tenant_id, user_type))
        results = cursor.fetchall()

        users = [
            {
                'id': row[0],
                'name': row[1],
                'username': row[2],
                'email': row[3]
            }
            for row in results
        ]

        return users

    def list_tracks(self):
        cursor = self.connection.cursor()
        query = """
        SELECT t.name, r.name AS ragam_name, t.level, t.description, t.track_path
        FROM tracks t
        JOIN ragas r ON t.ragam_id = r.id;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        tracks_details = [
            {
                "track_name": row[0],
                "ragam": row[1],
                "level": row[2],
                "description": row[3],
                "track_path": row[4]
            }
            for row in results
        ]

        return tracks_details

    def get_submissions_by_user_id(self, user_id, limit=20):
        cursor = self.connection.cursor()
        query = """
        SELECT r.timestamp, t.name AS track_name, r.blob_url AS recording_audio_url, 
               t.track_path AS track_audio_url, r.analysis AS system_remarks, 
               r.remarks AS teacher_remarks, r.score, t.id as track_id, r.id
        FROM recordings r
        JOIN tracks t ON r.track_id = t.id
        WHERE r.user_id = %s
        ORDER BY r.timestamp DESC
        LIMIT %s
        """
        cursor.execute(query, (user_id, limit))
        results = cursor.fetchall()

        submissions = [
            {
                "timestamp": row[0],
                "track_name": row[1],
                "recording_audio_url": row[2],
                "track_audio_url": row[3],
                "system_remarks": row[4],
                "teacher_remarks": row[5],
                "score": row[6],
                "track_id": row[7],
                "recording_id": row[8]
            }
            for row in results
        ]

        return submissions

    def get_badges_grouped_by_tracks(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT recordings.track_id, GROUP_CONCAT(user_achievements.badge) as badges 
            FROM user_achievements 
            JOIN recordings ON user_achievements.recording_id = recordings.id
            WHERE user_achievements.user_id = %s 
            GROUP BY recordings.track_id
        """, (user_id,))
        result = cursor.fetchall()
        return [{'track_id': row['track_id'], 'badges': row['badges'].split(',')} for row in result]







