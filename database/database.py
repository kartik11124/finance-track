"""Database access and initialization layer for SQLite.
Ensures automatic table creation, parameterized queries, and seeding on first run.
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from config.config import DB_DIR, DB_PATH, SCHEMA_PATH


def get_db_connection() -> sqlite3.Connection:
    """Create and return a configured SQLite connection."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initialize SQLite database, execute schema, and seed investment records."""
    DB_DIR.mkdir(parents=True, exist_ok=True)

    conn = get_db_connection()
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

        # Check if investment table is empty and seed
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM investments;")
        count = cur.fetchone()[0]

        if count == 0:
            seed_investments(conn)
            seed_fallback_caches(conn)
            conn.commit()
    finally:
        conn.close()


def seed_investments(conn: sqlite3.Connection) -> None:
    """Seed comprehensive real-world investment catalog into SQLite."""
    seed_data = [
        # LOW RISK
        (
            "Overnight & Liquid Mutual Fund",
            "Mutual Fund",
            "LOW",
            500.0,
            "SHORT",
            6.5,
            "~6.2% - 6.8% p.a. (Historical debt market yield)",
            "HIGH",
            "Emergency Fund",
            "High safety and 1-day liquidity, ideal for parking emergency funds and immediate expenses."
        ),
        (
            "Bank Fixed Deposit (1-Year Term)",
            "Fixed Deposit",
            "LOW",
            1000.0,
            "SHORT",
            7.1,
            "~6.8% - 7.2% p.a. guaranteed interest rate",
            "MEDIUM",
            "Emergency Fund",
            "Safe bank deposit backed by DICGC guarantee up to ₹5 Lakhs, suitable for conservative short-term growth."
        ),
        (
            "91-Day Government Treasury Bills (T-Bills)",
            "Government Scheme",
            "LOW",
            10000.0,
            "SHORT",
            6.8,
            "~6.7% - 6.9% p.a. annualized yield",
            "HIGH",
            "Emergency Fund",
            "Sovereign government debt instruments with zero credit default risk, suitable for liquid capital preservation."
        ),
        (
            "Post Office Monthly Income Scheme (POMIS)",
            "Government Scheme",
            "LOW",
            1000.0,
            "MEDIUM",
            7.4,
            "7.4% p.a. fixed monthly payout (Govt backed)",
            "LOW",
            "Regular Income",
            "Safe government-backed fixed income scheme with 5-year lock-in providing dependable monthly payouts."
        ),
        (
            "Bank Fixed Deposit (3 to 5-Year Term)",
            "Fixed Deposit",
            "LOW",
            5000.0,
            "MEDIUM",
            7.3,
            "~7.0% - 7.5% p.a. compounded quarterly",
            "MEDIUM",
            "Vehicle",
            "Medium-term term deposit lock-in offering assured compounded interest for planned goals."
        ),
        (
            "Public Provident Fund (PPF)",
            "Government Scheme",
            "LOW",
            500.0,
            "LONG",
            7.1,
            "7.1% p.a. tax-free EEE status (Govt backed)",
            "LOW",
            "Wealth Creation",
            "15-year sovereign-backed retirement and wealth vehicle with Section 80C tax exemption and tax-free maturity."
        ),
        (
            "Sovereign Gold Bonds (SGB)",
            "Gold",
            "LOW",
            5000.0,
            "LONG",
            9.5,
            "2.5% p.a. interest + capital appreciation of Gold",
            "MEDIUM",
            "Wealth Creation",
            "RBI-issued gold bonds providing periodic 2.5% annual interest payouts plus zero-tax physical gold appreciation."
        ),

        # MEDIUM RISK
        (
            "Corporate Bond Debt Fund",
            "Mutual Fund",
            "MEDIUM",
            1000.0,
            "SHORT",
            7.8,
            "~7.5% - 8.2% p.a. (AAA corporate yield)",
            "HIGH",
            "Other",
            "Invests in high-quality AA+ and AAA rated corporate bonds offering steady accrual yield."
        ),
        (
            "Balanced Advantage / Dynamic Hybrid Fund",
            "Mutual Fund",
            "MEDIUM",
            1000.0,
            "MEDIUM",
            10.5,
            "~9.5% - 11.5% p.a. historical 5-year CAGR",
            "HIGH",
            "Vehicle",
            "Dynamically shifts asset allocation between equity and debt to protect downside during market volatility."
        ),
        (
            "Gold Exchange Traded Fund (ETF)",
            "Gold",
            "MEDIUM",
            1000.0,
            "MEDIUM",
            10.0,
            "Tracks 99.5% pure physical gold spot prices",
            "HIGH",
            "Wealth Creation",
            "Dematerialized units of gold traded on stock exchanges, providing instant liquidity and inflation hedging."
        ),
        (
            "Nifty 50 Index Mutual Fund",
            "Mutual Fund",
            "MEDIUM",
            500.0,
            "LONG",
            12.5,
            "~12.0% - 13.5% p.a. 10-year historical CAGR",
            "HIGH",
            "Wealth Creation",
            "Low-cost passive index fund mirroring the 50 largest bluechip companies in India, ideal for disciplined compounding."
        ),
        (
            "National Pension System (Tier-1 Auto Choice)",
            "Government Scheme",
            "MEDIUM",
            1000.0,
            "LONG",
            10.2,
            "~9.5% - 11.0% p.a. blended market returns",
            "LOW",
            "Retirement",
            "Low-cost regulated retirement vehicle providing additional tax deductions and diversified equity/debt exposure."
        ),

        # HIGH RISK
        (
            "Nifty Next 50 Large-Midcap Fund",
            "Mutual Fund",
            "HIGH",
            1000.0,
            "MEDIUM",
            13.5,
            "~13.0% - 15.0% p.a. historical CAGR",
            "HIGH",
            "Wealth Creation",
            "Exposure to emerging market leaders positioned directly behind top 50 bluechips, offering strong growth potential."
        ),
        (
            "Direct Bluechip Equity Basket (Large Cap)",
            "Equity",
            "HIGH",
            2500.0,
            "LONG",
            14.5,
            "~13.5% - 16.0% p.a. estimated long-term growth",
            "HIGH",
            "Wealth Creation",
            "Direct ownership in resilient market leaders like Reliance, TCS, HDFC Bank, and Infosys for long-term equity growth."
        ),
        (
            "Flexi Cap Equity Mutual Fund",
            "Mutual Fund",
            "HIGH",
            1000.0,
            "LONG",
            15.0,
            "~14.0% - 16.5% p.a. 7-year historical CAGR",
            "HIGH",
            "Wealth Creation",
            "Fund managers dynamically invest across large, mid, and small cap equities to capture high growth opportunities."
        ),
        (
            "Mid & Small Cap Growth Basket",
            "Equity",
            "HIGH",
            5000.0,
            "LONG",
            17.0,
            "~15.0% - 18.5% p.a. high volatility growth",
            "HIGH",
            "Wealth Creation",
            "High-beta growth basket investing in agile mid-sized and small companies, carrying higher volatility for maximum upside."
        )
    ]

    sql = """
        INSERT INTO investments (
            name, category, risk_level, minimum_amount, duration,
            expected_return_rate, expected_return_information, liquidity,
            suitable_goal, description
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """
    conn.executemany(sql, seed_data)


def seed_fallback_caches(conn: sqlite3.Connection) -> None:
    """Seed initial offline cache entries for market, gold, news, and mutual funds."""
    # Market data seed
    market_seeds = [
        ("RELIANCE", 2980.50, 2955.00, 25.50, "+0.86%", "2026-09-22", "Alpha Vantage Cache"),
        ("TCS", 4210.00, 4190.25, 19.75, "+0.47%", "2026-09-22", "Alpha Vantage Cache"),
        ("INFY", 1885.75, 1900.00, -14.25, "-0.75%", "2026-09-22", "Alpha Vantage Cache"),
        ("HDFCBANK", 1645.20, 1638.10, 7.10, "+0.43%", "2026-09-22", "Alpha Vantage Cache"),
    ]
    conn.executemany(
        """
        INSERT INTO market_data (symbol, price, previous_close, change, change_percent, latest_trading_day, source)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """,
        market_seeds
    )

    # Gold rate seed (INR per gram standard: ~₹7,350/g, ₹2,28,600/oz)
    conn.execute(
        """
        INSERT INTO gold_data (price_per_gram, price_per_ounce, currency, unit, source)
        VALUES (7385.50, 229715.00, 'INR', 'gram', 'GoldAPI Cache');
        """
    )

    # News seed
    news_seeds = [
        (
            "RBI Monetary Policy Committee Maintains Prudent Rate Outlook Amid Steady Growth",
            "Reserve Bank of India Bulletin",
            "2026-09-22",
            "The Reserve Bank of India emphasized macroeconomic stability and inflation containment while forecasting resilient domestic GDP expansion.",
            "https://rbi.org.in"
        ),
        (
            "Retail Investor Participation in Mutual Fund SIPs Hits New Record High in India",
            "Financial Express",
            "2026-09-21",
            "Systematic Investment Plan (SIP) contributions crossed landmark milestones as retail investors increasingly favor disciplined monthly compounding.",
            "https://financialexpress.com"
        ),
        (
            "Sovereign Gold Bonds and Gold ETFs Witness Steady Inflows Amid Global Hedging",
            "Mint",
            "2026-09-20",
            "Domestic investors continue to allocate capital to digital gold assets as a hedge against inflation and currency fluctuations.",
            "https://livemint.com"
        )
    ]
    conn.executemany(
        """
        INSERT INTO news (title, source, published_at, description, url)
        VALUES (?, ?, ?, ?, ?);
        """,
        news_seeds
    )

    # Mutual fund seed (MFAPI format)
    mf_seeds = [
        (120503, "Nippon India Small Cap Fund - Direct Plan - Growth", 175.42, "2026-09-22", "Equity - Small Cap"),
        (119063, "Parag Parikh Flexi Cap Fund - Direct Plan - Growth", 82.68, "2026-09-22", "Equity - Flexi Cap"),
        (120716, "UTI Nifty 50 Index Fund - Direct Plan - Growth", 192.15, "2026-09-22", "Index Fund"),
        (118989, "HDFC Balanced Advantage Fund - Direct Plan - Growth", 478.20, "2026-09-22", "Hybrid - Dynamic"),
    ]
    conn.executemany(
        """
        INSERT INTO mutual_funds (scheme_code, scheme_name, nav, date, category)
        VALUES (?, ?, ?, ?, ?);
        """,
        mf_seeds
    )


def execute_query(sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return list of dictionaries."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def execute_one(sql: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Execute a SELECT query and return a single row as dictionary or None."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def execute_insert(sql: str, params: tuple = ()) -> int:
    """Execute an INSERT statement and return the inserted row id."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def execute_update(sql: str, params: tuple = ()) -> int:
    """Execute an UPDATE or DELETE statement and return affected row count."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
