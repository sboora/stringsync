import pandas as pd
import plotly.figure_factory as ff
import streamlit as st

from repositories.UserPracticeLogRepository import UserPracticeLogRepository


class PracticeDashboardBuilder:
    def __init__(self,
                 user_practice_log_repo: UserPracticeLogRepository):
        self.user_practice_log_repo = user_practice_log_repo

    def practice_dashboard(self, user_id):
        practice_data = self.user_practice_log_repo.fetch_daily_practice_minutes(user_id)

        # Check if practice_data is empty
        if not practice_data:
            return

        df = pd.DataFrame(practice_data)
        df['date'] = pd.to_datetime(df['date'])

        # Determine the start date for the last 4 weeks
        last_4_weeks_start_date = (pd.Timestamp.today() - pd.DateOffset(weeks=4)).normalize()

        # Filter merged_df for only the last 4 weeks
        merged_df = df[df['date'] >= last_4_weeks_start_date].copy()

        # Ensure all days of the week are represented
        all_days = pd.date_range(start=last_4_weeks_start_date, end=pd.Timestamp.today().normalize(), freq='D')

        # Reindex the DataFrame to include all days
        merged_df = merged_df.set_index('date').reindex(all_days).fillna({'total_minutes': 0}).reset_index()

        # The reset_index call might have changed the 'date' column name to 'index', so rename it back to 'date'
        merged_df.rename(columns={'index': 'date'}, inplace=True)

        # Now you can safely convert the minutes back to integers without affecting other data
        merged_df['total_minutes'] = merged_df['total_minutes'].astype(int)

        # Create a pivot table to get the matrix format
        pivot_table = merged_df.pivot_table(values='total_minutes', index=merged_df['date'].dt.dayofweek,
                                            columns=merged_df['date'].dt.isocalendar().week, fill_value=0)

        # Use the Plotly Figure Factory to create the annotated heatmap
        z = pivot_table.values
        x = ['Week ' + str(int(week)) for week in pivot_table.columns]
        y = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

        fig = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=z, colorscale='Blues')
        fig.update_layout(
            title='',
            xaxis_title='Week',
            yaxis_title='Day'
        )

        # Adjust the shape coordinates to encapsulate the entire chart including labels
        fig.update_layout(
            shapes=[
                dict(
                    type="rect",
                    xref="paper",
                    yref="paper",
                    x0=-0.07,  # left side
                    y0=-0.0,  # bottom
                    x1=1.0,  # right side
                    y1=1.12,  # top
                    line=dict(
                        color="#EAEDED",
                        width=2,
                    ),
                )
            ]
        )
        st.plotly_chart(fig, use_column_width=True, config={'displayModeBar': False, 'displaylogo': False})
