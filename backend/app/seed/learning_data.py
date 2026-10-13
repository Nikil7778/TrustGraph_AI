import json
from typing import List, Dict, Any

LEARNING_MODULES_SEED: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. SQL Fundamentals
    # -------------------------------------------------------------------------
    {
        "slug": "sql-fundamentals",
        "skill_name": "SQL",
        "title": "Relational Querying & Aggregation Fundamentals",
        "concept_name": "SQL Relational Filtering & Aggregations",
        "difficulty": "Beginner",
        "estimated_minutes": 25,
        "order_index": 1,
        "prerequisite_concept_slugs": "",
        "target_role_name": "All",
        "learning_objectives": [
            "Master the logical SQL query processing order (FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY)",
            "Filter records accurately using predicates, pattern matching (LIKE), and NULL checks (IS NULL)",
            "Aggregate metrics using COUNT, SUM, AVG, MIN, and MAX grouped by dimensional attributes",
        ],
        "explanation": """### SQL Logical Query Processing Order
To write performant and bug-free SQL queries, you must understand how relational database engines process SQL statements. Even though queries begin with `SELECT`, the engine executes clauses in a strict logical sequence:

1. **`FROM`**: Identifies source tables and establishes row sets.
2. **`WHERE`**: Filters individual base rows before any aggregation takes place.
3. **`GROUP BY`**: Collapses rows into distinct groups based on key columns.
4. **`HAVING`**: Filters groups *after* aggregate functions have run.
5. **`SELECT`**: Evaluates expressions, aliases, and selects output columns.
6. **`ORDER BY`**: Sorts the resulting records.

#### Key Syntax Rules:
* Never use aggregate functions like `SUM()` or `COUNT()` inside a `WHERE` clause; use `HAVING` instead.
* In standard SQL, you cannot filter on column aliases defined in `SELECT` within the same query's `WHERE` clause.
* Use `IS NULL` and `IS NOT NULL` to evaluate missing values; `= NULL` always evaluates to UNKNOWN.

#### Top Common Mistake:
Filtering on aggregated metrics using `WHERE` instead of `HAVING` (e.g. `WHERE COUNT(*) > 5` causes a syntax error).""",
        "key_rules": "- Logical order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY\n- Aggregates cannot appear in WHERE\n- Use IS NULL, never = NULL",
        "common_mistakes": "- Placing aggregate filters in WHERE instead of HAVING\n- Forgetting to group by all non-aggregated columns in the SELECT list\n- Assuming ORDER BY is applied before GROUP BY",
        "worked_example": {
            "scenario": "A retailer needs to find all customer segments with more than 3 completed orders, returning the segment and total revenue.",
            "code": "SELECT segment, COUNT(order_id) AS total_orders, SUM(total_amount) AS gross_revenue\nFROM orders\nWHERE payment_status = 'COMPLETED'\nGROUP BY segment\nHAVING COUNT(order_id) > 3\nORDER BY gross_revenue DESC;",
            "reasoning": "1. Filters base rows where payment_status is 'COMPLETED'. 2. Groups rows by 'segment'. 3. Uses HAVING to discard segments with 3 or fewer orders. 4. Calculates aggregate sum. 5. Sorts descending by revenue.",
            "expected_output": "| segment | total_orders | gross_revenue |\n| :--- | :--- | :--- |\n| Enterprise | 8 | 14500.00 |\n| Mid-Market | 5 | 8200.00 |"
        },
        "guided_practice": {
            "prompt": "Write a query to calculate the average order value (AOV) and total orders for each product category from the `orders` table. Only include orders where `status` is 'DELIVERED', and only show categories that generated at least $1,000 in total sales.",
            "starter_code": "-- Calculate category AOV and total orders\nSELECT category\nFROM orders\n-- Your code here",
            "solution": "SELECT category, COUNT(*) AS total_orders, AVG(amount) AS aov, SUM(amount) AS total_sales\nFROM orders\nWHERE status = 'DELIVERED'\nGROUP BY category\nHAVING SUM(amount) >= 1000\nORDER BY total_sales DESC;",
            "hints": [
                "Step 1: Start with WHERE status = 'DELIVERED' before the GROUP BY clause.",
                "Step 2: Group by category, then use HAVING SUM(amount) >= 1000 to filter category totals.",
                "Step 3: Select category, COUNT(*), AVG(amount), and SUM(amount) in your SELECT list."
            ]
        },
        "independent_practice": {
            "prompt": "Retrieve all customer IDs who placed orders in 2024 with a total spending of over $5,000 across their completed orders. Return customer_id and total_spent sorted highest to lowest.",
            "starter_code": "SELECT customer_id, SUM(amount) AS total_spent\nFROM orders\nWHERE strftime('%Y', order_date) = '2024'\n-- Complete query",
            "solution": "SELECT customer_id, SUM(amount) AS total_spent\nFROM orders\nWHERE strftime('%Y', order_date) = '2024' AND payment_status = 'COMPLETED'\nGROUP BY customer_id\nHAVING SUM(amount) > 5000\nORDER BY total_spent DESC;",
            "test_criteria": "Filters by year and status, groups by customer_id, uses HAVING SUM > 5000, orders DESC."
        },
        "concept_check": [
            {
                "question_text": "Why does the query `SELECT dept, AVG(salary) FROM employees WHERE AVG(salary) > 50000 GROUP BY dept;` fail with an error?",
                "options": [
                    "Department names cannot be grouped in SQL",
                    "Aggregate functions cannot be used in the WHERE clause",
                    "AVG(salary) must always be rounded to an integer",
                    "ORDER BY is required whenever GROUP BY is used"
                ],
                "correct": "Aggregate functions cannot be used in the WHERE clause",
                "explanation": "WHERE filters rows before groups are formed. To filter on aggregate calculations like AVG(), use the HAVING clause."
            },
            {
                "question_text": "In the logical execution order of an SQL query, which clause is executed immediately after GROUP BY?",
                "options": ["SELECT", "ORDER BY", "HAVING", "WHERE"],
                "correct": "HAVING",
                "explanation": "Logical sequence is FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY."
            },
            {
                "question_text": "What is the correct way to test if a column 'discount_code' has no recorded value in SQL?",
                "options": ["discount_code = NULL", "discount_code IS NULL", "discount_code == 'NONE'", "discount_code.isna()"],
                "correct": "discount_code IS NULL",
                "explanation": "In SQL three-valued logic, NULL compared with = always yields UNKNOWN. You must use IS NULL."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Analyst quarterly performance evaluation",
            "task_description": "Aggregate customer transactional records to identify high-value accounts experiencing order growth.",
            "starter_code": "SELECT customer_id, COUNT(*) AS num_orders, SUM(order_total) AS revenue\nFROM customer_orders\nWHERE order_status = 'COMPLETED'\nGROUP BY customer_id\nHAVING SUM(order_total) > 2500;",
            "rubrics": "Correctly filters by order_status, groups by customer_id, filters on group revenue threshold using HAVING."
        }
    },

    # -------------------------------------------------------------------------
    # 2. SQL JOINs
    # -------------------------------------------------------------------------
    {
        "slug": "sql-joins-mastery",
        "skill_name": "SQL JOINs",
        "title": "Multi-Table Relational Merges & Null Safety",
        "concept_name": "SQL Multi-Table JOINs & Null Handling",
        "difficulty": "Intermediate",
        "estimated_minutes": 30,
        "order_index": 2,
        "prerequisite_concept_slugs": "sql-fundamentals",
        "target_role_name": "All",
        "learning_objectives": [
            "Distinguish between INNER, LEFT, RIGHT, and FULL OUTER JOIN semantics",
            "Preserve unmatched parent records using LEFT JOIN to avoid catastrophic cohort data loss",
            "Safely handle NULL values produced by non-matching rows using COALESCE()",
        ],
        "explanation": """### Relational Joins & The Silent INNER JOIN Pitfall
In relational analytics, business metrics almost always span normalized tables (e.g. `customers`, `orders`, `returns`). Choosing the wrong join type will silently corrupt business metrics.

#### The Core Join Types:
* **`INNER JOIN`**: Retains only rows that satisfy the join condition in *both* tables. If a customer has made 0 orders, an INNER JOIN silently discards that customer entirely!
* **`LEFT JOIN`**: Retains *all* rows from the left table, linking columns from the right table when matching, and filling with `NULL` when unmatched.
* **`COALESCE(val, fallback)`**: Returns the first non-null argument. Essential for converting `NULL` refunds to `$0.00` so arithmetic operations do not evaluate to `NULL`.

#### Critical Scenario: E-Commerce Refund Analytics
If an analyst executes:
```sql
SELECT c.segment, SUM(o.amount) - SUM(r.refund_amount)
FROM customers c
INNER JOIN orders o ON c.id = o.customer_id
INNER JOIN returns r ON o.id = r.order_id
```
**Why this fails:** Because returns only occur on a fraction of orders (~10%), the `INNER JOIN returns` drops the ~90% of orders that had zero returns! Revenue is severely undercounted.""",
        "key_rules": "- When parent records can exist without child records, always use LEFT JOIN\n- Wrap nullable numeric fields in COALESCE(field, 0)\n- Filter conditions on the right table of a LEFT JOIN must go in the ON clause if you want to keep left rows",
        "common_mistakes": "- Using INNER JOIN for cohort, retention, or churn metrics\n- Forgetting COALESCE() on SUM(refunds), resulting in NULL for any customer without refunds\n- Placing a WHERE condition on a right-table column that filters out NULLs, accidentally converting LEFT JOIN into INNER JOIN",
        "worked_example": {
            "scenario": "Calculate segment-level gross revenue, refunds, and net revenue for an e-commerce platform.",
            "code": "SELECT\n    c.segment,\n    COUNT(DISTINCT o.id) AS total_orders,\n    ROUND(SUM(o.total_amount), 2) AS gross_revenue,\n    ROUND(COALESCE(SUM(r.refund_amount), 0), 2) AS total_refunds,\n    ROUND(SUM(o.total_amount) - COALESCE(SUM(r.refund_amount), 0), 2) AS net_revenue\nFROM customers c\nJOIN orders o ON c.id = o.customer_id\nLEFT JOIN returns r ON o.id = r.order_id\nWHERE o.payment_status = 'COMPLETED'\nGROUP BY c.segment\nORDER BY net_revenue DESC;",
            "reasoning": "1. Joins customers to orders. 2. LEFT JOINs returns so orders with 0 returns remain in the calculation. 3. COALESCE ensures zero returns evaluates to 0.00 rather than NULL. 4. Filters only COMPLETED orders.",
            "expected_output": "| segment | total_orders | gross_revenue | total_refunds | net_revenue |\n| :--- | :--- | :--- | :--- | :--- |\n| Enterprise | 6 | 8500.00 | 358.00 | 8142.00 |\n| SMB | 4 | 3200.00 | 0.00 | 3200.00 |"
        },
        "guided_practice": {
            "prompt": "Join the `users` table with the `subscriptions` table using a LEFT JOIN to find all users, their plan name, and their monthly billing. Replace any missing plan names with 'Free Tier' and missing monthly billing with 0.",
            "starter_code": "-- Link users and subscriptions safely\nSELECT u.user_id, u.email\nFROM users u\n-- Add LEFT JOIN and COALESCE here",
            "solution": "SELECT u.user_id, u.email, COALESCE(s.plan_name, 'Free Tier') AS plan_name, COALESCE(s.monthly_cost, 0) AS monthly_cost\nFROM users u\nLEFT JOIN subscriptions s ON u.user_id = s.user_id;",
            "hints": [
                "Use LEFT JOIN subscriptions s ON u.user_id = s.user_id to keep users who have no active subscription.",
                "Wrap s.plan_name with COALESCE(s.plan_name, 'Free Tier').",
                "Wrap s.monthly_cost with COALESCE(s.monthly_cost, 0) to prevent NULL arithmetic."
            ]
        },
        "independent_practice": {
            "prompt": "Write a query connecting `departments`, `employees`, and `projects`. Return each department name, count of employees, and count of active assigned projects. Departments with 0 employees or 0 projects must still appear in the output.",
            "starter_code": "SELECT d.name AS dept_name\nFROM departments d\n-- Complete with multi-table LEFT JOINs",
            "solution": "SELECT d.name AS dept_name, COUNT(DISTINCT e.id) AS num_employees, COUNT(DISTINCT p.id) AS num_projects\nFROM departments d\nLEFT JOIN employees e ON d.id = e.dept_id\nLEFT JOIN projects p ON d.id = p.dept_id\nGROUP BY d.name\nORDER BY num_employees DESC;",
            "test_criteria": "Uses LEFT JOIN for both relations, COUNT(DISTINCT) to prevent cartesian explosion, groups by dept_name."
        },
        "concept_check": [
            {
                "id": "joins-check-1",
                "question_text": "If table A has 100 customers and table B has orders for only 60 of them, how many rows will `SELECT * FROM A INNER JOIN B ON A.id = B.customer_id;` return if each ordering customer has exactly 1 order?",
                "options": ["100 rows", "60 rows", "160 rows", "40 rows"],
                "correct": "60 rows",
                "correct_index": 1,
                "explanation": "INNER JOIN requires matches in both tables. The 40 customers with 0 orders are omitted entirely."
            },
            {
                "id": "joins-check-2",
                "question_text": "What happens if you execute `SELECT 100 - NULL;` in standard SQL?",
                "options": ["Returns 100", "Returns NULL", "Throws SyntaxError", "Returns 0"],
                "correct": "Returns NULL",
                "correct_index": 1,
                "explanation": "Any arithmetic operation with a NULL operand evaluates to NULL. This is why COALESCE is mandatory."
            },
            {
                "id": "joins-check-3",
                "question_text": "You execute a LEFT JOIN between Accounts and Invoices, but your WHERE clause has `WHERE Invoices.status = 'PAID'`. What is the unintended side effect?",
                "options": [
                    "Accounts with 0 invoices are still included with NULLs",
                    "It converts the LEFT JOIN into an INNER JOIN, discarding accounts with 0 invoices",
                    "It causes a table lock error",
                    "It duplicates invoice rows"
                ],
                "correct": "It converts the LEFT JOIN into an INNER JOIN, discarding accounts with 0 invoices",
                "correct_index": 1,
                "explanation": "Since Invoices.status is NULL for accounts without invoices, `status = 'PAID'` evaluates to UNKNOWN/FALSE, discarding non-invoiced accounts."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Analyst Retail Returns Rescue",
            "task_description": "Produce a robust financial summary of orders and refunds across customer segments without discarding non-returned orders.",
            "starter_code": "SELECT c.segment, COUNT(DISTINCT o.id) AS orders, SUM(o.total_amount) AS gross_rev\nFROM lab_retail_customers c\nJOIN lab_retail_orders o ON c.id = o.customer_id\nLEFT JOIN lab_retail_returns r ON o.id = r.order_id\nWHERE o.payment_status = 'COMPLETED'\nGROUP BY c.segment;",
            "rubrics": "Uses LEFT JOIN on returns, filters COMPLETED payment status, groups by segment, prevents NULL refund errors."
        }
    },

    # -------------------------------------------------------------------------
    # 3. Python Foundations & Pandas
    # -------------------------------------------------------------------------
    {
        "slug": "python-pandas-pipelines",
        "skill_name": "Python",
        "title": "Python Data Manipulation with Pandas & Vectorization",
        "concept_name": "Pandas DataFrames, Method Chaining & Vectorization",
        "difficulty": "Beginner",
        "estimated_minutes": 30,
        "order_index": 3,
        "prerequisite_concept_slugs": "",
        "target_role_name": "All",
        "learning_objectives": [
            "Construct vectorized transformations using Pandas without inefficient Python loops",
            "Clean tabular data with proper handling of NaN, dtype casting, and categorical conversions",
            "Perform grouping, aggregation, and merging across DataFrames",
        ],
        "explanation": """### Vectorization vs. Iteration in Pandas
Pandas is built on top of NumPy's contiguous C-level memory buffers. Performing operations across columns vectorially executes orders of magnitude faster than iterating row-by-row with `for` loops or `iterrows()`.

#### The Golden Rules of Pandas:
1. **Never iterate over rows** when a vectorized expression exists:
   * Bad: `for index, row in df.iterrows(): df.loc[index, 'total'] = row['qty'] * row['price']`
   * Good: `df['total'] = df['qty'] * df['price']`
2. **Missing Data Handling**: Use `df.isna().sum()` to audit missingness, and choose between `df.dropna()` or `df.fillna()` based on domain context.
3. **Data Type Memory Optimization**: Convert high-cardinality strings to `category` dtype when unique values represent < 50% of the total rows: `df['segment'] = df['segment'].astype('category')`.
4. **Groupby Aggregations**:
   ```python
   summary = df.groupby('segment').agg(
       total_revenue=('revenue', 'sum'),
       avg_order_value=('revenue', 'mean'),
       order_count=('order_id', 'count')
   ).reset_index()
   ```""",
        "key_rules": "- Vectorized operations execute in C; avoid iterrows()\n- Use df.assign() for clean method chaining\n- Convert repetitive text columns to 'category' dtype",
        "common_mistakes": "- Mutating a slice of a DataFrame causing SettingWithCopyWarning\n- In-place mutation breaking data pipeline reproducibility\n- Index misalignment when adding two Series without matching indices",
        "worked_example": {
            "scenario": "A data professional needs to clean a messy retail DataFrame, impute missing discount values, and compute net sales per region.",
            "code": "import pandas as pd\n\ndef clean_and_summarize(df: pd.DataFrame) -> pd.DataFrame:\n    cleaned = (\n        df.copy()\n        .assign(discount=lambda d: d['discount'].fillna(0.0))\n        .assign(net_revenue=lambda d: d['gross_revenue'] * (1 - d['discount']))\n        .groupby('region', as_index=False)\n        .agg(total_net=('net_revenue', 'sum'), orders=('order_id', 'count'))\n        .sort_values(by='total_net', ascending=False)\n    )\n    return cleaned",
            "reasoning": "Uses method chaining with .assign(), prevents SettingWithCopyWarning, fills missing discounts with 0, and aggregates by region cleanly.",
            "expected_output": "  region  total_net  orders\n0  North    48200.5      42\n1  South    31400.0      28"
        },
        "guided_practice": {
            "prompt": "Given a DataFrame `df` with columns `['customer_id', 'purchase_amount', 'churn_status']`, create a new column `log_amount` containing the natural logarithm of `purchase_amount + 1` using NumPy, and filter for active customers (`churn_status == 0`).",
            "starter_code": "import numpy as np\nimport pandas as pd\n\ndef process_customers(df: pd.DataFrame) -> pd.DataFrame:\n    # Add log_amount and filter active\n    pass",
            "solution": "import numpy as np\nimport pandas as pd\n\ndef process_customers(df: pd.DataFrame) -> pd.DataFrame:\n    result = df[df['churn_status'] == 0].copy()\n    result['log_amount'] = np.log1p(result['purchase_amount'])\n    return result",
            "hints": [
                "Filter active customers using boolean indexing: df[df['churn_status'] == 0].copy().",
                "Use np.log1p(x) which calculates log(1 + x) accurately for small values.",
                "Assign the result vectorially to result['log_amount']."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function that merges two DataFrames `orders_df` and `customers_df` on `customer_id` using a left merge, fills missing `tier` values with 'Standard', and computes total spend per tier.",
            "starter_code": "def tier_spend_summary(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:\n    # Merge, fillna, and aggregate\n    pass",
            "solution": "def tier_spend_summary(orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> pd.DataFrame:\n    merged = pd.merge(orders_df, customers_df, on='customer_id', how='left')\n    merged['tier'] = merged['tier'].fillna('Standard')\n    return merged.groupby('tier', as_index=False)['amount'].sum().rename(columns={'amount': 'total_spend'})",
            "test_criteria": "Uses pd.merge(..., how='left'), handles missing tier values, returns grouped spend DataFrame."
        },
        "concept_check": [
            {
                "question_text": "Why is `df['col_c'] = df['col_a'] + df['col_b']` significantly faster than iterating with `df.iterrows()` in Pandas?",
                "options": [
                    "Vectorization bypasses the Python interpreter loop and runs compiled C/NumPy code over contiguous memory",
                    "iterrows() writes data to disk on every iteration",
                    "Vectorization uses multi-threading by default across all CPU cores",
                    "iterrows() encrypts data before reading"
                ],
                "correct": "Vectorization bypasses the Python interpreter loop and runs compiled C/NumPy code over contiguous memory",
                "explanation": "NumPy and Pandas operate on contiguous blocks of memory in compiled C, avoiding overhead on every Python object loop."
            },
            {
                "question_text": "What does the method `df.assign(new_col=lambda x: x['a'] * 2)` return?",
                "options": [
                    "Mutates the original DataFrame in-place and returns None",
                    "Returns a new DataFrame with the added/modified column",
                    "A Python generator object",
                    "A Boolean Series"
                ],
                "correct": "Returns a new DataFrame with the added/modified column",
                "explanation": "df.assign() returns a new DataFrame copy with the calculated column, ideal for method chaining."
            },
            {
                "question_text": "When performing `df['A'] + df['B']`, what occurs if the index labels of Series A and Series B do not align?",
                "options": [
                    "Pandas throws an unrecoverable ValueError",
                    "Pandas aligns by index labels, inserting NaN for unaligned indices",
                    "Pandas truncates the longer Series silently",
                    "Pandas treats index labels as integer positions"
                ],
                "correct": "Pandas aligns by index labels, inserting NaN for unaligned indices",
                "explanation": "Pandas always performs index-aligned operations. Unmatched indices result in NaN."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Science Feature Engineering Pipeline",
            "task_description": "Clean raw e-commerce transaction data, parse timestamps, compute days since last purchase, and aggregate metrics per customer.",
            "starter_code": "def build_customer_features(raw_df: pd.DataFrame) -> pd.DataFrame:\n    # Feature pipeline implementation\n    return raw_df",
            "rubrics": "Vectorized calculation of recency, clean handling of missing values, aggregations per customer_id."
        }
    },

    # -------------------------------------------------------------------------
    # 4. Statistics & Hypothesis Testing
    # -------------------------------------------------------------------------
    {
        "slug": "statistics-hypothesis-testing",
        "skill_name": "Statistics",
        "title": "Applied Statistical Analysis & Hypothesis Testing",
        "concept_name": "Descriptive Statistics, Confidence Intervals & Hypothesis Tests",
        "difficulty": "Intermediate",
        "estimated_minutes": 30,
        "order_index": 4,
        "prerequisite_concept_slugs": "python-pandas-pipelines",
        "target_role_name": "All",
        "learning_objectives": [
            "Interpret measures of central tendency, spread, variance, and skewness",
            "Formulate null ($H_0$) and alternative ($H_1$) hypotheses for business experiments",
            "Evaluate p-values, significance levels ($\\alpha = 0.05$), and Type I vs. Type II error trade-offs",
        ],
        "explanation": """### Statistical Rigor in Data Decision-Making
Data analysts and scientists must distinguish real business signals from random noise. Whether analyzing A/B tests or assessing customer retention improvements, statistical hypothesis testing provides the mathematical foundation.

#### Core Concepts:
1. **Central Tendency & Skewness**:
   * For symmetric normal distributions: Mean $\\approx$ Median.
   * For right-skewed distributions (e.g., income, order value, SaaS LTV): Median is resistant to extreme outliers, while Mean is pulled to the right. Always report Median + IQR for skewed business data!
2. **Hypothesis Testing Framework**:
   * **Null Hypothesis ($H_0$)**: No real difference exists; observed difference is due to chance.
   * **Alternative Hypothesis ($H_1$)**: A statistically significant difference exists.
3. **The p-value**:
   * The probability of observing results at least as extreme as the sample data, assuming $H_0$ is true.
   * If $p < \\alpha$ (typically $0.05$): Reject $H_0$. The difference is statistically significant.
   * If $p \\ge \\alpha$: Fail to reject $H_0$. Insufficient evidence of an effect.
4. **Errors in Decision Making**:
   * **Type I Error (False Positive)**: Claiming an effect exists when it doesn't (Rejecting true $H_0$). Probability = $\\alpha$.
   * **Type II Error (False Negative)**: Failing to detect a real effect (Failing to reject false $H_0$). Probability = $\\beta$. Power = $1 - \\beta$.""",
        "key_rules": "- In skewed distributions, report Median and IQR instead of Mean and Standard Deviation\n- p < 0.05 indicates statistical significance, not necessarily practical business significance\n- Always verify sample size and statistical power before declaring a feature launch failed",
        "common_mistakes": "- Conflating correlation with causation\n- Interpreting p-value as the probability that the null hypothesis is true\n- Stopping A/B tests early as soon as p < 0.05 without reaching required sample size (p-hacking)",
        "worked_example": {
            "scenario": "An e-commerce firm tests a new checkout flow (Variant B) against the control (Variant A). Conversion rates are recorded across 10,000 visitors per variant.",
            "code": "from scipy import stats\n\ndef evaluate_ab_test(conv_a: int, n_a: int, conv_b: int, n_b: int, alpha: float = 0.05):\n    # Two-proportion z-test\n    p_a = conv_a / n_a\n    p_b = conv_b / n_b\n    p_pool = (conv_a + conv_b) / (n_a + n_b)\n    se = (p_pool * (1 - p_pool) * (1/n_a + 1/n_b)) ** 0.5\n    z_stat = (p_b - p_a) / se\n    p_val = 2 * (1 - stats.norm.cdf(abs(z_stat)))\n    \n    is_significant = p_val < alpha\n    return {'rate_a': p_a, 'rate_b': p_b, 'p_value': p_val, 'significant': is_significant}",
            "reasoning": "Computes pooled standard error, standard z-score, and two-tailed p-value to establish significance rigorously.",
            "expected_output": "{'rate_a': 0.042, 'rate_b': 0.051, 'p_value': 0.0031, 'significant': True}"
        },
        "guided_practice": {
            "prompt": "Write a Python function using `scipy.stats.ttest_ind` to compare customer spending between loyalty program members and non-members. Return whether the difference is significant at alpha = 0.05.",
            "starter_code": "from scipy import stats\nimport numpy as np\n\ndef test_loyalty_spend(members: np.ndarray, non_members: np.ndarray) -> bool:\n    # Execute two-sample t-test\n    pass",
            "solution": "from scipy import stats\nimport numpy as np\n\ndef test_loyalty_spend(members: np.ndarray, non_members: np.ndarray) -> bool:\n    stat, p_val = stats.ttest_ind(members, non_members, equal_var=False)\n    return p_val < 0.05",
            "hints": [
                "Use stats.ttest_ind(members, non_members, equal_var=False) for Welch's t-test.",
                "Compare the returned p_value against 0.05.",
                "Return True if p_value < 0.05, else False."
            ]
        },
        "independent_practice": {
            "prompt": "Given a skewed array of order amounts, write a function that calculates the Median, 25th percentile (Q1), 75th percentile (Q3), and the Interquartile Range (IQR).",
            "starter_code": "import numpy as np\n\ndef robust_spread(data: np.ndarray) -> dict:\n    # Compute median, Q1, Q3, IQR\n    pass",
            "solution": "import numpy as np\n\ndef robust_spread(data: np.ndarray) -> dict:\n    q1 = float(np.percentile(data, 25))\n    median = float(np.median(data))\n    q3 = float(np.percentile(data, 75))\n    return {'median': median, 'q1': q1, 'q3': q3, 'iqr': q3 - q1}",
            "test_criteria": "Uses np.percentile and np.median, calculates IQR = Q3 - Q1."
        },
        "concept_check": [
            {
                "question_text": "In a right-skewed revenue distribution with several multi-million dollar enterprise clients, which measure of central tendency provides the most representative benchmark for a typical customer?",
                "options": ["Mean", "Median", "Standard Deviation", "Variance"],
                "correct": "Median",
                "explanation": "The median is robust against high-magnitude right-tail outliers that artificially inflate the arithmetic mean."
            },
            {
                "question_text": "What does a p-value of 0.02 indicate in a two-tailed hypothesis test with significance level alpha = 0.05?",
                "options": [
                    "Reject the null hypothesis; the observed effect is statistically significant",
                    "Fail to reject the null hypothesis; no effect exists",
                    "There is a 98% probability that the alternative hypothesis is true",
                    "The test sample was biased"
                ],
                "correct": "Reject the null hypothesis; the observed effect is statistically significant",
                "explanation": "Since p (0.02) < alpha (0.05), we reject the null hypothesis and declare statistical significance."
            },
            {
                "question_text": "What is a Type II Error in experimentation?",
                "options": [
                    "Rejecting the null hypothesis when it is actually true (False Positive)",
                    "Failing to reject the null hypothesis when a real effect exists (False Negative)",
                    "Calculating standard deviation incorrectly",
                    "Drawing a sample with zero variance"
                ],
                "correct": "Failing to reject the null hypothesis when a real effect exists (False Negative)",
                "explanation": "Type II error (beta) occurs when a real effect exists in reality but the test lacks power to detect it."
            }
        ],
        "applied_task": {
            "role_scenario": "Product Experimentation Analysis",
            "task_description": "Analyze A/B test conversion data for an onboarding flow to determine if feature adoption is statistically significant.",
            "starter_code": "def evaluate_onboarding_experiment(control_group, treatment_group):\n    # Statistical comparison\n    pass",
            "rubrics": "Formulates hypothesis, executes appropriate test, correctly interprets p-value and statistical significance."
        }
    },

    # -------------------------------------------------------------------------
    # 5. Exploratory Data Analysis (EDA)
    # -------------------------------------------------------------------------
    {
        "slug": "eda-workflow-data-profiling",
        "skill_name": "EDA",
        "title": "Exploratory Data Analysis, Outlier Detection & Profiling",
        "concept_name": "EDA Workflows, Imputation Strategies & Anomaly Detection",
        "difficulty": "Intermediate",
        "estimated_minutes": 30,
        "order_index": 5,
        "prerequisite_concept_slugs": "python-pandas-pipelines,statistics-hypothesis-testing",
        "target_role_name": "All",
        "learning_objectives": [
            "Conduct structured exploratory profiling on multi-dimensional tabular datasets",
            "Detect data anomalies and outliers using IQR and Z-score boundaries",
            "Apply principled missing data treatment (deletion vs. mean/median vs. model-based imputation)",
        ],
        "explanation": """### The Systematic EDA Workflow
Before any predictive model is trained or executive dashboard is built, Exploratory Data Analysis (EDA) uncovers structural distributions, relationships, missingness patterns, and outliers.

#### The 4-Step EDA Sequence:
1. **Structural Profiling**:
   * Inspect shapes, data types, and cardinality: `df.info()`, `df.describe()`, `df.nunique()`.
2. **Missing Value Diagnostics**:
   * Missing completely at random (MCAR) vs. Missing at random (MAR) vs. Missing not at random (MNAR).
   * For numerical columns with skew, impute with **Median** rather than Mean to avoid shifting the distribution.
3. **Outlier Detection**:
   * **IQR Rule (Tukey's Fences)**:
     $$\\text{Lower Bound} = Q1 - 1.5 \\times \\text{IQR}, \\quad \\text{Upper Bound} = Q3 + 1.5 \\times \\text{IQR}$$
   * **Z-score Threshold**: Flags observations where $|z| = \\left|\\frac{x - \\mu}{\\sigma}\\right| > 3.0$ (for normally distributed variables).
4. **Bivariate & Correlation Analysis**:
   * Pearson correlation measures linear association; Spearman correlation measures monotonic relationships.
   * Check for multicollinearity ($r > 0.85$) prior to regression modeling.""",
        "key_rules": "- Check distribution skewness before selecting imputation method\n- Never blindly drop outliers without determining if they represent fraudulent or high-value authentic events\n- Verify correlation matrix for multicollinearity",
        "common_mistakes": "- Imputing test set data using test set statistics (Data Leakage! Always fit imputation on training set)\n- Treating missing values as 0 automatically\n- Overlooking categorical cardinality explosion",
        "worked_example": {
            "scenario": "Detect and cap extreme transaction outliers in a payments dataset using Tukey's IQR rule.",
            "code": "import numpy as np\nimport pandas as pd\n\ndef treat_outliers_iqr(df: pd.DataFrame, column: str) -> pd.DataFrame:\n    q1 = df[column].quantile(0.25)\n    q3 = df[column].quantile(0.75)\n    iqr = q3 - q1\n    lower_limit = q1 - 1.5 * iqr\n    upper_limit = q3 + 1.5 * iqr\n    \n    # Windorize / Cap boundaries\n    capped_df = df.copy()\n    capped_df[f'{column}_capped'] = np.clip(capped_df[column], lower_limit, upper_limit)\n    return capped_df",
            "reasoning": "Calculates Q1 and Q3, determines 1.5x IQR boundaries, and caps values rather than discarding valid rows.",
            "expected_output": "Creates capped column containing preserved values constrained within realistic bounds."
        },
        "guided_practice": {
            "prompt": "Write a function `audit_missingness(df)` that returns a summary DataFrame listing each column, count of missing values, and the percentage of missing values, ordered by missing percentage descending.",
            "starter_code": "import pandas as pd\n\ndef audit_missingness(df: pd.DataFrame) -> pd.DataFrame:\n    # Return DataFrame with ['column', 'missing_count', 'missing_pct']\n    pass",
            "solution": "import pandas as pd\n\ndef audit_missingness(df: pd.DataFrame) -> pd.DataFrame:\n    missing_count = df.isna().sum()\n    missing_pct = (missing_count / len(df)) * 100\n    summary = pd.DataFrame({'missing_count': missing_count, 'missing_pct': missing_pct})\n    return summary[summary['missing_count'] > 0].sort_values(by='missing_pct', ascending=False).reset_index().rename(columns={'index': 'column'})",
            "hints": [
                "Use df.isna().sum() to count missing records per column.",
                "Calculate percentage as (missing_count / len(df)) * 100.",
                "Filter for columns where missing_count > 0 and sort descending."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function that identifies all numeric columns in a DataFrame that have a Pearson correlation coefficient greater than 0.80 with the target column `'target'`, excluding the target column itself.",
            "starter_code": "import pandas as pd\n\ndef high_corr_features(df: pd.DataFrame, target: str) -> list:\n    # Return list of feature names with |r| > 0.80\n    pass",
            "solution": "import pandas as pd\n\ndef high_corr_features(df: pd.DataFrame, target: str) -> list:\n    corr = df.corr(numeric_only=True)[target].drop(target)\n    return corr[corr.abs() > 0.80].index.tolist()",
            "test_criteria": "Calculates correlation with target, drops target self-correlation, filters for absolute correlation > 0.80."
        },
        "concept_check": [
            {
                "question_text": "What is the primary danger of imputing missing values in a machine learning workflow using the mean of the entire combined dataset (train + test)?",
                "options": [
                    "Data leakage: Information from the test set leaks into the training pipeline, leading to overly optimistic evaluation",
                    "It causes memory crashes in Pandas",
                    "It transforms the target variable into a categorical string",
                    "It breaks the correlation matrix"
                ],
                "correct": "Data leakage: Information from the test set leaks into the training pipeline, leading to overly optimistic evaluation",
                "explanation": "Imputation statistics must be learned strictly on training data and applied to test data to prevent data leakage."
            },
            {
                "question_text": "In Tukey's IQR rule for outlier detection, what is the upper boundary formula?",
                "options": ["Mean + 3 * Std", "Q3 + 1.5 * IQR", "Median + 2 * IQR", "Q3 + 3.0 * IQR"],
                "correct": "Q3 + 1.5 * IQR",
                "explanation": "Tukey's standard fence uses Q3 + 1.5 * IQR for mild outliers, and Q3 + 3.0 * IQR for extreme outliers."
            },
            {
                "question_text": "When is Spearman rank correlation preferred over Pearson correlation?",
                "options": [
                    "When variables exhibit a monotonic non-linear relationship or contain significant outliers",
                    "Only when working with time-series data",
                    "When all variables are perfectly normally distributed",
                    "When sample size is under 10 rows"
                ],
                "correct": "When variables exhibit a monotonic non-linear relationship or contain significant outliers",
                "explanation": "Spearman evaluates monotonic relationships based on ranks, making it robust to non-linearity and outliers."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Science Preprocessing & EDA",
            "task_description": "Profile customer transaction dataset, handle missing values in income, treat high-value transaction outliers, and summarize key drivers.",
            "starter_code": "def run_eda_pipeline(df: pd.DataFrame):\n    # Complete end-to-end data audit and cleaning\n    pass",
            "rubrics": "Correctly profiles missingness, imputes with median, identifies outliers via IQR boundaries, outputs clean DataFrame."
        }
    },

    # -------------------------------------------------------------------------
    # 6. Machine Learning Foundations
    # -------------------------------------------------------------------------
    {
        "slug": "machine-learning-foundations",
        "skill_name": "Machine Learning",
        "title": "Supervised Learning, Model Evaluation & Regularization",
        "concept_name": "Supervised ML, Bias-Variance Tradeoff & Evaluation Metrics",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "order_index": 6,
        "prerequisite_concept_slugs": "python-pandas-pipelines,statistics-hypothesis-testing,eda-workflow-data-profiling",
        "target_role_name": "Data Scientist, ML Engineer",
        "learning_objectives": [
            "Distinguish between regression and classification tasks and select appropriate loss functions",
            "Navigate the Bias-Variance tradeoff through cross-validation and L1/L2 regularization",
            "Evaluate models using Precision, Recall, F1-Score, ROC-AUC, and Confusion Matrices",
        ],
        "explanation": """### The Supervised Machine Learning Paradigm
Supervised machine learning fits a parameter or tree structure to map input features $X$ to ground-truth labels $y$. Achieving production-grade performance requires balancing model complexity and generalization.

#### 1. The Bias-Variance Tradeoff:
* **High Bias (Underfitting)**: Model is overly simplistic (e.g. linear model on non-linear data). Exhibits high training error and high validation error.
* **High Variance (Overfitting)**: Model memorizes training noise (e.g. unpruned deep decision tree). Exhibits near-zero training error but poor validation generalization.

#### 2. Regularization Mechanisms:
* **L1 Regularization (Lasso)**: Adds $\\lambda \\sum |w_i|$ penalty. Drives non-informative coefficients strictly to 0, performing automatic feature selection.
* **L2 Regularization (Ridge)**: Adds $\\lambda \\sum w_i^2$ penalty. Shrinks weights toward zero smoothly without zeroing them out, reducing multicollinearity sensitivity.

#### 3. Classification Evaluation Metrics:
* **Accuracy**: $\\frac{TP + TN}{\\text{Total}}$. Misleading on imbalanced datasets (e.g. 99% non-fraud).
* **Precision**: $\\frac{TP}{TP + FP}$. Of all positive predictions, how many were correct? Critical when False Positives are costly (e.g. spam filtering).
* **Recall (Sensitivity)**: $\\frac{TP}{TP + FN}$. Of all actual positive cases, how many did the model catch? Critical when False Negatives are catastrophic (e.g. cancer detection, fraud prevention).
* **F1-Score**: Harmonic mean of Precision and Recall: $2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}}$.
* **ROC-AUC**: Evaluates model discrimination across all classification probability thresholds.""",
        "key_rules": "- Never evaluate classification performance using accuracy alone on imbalanced datasets\n- Use stratified K-fold cross validation for classification tasks\n- Scale features with StandardScaler before applying L1/L2 regularized algorithms",
        "common_mistakes": "- Evaluating models on training data instead of held-out validation sets\n- Fitting Scalers or Transformers on combined train and test splits (Data leakage)\n- Optimizing accuracy when the business metric prioritizes recall or precision",
        "worked_example": {
            "scenario": "Train a regularized logistic regression model to predict customer churn, evaluate cross-validated ROC-AUC, and print classification report.",
            "code": "from sklearn.model_selection import train_test_split, cross_val_score\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.metrics import classification_report, roc_auc_score\nimport numpy as np\n\ndef train_churn_model(X, y):\n    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)\n    scaler = StandardScaler()\n    X_train_scaled = scaler.fit_transform(X_train)\n    X_test_scaled = scaler.transform(X_test)\n    \n    model = LogisticRegression(C=1.0, penalty='l2', solver='lbfgs')\n    model.fit(X_train_scaled, y_train)\n    \n    preds = model.predict(X_test_scaled)\n    probs = model.predict_proba(X_test_scaled)[:, 1]\n    auc = roc_auc_score(y_test, probs)\n    return {'model': model, 'auc': auc, 'report': classification_report(y_test, preds)}",
            "reasoning": "Splits with stratification, fits scaler only on train split, fits L2 model, and evaluates with ROC-AUC.",
            "expected_output": "Outputs trained model with generalization ROC-AUC score and full precision/recall metrics."
        },
        "guided_practice": {
            "prompt": "Write a function `evaluate_binary_model(y_true, y_pred)` that computes and returns Precision, Recall, and F1-score as a dictionary.",
            "starter_code": "from sklearn.metrics import precision_score, recall_score, f1_score\n\ndef evaluate_binary_model(y_true, y_pred) -> dict:\n    # Calculate precision, recall, f1\n    pass",
            "solution": "from sklearn.metrics import precision_score, recall_score, f1_score\n\ndef evaluate_binary_model(y_true, y_pred) -> dict:\n    return {\n        'precision': round(float(precision_score(y_true, y_pred)), 4),\n        'recall': round(float(recall_score(y_true, y_pred)), 4),\n        'f1': round(float(f1_score(y_true, y_pred)), 4),\n    }",
            "hints": [
                "Import precision_score, recall_score, and f1_score from sklearn.metrics.",
                "Call each metric function passing (y_true, y_pred).",
                "Return a dictionary containing all three metrics."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function that accepts training and testing data, fits a `RandomForestClassifier` with 100 trees and max_depth=5, and returns the feature importance rankings sorted in descending order.",
            "starter_code": "from sklearn.ensemble import RandomForestClassifier\nimport pandas as pd\n\ndef feature_importance_rank(X_train, y_train, feature_names: list) -> pd.DataFrame:\n    # Fit RandomForest and return feature importances\n    pass",
            "solution": "from sklearn.ensemble import RandomForestClassifier\nimport pandas as pd\n\ndef feature_importance_rank(X_train, y_train, feature_names: list) -> pd.DataFrame:\n    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)\n    rf.fit(X_train, y_train)\n    return pd.DataFrame({'feature': feature_names, 'importance': rf.feature_importances_}).sort_values(by='importance', ascending=False).reset_index(drop=True)",
            "test_criteria": "Initializes and fits RandomForestClassifier, maps feature_importances_ to names, sorts descending."
        },
        "concept_check": [
            {
                "question_text": "In a medical diagnostic classifier detecting a rare disease where missing an infected patient is fatal, which evaluation metric must be maximized?",
                "options": ["Recall (Sensitivity)", "Precision", "Overall Accuracy", "Specificity"],
                "correct": "Recall (Sensitivity)",
                "explanation": "Recall measures the proportion of actual positive cases detected. Maximizing recall minimizes False Negatives."
            },
            {
                "question_text": "What is the primary difference between L1 (Lasso) and L2 (Ridge) regularization?",
                "options": [
                    "L1 can shrink coefficients exactly to zero, performing feature selection; L2 shrinks weights asymptotically toward zero",
                    "L2 cannot be used with gradient descent",
                    "L1 only works on decision trees",
                    "L2 eliminates features completely"
                ],
                "correct": "L1 can shrink coefficients exactly to zero, performing feature selection; L2 shrinks weights asymptotically toward zero",
                "explanation": "The L1 diamond-shaped constraint boundary produces sparse solutions where non-essential weights become exactly 0."
            },
            {
                "question_text": "A classification model achieves 99.2% accuracy on a fraud detection dataset where 99.2% of transactions are legitimate and 0.8% are fraudulent. What is most likely true?",
                "options": [
                    "The model has achieved state-of-the-art predictive mastery",
                    "The model may be a trivial classifier predicting 'No Fraud' for every transaction, with zero fraud detection capability",
                    "The model has high variance and is severely overfitting",
                    "The dataset requires no further exploration"
                ],
                "correct": "The model may be a trivial classifier predicting 'No Fraud' for every transaction, with zero fraud detection capability",
                "explanation": "Due to class imbalance, predicting the majority class yields high accuracy while failing completely at detecting actual fraud."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Science / ML Engineering Churn Prevention",
            "task_description": "Build a cross-validated predictive classification model predicting customer churn, tuning threshold to maximize recall for high-value cohorts.",
            "starter_code": "def build_churn_predictor(X, y):\n    # ML pipeline training and threshold tuning\n    pass",
            "rubrics": "Uses stratified splitting, applies feature scaling, trains classifier, tunes probability threshold, evaluates F1/ROC-AUC."
        }
    },
]

from app.seed.role_modules_data import ADDITIONAL_LEARNING_MODULES_SEED, LEARNING_RESOURCES_SEED

LEARNING_MODULES_SEED.extend(ADDITIONAL_LEARNING_MODULES_SEED)

__all__ = ["LEARNING_MODULES_SEED", "LEARNING_RESOURCES_SEED"]

