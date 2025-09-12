# test_groq.py
import requests
import json
import getpass  # Import the getpass library for secure input

def get_groq_models():
    """
    Connects to the Groq API by asking for the key at runtime.
    """
    # 1. Prompt the user to securely enter their API key
    try:
        api_key = getpass.getpass("Please paste your GROQ_API_KEY and press Enter: ")
    except Exception as e:
        print(f"Could not read the API key: {e}")
        return

    if not api_key:
        print("\nError: No API key was entered.")
        return

    # 2. Define the API endpoint and headers
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    print("\nAttempting to connect to the Groq API endpoint...")

    try:
        # 3. Make the GET request
        response = requests.get(url, headers=headers, timeout=10)

        # 4. Check the response and print the results
        if response.status_code == 200:
            print("\n✅ Success! Connection established.\n")
            models_data = response.json()
            
            print("Available Models on GroqCloud:")
            print("-" * 30)
            print(json.dumps(models_data, indent=2))
            
        else:
            print("\n❌ Error: Failed to fetch models. Check if your API key is correct.")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ An error occurred during the network request: {e}")

if __name__ == "__main__":
    get_groq_models()