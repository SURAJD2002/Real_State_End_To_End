"""
Financial Feasibility Pro-Forma Engine
Calculates institutional real estate underwriting metrics:
Gross Development Value (GDV), Total Development Cost (TDC), Developer Margin, and Equity IRR.
"""

from typing import Dict, Any


def calculate_financial_proforma(
    permissible_bua_sqm: float,
    premium_fsi: float = 0.5,
    avg_sale_rate_sqm: float = 185000.0,      # ₹185,000 / sqm (~₹17,180 / sqft)
    civil_cost_sqm: float = 46000.0,           # ₹46,000 / sqm (~₹4,270 / sqft)
    annual_interest_rate_pct: float = 11.5,
    tenure_months: int = 36
) -> Dict[str, Any]:
    """
    Computes institutional capital budgeting and return metrics for Mumbai development.
    """
    # 1. Capital Revenue (GDV)
    # Permissible BUA * Average Sale Realization Rate
    gdv = round(permissible_bua_sqm * avg_sale_rate_sqm, 2)

    # 2. Hard Civil Construction Cost
    civil_cost = round(permissible_bua_sqm * civil_cost_sqm, 2)

    # 3. Statutory Municipal Approval Premiums (DCPR 2034)
    # 50% of Ready Reckoner Rate for Premium FSI + Scrutiny & Development charges
    approx_ready_reckoner_rate = avg_sale_rate_sqm * 0.45
    premium_bua = permissible_bua_sqm * (premium_fsi / (1.0 + premium_fsi + 0.5))
    statutory_premiums = round(premium_bua * (approx_ready_reckoner_rate * 0.50) + (permissible_bua_sqm * 3500.0), 2)

    # 4. Soft Costs (Architectural, Legal, Sales & Marketing ~ 7% of GDV)
    soft_costs = round(gdv * 0.07, 2)

    # 5. Financing & Debt Service Cost (~ 40% debt at 11.5% for half duration)
    debt_amount = (civil_cost + statutory_premiums) * 0.50
    finance_cost = round(debt_amount * (annual_interest_rate_pct / 100.0) * (tenure_months / 24.0), 2)

    # 6. Total Development Cost (TDC)
    tdc = round(civil_cost + statutory_premiums + soft_costs + finance_cost, 2)

    # 7. Profitability & Returns
    net_profit = round(gdv - tdc, 2)
    margin_pct = round((net_profit / gdv) * 100.0, 2) if gdv > 0 else 0.0

    # Simplified project equity IRR estimation (Assuming 40% Equity sponsor capital)
    equity_invested = tdc * 0.40
    # Over 3 years: ((net_profit + equity) / equity) ^ (1/3) - 1
    if equity_invested > 0:
        multiplier = (equity_invested + net_profit) / equity_invested
        irr_pct = round(((multiplier ** (12.0 / tenure_months)) - 1.0) * 100.0, 2)
    else:
        irr_pct = 0.0

    return {
        "currency": "INR",
        "grossDevelopmentValue": gdv,
        "civilConstructionCost": civil_cost,
        "statutoryApprovalPremiums": statutory_premiums,
        "softCostsAndMarketing": soft_costs,
        "financingCost": finance_cost,
        "totalDevelopmentCost": tdc,
        "netMarginValue": net_profit,
        "netMarginPercent": margin_pct,
        "equityIRRPercent": irr_pct
    }
