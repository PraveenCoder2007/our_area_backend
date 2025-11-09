import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel handler
def handler(request):
    return app(request.scope, request.receive, request.send)

# For Vercel
app = app