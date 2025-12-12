```markdown
# Research Lab Manager

Research Lab Manager is a teaching/demo project (DBMS implementation) that uses SQLite + Flask to manage lab members, projects, equipment, grants, publications and related workflows.

## Prerequisites
- Python 3.10+ (Windows, macOS, Linux)
- Git (optional)

## Quick setup
1. Create and activate a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

On macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Initialize the database (creates `labmanager.db` from schema and sample data):

```powershell
python init_db.py
```

3. Run the Flask app locally:

```powershell
# from project root
python -m app.app
# or
set FLASK_APP=app.app
flask run
```

Open http://127.0.0.1:5000 in your browser.

## Files and structure
- [sql/schema_sqlite.sql](sql/schema_sqlite.sql) — database DDL (tables, triggers)
- [sql/sample_data.sql](sql/sample_data.sql) — seed data used by `init_db.py`
- [init_db.py](init_db.py) — runs schema + sample SQL to create `labmanager.db`
- [app/](app/) — Flask app, templates and static assets (main code)
- [app/static/css/style.css](app/static/css/style.css) — primary stylesheet for the app

## Notes on constraints and behavior
- The `Project` table stores a single `leader_id` (FK to `Faculty`) — each project therefore has a single canonical leader.
- Additional role-level constraints (for example preventing multiple PIs in `WorksOn`) are implemented via triggers where needed; see [sql/schema_sqlite.sql](sql/schema_sqlite.sql).
- Equipment concurrency is limited via triggers to prevent more than 3 overlapping users per equipment.

## Recommended cleanup before committing
- Add the virtual environment and DB file to `.gitignore`:

```
venv/
.venv/
labmanager.db
*.log
__pycache__/
```


```