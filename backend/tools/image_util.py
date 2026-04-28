import os
import io
import uuid
import base64
import requests
import tempfile
from pathlib import Path

def path_to_b64(image_file):
    try:
        with open(image_file, "rb") as img_file:
            image_data = img_file.read()
            base64_image = base64.b64encode(image_data).decode("utf-8")
            return base64_image
    except Exception as e:
        print("ERROR", f"Error reading image {image_file}: {e}")
        return {"error": f"Failed to read image {image_file}: {str(e)}"}

def path_to_base64url(image_file):
    file_ext = Path(image_file).suffix.lower()
    if file_ext in [".jpg", ".jpeg"]:
        media_type = "image/jpeg"
    elif file_ext == ".png":
        media_type = "image/png"
    elif file_ext == ".gif":
        media_type = "image/gif"
    elif file_ext == ".webp":
        media_type = "image/webp"
    else:
        media_type = "image/jpeg"
    return f"data:{media_type};base64,{path_to_b64(image_file)}"

def paths_to_b64urls(image_files):
    # Convert images to base64
    base64_images = []
    for img_path in image_files:
        base64_images.append(path_to_base64url(img_path))
    return base64_images

def url_to_base64(img_url):
    # Download the image to a temp location
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f"tmp_{uuid.uuid4()}.png")

    print(f"Downloading generated image from: {img_url}")
    img_data = requests.get(img_url).content
    
    with open(temp_path, "wb") as f:
        f.write(img_data)
    
    # Convert to base64
    with open(temp_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode("utf-8")
    
    # Cleanup
    if os.path.exists(temp_path):
        os.remove(temp_path)
        print(f"Temporary file {temp_path} deleted.")
        
    return base64_image

def read_image_files(input_folder):
    # Get all images from folder
    image_files = []
    if os.path.exists(input_folder):
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        for file in os.listdir(input_folder):
            if Path(file).suffix.lower() in image_extensions:
                full_path = os.path.join(input_folder, file)
                image_files.append(full_path)
    else:
        return {"error": f"Folder not found: {input_folder}"}

    if not image_files:
        return {
            "error": f"No images found in {input_folder}. Checked extensions: jpg, jpeg, png, gif, webp"
        }

    print("INFO", f"Total images found: {len(image_files)}")
    return image_files

def map_image_to_openai(image_path):
    return [
        {"type": "text", "text": f"Next image: {Path(image_path).name}"},
        {"type": "image_url", "image_url": {"url": path_to_base64url(image_path)}}
    ]

def get_file_object(base64_string):
    # Convert base64 string to file-like object
    
    
    # Remove data URL prefix if present
    if base64_string.startswith('data:'):
        base64_data = base64_string.split(',')[1]
    else:
        base64_data = base64_string
        
    # Decode base64 and create file-like object
    image_bytes = base64.b64decode(base64_data)
    image_file = io.BytesIO(image_bytes)
    
    return image_file

def path_to_file_object(image_path):
    # Convert path string to file-like object
    with open(image_path, "rb") as f:
        image_file = io.BytesIO(f.read())
    
    return image_file

def save_to_temp(file_content: bytes, folder: str, file_extension: str = "pdf"):
    """
    Save file content to temporary file with a prefix folder in temp directory
    
    Args:
        file_content: The file content as bytes
        folder: The prefix folder name within temp directory
        file_extension: File extension (default: "pdf")
    
    Returns:
        Full path to the temporary file
    """
    # Create the prefix folder in temp directory
    temp_dir = tempfile.mkdtemp(prefix=folder)
    
    # Create temporary file with the specified extension
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, 
        suffix=f".{file_extension}",
        dir=temp_dir
    )
    
    # Write file content
    temp_file.write(file_content)
    temp_file.flush()
    temp_file.close()
    
    return temp_file.name