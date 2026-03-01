import hashlib

def hash_file(file_obj) -> str:
  """
  Docstring for hash_file
  Generate SHA-256 hash for a file-like object.
  8192: The "Bite Size"  (keeps the RAM usage low).
  :param file_obj: Description
  :return: Description
  :rtype: str
  """
  sha256 = hashlib.sha256()

  while True:
    chunk = file_obj.read(8192)
    if not chunk:
      break
    sha256.update(chunk)
  
  # Reset file pointer so i can be reused later.
  file_obj.seek(0)

  return sha256.hexdigest()

