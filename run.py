"""Development entry point. Never run debug=True on a public server."""
from eventhub.web import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5000)
