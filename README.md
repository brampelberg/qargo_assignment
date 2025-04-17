# Qargo Assignment

## Overview

This project provides a tool to synchronize unavailabilities for resources from an external master data system into a Qargo environment. The synchronization process ensures that planners have up-to-date data for the year 2025 (configurable). The tool is implemented in Python and leverages the Qargo API for data retrieval and updates.

## Features

- Synchronizes unavailabilities from an external master system to the Qargo environment.
- Filters unavailabilities to only include those in the year 2025.
- Implements the **Decorator Design Pattern** for retry logic with exponential backoff.
- Uses **Pydantic** for data validation and mapping.
- Includes extended debug logging for maintainability
- Configurable via environment variables for flexibility and security.

## Dependencies

- `requests`
- `python-dotenv`
- `pydantic`
- `APScheduler`
- `pytz`

## Installation

1. Clone the repository:
2. 
```bash
git clone https://github.com/your-repo/qargo-assignment.git
cd qargo-assignment
```

1. Create a virtual environment and activate it:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate
```

3. Install the required dependencies:

`pip install -r requirements.txt`

4. Create a `.env` file in the root folder based on the provided `.env.template` and fill in the required values:

```sh
MASTER_API_CLIENT_ID="your-master-client-id"
MASTER_API_CLIENT_SECRET="your-master-client-secret"
API_CLIENT_ID="your-target-client-id"
API_CLIENT_SECRET="your-target-client-secret"
API_URL="your-api-url"
LOG_LEVEL="INFO"
LOG_FILE="./app.log"
LOG_TO_FILE=true
LOG_TO_CONSOLE=true
SYNC_CRON_SCHEDULE="*/5 * * * *"
```

## Usage
1. Run the script:

`python src/main.py`

2. The script will start an APScheduler job that synchronizes unavailabilities based on the cron schedule defined in the `.env` file.

## Design Patterns
- The Decorator Design Pattern is implemented in the with_exponential_backoff function located in `src/utils/utils.py`. This decorator is applied to API calls to handle retries with exponential backoff in case of rate-limiting. This ensures resilience and reliability in the integration.
- The Adapter Design Pattern is implemented using dtos and QargoAPIClient. The dtos represent the API response in a 1 to 1 manner and are used to parse the response into a python object. Afterwards the dtos are converted to an internal model used in the synchronisation logic. This way the application logic is not dependend on the API response and doesn't need to be changed if the API changes slightly. The QargoAPIClient acts as the adapter and exposes an interface that takes the internal model and translates it to the correct API calls.

## Logging
The tool uses a configurable logging setup:
- Log level and log file path can be configured via the `.env` file.
- Extra debug logging is added for the sync plan.

## Error Handling
- API calls are wrapped with retry logic to handle rate limit errors.
- Validation errors from Pydantic are logged and raised for debugging.
- Critical failures (e.g., inability to fetch resources) terminate the sync job gracefully with appropriate logs.

## Security Measures
- API credentials are stored in a `.env` file and loaded securely using python-dotenv.
- Sensitive information is excluded from logs.
- The `.env` file is included in `.gitignore` to prevent accidental exposure.
