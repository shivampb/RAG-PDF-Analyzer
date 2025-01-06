# PDF Query App

This repository provides a web application built with Streamlit to query PDF documents efficiently. By combining modern AI models for embedding and large language model-based queries, this application processes PDFs to deliver insightful answers to user queries.

![rag](assets/rag.png)


## Features

- **PDF Upload and Processing**: Users can upload PDF files to analyze their content.
- **Asynchronous Execution**: Ensures efficient processing of large documents.
- **Text Splitting**: Splits large text into manageable chunks for better embedding and querying.
- **Vector Store Integration**: Uses Chroma for storing document embeddings.
- **AI-Powered Queries**: Integrates the latest LLMs for accurate and contextually rich responses.
- **Chat History**: Keeps track of user queries and corresponding responses.

---

## Installation Guide

Follow these steps to install and run the PDF Query App:

### Prerequisites

Ensure you have the following installed:

- Python 3.8 or higher
- `pip` for Python package management

### Step 1: Clone the Repository

```bash
# Clone the repository
$ git clone https://github.com/yourusername/pdf-query-app.git

# Navigate to the project directory
$ cd pdf-query-app
```

### Step 2: Set Up a Virtual Environment (Optional but Recommended)

```bash
# Create a virtual environment
$ python -m venv venv

# Activate the virtual environment
# On Windows:
$ venv\Scripts\activate
# On Mac/Linux:
$ source venv/bin/activate
```

### Step 3: Install Required Libraries

```bash
# Install dependencies
$ pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
# Start the Streamlit app
$ streamlit run app.py
```

---

## Usage Instructions

1. **Upload a PDF**: Use the sidebar to upload your PDF document.
2. **Enter Your Query**: Input the question you'd like to ask about the document.
3. **View Responses**: The application will process your query and display the result along with a history of previous queries.

---

## Key Components

- **`main(file, query)`**: An asynchronous function to process the PDF and retrieve responses.
- **`RecursiveCharacterTextSplitter`**: Splits the PDF content into chunks for embedding.
- **`OllamaEmbeddings`**\*\* and \*\*\*\*`OllamaLLM`\*\*: Utilizes cutting-edge embeddings and LLMs.
- **`Chroma`**: Serves as the vector store for efficient similarity search.
- **Streamlit Interface**: A user-friendly UI to interact with the app.

---

## Troubleshooting

- **Error: Missing Dependencies**: Ensure all required packages are installed using `pip install -r requirements.txt`.
- **Streamlit Not Found**: Run `pip install streamlit` if the module is not found.
- **Model Connection Issues**: Verify that the Ollama models are hosted and accessible at the configured base URL.

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Screenshot

Below is a conceptual layout of the app:
![rag](assets/Screenshot.png)




---

## Contact

For inquiries or support, please reach out at [thenan0987@gmail.com](mailto\:thenan0987@gmail.com).

