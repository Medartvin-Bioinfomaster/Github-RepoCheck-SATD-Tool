"""
AI-powered context extraction using Azure OpenAI
Intelligently identifies relevant code context for SATD comments
"""

import requests
import json
import re
from apiConfig import (
    AZURE_API_KEY,
    AZURE_ENDPOINT,
    AZURE_API_VERSION,
    AZURE_DEPLOYMENT_NAME,
    MAX_CONTEXT_LINES,
    MAX_RETURNED_LINES
)


def extract_context_with_ai(satd_comment, code_after_comment):
    """
    Use AI to intelligently extract relevant code context for a SATD comment.
    Returns plain text code as a list of strings.
    
    Args:
        satd_comment: The SATD comment text (e.g., "TODO: add error handling")
        code_after_comment: Lines of code following the comment (list of strings)
    
    Returns:
        List of strings (the relevant code lines)
    """
    
    # Number the lines for the AI
    numbered_lines = []
    for i, line in enumerate(code_after_comment[:MAX_CONTEXT_LINES], 1):
        numbered_lines.append(f"{i}: {line}")
    code_with_numbers = '\n'.join(numbered_lines)
    
    # Create simple prompt - asking for plain text code only
    prompt = f"""Identify relevant code for this technical debt comment.

SATD Comment: {satd_comment}

Code (with line numbers):
{code_with_numbers}

Copy ONLY the relevant code lines (no line numbers, no explanations, just raw code):
Max number of lines {MAX_RETURNED_LINES}"""
    
    try:
        # Construct URL
        url = f"{AZURE_ENDPOINT}/openai/responses?api-version={AZURE_API_VERSION}"
        
        # Prepare headers
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AZURE_API_KEY}"
        }
        
        # Prepare request - plain text response
        payload = {
            "input": prompt,
            "max_output_tokens": 1600,
            "model": AZURE_DEPLOYMENT_NAME
        }
        
        # Make API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
       # Check for errors
        if response.status_code != 200:
            print(f"  Warning: API returned status {response.status_code}")
            print(f"  Error details: {response.text}")  # ← See what the error actually says
            raise Exception(f"API error: {response.status_code}")
        
        # Parse response
        response_data = response.json()
        
        # Check if response is incomplete
        if response_data.get('status') == 'incomplete':
            reason = response_data.get('incomplete_details', {}).get('reason', 'unknown')
            print(f"  Warning: Response incomplete ({reason})")
            usage = response_data.get('usage', {})
            print(f"  Tokens used: {usage.get('output_tokens', '?')} (reasoning: {usage.get('output_tokens_details', {}).get('reasoning_tokens', '?')})")
            raise Exception(f"Incomplete response: {reason}")
        
        # Extract AI response from Azure Responses API format
        ai_response = None
        
        if 'output' in response_data and isinstance(response_data['output'], list):
            # Find the message output (type='message')
            for output_item in response_data['output']:
                if output_item.get('type') == 'message':
                    # Get the content
                    content = output_item.get('content', [])
                    if content and len(content) > 0:
                        ai_response = content[0].get('text', '')
                        break
        
        if not ai_response:
            print(f"  Warning: Could not extract text from response")
            print(f"  Response status: {response_data.get('status')}")
            raise Exception("Could not parse AI response")
        
        # Clean up response
        ai_response = ai_response.strip()
        
        # Remove line numbers if AI included them
        lines = ai_response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Remove "N: " pattern at start (e.g., "2: code" → "code")
            cleaned_line = re.sub(r'^\s*\d+:\s*', '', line)
            cleaned_lines.append(cleaned_line)
        
        # Remove empty lines at start
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        
        # Remove empty lines at end
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
        
        # Validate we got something
        if not cleaned_lines:
            raise Exception("AI returned empty response")
        
        print(f"    AI selected {len(cleaned_lines)} lines of code")
        
        return cleaned_lines
    
    except Exception as e:
        print(f"  Warning: AI context extraction failed: {e}")
        print(f"  Using fallback (first 3 lines)")
        return code_after_comment[:3]