import streamlit as st

from repositories.ResourceRepository import ResourceRepository
from repositories.StorageRepository import StorageRepository


class ResourceDashboardBuilder:
    def __init__(self, resource_repo: ResourceRepository, storage_repo: StorageRepository):
        self.resource_repo = resource_repo
        self.storage_repo = storage_repo

    def resources_dashboard(self):
        resources = self.resource_repo.list_resources()

        # Organize resources by type
        resources_by_type = {
            'PDF': [],
            'Audio': [],
            'Video': [],
            'Link': []
        }

        for resource in resources:
            resources_by_type[resource['type']].append(resource)

        # Check if there are any resources
        if resources:
            # Display resources by type in separate expanders
            for resource_type, resources_list in resources_by_type.items():
                if resources_list:  # Check if there are any resources of this type
                    with st.expander(f"{resource_type}s"):
                        # Use columns to display each resource in a row
                        for resource in resources_list:
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col1:
                                st.markdown(f"**{resource['title']}**")
                            with col2:
                                st.write(resource['description'])
                            with col3:
                                # Display the appropriate content based on the resource type
                                if resource['type'] == 'PDF':
                                    data = self.storage_repo.download_blob_by_url(resource['file_url'])
                                    st.download_button(
                                        label="Download",
                                        data=data,
                                        file_name=f"{resource['title']}.pdf",
                                        mime='application/pdf',
                                        key=f"download_{resource['id']}",
                                        type='primary'
                                    )
                                elif resource['type'] == 'Link':
                                    st.markdown(f"[Link]({resource['link']})", unsafe_allow_html=True)
                                elif resource['type'] == 'Video':
                                    st.video(resource['file_url'])
                                elif resource['type'] == 'Audio':
                                    st.audio(resource['file_url'])
        else:
            st.info("No resources found.")
