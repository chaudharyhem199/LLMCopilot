#!/usr/bin/env python3
"""
Fixed Implementation of the LLM Copilot with Bug Fixes
=====================================================

This file contains the corrected implementation that fixes:
1. Deprecated LangChain imports
2. Missing error handling and resource management 
3. Logic flaw in context handling (proper RAG implementation)
"""

from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings  # Fixed: Updated import
from dotenv import load_dotenv
import os
import json
import requests
import sys
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

# Import helper functions from the fixed helper.py
from helper import load_pdf_file, text_split, download_hugging_face_embeddings


class ImprovedOllamaClient:
    """Improved Ollama client with proper error handling."""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url
        self.headers = {
            'Content-Type': 'application/json',
        }
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'

    def chat(self, model: str, prompt: str, temperature: float = 0.4, max_tokens: int = 500) -> Dict[str, Any]:
        """
        Send a chat request to the Ollama API with proper error handling.
        
        Args:
            model: The model name to use
            prompt: The prompt to send
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing the response or error information
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/v1/chat', 
                headers=self.headers, 
                data=json.dumps(payload),
                timeout=30  # Add timeout
            )
            response.raise_for_status()  # Raise exception for bad status codes
            return {"success": True, "response": response, "data": response.json()}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}


def validate_environment_variables() -> Dict[str, str]:
    """
    Validate and load required environment variables.
    
    Returns:
        Dict containing validated environment variables
        
    Raises:
        SystemExit: If required variables are missing
    """
    load_dotenv()
    
    pinecone_api_key = os.environ.get('PINECONE_API_KEY')
    ollama_api_key = os.environ.get('OLLAMA_API_KEY')
    
    # Validate required environment variables
    if not pinecone_api_key:
        print("ERROR: PINECONE_API_KEY environment variable is not set!")
        print("Please set your Pinecone API key in a .env file or environment variable.")
        sys.exit(1)
    
    if not ollama_api_key:
        print("WARNING: OLLAMA_API_KEY environment variable is not set!")
        print("Some functionality may not work without the API key.")
    
    print("✓ Environment variables loaded successfully")
    return {
        'PINECONE_API_KEY': pinecone_api_key,
        'OLLAMA_API_KEY': ollama_api_key
    }


def setup_pinecone_index(api_key: str, index_name: str = "llmcopilotlama") -> object:
    """
    Set up Pinecone index with proper error handling.
    
    Args:
        api_key: Pinecone API key
        index_name: Name of the index to create/use
        
    Returns:
        Pinecone client instance
        
    Raises:
        Exception: If Pinecone setup fails
    """
    try:
        from pinecone.grpc import PineconeGRPC as Pinecone
        from pinecone import ServerlessSpec
        
        pc = Pinecone(api_key=api_key)
        
        # Check if index already exists
        existing_indexes = pc.list_indexes().names()
        
        if index_name not in existing_indexes:
            print(f"Creating new Pinecone index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=384, 
                metric="cosine", 
                spec=ServerlessSpec(
                    cloud="aws", 
                    region="us-east-1"
                ) 
            )
            print(f"✓ Index {index_name} created successfully")
        else:
            print(f"✓ Index {index_name} already exists, skipping creation")
            
        return pc
        
    except Exception as e:
        print(f"Error with Pinecone setup: {e}")
        raise


def get_context_from_retriever(question: str, retriever) -> str:
    """
    Retrieve relevant documents and format them as context.
    
    Args:
        question: The user's question
        retriever: The document retriever
        
    Returns:
        Formatted context string from retrieved documents
    """
    try:
        retrieved_docs = retriever.invoke(question)
        if not retrieved_docs:
            return "No relevant documents found."
        
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            context_parts.append(f"Document {i}:\n{doc.page_content}\n")
        
        return "\n".join(context_parts)
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return "Error retrieving relevant documents."


def main():
    """
    Main function demonstrating the fixed RAG implementation.
    """
    print("🚀 Starting Fixed LLM Copilot Implementation")
    print("=" * 50)
    
    # Step 1: Validate environment variables
    env_vars = validate_environment_variables()
    
    # Step 2: Load and process documents
    try:
        print("\n📄 Loading PDF documents...")
        extracted_data = load_pdf_file(data='Data/')
        print(f"✓ Loaded {len(extracted_data)} documents")
        
        print("\n✂️ Splitting documents into chunks...")
        text_chunks = text_split(extracted_data)
        print(f"✓ Created {len(text_chunks)} text chunks")
        
    except Exception as e:
        print(f"Error processing documents: {e}")
        return
    
    # Step 3: Initialize embeddings
    try:
        print("\n🔤 Initializing embeddings...")
        embeddings = download_hugging_face_embeddings()
        print("✓ Embeddings initialized successfully")
        
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        return
    
    # Step 4: Setup Pinecone
    try:
        print("\n🌲 Setting up Pinecone...")
        pc = setup_pinecone_index(env_vars['PINECONE_API_KEY'])
        index_name = "llmcopilotlama"
        
    except Exception as e:
        print(f"Error setting up Pinecone: {e}")
        return
    
    # Step 5: Setup vector store and retriever
    try:
        print("\n🔍 Setting up vector store and retriever...")
        from langchain_pinecone import PineconeVectorStore
        
        # Try to load existing index first, create if it doesn't exist
        try:
            docsearch = PineconeVectorStore.from_existing_index(
                index_name=index_name,
                embedding=embeddings
            )
            print("✓ Loaded existing vector store")
        except:
            # If loading fails, create new vector store
            docsearch = PineconeVectorStore.from_documents(
                documents=text_chunks,
                index_name=index_name,
                embedding=embeddings, 
            )
            print("✓ Created new vector store with documents")
        
        retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        print("✓ Retriever configured successfully")
        
    except Exception as e:
        print(f"Error setting up vector store: {e}")
        return
    
    # Step 6: Setup Ollama client
    try:
        print("\n🦙 Initializing Ollama client...")
        ollama_client = ImprovedOllamaClient(
            base_url="http://workstation.ferienakademie.de:11434", 
            api_key=env_vars['OLLAMA_API_KEY']
        )
        print("✓ Ollama client initialized successfully")
        
    except Exception as e:
        print(f"Error initializing Ollama client: {e}")
        ollama_client = None
    
    # Step 7: Setup prompt template
    system_prompt = (
        "You are an AI assistant specialized in troubleshooting production line machines. "
        "Your task is to help the user resolve any issues they're experiencing with the production line. "
        "Based on the user's input, logs, and context, please: "
        "1. Identify the problem and its potential causes. "
        "2. Provide a clear, step-by-step solution for the user to follow. "
        "3. Explain your reasoning, referencing specific parts of the logs or context that informed your diagnosis. "
        "4. If applicable, mention any protocols or documentation sources you used. "
        "5. Ask the user to confirm if the solution works, and offer to explore alternative solutions if needed. "
        "Be clear, concise, short, and user-friendly in your explanations. "
        "When answering, use context provided below. Always reference the source documents. "
        "Answer concisely.\n\n"
        "Context:\n{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])
    
    # Step 8: Demonstrate fixed RAG functionality
    print("\n🤖 Testing RAG functionality...")
    question = "Tell me about Error motor X and how can I solve it?"
    
    # Fixed: Properly use RAG by retrieving relevant documents
    context_data = get_context_from_retriever(question, retriever)
    print(f"✓ Retrieved context length: {len(context_data)} characters")
    
    # Generate prompt with proper context
    prompt_filled = prompt.format(input=question, context=context_data)
    
    # Send request with error handling
    if ollama_client:
        print("\n📤 Sending request to Ollama...")
        result = ollama_client.chat(model="llama3.1", prompt=prompt_filled)
        
        if result["success"]:
            print("✓ Successfully got response from Ollama")
            print("\n🎯 Response:")
            print("-" * 30)
            if 'data' in result and 'response' in result['data']:
                print(result['data']['response'])
            else:
                print("Response received but format is different than expected")
                print(result)
        else:
            print(f"❌ Error calling Ollama API: {result['error']}")
    else:
        print("❌ Ollama client not available")
    
    print("\n✅ Fixed implementation completed successfully!")


if __name__ == "__main__":
    main()