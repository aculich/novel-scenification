import pandas as pd
import re

# Read the keep_for_summary_tags.tsv file
with open('keep_for_summary_tags.tsv', 'r') as f:
    tags_to_match = [line.strip() for line in f.readlines()]

# Read the Excel file
xlsx = pd.read_excel('data/tag_counts_summary.xlsx', sheet_name='Summary All Tags')

# Get all column headers and remove the _Count and _Words suffixes
column_headers = []
for col in xlsx.columns:
    if col.endswith('_Count'):
        column_headers.append(col[:-6])  # Keep original case for output

# Find matches for each tag
summary_matches = []
detailed_matches = []

for tag in tags_to_match:
    # Skip empty lines
    if not tag.strip():
        continue
        
    # Handle wildcard (*) in tags
    if '*' in tag:
        # Convert glob pattern to regex pattern
        regex_pattern = "^" + tag.lower().replace('*', '.*') + "$"
        pattern = re.compile(regex_pattern)
        
        # For wildcard patterns, find all matches
        matching_cols = []
        for col in column_headers:
            if pattern.match(col.lower()):
                matching_cols.append(col)
                detailed_matches.append([tag, col])  # Add each individual match
                
        # For the summary file
        if len(matching_cols) > 10:
            base_pattern = tag.replace('*', '')
            summary_matches.append([tag, f"Found {len(matching_cols)} matches starting with '{base_pattern}'"])
        else:
            # For patterns with fewer matches, list them all
            summary_matches.append([tag, ", ".join(matching_cols[:5]) + ("..." if len(matching_cols) > 5 else "")])
    else:
        # Direct match (case-insensitive)
        matched = False
        for col in column_headers:
            if col.lower() == tag.lower():
                summary_matches.append([tag, col])
                detailed_matches.append([tag, col])
                matched = True
                break
        
        # If no match found, note it
        if not matched:
            summary_matches.append([tag, "No direct match found"])

# Write the summary results to a TSV file
with open('tag_matches_summary.tsv', 'w') as f:
    f.write("Original_Tag\tMatched_Column\n")
    for match in summary_matches:
        f.write(f"{match[0]}\t{match[1]}\n")

# Write the detailed results to a TSV file
with open('tag_matches_detailed.tsv', 'w') as f:
    f.write("Original_Tag\tMatched_Column\n")
    for match in detailed_matches:
        f.write(f"{match[0]}\t{match[1]}\n")

print(f"Successfully created tag_matches_summary.tsv with {len(summary_matches)} entries")
print(f"Successfully created tag_matches_detailed.tsv with {len(detailed_matches)} entries") 