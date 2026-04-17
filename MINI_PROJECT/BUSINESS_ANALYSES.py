"""
=============================================================================
                    SALES ANALYTICS DASHBOARD
                    Data Analyst & Python Expert
=============================================================================
Comprehensive sales analysis: data processing, statistical analysis,
business insights, and visualization on a synthetic 2023 dataset.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 1. SYNTHETIC DATA GENERATION
# ============================================================================

def generate_sales_data(n_records=365):
    np.random.seed(42)
    start_date = datetime(2023, 1, 1)
    dates      = [start_date + timedelta(days=x) for x in range(n_records)]
    products   = ['Product_A', 'Product_B', 'Product_C']
    regions    = ['North', 'South', 'East', 'West']
    base_prices = {'Product_A': 100, 'Product_B': 150, 'Product_C': 120}

    data = {
        'Date':       np.repeat(dates, len(products) * len(regions)),
        'Product':    np.tile(np.repeat(products, len(regions)), n_records),
        'Region':     np.tile(regions, n_records * len(products)),
        'Units_Sold': np.random.randint(10, 100, n_records * len(products) * len(regions)),
        'Discount':   np.random.uniform(0, 0.3,  n_records * len(products) * len(regions)),
    }
    df = pd.DataFrame(data)
    df['Price']        = df['Product'].map(base_prices)
    df['Cost_Per_Unit'] = df['Price'] * 0.6
    return df

# ============================================================================
# 2. DATA PROCESSING
# ============================================================================

def process_sales_data(df):
    df['Unit_Revenue']   = df['Price'] * (1 - df['Discount'])
    df['Total_Revenue']  = df['Unit_Revenue'] * df['Units_Sold']
    df['Total_Cost']     = df['Cost_Per_Unit'] * df['Units_Sold']
    df['Total_Profit']   = df['Total_Revenue'] - df['Total_Cost']
    df['Profit_Margin_%'] = (df['Total_Profit'] / df['Total_Revenue'] * 100).round(2)

    df['Date']        = pd.to_datetime(df['Date'])
    df['Month']       = df['Date'].dt.month
    df['Month_Name']  = df['Date'].dt.strftime('%B')
    df['Month_Abbr']  = df['Date'].dt.strftime('%b')
    df['Day_Of_Week'] = df['Date'].dt.day_name()
    df['Quarter']     = df['Date'].dt.quarter
    df['Week']        = df['Date'].dt.isocalendar().week
    return df

# ============================================================================
# 3. AGGREGATION & STATISTICS
# ============================================================================

def calculate_statistics(df):
    return {
        'Total_Revenue':        df['Total_Revenue'].sum(),
        'Average_Revenue':      df['Total_Revenue'].mean(),
        'Std_Dev_Revenue':      df['Total_Revenue'].std(),
        'Total_Profit':         df['Total_Profit'].sum(),
        'Average_Profit':       df['Total_Profit'].mean(),
        'Std_Dev_Profit':       df['Total_Profit'].std(),
        'Total_Units':          df['Units_Sold'].sum(),
        'Average_Profit_Margin': df['Profit_Margin_%'].mean(),
        'Overall_Discount_Rate': df['Discount'].mean() * 100,
    }

def aggregate_by_month(df):
    monthly = df.groupby(['Month', 'Month_Name', 'Month_Abbr']).agg(
        Total_Units=('Units_Sold',     'sum'),
        Revenue    =('Total_Revenue',  'sum'),
        Profit     =('Total_Profit',   'sum'),
        Avg_Profit_Margin_pct=('Profit_Margin_%', 'mean'),
        Avg_Discount_pct     =('Discount',        'mean'),
    ).reset_index()
    monthly['Avg_Discount_pct'] = (monthly['Avg_Discount_pct'] * 100).round(2)
    return monthly.sort_values('Month').reset_index(drop=True)

def aggregate_by_quarter(df):
    q = df.groupby('Quarter').agg(
        Revenue=('Total_Revenue', 'sum'),
        Profit =('Total_Profit',  'sum'),
        Units  =('Units_Sold',    'sum'),
    ).reset_index()
    q['Profit_Margin_%'] = (q['Profit'] / q['Revenue'] * 100).round(2)
    return q

def calculate_product_metrics(df):
    pm = df.groupby('Product').agg(
        Units_Sold    =('Units_Sold',     'sum'),
        Total_Revenue =('Total_Revenue',  'sum'),
        Total_Profit  =('Total_Profit',   'sum'),
        Profit_Margin_pct=('Profit_Margin_%', 'mean'),
    ).reset_index()
    pm['Revenue_Share_%'] = (pm['Total_Revenue'] / pm['Total_Revenue'].sum() * 100).round(2)
    return pm.sort_values('Total_Profit', ascending=False).reset_index(drop=True)

def calculate_region_metrics(df):
    rm = df.groupby('Region').agg(
        Units_Sold   =('Units_Sold',    'sum'),
        Total_Revenue=('Total_Revenue', 'sum'),
        Total_Profit =('Total_Profit',  'sum'),
        Profit_Margin_pct=('Profit_Margin_%', 'mean'),
    ).reset_index()
    return rm.sort_values('Total_Profit', ascending=False).reset_index(drop=True)

# ============================================================================
# 4. BUSINESS INSIGHTS
# ============================================================================

def identify_best_worst_months(monthly):
    return monthly.loc[monthly['Profit'].idxmax()], monthly.loc[monthly['Profit'].idxmin()]

def calculate_month_over_month_growth(monthly):
    monthly = monthly.copy()
    monthly['MoM_Growth_%'] = monthly['Profit'].pct_change().mul(100).fillna(0).round(2)
    valid = monthly[monthly['MoM_Growth_%'] != 0]
    highest_growth = monthly.loc[valid['MoM_Growth_%'].idxmax()] if not valid.empty else monthly.iloc[1]
    return monthly, highest_growth

def get_product_rankings(product_metrics):
    r = product_metrics[['Product', 'Total_Revenue', 'Total_Profit', 'Revenue_Share_%']].copy()
    r['Revenue_Rank'] = r['Total_Revenue'].rank(ascending=False, method='min').astype(int)
    r['Profit_Rank']  = r['Total_Profit'].rank(ascending=False, method='min').astype(int)
    return r

# ============================================================================
# 5. VISUALIZATION
# ============================================================================

def _fmt_k(x, _):
    return f'${x/1000:.0f}K' if abs(x) >= 1000 else f'${x:.0f}'

def _bar_labels(ax, fmt='${:,.0f}', fontsize=7, color='black', padding=2):
    for bar in ax.patches:
        h = bar.get_height()
        if h == 0:
            continue
        ax.annotate(fmt.format(h),
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, padding), textcoords='offset points',
                    ha='center', va='bottom', fontsize=fontsize, color=color)

def _hbar_labels(ax, fmt='${:,.0f}', fontsize=7, padding=3):
    for bar in ax.patches:
        w = bar.get_width()
        ax.annotate(fmt.format(w),
                    xy=(w, bar.get_y() + bar.get_height() / 2),
                    xytext=(padding, 0), textcoords='offset points',
                    ha='left', va='center', fontsize=fontsize)

def create_dashboard(df, monthly, stats, product_metrics, region_metrics):
    PALETTE = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12',
               '#9b59b6', '#1abc9c', '#e67e22', '#34495e']

    fig = plt.figure(figsize=(20, 14))
    fig.patch.set_facecolor('#f8f9fa')
    fig.suptitle('Sales Analytics Dashboard  |  2023', fontsize=22,
                 fontweight='bold', y=0.98, color='#2c3e50')

    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.55, wspace=0.38)

    monthly_s = monthly.sort_values('Month').reset_index(drop=True)
    best_m, worst_m = identify_best_worst_months(monthly_s)

    # ── 1. Monthly Profit Bar (spans 2 cols) ──────────────────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    bar_colors = [PALETTE[0] if x >= 0 else PALETTE[2] for x in monthly_s['Profit']]
    bars = ax1.bar(monthly_s['Month_Abbr'], monthly_s['Profit'],
                   color=bar_colors, alpha=0.85, edgecolor='white', linewidth=0.6)
    # annotate best / worst
    for i, row in monthly_s.iterrows():
        if row['Month_Name'] == best_m['Month_Name']:
            ax1.bar(row['Month_Abbr'], row['Profit'], color='#27ae60', edgecolor='#1e8449', linewidth=1.2)
            ax1.annotate('BEST', xy=(i, row['Profit']), xytext=(0, 6),
                         textcoords='offset points', ha='center', fontsize=7,
                         fontweight='bold', color='#1e8449')
        if row['Month_Name'] == worst_m['Month_Name']:
            ax1.bar(row['Month_Abbr'], row['Profit'], color='#e74c3c', edgecolor='#c0392b', linewidth=1.2)
            ax1.annotate('WORST', xy=(i, row['Profit']), xytext=(0, 6),
                         textcoords='offset points', ha='center', fontsize=7,
                         fontweight='bold', color='#c0392b')
    ax1.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
    ax1.set_title('Monthly Profit  (Best vs Worst highlighted)', fontweight='bold', fontsize=10)
    ax1.set_ylabel('Profit ($)', fontsize=9)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    ax1.set_facecolor('#fdfdfd')

    # ── 2. Monthly Revenue Line + Trend (spans 2 cols) ───────────────────
    ax2 = fig.add_subplot(gs[0, 2:])
    x_idx = np.arange(len(monthly_s))
    ax2.plot(monthly_s['Month_Abbr'], monthly_s['Revenue'],
             marker='o', linewidth=2.2, markersize=6, color=PALETTE[1], label='Revenue')
    ax2.fill_between(x_idx, monthly_s['Revenue'], alpha=0.15, color=PALETTE[1])
    # polynomial trend line
    z = np.polyfit(x_idx, monthly_s['Revenue'], 2)
    p = np.poly1d(z)
    ax2.plot(monthly_s['Month_Abbr'], p(x_idx),
             linestyle='--', linewidth=1.5, color=PALETTE[3], label='Trend')
    ax2.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
    ax2.set_title('Monthly Revenue  +  Polynomial Trend', fontweight='bold', fontsize=10)
    ax2.set_ylabel('Revenue ($)', fontsize=9)
    ax2.tick_params(axis='x', rotation=30, labelsize=8)
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3, linestyle='--')
    ax2.set_facecolor('#fdfdfd')

    # ── 3. MoM Growth Bar ────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, :2])
    growth_data = monthly_s.iloc[1:]
    g_colors = [PALETTE[0] if x >= 0 else PALETTE[2] for x in growth_data['MoM_Growth_%']]
    ax3.bar(growth_data['Month_Abbr'], growth_data['MoM_Growth_%'],
            color=g_colors, alpha=0.85, edgecolor='white', linewidth=0.6)
    ax3.axhline(0, color='#2c3e50', linewidth=0.8)
    for bar, val in zip(ax3.patches, growth_data['MoM_Growth_%']):
        ax3.annotate(f'{val:+.1f}%',
                     xy=(bar.get_x() + bar.get_width() / 2,
                         val + (0.3 if val >= 0 else -0.6)),
                     ha='center', fontsize=7,
                     color='#27ae60' if val >= 0 else '#c0392b')
    ax3.set_title('Month-over-Month Profit Growth %', fontweight='bold', fontsize=10)
    ax3.set_ylabel('Growth %', fontsize=9)
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    ax3.set_facecolor('#fdfdfd')

    # ── 4. Product Revenue Pie ────────────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 2])
    pie_colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']
    wedges, texts, autotexts = ax4.pie(
        product_metrics['Total_Revenue'],
        labels=product_metrics['Product'],
        autopct='%1.1f%%', colors=pie_colors,
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(edgecolor='white', linewidth=1.5))
    for at in autotexts:
        at.set_fontsize(8)
    ax4.set_title('Product Revenue Share', fontweight='bold', fontsize=10)

    # ── 5. Product Profit Horizontal Bar ─────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 3])
    ax5.barh(product_metrics['Product'], product_metrics['Total_Profit'],
             color=PALETTE[:3], alpha=0.85, edgecolor='white')
    _hbar_labels(ax5, fmt='${:,.0f}', fontsize=7)
    ax5.xaxis.set_major_formatter(FuncFormatter(_fmt_k))
    ax5.set_title('Product Profit', fontweight='bold', fontsize=10)
    ax5.set_xlabel('Profit ($)', fontsize=9)
    ax5.grid(axis='x', alpha=0.3, linestyle='--')
    ax5.set_facecolor('#fdfdfd')

    # ── 6. Regional Profit Bar ────────────────────────────────────────────
    ax6 = fig.add_subplot(gs[2, 0])
    region_metrics_s = region_metrics.sort_values('Total_Profit', ascending=False)
    ax6.bar(region_metrics_s['Region'], region_metrics_s['Total_Profit'],
            color=PALETTE[4:8], alpha=0.85, edgecolor='white')
    _bar_labels(ax6, fmt='${:,.0f}', fontsize=7)
    ax6.yaxis.set_major_formatter(FuncFormatter(_fmt_k))
    ax6.set_title('Regional Profit', fontweight='bold', fontsize=10)
    ax6.set_ylabel('Profit ($)', fontsize=9)
    ax6.grid(axis='y', alpha=0.3, linestyle='--')
    ax6.set_facecolor('#fdfdfd')

    # ── 7. Profit Margin by Product ───────────────────────────────────────
    ax7 = fig.add_subplot(gs[2, 1])
    ax7.barh(product_metrics['Product'], product_metrics['Profit_Margin_pct'],
             color=['#8e44ad', '#d35400', '#16a085'], alpha=0.85, edgecolor='white')
    _hbar_labels(ax7, fmt='{:.1f}%', fontsize=7)
    ax7.set_title('Avg Profit Margin by Product', fontweight='bold', fontsize=10)
    ax7.set_xlabel('Profit Margin %', fontsize=9)
    ax7.grid(axis='x', alpha=0.3, linestyle='--')
    ax7.set_facecolor('#fdfdfd')

    # ── 8. Units Sold by Month ────────────────────────────────────────────
    ax8 = fig.add_subplot(gs[2, 2])
    ax8.plot(monthly_s['Month_Abbr'], monthly_s['Total_Units'],
             marker='s', linewidth=2.2, markersize=6, color=PALETTE[2])
    ax8.fill_between(x_idx, monthly_s['Total_Units'], alpha=0.15, color=PALETTE[2])
    ax8.set_title('Total Units Sold by Month', fontweight='bold', fontsize=10)
    ax8.set_ylabel('Units', fontsize=9)
    ax8.tick_params(axis='x', rotation=30, labelsize=8)
    ax8.grid(alpha=0.3, linestyle='--')
    ax8.set_facecolor('#fdfdfd')

    # ── 9. KPI Summary Text Box ───────────────────────────────────────────
    ax9 = fig.add_subplot(gs[2, 3])
    ax9.axis('off')
    kpi = (
        f"  KEY METRICS SUMMARY\n"
        f"  {'='*26}\n"
        f"  Total Revenue  : ${stats['Total_Revenue']:>13,.0f}\n"
        f"  Total Profit   : ${stats['Total_Profit']:>13,.0f}\n"
        f"  Total Units    : {stats['Total_Units']:>14,}\n"
        f"  {'─'*28}\n"
        f"  Avg Revenue    : ${stats['Average_Revenue']:>13,.0f}\n"
        f"  Avg Profit     : ${stats['Average_Profit']:>13,.0f}\n"
        f"  Profit Margin  : {stats['Average_Profit_Margin']:>13.2f}%\n"
        f"  {'─'*28}\n"
        f"  Rev Std Dev    : ${stats['Std_Dev_Revenue']:>13,.0f}\n"
        f"  Profit Std Dev : ${stats['Std_Dev_Profit']:>13,.0f}\n"
        f"  Avg Discount   : {stats['Overall_Discount_Rate']:>13.2f}%\n"
    )
    ax9.text(0.02, 0.97, kpi, transform=ax9.transAxes,
             fontsize=8.5, family='monospace', verticalalignment='top',
             bbox=dict(boxstyle='round,pad=0.6', facecolor='#eaf4fb',
                       edgecolor='#3498db', alpha=0.9))

    return fig

# ============================================================================
# 6. CONSOLE DASHBOARD SUMMARY
# ============================================================================

def print_dashboard_summary(stats, monthly, product_metrics, region_metrics, quarterly):
    W = 80
    def hdr(title, ch='-'):
        pad = W - len(title) - 4
        return f"+-- {title} " + ch * pad + "+"

    print("\n" + "=" * W)
    print(" " * 20 + "SALES ANALYTICS DASHBOARD SUMMARY  2023")
    print("=" * W + "\n")

    # Overall
    print(hdr("OVERALL PERFORMANCE METRICS"))
    print(f"|  Total Revenue          : ${stats['Total_Revenue']:>18,.2f}  |")
    print(f"|  Total Profit           : ${stats['Total_Profit']:>18,.2f}  |")
    print(f"|  Total Units Sold       : {stats['Total_Units']:>19,}  |")
    print(f"|  Avg Daily Revenue      : ${stats['Average_Revenue']:>18,.2f}  |")
    print(f"|  Avg Daily Profit       : ${stats['Average_Profit']:>18,.2f}  |")
    print(f"|  Avg Profit Margin      : {stats['Average_Profit_Margin']:>18.2f}%  |")
    print(f"|  Revenue Std Dev        : ${stats['Std_Dev_Revenue']:>18,.2f}  |")
    print(f"|  Profit Std Dev         : ${stats['Std_Dev_Profit']:>18,.2f}  |")
    print(f"|  Avg Discount Rate      : {stats['Overall_Discount_Rate']:>18.2f}%  |")
    print("+" + "-" * (W - 1) + "+\n")

    # Quarterly
    print(hdr("QUARTERLY SUMMARY"))
    print(f"|  {'Quarter':<10} {'Revenue':>14} {'Profit':>14} {'Units':>10} {'Margin%':>8}  |")
    print("|" + "-" * (W - 1) + "|")
    for _, r in quarterly.iterrows():
        print(f"|  Q{int(r['Quarter']):<9} ${r['Revenue']:>13,.0f} ${r['Profit']:>13,.0f} "
              f"{r['Units']:>9,} {r['Profit_Margin_%']:>7.1f}%  |")
    print("+" + "-" * (W - 1) + "+\n")

    # Monthly
    print(hdr("MONTHLY PERFORMANCE"))
    print(f"|  {'Month':<11} {'Revenue':>13} {'Profit':>13} {'Units':>8} {'Margin%':>8} {'MoM%':>7}  |")
    print("|" + "-" * (W - 1) + "|")
    monthly_s = monthly.sort_values('Month')
    for i, (_, r) in enumerate(monthly_s.iterrows()):
        mom = f"{r['MoM_Growth_%']:>+6.1f}%" if i > 0 else "    N/A"
        print(f"|  {r['Month_Name']:<11} ${r['Revenue']:>12,.0f} ${r['Profit']:>12,.0f} "
              f"{r['Total_Units']:>7,} {r['Avg_Profit_Margin_pct']:>7.1f}% {mom}  |")
    print("+" + "-" * (W - 1) + "+\n")

    # Best / Worst
    best_m, worst_m = identify_best_worst_months(monthly)
    print(hdr("PERFORMANCE EXTREMES"))
    print(f"|  BEST  Month : {best_m['Month_Name']:<12}  Profit: ${best_m['Profit']:>13,.2f}  |")
    print(f"|  WORST Month : {worst_m['Month_Name']:<12}  Profit: ${worst_m['Profit']:>13,.2f}  |")
    print(f"|  Difference  :                           ${best_m['Profit'] - worst_m['Profit']:>13,.2f}  |")
    print("+" + "-" * (W - 1) + "+\n")

    # Product
    print(hdr("PRODUCT PERFORMANCE"))
    print(f"|  {'Product':<12} {'Revenue':>13} {'Profit':>13} {'Units':>8} {'Share%':>7} {'Margin%':>8}  |")
    print("|" + "-" * (W - 1) + "|")
    for _, r in product_metrics.iterrows():
        print(f"|  {r['Product']:<12} ${r['Total_Revenue']:>12,.0f} ${r['Total_Profit']:>12,.0f} "
              f"{r['Units_Sold']:>7,} {r['Revenue_Share_%']:>6.1f}% {r['Profit_Margin_pct']:>7.1f}%  |")
    print("+" + "-" * (W - 1) + "+\n")

    # Region
    print(hdr("REGIONAL PERFORMANCE"))
    print(f"|  {'Region':<10} {'Revenue':>13} {'Profit':>13} {'Units':>8} {'Margin%':>8}  |")
    print("|" + "-" * (W - 1) + "|")
    for _, r in region_metrics.iterrows():
        print(f"|  {r['Region']:<10} ${r['Total_Revenue']:>12,.0f} ${r['Total_Profit']:>12,.0f} "
              f"{r['Units_Sold']:>7,} {r['Profit_Margin_pct']:>7.1f}%  |")
    print("+" + "-" * (W - 1) + "+\n")

    # MoM Growth
    print(hdr("MONTH-OVER-MONTH GROWTH"))
    print(f"|  {'Month':<11} {'Profit':>13} {'MoM Growth':>12}  |")
    print("|" + "-" * (W - 1) + "|")
    for i, (_, r) in enumerate(monthly_s.iterrows()):
        mom = f"{r['MoM_Growth_%']:>+10.2f}%" if i > 0 else "       N/A"
        print(f"|  {r['Month_Name']:<11} ${r['Profit']:>12,.0f} {mom}  |")
    print("+" + "-" * (W - 1) + "+\n")

    # Key Insights
    _, highest_growth = calculate_month_over_month_growth(monthly)
    rankings = get_product_rankings(product_metrics)
    print(hdr("KEY BUSINESS INSIGHTS"))
    top_p = product_metrics.iloc[0]
    top_r = region_metrics.iloc[0]
    print(f"|  [TOP PRODUCT]  {top_p['Product']:<14}  Profit: ${top_p['Total_Profit']:>12,.0f}  "
          f"Share: {top_p['Revenue_Share_%']:.1f}%  |")
    print(f"|  [TOP REGION ]  {top_r['Region']:<14}  Profit: ${top_r['Total_Profit']:>12,.0f}  "
          f"Margin: {top_r['Profit_Margin_pct']:.1f}%  |")
    if highest_growth is not None:
        print(f"|  [BEST GROWTH]  {highest_growth['Month_Name']:<14}  MoM Growth: "
              f"{highest_growth['MoM_Growth_%']:>+8.2f}%  |")
    print(f"|  [PROFIT MARGIN]  Overall Avg: {stats['Average_Profit_Margin']:.2f}%   "
          f"Avg Discount: {stats['Overall_Discount_Rate']:.2f}%  |")
    print("+" + "-" * (W - 1) + "+\n")

    print("=" * W)
    print(" " * 25 + "END OF DASHBOARD REPORT")
    print("=" * W + "\n")

# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

def main():
    print("\n[*] Initializing Sales Analytics Pipeline...\n")

    print("[+] Generating synthetic sales dataset...")
    df = generate_sales_data(n_records=365)

    print("[+] Processing and enriching data...")
    df = process_sales_data(df)

    print("[+] Calculating statistical summaries...")
    stats = calculate_statistics(df)

    print("[+] Aggregating data by month, quarter, product, and region...")
    monthly         = aggregate_by_month(df)
    monthly, _      = calculate_month_over_month_growth(monthly)
    quarterly       = aggregate_by_quarter(df)
    product_metrics = calculate_product_metrics(df)
    region_metrics  = calculate_region_metrics(df)

    print("[+] Generating formatted dashboard summary...\n")
    print_dashboard_summary(stats, monthly, product_metrics, region_metrics, quarterly)

    print("[+] Building visualization dashboard...")
    fig = create_dashboard(df, monthly, stats, product_metrics, region_metrics)
    plt.tight_layout(rect=[0, 0, 1, 0.96])

    out_path = r"d:\Ultron\CLG_PROGRAMS\MINI_PROJECT\sales_dashboard_2023.png"
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"[+] Dashboard saved -> {out_path}")

    plt.show()
    print("[OK] Analytics Pipeline Completed Successfully!")

    return df, stats, monthly, product_metrics, region_metrics, quarterly

if __name__ == "__main__":
    df, stats, monthly, product_metrics, region_metrics, quarterly = main()
