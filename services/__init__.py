# Services package
from .auth_service import register_user, authenticate_user, get_user_by_id, get_user_profile, update_user_profile
from .finance_service import (
    add_income, update_income, delete_income, get_user_income_list, get_total_income,
    add_expense, update_expense, delete_expense, get_user_expense_list, get_total_expenses, get_category_expenses,
    set_budget, delete_budget, apply_batch_budgets, get_user_budgets, get_budget_comparison,
    add_financial_goal, update_financial_goal, delete_financial_goal, get_user_goals,
    get_financial_summary
)
from .investment_service import get_all_investments, get_investment_by_id, search_and_filter_investments
from .recommendation_service import calculate_investment_capacity, get_personalized_recommendations
from .dashboard_service import get_dashboard_data
