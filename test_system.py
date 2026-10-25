"""Comprehensive System & Acceptance Test Suite for Smart Personal Finance & Budget Management System.
Executes automated tests covering Database CRUD, DSA algorithms, API fallbacks,
and the complete Requirement 37 Final Acceptance Workflow.
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database.database import (
    init_db,
    get_db_connection,
    execute_query,
    execute_one,
    execute_insert,
    execute_update
)
from algorithms.searching import linear_search, binary_search, build_hash_index, search_investments
from algorithms.sorting import quicksort, mergesort, sort_investments
from algorithms.filtering import filter_by_risk, filter_by_capacity, filter_by_duration, apply_multi_criteria_filter
from algorithms.recommendation import RecommendationPriorityQueue, calculate_compatibility, generate_recommendations
from api.alpha_vantage import fetch_stock_quote, get_all_cached_stocks
from api.gold_api import fetch_gold_price, get_cached_gold_price
from api.news_api import fetch_financial_news, get_cached_news
from api.mf_api import search_mutual_funds, fetch_mutual_fund_details, get_cached_mutual_funds
from services.auth_service import register_user, authenticate_user, get_user_profile, update_user_profile
from services.finance_service import (
    add_income, get_total_income, get_user_income_list, delete_income,
    add_expense, get_total_expenses, get_category_expenses, delete_expense,
    set_budget, get_user_budgets, get_budget_comparison, delete_budget,
    add_financial_goal, get_user_goals, update_financial_goal, delete_financial_goal,
    get_financial_summary
)
from services.recommendation_service import calculate_investment_capacity, get_personalized_recommendations
from services.dashboard_service import get_dashboard_data
from services.status_service import get_system_status
from app import app


class TestSmartFinanceSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Initialize database before test suite runs."""
        init_db()
        cls.test_email = f"test_{int(datetime.now().timestamp())}@example.com"
        cls.test_password = "securePassword123"
        cls.test_name = "Test Student"

    def test_01_database_and_seed(self):
        """Test database table creation and seed data insertion."""
        investments = execute_query("SELECT * FROM investments;")
        self.assertGreaterEqual(len(investments), 10, "Investments catalog should have seed records.")

        gold_cache = execute_query("SELECT * FROM gold_data;")
        self.assertGreaterEqual(len(gold_cache), 1, "Gold cache should have fallback records.")

        market_cache = execute_query("SELECT * FROM market_data;")
        self.assertGreaterEqual(len(market_cache), 4, "Market cache should have default stock records.")

        news_cache = execute_query("SELECT * FROM news;")
        self.assertGreaterEqual(len(news_cache), 1, "News cache should have fallback records.")

    def test_02_auth_service(self):
        """Test registration, hashing, and authentication."""
        # 1. Register
        success, msg, user_id = register_user(self.test_name, self.test_email, self.test_password)
        self.assertTrue(success, f"Registration failed: {msg}")
        self.assertIsNotNone(user_id)
        self.__class__.user_id = user_id

        # 2. Duplicate registration should fail
        dup_success, dup_msg, _ = register_user(self.test_name, self.test_email, self.test_password)
        self.assertFalse(dup_success, "Duplicate email registration must fail.")

        # 3. Authenticate with valid password
        auth_ok, auth_msg, user_info = authenticate_user(self.test_email, self.test_password)
        self.assertTrue(auth_ok, "Authentication should succeed with valid credentials.")
        self.assertEqual(user_info["id"], user_id)

        # 4. Authenticate with wrong password
        fail_ok, _, _ = authenticate_user(self.test_email, "wrongPassword")
        self.assertFalse(fail_ok, "Authentication should fail with wrong password.")

    def test_03_dsa_algorithms(self):
        """Test Linear Search, Binary Search, QuickSort, MergeSort, Hash Map, and Priority Queue."""
        data = [
            {"id": 1, "name": "FD", "amount": 1000, "risk": "LOW"},
            {"id": 2, "name": "PPF", "amount": 500, "risk": "LOW"},
            {"id": 3, "name": "Index Fund", "amount": 5000, "risk": "MEDIUM"},
            {"id": 4, "name": "Small Cap", "amount": 2500, "risk": "HIGH"},
        ]

        # 1. Linear Search
        res_linear = linear_search(data, key="risk", target="LOW")
        self.assertEqual(len(res_linear), 2)

        # 2. QuickSort (ascending by amount)
        sorted_qs = quicksort(data, key="amount", reverse=False)
        self.assertEqual([x["amount"] for x in sorted_qs], [500, 1000, 2500, 5000])

        # 3. MergeSort (descending by amount)
        sorted_ms = mergesort(data, key="amount", reverse=True)
        self.assertEqual([x["amount"] for x in sorted_ms], [5000, 2500, 1000, 500])

        # 4. Binary Search on sorted list
        idx = binary_search(sorted_qs, key="amount", target_val=2500)
        self.assertEqual(idx, 2)
        self.assertEqual(sorted_qs[idx]["name"], "Small Cap")

        # 5. Hash Map Indexing
        hash_map = build_hash_index(data, "risk")
        self.assertIn("LOW", hash_map)
        self.assertEqual(len(hash_map["LOW"]), 2)

        # 6. Priority Queue (Max-Heap)
        pq = RecommendationPriorityQueue()
        pq.push(75.5, {"name": "Fund B"})
        pq.push(92.0, {"name": "Fund A"})
        pq.push(64.0, {"name": "Fund C"})

        score1, item1 = pq.pop()
        self.assertEqual(score1, 92.0)
        self.assertEqual(item1["name"], "Fund A")

        score2, item2 = pq.pop()
        self.assertEqual(score2, 75.5)
        self.assertEqual(item2["name"], "Fund B")

    def test_04_api_resilience_and_fallbacks(self):
        """Test API clients under missing or placeholder keys."""
        # 1. Stock quote
        quote = fetch_stock_quote("RELIANCE")
        self.assertIn("price", quote)
        self.assertEqual(quote["symbol"], "RELIANCE")

        # 2. Invalid symbol
        inv_quote = fetch_stock_quote("NON_EXISTENT_SYM_XYZ123")
        self.assertTrue("error" in inv_quote or "notice" in inv_quote)

        # 3. Gold price
        gold = fetch_gold_price()
        self.assertIn("price_per_gram", gold)
        self.assertGreater(gold["price_per_gram"], 0)

        # 4. News
        news = fetch_financial_news(limit=5)
        self.assertIn("articles", news)
        self.assertGreater(len(news["articles"]), 0)

        # 5. MFAPI
        funds = get_cached_mutual_funds()
        self.assertGreaterEqual(len(funds), 1)

    def test_05_final_acceptance_test_requirement_37(self):
        """Requirement 37: Complete End-to-End Acceptance Test:
        Income: ₹50,000
        Expenses: ₹30,000
        Risk: MEDIUM
        Duration: LONG
        Goal: WEALTH CREATION
        Target: ₹5,00,000
        Then:
        - save data
        - calculate savings
        - calculate available investment amount
        - retrieve API data
        - query SQLite
        - execute DSA recommendation algorithm
        - rank investment options
        - display recommendations
        - display market data
        - display gold price
        - display financial news
        - reload & verify data remains in SQLite
        """
        user_id = self.__class__.user_id

        # 1. Enter Income: ₹50,000
        inc_id = add_income(
            user_id=user_id,
            amount=50000.0,
            source="Salary",
            date="2026-09-22",
            description="Monthly Technology Salary"
        )
        self.assertIsNotNone(inc_id)

        # 2. Enter Expenses: ₹30,000 (across categories)
        add_expense(user_id=user_id, amount=15000.0, category="Rent", date="2026-09-22", description="Apartment rent")
        add_expense(user_id=user_id, amount=8000.0, category="Food", date="2026-09-22", description="Monthly groceries")
        add_expense(user_id=user_id, amount=4000.0, category="Utilities", date="2026-09-22", description="Electricity and internet")
        add_expense(user_id=user_id, amount=3000.0, category="Transport", date="2026-09-22", description="Fuel and transit")

        # 3. Verify Calculations: Total Income, Total Expenses, Total Savings
        summary = get_financial_summary(user_id)
        self.assertEqual(summary["total_income"], 50000.0)
        self.assertEqual(summary["total_expenses"], 30000.0)
        self.assertEqual(summary["total_savings"], 20000.0)
        self.assertEqual(summary["savings_rate"], 40.0)  # (20,000 / 50,000) * 100

        # 4. Create Financial Goal: Target ₹5,00,000, Current ₹50,000, 3 Years
        target_date = (datetime.now() + timedelta(days=365 * 3)).strftime("%Y-%m-%d")
        goal_id = add_financial_goal(
            user_id=user_id,
            name="Wealth Creation",
            target_amount=500000.0,
            current_amount=50000.0,
            target_date=target_date,
            category="Wealth Creation"
        )
        self.assertIsNotNone(goal_id)

        goals = get_user_goals(user_id)
        self.assertEqual(len(goals), 1)
        g = goals[0]
        self.assertEqual(g["remaining_amount"], 450000.0)
        self.assertEqual(g["progress_percentage"], 10.0)
        self.assertGreater(g["monthly_contribution"], 0)

        # 5. Set Risk Profile: Risk=MEDIUM, Duration=LONG, Primary Goal="Wealth Creation"
        update_user_profile(
            user_id=user_id,
            risk_tolerance="MEDIUM",
            investment_horizon="LONG",
            primary_goal="Wealth Creation",
            emergency_fund_months=3
        )
        profile = get_user_profile(user_id)
        self.assertEqual(profile["risk_tolerance"], "MEDIUM")
        self.assertEqual(profile["investment_horizon"], "LONG")

        # 6. Calculate Financially Available Investment Capacity
        capacity_info = calculate_investment_capacity(user_id)
        self.assertGreater(capacity_info["monthly_surplus"], 0)
        self.assertGreater(capacity_info["available_capacity"], 0)
        self.assertLess(capacity_info["available_capacity"], 20000.0)  # Must be strictly less than full surplus because of emergency buffer & goal obligations!

        # 7. Execute DSA Recommendation Algorithm
        rec_payload = get_personalized_recommendations(
            user_id=user_id,
            override_risk="MEDIUM",
            override_duration="LONG",
            override_goal="Wealth Creation"
        )
        recs = rec_payload["recommendations"]
        self.assertGreaterEqual(len(recs), 3, "Should return ranked recommendations.")

        # Verify ranking order: Top recommendations must have descending scores
        scores = [r["score"] for r in recs]
        self.assertEqual(scores, sorted(scores, reverse=True), "Recommendations must be sorted descending by score via Priority Queue.")

        # Check top recommendation attributes
        top_rec = recs[0]
        self.assertIn("score", top_rec)
        self.assertIn("reasons", top_rec)
        self.assertGreaterEqual(top_rec["score"], 60.0)
        self.assertTrue(len(top_rec["reasons"]) > 0)

        # 8. Verify Dashboard Payload
        dashboard_data = get_dashboard_data(user_id)
        self.assertTrue(dashboard_data["has_financial_data"])
        self.assertEqual(dashboard_data["summary"]["total_income"], 50000.0)
        self.assertEqual(dashboard_data["summary"]["total_expenses"], 30000.0)
        self.assertEqual(dashboard_data["summary"]["total_savings"], 20000.0)
        self.assertIn("price_per_gram", dashboard_data["gold_data"])
        self.assertGreater(len(dashboard_data["market_stocks"]), 0)
        self.assertGreater(len(dashboard_data["news_articles"]), 0)

        # 9. Verify SQLite Persistence (Query directly to confirm all data remains in DB)
        direct_income = execute_one("SELECT amount FROM income WHERE id = ?;", (inc_id,))
        self.assertEqual(float(direct_income["amount"]), 50000.0)

        direct_expenses = execute_query("SELECT SUM(amount) as total FROM expenses WHERE user_id = ?;", (user_id,))
        self.assertEqual(float(direct_expenses[0]["total"]), 30000.0)

        direct_goal = execute_one("SELECT target_amount FROM financial_goals WHERE id = ?;", (goal_id,))
        self.assertEqual(float(direct_goal["target_amount"]), 500000.0)

        # Check recommendations audit log in SQLite
        saved_recs = execute_query("SELECT * FROM recommendations WHERE user_id = ?;", (user_id,))
        self.assertGreater(len(saved_recs), 0, "Recommendations must be persisted in SQLite table.")

    def test_06_flask_routes_and_views(self):
        """Test Flask web endpoints and rendering with test client."""
        client = app.test_client()

        # Unauthenticated endpoints
        res_login = client.get("/login")
        self.assertEqual(res_login.status_code, 200)
        self.assertIn(b"Log In", res_login.data)

        res_reg = client.get("/register")
        self.assertEqual(res_reg.status_code, 200)

        res_status = client.get("/status")
        self.assertEqual(res_status.status_code, 200)
        self.assertIn(b"Backend Diagnostics", res_status.data)
        self.assertIn(b"SQLite 3", res_status.data)

        # Authenticate session
        with client.session_transaction() as sess:
            sess["user_id"] = self.__class__.user_id
            sess["user_name"] = self.test_name
            sess["user_email"] = self.test_email

        # Authenticated views
        endpoints = [
            "/dashboard",
            "/income",
            "/expenses",
            "/budget",
            "/smart-budget",
            "/goals",
            "/recommendations",
            "/investments",
            "/market",
            "/gold",
            "/news",
            "/mutual-funds",
            "/profile"
        ]

        for ep in endpoints:
            res = client.get(ep)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} failed with status {res.status_code}")

    def test_07_smart_budget_allocation_algorithm(self):
        """Test the Algorithmic Budget Allocation Engine across strategies."""
        from algorithms.budget_allocation import calculate_algorithmic_budget

        # 1. Test Balanced 50/30/20 Rule on ₹60,000 income
        res_balanced = calculate_algorithmic_budget(60000.0, "balanced_50_30_20")
        self.assertEqual(res_balanced["needs_total"], 30000.0)      # 50%
        self.assertEqual(res_balanced["wants_total"], 18000.0)      # 30%
        self.assertEqual(res_balanced["invest_total"], 12000.0)     # 20%
        
        # Category checks
        cats = res_balanced["categories"]
        self.assertEqual(cats["Rent"]["amount"], 15000.0)          # 25% of 60,000
        self.assertEqual(cats["Food"]["amount"], 7200.0)           # 12% of 60,000
        self.assertEqual(cats["Utilities"]["amount"], 4200.0)      # 7% of 60,000
        self.assertEqual(cats["Transport"]["amount"], 3600.0)      # 6% of 60,000
        self.assertEqual(cats["Investments"]["amount"], 12000.0)   # 20% of 60,000

        # 2. Test Aggressive Wealth Builder 40/20/40 on ₹1,00,000 income
        res_wealth = calculate_algorithmic_budget(100000.0, "wealth_builder_40_20_40")
        self.assertEqual(res_wealth["invest_total"], 40000.0)      # 40%
        self.assertEqual(res_wealth["needs_total"], 40000.0)       # 40%
        self.assertEqual(res_wealth["wants_total"], 20000.0)       # 20%

    def test_08_smart_budget_apply_flow(self):
        """Test applying algorithmic and custom budget allocations to SQLite."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess["user_id"] = self.__class__.user_id
            sess["user_name"] = self.test_name
            sess["user_email"] = self.test_email

        # 1. Apply suggested allocation via POST
        post_data = {
            "action": "apply_suggested",
            "income": "60000",
            "cat_Rent": "15000",
            "cat_Food": "7200",
            "cat_Transport": "3600",
            "cat_Utilities": "4200",
            "cat_Shopping": "6000",
            "cat_Entertainment": "4800",
            "cat_Healthcare": "3600",
            "cat_Other": "3600"
        }
        res_apply = client.post("/smart-budget", data=post_data, follow_redirects=True)
        self.assertEqual(res_apply.status_code, 200)

        # Verify in SQLite
        rent_budget = execute_one(
            "SELECT amount FROM budgets WHERE user_id = ? AND category = 'Rent';",
            (self.__class__.user_id,)
        )
        self.assertIsNotNone(rent_budget)
        self.assertEqual(float(rent_budget["amount"]), 15000.0)

        # 2. Apply custom allocation via POST
        custom_data = {
            "action": "apply_custom",
            "income": "60000",
            "custom_Rent": "18000",
            "custom_Food": "9000",
            "custom_Transport": "4000",
            "custom_Utilities": "5000",
            "custom_Shopping": "4000",
            "custom_Entertainment": "3000",
            "custom_Healthcare": "2000",
            "custom_Other": "1000"
        }
        res_custom = client.post("/smart-budget", data=custom_data, follow_redirects=True)
        self.assertEqual(res_custom.status_code, 200)

        updated_rent = execute_one(
            "SELECT amount FROM budgets WHERE user_id = ? AND category = 'Rent';",
            (self.__class__.user_id,)
        )
        self.assertEqual(float(updated_rent["amount"]), 18000.0)

        # 3. Test 404 handler
        res_404 = client.get("/non_existent_page_12345")
        self.assertEqual(res_404.status_code, 404)
        self.assertIn(b"404 - Page Not Found", res_404.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
