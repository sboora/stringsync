import pytest

from enums.Badges import UserBadges, TrackBadges


class TestUserBadges:

    @pytest.mark.parametrize("badge_member, expected_value", [
        (UserBadges.FIRST_NOTE, "First Note"),
        (UserBadges.RISING_STAR, "Rising Star"),
        (UserBadges.ROCKSTAR, "Rockstar"),
        (UserBadges.TWO_DAY_STREAK, "2 Day Streak"),
        (UserBadges.THREE_DAY_STREAK, "3 Day Streak"),
        (UserBadges.FIVE_DAY_STREAK, "5 Day Streak"),
        (UserBadges.SEVEN_DAY_STREAK, "7 Day Streak"),
        (UserBadges.TEN_DAY_STREAK, "10 Day Streak"),
        (UserBadges.WEEKLY_MAX_PRACTICE_MINUTES, "Practice Champ"),
        (UserBadges.WEEKLY_MAX_RECORDING_MINUTES, "Sound Sorcerer"),
        (UserBadges.WEEKLY_MAX_DAILY_PRACTICE_MINUTES, "Practice Prodigy"),
        (UserBadges.WEEKLY_MAX_RECORDINGS, "Recording Kingpin"),
        (UserBadges.WEEKLY_MAX_SCORER, "Melody Master"),
        (UserBadges.WEEKLY_MAX_TRACK_RECORDER, "Track Titan"),
        (UserBadges.WEEKLY_MAX_BADGE_EARNER, "Badge Baron"),
        (UserBadges.MONTHLY_MAX_PRACTICE_MINUTES, "Monthly Star"),
        (UserBadges.MONTHLY_MAX_RECORDING_MINUTES, "Mic Champ")
    ])
    def test_value_property(self, badge_member, expected_value):
        assert badge_member.value == expected_value

    @pytest.mark.parametrize("value, expected_member", [
        ("First Note", UserBadges.FIRST_NOTE),
        ("Rising Star", UserBadges.RISING_STAR),
        ("Rockstar", UserBadges.ROCKSTAR),
        ("2 Day Streak", UserBadges.TWO_DAY_STREAK),
        ("3 Day Streak", UserBadges.THREE_DAY_STREAK),
        ("5 Day Streak", UserBadges.FIVE_DAY_STREAK),
        ("7 Day Streak", UserBadges.SEVEN_DAY_STREAK),
        ("10 Day Streak", UserBadges.TEN_DAY_STREAK),
        ("Practice Champ", UserBadges.WEEKLY_MAX_PRACTICE_MINUTES),
        ("Sound Sorcerer", UserBadges.WEEKLY_MAX_RECORDING_MINUTES),
        ("Practice Prodigy", UserBadges.WEEKLY_MAX_DAILY_PRACTICE_MINUTES),
        ("Recording Kingpin", UserBadges.WEEKLY_MAX_RECORDINGS),
        ("Melody Master", UserBadges.WEEKLY_MAX_SCORER),
        ("Track Titan", UserBadges.WEEKLY_MAX_TRACK_RECORDER),
        ("Badge Baron", UserBadges.WEEKLY_MAX_BADGE_EARNER),
        ("Monthly Star", UserBadges.MONTHLY_MAX_PRACTICE_MINUTES),
        ("Mic Champ", UserBadges.MONTHLY_MAX_RECORDING_MINUTES)
    ])
    def test_from_value(self, value, expected_member):
        assert UserBadges.from_value(value) is expected_member

    @pytest.mark.parametrize("badge_member, format_value, expected_output", [
        (UserBadges.FIRST_NOTE, 100, "You made your first recording!"),
        (UserBadges.RISING_STAR, 200, "You've achieved the Rising Star badge by showcasing your talent!"),
        (UserBadges.ROCKSTAR, 300, "You've reached Rockstar status with your impressive skills!"),
        (UserBadges.TWO_DAY_STREAK, 2, "You maintained a 2-day practice streak!"),
        (UserBadges.THREE_DAY_STREAK, 3, "You've kept up a 3-day practice streak!"),
        (UserBadges.FIVE_DAY_STREAK, 5, "You've impressively maintained a 5-day practice streak!"),
        (UserBadges.SEVEN_DAY_STREAK, 7, "You've completed a commendable 7-day practice streak!"),
        (UserBadges.TEN_DAY_STREAK, 10, "You've achieved an incredible 10-day practice streak!"),
        (UserBadges.WEEKLY_MAX_PRACTICE_MINUTES, 60, "You practiced for **60 minutes** this week, topping the charts!"),
        (UserBadges.WEEKLY_MAX_RECORDING_MINUTES, 10,
         "You've recorded for **10 minutes** this week as the **Sound Sorcerer**!"),
        (UserBadges.WEEKLY_MAX_DAILY_PRACTICE_MINUTES, 45,
         "You're a **Practice Prodigy** with **45 minutes** of practice on a single day!"),
        (UserBadges.WEEKLY_MAX_RECORDINGS, 5,
         "You made **5 recordings** this week, earning you the **Recording Kingpin** badge!"),
        (UserBadges.WEEKLY_MAX_SCORER, 40,
         "You've earned the **Melody Master** badge with a high score of **40 points**!"),
        (UserBadges.WEEKLY_MAX_TRACK_RECORDER, 3,
         "Recording on **3** different **tracks** makes you a **Track Titan**!"),
        (UserBadges.WEEKLY_MAX_BADGE_EARNER, 3,
         "You've earned **3** different **badges**, making you a true **Badge Baron**!"),
        (UserBadges.MONTHLY_MAX_PRACTICE_MINUTES, 250,
         "Your **250 minutes** of practice this month have made you a **Monthly Star**!"),
        (UserBadges.MONTHLY_MAX_RECORDING_MINUTES, 30,
         "With **30 minutes** of recordings this month, you're the undisputed **Mic Champ**!")
    ])
    def test_format_stats_info(self, badge_member, format_value, expected_output):
        assert badge_member.format_stats_info(format_value) == expected_output


class TestTrackBadges:

    @pytest.mark.parametrize("badge_member, expected_value", [
        (TrackBadges.FAST_LEARNER, "Fast Learner"),
        (TrackBadges.SONG_BIRD, "Song Bird"),
        (TrackBadges.MAESTRO, "Maestro"),
        (TrackBadges.PERFECT_PITCH, "Perfect Pitch"),
        (TrackBadges.PERFECT_BEAT, "Perfect Beat"),
        (TrackBadges.MUSIC_WIZARD, "Music Wizard"),
        (TrackBadges.VIRTUOSO, "Virtuoso"),
        (TrackBadges.PRACTICE_MAKES_PERFECT, "Practice Makes Perfect")
    ])
    def test_value_property(self, badge_member, expected_value):
        assert badge_member.value == expected_value

    @pytest.mark.parametrize("value, expected_member", [
        ("Fast Learner", TrackBadges.FAST_LEARNER),
        ("Song Bird", TrackBadges.SONG_BIRD),
        ("Maestro", TrackBadges.MAESTRO),
        ("Perfect Pitch", TrackBadges.PERFECT_PITCH),
        ("Perfect Beat", TrackBadges.PERFECT_BEAT),
        ("Music Wizard", TrackBadges.MUSIC_WIZARD),
        ("Virtuoso", TrackBadges.VIRTUOSO),
        ("Practice Makes Perfect", TrackBadges.PRACTICE_MAKES_PERFECT)
    ])
    def test_from_value(self, value, expected_member):
        assert TrackBadges.from_value(value) is expected_member

    @pytest.mark.parametrize("badge_member, format_value, expected_output", [
        (TrackBadges.FAST_LEARNER, 100, "You mastered a new track in record time!"),
        (TrackBadges.SONG_BIRD, 200, "Your pitch-perfect performance earned you the Song Bird badge!"),
        (TrackBadges.MAESTRO, 300, "Your exceptional performance skills have earned you the Maestro badge!"),
        (TrackBadges.PERFECT_PITCH, 400, "Your pitch-perfect recordings have earned you the Perfect Pitch badge!"),
        (TrackBadges.PERFECT_BEAT, 500, "Your impeccable timing has earned you the Perfect Beat badge!"),
        (TrackBadges.MUSIC_WIZARD, 600, "Your creative and skillful performances make you a Music Wizard!"),
        (TrackBadges.VIRTUOSO, 700, "Your artistry and skill have earned you the Virtuoso badge!"),
        (TrackBadges.PRACTICE_MAKES_PERFECT, 800,
         "Your commitment to practice has rightfully earned you the Practice Makes Perfect badge!")
    ])
    def test_format_stats_info(self, badge_member, format_value, expected_output):
        assert badge_member.format_stats_info(format_value) == expected_output
