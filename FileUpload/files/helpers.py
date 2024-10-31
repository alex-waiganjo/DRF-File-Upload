# Accept Excel, Pdf
import pandas as pd
import PyPDF2
import numpy as np
import re

def sanitize_data(data):
    """Recursively replace inf, -inf, and NaN with None in lists or dictionaries."""
    if isinstance(data, float):
        # Replace NaN and infinite values with None
        if np.isnan(data) or data == float('inf') or data == float('-inf'):
            return None
    elif isinstance(data, dict):
        return {key: sanitize_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    return data

# Handle Excel file reading and extraction
def parse_excel(file):
    df = pd.read_excel(file)
    
    # Replace infinite values with None
    df.replace([np.inf, -np.inf], None, inplace=True)
    
    # Convert DataFrame to a dictionary
    data = df.to_dict(orient='list')
    sanitized_data = sanitize_data(data)
    return sanitized_data


# Handle PDF reading and extraction
# def parse_pdf(file):
#     pdf_reader = PyPDF2.PdfReader(file)
#     text = ""
#     for page in pdf_reader.pages:
#         text += page.extract_text()
#     return {"content": text} 


def parse_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""

    # Extract text from each page
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # Split text by lines to identify rows in the table
    lines = text.strip().split('\n')
    
    # Attempt to identify headers (assuming headers are the first line)
    # For example, header line might be something like: "Name Age Department Position"
    headers = re.split(r'\s{2,}', lines[0])  # Split headers by multiple spaces
    
    # Initialize list for employee data
    data_list = []
    
    # Iterate over lines after header row
    for line in lines[1:]:
        # Split each line based on multiple spaces (assuming cells are separated by spaces)
        cells = re.split(r'\s{2,}', line.strip())
        
        # Only proceed if cells match the number of headers
        if len(cells) == len(headers):
            # Dynamically map each cell to the corresponding header
            row_data = {headers[i].strip().lower(): cells[i].strip() for i in range(len(headers))}
            data_list.append(row_data)
    
    # Return data in JSON-like structure
    return {"data": data_list}
