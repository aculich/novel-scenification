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
            # Use the truncated sheet name for references in the summary
            sheet_name = base_name[:31]
            
            # First read the CSV to get the sheet name
            df = pd.read_csv(csv_file)
            
            summary_data.append({
                'Sheet': f'=HYPERLINK("#\'{sheet_name}\'!A1","{base_name}")',
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
    
    # After processing all files, create Excel summary
    print("\nCreating Excel summary file...")
    create_excel_summary()
    print("Excel summary file created at: data/tag_counts_summary.xlsx")

if __name__ == "__main__":
    process_all_files()