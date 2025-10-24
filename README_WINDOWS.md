# AI-Powered Investment Fit Report Generator (Windows Guide)

This project is a Streamlit web application that generates a preliminary investment fit report for a given startup. It uses AI to gather and analyze data, and then presents it in a clean, downloadable report in both PDF and Markdown formats.

## Features

- **AI-Powered Data Gathering:** Uses the Perplexity AI API to get factual data about a startup.
- **In-Depth Analysis:** Leverages the Groq API with a large language model (Llama 3.3) to generate a qualitative analysis.
- **Custom Investment Rules:** Applies a predefined set of rules to assess the investment fit.
- **Streamlit Web Interface:** Provides a simple and intuitive user interface for generating reports.
- **PDF & Markdown Reports:** Generates professional-looking reports that can be downloaded in both PDF and Markdown formats.

## How to Use (Windows)

0.  **Install Python:**
    This project requires Python 3.8 or newer. If you don't have Python installed, or if you have an older version, follow these steps:

    1.  **Download Python:** Go to the official Python website: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
    2.  **Run the Installer:** Download the latest stable version for Windows (e.g., "Windows installer (64-bit)").
    3.  **Important:** During installation, make sure to check the box that says "**Add Python X.Y to PATH**" (where X.Y is the version number). This will allow you to run Python commands from any terminal.
    4.  **Verify Installation:** Open a new Command Prompt or PowerShell window and type:
        ```bash
        python --version
        ```
        You should see the installed Python version.

1.  **Install Git (if not already installed):**
    Git is essential for cloning the repository. You can install it using Winget (Windows Package Manager), which is often pre-installed on modern Windows versions.

    1.  **Open PowerShell as Administrator:**
        *   Search for "PowerShell" in the Start Menu.
        *   Right-click on "Windows PowerShell" and select "Run as administrator."

    2.  **Install Git:**
        *   In the Administrator PowerShell window, type the following command and press Enter:
            ```powershell
            winget install Git.Git
            ```
        *   If `winget` is not recognized, install it from the Microsoft Store by searching for "App Installer" or visiting [https://aka.ms/getwinget](https://aka.ms/getwinget).
        *   Follow any prompts to accept agreements.

    3.  **Verify Installation:**
        *   After installation, **close and reopen** your PowerShell or Command Prompt window.
        *   Then, type:
            ```bash
            git --version
            ```
            You should see the installed Git version.

2.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd investment-tool
    ```

3.  **Create a virtual environment and install dependencies:**
    Open the Windows Command Prompt (`cmd`) or PowerShell and run the following commands.
    ```powershell
    # Create the virtual environment folder named 'venv'
    python -m venv venv

    # Activate the environment
    .\venv\Scripts\activate

    # Install the required packages
    pip install -r requirements.txt
    ```

4.  **Set up your API keys:**
    - Rename the `.env.example` file to `.env`.
    - Open the `.env` file and add your API keys for Perplexity AI and Groq.

5.  **Run the Streamlit application:**
    With your virtual environment still active, run:
    ```powershell
    streamlit run app.py
    ```

6.  **Generate a report:**
    - Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).
    - Enter the name of the startup and the target sector in the sidebar.
    - Click the "Generate Report" button.

## Creating a Standalone `.exe` File

You can package this application into a single `.exe` file that can be run on other Windows machines without needing Python or any dependencies installed.

1.  **Install PyInstaller:**
    In your active virtual environment, run:
    ```powershell
    pip install pyinstaller
    ```

2.  **Run the PyInstaller command:**
    From the project's root directory, run the following command. This includes a critical flag (`--add-data`) to ensure the `rules.json` file is included in your final executable.
    ```powershell
    pyinstaller --onefile --windowed --add-data "rules.json;." app.py
    ```

3.  **Find your executable:**
    PyInstaller will create a `dist` folder. Inside this folder, you will find `app.exe`. This is your standalone application.


## Project Structure

- **`app.py`:** The main Streamlit application file.
- **`api_calls.py`:** Contains functions for making API calls.
- **`prompts.py` & `new_prompts.py`:** Contain the prompts for the AI models.
- **`rules.py` & `rules.json`:** Define the custom investment rules.
- **`pdf_generator.py`:** Includes the class to generate PDF reports using `reportlab`.
- **`.env`:** Stores the API keys.

## Dependencies

This project uses the following Python libraries, as listed in `requirements.txt`:
- `streamlit`
- `python-dotenv`
- `requests`
- `groq`
- `reportlab`
