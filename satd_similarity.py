"""
SATD Similarity Analysis using all-MiniLM-L6-v2
Fast and efficient sentence transformer optimized for semantic similarity.

"""

from sentence_transformers import SentenceTransformer
import numpy as np
from satd_knowledgebase import view_all_entries


# Load CodeBERT model ONCE (when module is imported)
print("Loading MiniLM-L6-V2 model...")
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')



def compute_similarity(code1, code2):
    """
    Compute semantic similarity between two text snippets using all-MiniLM-L6-v2.
    Uses cosine similarity of sentence embeddings
    
    """
    # Generate embeddings 
    embedding1 = model.encode(code1, convert_to_tensor=False)
    embedding2 = model.encode(code2, convert_to_tensor=False)

    
    # Compute cosine similarity
    dot_product = np.dot(embedding1, embedding2)
    magnitude1 = np.linalg.norm(embedding1)
    magnitude2 = np.linalg.norm(embedding2)

    
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0
    
    similarity = dot_product / (magnitude1 * magnitude2)
    
    return float(similarity)


def find_similar_satd_in_kb(user_code, threshold=0.70):
    """

    Compares only against code context (not SATD comments) to find 
    structurally similar code patterns.
    
    """
    kb_entries = view_all_entries()
    
    if not kb_entries:
        print(" Knowledge base is empty!")
        return []
    
    print(f"\n Comparing your code with {len(kb_entries)} entries using MiniLM-L6-V2...")
    
    results = []
    
    

    for idx, entry in enumerate(kb_entries, 1):
        # Uses only code context and ignores comments for similarity
        kb_code = '\n'.join(entry['satd']['context_after'])

        similarity = compute_similarity(user_code, kb_code)
        
        # Only keep if above threshold
        if similarity >= threshold:
            results.append((entry, similarity))
        
        # Progress indicator 
        if idx % 5 == 0 or idx == len(kb_entries):
            print(f"  Progress: {idx}/{len(kb_entries)} entries processed...", end='\r')
    
    print(f"\n✓ Comparison complete!")
    
    # Sort by similarity (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    return results