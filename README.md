# Quick website chatbot in streamlit

This project is a simple yet powerful website chatbot built with Streamlit and LangGraph. It allows users to:

1. Index any website by providing a URL and collection name
2. Chat with an AI assistant about the website's content
3. Get intelligent responses based on different intents:
   - Product information and searches
   - General information queries
   - Purchase assistance
   - Other general questions

The chatbot uses:
- ChromaDB for storing and retrieving website content
- LangGraph for orchestrating conversation flow
- OpenAI's GPT-4 for natural language understanding
- Streamlit for the user interface

The bot intelligently classifies user intent and provides contextually relevant responses by searching through the indexed website content. This makes it ideal for creating quick customer service or information retrieval chatbots for any website.


## Installation



## Usage

```terminal
# Create and activate conda environment
conda create -n webchat python=3.10
conda activate webchat

# Install requirements
pip install -r requirements.txt

# Run the Streamlit app
streamlit run stl.py


```
## TODO
- [ ] Reverse engineer API to add to cart functionality
- [ ] Add tooling for sales bot capabilities
- [ ] Refactor code from notebook format to proper code structure
## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[MIT](https://choosealicense.com/licenses/mit/)