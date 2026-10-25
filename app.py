"""Smart Personal Finance & Budget Management System.
Flask Application Entrypoint & Web Routing.
"""

from functools import wraps
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from config.config import PORT, SECRET_KEY
from database.database import init_db
from models.expense import VALID_CATEGORIES
from services.auth_service import (
    authenticate_user,
    get_user_by_id,
    get_user_profile,
    register_user,
    update_user_profile,
)
from services.dashboard_service import get_dashboard_data
from services.finance_service import (
    add_expense,
    add_financial_goal,
    add_income,
    delete_budget,
    delete_expense,
    delete_financial_goal,
    delete_income,
    get_budget_comparison,
    get_category_expenses,
    get_financial_summary,
    get_total_expenses,
    get_total_income,
    get_user_budgets,
    get_user_expense_list,
    get_user_goals,
    get_user_income_list,
    set_budget,
    apply_batch_budgets,
    update_expense,
    update_financial_goal,
    update_income,
)
from services.investment_service import get_investment_by_id, search_and_filter_investments
from services.recommendation_service import (
    calculate_investment_capacity,
    get_personalized_recommendations,
)
from services.status_service import get_system_status
from api.alpha_vantage import fetch_stock_quote, get_all_cached_stocks, DEFAULT_SYMBOLS
from api.gold_api import fetch_gold_price
from api.news_api import fetch_financial_news
from api.mf_api import fetch_mutual_fund_details, get_cached_mutual_funds, search_mutual_funds
from algorithms.budget_allocation import calculate_algorithmic_budget, ALLOCATION_STRATEGIES

# Initialize Flask application
app = Flask(__name__)
app.secret_key = SECRET_KEY


def login_required(f):
    """Decorator to enforce user authentication on protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ==================== AUTHENTICATION ROUTES ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html", name=name, email=email)

        success, message, user_id = register_user(name, email, password)
        if success:
            flash(message, "success")
            return redirect(url_for("login"))
        else:
            flash(message, "danger")
            return render_template("register.html", name=name, email=email)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        success, message, user_info = authenticate_user(email, password)
        if success and user_info:
            session["user_id"] = user_info["id"]
            session["user_name"] = user_info["name"]
            session["user_email"] = user_info["email"]
            flash(f"Welcome back, {user_info['name']}!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash(message, "danger")
            return render_template("login.html", email=email)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been securely logged out.", "info")
    return redirect(url_for("login"))


# ==================== MAIN DASHBOARD ====================

@app.route("/")
@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    dashboard_data = get_dashboard_data(user_id)
    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User"),
        data=dashboard_data
    )


# ==================== INCOME MANAGEMENT ====================

@app.route("/income", methods=["GET", "POST"])
@login_required
def income():
    user_id = session["user_id"]

    if request.method == "POST":
        amount_str = request.form.get("amount", "0")
        source = request.form.get("source", "").strip()
        date = request.form.get("date", "").strip()
        desc = request.form.get("description", "").strip()

        try:
            amount = float(amount_str)
            add_income(user_id, amount, source, date, desc)
            flash(f"Income of ₹{amount:,.2f} recorded successfully.", "success")
            return redirect(url_for("income"))
        except ValueError as e:
            flash(str(e), "danger")

    income_entries = get_user_income_list(user_id)
    total_income = get_total_income(user_id)
    return render_template(
        "income.html",
        income_entries=income_entries,
        total_income=total_income
    )


@app.route("/income/delete/<int:income_id>", methods=["POST"])
@login_required
def delete_income_route(income_id):
    user_id = session["user_id"]
    if delete_income(income_id, user_id):
        flash("Income entry deleted.", "info")
    else:
        flash("Unable to delete income entry.", "danger")
    return redirect(url_for("income"))


# ==================== EXPENSE MANAGEMENT ====================

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    user_id = session["user_id"]

    if request.method == "POST":
        amount_str = request.form.get("amount", "0")
        category = request.form.get("category", "").strip()
        date = request.form.get("date", "").strip()
        desc = request.form.get("description", "").strip()

        try:
            amount = float(amount_str)
            add_expense(user_id, amount, category, date, desc)
            flash(f"Expense of ₹{amount:,.2f} added to {category}.", "success")
            return redirect(url_for("expenses"))
        except ValueError as e:
            flash(str(e), "danger")

    expense_entries = get_user_expense_list(user_id)
    total_expenses = get_total_expenses(user_id)
    category_totals = get_category_expenses(user_id)

    return render_template(
        "expenses.html",
        expense_entries=expense_entries,
        total_expenses=total_expenses,
        category_totals=category_totals,
        categories=VALID_CATEGORIES
    )


@app.route("/expenses/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense_route(expense_id):
    user_id = session["user_id"]
    if delete_expense(expense_id, user_id):
        flash("Expense entry deleted.", "info")
    else:
        flash("Unable to delete expense entry.", "danger")
    return redirect(url_for("expenses"))


# ==================== BUDGET MANAGEMENT ====================

@app.route("/budget", methods=["GET", "POST"])
@login_required
def budget():
    user_id = session["user_id"]

    if request.method == "POST":
        category = request.form.get("category", "").strip()
        amount_str = request.form.get("amount", "0")

        try:
            amount = float(amount_str)
            set_budget(user_id, category, amount)
            flash(f"Budget for {category} set to ₹{amount:,.2f}.", "success")
            return redirect(url_for("budget"))
        except ValueError as e:
            flash(str(e), "danger")

    budget_comparison = get_budget_comparison(user_id)
    total_budgeted = sum(b["budgeted"] for b in budget_comparison)
    total_spent = sum(b["spent"] for b in budget_comparison)

    chart_labels = [b["category"] for b in budget_comparison]
    chart_allocated = [b["budgeted"] for b in budget_comparison]
    chart_spent = [b["spent"] for b in budget_comparison]

    return render_template(
        "budget.html",
        budget_comparison=budget_comparison,
        total_budgeted=total_budgeted,
        total_spent=total_spent,
        chart_labels=chart_labels,
        chart_allocated=chart_allocated,
        chart_spent=chart_spent,
        categories=VALID_CATEGORIES
    )


@app.route("/budget/delete/<int:budget_id>", methods=["POST"])
@login_required
def delete_budget_route(budget_id):
    user_id = session["user_id"]
    if delete_budget(budget_id, user_id):
        flash("Budget target removed.", "info")
    else:
        flash("Unable to remove budget target.", "danger")
    return redirect(url_for("budget"))


# ==================== SMART BUDGET ALLOCATOR ====================

@app.route("/smart-budget", methods=["GET", "POST"])
@login_required
def smart_budget():
    user_id = session["user_id"]
    user_recorded_income = get_total_income(user_id)

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "apply_suggested":
            budgets_to_apply = {}
            for cat in VALID_CATEGORIES:
                val_str = request.form.get(f"cat_{cat}")
                if val_str:
                    try:
                        budgets_to_apply[cat] = float(val_str)
                    except ValueError:
                        pass
            count = apply_batch_budgets(user_id, budgets_to_apply)
            flash(f"Successfully applied {count} strategic budget allocations to your active tracking!", "success")
            return redirect(url_for("budget"))

        elif action == "apply_custom":
            custom_budgets = {}
            for cat in VALID_CATEGORIES:
                val_str = request.form.get(f"custom_{cat}")
                if val_str:
                    try:
                        custom_budgets[cat] = float(val_str)
                    except ValueError:
                        pass
            count = apply_batch_budgets(user_id, custom_budgets)
            flash(f"Successfully saved {count} tailored category budget allocations!", "success")
            return redirect(url_for("budget"))

    # GET logic
    income_param = request.args.get("income", "").strip()
    strategy_key = request.args.get("strategy", "balanced_50_30_20").strip()

    if income_param:
        try:
            income_val = float(income_param)
        except ValueError:
            income_val = user_recorded_income if user_recorded_income > 0 else 50000.0
    else:
        income_val = user_recorded_income if user_recorded_income > 0 else 50000.0

    allocation = calculate_algorithmic_budget(income_val, strategy_key)
    existing_budgets = get_user_budgets(user_id)
    current_budgets_map = {b["category"]: float(b["amount"]) for b in existing_budgets}

    return render_template(
        "smart_budget.html",
        income=income_val,
        user_recorded_income=user_recorded_income,
        strategy_key=strategy_key,
        allocation=allocation,
        available_strategies=allocation["available_strategies"],
        current_budgets_map=current_budgets_map,
        valid_categories=VALID_CATEGORIES
    )


# ==================== FINANCIAL GOALS ====================

@app.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    user_id = session["user_id"]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        target_str = request.form.get("target_amount", "0")
        current_str = request.form.get("current_amount", "0")
        target_date = request.form.get("target_date", "").strip()
        category = request.form.get("category", "Wealth Creation").strip()

        try:
            target_amount = float(target_str)
            current_amount = float(current_str)
            add_financial_goal(user_id, name, target_amount, current_amount, target_date, category)
            flash(f"Goal '{name}' created successfully!", "success")
            return redirect(url_for("goals"))
        except ValueError as e:
            flash(str(e), "danger")

    user_goals = get_user_goals(user_id)
    return render_template("goals.html", goals=user_goals)


@app.route("/goals/update/<int:goal_id>", methods=["POST"])
@login_required
def update_goal_route(goal_id):
    user_id = session["user_id"]
    name = request.form.get("name", "").strip()
    target_str = request.form.get("target_amount", "0")
    current_str = request.form.get("current_amount", "0")
    target_date = request.form.get("target_date", "").strip()
    category = request.form.get("category", "Wealth Creation").strip()
    status = request.form.get("status", "IN_PROGRESS")

    try:
        target_amount = float(target_str)
        current_amount = float(current_str)
        update_financial_goal(goal_id, user_id, name, target_amount, current_amount, target_date, category, status)
        flash("Goal updated successfully.", "success")
    except ValueError as e:
        flash(str(e), "danger")

    return redirect(url_for("goals"))


@app.route("/goals/delete/<int:goal_id>", methods=["POST"])
@login_required
def delete_goal_route(goal_id):
    user_id = session["user_id"]
    if delete_financial_goal(goal_id, user_id):
        flash("Financial goal removed.", "info")
    else:
        flash("Unable to remove goal.", "danger")
    return redirect(url_for("goals"))


# ==================== INVESTMENT CATALOG ====================

@app.route("/investments")
@login_required
def investments():
    q = request.args.get("q", "").strip()
    risk = request.args.get("risk", "ALL").strip()
    category = request.args.get("category", "ALL").strip()
    duration = request.args.get("duration", "ALL").strip()
    sort_by = request.args.get("sort_by", "minimum_amount").strip()
    max_amount_str = request.args.get("max_amount", "").strip()

    max_amount = None
    if max_amount_str:
        try:
            max_amount = float(max_amount_str)
        except ValueError:
            pass

    items = search_and_filter_investments(
        query=q,
        risk=risk,
        category=category,
        duration=duration,
        max_amount=max_amount,
        sort_by=sort_by
    )

    return render_template(
        "investments.html",
        investments=items,
        query=q,
        risk=risk,
        category=category,
        duration=duration,
        sort_by=sort_by,
        max_amount=max_amount_str
    )


# ==================== RECOMMENDATION ENGINE ====================

@app.route("/recommendations", methods=["GET", "POST"])
@login_required
def recommendations():
    user_id = session["user_id"]
    profile = get_user_profile(user_id)
    capacity_info = calculate_investment_capacity(user_id)

    # Defaults from profile & calculation
    risk = profile.get("risk_tolerance", "MEDIUM")
    duration = profile.get("investment_horizon", "LONG")
    goal = profile.get("primary_goal", "Wealth Creation")
    custom_capacity = capacity_info["available_capacity"]

    if request.method == "POST":
        risk = request.form.get("risk", risk)
        duration = request.form.get("duration", duration)
        goal = request.form.get("goal", goal)
        cap_str = request.form.get("capacity", "")
        if cap_str:
            try:
                custom_capacity = float(cap_str)
            except ValueError:
                pass

    rec_payload = get_personalized_recommendations(
        user_id=user_id,
        override_risk=risk,
        override_duration=duration,
        override_goal=goal,
        override_capacity=custom_capacity
    )

    return render_template(
        "recommendations.html",
        recommendations=rec_payload["recommendations"],
        capacity_info=capacity_info,
        selected_risk=risk,
        selected_duration=duration,
        selected_goal=goal,
        selected_capacity=custom_capacity,
        disclaimer=rec_payload["disclaimer"]
    )


# ==================== LIVE MARKET DATA (ALPHA VANTAGE) ====================

@app.route("/market", methods=["GET", "POST"])
@login_required
def market():
    symbol_query = request.args.get("symbol", "").strip() or request.form.get("symbol", "").strip()
    active_quote = None

    if symbol_query:
        active_quote = fetch_stock_quote(symbol_query)

    cached_stocks = get_all_cached_stocks()
    return render_template(
        "market.html",
        active_quote=active_quote,
        symbol_query=symbol_query,
        cached_stocks=cached_stocks,
        default_symbols=DEFAULT_SYMBOLS
    )


# ==================== GOLD PRICE (GOLDAPI) ====================

@app.route("/gold", methods=["GET", "POST"])
@login_required
def gold():
    gold_data = fetch_gold_price()
    return render_template("gold.html", gold_data=gold_data)


# ==================== FINANCIAL NEWS (NEWSAPI) ====================

@app.route("/news")
@login_required
def news():
    news_payload = fetch_financial_news(limit=15)
    return render_template(
        "news.html",
        articles=news_payload.get("articles", []),
        is_cached=news_payload.get("is_cached", False),
        notice=news_payload.get("notice")
    )


# ==================== MUTUAL FUNDS (MFAPI) ====================

@app.route("/mutual-funds", methods=["GET", "POST"])
@login_required
def mutual_funds():
    search_q = request.args.get("q", "").strip() or request.form.get("q", "").strip()
    scheme_code_param = request.args.get("code")

    scheme_details = None
    if scheme_code_param:
        try:
            scheme_details = fetch_mutual_fund_details(int(scheme_code_param))
        except ValueError:
            pass

    search_results = []
    if search_q:
        search_results = search_mutual_funds(search_q)

    cached_funds = get_cached_mutual_funds()

    return render_template(
        "mutual_funds.html",
        search_results=search_results,
        scheme_details=scheme_details,
        cached_funds=cached_funds,
        search_query=search_q
    )


# ==================== BACKEND STATUS & DIAGNOSTICS ====================

@app.route("/status")
def status():
    """System health & diagnostic overview."""
    system_status = get_system_status()
    return render_template("status.html", status=system_status)


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


# ==================== USER PROFILE & SETTINGS ====================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = session["user_id"]
    user_info = get_user_by_id(user_id)

    if request.method == "POST":
        risk = request.form.get("risk_tolerance", "MEDIUM")
        horizon = request.form.get("investment_horizon", "LONG")
        goal = request.form.get("primary_goal", "Wealth Creation")
        emergency_months = int(request.form.get("emergency_fund_months", 3))

        update_user_profile(user_id, risk, horizon, goal, emergency_months)
        flash("Financial profile updated successfully.", "success")
        return redirect(url_for("profile"))

    user_profile = get_user_profile(user_id)
    return render_template(
        "profile.html",
        user_info=user_info,
        profile=user_profile
    )


# ==================== STARTUP BOOTSTRAP ====================

# Automatically bootstrap database on load
init_db()

if __name__ == "__main__":
    print(f"Starting Smart Personal Finance & Budget Management System on http://127.0.0.1:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=True)
