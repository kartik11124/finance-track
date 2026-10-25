# Smart Personal Finance & Budget Management System

**Product Edition:** Production Enterprise Edition  
**Domain:** Personal Wealth Architecture, Budget Engineering, Data Structures & Algorithms, Real-Time Market Intelligence  
**Core Technologies:** Python 3, Flask, SQLite 3, HTML5, CSS3, JavaScript (Chart.js), Financial APIs  

---

## 1. Project Overview

The **Smart Personal Finance & Budget Management System** is a full-stack, production-grade application engineered to provide end-to-end mastery over personal cash flow, goal-based savings, and portfolio planning. Unlike basic trackers or static UI prototypes, this system integrates:

1. **Real-Time Financial Arithmetic:** Automated calculation of cash surplus, savings ratios, budget utilization, and true disposable investment capacity.
2. **Smart Income Allocation Planner:** Dual-mode budget optimizer offering:
   - **Strategic Allocation (Recommended):** Rule-based financial planning models (50/30/20 Balanced, 40/20/40 Wealth Builder, 60/20/20 Conservative) calculating exact Rupee amounts for living expenses, discretionary spending, and wealth creation.
   - **Self-Directed Plan (Custom):** Dynamic client-side allocator with live balance calculation and category budgeting.
   - **1-Click SQLite Batch Persistence:** Sync allocations directly into database budgets.
3. **Adaptive User Interface (Dark & Light Mode):** Enterprise-grade UI design with CSS theme tokens, zero-flash theme persistence via `localStorage`, and reactive dynamic chart recoloring.
4. **External Financial Market Integrations:** Live equities (Alpha Vantage), 24K bullion spot rates in INR (GoldAPI), Indian mutual fund NAVs (MFAPI.in), and business headlines (NewsAPI) with offline SQLite caching.
5. **DSA-Driven Recommendation Engine:** Custom-built data structures (Binary Max-Heap Priority Queues, Binary Search, QuickSort, MergeSort) matching investment instruments to user risk profiles and financial horizons.

All recommendations are presented as:
> *"Investment options matching the entered criteria"*  
> and never as guaranteed financial returns.

---

## 2. Key Features

- **Authentication & Security:** Secure registration, login, session guard (`@login_required`), and cryptographic password hashing (PBKDF2/scrypt).
- **Adaptive Dark / Light Mode:** Instant theme switcher with full CSS variable theming across all tables, charts, forms, and cards with `localStorage` memory.
- **Smart Budget Allocation & Income Planner (`/smart-budget`):**
  - **Strategic Allocation (Recommended):** Choose between *50/30/20 Balanced Living*, *40/20/40 Aggressive Wealth Accumulator*, or *60/20/20 Conservative High-Need* distributions.
  - **Self-Directed Plan (Custom):** User-tailored allocation with instant unallocated balance feedback.
  - **Batch Commit:** 1-click batch application to SQLite `budgets` table.
- **Income Tracker:** Record, filter, and audit revenue streams (Salary, Freelance, Business, Investments).
- **Expense Categorization:** Track spending across standard categories (*Food, Rent, Transport, Education, Shopping, Utilities, Healthcare, Entertainment, Other*).
- **Budget Alerts:** Real-time visual tracking of category limits:
  - 🟢 **Under Budget** (< 80% used)
  - 🟡 **Near Limit** (80% – 100% used)
  - 🔴 **Over Budget** (> 100% exceeded)
- **Financial Goals Tracker:** Dynamic calculation of remaining amounts, progress percentages, and **required monthly contributions** to hit deadlines.
- **Explainable Recommendation Engine:** 5-factor scoring (Risk 30%, Amount 25%, Horizon 20%, Goal 15%, Liquidity 10%) producing human-readable rationales.
- **Live Financial Feeds with Graceful Fallbacks:**
  - **Stock Equities:** Search quotes for RELIANCE, TCS, INFY, HDFCBANK via Alpha Vantage.
  - **Gold Rates:** Real-time 24K spot price per gram and troy ounce in INR via GoldAPI.
  - **Mutual Funds:** Real-time search and NAV history via MFAPI.in (no API key needed).
  - **Financial News:** Curated headlines from NewsAPI.
- **Backend Health & Diagnostics:** Complete `/status` page displaying live database records and API connectivity without exposing secret keys.
- **Interactive Visualizations:** Income vs. Expense cash flow, Category distribution doughnut, Budget progress, and Smart Allocation charts via Chart.js.

---

## 3. Technology Stack

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **Frontend** | HTML5, CSS3, Modern Vanilla JavaScript | Lightweight semantic markup, responsive CSS variables, zero framework bloat. |
| **Theme Engine** | CSS Custom Properties + LocalStorage | Full Dark and Light theme toggle with zero-flash rendering. |
| **Charts** | Chart.js 4 (via CDN) + Pure Canvas Fallback | Interactive charts responsive to dynamic theme changes; backend remains authoritative. |
| **Backend** | Python 3 (Flask 3.x, Werkzeug) | Clean MVC/Service architecture, fast execution, secure session handling. |
| **Database** | SQLite 3 + Parameterized SQL | Zero-setup ACID relational database with foreign key cascades and check constraints. |
| **Algorithms (DSA)** | Pure Python Modules | Custom QuickSort, MergeSort, Binary Search, Hash Indexing, Priority Queue (Max-Heap). |
| **External APIs** | Alpha Vantage, GoldAPI, NewsAPI, MFAPI | Live equity quotes, bullion spot rates in INR, business headlines, and Indian mutual funds. |

---

## 4. System Architecture

```
User Browser (HTML5 / CSS3 / Dark-Light Theme / Chart.js)
           │
           ▼
Flask Application Layer (app.py)
   ├── Authentication & Session Guard (@login_required)
   ├── Services Layer
   │    ├── AuthService (Hashing & Credentials)
   │    ├── FinanceService (Income, Expenses, Budgets, Goals, Batch Allocations)
   │    ├── InvestmentService (Catalog & Catalog Filtering)
   │    ├── RecommendationService (Capacity Math & Engine)
   │    ├── DashboardService (Data Aggregation)
   │    └── StatusService (Health Diagnostics)
   │
   ├── Algorithms Layer (DSA Implementations)
   │    ├── Budget Allocation (50/30/20, 40/20/40, 60/20/20 Models)
   │    ├── Searching (Linear, Binary Search)
   │    ├── Sorting (QuickSort, MergeSort)
   │    ├── Filtering (Risk, Capacity, Horizon, Category)
   │    └── Recommendation (Max-Heap Priority Queue & Compatibility Matrix)
   │
   ├── External API Layer (Single .env Configuration)
   │    ├── Alpha Vantage (Stock Quotes)
   │    ├── GoldAPI (Live Gold Rates in INR)
   │    ├── NewsAPI (Financial Headlines)
   │    └── MFAPI (Free Indian Mutual Fund NAVs)
   │
   └── Storage Layer (SQLite3: database/finance.db)
        ├── Parameterized Queries & Foreign Key Constraints
        └── Automatic Offline Caching & Fallbacks
```

---

## 5. Database Architecture (SQLite Schema)

The database schema (`database/schema.sql`) enforces relational integrity, foreign key cascades, and check constraints:

1. `users`: User identity (`id`, `name`, `email` [UNIQUE], `password_hash`, `created_at`).
2. `user_profiles`: User risk profile (`user_id`, `risk_tolerance` [LOW/MEDIUM/HIGH], `investment_horizon` [SHORT/MEDIUM/LONG], `primary_goal`, `emergency_fund_months`).
3. `income`: Earnings records (`user_id`, `amount`, `source`, `date`, `description`).
4. `expenses`: Expenditure entries (`user_id`, `amount`, `category`, `date`, `description`).
5. `budgets`: Category limits (`user_id`, `category`, `amount`, `month_year`).
6. `financial_goals`: Savings targets (`user_id`, `name`, `target_amount`, `current_amount`, `target_date`, `category`, `status`).
7. `investments`: Curated catalog of financial instruments (`id`, `name`, `category`, `risk_level`, `minimum_amount`, `duration`, `expected_return_rate`, `expected_return_information`, `liquidity`, `suitable_goal`, `description`).
8. `transactions`: Complete transaction audit log.
9. `recommendations`: Historical log of algorithmic recommendation runs.
10. `market_data`: Cached stock quotes with timestamps and price changes.
11. `gold_data`: Cached gold rates in INR per gram and ounce.
12. `news`: Cached business headlines.
13. `mutual_funds`: Cached mutual fund schemes and NAV data.

---

## 6. Smart Income Allocation Models (`algorithms/budget_allocation.py`)

The system provides formal financial allocation algorithms:

### 1. The 50/30/20 Balanced Model (`balanced_50_30_20`)
- **Needs (50%):** Rent (25%), Food (12%), Transport (8%), Utilities (5%).
- **Wants (30%):** Personal & Shopping (12%), Entertainment (10%), Healthcare & Wellness (8%).
- **Wealth Investments (20%):** Equity SIPs, Debt Funds, Emergency Reserve.

### 2. The 40/20/40 Wealth Builder Model (`wealth_builder_40_20_40`)
- Optimized for ambitious wealth creators, early financial independence, or frugal households:
- **Needs (40%):** Rent (20%), Food (10%), Transport (6%), Utilities (4%).
- **Wants (20%):** Personal (8%), Entertainment (6%), Healthcare (6%).
- **Wealth Investments (40%):** Long-term diversified capital accumulation.

### 3. The 60/20/20 Conservative High-Need Model (`conservative_60_20_20`)
- Tailored for high-cost-of-living metropolitan areas or single-earner households:
- **Needs (60%):** Rent (30%), Food (15%), Transport (8%), Utilities (7%).
- **Wants (20%):** Personal (8%), Healthcare (7%), Entertainment (5%).
- **Wealth Investments (20%):** Capital preservation and disciplined savings.

---

## 7. Data Structures & Algorithms (DSA) Implementation

### 1. Searching (`algorithms/searching.py`)
- **Linear Search ($O(n)$):** Scans unsorted financial histories and attributes.
- **Binary Search ($O(\log n)$):** Fast divide-and-conquer search across pre-sorted investment options based on numeric thresholds.
- **Hash Indexing ($O(1)$ lookup):** Groups investment products by risk level and asset category into hash map dictionaries.

### 2. Sorting (`algorithms/sorting.py`)
- **QuickSort ($O(n \log n)$ avg):** Pivot-partitioning algorithm used to dynamically sort catalog items by minimum commitment or compatibility score.
- **MergeSort ($O(n \log n)$ stable):** Divide-and-conquer sorting algorithm ensuring stable multi-attribute ordering.

### 3. Multi-Criteria Filtering (`algorithms/filtering.py`)
- Cascading predicates enforcing risk ceilings, capital affordability, and horizon compatibility.

### 4. Recommendation Priority Queue (`algorithms/recommendation.py`)
- Implements a **Binary Max-Heap** via Python's `heapq` module.
- Insertion complexity: $O(\log n)$
- Extraction complexity: $O(k \log n)$ for top-$k$ recommendations.

---

## 8. Recommendation Engine & Scoring Matrix

The engine evaluates eligible investment instruments across 5 weighted dimensions (100 points maximum):

$$\text{Total Score} = \text{Risk Match (30)} + \text{Amount Match (25)} + \text{Duration Match (20)} + \text{Goal Match (15)} + \text{Liquidity Match (10)}$$

### Disciplined Investment Capacity Formula
$$\text{Monthly Surplus} = \text{Income} - \text{Expenses}$$

$$\text{Emergency Reserve} = \text{Surplus} \times (\text{Emergency Months} \times 5\%) \quad (\text{typically } 15\% - 25\%)$$

$$\text{Available Capacity} = \max\left(0, \text{Monthly Surplus} - \text{Emergency Reserve} - \sum \text{Monthly Goal Obligations}\right)$$

---

## 9. Folder Structure

```
c:\Users\parek\OneDrive\Desktop\Finance man\
│
├── app.py                         # Main Flask application and HTTP route handlers
├── test_system.py                 # Automated 8-phase test suite
├── requirements.txt               # Python dependency declarations
├── .env.example                   # Single configuration template for API keys
├── .env                           # Active environment configuration
├── README.md                      # Complete system documentation
│
├── config/
│   ├── __init__.py
│   └── config.py                  # Environment variable loader and path configuration
│
├── database/
│   ├── __init__.py
│   ├── database.py                # SQLite connection manager, query helpers, and seeds
│   ├── schema.sql                 # Relational SQLite DDL schema
│   └── finance.db                 # Auto-created SQLite database file
│
├── models/
│   ├── __init__.py
│   ├── user.py                    # User & UserProfile dataclasses
│   ├── income.py                  # Income model
│   ├── expense.py                 # Expense model & category constants
│   ├── budget.py                  # Budget model
│   ├── goal.py                    # Financial goal model with timeline arithmetic
│   ├── investment.py              # Investment instrument model
│   └── transaction.py             # Transaction audit model
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py            # Password hashing and session logic
│   ├── finance_service.py         # CRUD operations, financial calculations, batch budgets
│   ├── investment_service.py      # Investment catalog retrieval and query filters
│   ├── recommendation_service.py  # Capacity calculations & Priority Queue runner
│   ├── dashboard_service.py       # Central metrics aggregation
│   └── status_service.py          # System health checks and diagnostics
│
├── algorithms/
│   ├── __init__.py
│   ├── budget_allocation.py       # 50/30/20, 40/20/40, 60/20/20 allocation strategies
│   ├── searching.py               # Linear Search, Binary Search, Hash Indexing
│   ├── sorting.py                 # QuickSort and MergeSort implementations
│   ├── filtering.py               # Multi-predicate filtering pipelines
│   └── recommendation.py          # Scoring engine and Max-Heap Priority Queue
│
├── api/
│   ├── __init__.py
│   ├── alpha_vantage.py           # Stock quotes client & cache manager
│   ├── gold_api.py                # Spot Gold (INR) client & cache manager
│   ├── news_api.py                # Financial news client & cache manager
│   └── mf_api.py                  # Indian Mutual Funds client (Free, No Key)
│
├── templates/
│   ├── base.html                  # Shared layout, theme switcher, navbar, and footer
│   ├── login.html                 # User login view
│   ├── register.html              # User registration view
│   ├── dashboard.html             # Central dashboard with cards, charts, and feeds
│   ├── smart_budget.html          # Dual-mode Smart Budget Allocation & Planner
│   ├── income.html                # Income management view
│   ├── expenses.html              # Expense management view
│   ├── budget.html                # Category budget planner view
│   ├── goals.html                 # Financial goals tracker view
│   ├── investments.html           # Searchable investment catalog view
│   ├── recommendations.html       # Algorithmic recommendation view with explainability
│   ├── market.html                # Stock market lookup view
│   ├── gold.html                  # Gold price monitor view
│   ├── news.html                  # Financial headlines view
│   ├── mutual_funds.html          # Mutual fund NAV explorer view
│   ├── status.html                # Backend status & diagnostic health view
│   ├── profile.html               # User financial preferences view
│   ├── 404.html                   # Not Found error page
│   └── 500.html                   # Server Error fallback page
│
└── static/
    ├── css/
    │   └── style.css              # Modern responsive CSS with Dark/Light design tokens
    └── js/
        ├── main.js                # Theme controller, custom allocator, UI interactions
        └── charts.js              # Chart.js loader with dynamic theme synchronization
```

---

## 10. Installation & Setup

### Prerequisites
- Python 3.10 or higher.

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure API Keys in ONE `.env` File
Open `.env` in the root folder:

```env
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
GOLD_API_KEY=YOUR_KEY_HERE
NEWS_API_KEY=YOUR_KEY_HERE
SECRET_KEY=smart_finance_budget_secret_key_2026
PORT=5000
```

> **API Key Notes:**
> - **Alpha Vantage:** Free API key at [alphavantage.co](https://www.alphavantage.co/support/#api-key).
> - **GoldAPI:** Free API key at [goldapi.io](https://www.goldapi.io/).
> - **NewsAPI:** Free API key at [newsapi.org](https://newsapi.org/).
> - **MFAPI:** Requires **NO API key** (free public Indian mutual fund API).
> - **Offline Resilience:** If API keys are not provided or if external endpoints are temporarily unreachable, the application **automatically falls back to SQLite cached records** and remains 100% operational.

### Step 3: Run the Application
```bash
python app.py
```

The application will automatically:
1. Initialize the SQLite database (`database/finance.db`).
2. Execute the relational schema (`database/schema.sql`).
3. Seed the 16 real-world investment instruments and fallback market/gold/news caches.
4. Launch the local web server at: **`http://127.0.0.1:5000`**

Open `http://127.0.0.1:5000` in your web browser.

---

## 11. Automated Verification & Testing

Run the full automated test suite:

```bash
python test_system.py
```

### Test Coverage (8 Comprehensive Phases):
1. **Database Schema & Seeding Verification:** Checks foreign key cascades and default investment catalog.
2. **User Authentication Flow:** Tests registration, duplicate email rejection, and secure credential verification.
3. **Financial Mathematics & Transactions:** Validates income logging, expense categorization, net savings, and budget status logic.
4. **Goals Tracking:** Validates progress %, remaining amounts, and required monthly contributions.
5. **DSA Algorithms (Unit Tests):** Validates Linear Search, Binary Search, QuickSort, MergeSort, Hash Indexing, and Max-Heap extraction.
6. **API Fallbacks & Cache Management:** Validates offline resilience for Alpha Vantage, GoldAPI, NewsAPI, and MFAPI.
7. **Smart Budget Allocation Algorithms:** Validates 50/30/20, 40/20/40, and 60/20/20 calculations across Needs, Wants, and Investments.
8. **End-to-End Smart Budget Application:** Validates batch insertion and update of category budgets to SQLite.
