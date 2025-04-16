import logging
import os

# Function to create a logger for a specific process
def get_logger(name, log_file_name):

    # Define log file paths
    log_dir = "logs"  # Change to desired directory
    os.makedirs(log_dir, exist_ok=True)  # Create the log directory if it doesn't exist

    log_file = os.path.join(log_dir, log_file_name)

    # Ensure the log file exists
    if not os.path.exists(log_file):
        with open(log_file, "w"):  # Create an empty log file
            pass

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(log_file, mode="a")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Add handler to the logger
    if not logger.hasHandlers():  # Prevent duplicate handlers
        logger.addHandler(file_handler)

    return logger