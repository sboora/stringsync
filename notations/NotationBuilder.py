import os
import re
import streamlit as st


class NotationBuilder:
    def __init__(self, track, notation_path):
        self.track = track
        self.notation_path = notation_path
        self.notation_content = None

    def display_notation(self):
        unique_notes = []
        if os.path.exists(self.notation_path):
            with open(self.notation_path, "r") as f:
                self.notation_content = f.read()
            st.markdown(f"**Notation:**")
            self.display_notes_with_subscript()

            # Extract and filter notes
            notes = re.split(r'[,\s_]+', self.notation_content.replace('b', '').strip())
            valid_notes = {'S', 'R1', 'R2', 'R3', 'G1', 'G2', 'G3', 'M1', 'M2', 'P', 'D1', 'D2', 'D3', 'N1', 'N2', 'N3'}
            unique_notes = list(set(notes).intersection(valid_notes))
        else:
            st.warning(f"No notation file found for track: {self.track}")
        return unique_notes

    def display_notes_with_subscript(self):
        formatted_notes = ""
        buffer = ""
        bold_flag = False
        section_flag = False

        for char in self.notation_content:
            if char.isalpha() and char != 'b':
                buffer += char
            elif char == ':':
                buffer += char
            elif char.isdigit():
                buffer += char
            elif char == 'b':
                bold_flag = True
            else:
                if section_flag:
                    formatted_notes += f"<b>{buffer}</b>"
                    section_flag = False
                else:
                    if len(buffer) > 1:
                        note = f"{buffer[0]}<sub>{buffer[1:]}</sub>"
                    else:
                        note = buffer

                    if bold_flag:
                        formatted_notes += f"<b>{note}</b>"
                    else:
                        formatted_notes += note

                if char in ['_', ',', '\n', ' ']:
                    formatted_notes += char if char != '\n' else "<br>"

                buffer = ""
                bold_flag = False

            if buffer == "Section:":
                section_flag = True
                buffer = ""

        if buffer:
            if len(buffer) > 1:
                note = f"{buffer[0]}<sub>{buffer[1:]}</sub>"
            else:
                note = buffer

            if bold_flag:
                formatted_notes += f"<b>{note}</b>"
            else:
                formatted_notes += note

        st.markdown(f"<div style='font-size: 16px; font-weight: normal;'>{formatted_notes}</div>",
                    unsafe_allow_html=True)
