# Digital Detox

## Overview
Digital Detox is a Windows application designed to help users improve focus and productivity by temporarily blocking distracting applications and internet access.

## Features
- **Block Specific Applications:** Prevent selected applications from running.
- **Block Internet Access:** Disable all internet connectivity.
- **Quick Blocking:** Immediately start a focus session by blocking apps or internet.
- **Routine/Scheduled Blocking:** Set up recurring schedules to block specific applications automatically.
- **Cooling Period:** A configurable delay to discourage users from prematurely ending a block.
- **Configuration Persistence:** Save and load lists of blocked applications and user settings.
- **Start with Windows:** Optionally configure the application to launch automatically when Windows starts.

## How to Use

The application is organized into several tabs:

-   **Dashboard:** Displays currently active blocks, upcoming scheduled blocks, and general usage statistics.
-   **Block Apps:**
    -   Select running applications from a list or browse to an application's executable file (`.exe`).
    -   Set a duration for how long the application(s) should be blocked.
    -   Initiate the block.
    -   Configure routine blocks for specific applications based on a schedule (e.g., block social media apps every weekday from 9 AM to 5 PM).
-   **Block Internet:**
    -   Set a duration for how long internet access should be blocked.
    -   Initiate the internet block.
-   **Settings:**
    -   Configure the duration of the "Cooling Period."
    -   Toggle the "Start with Windows" option.

**General Workflow for Blocking an Application:**
1.  Navigate to the "Block Apps" tab.
2.  Either select one or more applications from the list of currently running processes or click "Block App by Path" to choose an application's executable file.
3.  Enter the desired block duration (e.g., "1h 30m" or "45m").
4.  Click the "Block Selected Apps" or "Block App by Path" button.

**General Workflow for Blocking Internet Access:**
1.  Navigate to the "Block Internet" tab.
2.  Enter the desired block duration (e.g., "2h" or "1h 15m").
3.  Click the "Block Internet" button.

**Cooling Period:**
If you attempt to unblock an application or restore internet access before the scheduled block duration has ended, the application will enforce a "cooling period." You will need to wait for this configurable period (e.g., 5 minutes) to elapse before the unblocking action is confirmed. This feature is designed to discourage impulsive unblocking.

## Installation/Setup

This is a Windows application.

**Running the Executable (if available):**
1.  Download the latest executable file from the project's Releases page (link to be added here if applicable).
2.  Run the downloaded `.exe` file. No installation is typically required.

**Running from Source:**
1.  **Prerequisites:**
    *   Python 3 (download from [python.org](https://www.python.org/downloads/))
    *   Required Python packages: `psutil`
2.  **Install Packages:**
    Open a command prompt or terminal and run:
    ```bash
    pip install psutil
    ```
    (Note: `tkinter` is usually included with standard Python installations on Windows.)
3.  **Run the Application:**
    Navigate to the directory containing the source code and run:
    ```bash
    python digital_detox.py
    ```

## Building from Source

You can create a standalone executable from the source code using `cx_Freeze`. A `setup.py` script is included for this purpose.

1.  **Prerequisite:** Install `cx_Freeze`:
    ```bash
    pip install cx_Freeze
    ```
2.  **Build Command:**
    Open a command prompt or terminal in the project's root directory and run:
    ```bash
    python setup.py build
    ```
    This will create a `build` directory containing the executable and its dependencies.

## Contributing
Contributions are welcome! Please fork the repository, create a new branch for your feature or bug fix, and submit a pull request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
