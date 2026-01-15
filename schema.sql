-- 1. Create Companies Table
CREATE TABLE IF NOT EXISTS companies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    business_number VARCHAR(20),
    domain VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_companies_domain ON companies(domain);

-- 2. Create Departments Table (Self-referencing for Hierarchy)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    parent_id INTEGER REFERENCES departments(id),
    name VARCHAR(100) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_departments_company_id ON departments(company_id);

-- 3. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    department_id INTEGER REFERENCES departments(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    google_id VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    profile_image VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_users_company_id ON users(company_id);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);

-- 4. Create Goals Table
CREATE TABLE IF NOT EXISTS goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    criteria TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_goals_user_id ON goals(user_id);

-- 5. Create OneOnOneSessions Table
CREATE TABLE IF NOT EXISTS one_on_one_sessions (
    id SERIAL PRIMARY KEY,
    company_id INTEGER NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id),
    manager_id INTEGER NOT NULL REFERENCES users(id),
    topic VARCHAR(200) NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    scheduled_at TIMESTAMPTZ NOT NULL,
    report_data TEXT,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS ix_one_on_one_sessions_company_id ON one_on_one_sessions(company_id);
