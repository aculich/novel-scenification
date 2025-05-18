#!/usr/bin/env python
import pandas as pd
import tempfile
import os
import subprocess
import difflib
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime

def extract_from_git(commit_hash, file_path):
    # Create a temporary file
    temp_fd, temp_path = tempfile.mkstemp(suffix=os.path.splitext(file_path)[1])
    os.close(temp_fd)
    
    # Extract the file from git
    cmd = ['git', 'show', f'{commit_hash}:{file_path}']
    with open(temp_path, 'wb') as f:
        subprocess.run(cmd, stdout=f)
    
    return temp_path

def compare_excel_metadata(file1, file2):
    """Compare metadata in Excel files (which are actually ZIP files)"""
    differences = []
    
    # Check creation dates, authors, etc.
    with zipfile.ZipFile(file1) as z1, zipfile.ZipFile(file2) as z2:
        # Compare docProps/core.xml for basic metadata
        if 'docProps/core.xml' in z1.namelist() and 'docProps/core.xml' in z2.namelist():
            with z1.open('docProps/core.xml') as f1, z2.open('docProps/core.xml') as f2:
                root1 = ET.parse(f1).getroot()
                root2 = ET.parse(f2).getroot()
                
                # Extract and compare relevant metadata
                namespaces = {
                    'dc': 'http://purl.org/dc/elements/1.1/',
                    'dcterms': 'http://purl.org/dc/terms/',
                    'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties'
                }
                
                for ns_prefix, ns_uri in namespaces.items():
                    ET.register_namespace(ns_prefix, ns_uri)
                
                # Compare creation date, modification date, author, etc.
                metadata_elements = [
                    ('dc:creator', 'Creator'),
                    ('dc:title', 'Title'),
                    ('dcterms:created', 'Created Date'),
                    ('dcterms:modified', 'Modified Date'),
                    ('cp:lastModifiedBy', 'Last Modified By')
                ]
                
                for xpath, label in metadata_elements:
                    elem1 = root1.find(xpath, namespaces) 
                    elem2 = root2.find(xpath, namespaces)
                    
                    val1 = elem1.text if elem1 is not None else None
                    val2 = elem2.text if elem2 is not None else None
                    
                    if val1 != val2:
                        differences.append(f"{label}: '{val1}' -> '{val2}'")
        
        # Compare the list of files in the ZIP
        files1 = set(z1.namelist())
        files2 = set(z2.namelist())
        
        if files1 != files2:
            added = files2 - files1
            removed = files1 - files2
            
            if added:
                differences.append(f"Added files in Excel ZIP: {sorted(added)}")
            if removed:
                differences.append(f"Removed files in Excel ZIP: {sorted(removed)}")
    
    return differences

def main():
    # Get the current version and the previous version's commit hash
    current_file = 'data/tag_counts_summary.xlsx'
    
    # Find the last commit that modified the file
    cmd = ['git', 'log', '-1', '--format=%H', '--', current_file]
    last_commit = subprocess.check_output(cmd).decode('utf-8').strip()
    
    print(f"Comparing current Excel file with version from commit {last_commit}")
    
    # Extract the previous version from git
    previous_file = extract_from_git(last_commit, current_file)
    
    # Compare file metadata
    print("\nMetadata Comparison:")
    metadata_diffs = compare_excel_metadata(previous_file, current_file)
    if metadata_diffs:
        print("Differences in file metadata:")
        for diff in metadata_diffs:
            print(f"  {diff}")
    else:
        print("No differences in file metadata")
    
    # Load both files
    try:
        print("\nExcel Content Comparison:")
        prev_excel = pd.ExcelFile(previous_file)
        curr_excel = pd.ExcelFile(current_file)
        
        # Compare sheet names
        prev_sheets = set(prev_excel.sheet_names)
        curr_sheets = set(curr_excel.sheet_names)
        
        print(f"\nSheet Comparison:")
        print(f"Previous sheets: {sorted(prev_sheets)}")
        print(f"Current sheets: {sorted(curr_sheets)}")
        
        if prev_sheets != curr_sheets:
            print("\nDifferences in sheet names:")
            print(f"Sheets added: {sorted(curr_sheets - prev_sheets)}")
            print(f"Sheets removed: {sorted(prev_sheets - curr_sheets)}")
        else:
            print("No differences in sheet names")
        
        # Compare content of each sheet that exists in both versions
        common_sheets = prev_sheets.intersection(curr_sheets)
        
        diffs_found = False
        
        for sheet in sorted(common_sheets):
            sheet_diffs = []
            
            prev_df = prev_excel.parse(sheet)
            curr_df = curr_excel.parse(sheet)
            
            # Check shape
            prev_shape = prev_df.shape
            curr_shape = curr_df.shape
            
            if prev_shape != curr_shape:
                sheet_diffs.append(f"Shape difference: Previous {prev_shape} vs Current {curr_shape}")
            
            # Check column names
            prev_cols = set(prev_df.columns)
            curr_cols = set(curr_df.columns)
            
            if prev_cols != curr_cols:
                sheet_diffs.append("Column differences:")
                sheet_diffs.append(f"  Columns added: {sorted(curr_cols - prev_cols)}")
                sheet_diffs.append(f"  Columns removed: {sorted(prev_cols - curr_cols)}")
            
            # For the Summary sheets, check for differences in specific columns
            if sheet.startswith('Summary'):
                # Get common columns
                common_cols = list(prev_cols.intersection(curr_cols))
                
                # Compare row counts
                if len(prev_df) != len(curr_df):
                    sheet_diffs.append(f"Row count: Previous {len(prev_df)} vs Current {len(curr_df)}")
                
                if len(prev_df) > 0 and len(curr_df) > 0:
                    # Check first column with file names
                    sheet_col = prev_df.columns[0]  # Assuming first column has file names
                    
                    # Extract sheet names for comparison
                    prev_names = set(prev_df[sheet_col].astype(str))
                    curr_names = set(curr_df[sheet_col].astype(str))
                    
                    if prev_names != curr_names:
                        sheet_diffs.append(f"Files added: {sorted(curr_names - prev_names)}")
                        sheet_diffs.append(f"Files removed: {sorted(prev_names - curr_names)}")
                    
                    # For files in both versions, check for numeric differences
                    common_names = list(prev_names.intersection(curr_names))
                    numeric_cols = [col for col in common_cols if col != sheet_col]
                    
                    for name in sorted(common_names):
                        prev_row = prev_df[prev_df[sheet_col].astype(str) == name]
                        curr_row = curr_df[curr_df[sheet_col].astype(str) == name]
                        
                        if len(prev_row) == 1 and len(curr_row) == 1:
                            # Compare numeric values
                            row_diffs = []
                            for col in numeric_cols:
                                prev_val = prev_row[col].iloc[0]
                                curr_val = curr_row[col].iloc[0]
                                
                                if pd.notna(prev_val) and pd.notna(curr_val) and prev_val != curr_val:
                                    row_diffs.append((col, prev_val, curr_val))
                            
                            if row_diffs:
                                sheet_diffs.append(f"Differences for {name}:")
                                for col, prev_val, curr_val in row_diffs:
                                    sheet_diffs.append(f"  {col}: {prev_val} -> {curr_val}")
            
            # For data sheets, do a more detailed comparison
            else:
                # Compare the actual data content
                if prev_df.equals(curr_df):
                    pass  # No differences
                else:
                    # Check shape first
                    if prev_shape == curr_shape:
                        # Same shape, check data changes
                        common_cols = list(prev_cols.intersection(curr_cols))
                        
                        # Compare data row by row, column by column
                        total_diffs = 0
                        for i in range(min(len(prev_df), len(curr_df))):
                            for col in common_cols:
                                prev_val = prev_df[col].iloc[i]
                                curr_val = curr_df[col].iloc[i]
                                
                                if pd.notna(prev_val) and pd.notna(curr_val) and prev_val != curr_val:
                                    total_diffs += 1
                                    # Only show the first few differences to avoid cluttering the output
                                    if total_diffs <= 5:
                                        sheet_diffs.append(f"Row {i}, Column '{col}': {prev_val} -> {curr_val}")
                        
                        if total_diffs > 5:
                            sheet_diffs.append(f"...and {total_diffs - 5} more differences")
                        elif total_diffs > 0:
                            sheet_diffs.append(f"Total differences: {total_diffs}")
            
            # Print sheet differences if any were found
            if sheet_diffs:
                diffs_found = True
                print(f"\nDifferences in sheet '{sheet}':")
                for diff in sheet_diffs:
                    print(f"  {diff}")
        
        if not diffs_found:
            print("\nNo content differences found across all sheets")
    
    finally:
        # Clean up the temporary file
        try:
            os.remove(previous_file)
        except:
            pass

if __name__ == "__main__":
    main() 