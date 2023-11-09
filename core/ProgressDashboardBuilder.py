import streamlit as st

from core.ListBuilder import ListBuilder
from repositories.RecordingRepository import RecordingRepository
from repositories.SettingsRepository import SettingsRepository
from repositories.TrackRepository import TrackRepository
from repositories.UserAchievementRepository import UserAchievementRepository
from repositories.UserPracticeLogRepository import UserPracticeLogRepository
import pandas as pd
import plotly.express as px


class ProgressDashboardBuilder:
    def __init__(self,
                 settings_repo: SettingsRepository,
                 recording_repo: RecordingRepository,
                 user_achievement_repo: UserAchievementRepository,
                 user_practice_log_repo: UserPracticeLogRepository,
                 track_repo: TrackRepository):
        self.settings_repo = settings_repo
        self.recording_repo = recording_repo
        self.user_achievement_repo = user_achievement_repo
        self.user_practice_log_repo = user_practice_log_repo
        self.track_repo = track_repo

    def progress_dashboard(self, user_id):
        tracks = self.get_tracks(user_id)
        # Display stats by track
        self.display_tracks(tracks)
        # Display the line graphs for duration, tracks, and average scores
        self.show_track_count_and_duration_trends(user_id)
        # Display practice logs line graph
        self.show_practice_trends(user_id)
        # bar graph for average score comparison
        self.show_score_graph_by_track(tracks)
        # bar graph for attempts comparison
        self.show_attempt_graph_by_track(tracks)

    def get_tracks(self, user_id):
        # Fetch all tracks and track statistics for this user
        tracks = self.track_repo.get_all_tracks()
        track_statistics = self.recording_repo.get_track_statistics_by_user(user_id)

        # Create a dictionary for quick lookup of statistics by track_id
        stats_dict = {stat['track_id']: stat for stat in track_statistics}

        # Build track details list using list comprehension
        track_details = [
            {
                'track': track,
                'num_recordings': stats_dict.get(track['id'], {}).get('num_recordings', 0),
                'avg_score': stats_dict.get(track['id'], {}).get('avg_score', 0),
                'min_score': stats_dict.get(track['id'], {}).get('min_score', 0),
                'max_score': stats_dict.get(track['id'], {}).get('max_score', 0)
            }
            for track in tracks
        ]

        return track_details

    @staticmethod
    def display_tracks(tracks):
        column_widths = [20, 20, 20, 20, 20]
        list_builder = ListBuilder(column_widths)

        list_builder.build_header(
            column_names=["Track", "Number of Recordings", "Average Score", "Min Score", "Max Score"])
        for track_detail in tracks:
            row_data = {
                "Track": track_detail['track']['name'],
                "Number of Recordings": track_detail['num_recordings'],
                "Average Score": track_detail['avg_score'],
                "Min Score": track_detail['min_score'],
                "Max Score": track_detail['max_score']
            }
            list_builder.build_row(row_data=row_data)

    def show_track_count_and_duration_trends(self, user_id):
        recording_duration_data = self.recording_repo.get_recording_duration_by_date(user_id)
        if not recording_duration_data:
            st.info("No data available.")
            return

        # Create a DataFrame from time_series_data
        df = pd.DataFrame(recording_duration_data)

        # Convert 'date' to datetime and ensure it's the index
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        # Determine the full range of dates from the available data
        full_date_range_start = df.index.min()
        full_date_range_end = df.index.max()

        # Determine the range of dates for plotting
        plot_start_date = min(full_date_range_start, (pd.Timestamp.today() - pd.DateOffset(weeks=4)).normalize())

        # Create a date range that includes every day from the earliest data or the last 4 weeks to the latest data
        all_days = pd.date_range(start=plot_start_date, end=full_date_range_end, freq='D')

        # Reindex the DataFrame to include all days, filling missing values with 0
        df = df.reindex(all_days).fillna(0).reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)

        # Plotting the line graph for Total Duration
        fig_duration = px.line(
            df,
            x='date',
            y='total_duration',
            title='Total Recording Duration Over Time',
            labels={'date': 'Date', 'total_duration': 'Total Duration (minutes)'}
        )
        fig_duration.update_yaxes(range=[0, max(60, df['total_duration'].max())])

        # Plotting the line graph for Total Tracks
        fig_tracks = px.line(
            df,
            x='date',
            y='total_tracks',
            title='Total Tracks Practiced Over Time',
            labels={'date': 'Date', 'total_tracks': 'Total Tracks'}
        )
        fig_tracks.update_yaxes(range=[0, df['total_tracks'].max()])

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_duration)
        with col2:
            st.plotly_chart(fig_tracks)

    def show_practice_trends(self, user_id):
        practice_data = self.user_practice_log_repo.fetch_daily_practice_minutes(user_id)

        if not practice_data:
            st.info("No data available for the line graph.")
            return

        df = pd.DataFrame(practice_data)
        df['date'] = pd.to_datetime(df['date'])

        # Determine the full range of dates in the dataset
        full_date_range_start = df['date'].min()
        full_date_range_end = df['date'].max()

        # Determine the start date for plotting which is the earlier of the two: the start date of your data or 4
        # weeks ago
        plot_start_date = min(full_date_range_start, (pd.Timestamp.today() - pd.DateOffset(weeks=4)).normalize())

        # Create a date range that includes every day from the start of your data or the last 4 weeks to today
        all_days = pd.date_range(start=plot_start_date, end=pd.Timestamp.today().normalize(), freq='D')

        # Reindex the DataFrame to include all days, filling missing values with 0 for 'total_minutes'
        df.set_index('date', inplace=True)
        df = df.reindex(all_days).fillna(0).reset_index()
        df.rename(columns={'index': 'date'}, inplace=True)
        df['total_minutes'] = df['total_minutes'].astype(int)

        # Plotting the line graph for total practice minutes
        fig_line = px.line(
            df,
            x='date',
            y='total_minutes',
            title='Daily Practice Minutes Over the Last 4 Weeks',
            labels={'date': 'Date', 'total_minutes': 'Total Minutes'}
        )

        # Set the y-axis to start from 0
        fig_line.update_yaxes(range=[0, max(60, df['total_minutes'].max())])

        # Adding the line graph to the Streamlit app
        st.plotly_chart(fig_line, use_column_width=True)

    @staticmethod
    def show_score_graph_by_track(tracks):
        # Flatten the track details for easier DataFrame creation
        flattened_tracks = [
            {
                'Track Name': track_detail['track']['name'],
                'Number of Recordings': track_detail['num_recordings'],
                'Average Score': track_detail['avg_score'],
                'Min Score': track_detail['min_score'],
                'Max Score': track_detail['max_score']
            }
            for track_detail in tracks
        ]

        # Create a DataFrame for the track statistics
        df_track_stats = pd.DataFrame(flattened_tracks)
        print(df_track_stats)
        df_track_stats.sort_values('Average Score', ascending=False, inplace=True)

        # Visualize with a bar chart
        fig = px.bar(
            df_track_stats,
            x='Track Name',  # Use the 'Track Name' for x-axis
            y='Average Score',
            color='Average Score',
            labels={'Track Name': 'Track', 'Average Score': 'Average Score'},
            title='Average Score per Track Comparison'
        )
        st.plotly_chart(fig)

    @staticmethod
    def show_attempt_graph_by_track(tracks):
        # Ensure the track details are flattened for DataFrame creation
        flattened_tracks = [
            {
                'Track Name': track_detail['track']['name'],
                'Number of Recordings': track_detail['num_recordings'],
                'Average Score': float(track_detail['avg_score']),  # Ensure numeric type for scores
                'Min Score': float(track_detail['min_score']),  # Convert to float if necessary
                'Max Score': float(track_detail['max_score'])
            }
            for track_detail in tracks
        ]

        # Create a DataFrame for the track statistics
        df_track_stats = pd.DataFrame(flattened_tracks)

        # Sort by 'Number of Recordings' for attempt comparison
        df_track_stats.sort_values('Number of Recordings', ascending=False, inplace=True)

        # Visualize with a bar chart comparing attempts
        fig = px.bar(
            df_track_stats,
            x='Track Name',
            y='Number of Recordings',
            color='Number of Recordings',
            labels={'Track Name': 'Track', 'Number of Recordings': 'Attempts'},
            title='Attempt Comparison per Track'
        )
        st.plotly_chart(fig)
