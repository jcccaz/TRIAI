import base64
import io
from PyPDF2 import PdfReader
from PIL import Image

MAX_TEXT_LENGTH = 100000  # Limit context to avoid hitting limits too fast

def process_file(file):
    """
    Process an uploaded file and return its type and content/context.
    Returns: (file_type, content, visual_data)
    
    file_type: 'text' or 'image'
    content: Extracted text context (for all models)
    visual_data: Base64 string (for vision models) or None
    """
    filename = file.filename.lower()
    
    # Handle Images
    if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
        try:
            # Read and compress if necessary
            image = Image.open(file)
            
            # Convert to RGB if needed (e.g. for PNG with alpha)
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
                
            # Resize if too large (standardize to max 1024px dimension)
            if max(image.size) > 1024:
                image.thumbnail((1024, 1024))
                
            # Convert to base64
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=85)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            return 'image', f"[User uploaded an image: {filename}]", img_str
        except Exception as e:
            return 'error', f"Error processing image: {str(e)}", None

    # Handle PDFs
    elif filename.endswith('.pdf'):
        try:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            # Truncate if huge
            if len(text) > MAX_TEXT_LENGTH:
                text = text[:MAX_TEXT_LENGTH] + "\n...[truncated]..."
                
            return 'text', f"--- START OF FILE: {filename} ---\n{text}\n--- END OF FILE ---", None
        except Exception as e:
            return 'error', f"Error reading PDF: {str(e)}", None
            
    # Handle Text Files
    elif filename.endswith(('.txt', '.md', '.csv', '.json', '.py', '.js', '.html', '.css')):
        try:
            text = file.read().decode('utf-8', errors='ignore')
             # Truncate if huge
            if len(text) > MAX_TEXT_LENGTH:
                text = text[:MAX_TEXT_LENGTH] + "\n...[truncated]..."
                
            return 'text', f"--- START OF FILE: {filename} ---\n{text}\n--- END OF FILE ---", None
        except Exception as e:
            return 'error', f"Error reading text file: {str(e)}", None
            
    return 'error', "Unsupported file type", None
