"""
Azure OpenAI API Configuration
University-provided API for intelligent context extraction
"""

# Azure OpenAI Configuration
AZURE_API_KEY = ""
AZURE_ENDPOINT = "https://gpt-ifi-prog-eksperimenter-swe1.openai.azure.com"
AZURE_API_VERSION = "2025-04-01-preview"
AZURE_DEPLOYMENT_NAME = "gpt-5.1-codex-mini-AM-edvinu-martieka-prod"

# Context extraction settings
MAX_CONTEXT_LINES = 60  # Maximum lines to send to AI for analysis
MAX_RETURNED_LINES = 25  # Maximum lines AI can return as context
