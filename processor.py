import os
import json
import pandas as pd
from io import StringIO
import tempfile
from unstructured.partition.pdf import partition_pdf

def _structure_table_element(element):
    """
    Parses a table element's HTML representation into a structured dict.
    (Private helper function)
    """
    html_string = element.metadata.text_as_html
    if html_string:
        try:
            df = pd.read_html(io=StringIO(html_string), header=0)[0].fillna("")
            return {
                "headers": df.columns.tolist(),
                "rows": df.values.tolist()
            }
        except Exception as e:
            print(f"Warning: Could not parse HTML for a table. Falling back to text. Error: {e}")
            return {"text": element.text}
    return {"text": element.text}

def _refine_and_link_hierarchy(page_elements):
    """
    Processes a list of elements for a single page to add hierarchy and refine categories.
    (Private helper function)
    """
    refined_content = []
    current_section = "Unknown"

    for el in page_elements:
        element_data = {}
        category = el.category

        if category in ("Title", "Header"):
            element_type = "section_heading"
            current_section = el.text
        elif category == "NarrativeText":
            element_type = "paragraph"
        elif category == "Table":
            element_type = "table"
            element_data["data"] = _structure_table_element(el)
        elif category == "Image":
            element_type = "chart"
        elif category == "ListItem":
            element_type = "list_item"
        else:
            element_type = "paragraph"

        element_data["type"] = element_type
        if "data" not in element_data:
            element_data["text"] = el.text
        
        element_data["section"] = current_section
        element_data["subsection"] = None

        refined_content.append(element_data)
        
    return refined_content

def process_pdf(pdf_path):
    """
    The main public function that orchestrates the full parsing and refinement pipeline.
    This is the only function that app.py will need to import.
    """
    print(f"Starting intelligent parsing with 'unstructured' for {pdf_path}...")
    elements = partition_pdf(pdf_path, strategy="hi_res", infer_table_structure=True)
    
    page_elements = {}
    for el in elements:
        page_num = el.metadata.page_number
        if page_num not in page_elements:
            page_elements[page_num] = []
        page_elements[page_num].append(el)

    final_output = {"document_path": os.path.basename(pdf_path), "pages": []}
    for num, els in sorted(page_elements.items()):
        refined_page_content = _refine_and_link_hierarchy(els)
        final_output["pages"].append({
            "page_number": num,
            "content": refined_page_content
        })
    
    print("Parsing complete.")
    return final_output