Here's an updated version of the README that focuses on explaining the entire project repository and providing steps for usage without detailed program file explanations:

---

# Data Aggregation and Reporting Project

## Overview

This project consolidates and processes user activity data from multiple sources, including LinkedIn, Fitbit, and Spotify, and generates daily aggregate reports. The goal is to provide insights into user behavior through various metrics such as health stats, music streaming, and social activity. The pipeline processes the data, aggregates key metrics, and outputs the results in CSV files for further analysis or use.

## Project Structure

```
├── runner.py                      # Main script to run the entire data processing pipeline
├── timeline_augmenter.py           # Augments event data with contextual timeline information
├── processors/                    # Data processing scripts for different sources (LinkedIn, Fitbit, Spotify)
│   ├── event.py                   # Defines structured event data using namedtuples
│   ├── fitbit_processor.py         # Processes Fitbit data
│   ├── linkedin_processor.py      # Processes LinkedIn data
│   └── spotify_processor.py       # Processes Spotify data
└── output/                        # Directory to store processed output files
    └── daily_aggregates.csv       # Aggregated daily report
    └── all_events_on_timeline.csv # Consolidated events from all sources
```

## Key Features

- **Data Consolidation**: Consolidates data from LinkedIn, Fitbit, and Spotify into a single dataset.
- **Data Aggregation**: Aggregates the data to calculate various metrics such as averages, sums, and distinct counts.
- **Timeline Augmentation**: Enriches event data with context, such as employer, location, and relationship status over time.
- **Customizable Output**: Outputs aggregated data in CSV format for easy access and further analysis.

## Requirements

To run this project, you'll need the following:

- Python 3.x
- Required dependencies listed in `requirements.txt`

### Install Dependencies

1. Clone the repository:

   ```bash
   git clone <repository_url>
   cd <repository_name>
   ```

2. Install the necessary Python packages:

   ```bash
   pip install -r requirements.txt
   ```

## Setup and Usage

### Step 1: Prepare Your Data

Place your source data files (LinkedIn, Fitbit, Spotify) in the appropriate directories or ensure they are accessible by the scripts.

- LinkedIn data should be in CSV/JSON format.
- Fitbit data should be in CSV/JSON format.
- Spotify data should be in JSON format.

### Step 2: Running the Pipeline

To run the data processing pipeline, simply execute the following command:

```bash
python runner.py
```

This command will:

1. Consolidate data from LinkedIn, Fitbit, and Spotify.
2. Process the data to compute daily aggregates such as averages, sums, and distinct counts.
3. Augment the event data with contextual information (e.g., employer, location, relationship status).
4. Output the results as two CSV files:
   - `daily_aggregates.csv`: Contains the aggregated metrics for each day.
   - `all_events_on_timeline.csv`: Contains the raw consolidated event data with timeline context.

Both files will be saved in the `output/` directory.

### Step 3: Reviewing the Output

After running the pipeline, you can find the following files in the `output/` directory:

- **`daily_aggregates.csv`**: This file contains the daily aggregates of key metrics from all data sources.
- **`all_events_on_timeline.csv`**: This file contains the raw event data from LinkedIn, Fitbit, and Spotify, along with timeline information such as employer and location.

## Contributing

We welcome contributions to improve the project! If you'd like to contribute:

1. Fork the repository.
2. Create a new branch for your feature or fix.
3. Submit a pull request with a description of your changes.
4. Ensure that your code follows the project structure and passes any relevant tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- This project integrates data from various platforms, including LinkedIn, Fitbit, and Spotify, using their respective APIs or file formats.
- Special thanks to the maintainers of the libraries and tools used in this project.

---

This version of the README provides a high-level overview of the project, installation instructions, setup, usage steps, and guidance for contributing. Let me know if you need further adjustments!