"""Recommendation Engine leveraging Data Structures and Algorithms.
Uses a Priority Queue (Max-Heap) for O(log n) insertion and ranking.
Calculates multi-attribute compatibility scores (0-100) and transparent
explainability rationale. This is criteria matching, NOT guaranteed returns.
"""

import heapq
from typing import Any, Dict, List, Optional, Tuple


class RecommendationPriorityQueue:
    """Priority Queue implementation using a binary heap (heapq).
    Maintains items ordered by descending matching score (max-heap behavior).
    Complexity:
      - Push: O(log n)
      - Pop: O(log n)
      - Peek: O(1)
    """

    def __init__(self):
        self._heap: List[Tuple[float, int, Dict[str, Any]]] = []
        self._counter = 0  # Tie-breaker for identical scores

    def push(self, score: float, item: Dict[str, Any]) -> None:
        """Push an item with priority `score`. Negates score to simulate max-heap."""
        heapq.heappush(self._heap, (-score, self._counter, item))
        self._counter += 1

    def pop(self) -> Tuple[float, Dict[str, Any]]:
        """Remove and return the highest-scoring (score, item) tuple."""
        if not self._heap:
            raise IndexError("Pop from empty priority queue")
        neg_score, _, item = heapq.heappop(self._heap)
        return (-neg_score, item)

    def is_empty(self) -> bool:
        return len(self._heap) == 0

    def size(self) -> int:
        return len(self._heap)


def calculate_compatibility(
    investment: Dict[str, Any],
    user_risk: str,
    user_horizon: str,
    user_goal: str,
    available_capacity: float
) -> Tuple[float, List[str], Dict[str, float]]:
    """Calculates multi-factor compatibility score (0-100) and rationale.
    Component Weights:
      1. Risk Match: 30 points
      2. Capacity / Amount Match: 25 points
      3. Horizon / Duration Match: 20 points
      4. Goal Alignment: 15 points
      5. Liquidity Match: 10 points
    Total = 100 points
    """
    reasons: List[str] = []
    scores_breakdown: Dict[str, float] = {}

    inv_risk = str(investment.get("risk_level", "MEDIUM")).upper()
    inv_duration = str(investment.get("duration", "MEDIUM")).upper()
    inv_min_amount = float(investment.get("minimum_amount", 0))
    inv_goal = str(investment.get("suitable_goal", "Wealth Creation")).lower()
    inv_liquidity = str(investment.get("liquidity", "HIGH")).upper()

    user_risk_clean = user_risk.upper()
    user_horizon_clean = user_horizon.upper()
    user_goal_clean = user_goal.lower()

    # 1. RISK MATCH (Max 30 pts)
    risk_score = 0.0
    if inv_risk == user_risk_clean:
        risk_score = 30.0
        reasons.append(f"Directly matches your {user_risk_clean} risk profile.")
    elif user_risk_clean == "HIGH" and inv_risk == "MEDIUM":
        risk_score = 24.0
        reasons.append("Medium-risk asset provides balanced stability for your high-risk profile.")
    elif user_risk_clean == "HIGH" and inv_risk == "LOW":
        risk_score = 18.0
        reasons.append("Low-risk allocation provides capital preservation anchor.")
    elif user_risk_clean == "MEDIUM" and inv_risk == "LOW":
        risk_score = 25.0
        reasons.append("Low-risk option provides safe, predictable capital growth.")
    else:
        # Investment risk exceeds user profile (e.g. LOW user, HIGH inv)
        risk_score = 0.0
        reasons.append(f"Caution: Risk level ({inv_risk}) exceeds your stated tolerance ({user_risk_clean}).")

    scores_breakdown["risk_score"] = risk_score

    # 2. AMOUNT / CAPACITY MATCH (Max 25 pts)
    amount_score = 0.0
    if available_capacity <= 0:
        if inv_min_amount <= 1000:
            amount_score = 15.0
            reasons.append(f"Accessible entry requirement (₹{inv_min_amount:,.0f}) suitable for disciplined start.")
        else:
            amount_score = 5.0
            reasons.append(f"Requires ₹{inv_min_amount:,.0f} minimum commitment; expand savings capacity.")
    elif inv_min_amount <= available_capacity:
        ratio = inv_min_amount / available_capacity
        if ratio <= 0.3:
            amount_score = 25.0
            reasons.append(f"Easily affordable: requires only ₹{inv_min_amount:,.0f} of your ₹{available_capacity:,.0f} capacity.")
        elif ratio <= 0.7:
            amount_score = 22.0
            reasons.append(f"Comfortably within your ₹{available_capacity:,.0f} monthly investment capacity.")
        else:
            amount_score = 18.0
            reasons.append(f"Affordable (₹{inv_min_amount:,.0f}) within current investment capacity.")
    else:
        amount_score = 0.0
        reasons.append(f"Minimum requirement (₹{inv_min_amount:,.0f}) exceeds current capacity (₹{available_capacity:,.0f}).")

    scores_breakdown["amount_score"] = amount_score

    # 3. DURATION MATCH (Max 20 pts)
    duration_score = 0.0
    duration_levels = {"SHORT": 1, "MEDIUM": 2, "LONG": 3}
    user_d_lvl = duration_levels.get(user_horizon_clean, 2)
    inv_d_lvl = duration_levels.get(inv_duration, 2)
    diff = abs(user_d_lvl - inv_d_lvl)

    if diff == 0:
        duration_score = 20.0
        reasons.append(f"Investment horizon ({inv_duration}) aligns with your target timeline.")
    elif diff == 1:
        duration_score = 12.0
        reasons.append(f"Investment tenure ({inv_duration}) is reasonably compatible with your horizon.")
    else:
        duration_score = 6.0
        reasons.append(f"Tenure ({inv_duration}) differs from your {user_horizon_clean} target horizon.")

    scores_breakdown["duration_score"] = duration_score

    # 4. GOAL ALIGNMENT (Max 15 pts)
    goal_score = 0.0
    if inv_goal in user_goal_clean or user_goal_clean in inv_goal:
        goal_score = 15.0
        reasons.append(f"Specifically suited for your primary goal of {user_goal.title()}.")
    elif "wealth creation" in inv_goal or "wealth creation" in user_goal_clean:
        goal_score = 12.0
        reasons.append("Versatile wealth generation asset applicable to your financial objective.")
    else:
        goal_score = 8.0
        reasons.append("Provides asset-class diversification supporting your overarching goal.")

    scores_breakdown["goal_score"] = goal_score

    # 5. LIQUIDITY MATCH (Max 10 pts)
    liquidity_score = 0.0
    is_emergency = "emergency" in user_goal_clean or user_horizon_clean == "SHORT"
    if is_emergency:
        if inv_liquidity == "HIGH":
            liquidity_score = 10.0
            reasons.append("High liquidity allows rapid redemption whenever needed.")
        elif inv_liquidity == "MEDIUM":
            liquidity_score = 5.0
            reasons.append("Moderate liquidity allows redemption within standard settlement cycles.")
        else:
            liquidity_score = 0.0
            reasons.append("Lock-in period / lower liquidity makes this less ideal for sudden cash needs.")
    else:
        # Long-term goals benefit from holding periods
        if inv_liquidity in ("HIGH", "MEDIUM"):
            liquidity_score = 10.0
            reasons.append(f"{inv_liquidity.title()} liquidity maintains portfolio flexibility.")
        else:
            liquidity_score = 8.0
            reasons.append("Structured lock-in instills long-term compounding discipline.")

    scores_breakdown["liquidity_score"] = liquidity_score

    total_score = round(risk_score + amount_score + duration_score + goal_score + liquidity_score, 1)
    total_score = min(100.0, max(0.0, total_score))

    return total_score, reasons, scores_breakdown


def generate_recommendations(
    investments: List[Dict[str, Any]],
    user_risk: str,
    user_horizon: str,
    user_goal: str,
    available_capacity: float,
    top_k: int = 6
) -> List[Dict[str, Any]]:
    """Runs the full DSA recommendation pipeline:
    1. Filter out completely ineligible investments (e.g. strict risk ceiling violation)
    2. Score remaining candidates across 5 criteria
    3. Push into Priority Queue (Max-Heap)
    4. Pop top K items in O(K log N) time
    """
    pq = RecommendationPriorityQueue()

    for inv in investments:
        # Reject candidates that violate strict risk ceiling (e.g. LOW risk user cannot get HIGH risk)
        inv_risk = str(inv.get("risk_level", "MEDIUM")).upper()
        if user_risk.upper() == "LOW" and inv_risk == "HIGH":
            continue

        score, reasons, breakdown = calculate_compatibility(
            investment=inv,
            user_risk=user_risk,
            user_horizon=user_horizon,
            user_goal=user_goal,
            available_capacity=available_capacity
        )

        # Create enriched result copy
        scored_item = dict(inv)
        scored_item["score"] = score
        scored_item["reasons"] = reasons
        scored_item["score_breakdown"] = breakdown

        pq.push(score, scored_item)

    ranked_recommendations: List[Dict[str, Any]] = []
    while not pq.is_empty() and len(ranked_recommendations) < top_k:
        score, item = pq.pop()
        ranked_recommendations.append(item)

    return ranked_recommendations
