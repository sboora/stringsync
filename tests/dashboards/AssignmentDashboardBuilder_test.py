import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from dashboards.AssignmentDashboard import AssignmentDashboard


@pytest.fixture
def mock_repos():
    return {
        "resource_repo": Mock(),
        "track_repo": Mock(),
        "assignment_repo": Mock(),
        "storage_repo": Mock(),
        "resource_dashboard_builder": Mock()
    }


@pytest.fixture
def dashboard_builder(mock_repos):
    return AssignmentDashboard(
        resource_repo=mock_repos["resource_repo"],
        track_repo=mock_repos["track_repo"],
        assignment_repo=mock_repos["assignment_repo"],
        storage_repo=mock_repos["storage_repo"],
        resource_dashboard_builder=mock_repos["resource_dashboard_builder"]
    )


def test_init(dashboard_builder, mock_repos):
    for key, repo in mock_repos.items():
        assert getattr(dashboard_builder, key) is repo


@patch("streamlit.info")
def test_assignments_dashboard_no_assignments(mock_info, dashboard_builder, mock_repos):
    mock_repos["assignment_repo"].get_assignments.return_value = []
    dashboard_builder.assignments_dashboard(user_id=123)
    mock_info.assert_called_once_with("No assignments available.")


def test_display_status_update(dashboard_builder, mock_repos):
    # Set the initial status returned by the repository
    mock_repos["assignment_repo"].get_detail_status.return_value = "In Progress"

    # Setup the selectbox mock to return a specific status when called
    with patch("streamlit.selectbox", return_value="Completed") as mock_selectbox, \
            patch("streamlit.button", return_value=True) as mock_button, \
            patch("streamlit.success") as mock_success:
        dashboard_builder._display_status_update(101, 123)

        # Check if the new status is updated in the repository
        mock_repos["assignment_repo"].update_assignment_status_by_detail.assert_called_with(123, 101, "Completed")
        mock_selectbox.assert_called()
        mock_button.assert_called()
        mock_success.assert_called()


