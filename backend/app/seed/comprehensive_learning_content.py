"""
SkillPath AI - Authoritative First-Party Learning Curriculum Content
Phase 22 - In-Depth First-Party Educational Content Expansion.

Design Invariant:
- SkillPath itself provides an exhaustive, university-grade, professional first-party learning experience.
- External learning resources (GeeksforGeeks, W3Schools, Khan Academy, Coursera, DataCamp)
  serve strictly as optional supplementary reinforcement under 'Further resources'.
- Content is level-aware (Beginner, Intermediate, Advanced) and role-tailored (Data Analyst, Data Scientist, Python Developer).
- Detailed 6-part Worked Examples: Problem -> Approach -> Solution -> Result -> Why It Works -> Production Alternative.
- Detailed Common Mistakes: What it looks like -> Why it happens -> How to fix it.
- Comprehensive Quick Reference: Key terms, Formulas & Rules, Decision Matrix, Core Takeaways.
"""

from typing import Dict, Any

COMPREHENSIVE_MODULE_ENHANCEMENTS: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 1. SQL JOINs Mastery
    # =========================================================================
    "sql-joins-mastery": {
        "title": "Multi-Table Relational Merges & Null Safety",
        "concept_name": "SQL Multi-Table JOINs & Null Handling",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Master relational join mechanics: INNER, LEFT, RIGHT, and FULL OUTER joins using set-theoretic mental models",
            "Identify candidate join keys by analyzing Primary Key to Foreign Key relationships to avoid unintended Cartesian fan-out",
            "Preserve unmatched cohort records with LEFT JOINs and prevent catastrophic silent cohort data loss",
            "Handle NULL values safely using COALESCE() to eliminate three-valued logic corruption in financial and KPI aggregations",
            "Differentiate filtering in the ON clause vs the WHERE clause in outer joins to maintain query correctness",
            "Select the optimal join strategy for business questions such as churn analysis, cohort retention, and multi-tier reporting",
        ],
        "explanation": """### 1. Conceptual Foundation & The Relational Model
In modern relational databases and enterprise data warehouses, information is normalized across separate tables to prevent data duplication and maintain transactional integrity. However, business decisions cannot be made by looking at a single table in isolation. To answer high-stakes business questions—such as *"Which customer tier generated the highest net revenue after refunds?"*—we must combine normalized tables along relationship keys.

Consider two core relational tables in an e-commerce platform:

#### Customers Table (`customers`)
| customer_id | name | segment | signup_date |
| :--- | :--- | :--- | :--- |
| **1** | Arun Sharma | Enterprise | 2024-01-10 |
| **2** | Meena Patel | Mid-Market | 2024-02-14 |
| **3** | Rahul Verma | SMB | 2024-03-01 |

#### Orders Table (`orders`)
| order_id | customer_id | order_date | amount | status |
| :--- | :--- | :--- | :--- | :--- |
| **101** | **1** | 2024-01-15 | $500.00 | COMPLETED |
| **102** | **1** | 2024-02-10 | $750.00 | COMPLETED |
| **103** | **2** | 2024-02-18 | $1,200.00 | COMPLETED |

Notice that **Rahul Verma (Customer ID 3)** signed up in March but has placed **zero orders**. This asymmetry is the fundamental challenge of relational joins. If an analyst performs an `INNER JOIN`, Rahul Verma is discarded completely from the dataset. Any subsequent count of customers or churn analysis will be corrupted.

---

### 2. The Four Primary Relational Join Types

```
  INNER JOIN (Intersection)            LEFT JOIN (All Left + Matching Right)
     ┌───────┬───────┐                     ┌───────┬───────┐
     │   A   │ A ∩ B │   B   │             │███████│███████│   B   │
     │       │       │       │             │██ A ██│█A ∩ B█│       │
     └───────┴───────┘                     └───────┴───────┘
```

1. **`INNER JOIN` (Set Intersection)**:
   Returns only records where the join key matches in **both** the left and right tables.
   $$\\text{Result} = \\{ (a, b) \\mid a \\in A, b \\in B, \\text{Key}(a) = \\text{Key}(b) \\}$$
   *When to use:* When you only care about events that have confirmed transactional pairs (e.g., shipments that have valid invoices).

2. **`LEFT OUTER JOIN` (Left Preservation)**:
   Returns **every record from the left table**, alongside matching records from the right table. When no match exists in the right table, the engine fills all right-table columns with `NULL`.
   *When to use:* Whenever the left table represents the master cohort (e.g., all active registered users, all products in catalog) and the right table represents optional occurrences (e.g., orders placed, discounts applied, returns filed).

3. **`RIGHT OUTER JOIN`**:
   The exact mirror image of `LEFT JOIN`. In modern production SQL style guides, `RIGHT JOIN` is discouraged in favor of `LEFT JOIN` by reordering tables, which makes reading queries top-to-bottom intuitive.

4. **`FULL OUTER JOIN` (Set Union)**:
   Preserves all rows from both tables. Rows that match on the join key are merged; rows with no match in either direction are filled with `NULL`. Essential for reconciling accounts, such as bank transaction logs vs ledger entries.

5. **`CROSS JOIN` (Cartesian Product)**:
   Pairs every row in Table A with every row in Table B. If Table A has 1,000 rows and Table B has 1,000 rows, a `CROSS JOIN` produces 1,000,000 rows. Usually an unintended bug caused by a missing `ON` condition.

---

### 3. Key Terminology Reference

* **Primary Key (PK)**: A column or set of columns guaranteeing row uniqueness in its native table (e.g., `customers.customer_id`).
* **Foreign Key (FK)**: A column in a child table referencing a Primary Key in a parent table (e.g., `orders.customer_id`).
* **Join Key / Predicate**: The logical expression in the `ON` clause determining row linkage (e.g., `ON c.customer_id = o.customer_id`).
* **Multiplicity (Fan-Out)**: The cardinality of the match. In a One-to-Many ($1:N$) join, one customer row is replicated $N$ times if the customer has $N$ orders.
* **Three-Valued Logic (3VL)**: SQL's logic model where boolean comparisons yield `TRUE`, `FALSE`, or `UNKNOWN` (NULL). Comparing with `= NULL` always evaluates to `UNKNOWN`.
* **Null Coalescing (`COALESCE`)**: A standard SQL function that evaluates arguments in sequence and returns the first non-null value:
  $$\\text{COALESCE}(\\text{refund}, 0) = \\begin{cases} \\text{refund} & \\text{if } \\text{refund} \\neq \\text{NULL} \\\\ 0 & \\text{if } \\text{refund} = \\text{NULL} \\end{cases}$$

---

### 4. Null Safety & The Arithmetic Pitfall
In SQL, arithmetic operations involving `NULL` automatically evaluate to `NULL`:
$$\\text{Gross Revenue} (\\$5,000) - \\text{Refund} (\\text{NULL}) = \\text{NULL}$$
If an analyst executes:
```sql
SELECT c.name, SUM(o.amount) - SUM(r.refund_amount) AS net_revenue
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN returns r ON o.order_id = r.order_id
GROUP BY c.name;
```
For any customer who has **zero refunds**, `SUM(r.refund_amount)` evaluates to `NULL`. Consequently, `SUM(o.amount) - NULL` evaluates to `NULL`, silently erasing thousands of dollars of legitimate customer revenue!
**The Defensive Pattern:** Always wrap nullable numerical fields in `COALESCE(SUM(r.refund_amount), 0.0)`.

---

### 5. The Critical ON vs WHERE Distinction in Outer Joins
A widespread mistake in SQL is placing filter conditions for the right table in the `WHERE` clause instead of the `ON` clause:
```sql
-- INCORRECT: Silently converts LEFT JOIN into INNER JOIN!
SELECT c.name, o.amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date >= '2024-01-01';
```
**Why this fails:** For customers without orders, `o.order_date` is `NULL`. The condition `'NULL >= 2024-01-01'` evaluates to `UNKNOWN`, which the `WHERE` clause discards. Customers with zero orders are wiped out!

**The Correct Pattern:**
```sql
-- CORRECT: Preserves all customers while filtering orders
SELECT c.name, o.amount
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
                  AND o.order_date >= '2024-01-01';
```""",
        "code_examples": [
            {
                "title": "Example 1: Safe Multi-Table Merge with Null Coalescing",
                "language": "sql",
                "code": """-- Multi-table join preserving all customers and handling null refunds safely
SELECT
    c.customer_id,
    c.name AS customer_name,
    c.segment,
    COUNT(DISTINCT o.order_id) AS total_completed_orders,
    ROUND(COALESCE(SUM(o.amount), 0.0), 2) AS gross_spend,
    ROUND(COALESCE(SUM(r.refund_amount), 0.0), 2) AS total_refunds,
    ROUND(COALESCE(SUM(o.amount), 0.0) - COALESCE(SUM(r.refund_amount), 0.0), 2) AS net_revenue
FROM customers c
LEFT JOIN orders o 
    ON c.customer_id = o.customer_id 
    AND o.status = 'COMPLETED'
LEFT JOIN returns r 
    ON o.order_id = r.order_id
GROUP BY c.customer_id, c.name, c.segment
ORDER BY net_revenue DESC;""",
                "explanation": "Uses LEFT JOIN for both orders and returns. Wraps sums in COALESCE to guarantee that customers without orders or without refunds return $0.00 rather than NULL. Uses COUNT(DISTINCT o.order_id) to prevent duplicate row counts caused by multiple return items."
            },
            {
                "title": "Example 2: The Anti-Join Pattern (Finding Inactive or Unmatched Records)",
                "language": "sql",
                "code": """-- Anti-Join: Identify all registered users who have NEVER placed an order
SELECT
    c.customer_id,
    c.name,
    c.signup_date,
    JULIANDAY('now') - JULIANDAY(c.signup_date) AS days_since_signup
FROM customers c
LEFT JOIN orders o 
    ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL
ORDER BY c.signup_date ASC;""",
                "explanation": "By performing a LEFT JOIN and filtering WHERE o.order_id IS NULL, the database engine returns exactly the cohort of users who have no corresponding records in the orders table. Highly performant for re-engagement marketing campaigns."
            },
            {
                "title": "Example 3: Safe Aggregation Prior to Join (Preventing Fan-Out Corruption)",
                "language": "sql",
                "code": """-- Production Pattern: Pre-aggregate child records in a Common Table Expression (CTE)
WITH customer_order_summary AS (
    SELECT
        customer_id,
        COUNT(order_id) AS order_count,
        SUM(amount) AS total_spend
    FROM orders
    WHERE status = 'COMPLETED'
    GROUP BY customer_id
),
customer_ticket_summary AS (
    SELECT
        customer_id,
        COUNT(ticket_id) AS support_tickets
    FROM support_tickets
    GROUP BY customer_id
)
SELECT
    c.customer_id,
    c.name,
    c.segment,
    COALESCE(cos.order_count, 0) AS total_orders,
    COALESCE(cos.total_spend, 0.0) AS gross_spend,
    COALESCE(cts.support_tickets, 0) AS open_tickets
FROM customers c
LEFT JOIN customer_order_summary cos ON c.customer_id = cos.customer_id
LEFT JOIN customer_ticket_summary cts ON c.customer_id = cts.customer_id
ORDER BY gross_spend DESC;""",
                "explanation": "If orders and support tickets are joined directly in a single query, a customer with 10 orders and 5 tickets will produce 50 rows (Cartesian explosion), causing SUM(spend) to be multiplied by 5! Pre-aggregating in CTEs ensures a clean 1:1 join."
            }
        ],
        "worked_example": {
            "title": "Enterprise Cohort Financial Reconciliation",
            "scenario": "A subscription software company needs an executive cohort financial summary for Q1 2024. The CFO requires a breakdown by customer tier showing total active accounts, total recurring billing, total refund write-offs, and true net revenue. Accounts with zero orders or zero write-offs must be included without throwing nulls or corrupting segment totals.",
            "problem": "Calculate segment-level active accounts, total gross billing, total refund write-offs, and net realized revenue, ensuring that accounts without billing or without refunds do not distort totals or disappear from executive reporting.",
            "approach": "1. Treat `customers` as the primary cohort dimension to retain all enterprise, mid-market, and SMB accounts.\n2. Left join `subscriptions` filtered by active Q1 dates to capture recurring invoices.\n3. Left join `disputes_and_refunds` on invoice IDs to capture credit adjustments.\n4. Apply COALESCE() to all monetary sums to ensure zero refunds evaluate to $0.00 rather than NULL.\n5. Group by customer segment and sort by net realized revenue descending.",
            "code": """SELECT
    c.segment AS account_tier,
    COUNT(DISTINCT c.customer_id) AS total_accounts,
    COUNT(DISTINCT s.subscription_id) AS active_subscriptions,
    ROUND(COALESCE(SUM(s.billing_amount), 0.0), 2) AS gross_billing,
    ROUND(COALESCE(SUM(r.refund_amount), 0.0), 2) AS refund_writeoffs,
    ROUND(COALESCE(SUM(s.billing_amount), 0.0) - COALESCE(SUM(r.refund_amount), 0.0), 2) AS net_revenue
FROM customers c
LEFT JOIN subscriptions s 
    ON c.customer_id = s.customer_id
    AND s.billing_date BETWEEN '2024-01-01' AND '2024-03-31'
    AND s.status = 'ACTIVE'
LEFT JOIN disputes_and_refunds r 
    ON s.invoice_id = r.invoice_id
GROUP BY c.segment
ORDER BY net_revenue DESC;""",
            "expected_output": "| account_tier | total_accounts | active_subscriptions | gross_billing | refund_writeoffs | net_revenue |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n| Enterprise | 45 | 52 | $485,000.00 | $12,400.00 | $472,600.00 |\n| Mid-Market | 120 | 114 | $228,000.00 | $4,500.00 | $223,500.00 |\n| SMB | 350 | 280 | $140,000.00 | $8,200.00 | $131,800.00 |",
            "reasoning": "Using LEFT JOIN ensures all 350 SMB accounts are visible even though only 280 have active subscriptions. COALESCE ensures that the 100+ accounts without refund disputes do not yield NULL for net revenue. Filtering dates in the ON clause preserves customers with zero Q1 subscriptions.",
            "why_it_works": "The database optimizer processes the FROM clause first, scanning customers as the outer loop. For each customer, matching subscriptions are joined. If none match, a synthetic NULL row is generated, allowing COUNT(DISTINCT c.customer_id) to accurately reflect the complete account population.",
            "alternative": """-- Alternative CTE Approach (Recommended for high-volume distributed data warehouses):
WITH q1_billing AS (
    SELECT customer_id, COUNT(subscription_id) AS active_subs, SUM(billing_amount) AS total_bill
    FROM subscriptions
    WHERE billing_date BETWEEN '2024-01-01' AND '2024-03-31' AND status = 'ACTIVE'
    GROUP BY customer_id
),
q1_refunds AS (
    SELECT s.customer_id, SUM(r.refund_amount) AS total_ref
    FROM subscriptions s
    JOIN disputes_and_refunds r ON s.invoice_id = r.invoice_id
    WHERE s.billing_date BETWEEN '2024-01-01' AND '2024-03-31'
    GROUP BY s.customer_id
)
SELECT
    c.segment AS account_tier,
    COUNT(c.customer_id) AS total_accounts,
    COALESCE(SUM(b.active_subs), 0) AS active_subscriptions,
    ROUND(COALESCE(SUM(b.total_bill), 0.0), 2) AS gross_billing,
    ROUND(COALESCE(SUM(r.total_ref), 0.0), 2) AS refund_writeoffs,
    ROUND(COALESCE(SUM(b.total_bill), 0.0) - COALESCE(SUM(r.total_ref), 0.0), 2) AS net_revenue
FROM customers c
LEFT JOIN q1_billing b ON c.customer_id = b.customer_id
LEFT JOIN q1_refunds r ON c.customer_id = r.customer_id
GROUP BY c.segment
ORDER BY net_revenue DESC;"""
        },
        "common_mistakes": """### Mistake 1 — Silent Cohort Loss with INNER JOIN
* **What it looks like:** `SELECT c.segment, COUNT(o.id) FROM customers c INNER JOIN orders o ON c.id = o.customer_id GROUP BY c.segment;`
* **Why it happens:** The analyst wants to see customer orders by segment, but doesn't realize customers who placed 0 orders are dropped completely.
* **How to fix it:** Use `LEFT JOIN` and aggregate using `COUNT(o.id)` (which evaluates to 0 for non-ordering customers), rather than `COUNT(*)` (which would mistakenly count the NULL row as 1).

### Mistake 2 — Null Arithmetic Corruption
* **What it looks like:** `SELECT SUM(amount) - SUM(refund_amount) AS net_sales ...`
* **Why it happens:** If even a single customer segment has 0 refunds, `SUM(refund_amount)` is `NULL`. In SQL, `amount - NULL = NULL`.
* **How to fix it:** Always use `COALESCE(SUM(refund_amount), 0.0)` for all arithmetic expressions.

### Mistake 3 — The WHERE Clause Outer Join Trap
* **What it looks like:** `FROM customers c LEFT JOIN orders o ON c.id = o.customer_id WHERE o.order_date >= '2024-01-01'`
* **Why it happens:** The analyst believes the WHERE clause filters only the orders. However, unmatched customers have `o.order_date = NULL`. Since `NULL >= '2024-01-01'` is false, all customers without orders are eliminated, turning the LEFT JOIN into an INNER JOIN.
* **How to fix it:** Move right-table filter predicates into the `ON` clause: `ON c.id = o.customer_id AND o.order_date >= '2024-01-01'`.

### Mistake 4 — Cartesian Multiplication (Fan-Out Explosion)
* **What it looks like:** Joining a customer to both their orders and their customer support tickets in a single flat join.
* **Why it happens:** 1 customer with 5 orders and 4 tickets generates $5 \\times 4 = 20$ rows. Summing order totals over these rows multiplies actual revenue by 4!
* **How to fix it:** Pre-aggregate independent one-to-many child relationships in separate CTEs before joining to the parent dimension.""",
        "key_rules": """- When parent entities can exist without child records, always use LEFT JOIN instead of INNER JOIN
- Wrap nullable numerical expressions in COALESCE(val, 0) to avoid arithmetic evaluation to NULL
- Predicates filtering the right table of a LEFT JOIN must reside in the ON clause to preserve left-side cohort integrity
- Never join two independent one-to-many child tables directly without pre-aggregating in CTEs to prevent Cartesian fan-out
- Use COUNT(right_table.id) instead of COUNT(*) when counting occurrences in a LEFT JOIN""",
        "quick_reference": {
            "key_terms": [
                {"term": "INNER JOIN", "definition": "Returns records with matching keys in both tables ($A \\cap B$)."},
                {"term": "LEFT JOIN", "definition": "Returns all rows from left table, with matching right rows or NULLs."},
                {"term": "FULL OUTER JOIN", "definition": "Returns all rows from both tables, filling unmatched columns with NULL."},
                {"term": "COALESCE(val, fallback)", "definition": "Returns first non-null expression. Essential for null-safe arithmetic."},
                {"term": "Fan-Out", "definition": "Row duplication caused by $1:N$ relationship merging across multiple child tables."},
                {"term": "Anti-Join", "definition": "A LEFT JOIN filtered by `WHERE right.id IS NULL` to find unmatched records."}
            ],
            "formulas_rules": [
                "INNER: Records = Matches(A, B)",
                "LEFT: Records >= Count(A)",
                "COALESCE(NULL, 0) = 0",
                "Value + NULL = NULL (Always use COALESCE)",
                "WHERE right_col = val converts LEFT JOIN to INNER JOIN"
            ],
            "decision_rules": [
                "Need only users who completed a checkout? -> Use INNER JOIN",
                "Need all registered users, including those with 0 checkouts? -> Use LEFT JOIN",
                "Reconciling two independent financial ledgers for discrepancies? -> Use FULL OUTER JOIN",
                "Finding customers who have NEVER made a purchase? -> Use Anti-Join (LEFT JOIN + WHERE right.id IS NULL)",
                "Joining multiple child transaction tables? -> Pre-aggregate in CTEs first"
            ],
            "takeaways": [
                "Never let an accidental INNER JOIN silently drop inactive customer cohorts from your analysis.",
                "Always safeguard monetary arithmetic with COALESCE to prevent silent nullification.",
                "Keep right-table date and status filters in the ON clause when writing outer joins.",
                "Verify join cardinality: verify row counts before and after joining to catch fan-out early."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Core Intuition & Two-Table Join Mechanics",
                "prerequisite_recap": "Assumes understanding of basic SELECT and WHERE statements.",
                "explanation_supplement": "Focuses on the visual mental model: pairing matching puzzle pieces between two tables using Primary Key and Foreign Key columns.",
                "key_additions": [
                    "Venn diagram set models",
                    "Step-by-step row matching walkthrough",
                    "Clear distinction between INNER and LEFT joins"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "Multi-Table Merges, Null Safety & Aggregation Integrity",
                "prerequisite_recap": "Assumes familiarity with basic 2-table joins.",
                "explanation_supplement": "Explores real-world production challenges: handling multi-table merges, null propagation in financial metrics with COALESCE, and the ON vs WHERE filtering pitfall.",
                "key_additions": [
                    "COALESCE defensive programming",
                    "Three-table joins with orders and returns",
                    "ON vs WHERE outer join filtering mechanics"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Execution Plans, Hash Joins & Distributed Data Skew",
                "prerequisite_recap": "Assumes mastery of complex multi-table SQL and CTEs.",
                "explanation_supplement": "Covers database optimizer mechanics: Nested Loop Joins vs Hash Joins vs Sort-Merge Joins. Explains how query planners estimate cardinality, memory spills during large hash joins, and strategies for handling data skew in distributed engines like Snowflake, Presto, and BigQuery.",
                "key_additions": [
                    "Optimizer join algorithms (Hash Join, Merge Join, Nested Loop)",
                    "Handling massive key skew and memory spillover",
                    "Broadcast joins vs shuffle joins in distributed environments"
                ]
            }
        }
    },

    # =========================================================================
    # 2. SQL Fundamentals & Aggregations
    # =========================================================================
    "sql-fundamentals": {
        "title": "Relational Querying & Aggregation Fundamentals",
        "concept_name": "SQL Relational Filtering & Aggregations",
        "difficulty": "Beginner",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Master the strict logical SQL query processing order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY",
            "Filter base records using complex boolean predicates, pattern matching (LIKE), and NULL testing (IS NULL)",
            "Aggregate metrics using COUNT, SUM, AVG, MIN, and MAX grouped across multiple business dimensions",
            "Differentiate between row-level filtering with WHERE and group-level filtering with HAVING",
            "Avoid common SQL syntax pitfalls including referencing column aliases in the WHERE clause",
        ],
        "explanation": """### 1. The Logical Processing Order of SQL
To write high-performance, bug-free SQL queries, you must master the fundamental paradox of SQL: **SQL is written in one order, but executed in a completely different logical order by the database engine.**

While a query begins with the keyword `SELECT`, the engine executes clauses in the following strict order:

```
  1. FROM        -> Identifies tables, evaluates JOINs, and establishes base row sets
  2. WHERE       -> Filters individual rows BEFORE any aggregation
  3. GROUP BY    -> Collapses rows into distinct groups based on grouping attributes
  4. HAVING      -> Filters aggregated groups AFTER summary functions have run
  5. SELECT      -> Computes expressions, resolves column aliases, and projects outputs
  6. DISTINCT    -> Eliminates duplicate rows from the projected output
  7. ORDER BY    -> Sorts the resulting records for presentation
  8. LIMIT/OFFSET-> Restricts the number of output rows returned to the client
```

#### Why Does This Matter?
1. **Column Aliases in WHERE:** Because `WHERE` (step 2) runs **before** `SELECT` (step 5), you **cannot** reference a column alias defined in the `SELECT` list inside your `WHERE` clause!
   ```sql
   -- SYNTAX ERROR: Total_spend does not exist yet when WHERE is evaluated!
   SELECT customer_id, amount * quantity AS total_spend
   FROM order_items
   WHERE total_spend > 500;
   ```
2. **Aggregates in WHERE:** Because aggregation occurs in `GROUP BY` (step 3), aggregate functions like `COUNT()` or `SUM()` do not exist during `WHERE` evaluation. To filter on aggregate thresholds, you must use `HAVING` (step 4).

---

### 2. Filtering Predicates & Three-Valued Logic
In relational databases, missing or unknown values are represented by `NULL`. SQL implements **Three-Valued Logic (3VL)**: every logical comparison evaluates to `TRUE`, `FALSE`, or `UNKNOWN`.

* The comparison `discount = NULL` evaluates to `UNKNOWN`, which is treated as `FALSE` by `WHERE` filters.
* To check for missing values, always use `IS NULL` or `IS NOT NULL`.
* Use `BETWEEN low AND high` for inclusive range checks.
* Use `IN ('val1', 'val2')` as an efficient shorthand for multiple `OR` conditions.
* Use `LIKE 'prefix%'` for wildcard string matching (`%` matches zero or more characters, `_` matches exactly one character).

---

### 3. Aggregation Engine Mechanics
Aggregate functions summarize multiple rows into a single scalar value:
* **`COUNT(*)`**: Counts every row in the group, including rows with NULLs.
* **`COUNT(column_name)`**: Counts only rows where `column_name` is **not NULL**.
* **`SUM(column_name)`**: Computes the numerical sum of non-null values.
* **`AVG(column_name)`**: Computes the arithmetic mean: $\\frac{\\sum x_i}{N_{\\text{non-null}}}$.
* **`MIN() / MAX()`**: Computes the extreme values (works on numbers, dates, and alphabetic strings).

**Golden Rule of GROUP BY:** Every column in the `SELECT` list that is **not** wrapped in an aggregate function **must** be explicitly listed in the `GROUP BY` clause.""",
        "code_examples": [
            {
                "title": "Example 1: Proper Dimensional Grouping with HAVING Filter",
                "language": "sql",
                "code": """-- Group sales by region and category, filtering for high-performing groups
SELECT
    region,
    product_category,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(revenue), 2) AS total_revenue,
    ROUND(AVG(revenue), 2) AS average_order_value
FROM store_sales
WHERE order_status = 'DELIVERED'
  AND order_date >= '2024-01-01'
GROUP BY region, product_category
HAVING COUNT(order_id) >= 10
   AND SUM(revenue) > 50000.00
ORDER BY total_revenue DESC;""",
                "explanation": "WHERE filters base rows before grouping (filtering out cancelled orders and pre-2024 dates). GROUP BY groups the data by region and category. HAVING filters out small categories with fewer than 10 orders or under $50,000 revenue."
            },
            {
                "title": "Example 2: Conditional Aggregation with CASE WHEN",
                "language": "sql",
                "code": """-- Pivot transactional data into executive metrics using conditional aggregation
SELECT
    DATE_TRUNC('month', order_date) AS order_month,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount), 2) AS gross_sales,
    ROUND(SUM(CASE WHEN payment_method = 'CREDIT_CARD' THEN amount ELSE 0 END), 2) AS cc_sales,
    ROUND(SUM(CASE WHEN payment_method = 'PAYPAL' THEN amount ELSE 0 END), 2) AS paypal_sales,
    ROUND(100.0 * COUNT(CASE WHEN is_first_purchase = 1 THEN 1 END) / COUNT(*), 1) AS new_customer_pct
FROM orders
WHERE status != 'CANCELLED'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY order_month ASC;""",
                "explanation": "Demonstrates conditional aggregation using CASE WHEN inside SUM() and COUNT(). Allows computing multiple business metrics across different segments in a single table scan."
            }
        ],
        "worked_example": {
            "title": "Quarterly Sales Performance Analysis",
            "scenario": "A business intelligence team needs an automated report identifying product sub-categories with at least 5 completed orders and an Average Order Value (AOV) exceeding $150.00 during Q1 2024. The results must be grouped by sales region and product category, showing total sales volume and average spend.",
            "problem": "Formulate an optimal SQL query that aggregates orders by region and category, filters out incomplete orders and non-Q1 transactions at the row level, and filters category groups based on volume and AOV thresholds.",
            "approach": "1. Scan the `sales_orders` table.\n2. Filter base rows in WHERE for `order_status = 'COMPLETED'` and Q1 date boundaries.\n3. Group by `region` and `product_category`.\n4. Apply HAVING clause to enforce `COUNT(order_id) >= 5` and `AVG(order_amount) > 150.00`.\n5. Project region, category, order count, total revenue, and AOV, sorting by total revenue descending.",
            "code": """SELECT
    region,
    product_category,
    COUNT(order_id) AS total_orders,
    ROUND(SUM(order_amount), 2) AS total_revenue,
    ROUND(AVG(order_amount), 2) AS avg_order_value
FROM sales_orders
WHERE order_status = 'COMPLETED'
  AND order_date BETWEEN '2024-01-01' AND '2024-03-31'
GROUP BY region, product_category
HAVING COUNT(order_id) >= 5
   AND AVG(order_amount) > 150.00
ORDER BY total_revenue DESC;""",
            "expected_output": "| region | product_category | total_orders | total_revenue | avg_order_value |\n| :--- | :--- | :--- | :--- | :--- |\n| North America | Laptops & Workstations | 18 | $34,200.00 | $1,900.00 |\n| EMEA | Enterprise Servers | 8 | $28,000.00 | $3,500.00 |\n| APAC | Cloud Accessories | 12 | $2,400.00 | $200.00 |",
            "reasoning": "Placing status and date filters in WHERE discards unnecessary rows before grouping, reducing memory footprint. Placing order count and AOV filters in HAVING filters summary metrics after group aggregation.",
            "why_it_works": "The engine reads the base table, filters unneeded rows in WHERE, partitions matching rows into buckets defined by (region, product_category), computes aggregates per bucket, tests HAVING conditions, and outputs sorted results.",
            "alternative": """-- CTE Alternative: Separates grouping logic from group-filtering for enhanced readability
WITH category_metrics AS (
    SELECT
        region,
        product_category,
        COUNT(order_id) AS total_orders,
        ROUND(SUM(order_amount), 2) AS total_revenue,
        ROUND(AVG(order_amount), 2) AS avg_order_value
    FROM sales_orders
    WHERE order_status = 'COMPLETED'
      AND order_date BETWEEN '2024-01-01' AND '2024-03-31'
    GROUP BY region, product_category
)
SELECT *
FROM category_metrics
WHERE total_orders >= 5
  AND avg_order_value > 150.00
ORDER BY total_revenue DESC;"""
        },
        "common_mistakes": """### Mistake 1 — Putting Aggregates in the WHERE Clause
* **What it looks like:** `SELECT dept, AVG(salary) FROM employees WHERE AVG(salary) > 80000 GROUP BY dept;`
* **Why it happens:** The author thinks of filtering criteria simultaneously without considering query execution order.
* **How to fix it:** Move aggregate conditions into the `HAVING` clause: `HAVING AVG(salary) > 80000`.

### Mistake 2 — Omission of Non-Aggregated Columns from GROUP BY
* **What it looks like:** `SELECT dept, job_title, AVG(salary) FROM employees GROUP BY dept;`
* **Why it happens:** The user assumes the database will choose any job title from the department.
* **How to fix it:** Every non-aggregated column in `SELECT` must be explicitly listed in `GROUP BY`: `GROUP BY dept, job_title`.

### Mistake 3 — Using = NULL instead of IS NULL
* **What it looks like:** `SELECT * FROM orders WHERE ship_date = NULL;`
* **Why it happens:** Familiarity with programming languages like Python (`x == None`) or JavaScript.
* **How to fix it:** Always use `WHERE ship_date IS NULL` because NULL cannot equal anything in SQL.""",
        "key_rules": """- Query execution order: FROM -> WHERE -> GROUP BY -> HAVING -> SELECT -> ORDER BY
- Never place aggregate functions in the WHERE clause; use HAVING
- Non-aggregated columns in SELECT must be included in the GROUP BY clause
- Test missing values with IS NULL and IS NOT NULL, never with = NULL
- Column aliases created in SELECT cannot be referenced in WHERE or GROUP BY in standard SQL""",
        "quick_reference": {
            "key_terms": [
                {"term": "Predicate", "definition": "A logical condition evaluating to TRUE, FALSE, or UNKNOWN in a WHERE or HAVING clause."},
                {"term": "GROUP BY", "definition": "Collapses rows with identical values in specified columns into summary rows."},
                {"term": "HAVING", "definition": "Filters summary rows produced by GROUP BY based on aggregate criteria."},
                {"term": "COUNT(*)", "definition": "Counts all rows in a group including NULLs."},
                {"term": "COUNT(col)", "definition": "Counts only non-NULL entries in the specified column."}
            ],
            "formulas_rules": [
                "WHERE filters rows BEFORE aggregation",
                "HAVING filters groups AFTER aggregation",
                "AVG(col) = SUM(col) / COUNT(col)",
                "col = NULL -> UNKNOWN (Always use IS NULL)"
            ],
            "decision_rules": [
                "Filtering individual transactions before summarizing? -> Use WHERE",
                "Filtering categories with total sales exceeding a threshold? -> Use HAVING",
                "Counting all rows regardless of missing values? -> Use COUNT(*)",
                "Counting how many users provided a phone number? -> Use COUNT(phone_number)"
            ],
            "takeaways": [
                "Understanding SQL's logical execution order eliminates 90% of beginner syntax errors.",
                "Filter early in WHERE to reduce data volume before resource-intensive GROUP BY operations.",
                "Always check for NULLs when evaluating numeric averages and counts."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Query Structure, Filtering & Basic Aggregations",
                "prerequisite_recap": "Starts from fundamental table concepts and simple SELECT statements.",
                "explanation_supplement": "Explains how a relational table is scanned row-by-row, how WHERE filters rows out, and how summary cards are computed.",
                "key_additions": [
                    "Basic SELECT syntax and filtering",
                    "COUNT, SUM, AVG basic usage",
                    "IS NULL vs = NULL intuition"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "Multi-Dimensional Grouping, HAVING & Conditional Aggregations",
                "prerequisite_recap": "Assumes basic querying literacy; focuses on business metrics and grouping mechanics.",
                "explanation_supplement": "Covers grouping across multiple dimensional hierarchies, pivoting data with CASE WHEN, and avoiding alias scope errors.",
                "key_additions": [
                    "Multi-column GROUP BY hierarchies",
                    "Conditional aggregations using CASE WHEN",
                    "HAVING vs WHERE query optimization"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Execution Plans, Index Scans & GroupBy Optimization",
                "prerequisite_recap": "Assumes mastery of grouping and aggregation queries.",
                "explanation_supplement": "Explores how storage engines execute aggregations: Hash Aggregate vs Stream Aggregate (Sort Aggregate). Examines composite indexing strategies (`(status, order_date, region)`) to enable index-only scans and prevent expensive disk sorts.",
                "key_additions": [
                    "Hash Aggregate vs Stream Aggregate engine internals",
                    "Composite B-Tree index design for GROUP BY acceleration",
                    "Memory management and tempdb spills during large aggregations"
                ]
            }
        }
    },

    # =========================================================================
    # 3. Python Foundations & Core Data Structures
    # =========================================================================
    "python-core-fundamentals": {
        "title": "Python Foundations: Syntax, Variables & Control Flow",
        "concept_name": "Python Language Foundations & Data Structures",
        "difficulty": "Beginner",
        "estimated_minutes": 30,
        "learning_objectives": [
            "Master Python object model: object identity, reference assignment, and mutable vs immutable data types",
            "Manipulate fundamental Python data structures: lists, tuples, sets, and dictionaries with idiomatic methods",
            "Write robust control flow statements: if/elif/else conditions, for/while loops, enumerate, and zip",
            "Construct clean, reusable functions with positional arguments, keyword arguments, default parameters, and type annotations",
            "Apply list, set, and dictionary comprehensions for concise, memory-efficient data transformations",
        ],
        "explanation": """### 1. The Python Object Model: Everything is an Object
Python is a dynamically typed, garbage-collected language where **variables are not memory buckets holding values; variables are labels (pointers) bound to objects in memory.**

```
  x = [1, 2, 3]        x ────┐
  y = x                y ────┴──> [ Heap Object: list [1, 2, 3] ]
  y.append(4)          
  print(x)  # Prints [1, 2, 3, 4]! Both labels point to the same object!
```

#### Mutability vs Immutability
* **Immutable Types**: Cannot be modified after creation. Modifying an immutable type creates a brand-new object in memory.
  * Examples: `int`, `float`, `str`, `tuple`, `bool`, `frozenset`.
* **Mutable Types**: Can be modified in place without changing the object's identity (`id()`).
  * Examples: `list`, `dict`, `set`, custom class instances.

Understanding mutability is crucial when passing arguments to functions and creating copies. Use `copy.deepcopy()` when you need an independent clone of nested data structures.

---

### 2. Core Built-In Data Structures

| Structure | Syntax | Mutable? | Ordered? | Duplicates? | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`list`** | `[1, 2, 3]` | Yes | Yes (Indexed) | Yes | Sequential collections, queues, data processing |
| **`tuple`** | `(1, 2, 3)` | **No** | Yes (Indexed) | Yes | Immutable records, dictionary keys, function returns |
| **`set`** | `{1, 2, 3}` | Yes | No | **No** | Unique member lookup ($O(1)$), set unions & intersections |
| **`dict`** | `{'k': 'v'}` | Yes | Yes (Insertion) | Keys unique | Key-value mapping, database records, JSON payloads |

#### Set Operations for High Performance:
Checking membership (`item in collection`) in a `list` takes $O(N)$ linear time. Checking membership in a `set` or `dict` takes $O(1)$ constant time thanks to hashing! Always convert lookup arrays to sets when filtering large datasets.

---

### 3. Idiomatic Comprehensions
Comprehensions provide a clean, declarative syntax for transforming iterables without messy loop boilerplate:

```python
# List Comprehension
clean_emails = [email.strip().lower() for email in raw_emails if "@" in email]

# Dictionary Comprehension
price_map = {item["id"]: item["price"] for item in inventory if item["in_stock"]}

# Set Comprehension
unique_domains = {email.split("@")[1] for email in clean_emails}
```

---

### 4. Functions, Parameter Binding & Type Hints
Modern Python utilizes type hints (PEP 484) to communicate contracts clearly:
```python
def calculate_discount(price: float, rate: float = 0.10) -> float:
    \"\"\"Calculate discounted price given base price and rate.\"\"\"
    if not (0.0 <= rate <= 1.0):
        raise ValueError(f"Invalid discount rate: {rate}")
    return round(price * (1.0 - rate), 2)
```
**Danger Rule:** Never use a mutable object (like `[]` or `{}`) as a default argument in a function definition! Default arguments are evaluated once at module load time, meaning all function calls share the same mutable instance.""",
        "code_examples": [
            {
                "title": "Example 1: Safe Data Cleansing & Set Operations",
                "language": "python",
                "code": """# Process customer emails and filter unauthorized domains
raw_users = [
    {"id": 1, "email": " alice@company.com ", "role": "admin"},
    {"id": 2, "email": "bob@gmail.com", "role": "user"},
    {"id": 3, "email": "CHARLIE@COMPANY.COM", "role": "user"},
    {"id": 4, "email": "invalid_entry", "role": "user"},
]

allowed_domains = {"company.com", "partner.org"}

cleaned_users = []
for user in raw_users:
    clean_email = user["email"].strip().lower()
    if "@" in clean_email:
        domain = clean_email.split("@")[1]
        if domain in allowed_domains:
            cleaned_users.append({
                "id": user["id"],
                "email": clean_email,
                "role": user["role"],
                "domain": domain
            })

print(f"Verified internal accounts: {len(cleaned_users)}")
# Output: Verified internal accounts: 2 (alice and charlie)""",
                "explanation": "Demonstrates string normalization, domain validation using $O(1)$ set membership, and clean dictionary reconstruction."
            },
            {
                "title": "Example 2: Dictionary Aggregation & Frequency Counting",
                "language": "python",
                "code": """from collections import defaultdict

# Calculate total sales and transaction counts per product category
transactions = [
    {"category": "Hardware", "amount": 120.50},
    {"category": "Software", "amount": 49.99},
    {"category": "Hardware", "amount": 350.00},
    {"category": "Cloud", "amount": 80.00},
    {"category": "Software", "amount": 15.00},
]

category_summary = defaultdict(lambda: {"total_revenue": 0.0, "count": 0})

for tx in transactions:
    cat = tx["category"]
    category_summary[cat]["total_revenue"] += tx["amount"]
    category_summary[cat]["count"] += 1

for cat, metrics in category_summary.items():
    avg = metrics["total_revenue"] / metrics["count"]
    print(f"{cat:10} | Orders: {metrics['count']:2} | Total: ${metrics['total_revenue']:8.2f} | AOV: ${avg:6.2f}")""",
                "explanation": "Uses collections.defaultdict to eliminate manual key initialization checks, computing category aggregations in a single clean pass."
            }
        ],
        "worked_example": {
            "title": "E-Commerce Transaction Stream Pipeline",
            "scenario": "A payment gateway receives an unstructured stream of transaction dictionaries. The data engineering team needs a clean, defensive Python pipeline that parses the payload, validates amounts, discards duplicates, separates successful payments from refunds, and returns a verified financial summary dictionary.",
            "problem": "Write an efficient Python function that accepts a list of raw transaction dictionaries, validates required keys, deduplicates by transaction ID, separates credits from debits, and computes net sales.",
            "approach": "1. Initialize tracking sets for transaction ID deduplication.\n2. Iterate through records, validating that required fields ('id', 'amount', 'status') exist and are non-null.\n3. Categorize into successful charges and refunds.\n4. Calculate gross volume, refund deductions, and net settlement.\n5. Return a structured dictionary with metrics and clean records.",
            "code": """from typing import List, Dict, Any, Tuple

def process_transaction_stream(
    raw_stream: List[Dict[str, Any]]
) -> Dict[str, Any]:
    seen_ids = set()
    valid_charges: List[Dict[str, Any]] = []
    total_gross = 0.0
    total_refunds = 0.0
    corrupted_count = 0

    for item in raw_stream:
        # Validate schema integrity
        tx_id = item.get("id")
        amount = item.get("amount")
        status = item.get("status")

        if not tx_id or amount is None or status is None:
            corrupted_count += 1
            continue

        # Deduplication
        if tx_id in seen_ids:
            continue
        seen_ids.add(tx_id)

        # Business processing
        if status == "SUCCESS":
            total_gross += float(amount)
            valid_charges.append(item)
        elif status == "REFUND":
            total_refunds += float(amount)

    net_settlement = round(total_gross - total_refunds, 2)

    return {
        "unique_transactions_processed": len(seen_ids),
        "valid_completed_charges": len(valid_charges),
        "corrupted_records_dropped": corrupted_count,
        "gross_volume": round(total_gross, 2),
        "refund_volume": round(total_refunds, 2),
        "net_settlement": net_settlement,
    }""",
            "expected_output": """{
  "unique_transactions_processed": 4,
  "valid_completed_charges": 3,
  "corrupted_records_dropped": 1,
  "gross_volume": 425.50,
  "refund_volume": 45.00,
  "net_settlement": 380.50
}""",
            "reasoning": "The function uses a set `seen_ids` for $O(1)$ duplicate lookups. It defensively inspects each dictionary with `.get()` to avoid uncaught `KeyError` exceptions, and separates charges from refunds before calculating net totals.",
            "why_it_works": "Python's hash table architecture makes set lookup instant regardless of stream length. Floats are parsed and accumulated sequentially, and round() prevents binary floating-point representation artifacts.",
            "alternative": """# Object-Oriented Dataclass Alternative:
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Transaction:
    id: str
    amount: float
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> Optional['Transaction']:
        try:
            return cls(id=str(data['id']), amount=float(data['amount']), status=str(data['status']))
        except (KeyError, ValueError, TypeError):
            return None"""
        },
        "common_mistakes": """### Mistake 1 — Mutable Default Arguments
* **What it looks like:** `def append_item(item, target_list=[]): target_list.append(item); return target_list`
* **Why it happens:** The author assumes a new empty list is created every time the function is invoked.
* **How to fix it:** Use `None` as the default value: `def append_item(item, target_list=None): if target_list is None: target_list = []`.

### Mistake 2 — Modifying a List While Iterating Over It
* **What it looks like:** `for item in items: if item < 0: items.remove(item)`
* **Why it happens:** Modifying the list shifts the internal index pointers, causing subsequent items to be skipped.
* **How to fix it:** Use a list comprehension to create a clean filtered copy: `items = [x for x in items if x >= 0]`.

### Mistake 3 — Shallow vs Deep Copying
* **What it looks like:** `nested_copy = original_list.copy()` where elements are dictionaries or sub-lists.
* **Why it happens:** `.copy()` creates a new outer list, but the inner dictionaries still reference the original memory addresses!
* **How to fix it:** Use `import copy; deep = copy.deepcopy(original)` when duplicating nested data structures.""",
        "key_rules": """- Variables are pointers to objects in memory; assignment does not copy mutable values
- Never use mutable default values (like [] or {}) in function signatures; use None
- Use sets for O(1) membership lookups instead of scanning lists with O(N) operations
- Avoid modifying collections while actively iterating over them; use comprehensions
- Always use type annotations to make function contracts clear and verifiable""",
        "quick_reference": {
            "key_terms": [
                {"term": "Mutability", "definition": "Ability of an object to change its state in place (e.g. lists, dicts)."},
                {"term": "Immutability", "definition": "Inability of an object to be altered once instantiated (e.g. tuples, strings)."},
                {"term": "Set", "definition": "Unordered collection of unique hashable elements with $O(1)$ membership checks."},
                {"term": "Dictionary", "definition": "Key-value mapping providing fast lookups based on hashed keys."},
                {"term": "Comprehension", "definition": "Compact syntactic construct for mapping and filtering iterables into new collections."}
            ],
            "formulas_rules": [
                "List membership: O(N) linear time",
                "Set / Dict membership: O(1) constant time",
                "y = x creates a reference, not a copy",
                "Default arguments evaluate once at definition time"
            ],
            "decision_rules": [
                "Need an ordered list of items that changes dynamically? -> Use list",
                "Need to guarantee records cannot be accidentally modified? -> Use tuple",
                "Need to remove duplicates and test membership instantly? -> Use set",
                "Associating attributes or values with unique IDs? -> Use dict"
            ],
            "takeaways": [
                "Mastering object identity and mutability prevents subtle bugs across data processing pipelines.",
                "Leverage sets and comprehensions for clean, idiomatic, and high-performance Python code.",
                "Write defensive functions with clear type hints, explicit defaults, and structured error handling."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Syntax, Variables, Basic Collections & Functions",
                "prerequisite_recap": "Starts from zero programming experience; introduces how Python executes scripts.",
                "explanation_supplement": "Covers variable naming, fundamental arithmetic, string formatting with f-strings, and basic for loops.",
                "key_additions": [
                    "Basic variable assignment and types",
                    "List appending and indexing",
                    "Simple if/else conditions"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "Comprehensions, Mutability, Dictionaries & Set Operations",
                "prerequisite_recap": "Assumes basic syntax literacy; focuses on data processing patterns.",
                "explanation_supplement": "Explores reference passing, deep vs shallow copying, dictionary transformations, and defensive data cleaning.",
                "key_additions": [
                    "List and dict comprehensions",
                    "Collections module (defaultdict, Counter)",
                    "Defensive function design with type hints"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Memory Management, Generators & CPython Internals",
                "prerequisite_recap": "Assumes fluent everyday Python development.",
                "explanation_supplement": "Covers CPython object layout (PyObject header, reference counting, cyclic garbage collection), memory efficiency with generators (`yield`), and `__slots__` optimization for massive object allocations.",
                "key_additions": [
                    "CPython reference counting and cyclic GC mechanics",
                    "Generator pipelines for streaming memory efficiency",
                    "__slots__ memory optimization for high-throughput classes"
                ]
            }
        }
    },

    # =========================================================================
    # 4. Python Data Manipulation with Pandas
    # =========================================================================
    "python-pandas-pipelines": {
        "title": "Python Data Manipulation with Pandas & Vectorization",
        "concept_name": "Pandas DataFrames, Vectorization & Pipeline Architecture",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Differentiate between 1D Series and 2D DataFrame architectures and their underlying NumPy memory layouts",
            "Leverage vectorized operations and broadcasting to achieve 100x speedups over iterative Python loops",
            "Perform precision indexing and slicing using `.loc` (label-based) vs `.iloc` (positional integer-based)",
            "Execute multi-dimensional aggregations, groupings, and window transformations with `.groupby()` and `.agg()`",
            "Diagnose and resolve the infamous `SettingWithCopyWarning` using explicit `.copy()` calls",
            "Handle real-world missing data, duplicates, and data type coercions defensively across analytics pipelines",
        ],
        "explanation": """### 1. The Core Architecture: Series vs DataFrames
Pandas is built on top of NumPy, meaning data is stored in contiguous C-style memory blocks. 
* **`Series`**: A one-dimensional labeled array capable of holding any data type. It consists of an **Index** and the underlying **NumPy data buffer**.
* **`DataFrame`**: A two-dimensional tabular data structure with labeled axes (rows and columns). Each column in a DataFrame is an individual `Series` sharing a common row `Index`.

```
        Columns (Axis 1) ───>
           'customer_id'    'amount'      'status'
Index 0         101           45.50      COMPLETED
 (Axis 0)       102          120.00      REFUNDED
           103           89.99      COMPLETED
```

---

### 2. The Golden Rule of Pandas: Vectorization over Iteration
Never use `for` loops or `df.iterrows()` to perform calculations on DataFrames! 
* Python loops execute dynamically in the CPython interpreter, checking types on every single iteration ($O(N)$ high overhead).
* **Vectorized operations** offload computations directly to pre-compiled C/Fortran SIMD vector instructions in NumPy, achieving **100x to 1,000x execution speedups**.

```python
# SLOW (Anti-Pattern): Iterating over 1,000,000 rows takes ~15 seconds
for idx, row in df.iterrows():
    df.at[idx, 'tax'] = row['amount'] * 0.08

# FAST (Idiomatic Vectorization): Takes ~0.005 seconds (3,000x faster!)
df['tax'] = df['amount'] * 0.08
```

---

### 3. Precision Indexing: `.loc` vs `.iloc`
* **`.loc[row_labels, col_labels]`**: Strictly **label-based** indexing.
* **`.iloc[row_indices, col_indices]`**: Strictly **integer position-based** indexing ($0, 1, ..., N-1$).

```python
# Filter rows where amount > 100, selecting specific named columns
high_value = df.loc[df['amount'] > 100, ['customer_id', 'amount', 'status']]

# Grab the first 5 rows and the first 3 columns by integer position
top_slice = df.iloc[0:5, 0:3]
```

---

### 4. Resolving `SettingWithCopyWarning`
The dreaded `SettingWithCopyWarning` occurs when you attempt chained indexing:
```python
# DANGEROUS: Chained indexing returns a temporary copy or view!
df[df['status'] == 'ACTIVE']['discount'] = 0.10  # Warning triggered!
```
**Why this happens:** Pandas cannot guarantee whether the sliced subset is a view (modifying the original memory) or a copy (modifications will be lost).
**The Clean Fix:** Always use `.loc` directly on the source DataFrame, or create an explicit copy:
```python
# Safe Option A: Explicit .loc
df.loc[df['status'] == 'ACTIVE', 'discount'] = 0.10

# Safe Option B: Explicit .copy() when creating a standalone subset
active_users = df.loc[df['status'] == 'ACTIVE'].copy()
active_users['discount'] = 0.10
```""",
        "code_examples": [
            {
                "title": "Example 1: GroupBy Multi-Aggregation & KPI Extraction",
                "language": "python",
                "code": """import pandas as pd
import numpy as np

# Sample transactional DataFrame
data = {
    'store_id': [1, 1, 2, 2, 3, 3, 3],
    'category': ['Electronics', 'Grocery', 'Electronics', 'Electronics', 'Grocery', 'Grocery', 'Electronics'],
    'revenue': [1200.0, 45.0, 850.0, 920.0, 60.0, 85.0, 1400.0],
    'units_sold': [2, 5, 1, 3, 6, 8, 2]
}
df = pd.DataFrame(data)

# Compute multi-metric summary per store and category
store_summary = (
    df.groupby(['store_id', 'category'])
    .agg(
        total_revenue=('revenue', 'sum'),
        avg_revenue=('revenue', 'mean'),
        total_units=('units_sold', 'sum'),
        transaction_count=('revenue', 'count')
    )
    .reset_index()
)

print(store_summary)""",
                "explanation": "Uses named aggregation inside .agg() to calculate sums, averages, and counts in a single pass while outputting clean, descriptive column headers."
            },
            {
                "title": "Example 2: Method Chaining Pipeline for Data Cleansing",
                "language": "python",
                "code": """import pandas as pd

def clean_sales_pipeline(raw_df: pd.DataFrame) -> pd.DataFrame:
    return (
        raw_df
        .dropna(subset=['customer_id', 'amount'])
        .drop_duplicates(subset=['transaction_id'])
        .assign(
            clean_date=lambda d: pd.to_datetime(d['order_date'], errors='coerce'),
            amount_usd=lambda d: pd.to_numeric(d['amount'], errors='coerce'),
            is_high_value=lambda d: d['amount_usd'] >= 1000.0
        )
        .dropna(subset=['clean_date', 'amount_usd'])
        .query("status == 'COMPLETED'")
        .sort_values(by='amount_usd', ascending=False)
        .reset_index(drop=True)
    )""",
                "explanation": "Demonstrates pandas method chaining. Each transformation returns a new DataFrame, producing readable, reproducible, functional data pipelines without creating dozens of intermediate variables."
            }
        ],
        "worked_example": {
            "title": "Customer Lifetime Value & Churn Prediction Pipeline",
            "scenario": "A financial analytics department has raw monthly subscription data. The lead analyst must build an end-to-end pipeline that takes messy transaction records, handles missing billing dates, flags accounts that have lapsed for more than 90 days, and produces a customer-level RFM (Recency, Frequency, Monetary) summary table.",
            "problem": "Transform raw e-commerce transaction logs into a clean, customer-level summary containing total lifetime spend, total order count, and days since last purchase, with zero SettingWithCopy warnings.",
            "approach": "1. Ingest raw dictionary records into a DataFrame.\n2. Convert date strings to datetime objects using pd.to_datetime(errors='coerce').\n3. Discard records with missing customer IDs or zero amounts.\n4. Group by customer_id and aggregate max date, order count, and total spend.\n5. Compute recency in days relative to a snapshot reference date.",
            "code": """import pandas as pd
import numpy as np

def compute_customer_rfm(raw_orders: pd.DataFrame, snapshot_date: str = '2024-04-01') -> pd.DataFrame:
    ref_date = pd.to_datetime(snapshot_date)

    # 1. Defensive cleaning
    df_clean = (
        raw_orders
        .dropna(subset=['customer_id', 'amount'])
        .assign(
            order_dt=lambda d: pd.to_datetime(d['order_date'], errors='coerce'),
            amount=lambda d: pd.to_numeric(d['amount'], errors='coerce')
        )
        .dropna(subset=['order_dt', 'amount'])
        .query("status == 'COMPLETED' and amount > 0")
        .copy()
    )

    # 2. RFM Aggregation
    rfm = (
        df_clean
        .groupby('customer_id')
        .agg(
            last_order_date=('order_dt', 'max'),
            frequency=('order_dt', 'count'),
            monetary_value=('amount', 'sum')
        )
        .reset_index()
    )

    # 3. Vectorized recency calculation
    rfm['recency_days'] = (ref_date - rfm['last_order_date']).dt.days
    rfm['monetary_value'] = rfm['monetary_value'].round(2)
    rfm['aov'] = (rfm['monetary_value'] / rfm['frequency']).round(2)

    return rfm.sort_values(by='monetary_value', ascending=False).reset_index(drop=True)""",
            "expected_output": """| customer_id | last_order_date | frequency | monetary_value | recency_days | aov |\n| :--- | :--- | :--- | :--- | :--- | :--- |\n| 1045 | 2024-03-28 | 8 | $3,450.00 | 4 | $431.25 |\n| 1088 | 2024-03-15 | 3 | $1,200.00 | 17 | $400.00 |\n| 1012 | 2024-01-05 | 1 | $150.00 | 87 | $150.00 |""",
            "reasoning": "Using `.assign()` with lambdas keeps operations functional and vectorized. `.dt.days` converts timedelta objects to integer day counts instantly across millions of rows without Python loops.",
            "why_it_works": "Pandas coordinates underlying NumPy arrays. Date parsing creates contiguous int64 nanosecond timestamps, enabling subtraction in single vectorized CPU instructions.",
            "alternative": """# Pivot Table Alternative for multi-dimensional cross-tabulation:
pivot_summary = df_clean.pivot_table(
    index='customer_id',
    columns='category',
    values='amount',
    aggfunc='sum',
    fill_value=0.0
)"""
        },
        "common_mistakes": """### Mistake 1 — Iterating with for loop or iterrows()
* **What it looks like:** `for i, r in df.iterrows(): df.loc[i, 'tax'] = r['amt'] * 0.08`
* **Why it happens:** Programmers familiar with standard imperative programming default to loops.
* **How to fix it:** Always use vectorized series arithmetic: `df['tax'] = df['amt'] * 0.08`.

### Mistake 2 — SettingWithCopyWarning via Chained Indexing
* **What it looks like:** `df[df['tier'] == 'Gold']['discount'] = 0.20`
* **Why it happens:** Chained brackets create an intermediate object whose memory ownership is ambiguous.
* **How to fix it:** Use single `.loc` indexing: `df.loc[df['tier'] == 'Gold', 'discount'] = 0.20`.

### Mistake 3 — Using .apply() When Vectorized Operations Exist
* **What it looks like:** `df['full_name'] = df.apply(lambda r: r['first'] + ' ' + r['last'], axis=1)`
* **Why it happens:** Believing `.apply()` is vectorized because it is a pandas method (it is just a hidden loop!).
* **How to fix it:** Use native vectorized string operations: `df['full_name'] = df['first'] + ' ' + df['last']`.""",
        "key_rules": """- Never iterate over DataFrames with Python loops; always vectorize
- Use .loc for label-based slicing and .iloc for positional integer slicing
- Always avoid chained indexing df[][] to eliminate SettingWithCopyWarning
- Use method chaining with .assign(), .query(), and .pipe() for clean pipelines
- Convert strings to datetime with pd.to_datetime(errors='coerce') to catch bad dates safely""",
        "quick_reference": {
            "key_terms": [
                {"term": "Series", "definition": "1D labeled array wrapping a contiguous NumPy buffer."},
                {"term": "DataFrame", "definition": "2D tabular data structure with heterogeneous typed column Series."},
                {"term": "Vectorization", "definition": "Executing operations across entire arrays via pre-compiled C routines without Python loops."},
                {"term": ".loc", "definition": "Label-based row and column indexer."},
                {"term": ".iloc", "definition": "Positional integer-based row and column indexer."}
            ],
            "formulas_rules": [
                "Loop speed: O(N) in Python bytecode (Slow)",
                "Vectorized speed: Compiled SIMD CPU instructions (100x Fast)",
                "df.loc[row_condition, 'col_name'] = val (Safe assignment)",
                "df.isna().sum() reveals column-wise missing value counts"
            ],
            "decision_rules": [
                "Accessing columns by name or boolean condition? -> Use .loc",
                "Accessing rows by integer index position (e.g. first 10 rows)? -> Use .iloc",
                "Grouping data and applying multiple metric summaries? -> Use .groupby().agg()",
                "Handling messy date formats with corrupted entries? -> Use pd.to_datetime(errors='coerce')"
            ],
            "takeaways": [
                "Embrace vectorization: if you find yourself writing a for loop in pandas, a vectorized alternative almost certainly exists.",
                "Structure data transformations as readable method chains.",
                "Inspect memory usage and data types regularly using `df.info()`."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "DataFrame Basics, Slicing & Simple Filtering",
                "prerequisite_recap": "Assumes basic Python variables and lists.",
                "explanation_supplement": "Covers creating DataFrames from dictionaries, viewing heads/tails, selecting columns, and basic boolean filtering.",
                "key_additions": [
                    "Creating DataFrames from dicts and CSVs",
                    "Selecting single and multiple columns",
                    "Simple boolean masks (df[df['age'] > 30])"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "Vectorization, GroupBy, Method Chaining & SettingWithCopy",
                "prerequisite_recap": "Assumes basic pandas querying knowledge.",
                "explanation_supplement": "Deep dives into .loc vs .iloc, multi-aggregation pipelines, resolving copy warnings, and joining DataFrames with pd.merge().",
                "key_additions": [
                    "Named aggregations in .groupby().agg()",
                    "SettingWithCopyWarning root cause and resolution",
                    "Pandas method chaining pipeline patterns"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Memory Optimization, PyArrow Backends & Performance Tuning",
                "prerequisite_recap": "Assumes fluent data engineering in pandas.",
                "explanation_supplement": "Explores the PyArrow backend introduced in Pandas 2.0, categorical downcasting (`category` dtypes) to reduce RAM by 80%, out-of-core computing with Dask/Polars, and custom Cython/Numba kernels for non-vectorizable operations.",
                "key_additions": [
                    "Pandas 2.0 PyArrow strings and nullable dtypes",
                    "Categorical encoding memory optimization",
                    "Numba JIT compilation for custom rolling window functions"
                ]
            }
        }
    },

    # =========================================================================
    # 5. Applied Statistical Analysis & Hypothesis Testing
    # =========================================================================
    "statistics-hypothesis-testing": {
        "title": "Applied Statistical Analysis & Hypothesis Testing",
        "concept_name": "Hypothesis Testing, P-Values & Statistical Significance",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Formulate statistical hypotheses: Null Hypothesis ($H_0$) vs Alternative Hypothesis ($H_1$)",
            "Interpret p-values rigorously without falling into common business fallacies or p-hacking",
            "Calculate test statistics: Z-scores and Student's t-statistics for single-sample and two-sample testing",
            "Evaluate Type I errors (False Positives, $\\alpha$) vs Type II errors (False Negatives, $\\beta$) and statistical power",
            "Construct and interpret Confidence Intervals at designated confidence levels ($1 - \\alpha$)",
            "Differentiate statistical significance from business practical effect size (Cohen's d)",
        ],
        "explanation": """### 1. The Core Scientific Framework: $H_0$ vs $H_1$
In business experimentation and data science, hypothesis testing provides a mathematical mechanism to determine whether an observed effect is **real** or merely an artifact of **random sampling variation**.

* **Null Hypothesis ($H_0$)**: The default skepticism benchmark—assumes **no true effect**, no difference between cohorts, or that an observed discrepancy arose purely by random chance.
  $$H_0: \\mu_{\\text{treatment}} = \\mu_{\\text{control}}$$
* **Alternative Hypothesis ($H_1$ or $H_a$)**: The claim we wish to establish—assumes a real, systematic difference exists.
  $$H_1: \\mu_{\\text{treatment}} \\neq \\mu_{\\text{control}} \\quad \\text{(Two-tailed)}$$

---

### 2. The Test Statistic & The Student's t-Distribution
When comparing sample means where population standard deviation is unknown, we calculate the **t-statistic**:

$$t = \\frac{\\bar{x}_1 - \\bar{x}_2}{s_p \\sqrt{\\frac{1}{n_1} + \\frac{1}{n_2}}}$$

Where:
* $\\bar{x}_1, \\bar{x}_2$ are the sample means of the cohorts.
* $s_p$ is the pooled sample standard deviation:
  $$s_p = \\sqrt{\\frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}}$$
* $n_1, n_2$ are the respective sample sizes.

The t-statistic measures: *"How many standard errors apart are our observed sample means?"*

---

### 3. Rigorous Interpretation of P-Values
**What a p-value IS:**
The probability of observing a test statistic as extreme as (or more extreme than) what was observed, **assuming the Null Hypothesis is strictly true**:
$$p = P(\\text{Data as extreme as observed} \\mid H_0 \\text{ is true})$$

**What a p-value is NOT:**
* It is **NOT** the probability that the Null Hypothesis is true ($P(H_0 \\mid \\text{Data})$).
* It is **NOT** the probability that the experimental feature was a success.
* A tiny p-value does **NOT** mean the effect is large or profitable—only that it is unlikely to be zero.

#### Significance Threshold ($\\alpha$):
By convention, researchers set $\\alpha = 0.05$ (5%). If $p < \\alpha$, we **reject the Null Hypothesis** and declare the result statistically significant.

---

### 4. Decision Matrix: Type I vs Type II Errors

| Reality \\ Decision | Fail to Reject $H_0$ | Reject $H_0$ (Declare Significance) |
| :--- | :--- | :--- |
| **$H_0$ is True** (No real effect) | **Correct Decision** ($1 - \\alpha$) | **Type I Error** (False Positive, rate = $\\alpha$) |
| **$H_0$ is False** (Real effect exists) | **Type II Error** (False Negative, rate = $\\beta$) | **Statistical Power** ($1 - \\beta$) |

* **Type I Error ($\\alpha$)**: Launching a website redesign thinking it increased conversion when in reality it had no effect.
* **Type II Error ($\\beta$)**: Killing a promising feature because your sample size was too small to detect the lift.
* **Statistical Power ($1 - \\beta$)**: The probability that a test will correctly reject a false null hypothesis. Minimum industry benchmark is 80% ($0.80$).

---

### 5. Confidence Intervals & Effect Size
A p-value tells you *whether* there is a difference, but a **Confidence Interval** tells you *how large the difference is and the precision of your estimate*:

$$\\text{CI}_{95\\%} = (\\bar{x}_1 - \\bar{x}_2) \\pm t_{\\alpha/2, \\text{df}} \\cdot \\text{SE}$$

If a 95% Confidence Interval for revenue lift spans $[+\\$0.02, +\\$0.05]$, the result is statistically significant ($p < 0.05$), but the business effect size is so tiny that engineering costs to maintain the feature may not be justified!""",
        "code_examples": [
            {
                "title": "Example 1: Independent Two-Sample T-Test with SciPy",
                "language": "python",
                "code": """import numpy as np
from scipy import stats

# A/B Test Experiment: Conversion revenue per user
# Group A (Control): Standard checkout flow
# Group B (Variant): Streamlined one-click checkout
np.random.seed(42)
control_rev = np.random.normal(loc=50.0, scale=12.0, size=500)
variant_rev = np.random.normal(loc=52.8, scale=12.5, size=500)

# Perform two-sample Welch's t-test (does not assume equal variance)
t_stat, p_val = stats.ttest_ind(variant_rev, control_rev, equal_var=False)

mean_ctrl = np.mean(control_rev)
mean_var = np.mean(variant_rev)
lift = mean_var - mean_ctrl
pct_lift = (lift / mean_ctrl) * 100.0

print(f"Control Mean: ${mean_ctrl:.2f} | Variant Mean: ${mean_var:.2f}")
print(f"Absolute Lift: +${lift:.2f} ({pct_lift:.1f}%)")
print(f"Welch's t-statistic: {t_stat:.4f} | p-value: {p_val:.4e}")

alpha = 0.05
if p_val < alpha:
    print("Decision: REJECT H0 - The conversion lift is statistically significant.")
else:
    print("Decision: FAIL TO REJECT H0 - Insufficient evidence to rule out random chance.")""",
                "explanation": "Executes Welch's t-test using scipy.stats. Computes practical lift percentage and evaluates p-value against the alpha=0.05 decision threshold."
            },
            {
                "title": "Example 2: 95% Confidence Interval Calculation",
                "language": "python",
                "code": """import numpy as np
from scipy import stats

def compute_diff_ci(sample1, sample2, confidence=0.95):
    n1, n2 = len(sample1), len(sample2)
    m1, m2 = np.mean(sample1), np.mean(sample2)
    s1, s2 = np.var(sample1, ddof=1), np.var(sample2, ddof=1)
    
    diff = m1 - m2
    se = np.sqrt(s1/n1 + s2/n2)
    
    # Welch-Satterthwaite degrees of freedom
    df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2 / (n1 - 1) + (s2/n2)**2 / (n2 - 1))
    
    t_crit = stats.t.ppf((1 + confidence) / 2, df)
    margin = t_crit * se
    
    return diff, (diff - margin, diff + margin)

diff, (ci_low, ci_high) = compute_diff_ci(variant_rev, control_rev)
print(f"Observed Difference: +${diff:.2f}")
print(f"95% Confidence Interval: [${ci_low:.2f}, ${ci_high:.2f}]")""",
                "explanation": "Calculates the exact 95% confidence interval for the difference between means. Since the interval does not cross $0.00, we confirm significance at 95% confidence."
            }
        ],
        "worked_example": {
            "title": "A/B Testing Checkout Conversion Lift",
            "scenario": "A digital commerce retailer tests a new checkout UX. The control group had 2,400 visitors with an average order value of $84.50 (std = $22.00). The treatment group had 2,500 visitors with an average order value of $87.10 (std = $24.00). The VP of Product wants to know if this $2.60 lift is real before authorizing an expensive global rollout.",
            "problem": "Evaluate whether the treatment checkout flow produced a statistically significant increase in AOV at alpha = 0.05, calculating the t-statistic, p-value, and 95% confidence interval.",
            "approach": "1. Formulate hypotheses: H0: mu_treatment - mu_control = 0 vs H1: mu_treatment - mu_control != 0.\n2. Compute standard error of the difference: SE = sqrt(s1^2/n1 + s2^2/n2).\n3. Compute test statistic: t = (x1 - x2) / SE.\n4. Determine degrees of freedom and p-value.\n5. Compare p-value to alpha = 0.05 and calculate confidence interval.",
            "code": """import numpy as np
from scipy import stats

# Experiment summary statistics
n_ctrl, mean_ctrl, s_ctrl = 2400, 84.50, 22.00
n_treat, mean_treat, s_treat = 2500, 87.10, 24.00

# 1. Standard Error
se_diff = np.sqrt((s_ctrl**2 / n_ctrl) + (s_treat**2 / n_treat))

# 2. t-statistic
diff = mean_treat - mean_ctrl
t_stat = diff / se_diff

# 3. Welch-Satterthwaite degrees of freedom
df = ((s_ctrl**2/n_ctrl + s_treat**2/n_treat)**2 / 
      ((s_ctrl**2/n_ctrl)**2/(n_ctrl - 1) + (s_treat**2/n_treat)**2/(n_treat - 1)))

# 4. Two-tailed p-value
p_val = 2 * (1 - stats.t.cdf(abs(t_stat), df))

# 5. 95% CI
t_crit = stats.t.ppf(0.975, df)
ci_low = diff - t_crit * se_diff
ci_high = diff + t_crit * se_diff

print(f"Observed Lift: +${diff:.2f}")
print(f"t-statistic: {t_stat:.4f} | df: {df:.1f} | p-value: {p_val:.4e}")
print(f"95% Confidence Interval for Lift: [${ci_low:.2f}, ${ci_high:.2f}]")""",
            "expected_output": """Observed Lift: +$2.60
t-statistic: 3.9482 | df: 4887.4 | p-value: 8.0051e-05
95% Confidence Interval for Lift: [+$1.31, +$3.89]""",
            "reasoning": "The t-statistic is 3.95, which is well past the standard critical threshold of 1.96. The p-value of 0.00008 is far below alpha=0.05. Furthermore, the 95% confidence interval spans [$1.31, $3.89], proving that even in the conservative scenario, the lift is at least $1.31 per order.",
            "why_it_works": "The central limit theorem ensures that with sample sizes over 2,000, the sampling distribution of the difference in means is normally distributed, making the t-test highly robust even if underlying individual transactions are slightly skewed.",
            "alternative": """# Non-parametric Bootstrap Alternative (Useful when distributions are heavily multimodal or skewed):
def bootstrap_diff_ci(sample_a, sample_b, n_iter=10000):
    diffs = []
    for _ in range(n_iter):
        boot_a = np.random.choice(sample_a, size=len(sample_a), replace=True)
        boot_b = np.random.choice(sample_b, size=len(sample_b), replace=True)
        diffs.append(np.mean(boot_b) - np.mean(boot_a))
    return np.percentile(diffs, [2.5, 97.5])"""
        },
        "common_mistakes": """### Mistake 1 — The P-Value Inversion Fallacy
* **What it looks like:** Stating: *"Since p = 0.03, there is a 97% probability that the new feature is better!"*
* **Why it happens:** Confusing $P(\\text{Data} \\mid H_0)$ with $P(H_1 \\mid \\text{Data})$.
* **How to fix it:** The p-value only quantifies how surprising the data is under the assumption of NO effect. It does not provide the probability that a hypothesis is true.

### Mistake 2 — Peeking and P-Hacking
* **What it looks like:** Checking the A/B test dashboard every morning and stopping the test the exact moment $p < 0.05$.
* **Why it happens:** Wanting quick business results.
* **How to fix it:** Repeatedly testing accumulating data inflates the False Positive rate from 5% to over 30%! Calculate required sample size in advance and only evaluate once the fixed horizon is reached.

### Mistake 3 — Confusing Statistical Significance with Business Impact
* **What it looks like:** Rolling out a multi-million-dollar machine learning system because $p < 0.001$, even though the lift was only 0.001%.
* **Why it happens:** With massive sample sizes (e.g. $N = 10,000,000$), microscopic differences become statistically significant.
* **How to fix it:** Always examine effect size and confidence intervals alongside p-values.""",
        "key_rules": """- H0 represents the null benchmark of no effect; H1 represents the claim of a systematic difference
- A p-value is the probability of observing data this extreme assuming H0 is true; it is NOT P(H0 is true)
- Set sample sizes and statistical power (1 - beta >= 0.80) before launching experiments to avoid p-hacking
- Never declare success solely on p < 0.05 without inspecting the Confidence Interval and business effect size
- Use Welch's t-test (equal_var=False) by default when sample sizes or group variances differ""",
        "quick_reference": {
            "key_terms": [
                {"term": "Null Hypothesis ($H_0$)", "definition": "Baseline assumption that no true relationship, difference, or effect exists."},
                {"term": "P-Value", "definition": "Probability of observing results at least as extreme as the sample data, assuming $H_0$ is true."},
                {"term": "Type I Error ($\\alpha$)", "definition": "Rejecting a true Null Hypothesis (False Positive). Standard threshold is 0.05."},
                {"term": "Type II Error ($\\beta$)", "definition": "Failing to reject a false Null Hypothesis (False Negative). Standard target is 0.20."},
                {"term": "Statistical Power ($1 - \\beta$)", "definition": "The probability of detecting a real effect when one exists (Standard target is 80%)."}
            ],
            "formulas_rules": [
                "t = (mean1 - mean2) / SE_diff",
                "SE_diff = sqrt(s1^2/n1 + s2^2/n2)",
                "Reject H0 if p-value < alpha (0.05)",
                "Confidence Interval = Diff +/- t_crit * SE_diff"
            ],
            "decision_rules": [
                "Comparing means of two independent groups? -> Use Two-Sample Welch's T-Test",
                "Comparing the same individuals before and after a treatment? -> Use Paired Samples T-Test",
                "Comparing proportions (e.g. click-through rates)? -> Use Two-Sample Z-Test for Proportions",
                "Data severely skewed with extreme outliers? -> Use Non-parametric Mann-Whitney U test or Bootstrapping"
            ],
            "takeaways": [
                "Hypothesis testing prevents companies from making decisions based on random noise.",
                "Never stop tests early merely because significance was temporarily reached.",
                "Always couple statistical significance with business ROI and practical effect size."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Core Intuition, Coin Flip Analogy & P-Value Meaning",
                "prerequisite_recap": "Starts from mean, median, and normal distribution concepts.",
                "explanation_supplement": "Uses the intuitive courtroom trial analogy: the defendant is presumed innocent (H0) until guilt is proven beyond a reasonable doubt (alpha threshold).",
                "key_additions": [
                    "The courtroom analogy of hypothesis testing",
                    "What a p-value represents in everyday terms",
                    "Simple A/B test conversion comparison"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "T-Tests, Two-Tailed Tests, Confidence Intervals & Power",
                "prerequisite_recap": "Assumes understanding of variance and sampling distributions.",
                "explanation_supplement": "Walks through standard error formulas, Welch's t-test implementation in Python, and evaluating Type I vs Type II errors.",
                "key_additions": [
                    "Welch's t-test calculation and degrees of freedom",
                    "Type I vs Type II error trade-offs in product decisions",
                    "95% Confidence Interval derivation"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Sequential Testing, False Discovery Rate (FDR) & Variance Reduction",
                "prerequisite_recap": "Assumes complete familiarity with standard frequentist testing.",
                "explanation_supplement": "Explores enterprise experimentation challenges: multiple testing corrections (Benjamini-Hochberg FDR, Bonferroni), sequential testing protocols (mSPRT) to allow early stopping safely, and CUPED variance reduction using pre-experiment covariates to reduce required sample sizes by 50%.",
                "key_additions": [
                    "Multiple comparison adjustments (Bonferroni, Benjamini-Hochberg)",
                    "CUPED variance reduction using pre-experiment covariates",
                    "Sequential testing and Alpha spending functions"
                ]
            }
        }
    }
}

# Merge modular content parts
try:
    from app.seed.comprehensive_learning_content_part2 import COMPREHENSIVE_MODULE_ENHANCEMENTS_PART2
    COMPREHENSIVE_MODULE_ENHANCEMENTS.update(COMPREHENSIVE_MODULE_ENHANCEMENTS_PART2)
except ImportError:
    pass

try:
    from app.seed.comprehensive_learning_content_part3 import COMPREHENSIVE_MODULE_ENHANCEMENTS_PART3
    COMPREHENSIVE_MODULE_ENHANCEMENTS.update(COMPREHENSIVE_MODULE_ENHANCEMENTS_PART3)
except ImportError:
    pass

