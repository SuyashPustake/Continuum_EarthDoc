"""
Pytest configuration: load .env from project root so GOOGLE_API_KEY is available for API tests.
"""

import os

# Load .env from Continuum_Earthdoc (parent of tests/)
try:
    from dotenv import load_dotenv
    _root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    _env = os.path.join(_root, ".env")
    if os.path.isfile(_env):
        load_dotenv(_env)
except ImportError:
    pass  # python-dotenv optional
