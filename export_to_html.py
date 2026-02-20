"""
Export knowledge base to an interactive HTML file.
HTML file is created with the help of AI.

"""

from satd_knowledgebase import load_knowledge_base, get_knowledge_base_stats



def export_to_html(output_file="satd_knowledge_base.html"):
    """Export knowledge base to a clean, professional HTML file."""
    
    kb = load_knowledge_base()
    stats = get_knowledge_base_stats()
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SATD Knowledge Base</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background-color: #f5f5f5;
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        
        header {{
            background-color: #fff;
            border-bottom: 2px solid #333;
            padding: 30px 40px;
        }}
        
        header h1 {{
            font-size: 1.8em;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }}
        
        header p {{
            color: #666;
            font-size: 0.95em;
        }}
        
        .stats {{
            display: flex;
            gap: 30px;
            padding: 25px 40px;
            background: #fafafa;
            border-bottom: 1px solid #ddd;
        }}
        
        .stat-item {{
            flex: 1;
        }}
        
        .stat-item .number {{
            font-size: 1.8em;
            font-weight: 600;
            color: #333;
        }}
        
        .stat-item .label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 2px;
        }}
        
        .controls {{
            padding: 20px 40px;
            background: #fff;
            border-bottom: 1px solid #ddd;
        }}
        
        .search-box {{
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 0.95em;
            margin-bottom: 15px;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #666;
        }}
        
        .filter-group {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 6px 14px;
            border: 1px solid #ccc;
            background: white;
            color: #333;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        
        .filter-btn:hover {{
            background: #f5f5f5;
            border-color: #999;
        }}
        
        .filter-btn.active {{
            background: #333;
            color: white;
            border-color: #333;
        }}
        
        .entries {{
            padding: 25px 40px;
        }}
        
        .entry {{
            border: 1px solid #ddd;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 4px;
            background: #fff;
        }}
        
        .entry:hover {{
            border-color: #999;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .entry-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }}
        
        .entry-type {{
            display: inline-block;
            padding: 4px 10px;
            border: 1px solid #666;
            border-radius: 3px;
            font-weight: 600;
            font-size: 0.8em;
            color: #333;
            background: #f5f5f5;
        }}
        
        .entry-meta {{
            color: #666;
            font-size: 0.85em;
            text-align: right;
        }}
        
        .entry-comment {{
            background: #fafafa;
            padding: 12px;
            border-left: 3px solid #666;
            margin: 12px 0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9em;
            color: #333;
        }}
        
        .entry-context {{
            background: #f8f8f8;
            border: 1px solid #ddd;
            padding: 12px;
            border-radius: 3px;
            overflow-x: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85em;
            margin-top: 12px;
        }}
        
        .entry-context pre {{
            margin: 0;
            white-space: pre-wrap;
            color: #333;
        }}
        
        .context-label {{
            color: #666;
            font-weight: 600;
            margin-bottom: 8px;
            display: block;
            font-size: 0.85em;
        }}
        
        .no-results {{
            text-align: center;
            padding: 60px 20px;
            color: #999;
        }}
        
        .no-results h2 {{
            font-size: 1.5em;
            margin-bottom: 10px;
            color: #666;
        }}
        
        footer {{
            text-align: center;
            padding: 20px;
            background: #fafafa;
            color: #666;
            font-size: 0.85em;
            border-top: 1px solid #ddd;
        }}
        
        footer p {{
            margin: 3px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>SATD Knowledge Base</h1>
            <p>Self-Admitted Technical Debt in Bioinformatics R Packages</p>
        </header>
        
        <div class="stats">
            <div class="stat-item">
                <div class="number">{stats['total_entries']}</div>
                <div class="label">Total Entries</div>
            </div>
            <div class="stat-item">
                <div class="number">{len(stats['by_repository'])}</div>
                <div class="label">Repositories</div>
            </div>
            <div class="stat-item">
                <div class="number">{len(stats['by_type'])}</div>
                <div class="label">SATD Types</div>
            </div>
        </div>
        
        <div class="controls">
            <input type="text" class="search-box" id="searchBox" placeholder="Search in comments, files, or repositories...">
            
            <div class="filter-group">
                <button class="filter-btn active" onclick="filterByType('ALL')">All</button>
"""
    
    # Add filter buttons for each type
    for satd_type in sorted(stats['by_type'].keys()):
        html += f'                <button class="filter-btn" onclick="filterByType(\'{satd_type}\')">{satd_type} ({stats["by_type"][satd_type]})</button>\n'
    
    html += """
            </div>
        </div>
        
        <div class="entries" id="entriesContainer">
"""
    
    # Add all entries
    for idx, entry in enumerate(kb['entries'], 1):
        satd_type = entry['satd']['type']
        
        # Context preview
        context_preview = '\n'.join(entry['satd']['context_after'][:10])
        if len(entry['satd']['context_after']) > 10:
            context_preview += f"\n... ({len(entry['satd']['context_after']) - 10} more lines)"
        
        html += f"""
            <div class="entry" data-type="{satd_type}" data-repo="{entry['repository']['name']}" data-file="{entry['satd']['filename']}" data-comment="{entry['satd']['comment']}">
                <div class="entry-header">
                    <div>
                        <span class="entry-type">{satd_type}</span>
                    </div>
                    <div class="entry-meta">
                        {entry['satd']['filename']} • Line {entry['satd']['line']} • {entry['repository']['name']}
                    </div>
                </div>
                
                <div class="entry-comment">
                    {entry['satd']['comment']}
                </div>
                
                <div class="entry-context">
                    <span class="context-label">Code Context ({entry['satd']['context_type']}):</span>
                    <pre>{context_preview}</pre>
                </div>
            </div>
"""
    
    html += """
        </div>
        
        <div class="no-results" id="noResults" style="display: none;">
            <h2>No results found</h2>
            <p>Try adjusting your search or filter criteria.</p>
        </div>
        
        <footer>
            <p>Last updated: """ + stats['metadata'].get('last_updated', 'Unknown') + """</p>
        </footer>
    </div>
    
    <script>
        let currentFilter = 'ALL';
        
        // Search functionality
        document.getElementById('searchBox').addEventListener('input', function(e) {
            filterEntries();
        });
        
        function filterByType(type) {
            currentFilter = type;
            
            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            filterEntries();
        }
        
        function filterEntries() {
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            const entries = document.querySelectorAll('.entry');
            let visibleCount = 0;
            
            entries.forEach(entry => {
                const type = entry.getAttribute('data-type');
                const repo = entry.getAttribute('data-repo').toLowerCase();
                const file = entry.getAttribute('data-file').toLowerCase();
                const comment = entry.getAttribute('data-comment').toLowerCase();
                
                const matchesType = currentFilter === 'ALL' || type === currentFilter;
                const matchesSearch = searchTerm === '' || 
                                     comment.includes(searchTerm) || 
                                     repo.includes(searchTerm) || 
                                     file.includes(searchTerm);
                
                if (matchesType && matchesSearch) {
                    entry.style.display = 'block';
                    visibleCount++;
                } else {
                    entry.style.display = 'none';
                }
            });
            
            // Show/hide no results message
            document.getElementById('noResults').style.display = visibleCount === 0 ? 'block' : 'none';
            document.getElementById('entriesContainer').style.display = visibleCount === 0 ? 'none' : 'block';
        }
    </script>
</body>
</html>
"""
    
    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML export created: {output_file}")
    print(f"Open it in your browser to view all {stats['total_entries']} entries!")
    return output_file


if __name__ == "__main__":
    export_to_html()