# String Sync: Enhance Your Musical Learning Experience

## Overview

String Sync is an innovative platform designed to help music teachers and students enhance their learning experience. Leveraging advanced audio analysis, String Sync allows you to compare your musical performance with a reference recording, providing you with a quantifiable score based on the similarity.

## How Does it Work?

### Steps to Follow

1. **Listen to the track**: Each track comes with a reference audio file. Listen to it carefully to understand what you need to achieve.
2. **Upload Your Recording**: Record your own performance and upload it here.
3. **Get Your Score**: Our advanced algorithm will compare your performance with the reference audio and give you a score based on how closely they match.

## Why Use String Sync?

- **Objective Feedback**: Get unbiased, data-driven feedback on your performance.
- **Progress Tracking**: Keep track of your scores to monitor your improvement over time.
- **Flexible**: Suitable for any instrument and skill level.

## Features

- Store tracks with metadata like `name`, `track_path`, `track_ref_path`, `notation_path`, `level`, `ragam`, and `type`.
- Support for tags to categorize tracks.
- Search functionality based on `ragam`, `level`, and `tags`.
- Support for `offset`, which represents the distance between the track and track_ref.

## Table Schema

### Tracks Table

| Field          | Type    | Description                          |
| -------------- | ------- | ------------------------------------ |
| id             | INTEGER | Auto-incremented primary key         |
| name           | TEXT    | Name of the track                    |
| track_path     | TEXT    | Path to the track file               |
| track_ref_path | TEXT    | Path to the reference track file     |
| notation_path  | TEXT    | Path to the notation file            |
| level          | INTEGER | Level of difficulty                  |
| ragam          | TEXT    | Musical scale or mode                |
| type           | TEXT    | Type of track (e.g., Lesson, Song)   |
| offset         | INTEGER | Offset between track and track_ref   |

### Tags Table

| Field     | Type    | Description                  |
| --------- | ------- | ---------------------------- |
| id        | INTEGER | Auto-incremented primary key |
| tag_name  | TEXT    | Name of the tag              |

### Track_Tags Table

| Field    | Type    | Description                  |
| -------- | ------- | ---------------------------- |
| track_id | INTEGER | Foreign key to Tracks table  |
| tag_id   | INTEGER | Foreign key to Tags table    |

## Setup

1. Clone the repository.
2. Run `your_script.py` to initialize the SQLite database and seed data.

## Ready to Get Started?

Select your track from the sidebar and either directly record or upload your performance!
