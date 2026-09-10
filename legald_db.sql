-- ============================================================
-- LEGAL CONTRACT MANAGEMENT SYSTEM
-- COMPLETE DATABASE SETUP (MySQL)
-- ============================================================

-- 1️⃣ Database drop (agar pehle se hai toh)
DROP DATABASE IF EXISTS legal_contract_db;

-- 2️⃣ Database create
CREATE DATABASE legal_contract_db;

-- 3️⃣ Database use karo
USE legal_contract_db;

-- ============================================================
-- TABLES CREATE (Enum ki jagah CHECK constraint use kiya hai)
-- ============================================================

-- 1️⃣ USERS TABLE
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'legal', 'viewer') DEFAULT 'viewer',
    department VARCHAR(100),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2️⃣ CONTRACTS TABLE
CREATE TABLE contracts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_number VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    contract_type ENUM('employment', 'nda', 'sales', 'purchase', 'lease', 'service', 'license', 'other') DEFAULT 'other',
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    file_size INT,
    clauses JSON,
    metadata JSON,
    tags JSON,
    status ENUM('draft', 'pending', 'reviewed', 'approved', 'rejected', 'archived') DEFAULT 'draft',
    current_version INT DEFAULT 1,
    start_date DATETIME,
    end_date DATETIME,
    signing_date DATETIME,
    expiry_date DATETIME,
    amount FLOAT,
    currency VARCHAR(10) DEFAULT 'USD',
    party_a VARCHAR(255),
    party_b VARCHAR(255),
    party_a_contact VARCHAR(255),
    party_b_contact VARCHAR(255),
    uploaded_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 3️⃣ CONTRACT VERSIONS TABLE
CREATE TABLE contract_versions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    version_number INT NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255),
    clauses JSON,
    change_summary TEXT,
    modified_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (modified_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 4️⃣ APPROVALS TABLE
CREATE TABLE approvals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contract_id INT NOT NULL,
    version_id INT NOT NULL,
    requested_by INT,
    approved_by INT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE,
    FOREIGN KEY (version_id) REFERENCES contract_versions(id) ON DELETE CASCADE,
    FOREIGN KEY (requested_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL
);

-- 5️⃣ AUDIT LOG TABLE
CREATE TABLE audit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    contract_id INT,
    action VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id) ON DELETE CASCADE
);

-- ============================================================
-- INDEXES (Performance Ke Liye)
-- ============================================================

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_contracts_status ON contracts(status);
CREATE INDEX idx_contracts_uploaded_by ON contracts(uploaded_by);
CREATE INDEX idx_contracts_contract_number ON contracts(contract_number);
CREATE INDEX idx_contract_versions_contract_id ON contract_versions(contract_id);
CREATE INDEX idx_approvals_contract_id ON approvals(contract_id);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_contract_id ON audit_log(contract_id);

-- ============================================================
-- SAMPLE DATA INSERT
-- ============================================================

-- 1️⃣ Admin User
INSERT INTO users (name, email, password, role, department) 
VALUES ('Admin', 'admin@system.com', 'admin123_hashed', 'admin', 'Management');

-- 2️⃣ Legal User
INSERT INTO users (name, email, password, role, department) 
VALUES ('Legal Team', 'legal@system.com', 'legal123_hashed', 'legal', 'Legal');

-- 3️⃣ Viewer User
INSERT INTO users (name, email, password, role, department) 
VALUES ('Viewer', 'viewer@system.com', 'viewer123_hashed', 'viewer', 'Sales');

-- 4️⃣ Sample Contract
INSERT INTO contracts (
    contract_number, title, description, contract_type, file_path, file_name, 
    clauses, uploaded_by, party_a, party_b, amount, currency
) VALUES (
    'CTR-2026-000001',
    'Employment Agreement',
    'Standard employment contract for full-time employees',
    'employment',
    '/uploads/employment_agreement.pdf',
    'employment_agreement.pdf',
    '{"clause_1": "Salary - ₹50,000/month", "clause_2": "Working Hours - 9 AM to 6 PM", "clause_3": "Leave Policy - 20 days/year"}',
    1,
    'Microsoft India',
    'Aniket Darekar',
    600000.00,
    'INR'
);

-- 5️⃣ Sample Version
INSERT INTO contract_versions (contract_id, version_number, file_path, file_name, clauses, change_summary, modified_by) 
VALUES (
    1,
    1,
    '/uploads/employment_agreement_v1.pdf',
    'employment_agreement_v1.pdf',
    '{"clause_1": "Salary - ₹50,000/month", "clause_2": "Working Hours - 9 AM to 6 PM", "clause_3": "Leave Policy - 20 days/year"}',
    'Initial version',
    1
);

-- 6️⃣ Sample Approval
INSERT INTO approvals (contract_id, version_id, requested_by, status, comments) 
VALUES (1, 1, 2, 'pending', 'Please review this employment contract');

-- 7️⃣ Sample Audit Log
INSERT INTO audit_log (user_id, contract_id, action, details) 
VALUES (1, 1, 'contract_uploaded', 'Uploaded Employment Agreement');

-- ============================================================
-- VERIFY DATA
-- ============================================================

SELECT 'USERS' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'CONTRACTS', COUNT(*) FROM contracts
UNION ALL
SELECT 'VERSIONS', COUNT(*) FROM contract_versions
UNION ALL
SELECT 'APPROVALS', COUNT(*) FROM approvals
UNION ALL
SELECT 'AUDIT_LOG', COUNT(*) FROM audit_log;

-- ============================================================
-- VIEW ALL DATA
-- ============================================================

SELECT * FROM users;
SELECT * FROM contracts;
SELECT * FROM contract_versions;
SELECT * FROM approvals;
SELECT * FROM audit_log;

-- ============================================================
-- DROP TABLES 
-- ============================================================

-- DROP TABLE IF EXISTS audit_log;
-- DROP TABLE IF EXISTS approvals;
-- DROP TABLE IF EXISTS contract_versions;
-- DROP TABLE IF EXISTS contracts;
-- DROP TABLE IF EXISTS users;