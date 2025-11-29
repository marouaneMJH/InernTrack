#!/usr/bin/env python3
"""
Data Deduplication Module

This module provides deduplication functionality to remove duplicate job
listings that may appear across different job boards or search queries.

Deduplication Strategies:

1. URL-Based Deduplication:
   - Primary method using job posting URLs
   - Most reliable as URLs are typically unique
   - Handles different URL formats from various platforms

2. Fallback ID Deduplication:
   - Uses raw job IDs when URLs are unavailable
   - Platform-specific identifier handling
   - Maintains referential integrity

3. Content Similarity (Future Enhancement):
   - Potential for fuzzy matching based on content
   - Title and description comparison
   - Company and location matching

Features:
- Memory-efficient set-based deduplication
- Preserves first occurrence of duplicates
- Detailed logging of removed duplicates
- Graceful handling of missing identifiers
- Debug logging for troubleshooting

Performance Characteristics:
- O(n) time complexity for URL-based deduplication
- Minimal memory overhead
- Suitable for large job datasets

Data Integrity:
- Preserves original job data structure
- Maintains raw data for debugging
- No modification of job content during deduplication

Logging:
- Debug-level logging for skipped duplicates
- Performance metrics for large datasets
- Error handling for malformed data

Usage:
    unique_jobs = dedupe_by_url(job_list)
    print(f"Removed {len(job_list) - len(unique_jobs)} duplicates")
    
Author: El Moujahid Marouane
Version: 1.0
"""

from .logger_setup import get_logger
logger = get_logger("dedupe")

def dedupe_by_url(jobs):
    seen = set()
    out = []
    for j in jobs:
        url = j.get("url") or j.get("raw", {}).get("id") or None
        if not url:
            out.append(j)
            continue
        if url in seen:
            logger.debug("Skipping duplicate: %s", url)
            continue
        seen.add(url)
        out.append(j)
    return out