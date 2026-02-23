"""
View and search the SATD knowledge base.

Usage: python view_knowledge_base.py
"""
import export_to_html
from satd_knowledgebase import (
    view_all_entries,
    search_knowledge_base,
    get_knowledge_base_stats
)


def print_entry(entry, index=None):
    """Pretty print a single SATD entry."""
    if index:
        print(f"\n{'='*80}")
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


def main():
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
        print("6. View knowledge base in HTML (open in browser)")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            stats = get_knowledge_base_stats()
            print(f"\n{'='*80}")
            print("KNOWLEDGE BASE STATISTICS")
            print(f"{'='*80}")
            print(f"Total Entries: {stats['total_entries']}")
            print(f"\nBy Type:")
            for satd_type, count in stats['by_type'].items():
                print(f"  {satd_type}: {count}")
            print(f"\nBy Repository:")
            for repo, count in stats['by_repository'].items():
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
        
        elif choice == '3':
            satd_type = input("Enter SATD type (TODO, FIXME, HACK, etc.): ").strip()
            results = search_knowledge_base(satd_type=satd_type)
            print(f"\nFound {len(results)} entries of type '{satd_type}':")
            for i, entry in enumerate(results[:10], 1):
                print_entry(entry, i)
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more entries")
        
        elif choice == '4':
            keyword = input("Enter keyword to search in comments: ").strip()
            results = search_knowledge_base(keyword=keyword)
            print(f"\nFound {len(results)} entries containing '{keyword}':")
            for i, entry in enumerate(results[:10], 1):
                print_entry(entry, i)
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more entries")
        
        elif choice == '5':
            repo = input("Enter repository name: ").strip()
            results = search_knowledge_base(repo_name=repo)
            print(f"\nFound {len(results)} entries from repository '{repo}':")
            for i, entry in enumerate(results[:10], 1):
                print_entry(entry, i)
            if len(results) > 10:
                print(f"\n... and {len(results) - 10} more entries")
        
        elif choice == '6':
            print("Opening knowledge base in HTML format...")
            export_to_html.export_to_html()
        
        elif choice == '7':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()