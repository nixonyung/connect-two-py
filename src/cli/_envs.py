import os

IS_TESTING = os.getenv("TESTING", default="0") == "1"
