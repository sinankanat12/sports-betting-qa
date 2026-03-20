import os


BASE_URL = os.getenv("BASE_URL", "https://qae-assignment-tau.vercel.app")
USER_ID = os.getenv("USER_ID", "candidate-0e2d9b4c")
BROWSER = os.getenv("BROWSER", "chrome")
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "10"))
EXPLICIT_WAIT = int(os.getenv("EXPLICIT_WAIT", "15"))

API_BASE_URL = f"{BASE_URL}/api"
