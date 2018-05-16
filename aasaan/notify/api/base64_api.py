import base64
import os.path as path
from tempfile import mkstemp

def get_base64_string(filename="", foldername="",
                        return_tempfile=False):
    if not filename:
        return False 

    try:
        full_file_name = path.join(foldername, filename)
        binfile = open(full_file_name, "rb")
        binfile_content = binfile.read()
        binfile_base64_content = base64.b64encode(binfile_content)
        binfile_base64_content_decoded = binfile_base64_content.decode()
        binfile.close()
    except FileNotFoundError:
        return False

    if not return_tempfile:
        return binfile_base64_content_decoded

    tempfile_name = mkstemp()[-1]

    tempfile = open(tempfile_name, "w")
    tempfile.write(binfile_base64_content_decoded)
    tempfile.close()

    return tempfile_name



    