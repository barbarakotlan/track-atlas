"""
Load documents from the knowledge base directory
"""
from docx import Document
from pathlib import Path
from pypdf import PdfReader
import re
import unicodedata

def scan_directory(directory_path):
    """Scans the given directory and returns a list of file paths for all files in the directory and its subdirectories.
    Args:
        directory_path (Path): The path to the directory to scan.
    Returns:
        list: All files found recursively in the directory and its subdirectories.
    """
    file_paths = []
    for item in directory_path.iterdir():
        if item.is_file():
            file_paths.append(item)
        elif item.is_dir():
            file_paths.extend(scan_directory(item))
    return file_paths

def is_supported_file(file_path):
    """Checks if the file is a supported document type (PDF, DOCX, or HTML).
    Args:
        file_path (Path): The path to the file to check.
    Returns:
        bool: True if the file is a supported document type, False otherwise.
    """
    supported_extensions = ['.pdf', '.docx', '.html']
    return file_path.suffix.lower() in supported_extensions

def load_document(file_path):
    """Loads the content of a document based on its file type.
    Args:
        file_path (Path): The path to the file to load.
    Returns:
        str: The content of the loaded document.
    """
    if file_path.suffix.lower() == '.pdf':
        return load_pdf(file_path)
    elif file_path.suffix.lower() == '.docx':
        return load_docx(file_path)
    elif file_path.suffix.lower() == '.html':
        return load_html(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")

def load_pdf(file_path):
    """Loads the content of a PDF document.
    Args:
        file_path (Path): The path to the PDF file to load.
    Returns:
        str: The text content of the PDF document.
    """
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def load_docx(file_path):
    """Loads the content of a DOCX document.
    Args:
        file_path (Path): The path to the DOCX file to load.
    Returns:
        str: The text content of the DOCX document."""
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def load_html(file_path):
    """Loads the content of an HTML file.
    Args:
        file_path (Path): The path to the HTML file to load.
    Returns:
        str: The text content of the HTML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()    

def clean_text(text):
    """Cleans the text by normalizing unicode characters, removing extra whitespace, and stripping leading/trailing whitespace.
    Args:
        text (str): The text to clean.
    Returns:
        str: The cleaned text. 
    """
    text = unicodedata.normalize("NFKD", text)
    cleaned_lines = []
    for line in text.splitlines():
        line = line.strip()
        line = re.sub(r'[ \t]+',' ', line)
        if line:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def extract_metadata(file_path):
    """Extracts metadata from a file.
    Args:
        file_path (Path): The path to the file to extract metadata from.
    Returns:
        dict: A dictionary containing metadata about the file."""
    metadata = {
        "file_name": file_path.name,
        "file_path": str(file_path),
        "file_size": file_path.stat().st_size,
        "file_type": file_path.suffix.lower(),
        "last_modified": file_path.stat().st_mtime,
    }
    return metadata

def create_document(text, metadata):
    """Creates a document object with the given text and metadata.
    Args:
        text (str): The text content of the document.
        metadata (dict): A dictionary containing metadata about the document.
    Returns:
        dict: A dictionary representing the document with its text and metadata.
    """
    return {
        "text": text,
        "metadata": metadata
    }

def load_all_documents(directory):
    """Loads all supported documents from the given directory and its subdirectories.
    Args:
        directory (Path): The path to the directory to load documents from.
    Returns:
        list: A list of document objects, each containing text and metadata."""
    file_paths = scan_directory(directory)
    documents = []
    for file_path in file_paths:
        if is_supported_file(file_path):
            text = load_document(file_path)
            text = clean_text(text)
            metadata = extract_metadata(file_path)
            document = create_document(text, metadata)
            documents.append(document)
    return documents
