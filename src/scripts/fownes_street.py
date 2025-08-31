from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from dateutil.relativedelta import relativedelta

# ========== Data Models (Typed) ==========


@dataclass(frozen=True)
class Assumptions:
    # Property & ownership
    purchase_date: date
    rental_start_date: date
    analysis_start_sale_date: date  # "sell now" date
    projection_years: int
    share: float
    purchase_price_whole: float
    current_estimated_value_whole: float
    current_annual_rent_whole: float

    # Selling costs
    selling_cost_rate: float  # e.g. 0.02

    # Rental economics (as % of gross rent)
    agent_fee_rate: float  # e.g. 0.12
    maintenance_rate: float  # e.g. 0.08
    voids_rate: float  # e.g. 0.04
    other_costs_rate: float  # e.g. 0.01
    rental_growth_rate: float  # e.g. 0.03
    income_tax_rate: float  # e.g. 0.20

    # Market & investment
    property_growth_rate: float  # e.g. 0.02
    portfolio_net_return_rate: float  # e.g. 0.0425 (after tax/fees)

    # CGT assumptions
    final_period_exemption_months: int  # usually 9 months
    annual_exempt_amount: float  # AEA (e.g. £3,000)
    residential_cgt_rate_conservative: float  # e.g. 0.24


@dataclass(frozen=True)
class CgtBreakdown:
    gross_gain: float
    ppr_fraction: float
    exempt_gain: float
    chargeable_gain: float
    cgt: float
    selling_costs: float


@dataclass(frozen=True)
class ProjectionRow:
    year: int
    date_assumed: date
    sell_invest_portfolio_value: float
    keep_property_value_pre_tax: float
    keep_cum_cash_reserve: float
    keep_est_cgt_if_sold: float
    keep_after_tax_liquidation_value: float


@dataclass(frozen=True)
class SensitivityRow:
    property_growth: float  # decimal (0.02 = 2%)
    portfolio_net_return: float  # decimal
    sell_invest_end_value: float
    keep_end_value: float
    keep_minus_sell: float


@dataclass(frozen=True)
class SaleNowSummary:
    assumed_sale_date: date
    your_50_sale_price: float
    selling_costs: float
    gross_gain_after_selling_costs: float
    ppr_relief_fraction: float
    exempt_gain_ppr: float
    chargeable_gain_after_aea: float
    cgt_at_conservative_rate: float
    net_cash_after_cgt_and_costs: float


@dataclass(frozen=True)
class ProjectionOutput:
    sale_now_summary: SaleNowSummary
    year_by_year: list[ProjectionRow]
    sensitivity: list[SensitivityRow]


# ========== Helpers ==========


def _months_between(start: date, end: date) -> int:
    """Whole months between start and end; +1 if end.day >= start.day
    (to mirror your original logic)."""
    if end < start:
        return 0
    rd = relativedelta(end, start)
    months = rd.years * 12 + rd.months
    if rd.days >= 0:
        months += 1
    return months


def compute_ppr_fraction(
    purchase_dt: date,
    sale_dt: date,
    occupied_end_dt: date,
    final_months: int,
) -> float:
    total_months = _months_between(purchase_dt, sale_dt)
    occupied_months = _months_between(purchase_dt, min(occupied_end_dt, sale_dt))
    ppr_months = min(total_months, occupied_months + final_months)
    return 0.0 if total_months == 0 else ppr_months / total_months


def compute_cgt(
    *,
    purchase_dt: date,
    sale_dt: date,
    base_cost_share: float,
    sale_price_share: float,
    occupied_end_dt: date,
    final_months: int,
    annual_exempt: float,
    cgt_rate: float,
    selling_cost_rate: float,
) -> CgtBreakdown:
    selling_costs = selling_cost_rate * sale_price_share  # allowable, reduces gain
    gross_gain = sale_price_share - base_cost_share - selling_costs
    ppr_fraction = compute_ppr_fraction(
        purchase_dt, sale_dt, occupied_end_dt, final_months
    )
    exempt_gain = gross_gain * ppr_fraction
    chargeable_gain = max(0.0, gross_gain - exempt_gain - annual_exempt)
    cgt = chargeable_gain * cgt_rate
    return CgtBreakdown(
        gross_gain=gross_gain,
        ppr_fraction=ppr_fraction,
        exempt_gain=exempt_gain,
        chargeable_gain=chargeable_gain,
        cgt=cgt,
        selling_costs=selling_costs,
    )


# ========== Core Projection ==========


def run_projection(a: Assumptions) -> ProjectionOutput:
    # Derived (your share)
    purchase_price_share = a.purchase_price_whole * a.share
    current_value_share = a.current_estimated_value_whole * a.share
    current_rent_share = a.current_annual_rent_whole * a.share

    # Immediate sale (year 0)
    sale_now = compute_cgt(
        purchase_dt=a.purchase_date,
        sale_dt=a.analysis_start_sale_date,
        base_cost_share=purchase_price_share,
        sale_price_share=current_value_share,
        occupied_end_dt=a.rental_start_date,
        final_months=a.final_period_exemption_months,
        annual_exempt=a.annual_exempt_amount,
        cgt_rate=a.residential_cgt_rate_conservative,
        selling_cost_rate=a.selling_cost_rate,
    )
    net_proceeds_now = current_value_share - sale_now.cgt - sale_now.selling_costs

    years = a.projection_years

    # Strategy A: Sell now & invest
    sell_invest_values: list[float] = [net_proceeds_now]
    for _ in range(1, years + 1):
        sell_invest_values.append(
            sell_invest_values[-1] * (1 + a.portfolio_net_return_rate)
        )

    # Strategy B: Keep & rent
    prop_values: list[float] = [current_value_share]
    rent = current_rent_share
    cash_reserve = 0.0  # reinvested net rent
    after_tax_cash_each_year: list[float] = []

    expense_rate_total = (
        a.agent_fee_rate + a.maintenance_rate + a.voids_rate + a.other_costs_rate
    )

    for _ in range(1, years + 1):
        # Property growth
        next_prop_val = prop_values[-1] * (1 + a.property_growth_rate)
        prop_values.append(next_prop_val)

        # Rental economics (this year)
        net_pre_tax = rent * (1 - expense_rate_total)
        tax = max(0.0, net_pre_tax) * a.income_tax_rate
        net_after_tax = net_pre_tax - tax
        after_tax_cash_each_year.append(net_after_tax)

        cash_reserve = (cash_reserve + net_after_tax) * (
            1 + a.portfolio_net_return_rate
        )
        rent *= 1 + a.rental_growth_rate

    # Yearly dates
    dates: list[date] = [
        a.analysis_start_sale_date + relativedelta(years=yr)
        for yr in range(0, years + 1)
    ]

    # Track cumulative cash by year (same compounding as above, but stored by step)
    cash_reserve_by_year: list[float] = [0.0]
    tmp_cash = 0.0
    rent_tmp = current_rent_share
    for _ in range(1, years + 1):
        net_pre_tax = rent_tmp * (1 - expense_rate_total)
        tax = max(0.0, net_pre_tax) * a.income_tax_rate
        net_after_tax = net_pre_tax - tax
        tmp_cash = (tmp_cash + net_after_tax) * (1 + a.portfolio_net_return_rate)
        cash_reserve_by_year.append(tmp_cash)
        rent_tmp *= 1 + a.rental_growth_rate

    # Keep-strategy liquidation value each year
    keep_capital_gains_taxes: list[float] = []
    keep_after_tax_values: list[float] = []
    for i, sale_dt in enumerate(dates):
        sale_price_share_i = prop_values[i]
        cgt_i = compute_cgt(
            purchase_dt=a.purchase_date,
            sale_dt=sale_dt,
            base_cost_share=purchase_price_share,
            sale_price_share=sale_price_share_i,
            occupied_end_dt=a.rental_start_date,
            final_months=a.final_period_exemption_months,
            annual_exempt=a.annual_exempt_amount,
            cgt_rate=a.residential_cgt_rate_conservative,
            selling_cost_rate=a.selling_cost_rate,
        )
        keep_capital_gains_taxes.append(cgt_i.cgt)
        net_property_after_sale = sale_price_share_i - cgt_i.cgt - cgt_i.selling_costs
        keep_after_tax_values.append(net_property_after_sale + cash_reserve_by_year[i])

    # Assemble rows
    rows: list[ProjectionRow] = []
    for i in range(years + 1):
        rows.append(
            ProjectionRow(
                year=i,
                date_assumed=dates[i],
                sell_invest_portfolio_value=sell_invest_values[i],
                keep_property_value_pre_tax=prop_values[i],
                keep_cum_cash_reserve=cash_reserve_by_year[i],
                keep_est_cgt_if_sold=keep_capital_gains_taxes[i],
                keep_after_tax_liquidation_value=keep_after_tax_values[i],
            )
        )

    # Sensitivity (Year N) grid
    sensitivity = run_sensitivity(
        a=a,
        net_proceeds_now=net_proceeds_now,
        current_value_share=current_value_share,
        current_rent_share=current_rent_share,
        purchase_price_share=purchase_price_share,
        expense_rate_total=expense_rate_total,
    )

    sale_now_summary = SaleNowSummary(
        assumed_sale_date=a.analysis_start_sale_date,
        your_50_sale_price=current_value_share,
        selling_costs=sale_now.selling_costs,
        gross_gain_after_selling_costs=sale_now.gross_gain,
        ppr_relief_fraction=sale_now.ppr_fraction,
        exempt_gain_ppr=sale_now.exempt_gain,
        chargeable_gain_after_aea=sale_now.chargeable_gain,
        cgt_at_conservative_rate=sale_now.cgt,
        net_cash_after_cgt_and_costs=net_proceeds_now,
    )

    return ProjectionOutput(
        sale_now_summary=sale_now_summary,
        year_by_year=rows,
        sensitivity=sensitivity,
    )


def run_sensitivity(
    *,
    a: Assumptions,
    net_proceeds_now: float,
    current_value_share: float,
    current_rent_share: float,
    purchase_price_share: float,
    expense_rate_total: float,
    property_growth_opts: tuple[float, ...] = (0.00, 0.02, 0.04),
    portfolio_return_opts: tuple[float, ...] = (0.03, 0.0425, 0.055),
) -> list[SensitivityRow]:
    """Compute Year-N outcomes across a small grid of property growth
    and portfolio returns."""
    years = a.projection_years

    def simulate_end(
        property_growth: float, portfolio_return: float
    ) -> tuple[float, float]:
        # Sell & invest
        portfolio = net_proceeds_now
        for _ in range(years):
            portfolio *= 1 + portfolio_return

        # Keep & rent
        prop_val = current_value_share
        r = current_rent_share
        cash = 0.0
        for _ in range(years):
            prop_val *= 1 + property_growth
            net_pre_tax = r * (1 - expense_rate_total)
            tax = max(0.0, net_pre_tax) * a.income_tax_rate
            net_after_tax = net_pre_tax - tax
            cash = (cash + net_after_tax) * (1 + portfolio_return)
            r *= 1 + a.rental_growth_rate

        sale_dt = a.analysis_start_sale_date + relativedelta(years=years)
        cgt = compute_cgt(
            purchase_dt=a.purchase_date,
            sale_dt=sale_dt,
            base_cost_share=purchase_price_share,
            sale_price_share=prop_val,
            occupied_end_dt=a.rental_start_date,
            final_months=a.final_period_exemption_months,
            annual_exempt=a.annual_exempt_amount,
            cgt_rate=a.residential_cgt_rate_conservative,
            selling_cost_rate=a.selling_cost_rate,
        ).cgt
        keep_liq = prop_val - cgt - a.selling_cost_rate * prop_val + cash
        return portfolio, keep_liq

    out: list[SensitivityRow] = []
    for g in property_growth_opts:
        for r in portfolio_return_opts:
            port_end, keep_end = simulate_end(g, r)
            out.append(
                SensitivityRow(
                    property_growth=g,
                    portfolio_net_return=r,
                    sell_invest_end_value=port_end,
                    keep_end_value=keep_end,
                    keep_minus_sell=keep_end - port_end,
                )
            )
    return out


# ========== Defaults matching your original inputs ==========

DEFAULT_ASSUMPTIONS = Assumptions(
    purchase_date=date(1984, 5, 1),  # May 1, 1984
    rental_start_date=date(2012, 7, 1),  # Jul 1, 2012
    analysis_start_sale_date=date(2025, 12, 31),  # Dec 31, 2025
    projection_years=10,
    share=0.50,
    purchase_price_whole=14_000.0,
    current_estimated_value_whole=650_000.0,
    current_annual_rent_whole=29_760.0,
    selling_cost_rate=0.02,
    agent_fee_rate=0.12,
    maintenance_rate=0.08,
    voids_rate=0.04,
    other_costs_rate=0.01,
    rental_growth_rate=0.03,
    income_tax_rate=0.20,
    property_growth_rate=0.02,
    portfolio_net_return_rate=0.0425,
    final_period_exemption_months=9,
    annual_exempt_amount=3_000.0,
    residential_cgt_rate_conservative=0.24,
)


def main() -> None:
    out = run_projection(DEFAULT_ASSUMPTIONS)

    # Pretty-print the sale-now summary
    s = out.sale_now_summary
    print("Sale-now summary:")
    print(f"  Assumed sale date:           {s.assumed_sale_date.isoformat()}")
    print(f"  Your 50% sale price:         £{s.your_50_sale_price:,.2f}")
    print(f"  Selling costs (2%):          £{s.selling_costs:,.2f}")
    print(f"  Gross gain (after costs):    £{s.gross_gain_after_selling_costs:,.2f}")
    print(f"  PPR relief fraction:         {s.ppr_relief_fraction:.4f}")
    print(f"  Exempt gain (PPR):           £{s.exempt_gain_ppr:,.2f}")
    print(f"  Chargeable gain (after AEA): £{s.chargeable_gain_after_aea:,.2f}")
    print(f"  CGT @24% (conservative):     £{s.cgt_at_conservative_rate:,.2f}")
    print(f"  Net cash after CGT & costs:  £{s.net_cash_after_cgt_and_costs:,.2f}")

    # Example: show final year comparison
    final = out.year_by_year[-1]
    print("\nYear-10 snapshot:")
    print(f"  Sell & invest value:         £{final.sell_invest_portfolio_value:,.0f}")
    print(
        f"  Keep after-tax liquidation:  £{final.keep_after_tax_liquidation_value:,.0f}"
    )

    # Example: one sensitivity row
    print("\nSensitivity (first 3 rows):")
    for row in out.sensitivity[:3]:
        print(
            f"  g={row.property_growth:.2%}, r={row.portfolio_net_return:.2%} -> "
            f"Sell £{row.sell_invest_end_value:,.0f}, Keep £{row.keep_end_value:,.0f}, "
            f"Δ £{row.keep_minus_sell:,.0f}"
        )



if __name__ == "__main__":
    main()
