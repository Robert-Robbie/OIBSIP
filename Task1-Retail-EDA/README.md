# Task 1 · Exploratory Data Analysis on Retail Sales Data

**Objective:** explore a retail sales dataset to uncover patterns, customer behaviour trends and actionable business insights.

## Business questions
1. Which products and categories drive the most sales and profit?
2. What is the trend of sales over time (monthly / quarterly / yearly)?
3. Which stores or regions perform best?
4. How do customer demographics (age, gender, city) influence sales?
5. What is the average order value and customer lifetime value?
6. How do discounts affect revenue?

## Dataset
`data/retail_sales_dataset.xlsx` is a four-sheet workbook:

| Sheet | Rows | Description |
|---|---|---|
| Customers | 200 | Gender, birth date, city, join date |
| Products | 50 | Category, sub-category, unit price, cost price |
| Stores | 5 | Store city and region |
| Transactions | 5,000 | Date, customer, product, store, quantity, discount, payment method |

## Project structure
```
Task1-Retail-EDA/
├── data/        raw workbook
├── notebooks/   analysis notebooks (run in order)
├── outputs/     cleaned data and figures
└── README.md
```

## Progress
- [x] **Part 1 – Cleaning & feature engineering** (`notebooks/01_cleaning_and_features.ipynb`)
- [ ] Part 2 – Business questions 1–6
- [ ] Part 3 – Insights and recommendations

## Part 1 summary: data cleaning
- All four sheets load cleanly: **no missing values, no duplicate rows, no orphan keys**; every product is priced above cost.
- **Data-quality issue:** 996 of 5,000 transactions (19.9%, across 75 customers) are dated *before* the customer's `JoinDate`. The sales are valid, so the rows were kept and flagged in `BeforeJoinDate`. Customer lifetime value will be based on actual transactions, not on `JoinDate`.
- Tables were merged into one 5,000-row table with a left join on the three keys (row count verified).
- Derived columns: `GrossSales`, `DiscountAmount`, `Revenue = Quantity × UnitPrice × (1 − Discount)`, `TotalCost`, `Profit`, `ProfitMargin`, date parts (`Year`, `Quarter`, `Month`, `YearMonth`), `Age`, `AgeGroup`, `DiscountBand`.
- Result: total revenue ≈ 14.30M, total profit ≈ 3.83M, overall margin 26.8%.

## How to run
```bash
pip install pandas numpy matplotlib seaborn openpyxl jupyter
cd notebooks
jupyter notebook 01_cleaning_and_features.ipynb
```
