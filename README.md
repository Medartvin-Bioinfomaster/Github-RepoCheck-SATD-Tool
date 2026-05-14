# Github-RepoCheck-SATD-Tool
# SATD Detection Tool for R

A practical Self-Admitted Technical Debt (SATD) detection tool designed specifically for R researchers and bioinformatics developers.

## Overview

Research software quality affects scientific validity, yet R developers lack tools to identify and manage technical debt in their code. This tool addresses that gap by providing accessible SATD detection, a curated knowledge base of real examples, and AI-powered similarity search—all designed for researchers without formal software engineering training.

## Features

###  SATD Detection
- Keyword-based detection of technical debt markers (TODO, FIXME, HACK, etc.)
- AI-powered context extraction to understand what code is affected
- Perfect recall (1.0) while maintaining acceptable precision (0.8)
- Handles non-standard syntax like "TO DO" with spaces

###  Accessible Metrics & Reporting
- **SATD Count**: Number of debt instances per 1,000 lines of code
- **Compromised Lines**: Proportion of code affected by technical debt
- **Risk Classification**: Color-coded Low/Medium/High risk levels
- HTML reports with visual indicators—no SE background required

###  Curated Knowledge Base
- 179 SATD instances from established R repositories
- Examples from Bioconductor (GenomicRanges, IRanges, etc.) and tidyverse
- Real code context showing why debt was admitted
- Searchable and browsable interface

###  AI-Powered Similarity Search
- Check code snippets against known SATD patterns
- Identify potential debt in borrowed or reused code
- Semantic matching using code embeddings
- Preventive quality check before incorporating external code
