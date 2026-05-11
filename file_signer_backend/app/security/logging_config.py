import logging
import sys
import os

def setup_logging():
  # 1.THE FORMATTER
  # %(asctime)s: Time of the event
  # %(name)s: Which file/module the Log came from
  # %(level)s: Is it an Info, Warning, or Error?
  # %(message)s: The actual description
  log_format = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  )

  # 2. THE ROOT LOGGER
  # We set it to info level, meaning it will record everything 
  # except "Debug" to keep the file clean.
  logger = logging.getLogger()
  logger.setLevel(logging.INFO)

  # 3. DESTINATION A: TERMINAL
  # this allows to see what's live in console
  console_handler = logging.StreamHandler(sys.stdout)
  console_handler.setFormatter(log_format)
  logger.addHandler(console_handler)

  # 4. DESTINATION B: A PERMANANT FILE (app.log)
  # This creates a file in the project root.
  file_handler = logging.FileHandler("app.log")
  file_handler.setFormatter(log_format)
  logger.addHandler(file_handler)

  logging.info("Logging system initialized: Console and File handlers are active.")