# AI-Powered Investment Fit Report Generator

This project is a Streamlit web application that generates a preliminary investment fit report for a given startup. It uses AI to gather and analyze data, and then presents it in a clean, downloadable report in both PDF and Markdown formats.

## Features

- **AI-Powered Data Gathering:** Uses the Perplexity AI API to get factual data about a startup.
- **In-Depth Analysis:** Leverages the Groq API with a large language model (Llama 3.3) to generate a qualitative analysis.
- **Custom Investment Rules:** Applies a predefined set of rules to assess the investment fit.
- **Streamlit Web Interface:** Provides a simple and intuitive user interface for generating reports.
- **PDF & Markdown Reports:** Generates professional-looking reports that can be downloaded in both PDF and Markdown formats.

## How to Use

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd investment-tool
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up your API keys:**
    - Rename the `.env.example` file to `.env`.
    - Open the `.env` file and add your API keys for Perplexity AI and Groq.

4.  **Run the Streamlit application:**
    ```bash
    streamlit run app.py
    ```

5.  **Generate a report:**
    - Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).
    - Enter the name of the startup and the target sector in the sidebar.
    - Click the "Generate Report" button.

## Project Structure

- **`app.py`:** The main Streamlit application file. It handles the user interface, orchestrates the API calls, and displays the final report.
- **`api_calls.py`:** Contains the functions for making API calls to Perplexity AI and Groq.
- **`prompts.py`:** Contains the prompts for the initial data gathering and high-level analysis.
- **`new_prompts.py`:** Contains the more detailed, stage and sector-specific prompts for founder and product analysis.
- **`rules.py`:** Defines the custom investment rules that are applied to the startup data.
- **`pdf_generator.py`:** Includes the `PDFReport` class, which uses the `reportlab` library to generate the PDF report.
- **`.env`:** Stores the API keys for Perplexity AI and Groq.

## Dependencies

This project uses the following Python libraries:

- `streamlit`
- `python-dotenv`
- `requests`
- `groq`
- `reportlab`

You can create a `requirements.txt` file with the following content:

```
streamlit
python-dotenv
requests
groq
reportlab
```

## Configuration

To use this application, you need to have API keys for both Perplexity AI and Groq. These keys should be stored in a `.env` file in the root directory of the project, like this:

```
PERPLEXITY_API_KEY="your_perplexity_api_key"
GROQ_API_KEY="your_groq_api_key"
```
