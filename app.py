from flask import Flask, render_template, request, jsonify
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import openai

# Azure Cognitive Search Configuration
search_service_name = "assistsearchapp"
search_index_name = "vector-1733595021750"
search_api_key = "9Chiz2MPEF82cQQ1veFLA4tBU9WYvyQO5VwTfyedWIAzSeAceUKG"

# OpenAI Configuration
openai.api_key = "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"

app = Flask(__name__)

# Initialize Search Client
search_client = SearchClient(
    endpoint=f"https://{search_service_name}.search.windows.net/",
    index_name=search_index_name,
    credential=AzureKeyCredential(search_api_key),
)

def search_index(query):
    """Search the Azure Cognitive Search index."""
    results = search_client.search(query)
    return [result for result in results]

def generate_response(user_input, search_results):
    """
    Generate a natural language response based on user input and search results.
    """
    search_summary = "\n".join([result["Column3"] for result in search_results])  # Adjust field name as needed
    messages = [
        {"role": "system", "content": "Your job is to explain to the user why they are seeing relevant information from the database, based on their user input"},
        {"role": "user", "content": f"User input: {user_input}"},
        {"role": "assistant", "content": f"Relevant information from the database:\n{search_summary}"},
    ]
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" for higher quality
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    
    return response.choices[0].message.content

def generate_response_db(user_input, search_results):
    """
    Generate a natural language response based on user input and search results.
    """
    search_summary = "\n".join([result["Column3"] for result in search_results])  # Adjust field name as needed
    messages = [
        {"role": "system", "content": "You are a helpful assistant providing information based on database search results."},
        {"role": "user", "content": f"User input: {user_input}"},
        {"role": "assistant", "content": f"Relevant information from the database:{search_summary}"},
    ]
    
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # Or "gpt-4" for higher quality
        messages=messages,
        max_tokens=150,
        temperature=0.7,
    )
    
    return search_summary

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.form['user_input']
    
    # Search the Azure index
    search_results = search_index(user_input)
    if not search_results:
        return jsonify({'error': 'No relevant information found'})

    # Generate response using OpenAI
    bot_response = generate_response(user_input, search_results)
    db_response = "\n".join([result["Column3"] for result in search_results])
    
    return jsonify({'bot_response': bot_response, 'db_response': db_response})

if __name__ == "__main__":
    app.run(debug=True)


def main():
    print("Welcome! Type your query and I will respond.")
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        try:
            # Search the Azure index
            search_results = search_index(user_input)
            if not search_results:
                print("Bot: I couldn't find any relevant information.")
                continue
            
            # Generate response using OpenAI
            bot_response = generate_response(user_input, search_results)
            db_response = generate_response_db(user_input, search_results)
            print(f"Bot: {bot_response}")
            print(f"The web info: {db_response}")
        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
