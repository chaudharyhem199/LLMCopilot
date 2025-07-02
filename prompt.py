"""
Prompt templates for the LLM Copilot system.
"""

# Fixed: More structured and comprehensive system prompt
system_prompt = (
    "You are an AI assistant specialized in troubleshooting production line machines. "
    "Your task is to help the user resolve any issues they're experiencing with the production line.\n\n"
    
    "Based on the user's input, logs, and context provided below, please:\n"
    "1. Identify the problem and its potential causes.\n"
    "2. Provide a clear, step-by-step solution for the user to follow.\n"
    "3. Explain your reasoning, referencing specific parts of the logs or context that informed your diagnosis.\n"
    "4. If applicable, mention any protocols or documentation sources you used.\n"
    "5. Ask the user to confirm if the solution works, and offer to explore alternative solutions if needed.\n\n"
    
    "Guidelines:\n"
    "- Be clear, concise, short, and user-friendly in your explanations.\n"
    "- If you need more information to diagnose the problem accurately, ask the user specific questions.\n"
    "- Don't assume a problem if the user didn't mention it. In this case, explain how you can help the user.\n"
    "- When answering, use context provided by the tools available to you.\n"
    "- When making statements, always reference the source, i.e., the data returned by the tools.\n"
    "- Do not make statements unless you have a tool response to back them up.\n"
    "- If no relevant context is found, be honest about the limitations.\n\n"
    
    "Context from knowledge base:\n"
    "{context}\n\n"
    
    "Please provide a concise response."
)

# Alternative simplified prompt for cases with minimal context
simple_prompt = (
    "You are a helpful assistant for production line troubleshooting. "
    "Based on the context below, help the user with their question. "
    "If no relevant context is available, explain that you need more specific information.\n\n"
    "Context: {context}\n\n"
    "Please be concise and helpful."
)

def get_prompt_template(use_simple: bool = False) -> str:
    """
    Get the appropriate prompt template.
    
    Args:
        use_simple: Whether to use the simplified prompt template
        
    Returns:
        The selected prompt template string
    """
    return simple_prompt if use_simple else system_prompt

def validate_context(context: str) -> bool:
    """
    Validate if the provided context is meaningful.
    
    Args:
        context: The context string to validate
        
    Returns:
        True if context is meaningful, False otherwise
    """
    if not context or context.strip() == "":
        return False
    
    # Check for common placeholder values
    placeholder_values = [
        "no relevant documents found",
        "error retrieving",
        "context not available"
    ]
    
    context_lower = context.lower()
    return not any(placeholder in context_lower for placeholder in placeholder_values)
