-- SQLite Schema for Smart Personal Finance & Budget Management System
-- Parameterized, robust constraints, and foreign key relations.

PRAGMA foreign_keys = ON;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. User Profiles Table (Risk preferences & horizon)
CREATE TABLE IF NOT EXISTS user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    risk_tolerance TEXT DEFAULT 'MEDIUM' CHECK(risk_tolerance IN ('LOW', 'MEDIUM', 'HIGH')),
    investment_horizon TEXT DEFAULT 'MEDIUM' CHECK(investment_horizon IN ('SHORT', 'MEDIUM', 'LONG')),
    primary_goal TEXT DEFAULT 'Wealth Creation',
    emergency_fund_months INTEGER DEFAULT 3 CHECK(emergency_fund_months >= 1),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Income Records Table
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    source TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Expenses Records Table
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    category TEXT NOT NULL CHECK(category IN (
        'Food', 'Rent', 'Transport', 'Education', 'Shopping',
        'Utilities', 'Healthcare', 'Entertainment', 'Other'
    )),
    date TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 5. Budgets Table (Category-level limits per user)
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL CHECK(amount > 0),
    month_year TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, category, month_year),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 6. Financial Goals Table
CREATE TABLE IF NOT EXISTS financial_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    target_amount REAL NOT NULL CHECK(target_amount > 0),
    current_amount REAL NOT NULL DEFAULT 0.0 CHECK(current_amount >= 0),
    target_date TEXT NOT NULL,
    category TEXT DEFAULT 'Wealth Creation',
    status TEXT DEFAULT 'IN_PROGRESS' CHECK(status IN ('IN_PROGRESS', 'COMPLETED', 'PAUSED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 7. Investment Catalog Table (Database of standard instruments for recommendations)
CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN (
        'Fixed Deposit', 'Mutual Fund', 'Equity', 'Gold', 'Government Scheme', 'Other'
    )),
    risk_level TEXT NOT NULL CHECK(risk_level IN ('LOW', 'MEDIUM', 'HIGH')),
    minimum_amount REAL NOT NULL CHECK(minimum_amount >= 0),
    duration TEXT NOT NULL CHECK(duration IN ('SHORT', 'MEDIUM', 'LONG')),
    expected_return_rate REAL,
    expected_return_information TEXT NOT NULL,
    liquidity TEXT NOT NULL CHECK(liquidity IN ('HIGH', 'MEDIUM', 'LOW')),
    suitable_goal TEXT NOT NULL,
    description TEXT NOT NULL
);

-- 8. General Financial Transactions Audit Table
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('INCOME', 'EXPENSE', 'INVESTMENT', 'GOAL_CONTRIBUTION')),
    amount REAL NOT NULL,
    reference_id INTEGER,
    category TEXT,
    date TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 9. Recommendations Log Table
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    investment_id INTEGER NOT NULL,
    score REAL NOT NULL,
    match_reasons TEXT NOT NULL,
    calculated_capacity REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (investment_id) REFERENCES investments(id) ON DELETE CASCADE
);

-- 10. Market Data Cache Table (Alpha Vantage / live prices)
CREATE TABLE IF NOT EXISTS market_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    price REAL NOT NULL,
    previous_close REAL,
    change REAL,
    change_percent TEXT,
    latest_trading_day TEXT,
    source TEXT DEFAULT 'Alpha Vantage',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. Gold Data Cache Table (GoldAPI live INR rates)
CREATE TABLE IF NOT EXISTS gold_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price_per_gram REAL NOT NULL,
    price_per_ounce REAL NOT NULL,
    currency TEXT DEFAULT 'INR',
    unit TEXT DEFAULT 'gram',
    source TEXT DEFAULT 'GoldAPI',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Financial News Cache Table (NewsAPI headlines)
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source TEXT,
    published_at TEXT,
    description TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. Mutual Funds Cache Table (MFAPI NAVs)
CREATE TABLE IF NOT EXISTS mutual_funds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_code INTEGER UNIQUE NOT NULL,
    scheme_name TEXT NOT NULL,
    nav REAL NOT NULL,
    date TEXT NOT NULL,
    category TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance Indexes
CREATE INDEX IF NOT EXISTS idx_income_user_date ON income(user_id, date);
CREATE INDEX IF NOT EXISTS idx_expense_user_date ON expenses(user_id, date);
CREATE INDEX IF NOT EXISTS idx_budget_user ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_goals_user ON financial_goals(user_id);
CREATE INDEX IF NOT EXISTS idx_investments_criteria ON investments(risk_level, duration, minimum_amount);
CREATE INDEX IF NOT EXISTS idx_market_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_mf_code ON mutual_funds(scheme_code);
