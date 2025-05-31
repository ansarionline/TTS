import gdown
file_id = "1pNLJXwybicBY8-xZHNKhxXN3m8UH3yU2"
url = f"https://drive.google.com/uc?id={file_id}"
output = "downloaded_file.zip"
gdown.download(url, output, quiet=False)
import shutil
shutil.unpack_archive("downloaded_file.zip", "backend")
import os
os.remove('downloaded_file.zip')