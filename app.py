from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
import sqlite3
import json
import uvicorn

app = FastAPI(title="Legal Document Management System")

# Database Setup
def init_db():
    conn = sqlite3.connect('legal_cms.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_number TEXT,
        title TEXT,
        client_name TEXT,
        case_type TEXT,
        status TEXT,
        date_filed TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

# Dummy Data
def seed_data():
    conn = sqlite3.connect('legal_cms.db')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cases")
    if cur.fetchone()[0] == 0:
        cases = [
            ('LEG-2024-001', 'Property Dispute', 'Rajesh Sharma', 'Civil', 'Active', '2024-01-15'),
            ('LEG-2024-002', 'Contract Breach', 'Priya Patel', 'Corporate', 'Pending', '2024-02-20'),
            ('LEG-2024-003', 'Divorce Petition', 'Amit Verma', 'Family', 'Closed', '2024-03-10'),
            ('LEG-2024-004', 'Employment Law', 'Sneha Gupta', 'Labor', 'Active', '2024-04-05'),
        ]
        cur.executemany("INSERT INTO cases (case_number, title, client_name, case_type, status, date_filed) VALUES (?, ?, ?, ?, ?, ?)", cases)
        conn.commit()
    conn.close()

seed_data()

# ---------------- BASE LAYOUT (Bootstrap + Dynamic JS) ----------------
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Document Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { font-family: 'Poppins', sans-serif; background-color: #f4f7f6; }
        
        /* SIDEBAR */
        .sidebar {
            height: 100vh; width: 280px; position: fixed; top: 0; left: 0;
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
            color: white; transition: all 0.3s; z-index: 1000;
        }
        .sidebar .brand {
            font-size: 24px; font-weight: 800; color: #fff; text-align: center; 
            margin-bottom: 30px; display: block; padding: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            background: linear-gradient(90deg, #fbbf24, #f59e0b);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .sidebar a {
            padding: 15px 20px; text-decoration: none; font-size: 15px; font-weight: 500; 
            color: #cbd5e1; display: block; transition: 0.3s; border-left: 4px solid transparent;
        }
        .sidebar a i { width: 25px; margin-right: 10px; color: #94a3b8; }
        .sidebar a:hover, .sidebar a.active { background: rgba(255,255,255,0.1); color: #fff; border-left: 4px solid #fbbf24; }
        .sidebar a:hover i, .sidebar a.active i { color: #fbbf24; }
        
        /* MAIN */
        .main-content { margin-left: 280px; padding: 20px; min-height: 100vh; }
        .topbar { background: white; padding: 15px 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; justify-content: space-between; align-items: center; }
        
        /* CARDS */
        .stat-card { border-radius: 15px; padding: 20px; color: white; box-shadow: 0 8px 20px rgba(0,0,0,0.1); transition: transform 0.3s; cursor: pointer; }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-card i { font-size: 45px; opacity: 0.5; float: right; }
        
        /* TABLE */
        .table thead th { background: #f8fafc; color: #475569; font-weight: 600; border: none; padding: 15px; }
        .table tbody tr { transition: 0.2s; }
        .table tbody tr:hover { background: #f1f5f9; }
        
        /* AUTH */
        .auth-container { height: 100vh; display: flex; justify-content: center; align-items: center; background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); }
        .auth-card { width: 450px; background: white; border-radius: 20px; padding: 40px; box-shadow: 0 15px 35px rgba(0,0,0,0.2); }
        .auth-card .logo { font-size: 50px; color: #fbbf24; text-align: center; margin-bottom: 20px; }
        .btn-primary { background: #1e3a8a; border: none; border-radius: 10px; }
        .btn-primary:hover { background: #172554; }
    </style>
</head>
<body>
    {content}
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Dynamic JS Function to switch pages without reload
        async function loadPage(url) {
            const response = await fetch(url);
            const html = await response.text();
            document.getElementById('app-content').innerHTML = html;
            // Update active sidebar link
            document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
            event.target.classList.add('active');
        }

        // Dynamic Function to add a new case (AJAX)
        async function addCase(event) {
            event.preventDefault();
            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData.entries());
            
            const response = await fetch('/api/add-case', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            if (response.ok) {
                alert('Case Added Successfully!');
                loadPage('/cases'); // Reload cases page
            } else {
                alert('Error adding case.');
            }
        }
    </script>
</body>
</html>
"""

# DASHBOARD HTML (Dynamic)
DASHBOARD_HTML = """
<div class="sidebar">
    <a href="#" class="brand"><i class="fas fa-scale-balanced"></i> Legal CMS</a>
    <a href="#" class="active" onclick="loadPage('/dashboard')"><i class="fas fa-th-large"></i> Dashboard</a>
    <a href="#" onclick="loadPage('/cases')"><i class="fas fa-folder-open"></i> Cases</a>
    <a href="#" onclick="loadPage('/clients')"><i class="fas fa-user-tie"></i> Clients</a>
    <a href="#" onclick="loadPage('/documents')"><i class="fas fa-file-contract"></i> Documents</a>
    <a href="#" onclick="loadPage('/hearings')"><i class="fas fa-gavel"></i> Hearings</a>
    <a href="#" onclick="loadPage('/reports')"><i class="fas fa-chart-pie"></i> Reports</a>
    <a href="#" onclick="loadPage('/settings')"><i class="fas fa-cog"></i> Settings</a>
    <a href="/logout"><i class="fas fa-sign-out-alt"></i> Logout</a>
</div>

<div class="main-content" id="app-content">
    <div class="topbar">
        <h4 class="text-primary fw-bold"><i class="fas fa-home me-2"></i> Dashboard</h4>
        <div>
            <span class="me-3 text-warning"><i class="fas fa-bell"></i></span>
            <img src="https://ui-avatars.com/api/?name=Admin&background=1e3a8a&color=fff" class="rounded-circle" width="40">
        </div>
    </div>

    <div class="row g-4 mb-4">
        <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #3b82f6, #2563eb);">
                <i class="fas fa-briefcase"></i>
                <h3>124</h3>
                <p>Total Cases</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #10b981, #059669);">
                <i class="fas fa-check-circle"></i>
                <h3>78</h3>
                <p>Closed Cases</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                <i class="fas fa-hourglass-half"></i>
                <h3>32</h3>
                <p>Pending Cases</p>
            </div>
        </div>
        <div class="col-md-3">
            <div class="stat-card" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                <i class="fas fa-users"></i>
                <h3>56</h3>
                <p>Total Clients</p>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-8">
            <div class="card shadow-sm border-0 p-3">
                <div class="d-flex justify-content-between align-items-center mb-3">
                    <h5 class="fw-bold text-primary"><i class="fas fa-list-alt me-2"></i> Recent Cases</h5>
                    <button class="btn btn-sm btn-warning fw-bold" onclick="loadPage('/cases')">View All</button>
                </div>
                <table class="table table-hover">
                    <thead>
                        <tr><th>Case No</th><th>Title</th><th>Client</th><th>Status</th><th>Date</th></tr>
                    </thead>
                    <tbody>
                        {case_rows}
                    </tbody>
                </table>
            </div>
        </div>
        <div class="col-md-4">
            <div class="card shadow-sm border-0 p-3">
                <h5 class="fw-bold text-success"><i class="fas fa-chart-line me-2"></i> Status Overview</h5>
                <div class="progress mb-3" style="height: 25px;">
                    <div class="progress-bar bg-primary" style="width: 60%">Active (60%)</div>
                </div>
                <div class="progress mb-3" style="height: 25px;">
                    <div class="progress-bar bg-warning" style="width: 25%">Pending (25%)</div>
                </div>
                <div class="progress" style="height: 25px;">
                    <div class="progress-bar bg-secondary" style="width: 15%">Closed (15%)</div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

# LOGIN HTML
LOGIN_HTML = """
<div class="auth-container">
    <div class="auth-card">
        <div class="logo"><i class="fas fa-scale-balanced"></i></div>
        <h3 class="text-center fw-bold text-primary mb-4">Legal CMS Login</h3>
        <form method="POST" action="/login">
            <div class="mb-3">
                <label class="form-label fw-bold">Email</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-envelope text-primary"></i></span>
                    <input type="email" name="email" class="form-control" placeholder="admin@legal.com" required>
                </div>
            </div>
            <div class="mb-4">
                <label class="form-label fw-bold">Password</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-lock text-primary"></i></span>
                    <input type="password" name="password" class="form-control" placeholder="********" required>
                </div>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2 fw-bold">Login</button>
        </form>
        <div class="text-center mt-3">New here? <a href="/register" class="fw-bold text-primary">Create Account</a></div>
    </div>
</div>
"""

# REGISTER HTML
REGISTER_HTML = """
<div class="auth-container">
    <div class="auth-card">
        <div class="logo"><i class="fas fa-user-plus"></i></div>
        <h3 class="text-center fw-bold text-primary mb-4">Create Account</h3>
        <form method="POST" action="/register">
            <div class="mb-3">
                <label class="form-label fw-bold">Name</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-user text-primary"></i></span>
                    <input type="text" name="name" class="form-control" placeholder="Full name" required>
                </div>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Email</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-envelope text-primary"></i></span>
                    <input type="email" name="email" class="form-control" placeholder="Email address" required>
                </div>
            </div>
            <div class="mb-4">
                <label class="form-label fw-bold">Password</label>
                <div class="input-group">
                    <span class="input-group-text"><i class="fas fa-lock text-primary"></i></span>
                    <input type="password" name="password" class="form-control" placeholder="Create password" required>
                </div>
            </div>
            <button type="submit" class="btn btn-primary w-100 py-2 fw-bold">Register</button>
        </form>
        <div class="text-center mt-3">Already have account? <a href="/login" class="fw-bold text-primary">Login</a></div>
    </div>
</div>
"""

# CASES HTML
CASES_HTML = """
<div class="main-content">
    <div class="topbar">
        <h4 class="text-primary fw-bold"><i class="fas fa-folder-open me-2"></i> Case Management</h4>
        <button class="btn btn-warning fw-bold" onclick="showAddCaseModal()"><i class="fas fa-plus me-2"></i>Add New Case</button>
    </div>
    
    <div class="card shadow-sm border-0 p-4">
        <table class="table table-hover">
            <thead>
                <tr><th>Case No</th><th>Title</th><th>Client</th><th>Type</th><th>Status</th><th>Date</th><th>Action</th></tr>
            </thead>
            <tbody id="cases-tbody">
                <!-- Data will be loaded via API -->
            </tbody>
        </table>
    </div>
</div>

<!-- Modal for Add Case -->
<div class="modal fade" id="addCaseModal" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Add New Case</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <form onsubmit="addCase(event)">
          <div class="mb-3"><input type="text" name="title" class="form-control" placeholder="Case Title" required></div>
          <div class="mb-3"><input type="text" name="client_name" class="form-control" placeholder="Client Name" required></div>
          <div class="mb-3">
            <select name="case_type" class="form-select" required>
                <option value="">Select Type</option>
                <option>Civil</option>
                <option>Corporate</option>
                <option>Family</option>
                <option>Labor</option>
            </select>
          </div>
          <button type="submit" class="btn btn-primary w-100">Save Case</button>
        </form>
      </div>
    </div>
  </div>
</div>

<script>
    // Load cases when page loads
    async function loadCases() {
        const response = await fetch('/api/get-cases');
        const cases = await response.json();
        const tbody = document.getElementById('cases-tbody');
        tbody.innerHTML = '';
        
        cases.forEach(c => {
            let badge = c[4] === 'Active' ? 'bg-success' : (c[4] === 'Pending' ? 'bg-warning text-dark' : 'bg-secondary');
            tbody.innerHTML += `
                <tr>
                    <td class="fw-bold text-primary">${c[1]}</td>
                    <td>${c[2]}</td>
                    <td>${c[3]}</td>
                    <td>${c[5]}</td>
                    <td><span class="badge ${badge}">${c[4]}</span></td>
                    <td>${c[6]}</td>
                    <td><button class="btn btn-sm btn-outline-danger"><i class="fas fa-trash"></i></button></td>
                </tr>
            `;
        });
    }

    function showAddCaseModal() {
        new bootstrap.Modal(document.getElementById('addCaseModal')).show();
    }

    // Load on initial page call
    loadCases();
</script>
"""

# ---------------- ROUTES ----------------

@app.get("/", response_class=HTMLResponse)
async def root():
    return BASE_LAYOUT.format(content=LOGIN_HTML)

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return BASE_LAYOUT.format(content=LOGIN_HTML)

@app.post("/login", response_class=HTMLResponse)
async def login_submit(email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('legal_cms.db')
    user = conn.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password)).fetchone()
    conn.close()
    if user:
        return RedirectResponse("/dashboard")
    else:
        return "<script>alert('Invalid Credentials'); window.location.href='/login';</script>"

@app.get("/register", response_class=HTMLResponse)
async def register_page():
    return BASE_LAYOUT.format(content=REGISTER_HTML)

@app.post("/register", response_class=HTMLResponse)
async def register_submit(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('legal_cms.db')
    try:
        conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
    except Exception:
        return "<script>alert('Email already exists'); window.location.href='/register';</script>"
    finally:
        conn.close()
    return RedirectResponse("/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    conn = sqlite3.connect('legal_cms.db')
    cases = conn.execute("SELECT * FROM cases").fetchall()
    conn.close()
    
    rows = ""
    for case in cases:
        status_color = "bg-success" if case[4] == "Active" else ("bg-warning" if case[4] == "Pending" else "bg-secondary")
        rows += f"""
        <tr>
            <td class="fw-bold text-primary">{case[1]}</td>
            <td>{case[2]}</td>
            <td>{case[3]}</td>
            <td><span class="badge {status_color}">{case[4]}</span></td>
            <td>{case[5]}</td>
        </tr>
        """
    return BASE_LAYOUT.format(content=DASHBOARD_HTML.format(case_rows=rows))

@app.get("/cases", response_class=HTMLResponse)
async def cases():
    return BASE_LAYOUT.format(content=CASES_HTML)

# ---------------- DYNAMIC API ENDPOINTS (JS uses these) ----------------

@app.get("/api/get-cases")
async def api_get_cases():
    conn = sqlite3.connect('legal_cms.db')
    cases = conn.execute("SELECT * FROM cases").fetchall()
    conn.close()
    return cases  # Returns list of tuples

@app.post("/api/add-case")
async def api_add_case(data: dict):
    conn = sqlite3.connect('legal_cms.db')
    case_no = f"LEG-2024-{len(conn.execute('SELECT * FROM cases').fetchall()) + 100:03d}"
    conn.execute("INSERT INTO cases (case_number, title, client_name, case_type, status, date_filed) VALUES (?, ?, ?, ?, ?, ?)",
                 (case_no, data['title'], data['client_name'], data['case_type'], 'Active', '2024-05-10'))
    conn.commit()
    conn.close()
    return {"message": "Case added successfully"}

@app.get("/logout")
async def logout():
    return RedirectResponse("/")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)