"""Simple Flask web frontend for the internships scraper."""
from flask import Flask, render_template, request, send_file
from src.database_client import DatabaseClient
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/')
def index():
    q = request.args.get('q')
    page = int(request.args.get('page', '1'))
    per_page = int(request.args.get('per_page', '25'))
    offset = (page - 1) * per_page

    db = DatabaseClient()
    items = db.list_internships(search=q, limit=per_page, offset=offset)
    # simple pagination info
    return render_template('index.html', items=items, q=q, page=page, per_page=per_page)

@app.route('/health')
def health():
    return {"status": "ok"}

if __name__ == '__main__':
    port = int(os.getenv('PORT', '5000'))
    app.run(host='0.0.0.0', port=port, debug=True)
