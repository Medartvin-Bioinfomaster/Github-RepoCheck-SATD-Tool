"""
SATD Knowledge Base - Simple JSON Implementation
"""

import json
import os
from datetime import datetime
from pathlib import Path


# Single JSON file - included in the repository
DEFAULT_KB_PATH = os.path.join(os.path.dirname(__file__), "satd_knowledge_base.json")


def load_knowledge_base(kb_path=DEFAULT_KB_PATH):
    #Load the knowledge base from JSON file.

    if not os.path.exists(kb_path):
        # Create empty knowledge base
        return {
            'metadata': {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'total_entries': 0,
                'last_updated': datetime.now().isoformat()
            },
            'entries': []
        }
    
    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error loading knowledge base: {e}")
        return {
            'metadata': {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'total_entries': 0,
                'last_updated': datetime.now().isoformat()
            },
            'entries': []
        }


def save_knowledge_base(kb, kb_path=DEFAULT_KB_PATH):
    #Save the knowledge base to JSON file.

    kb['metadata']['last_updated'] = datetime.now().isoformat()
    kb['metadata']['total_entries'] = len(kb['entries'])
    
    with open(kb_path, 'w', encoding='utf-8') as f:
        json.dump(kb, f, indent=2, ensure_ascii=False)
    
    print(f"\n Knowledge base saved: {kb_path}")
    print(f" Total entries: {kb['metadata']['total_entries']}")


def add_to_knowledge_base(satd_results, repo_name, repo_url=None, user_id=None, kb_path=DEFAULT_KB_PATH):
    """
    Add SATD findings to the knowledge base.
    For Dev only, aka us
    
    Args:
        satd_results: List of SATD items from detect_satd_in_code()
        repo_name: Name of the repository
        repo_url: Optional URL of the repository
        user_id: Optional user identifier, can be deleted later
        kb_path: Path to JSON file
    
    Returns:
        Number of entries added
    """
    kb = load_knowledge_base(kb_path)
    
    # Create a set of existing entries for fast duplicate checking
    existing_entries = set()
    for entry in kb['entries']:
        # Create unique key: file path + line number + type
        key = (
            entry['satd']['file'],
            entry['satd']['line'],
            entry['satd']['type']
        )
        existing_entries.add(key)
    
    added_count = 0
    skipped_count = 0
    
    for satd in satd_results:
        # Create key for this entry
        entry_key = (
            satd['file'],
            satd['line'],
            satd['type']
        )
        
        # Check if already exists
        if entry_key in existing_entries:
            skipped_count += 1
            continue  # Skip duplicate
        
        # Not a duplicate - add it
        entry = {
            'id': f"{repo_name}_{Path(satd['file']).name}_{satd['line']}_{int(datetime.now().timestamp())}",
            'timestamp': datetime.now().isoformat(),
            'repository': {
                'name': repo_name,
                'url': repo_url
            },
            'user_id': user_id,
            'satd': {
                'file': satd['file'],
                'filename': Path(satd['file']).name,
                'line': satd['line'],
                'type': satd['type'],
                'text': satd['text'],
                'comment': satd['comment'],
                'context_after': satd['context_after'],
                'context_type': satd['context_type']
            }
        }
        kb['entries'].append(entry)
        existing_entries.add(entry_key)  # Add to set for next iteration
        added_count += 1
    
    save_knowledge_base(kb, kb_path)
    
    print(f" Added {added_count} new entries to knowledge base")
    
    
    return added_count


def search_knowledge_base(satd_type=None, repo_name=None, keyword=None, 
                         context_type=None, kb_path=DEFAULT_KB_PATH):
    """
    Search the knowledge base for SATD entries.
    
    """
    kb = load_knowledge_base(kb_path)
    results = kb['entries']
    
    # Apply filters
    if satd_type:
        results = [e for e in results if e['satd']['type'] == satd_type.upper()]
    
    if repo_name:
        results = [e for e in results if repo_name.lower() in e['repository']['name'].lower()]
    
    if keyword:
        results = [e for e in results if keyword.lower() in e['satd']['comment'].lower()]
    
    if context_type:
        results = [e for e in results if e['satd']['context_type'] == context_type]
    
    return results


def get_knowledge_base_stats(kb_path=DEFAULT_KB_PATH):
    #Get statistics about the knowledge base
    
    kb = load_knowledge_base(kb_path)
    
    # Count by type
    type_counts = {}
    repo_counts = {}
    context_type_counts = {}
    
    for entry in kb['entries']:
        satd_type = entry['satd']['type']
        repo_name = entry['repository']['name']
        ctx_type = entry['satd']['context_type']
        
        type_counts[satd_type] = type_counts.get(satd_type, 0) + 1
        repo_counts[repo_name] = repo_counts.get(repo_name, 0) + 1
        context_type_counts[ctx_type] = context_type_counts.get(ctx_type, 0) + 1
    
    return {
        'total_entries': len(kb['entries']),
        'by_type': type_counts,
        'by_repository': repo_counts,
        'by_context_type': context_type_counts,
        'metadata': kb['metadata']
    }


def view_all_entries(kb_path=DEFAULT_KB_PATH, limit=None):
    """
    View all entries in the knowledge base.
    
    """
    kb = load_knowledge_base(kb_path)
    entries = kb['entries']
    
    if limit:
        return entries[:limit]
    return entries