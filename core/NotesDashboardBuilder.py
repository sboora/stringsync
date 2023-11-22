import streamlit as st

from datetime import datetime
from repositories.NotesRepository import NotesRepository


class NotesDashboardBuilder:
    def __init__(self, notes_repo: NotesRepository):
        self.notes_repo = notes_repo

    def notes_dashboard(self, user_id):
        # Note posting area
        with st.form("post_note", clear_on_submit=True):
            note_content = st.text_area("Jot down your note:", height=150)
            submit_note = st.form_submit_button("Post Note 📝")

            if submit_note and note_content:
                # Add the note using the current user's ID
                self.notes_repo.add_note(user_id, note_content)
                st.success("Your note has been posted 🌟")
                # Use st.experimental_rerun() to refresh the notes display
                st.experimental_rerun()

        # Display notes for the current user
        notes = self.notes_repo.get_notes(user_id)
        for note in notes:
            timestamp = note['timestamp'].strftime('%-I:%M %p | %b %d') \
                if isinstance(note['timestamp'], datetime) else note['timestamp']
            content_with_br = note['content'].replace("\n", "<br>")

            st.markdown(f"""
                <div style='background-color: #E8F4FA; border-radius: 10px; padding: 10px; margin-bottom: 5px;'>
                    <p style='color: #4F8BF9; font-weight: bold;'>{timestamp}</p>
                    <p>{content_with_br}</p>
                </div>
                """, unsafe_allow_html=True)
