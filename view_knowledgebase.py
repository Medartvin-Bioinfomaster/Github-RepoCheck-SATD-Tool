
"""
View and search the SATD knowledge base.


Usage: python view_knowledge_base.py
"""

from satd_knowledgebase import (
    view_all_entries,
    search_knowledge_base,
    get_knowledge_base_stats
)
import os


def print_entry(entry, index=None, similarity=None, show_scores=False):

 # Pretty print a single SATD entry with optional similarity score.
 # Print code is based on AI generated code

    if index:
        print(f"\n{'='*80}")
        if similarity:
            print(f"Match #{index} - Similarity: {similarity:.1%}")
        else:
            print(f"Entry #{index}")


    print(f"{'='*80}")
    print(f"Repository: {entry['repository']['name']}")

    if entry['repository'].get('url'):
        print(f"URL: {entry['repository']['url']}")

    print(f"File: {entry['satd']['filename']} (Line {entry['satd']['line']})")
    print(f"Type: {entry['satd']['type']}")
    print(f"Timestamp: {entry['timestamp']}")
    print(f"\nSATD Comment:")
    print(f"  {entry['satd']['comment']}")
    print(f"\nContext Type: {entry['satd']['context_type']}")
    print(f"Context (first 10 lines):")

    for i, line in enumerate(entry['satd']['context_after'][:10]):
        print(f"  {line}")
    if len(entry['satd']['context_after']) > 10:
        print(f"  ... ({len(entry['satd']['context_after']) - 10} more lines)")


def similarity_search():
    """
    Perform semantic similarity search using all-MiniLM-L6-v2.
    User pastes code, system finds similar SATD entries.
    """
    print("\n" + "="*80)
    print("SEMANTIC SIMILARITY SEARCH")
    print("="*80)
    print("\nInstructions:")
    print("  1. Set your similarity threshold")
    print("  2. Paste your code snippet")
    print("  3. Press Enter twice when finished")
    print("\nNote: Uses all-MiniLM-L6-v2 for semantic similarity detection")
    print("\n" + "-"*80 + "\n")
    
    # Get threshold from user
    while True:
        try:
            threshold_input = input("Enter similarity threshold (0-100%, default 70): ").strip()
            
            if not threshold_input:
                threshold = 0.70  # Default
                print(f"Using default threshold: 70%")
                break
            
            threshold_value = float(threshold_input)
            
            # Accept both 0-1 format and 0-100 format
            if 0 <= threshold_value <= 1:
                threshold = threshold_value
            elif 1 < threshold_value <= 100:
                threshold = threshold_value / 100.0
            else:
                print("Please enter a value between 0-100")
                continue
            
            print(f"Threshold set to: {threshold:.0%}")
            break
            
        except ValueError:
            print("Invalid input. Please enter a number between 0-100")
    
    print("\n" + "-"*80 + "\n")
    print("Paste your code snippet below (press Enter twice when finished):\n")
    
    # Collect user input
    code_lines = []
    empty_count = 0
    
    try:
        while True:
            line = input()
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
                code_lines.append(line)
            else:
                empty_count = 0
                code_lines.append(line)
    except KeyboardInterrupt:
        print("\n\nSearch cancelled.")
        return
    
    user_code = '\n'.join(code_lines).strip()
    
    if not user_code:
        print("\nNo code provided.")
        return
    
    # Display what user entered
    print(f"\n{'='*80}")
    print("YOUR CODE SNIPPET:")
    print(f"{'='*80}")
    if len(user_code) > 300:
        print(user_code[:300] + "\n... (truncated for display)")
    else:
        print(user_code)
    print(f"{'='*80}\n")

    print("Starting similarity search ... allMiniLM-L6-v2 model is loading!\n")
    
    # Perform similarity search
    try:
        from satd_similarity import find_similar_satd_in_kb
        
        print("Initializing similarity search...")
        
        results = find_similar_satd_in_kb(user_code, threshold)
        
        # Display results
        print(f"\n{'='*80}")
        print("RESULTS")
        print(f"{'='*80}\n")
        
        if not results:
            print(f"No similar entries found (all scores below {threshold:.0%})\n")
            print("Suggestions:")
            print("  - Try a different code snippet")
            print("  - Use more complete code context")
            print(f"  - Lower the threshold (currently {threshold:.0%})")
        else:
            print(f"Found {len(results)} similar SATD entries")
            print(f"(Similarity >= {threshold:.0%})\n")
            print(f"{'='*80}\n")
            
            # Display top results
            for idx, (entry, similarity_score) in enumerate(results[:10], 1):
                print_entry(entry, idx, similarity_score)
                
                # Pause between results for readability
                if idx < len(results[:10]) and idx < len(results):
                    try:
                        input("\n[Press Enter for next result, or Ctrl+C to stop]")
                    except KeyboardInterrupt:
                        print("\n")
                        break
            
            # Offer to show more if available
            if len(results) > 10:
                print(f"\n{'='*80}")
                print(f"... and {len(results) - 10} more similar entries")
                print(f"{'='*80}\n")
                
                try:
                    show_all = input(f"Show all {len(results)} results? (y/n): ").strip().lower()
                    if show_all == 'y':
                        for idx, (entry, similarity_score) in enumerate(results[10:], 11):
                            print_entry(entry, idx, similarity_score)
                            if idx < len(results):
                                input("\n[Press Enter to continue...]")
                except KeyboardInterrupt:
                    print("\n")
    
    except ImportError:
        print("\nError: satd_similarity.py not found or dependencies missing!")
        print("\nInstall required packages:")
        print("  pip install sentence-transformers numpy --break-system-packages")
    except Exception as e:
        print(f"\nError during similarity search: {e}")


def start_db_interaction():
    """Main menu loop."""
    print("=" * 80)
    print("SATD KNOWLEDGE BASE VIEWER")
    print("=" * 80)
    
    while True:
        print("\nOptions:")
        print("1. View statistics")
        print("2. View all entries (first 10)")
        print("3. Search by SATD type")
        print("4. Search by keyword")
        print("5. Search by repository")
        print("6. Export to HTML")
        print("7. Semantic similarity search (AI)")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ").strip()
        
        if choice == '1':
            stats = get_knowledge_base_stats()
            print(f"\n{'='*80}")
            print("KNOWLEDGE BASE STATISTICS")
            print(f"{'='*80}")
            print(f"Total Entries: {stats['total_entries']}")
            print(f"\nBy Type:")
            
            for satd_type, count in sorted(stats['by_type'].items()):
                print(f"  {satd_type}: {count}")
            print(f"\nBy Repository:")
            for repo, count in sorted(stats['by_repository'].items()):
                print(f"  {repo}: {count}")
            print(f"\nBy Context Type:")
            for ctx_type, count in stats['by_context_type'].items():
                print(f"  {ctx_type}: {count}")
        

        elif choice == '2':
            entries = view_all_entries(limit=10)
            total = len(view_all_entries())
            print(f"\nShowing first 10 entries (out of {total} total):")
            for i, entry in enumerate(entries, 1):
                print_entry(entry, i)
                if i < 10:
                    try:
                        input("\n[Press Enter for next entry...]")
                    except KeyboardInterrupt:
                        print("\n")
                        break
        
        elif choice == '3':
            satd_type = input("\nEnter SATD type (TODO, FIXME, HACK, etc.): ").strip()
            results = search_knowledge_base(satd_type=satd_type)
            print(f"\nFound {len(results)} entries of type '{satd_type}':")
            for i, entry in enumerate(results[:10], 1):
                print_entry(entry, i)
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more entries")
        
        elif choice == '4':
            keyword = input("\nEnter keyword to search in comments: ").strip()
            results = search_knowledge_base(keyword=keyword)
            print(f"\nFound {len(results)} entries containing '{keyword}':")
            for i, entry in enumerate(results[:10], 1):
                print_entry(entry, i)
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more entries")
        
        elif choice == '5':
            repo = input("\nEnter repository name: ").strip()
            results = search_knowledge_base(repo_name=repo)
            print(f"\nFound {len(results)} entries from repository '{repo}':")
            for i, entry in enumerate(results[:10], 1):
                print_entry(entry, i)
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more entries")
        
        elif choice == '6':
            print("\n" + "="*80)
            print("EXPORT TO HTML")
            print("="*80)
            
            output_file = input("\nEnter output filename (press Enter for default): ").strip()
            if not output_file:
                output_file = "satd_knowledge_base.html"
            
            if not output_file.endswith('.html'):
                output_file += '.html'
            
            try:
                from export_to_html import export_to_html
                
                print(f"\nGenerating HTML export...")
                export_to_html(output_file)
                
                open_browser = input("\nOpen in browser? (y/n): ").strip().lower()
                if open_browser == 'y':
                    import webbrowser
                    webbrowser.open('file://' + os.path.abspath(output_file))
                    print("Opened in browser!")
                
            except ImportError:
                print("\nError: export_to_html.py not found!")
            except Exception as e:
                print(f"\nError: {e}")
        
        elif choice == '7':
            similarity_search()
        
        elif choice == '8':
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    start_db_interaction()
