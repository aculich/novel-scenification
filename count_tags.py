#!/usr/bin/env python

"""
This script uses Python's BeautifulSoup4 library for HTML parsing and the Collections Counter
for efficient hierarchical nested tag and word counting in the following ways:
   - Parses custom-tagged HTML files containing literary text using BeautifulSoup4's HTML parser
   - Processes both standalone tags and hierarchical nested tag relationships
   - Counts occurrences of individual tags (e.g., 'chapmarker', 'sceneaction', 'dia')
   - Analyzes hierarchical nested tag relationships (e.g., 'sceneaction_dia' counts dialogue within scene actions)
   - Calculates word counts within each tag type and hierarchical combination
   - Counts total words and tags in the document
   - Tracks word counts within each tag type
   - Generates compound metrics for hierarchical relationships (e.g., dialogue words within scenes)
"""

from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import Counter
import os
import glob
from openpyxl.styles import Font, Border, Side, Alignment, PatternFill
from urllib.parse import quote

def parse_html_to_csv(html_file, csv_file):
    # Read and parse the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
    
    # Count all tags and their word contents
    tag_counts = Counter(tag.name for tag in soup.find_all())
    tag_word_counts = {}
    compound_tag_counts = Counter()
    compound_word_counts = {}
    
    # Get total word count and total tag count
    all_text = soup.get_text()
    total_words = len([word for word in re.split(r'\s+', all_text.strip()) if word])
    total_tags = len(soup.find_all())
    
    # Count words for each tag type
    for tag_name in tag_counts.keys():
        total_tag_words = 0
        for tag in soup.find_all(tag_name):
            # Get text and split into words, filtering out empty strings
            words = [word for word in re.split(r'\s+', tag.get_text().strip()) if word]
            total_tag_words += len(words)
        tag_word_counts[tag_name] = total_tag_words
    
    # Count hierarchical tag combinations
    for parent_tag in soup.find_all():
        # For each child tag within this parent
        for child_tag in parent_tag.find_all():
            # Create compound tag name
            compound_name = f"{parent_tag.name}_{child_tag.name}".lower()
            compound_tag_counts[compound_name] += 1
            
            # Count words in child tag
            words = [word for word in re.split(r'\s+', child_tag.get_text().strip()) if word]
            if compound_name not in compound_word_counts:
                compound_word_counts[compound_name] = 0
            compound_word_counts[compound_name] += len(words)
    
    # Combine all tags into one dictionary
    all_tags = {}
    # Add regular tags
    for tag in tag_counts:
        all_tags[tag] = {
            'tag_count': tag_counts[tag],
            'word_count': tag_word_counts[tag]
        }
    # Add compound tags
    for tag in compound_tag_counts:
        all_tags[tag] = {
            'tag_count': compound_tag_counts[tag],
            'word_count': compound_word_counts[tag]
        }
    
    # Create sorted list of tags and counts
    sorted_tags = []
    for tag in sorted(all_tags.keys()):
        sorted_tags.append({
            'tag': tag,
            'tag_count': all_tags[tag]['tag_count'],
            'word_count': all_tags[tag]['word_count']
        })
    
    # Add document total at the top
    sorted_tags.insert(0, {
        'tag': 'totaldoctagswords',
        'tag_count': total_tags,
        'word_count': total_words
    })
    
    # Print combined counts
    print("\nTag and Word Counts:")
    print("-" * 50)
    print(f"{'Tag':<30} {'Tag Count':<12} {'Word Count'}")
    print("-" * 50)
    for entry in sorted_tags:
        print(f"{entry['tag']:<30} {entry['tag_count']:<12} {entry['word_count']}")
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(sorted_tags)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(csv_file), exist_ok=True)
    
    # Save to CSV
    df.to_csv(csv_file, index=False)

def create_markdown_summary(summary_data, commit_hash=None):
    """Generate a markdown summary file with links to the input files."""
    if not commit_hash:
        commit_hash = get_current_git_commit()
        
    markdown_content = "# Tag Counts Summary\n\n"
    markdown_content += "| Sheet | Total_Tags | Total_Words | Chapter_Count | SceneAction_Count | SceneAction_Words | SceneDia_Count | SceneDia_Words | Dialogue_Count | Dialogue_Words |\n"
    markdown_content += "|-------|------------|-------------|---------------|------------------|------------------|----------------|----------------|----------------|----------------|\n"
    
    for row in summary_data:
        # Extract the actual name from the HYPERLINK formula
        sheet_name = row['Sheet'].split('"')[3]  # Get the original name from the formula
        # URL encode the filename for the GitHub link
        encoded_filename = quote(f"{sheet_name}.html")
        # Create the GitHub link with commit hash
        if commit_hash:
            github_link = f"[{sheet_name}](https://github.com/aculich/novel-scenification/blob/{commit_hash}/data/input/{encoded_filename})"
        else:
            github_link = f"[{sheet_name}](https://github.com/aculich/novel-scenification/blob/main/data/input/{encoded_filename})"
        
        markdown_content += f"| {github_link} | {row['Total_Tags']} | {row['Total_Words']} | {row['Chapter_Count']} | {row['SceneAction_Count']} | {row['SceneAction_Words']} | {row['SceneDia_Count']} | {row['SceneDia_Words']} | {row['Dialogue_Count']} | {row['Dialogue_Words']} |\n"
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    with open('data/SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def create_excel_summary():
    counts_dir = "data/counts"
    output_file = "data/tag_counts_summary.xlsx"
    
    # Create Excel writer
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # First collect all CSV files and write individual sheets
        csv_files = glob.glob(os.path.join(counts_dir, "*.csv"))
        
        # Process each CSV file first to create all sheets
        for csv_file in csv_files:
            df = pd.read_csv(csv_file)
            
            # Remove rows where both tag_count and word_count are zero
            # Keep 'totaldoctagswords' row regardless
            total_row = df[df['tag'] == 'totaldoctagswords']
            df = df[(df['tag_count'] > 0) | (df['word_count'] > 0) | (df['tag'] == 'totaldoctagswords')]
            
            base_name = os.path.splitext(os.path.basename(csv_file))[0]
            # Truncate sheet name to 31 characters to avoid Excel warnings
            sheet_name = base_name[:31]
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Apply formatting to the sheet
            worksheet = writer.sheets[sheet_name]
            
            # Apply column width adjustment
            for idx, col in enumerate(df.columns):
                # Get the maximum length in the column
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(str(col))
                )
                # Add a little extra space
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
            
            # Apply header formatting
            header_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
            header_font = Font(bold=True)
            thin_border = Border(
                left=Side(style='thin'), 
                right=Side(style='thin'), 
                top=Side(style='thin'), 
                bottom=Side(style='thin')
            )
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.border = thin_border
                cell.alignment = Alignment(horizontal='center')
            
            # Apply borders to data cells
            data_rows = worksheet.max_row
            data_cols = worksheet.max_column
            
            # Create light gray fill for alternating rows
            light_gray = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
            
            for row in range(2, data_rows + 1):
                # Apply alternating row colors
                if row % 2 == 0:  # Even rows
                    for col in range(1, data_cols + 1):
                        worksheet.cell(row=row, column=col).fill = light_gray
                
                for col in range(1, data_cols + 1):
                    cell = worksheet.cell(row=row, column=col)
                    cell.border = thin_border
                    
                    # Center-align numeric columns
                    if col > 1:  # Assuming first column is the tag name
                        cell.alignment = Alignment(horizontal='center')
            
            # Freeze the header row
            worksheet.freeze_panes = "A2"
        
        # Now create summary data with references
        summary_data = []
        for csv_file in csv_files:
            base_name = os.path.splitext(os.path.basename(csv_file))[0]
            # Use the truncated sheet name for Excel references, but keep full name for display
            sheet_name = base_name[:31]
            
            # First read the CSV to get the sheet name
            df = pd.read_csv(csv_file)
            
            summary_data.append({
                'Sheet': f'=HYPERLINK("#\'{sheet_name}\'!A1","{base_name}")',  # Keep full name in display
                'Total_Tags': df[df['tag'] == 'totaldoctagswords']['tag_count'].iloc[0],
                'Total_Words': df[df['tag'] == 'totaldoctagswords']['word_count'].iloc[0],
                'Chapter_Count': df[df['tag'] == 'chapmarker']['tag_count'].sum() if 'chapmarker' in df['tag'].values else 0,
                'SceneAction_Count': df[df['tag'] == 'sceneaction']['tag_count'].sum() if 'sceneaction' in df['tag'].values else 0,
                'SceneAction_Words': df[df['tag'] == 'sceneaction']['word_count'].sum() if 'sceneaction' in df['tag'].values else 0,
                'SceneDia_Count': df[df['tag'] == 'scenedia']['tag_count'].sum() if 'scenedia' in df['tag'].values else 0,
                'SceneDia_Words': df[df['tag'] == 'scenedia']['word_count'].sum() if 'scenedia' in df['tag'].values else 0,
                'Dialogue_Count': df[df['tag'] == 'dia']['tag_count'].sum() if 'dia' in df['tag'].values else 0,
                'Dialogue_Words': df[df['tag'] == 'dia']['word_count'].sum() if 'dia' in df['tag'].values else 0
            })
        
        # Create and write summary sheet
        summary_df = pd.DataFrame(summary_data)
        
        # Remove rows with all zero counts (excluding the 'Sheet' column)
        numeric_columns = summary_df.columns.difference(['Sheet'])
        mask = summary_df[numeric_columns].sum(axis=1) > 0
        summary_df = summary_df[mask]
        
        # Generate markdown summary before writing to Excel
        commit_hash = get_current_git_commit()
        create_markdown_summary(summary_data, commit_hash)
        
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Apply formatting to the summary sheet
        worksheet = writer.sheets['Summary']
        
        # Apply column width adjustment        
        for idx, col in enumerate(summary_df.columns):
            # For the Sheet column, include the base name length and formula overhead
            if idx == 0:
                max_length = max(
                    max(len(str(val)) for val in summary_df[col].str.extract(r'"(.*?)"')[0]),  # Extract sheet names from HYPERLINK formula
                    len(col)
                )
            else:
                # For numeric columns, get max length of the actual values
                max_length = max(
                    max(len(str(val)) for val in summary_df[col]),
                    len(col)
                )
            # Add extra space for readability
            worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
        
        # Apply header formatting
        header_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
        header_font = Font(bold=True)
        thin_border = Border(
            left=Side(style='thin'), 
            right=Side(style='thin'), 
            top=Side(style='thin'), 
            bottom=Side(style='thin')
        )
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.border = thin_border
            cell.alignment = Alignment(horizontal='center')
        
        # Apply borders to data cells
        data_rows = worksheet.max_row
        data_cols = worksheet.max_column
        
        # Create light gray fill for alternating rows
        light_gray = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        
        for row in range(2, data_rows + 1):
            # Apply alternating row colors
            if row % 2 == 0:  # Even rows
                for col in range(1, data_cols + 1):
                    worksheet.cell(row=row, column=col).fill = light_gray
            
            for col in range(1, data_cols + 1):
                cell = worksheet.cell(row=row, column=col)
                cell.border = thin_border
                
                # Center-align numeric columns
                if col > 1:  # Assuming first column is the sheet name with hyperlink
                    cell.alignment = Alignment(horizontal='center')
        
        # Freeze the header row
        worksheet.freeze_panes = "A2"
        
        # Move Summary sheet to the first position
        workbook = writer.book
        workbook._sheets.insert(0, workbook._sheets.pop(workbook._sheets.index(worksheet)))

def get_current_git_commit():
    """Get the current git commit hash."""
    import subprocess
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def analyze_scene_complexity(scene_tag):
    """Analyze the complexity of a scene based on its internal structure."""
    # Count unique tag types
    unique_tags = set(tag.name for tag in scene_tag.find_all())
    # Count total nested tags
    total_tags = len(scene_tag.find_all())
    # Count words
    words = len([w for w in re.split(r'\s+', scene_tag.get_text().strip()) if w])
    # Calculate complexity score (can be adjusted)
    return {
        'score': len(unique_tags) * 2 + total_tags + words/100,
        'unique_tags': unique_tags,
        'total_tags': total_tags,
        'words': words,
        'text': scene_tag.prettify()
    }

def find_interesting_excerpts(scene_tag, scene_type):
    """Find interesting excerpts from a scene including opening, transitions, rich dialog sections, and ending."""
    excerpts = []
    
    # Helper function to truncate text to a reasonable length while preserving tag structure
    def truncate_html(html_text, max_words=175):  # Increased from 50 to 175 to match screenshot example
        soup = BeautifulSoup(html_text, 'html.parser')
        words = soup.get_text().split()
        if len(words) <= max_words:
            return html_text
        
        # Find a good breakpoint near max_words
        text = ' '.join(words[:max_words])
        # Find the last complete sentence if possible
        last_period = text.rfind('.')
        if last_period > len(text) * 0.6:  # If we can find a period in the latter half
            text = text[:last_period+1]
        return html_text[:html_text.find(text) + len(text)] + "..."
    
    # Get the full scene text
    scene_text = str(scene_tag)
    
    # Find rich dialog sections (sections with multiple tag types and interesting content)
    dialog_sections = []
    for dia in scene_tag.find_all('dia', recursive=False):
        # Look at the immediate context
        context = dia
        # Try to expand context to include nearby dialog if available
        parent = dia.parent
        if parent and parent != scene_tag:  # Only expand if we have a non-root parent
            siblings = list(parent.find_all('dia', recursive=False))
            if len(siblings) > 1:
                dia_index = siblings.index(dia)
                start_idx = max(0, dia_index - 1)
                end_idx = min(len(siblings), dia_index + 2)
                context = parent
                # Only keep content between the dialogs we want
                for child in list(context.children):
                    if isinstance(child, BeautifulSoup.Tag) and child.name == 'dia' and child not in siblings[start_idx:end_idx]:
                        child.decompose()
        
        tags_in_context = set(tag.name for tag in context.find_all())
        
        # Calculate richness score based on:
        # - Number of unique tag types
        # - Presence of interesting tags (m, chnoneameintro, trigger)
        # - Length of the dialog (prefer medium-length)
        interesting_tags = {'m', 'chnoneameintro', 'trigger'}
        score = (
            len(tags_in_context) * 2 +  # Weight for tag variety
            len(tags_in_context & interesting_tags) * 3 +  # Extra weight for interesting tags
            min(len(context.get_text().split()) / 50, 3)  # Length score, max 3 points
        )
        
        if score >= 4:  # Only keep sections with good scores
            dialog_sections.append({
                'text': str(context),
                'score': score,
                'tag_count': len(tags_in_context)
            })
    
    if dialog_sections:
        # Sort by score and take the top ones
        dialog_sections.sort(key=lambda x: x['score'], reverse=True)
        for section in dialog_sections[:2]:  # Take up to 2 best sections
            # Truncate to reasonable length
            text = truncate_html(section['text'])
            if len(text) > 150:  # Increased minimum length to ensure rich content
                excerpts.append({
                    'type': 'rich_dialog',
                    'text': text,
                    'description': 'Rich Dialog Section with Multiple Tag Types'
                })
    
    # Find transitions with triggers (if any)
    triggers = scene_tag.find_all('trigger')
    if triggers:
        # Get context around the most interesting trigger
        trigger_contexts = []
        for trigger in triggers:
            context = trigger.parent
            tags_in_context = set(tag.name for tag in context.find_all())
            if len(tags_in_context) >= 2:  # Only if there are multiple tag types
                trigger_contexts.append({
                    'text': str(context),
                    'tag_count': len(tags_in_context)
                })
        
        if trigger_contexts:
            # Take the richest trigger context
            trigger_contexts.sort(key=lambda x: x['tag_count'], reverse=True)
            text = truncate_html(trigger_contexts[0]['text'])
            if len(text) > 50:
                excerpts.append({
                    'type': 'transition',
                    'text': text,
                    'description': 'Scene Transition'
                })
    
    # Only include opening/ending if they have interesting tags
    def is_interesting_section(text):
        soup = BeautifulSoup(text, 'html.parser')
        tags = set(tag.name for tag in soup.find_all())
        return len(tags) >= 2  # At least 2 different tag types
    
    # Check opening
    opening_match = re.search(r'<' + scene_type + r'[^>]*>.*?(<.*?</.*?>)', scene_text, re.DOTALL)
    if opening_match and is_interesting_section(opening_match.group(0)):
        text = truncate_html(opening_match.group(0))
        if len(text) > 50:
            excerpts.append({
                'type': 'opening',
                'text': text,
                'description': 'Scene Opening'
            })
    
    # Check ending
    ending_match = re.search(r'(<.*?</.*?>)[^<]*</' + scene_type + '>', scene_text, re.DOTALL)
    if ending_match and is_interesting_section(ending_match.group(0)):
        text = truncate_html(ending_match.group(0))
        if len(text) > 50:
            excerpts.append({
                'type': 'ending',
                'text': text,
                'description': 'Scene Ending'
            })
    
    return excerpts

def find_rich_samples(html_file):
    """Find rich samples from a given HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.readlines()
        soup = BeautifulSoup(''.join(content), 'html.parser')
    
    samples = []
    # Look for SceneAction and SceneDia tags
    for scene_type in ['sceneaction', 'scenedia']:
        scenes = soup.find_all(scene_type, recursive=False)  # Only get top-level scenes
        if not scenes:
            continue
            
        # Analyze complexity of each scene
        analyzed_scenes = []
        for scene in scenes:
            analysis = analyze_scene_complexity(scene)
            
            # Get the raw scene text and clean it up
            scene_text = str(scene)
            opening_tag = f"<{scene_type}"
            closing_tag = f"</{scene_type}>"
            
            # Find the scene in the original content
            start_line = None
            end_line = None
            
            # Look for opening tag
            for i, line in enumerate(content, 1):
                if opening_tag.lower() in line.lower():
                    start_line = i
                    break
            
            if start_line is not None:
                # Look for closing tag after start line
                for i, line in enumerate(content[start_line-1:], start_line):
                    if closing_tag.lower() in line.lower():
                        end_line = i
                        break
            
            # Only include scenes where we found both start and end lines
            if start_line is not None and end_line is not None:
                analysis['start_line'] = start_line
                analysis['end_line'] = end_line
                analysis['scene_type'] = scene_type
                analysis['excerpts'] = find_interesting_excerpts(scene, scene_type)
                analyzed_scenes.append(analysis)
        
        # Sort by complexity score and take the top one
        if analyzed_scenes:
            analyzed_scenes.sort(key=lambda x: x['score'], reverse=True)
            samples.append(analyzed_scenes[0])
    
    return samples

def create_samples_markdown(commit_hash=None):
    """Generate a markdown file with rich samples from each input file."""
    if not commit_hash:
        commit_hash = get_current_git_commit()
    
    markdown_content = "# Scene Samples\n\n"
    markdown_content += "This document contains particularly rich examples of scene markup from each text, "
    markdown_content += "showing complex interactions between different types of scenes and their components. "
    markdown_content += "For each scene, we show interesting excerpts including openings, transitions, rich dialog sections, and endings.\n\n"
    
    input_dir = "data/input"
    html_files = glob.glob(os.path.join(input_dir, "*.html"))
    
    for html_file in html_files:
        base_name = os.path.basename(html_file)
        markdown_content += f"## {base_name}\n\n"
        
        samples = find_rich_samples(html_file)
        if not samples:
            markdown_content += "No complex scenes found in this file.\n\n"
            continue
        
        for sample in samples:
            # Create the GitHub permalink
            encoded_filename = quote(base_name)
            if commit_hash:
                file_link = f"https://github.com/aculich/novel-scenification/blob/{commit_hash}/data/input/{encoded_filename}#L{sample['start_line']}-L{sample['end_line']}"
            else:
                file_link = f"https://github.com/aculich/novel-scenification/blob/main/data/input/{encoded_filename}#L{sample['start_line']}-L{sample['end_line']}"
            
            markdown_content += f"### Complex {sample['scene_type'].title()} (Lines {sample['start_line']}-{sample['end_line']})\n\n"
            markdown_content += f"[View full scene on GitHub]({file_link})\n\n"
            markdown_content += f"**Complexity Metrics:**\n"
            markdown_content += f"- Unique tag types: {len(sample['unique_tags'])}\n"
            markdown_content += f"- Total nested tags: {sample['total_tags']}\n"
            markdown_content += f"- Word count: {sample['words']}\n"
            markdown_content += f"- Tag types present: {', '.join(sorted(sample['unique_tags']))}\n\n"
            
            # Add excerpts
            markdown_content += "**Interesting Excerpts:**\n\n"
            for excerpt in sample['excerpts']:
                markdown_content += f"*{excerpt['description']}:*\n"
                markdown_content += "```html\n"
                markdown_content += excerpt['text']
                markdown_content += "\n```\n\n"
    
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    with open('data/SAMPLES.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def create_readme():
    """Generate README.md from template and include summaries."""
    try:
        # Try to read existing README.md
        with open('README.md', 'r', encoding='utf-8') as f:
            existing_content = f.read()
            
        # Split at "## Tag Counts Summary" if it exists
        parts = existing_content.split("## Tag Counts Summary")
        template_content = parts[0].rstrip()  # Use everything before this section
    except FileNotFoundError:
        # If README.md doesn't exist, start with empty content
        template_content = ""
    
    # Add links to full files
    summary_section = "\n\n## Tag Counts Summary\n\n"
    summary_section += "[View complete tag counts summary](data/SUMMARY.md)\n\n"
    
    # Track which files we'll show samples from
    sample_files = set()
    with open('data/SAMPLES.md', 'r', encoding='utf-8') as f:
        samples_content = f.read()
        sections = samples_content.split('\n## ')
        for section in sections[1:]:  # Skip intro
            if 'Complex Scene' in section:
                # Extract filename from the section, removing .html extension if present
                filename = section.split('\n')[0].strip()
                if filename.endswith('.html'):
                    filename = filename[:-5]
                if filename:
                    sample_files.add(filename)
    
    # Add excerpt from SUMMARY.md, but only for files we're showing samples from
    with open('data/SUMMARY.md', 'r', encoding='utf-8') as f:
        summary_content = f.read()
        summary_lines = summary_content.split('\n')
        # Find the table header and separator lines
        table_start = -1
        for i, line in enumerate(summary_lines):
            if line.startswith('| Sheet | Total_Tags'):
                table_start = i
                break
        
        if table_start >= 0 and len(summary_lines) >= table_start + 2:
            # Add the table header and separator
            summary_section += summary_lines[table_start] + "\n"  # Header
            summary_section += summary_lines[table_start + 1] + "\n"  # Separator
            
            # Add rows only for files we're showing samples from
            for line in summary_lines[table_start + 2:]:  # Start after header and separator
                if not line.strip():  # Skip empty lines
                    continue
                for sample_file in sample_files:
                    # Extract the filename from the markdown link format [filename](url)
                    match = re.search(r'\[(.*?)\]', line)
                    if match and match.group(1) == sample_file:
                        summary_section += line + "\n"
            summary_section += "\n[View complete tag counts summary](data/SUMMARY.md)\n\n"
    
    # Add excerpt from SAMPLES.md
    samples_section = "\n## Scene Samples\n\n"
    samples_section += "[View complete samples analysis](data/SAMPLES.md)\n\n"
    
    with open('data/SAMPLES.md', 'r', encoding='utf-8') as f:
        samples_content = f.read()
        # Split by sections and take introduction plus first two samples
        sections = samples_content.split('\n## ')
        if len(sections) > 0:
            intro = sections[0]
            samples = []
            count = 0
            for section in sections[1:]:
                if count < 2 and 'Complex Scene' in section:
                    samples.append(section)
                    count += 1
            
            samples_section += intro + "\n"
            if samples:
                samples_section += "## " + "\n## ".join(samples) + "\n...\n\n"
                samples_section += "[View all scene samples](data/SAMPLES.md)\n"
    
    # Combine everything
    readme_content = template_content + summary_section + samples_section
    
    # Write the README
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)

def process_all_files():
    input_dir = "data/input"
    output_dir = "data/counts"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all HTML files in input directory
    html_files = glob.glob(os.path.join(input_dir, "*.html"))
    
    for html_file in html_files:
        # Generate output filename by replacing directory and extension
        base_name = os.path.basename(html_file)
        csv_name = os.path.splitext(base_name)[0] + ".csv"
        csv_file = os.path.join(output_dir, csv_name)
        
        print(f"\nProcessing: {base_name}")
        print("=" * 60)
        
        parse_html_to_csv(html_file, csv_file)
        print(f"Output saved to: {csv_file}\n")
    
    # After processing all files, create Excel summary and samples
    print("\nCreating Excel summary file...")
    create_excel_summary()
    print("Excel summary file created at: data/tag_counts_summary.xlsx")
    
    print("\nGenerating rich samples documentation...")
    create_samples_markdown()
    print("Rich samples documentation created at: data/SAMPLES.md")
    
    print("\nGenerating README.md...")
    create_readme()
    print("README.md generated from template with summaries")

if __name__ == "__main__":
    process_all_files()