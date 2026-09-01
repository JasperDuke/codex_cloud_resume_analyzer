import json
import os
import sqlite3
import sys
from datetime import datetime, timezone

DB_PATH = os.environ.get("DATABASE_PATH", "data/resume-analyzer.db")
os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
db = sqlite3.connect(DB_PATH)
db.row_factory = sqlite3.Row
db.execute("""CREATE TABLE IF NOT EXISTS resumes (
  id TEXT PRIMARY KEY, filename TEXT NOT NULL, stored_filename TEXT NOT NULL,
  mime_type TEXT NOT NULL, created_at TEXT NOT NULL
)""")
db.execute("""CREATE TABLE IF NOT EXISTS analyses (
  id TEXT PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, resume_filename TEXT NOT NULL,
  resume_file TEXT NOT NULL, job_description TEXT NOT NULL, atenxion_url TEXT NOT NULL,
  status TEXT NOT NULL, result TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
)""")
db.commit()

def now(): return datetime.now(timezone.utc).isoformat()
def row(r): return dict(r) if r else None
payload = json.load(sys.stdin)
op, args = payload["op"], payload.get("args", {})

if op == "create_resume":
  db.execute("INSERT INTO resumes VALUES (?, ?, ?, ?, ?)", (args["id"], args["filename"], args["storedFilename"], args["mimeType"], now()))
  db.commit(); print(json.dumps({"ok": True}))
elif op == "get_resume":
  print(json.dumps(row(db.execute("SELECT * FROM resumes WHERE id = ?", (args["id"],)).fetchone())))
elif op == "delete_resume":
  r = db.execute("SELECT * FROM resumes WHERE id = ?", (args["id"],)).fetchone()
  if r: db.execute("DELETE FROM resumes WHERE id = ?", (args["id"],)); db.commit()
  print(json.dumps(row(r)))
elif op == "create_analysis":
  t = now(); db.execute("INSERT INTO analyses VALUES (?, ?, ?, ?, ?, ?, 'pending', NULL, ?, ?)", (args["id"], args["eventId"], args["resumeFilename"], args["resumeFile"], args["jobDescription"], args["atenxionUrl"], t, t)); db.commit(); print(json.dumps({"ok": True}))
elif op == "set_status":
  db.execute("UPDATE analyses SET status = ?, updated_at = ? WHERE event_id = ?", (args["status"], now(), args["eventId"])); db.commit(); print(json.dumps({"ok": True}))
elif op == "get_analysis":
  print(json.dumps(row(db.execute("SELECT * FROM analyses WHERE event_id = ?", (args["eventId"],)).fetchone())))
elif op == "complete_analysis":
  r = db.execute("SELECT event_id FROM analyses WHERE event_id = ?", (args["eventId"],)).fetchone()
  if r: db.execute("UPDATE analyses SET status = 'completed', result = ?, updated_at = ? WHERE event_id = ?", (json.dumps(args["result"]), now(), args["eventId"])); db.commit()
  print(json.dumps({"found": bool(r)}))
