# Simple run script with built-in debug service
# For more robust deployment options, check the
# Flask user-guide under deployments.
from app import app
app.run(host='0.0.0.0', port=8080, debug=True)
