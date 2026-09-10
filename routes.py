from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from database import get_db, init_db
import uvicorn

app = FastAPI(title="Legal CMS System")

# Database initialize
init_db()

# Import HTML strings from separate file
from templates_html import BASE_LAYOUT, LOGIN_HTML, REGISTER_HTML, DASHBOARD_HTML, CASES_HTML, CLIENTS_HTML, DOCUMENTS_HTML

# ---------------- ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
async def root():
    return BASE_LAYOUT.format(content=LOGIN_HTML)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return BASE_LAYOUT.format(content=LOGIN_HTML)

@app.post("/login", response_class=HTMLResponse)
async def login_submit(email: str = Form(...), password: str = Form(...)):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    if user:
        return RedirectResponse("/dashboard")
    else:
        return "<script>alert('Invalid Credentials'); window.location.href='/login';</script>"

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return BASE_LAYOUT.format(content=REGISTER_HTML)

@app.post("/register", response_class=HTMLResponse)
async def register_submit(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    db = get_db()
    try:
        db.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        db.commit()
    except Exception:
        return "<script>alert('Email already exists'); window.location.href='/register';</script>"
    finally:
        db.close()
    return RedirectResponse("/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    db = get_db()
    cases = db.execute("SELECT * FROM cases").fetchall()
    db.close()
    
    rows = ""
    for case in cases:
        status_color = "bg-success" if case['status'] == "Active" else ("bg-warning" if case['status'] == "Pending" else "bg-secondary")
        rows += f"""
        <tr>
            <td class="fw-bold text-primary">{case['case_number']}</td>
            <td>{case['title']}</td>
            <td>{case['client_name']}</td>
            <td><span class="badge {status_color}">{case['status']}</span></td>
            <td>{case['date_filed']}</td>
        </tr>
        """
    return BASE_LAYOUT.format(content=DASHBOARD_HTML.format(case_rows=rows))

@app.get("/cases", response_class=HTMLResponse)
async def cases():
    return BASE_LAYOUT.format(content=CASES_HTML)

@app.get("/clients", response_class=HTMLResponse)
async def clients():
    return BASE_LAYOUT.format(content=CLIENTS_HTML)

@app.get("/documents", response_class=HTMLResponse)
async def documents():
    return BASE_LAYOUT.format(content=DOCUMENTS_HTML)

@app.get("/logout")
async def logout():
    return RedirectResponse("/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)