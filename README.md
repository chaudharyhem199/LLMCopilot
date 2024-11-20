# LLMCopilot
Production Copilot

STEP 01- Create a conda environment after opening the repository

conda create -n medibot python=3.10 -y

conda activate medibot

STEP 02- Install all necessary dependencies from the requirements.txt file:
pip install -r requirements.txt


STEP 03 - Set up environment variables
Create a .env file in the root directory and add the following details:
ELASTICSEARCH_HOST=your_elasticsearch_host  
ELASTICSEARCH_PORT=your_elasticsearch_port  
OPENAI_API_KEY=your_openai_api_key  

STEP 04 - Generate FAISS Index for Vector Database
Use a Hugging Face embedding model (e.g., sentence-transformers/all-MiniLM-L6-v2) to generate vector embeddings for your data.
Run the store_index.py script to create a FAISS index:
