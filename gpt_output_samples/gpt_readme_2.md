# Project Title

This repository contains a data aggregation and analysis pipeline that consolidates data from multiple sources, processes it, and generates meaningful daily aggregates with timeline augmentation. It primarily integrates data from Fitbit, LinkedIn, and Spotify, processes it, and produces an output of aggregated metrics.

## Overview

The project is designed to extract and process data from three primary sources:

- **Fitbit**: Tracks various health metrics such as heart rate variability, sleep score, steps, and more.
- **LinkedIn**: Collects user engagement data such as shares, comments, and reactions.
- **Spotify**: Tracks music listening behavior including playtime, distinct songs, and distinct artists played.

This data is processed, aggregated, and augmented with timelines based on various personal milestones such as employment, location, and relationship status.

## Features

- Data extraction from Fitbit, LinkedIn, and Spotify.
- Aggregation of data to calculate daily metrics (e.g., average heart rate, total steps).
- Augmentation of timelines with personalized metadata (e.g., employment history, location, relationship status).
- Generates consolidated and pivoted data output for analysis.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/project-repository.git
   cd project-repository
   ```

2. **Install dependencies:**

   Ensure you have Python 3 installed. Then, install the required libraries by running:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare the Data:**

   Before running the pipeline, ensure that the data from Fitbit, LinkedIn, and Spotify is available in the appropriate folder structure. The script assumes the following directory layout for each data source:

   - Fitbit: Data should be placed in `data/fitbit/{USERNAME}/`
   - LinkedIn: Data should be placed in `data/linkedin/`
   - Spotify: Data should be placed in `data/spotify/`

2. **Run the Data Pipeline:**

   The pipeline can be executed by running the `runner.py` script, which will handle data extraction, aggregation, and timeline augmentation.

   ```bash
   python runner.py
   ```

   This will read data from the respective directories, process the metrics, and output the daily aggregates in `output/daily_aggregates.csv` and the pivoted data in `output/pivoted.csv`.

3. **Modify the `FITBIT_NAME`:**

   Ensure that the `FITBIT_NAME` variable in `runner.py` is set to your Fitbit username to fetch the correct data.

4. **Timeline Augmentation:**

   The timeline data for employment, location, and relationship status is predefined in the `timeline_augmenter.py` file. These timelines will be used to augment the daily aggregated data with contextual information.

## File Descriptions

- **`runner.py`**: Main script that orchestrates the extraction and aggregation of data from all sources and writes the final aggregated results to CSV files.
- **`timeline_augmenter.py`**: Defines the timeline augmentation logic and the personal milestones that will be applied to the data.
- **`processors/fitbit_processor.py`**: Contains the logic for processing Fitbit data, including parsing CSV and JSON files.
- **`processors/linkedin_processor.py`**: Contains the logic for processing LinkedIn data, handling CSV and JSON files.
- **`processors/spotify_processor.py`**: Contains the logic for processing Spotify data, extracting relevant metrics from JSON files.
- **`processors/event.py`**: Defines the data structure for an event containing the source, metric name, timestamp, value, and content.

## Example Output

The output will include:

- `output/daily_aggregates.csv`: A CSV file containing daily aggregate metrics, such as average heart rate and total steps.
- `output/pivoted.csv`: A pivoted version of the daily aggregates, with metrics as columns and dates as rows.

## Contributions

Feel free to fork the repository, make changes, and submit pull requests. If you find any issues or have suggestions for improvements, open an issue in the GitHub repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README file provides a general overview and guidance on how to set up and use the project.