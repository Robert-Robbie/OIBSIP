"""Re-draw five charts from the notebook with larger text so they stay readable on a projected slide.

Run from the Task1-Retail-EDA folder:  python scripts/make_slide_figures.py
Reads outputs/retail_clean.csv (created by notebook 01) and writes PNGs to outputs/figures/slides/.
The numbers are identical to the notebook; only the layout and font sizes differ.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

OUT = Path("outputs/figures/slides")
OUT.mkdir(parents=True, exist_ok=True)
df = pd.read_csv("outputs/retail_clean.csv", parse_dates=["Date", "BirthDate", "JoinDate"])

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
    "text.color": INK, "axes.titlecolor": INK, "axes.titleweight": "bold", "axes.titlesize": 16,
    "axes.titlelocation": "left", "font.size": 14, "legend.frameon": False, "legend.fontsize": 13,
})


def money(x, pos=None):
    return f"{x/1e6:.1f}M" if abs(x) >= 1e6 else (f"{x/1e3:.0f}k" if abs(x) >= 1e3 else f"{x:.0f}")


def money2(x):
    return f"{x/1e6:.2f}M" if abs(x) >= 1e6 else money(x)


MONEY = FuncFormatter(money)
PCT = FuncFormatter(lambda v, p: f"{v:.0%}")


def style(ax, grid="y"):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid, color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def save(fig, name):
    fig.savefig(OUT / name, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------- Q3: region and store revenue (stacked panels)
reg = df.groupby("Region").agg(Revenue=("Revenue", "sum"), Stores=("StoreID", "nunique")).sort_values("Revenue", ascending=False)
sto = df.groupby(["StoreName", "Region"]).Revenue.sum().reset_index().sort_values("Revenue", ascending=False)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 6.6), gridspec_kw={"width_ratios": [4, 5]})
b = a1.bar([f"{r}\n({int(s)} store{'s' if s > 1 else ''})" for r, s in zip(reg.index, reg.Stores)], reg.Revenue, color=BLUE, width=0.62)
a1.bar_label(b, labels=[money2(v) for v in reg.Revenue], padding=3, fontsize=14)
a1.yaxis.set_major_formatter(MONEY); a1.set_ylim(0, reg.Revenue.max() * 1.17)
a1.set_title("By region: East has 2 stores"); style(a1)
short = sto.StoreName.str.replace("MegaMart ", "").replace({"Jimenezborough": "Jimenez-\nborough", "New Michele": "New\nMichele", "Brianahaven": "Briana-\nhaven"})
b = a2.bar([f"{n}\n({r})" for n, r in zip(short, sto.Region)], sto.Revenue, color=BLUE, width=0.62)
a2.bar_label(b, labels=[money2(v) for v in sto.Revenue], padding=3, fontsize=13)
a2.yaxis.set_major_formatter(MONEY); a2.set_ylim(0, sto.Revenue.max() * 1.17)
a2.set_title("By store: all within 6%"); style(a2)
fig.tight_layout(w_pad=2.0)
save(fig, "slide_q3_region_store.png")

# ---------------------------------------------------------------- Q5: order value and customer profit (stacked panels)
aov, med = df.Revenue.mean(), df.Revenue.median()
cust = df.groupby("CustomerID").Profit.sum()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 6.6))
a1.hist(df.Revenue, bins=30, color=BLUE, edgecolor=SURF, linewidth=1)
a1.set_ylim(0, a1.get_ylim()[1] * 1.22)
for v, lab, side in [(aov, f"mean {aov:,.0f}", 1), (med, f"median {med:,.0f}", -1)]:
    a1.axvline(v, color=INK2, lw=1.3, ls="--")
    a1.text(v + side * 120, a1.get_ylim()[1] * 0.92, lab, color=INK2, fontsize=13, ha="left" if side > 0 else "right")
a1.xaxis.set_major_formatter(MONEY); a1.set_xlabel("Revenue per order"); a1.set_ylabel("Orders")
a1.set_title("Order values: mostly small"); style(a1)
a2.hist(cust, bins=20, color=BLUE, edgecolor=SURF, linewidth=1)
a2.axvline(cust.mean(), color=INK2, lw=1.3, ls="--")
a2.text(cust.mean() + 400, a2.get_ylim()[1] * 0.93, f"mean {cust.mean():,.0f}", color=INK2, fontsize=13)
a2.xaxis.set_major_formatter(MONEY); a2.set_xlabel("Profit over 24 months"); a2.set_ylabel("Customers")
a2.set_title("Lifetime profit per customer"); style(a2)
fig.tight_layout(w_pad=2.0)
save(fig, "slide_q5_aov_clv.png")

# ---------------------------------------------------------------- Q6: discount effect (three stacked small panels)
d = df.groupby("Discount").agg(AvgUnits=("Quantity", "mean"), Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
d["Margin"] = d.Profit / d.Revenue
d.index = [f"{int(i * 100)}%" for i in d.index]
fig, axes = plt.subplots(1, 3, figsize=(12, 6.4))
for ax, vals, title, fmt, ylim, yfmt in [
    (axes[0], d.AvgUnits, "Units per order", lambda v: f"{v:.2f}", (0, 4), None),
    (axes[1], d.Margin, "Profit margin", lambda v: f"{v:.0%}", (0, 0.4), PCT),
    (axes[2], d.Profit, "Total profit", money2, (0, d.Profit.max() * 1.2), MONEY),
]:
    b = ax.bar(vals.index, vals.values, color=BLUE, width=0.62)
    ax.bar_label(b, labels=[fmt(v) for v in vals.values], padding=3, fontsize=14)
    ax.set_ylim(*ylim); ax.set_title(title); ax.set_xlabel("Discount level"); style(ax)
    if yfmt is not None:
        ax.yaxis.set_major_formatter(yfmt)
fig.tight_layout(w_pad=2.0)
save(fig, "slide_q6_discount.png")

# ---------------------------------------------------------------- Extra: price tiers
df["PriceTier"] = pd.qcut(df.UnitPrice, 4, labels=["Cheapest\n25%", "Lower-\nmid", "Upper-\nmid", "Priciest\n25%"])
tier = df.groupby("PriceTier", observed=True).agg(Units=("Quantity", "sum"), Revenue=("Revenue", "sum"), Profit=("Profit", "sum"))
tier["Margin"] = tier.Profit / tier.Revenue
shares = tier[["Units", "Revenue", "Profit"]] / tier[["Units", "Revenue", "Profit"]].sum()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 6.6), gridspec_kw={"width_ratios": [5, 3]})
x = np.arange(len(tier)); w = 0.26
for k, (col, colr) in enumerate([("Units", AQUA), ("Revenue", BLUE), ("Profit", ORANGE)]):
    bars = a1.bar(x + (k - 1) * w, shares[col], w, color=colr, label=f"Share of {col.lower()}")
    a1.bar_label(bars, labels=[f"{v:.0%}" for v in shares[col]], padding=2, fontsize=11)
a1.set_xticks(x, [str(t) for t in tier.index])
a1.yaxis.set_major_formatter(PCT); a1.set_ylim(0, 0.52)
a1.legend(loc="upper left", fontsize=12); a1.set_title("Same units sold, very different revenue"); style(a1)
b = a2.bar(range(len(tier)), tier.Margin, color=BLUE, width=0.55)
a2.bar_label(b, labels=[f"{v:.0%}" for v in tier.Margin], padding=3, fontsize=14)
a2.set_xticks(range(len(tier)), [str(t) for t in tier.index])
a2.yaxis.set_major_formatter(PCT); a2.set_ylim(0, 0.4)
a2.set_title("Profit margin by tier"); style(a2)
fig.tight_layout(w_pad=2.0)
save(fig, "slide_extra_price_tiers.png")

# ---------------------------------------------------------------- Correlation heatmap
cols = ["Quantity", "Discount", "UnitPrice", "CostPrice", "GrossSales", "Revenue", "Profit", "ProfitMargin", "Age"]
corr = df[cols].corr()
cmap = LinearSegmentedColormap.from_list("div", [ORANGE, "#f1f0ec", BLUE])
fig, ax = plt.subplots(figsize=(7.2, 6.2))
im = ax.imshow(corr, cmap=cmap, vmin=-1, vmax=1)
ax.set_xticks(range(len(corr)), corr.columns, rotation=40, ha="right"); ax.set_yticks(range(len(corr)), corr.columns)
for i in range(len(corr)):
    for j in range(len(corr)):
        v = corr.iloc[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=12, color="white" if abs(v) > 0.6 else INK)
ax.grid(False); ax.tick_params(length=0)
for sp in ax.spines.values():
    sp.set_visible(False)
cb = fig.colorbar(im, ax=ax, shrink=0.85); cb.outline.set_visible(False)
fig.tight_layout()
save(fig, "slide_corr_heatmap.png")
print("wrote", sorted(p.name for p in OUT.glob("*.png")))
