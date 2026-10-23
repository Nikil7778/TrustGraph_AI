"""
SkillPath AI - Authoritative First-Party Learning Curriculum Content (Part 2)
Phase 22 - In-Depth First-Party Educational Content Expansion.

Covers:
- eda-workflow-data-profiling (EDA, Outliers, Distributions, Profiling)
- power-bi-dax-modeling (Power BI, DAX Measures, Filter Context, Star Schema)
- machine-learning-foundations (Supervised Learning, Bias-Variance, Regularization)
- feature-engineering-pipelines (Encoding, Scaling, Missing Value Imputation)
- model-evaluation-metrics (Confusion Matrix, Precision/Recall, ROC-AUC, F1)
"""

from typing import Dict, Any

COMPREHENSIVE_MODULE_ENHANCEMENTS_PART2: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # 6. Exploratory Data Analysis & Data Profiling
    # =========================================================================
    "eda-workflow-data-profiling": {
        "title": "Exploratory Data Analysis, Outlier Detection & Profiling",
        "concept_name": "EDA Workflow, Data Profiling & Statistical Distribution Analysis",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Execute systematic 4-stage exploratory data analysis: structural profiling, univariate distribution review, bivariate correlation analysis, and multivariate synthesis",
            "Detect statistical anomalies and extreme values using both Interquartile Range (IQR) fence rules and Z-score standardization thresholds",
            "Diagnose missing data mechanisms (MCAR, MAR, MNAR) and evaluate the risks of mean imputation vs domain-specific or indicator imputation",
            "Identify and quantify feature collinearity and skewed distributions using skewness coefficients and Spearman/Pearson correlation matrices",
            "Translate statistical exploratory patterns into actionable executive findings and downstream feature engineering decisions",
        ],
        "explanation": """### 1. Conceptual Foundation: The Objective of Exploratory Data Analysis
Exploratory Data Analysis (EDA) is the foundational investigative discipline of modern data science and analytics. Coined by statistician John Tukey, EDA is not merely creating random charts; it is a disciplined interrogation of raw data to uncover underlying structural anomalies, validate business assumptions, test hypotheses, and ensure data integrity before modeling or executive reporting.

Before a single line of machine learning code is written or a dashboard is deployed, a practitioner must answer three essential questions:
1. **What is the true shape, central tendency, and spread of each feature?**
2. **What data quality issues (missing values, extreme outliers, silent corruptions) exist?**
3. **How do features interact and correlate with the target business outcome?**

---

### 2. The 4-Stage EDA Protocol
A robust, production-grade EDA pipeline follows four sequential stages:

```
+--------------------------------------------------------------------------------+
|  Stage 1: Structural Profiling                                                 |
|  - Dimensions (rows x columns), data types (dtypes), memory consumption        |
|  - Distinct cardinality counts, unexpected nulls, and duplicate primary keys   |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|  Stage 2: Univariate Analysis                                                  |
|  - Quantitative: Mean, Median, IQR, Variance, Skewness, Kurtosis               |
|  - Categorical: Frequency tables, high-cardinality flags, imbalance ratios      |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|  Stage 3: Bivariate & Cross-Feature Analysis                                   |
|  - Correlation matrices (Pearson linear vs Spearman rank-monotonic)            |
|  - Categorical vs Numeric distributions across cohorts (box plots, violin)     |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|  Stage 4: Outlier & Anomaly Diagnosis                                          |
|  - Tukey's IQR Fences: [Q1 - 1.5 * IQR, Q3 + 1.5 * IQR]                        |
|  - Standardized Z-Scores: |Z| > 3.0                                            |
+--------------------------------------------------------------------------------+
```

---

### 3. Outlier Detection Mathematics: Tukey's Fences vs. Z-Score

#### A. Tukey's Interquartile Range (IQR) Rule
For non-normal or skewed business distributions (e.g., salaries, order transaction amounts, website dwell times), standard deviation is vulnerable to extreme values. Tukey's IQR rule provides a robust, non-parametric detection threshold:

$$\\text{IQR} = Q_3 - Q_1$$

Where $Q_1$ is the 25th percentile and $Q_3$ is the 75th percentile. The outer fences are defined as:

$$\\text{Lower Fence} = Q_1 - 1.5 \\times \\text{IQR}$$
$$\\text{Upper Fence} = Q_3 + 1.5 \\times \\text{IQR}$$

Any observation falling outside $[\\text{Lower Fence}, \\text{Upper Fence}]$ is flagged as an outlier candidate. For extreme outliers, a multiplier of $3.0$ is commonly used.

#### B. Parametric Z-Score Standardization
When a continuous variable is approximately normally distributed:

$$Z = \\frac{x - \\mu}{\\sigma}$$

Observations where $|Z| > 3.0$ represent events with less than $0.27\\%$ probability under a normal curve, indicating significant statistical deviation.

---

### 4. Missing Data Mechanisms: MCAR vs MAR vs MNAR
Understanding *why* data is missing dictates how it must be addressed:
* **Missing Completely at Random (MCAR)**: The missingness has no relationship to any observed or unobserved variable (e.g., accidental sensor network packet drop). Simple listwise deletion or imputation introduces minimal bias.
* **Missing at Random (MAR)**: Missingness is systematically related to other observed features, but not the missing value itself (e.g., younger users omitting salary, where age is observed). Imputation models conditioning on observed features work effectively.
* **Missing Not at Random (MNAR)**: Missingness depends directly on the unobserved value itself (e.g., high-income executives refusing to answer wealth surveys). Dropping or naive mean imputation severely biases the sample. An explicit missingness indicator column (`is_missing`) is required.""",
        "subtopics": [
            "Data Profiling & Automated Schema Auditing",
            "Univariate Distribution Metrics & Skewness",
            "Tukey's IQR & Parametric Z-Score Outlier Detection",
            "Missingness Typology: MCAR, MAR, and MNAR",
            "Bivariate Correlation & Multicollinearity Inspection",
            "Translating EDA Insights to Downstream Modeling Decisions"
        ],
        "why_it_matters_by_role": {
            "Data Analyst": "Uncovers revenue anomalies, faulty transaction logging, and skewed user metrics before reporting corrupted KPIs to leadership.",
            "Data Scientist": "Prevents garbage-in/garbage-out in machine learning pipelines by identifying multicollinearity, label leakage, and distribution shifts.",
            "Python Developer": "Enables writing defensive backend data validation pipelines and schema checks using Pydantic, Pandas, and Great Expectations."
        },
        "code_examples": [
            {
                "title": "Comprehensive Data Profiling & Structural Audit",
                "code": "import pandas as pd\nimport numpy as np\n\ndef profile_dataset(df: pd.DataFrame) -> pd.DataFrame:\n    \"\"\"Generates a comprehensive structural summary of a pandas DataFrame.\"\"\"\n    profile = pd.DataFrame({\n        'dtype': df.dtypes,\n        'total_rows': len(df),\n        'null_count': df.isnull().sum(),\n        'null_pct': (df.isnull().sum() / len(df) * 100).round(2),\n        'distinct_values': df.nunique(),\n        'cardinality_pct': (df.nunique() / len(df) * 100).round(2),\n    })\n    # Add skewness for numeric columns\n    numeric_cols = df.select_dtypes(include=[np.number]).columns\n    profile['skewness'] = np.nan\n    profile.loc[numeric_cols, 'skewness'] = df[numeric_cols].skew().round(3)\n    return profile\n\n# Example usage\ndf = pd.DataFrame({\n    'user_id': [101, 102, 103, 104, 105],\n    'income': [45000, 52000, 48000, 250000, np.nan],\n    'plan': ['Basic', 'Pro', 'Basic', 'Enterprise', 'Pro']\n})\nprint(profile_dataset(df))",
                "explanation": "Calculates dimensions, missing value percentages, unique cardinality, and skewness for each column in one pass.",
                "expected_output": "                 dtype  total_rows  null_count  null_pct  distinct_values  cardinality_pct  skewness\nuser_id          int64           5           0       0.0                5            100.0     0.000\nincome         float64           5           1      20.0                4             80.0     2.158\nplan            object           5           0       0.0                3             60.0       NaN"
            },
            {
                "title": "Tukey's IQR Outlier Detection & Capping",
                "code": "def detect_and_cap_outliers_iqr(series: pd.Series, factor: float = 1.5) -> pd.Series:\n    \"\"\"Identifies IQR outliers and caps values to the upper and lower fences.\"\"\"\n    q1 = series.quantile(0.25)\n    q3 = series.quantile(0.75)\n    iqr = q3 - q1\n    lower_fence = q1 - (factor * iqr)\n    upper_fence = q3 + (factor * iqr)\n    \n    outliers = series[(series < lower_fence) | (series > upper_fence)]\n    print(f'Detected {len(outliers)} outliers outside [{lower_fence:.2f}, {upper_fence:.2f}]')\n    return series.clip(lower=lower_fence, upper=upper_fence)\n\ntransactions = pd.Series([12, 15, 18, 14, 16, 19, 14, 150, 3, -40])\nclean_transactions = detect_and_cap_outliers_iqr(transactions)",
                "explanation": "Uses robust non-parametric quantile estimation to compute fences and winsorize extreme values without discarding sample size.",
                "expected_output": "Detected 2 outliers outside [-0.50, 31.50]"
            }
        ],
        "worked_example": {
            "scenario": "A FinTech analytics team is preparing loan applicant data for risk modeling. The 'annual_income' feature contains extreme outliers and 8% missing values. You must conduct a systematic EDA investigation, identify anomalies, and apply appropriate remediation.",
            "problem": "Raw income data has extreme right-skew (multi-millionaire applicants mixed with standard earners) and missing values. Naive mean imputation would artificially distort the variance and bias downstream models.",
            "approach": "1. Compute 5-number summary and skewness coefficient to confirm distribution shape.\n2. Quantify missingness mechanism and assess correlation with applicant employment status.\n3. Compute Tukey's IQR fences.\n4. Apply median imputation partitioned by employment category, combined with an explicit binary missingness indicator column.",
            "solution": "import pandas as pd\nimport numpy as np\n\ndata = {\n    'employment': ['Salaried', 'Self-Employed', 'Salaried', 'Executive', 'Salaried', 'Self-Employed'],\n    'income': [55000, 72000, np.nan, 850000, 60000, np.nan]\n}\ndf = pd.DataFrame(data)\n\n# 1. Add missingness indicator\ndf['income_was_missing'] = df['income'].isnull().astype(int)\n\n# 2. Impute with group-level median rather than global mean\nmedian_by_emp = df.groupby('employment')['income'].transform('median')\ndf['imputed_income'] = df['income'].fillna(median_by_emp)\n\n# 3. Apply log-transformation to compress extreme right-skew\ndf['log_income'] = np.log1p(df['imputed_income'])\nprint(df[['employment', 'income', 'income_was_missing', 'imputed_income', 'log_income']])",
            "result": "      employment    income  income_was_missing  imputed_income  log_income\n0       Salaried   55000.0                   0         55000.0   10.915107\n1  Self-Employed   72000.0                   0         72000.0   11.184435\n2       Salaried       NaN                   1         57500.0   10.959557\n3      Executive  850000.0                   0        850000.0   13.652993\n4       Salaried   60000.0                   0         60000.0   11.002117\n5  Self-Employed       NaN                   1         72000.0   11.184435",
            "why_it_works": "The binary indicator preserves the signal that the applicant omitted their income (potentially MNAR). Imputing the median by employment tier prevents distorting the distribution, and log1p compresses the extreme right-skew so executive outliers do not dominate linear models.",
            "alternative": "Use IterativeImputer (MICE) from scikit-learn to model income as a function of credit score, age, and loan amount rather than simple group medians."
        },
        "common_mistakes": [
            {
                "title": "Mistake 1 — Blindly Imputing Global Mean on Skewed Features",
                "what_it_looks_like": "Imputing `df['income'].fillna(df['income'].mean())` when income ranges from $20k to $10M.",
                "why_it_happens": "Beginners default to mean imputation because it is easy and taught as the standard default.",
                "how_to_fix_it": "Check skewness first. If $|\\text{skewness}| > 1.0$, use median imputation or group-conditioned imputation, and always create a `_was_missing` binary flag."
            },
            {
                "title": "Mistake 2 — Deleting Outliers Without Domain Investigation",
                "what_it_looks_like": "Running `df = df[df['amount'] < upper_fence]` and dropping 500 high-value VIP transactions.",
                "why_it_happens": "Equating statistical outliers with 'bad data' or errors.",
                "how_to_fix_it": "Distinguish measurement errors (e.g., negative age or impossible temperature) from legitimate high-value business events. Use robust models, tree ensembles, or log-transforms instead of deleting real customer transactions."
            },
            {
                "title": "Mistake 3 — Evaluating Linear Correlation (Pearson) on Non-Linear Relationships",
                "what_it_looks_like": "Observing a Pearson $r = 0.05$ between marketing spend and customer retention and concluding there is no relationship.",
                "why_it_happens": "Pearson correlation measures purely linear association; U-shaped or quadratic relationships produce an $r$ near zero.",
                "how_to_fix_it": "Always inspect scatter plots visually and evaluate Spearman rank correlation or mutual information alongside Pearson $r$."
            }
        ],
        "guided_practice": {
            "prompt": "You are given a DataFrame of e-commerce session durations (in seconds). Compute the 1st and 3rd quartiles, the IQR, and filter the DataFrame to return only rows that are strictly within Tukey's fences (1.5x IQR).",
            "starter_code": "import pandas as pd\n\ndata = {'session_id': range(1, 9), 'duration': [45, 52, 60, 48, 55, 320, 12, 50]}\ndf = pd.DataFrame(data)\n\n# Step 1: Compute Q1, Q3, and IQR\n# Step 2: Calculate lower and upper fences\n# Step 3: Filter df to keep non-outliers\n",
            "solution": "import pandas as pd\n\ndata = {'session_id': range(1, 9), 'duration': [45, 52, 60, 48, 55, 320, 12, 50]}\ndf = pd.DataFrame(data)\n\nq1 = df['duration'].quantile(0.25)\nq3 = df['duration'].quantile(0.75)\niqr = q3 - q1\n\nlower_fence = q1 - 1.5 * iqr\nupper_fence = q3 + 1.5 * iqr\n\nclean_df = df[(df['duration'] >= lower_fence) & (df['duration'] <= upper_fence)]\nprint(clean_df)",
            "hints": [
                "Use `df['duration'].quantile(0.25)` and `df['duration'].quantile(0.75)`.",
                "Compute `iqr = q3 - q1`.",
                "Calculate `lower_fence = q1 - 1.5 * iqr` and `upper_fence = q3 + 1.5 * iqr`.",
                "Filter with `df[(df['duration'] >= lower_fence) & (df['duration'] <= upper_fence)]`."
            ]
        },
        "independent_practice": {
            "prompt": "Given a customer DataFrame with columns `['customer_id', 'monthly_charges', 'churn']`, write a function `profile_and_flag_bivariate(df)` that: 1) calculates the median and IQR of `monthly_charges` grouped by `churn` status, 2) flags whether the churn group has a higher median charge than the retained group, and 3) returns a dictionary summarizing these findings.",
            "starter_code": "import pandas as pd\n\ndef profile_and_flag_bivariate(df: pd.DataFrame) -> dict:\n    # Implement here\n    pass\n",
            "solution": "import pandas as pd\n\ndef profile_and_flag_bivariate(df: pd.DataFrame) -> dict:\n    summary = df.groupby('churn')['monthly_charges'].agg([\n        ('median', 'median'),\n        ('q1', lambda x: x.quantile(0.25)),\n        ('q3', lambda x: x.quantile(0.75))\n    ])\n    summary['iqr'] = summary['q3'] - summary['q1']\n    \n    churned_median = summary.loc[1, 'median'] if 1 in summary.index else 0\n    retained_median = summary.loc[0, 'median'] if 0 in summary.index else 0\n    \n    return {\n        'churned_median': float(churned_median),\n        'retained_median': float(retained_median),\n        'churned_higher': bool(churned_median > retained_median),\n        'group_metrics': summary.to_dict()\n    }",
            "evaluation_criteria": [
                "Correctly computes median and IQR by group using groupby and quantile",
                "Accurately handles boolean/binary index lookups",
                "Returns structured dictionary with type-cast standard Python primitives"
            ]
        },
        "concept_check": [
            {
                "question": "Why is Tukey's IQR rule generally preferred over the Z-score method for detecting outliers in financial transaction datasets?",
                "options": [
                    "IQR is non-parametric and not distorted by extreme outliers, whereas mean and standard deviation in Z-scores are themselves pulled by extreme values",
                    "Z-score requires a minimum sample size of 10 million records to converge",
                    "IQR guarantees that no more than 1% of records will ever be flagged as outliers",
                    "Z-score only works on categorical text variables"
                ],
                "correct_index": 0,
                "explanation": "Mean and standard deviation are non-robust statistics: a single billion-dollar transaction massively inflates the mean and standard deviation, causing other genuine outliers to escape Z-score detection. IQR relies on order statistics (quantiles), which are immune to extreme values."
            },
            {
                "question": "Under the Missingness Typology, what distinguishes Missing Not at Random (MNAR) from Missing at Random (MAR)?",
                "options": [
                    "MNAR means the missingness directly depends on the value of the missing variable itself",
                    "MAR means the missing data was deleted intentionally by a database administrator",
                    "MNAR is completely random and safe to drop without introducing any sample bias",
                    "There is no mathematical difference; both represent sensor failure"
                ],
                "correct_index": 0,
                "explanation": "In MNAR, the probability of missingness depends on the unobserved value itself (e.g., people with low credit scores omitting credit scores). In MAR, missingness depends on other observed features (e.g., age or income)."
            },
            {
                "question": "A scatter plot between feature X and target Y shows a perfect parabolic U-shape (Y = X^2). What will the Pearson correlation coefficient between X and Y be?",
                "options": [
                    "Approximately 0.0, because Pearson correlation only captures monotonic linear relationships",
                    "+1.0, because the relationship is deterministic and perfect",
                    "-1.0, because the first half of the curve is negative",
                    "0.50, representing the average slope"
                ],
                "correct_index": 0,
                "explanation": "Pearson correlation measures purely linear association. Symmetrical non-linear relationships (like Y = X^2 centered at zero) yield a Pearson correlation near 0.0 despite having an exact mathematical dependency."
            }
        ],
        "applied_task": {
            "title": "Comprehensive Retail Fraud & Customer Dwell Profiling Audit",
            "context": "You are the Lead Data Analyst auditing a transactional log of 500,000 checkout events for an international e-commerce platform. Executives suspect payment processor timeouts have created phantom zero-dollar orders, and high-value bot attacks are skewing revenue KPIs.",
            "deliverables": [
                "Profile all numeric and categorical columns: compute missingness, cardinality, and skewness",
                "Implement Tukey's IQR filter to isolate bot transactions (checkout times under 3 seconds or order amounts exceeding upper fence)",
                "Document findings in a structured executive summary highlighting the percentage of corrupted transactions and recommending production data validation rules"
            ],
            "rubric": [
                "Data profiling accurately computes 5-number summary and skewness",
                "IQR outlier detection correctly isolates both lower (speed bots) and upper (whale/fraud) anomalies",
                "Provides domain-informed recommendations rather than blindly dropping high-revenue transactions"
            ]
        },
        "quick_reference": {
            "key_terms": [
                "Univariate Analysis: Analysis of a single variable's distribution and spread",
                "Bivariate Analysis: Analysis of the relationship between two distinct variables",
                "IQR (Interquartile Range): Q3 - Q1, representing the middle 50% of sorted observations",
                "Tukey's Fences: Q1 - 1.5*IQR (lower) and Q3 + 1.5*IQR (upper)",
                "MCAR / MAR / MNAR: The three formal statistical mechanisms of missing data"
            ],
            "formulas_and_rules": [
                "IQR = Q3 - Q1",
                "Tukey Outlier: x < Q1 - 1.5*IQR or x > Q3 + 1.5*IQR",
                "Z-Score: Z = (x - mean) / std_dev",
                "Log-Transform: np.log1p(x) = ln(1 + x) for compressing positive right-skew"
            ],
            "decision_matrix": [
                "Feature has high right-skew (skew > 1.0)? -> Use Median, IQR, and log1p transformation",
                "Feature has missing values (MAR)? -> Impute with group median/mode + add boolean is_missing flag",
                "Feature has extreme values that are real VIPs? -> Winsorize/cap at 99th percentile rather than deleting"
            ],
            "takeaways": [
                "Never begin predictive modeling or dashboarding without a complete structural and distribution audit.",
                "Outliers are not inherently bad data; investigate before deleting.",
                "Always check scatter plots; zero linear correlation does not mean no relationship."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Core Summary Statistics, Box Plots & Identifying Missing Values",
                "prerequisite_recap": "Covers basic summary statistics: mean, median, mode, and standard deviation.",
                "explanation_supplement": "Explains how to interpret box plots visually and walk through df.info(), df.describe(), and df.isnull().sum() step-by-step.",
                "key_additions": [
                    "Visual box plot interpretation guide",
                    "Basic Pandas inspection commands (info, describe, shape)",
                    "Simple mean vs median comparison"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "Tukey Fences, Correlation Matrices, Skewness & Imputation Strategies",
                "prerequisite_recap": "Assumes comfort with basic Pandas slicing and standard deviation.",
                "explanation_supplement": "Covers IQR fence calculations, skewness metrics, missing data mechanisms (MCAR/MAR), and group-level median imputation.",
                "key_additions": [
                    "Tukey's 1.5x IQR formula derivation and implementation",
                    "Missing data categorization (MCAR vs MAR)",
                    "Handling skewed distributions with log1p"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "MICE Imputation, Multivariate Outlier Detection (Mahalanobis / Isolation Forest) & Data Drift",
                "prerequisite_recap": "Assumes complete familiarity with univariate statistical distributions.",
                "explanation_supplement": "Explores multivariate anomaly detection using Mahalanobis distance and Isolation Forests, Multiple Imputation by Chained Equations (MICE), and detecting population covariate shift using Kolmogorov-Smirnov distribution tests.",
                "key_additions": [
                    "Isolation Forests for multidimensional anomaly detection",
                    "MICE (IterativeImputer) multivariate imputation",
                    "Population stability index (PSI) and Kolmogorov-Smirnov distribution drift testing"
                ]
            }
        }
    },

    # =========================================================================
    # 7. Power BI & DAX Modeling
    # =========================================================================
    "power-bi-dax-modeling": {
        "title": "Business Intelligence, DAX Modeling & Semantic Layers",
        "concept_name": "DAX Measures, Filter Context & Dimensional Modeling",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Architect star-schema semantic data models distinguishing high-volume Fact tables from Conformed Dimension tables",
            "Master DAX calculation engine mechanics: Row Context, Filter Context, and Context Transition",
            "Formulate robust executive KPIs using CALCULATE, FILTER, ALL, and safe division via DIVIDE",
            "Implement Time-Intelligence calculations (YTD, Prior Year, YoY Growth) with dedicated Date dimensions",
            "Diagnose and eliminate bidirectional relationship hazards and performance bottlenecks in semantic models",
        ],
        "explanation": """### 1. Dimensional Modeling: Star Schema vs. Flat Reporting
In modern enterprise business intelligence, relational databases are rarely visualized directly. Instead, Data Analysts transform raw transactional tables into an optimized analytical model known as a **Star Schema**:

```
                 +-----------------------+
                 |    Dim_Customer       |
                 |-----------------------|
                 | Customer_Key (PK)     |
                 | Customer_Name         |
                 | Segment, Country      |
                 +-----------------------+
                             | 1
                             |
                             | *
+--------------------+   +-----------------------+   +--------------------+
|     Dim_Date       |   |      Fact_Sales       |   |    Dim_Product     |
|--------------------|   |-----------------------|   |--------------------|
| Date_Key (PK)      |1  | Sales_ID (PK)         |  1| Product_Key (PK)   |
| Calendar_Year      |---| Date_Key (FK)         |---| Product_Name       |
| Quarter, Month     |*  | Customer_Key (FK)     |*  | Category, Margin   |
+--------------------+   | Product_Key (FK)      |   +--------------------+
                         | Revenue, Quantity     |
                         | Discount_Amount       |
                         +-----------------------+
```

#### Why Star Schema Matters:
1. **Fact Tables**: Contain granular numerical measurements (revenue, quantity, latency). They have millions or billions of rows and few columns.
2. **Dimension Tables**: Contain descriptive business attributes (customer name, region, product category). They provide filtering and slicing context.
3. **1-to-Many Relationships**: Standard star schemas use unidirectional (1-to-*) relationships flowing from Dimensions down to Facts. Bidirectional filters should be avoided as they introduce circular calculation ambiguities.

---

### 2. The Core DAX Calculation Engine: Row Context vs. Filter Context

The single greatest conceptual hurdle in mastering DAX (Data Analysis Expressions) is differentiating **Row Context** from **Filter Context**:

#### A. Row Context (Iteration)
* Exists during table iterations (e.g., Calculated Columns or iterator functions like `SUMX`, `AVERAGEX`).
* Evaluates expressions row-by-row.
* **Crucial Rule**: Row Context *does NOT filter other tables or measures by itself*. It only knows the values of columns in the current row.

#### B. Filter Context (Aggregation & Slicers)
* The active set of filters applied by visual elements, report slicers, matrix row/column headers, and DAX expressions.
* Determines which rows of the underlying data model are visible when evaluating a Measure.

#### C. Context Transition & The Power of CALCULATE
`CALCULATE(<expression>, <filter1>, <filter2>, ...)` is the engine's most vital function. It performs two critical tasks:
1. **Modifies Filter Context**: It overrides, removes, or adds filters to the existing visual filter context.
2. **Triggers Context Transition**: When wrapped around a measure inside a Row Context (such as in `SUMX` or a calculated column), `CALCULATE` automatically converts the current row's column values into an equivalent Filter Context!

---

### 3. Safe Division & KPI Formulas

In DAX, never use the forward slash (`/`) operator for financial ratios. Always use `DIVIDE()`:

$$\\text{DIVIDE}(\\text{Numerator}, \\text{Denominator}, [\\text{AlternateResult}])$$

`DIVIDE()` intercepts division-by-zero at the engine level, returning `BLANK()` (or a specified fallback like 0) without raising runtime errors or generating `#DIV/0!` visual breaks.""",
        "subtopics": [
            "Star Schema Architecture & Dimensional Modeling",
            "Row Context vs. Filter Context Mechanics",
            "CALCULATE and Context Transition",
            "Time Intelligence: DATESYTD, SAMEPERIODLASTYEAR",
            "Iterator Functions: SUMX, AVERAGEX, and Performance",
            "Eliminating Bidirectional Ambiguity & Cross-Filter Traps"
        ],
        "why_it_matters_by_role": {
            "Data Analyst": "Essential for delivering executive dashboards, financial statements, and high-performance semantic models in Power BI and Fabric.",
            "Data Scientist": "Enables understanding how business KPIs are calculated and aggregated in BI layers before extracting features for machine learning.",
            "Python Developer": "Helps in structuring backend SQL data marts and OLAP views that feed directly into Power BI enterprise datasets."
        },
        "code_examples": [
            {
                "title": "Robust Margin Percentage Measure with Safe Division",
                "code": "-- Gross Margin Percentage Measure\nMargin Pct = \nVAR TotalRevenue = SUM(FactSales[Revenue])\nVAR TotalCost = SUM(FactSales[TotalCost])\nVAR GrossProfit = TotalRevenue - TotalCost\nRETURN\n    DIVIDE(GrossProfit, TotalRevenue, 0)",
                "explanation": "Uses variables (VAR) for readability and performance (evaluating aggregations once), and DIVIDE to safely handle zero-revenue edge cases.",
                "expected_output": "Evaluates to 0.384 (38.4%) under a visual filtered to Category = 'Electronics'"
            },
            {
                "title": "Prior Year Sales & Year-over-Year Growth using Time Intelligence",
                "code": "-- 1. Prior Year Sales\nSales Prior Year = \nCALCULATE(\n    [Total Sales],\n    SAMEPERIODLASTYEAR(DimDate[Date])\n)\n\n-- 2. YoY Growth Percentage\nSales YoY Growth Pct = \nVAR CurrentSales = [Total Sales]\nVAR PriorSales = [Sales Prior Year]\nVAR GrowthAmount = CurrentSales - PriorSales\nRETURN\n    DIVIDE(GrowthAmount, PriorSales, BLANK())",
                "explanation": "Leverages SAMEPERIODLASTYEAR across a contiguous Date dimension to shift the filter context exactly 365 days back.",
                "expected_output": "| Year | Total Sales | Sales Prior Year | Sales YoY Growth Pct |\n| 2023 | $1,200,000  | $1,000,000        | 20.0%                |"
            }
        ],
        "worked_example": {
            "scenario": "The Chief Revenue Officer needs a dynamic measure showing the 'Contribution Percentage of Selected Category to Total Enterprise Sales'. The measure must accurately reflect slicers for date and region, but must ignore any category filter on the denominator.",
            "problem": "When a user selects Category = 'Furniture' on a slicer, standard [Total Sales] automatically filters to Furniture on both numerator and denominator, producing 100%. The denominator must override the Category filter while preserving Date and Region filters.",
            "approach": "1. Define base aggregation for numerator: [Total Sales].\n2. Use CALCULATE with REMOVEFILTERS(DimProduct[Category]) on the denominator to strip only category filters.\n3. Combine using DIVIDE with a 0 fallback.",
            "solution": "Category Contribution Pct = \nVAR CategorySales = [Total Sales]\nVAR AllCategorySales = \n    CALCULATE(\n        [Total Sales],\n        REMOVEFILTERS(DimProduct[Category])\n    )\nRETURN\n    DIVIDE(CategorySales, AllCategorySales, 0)",
            "result": "When 'Furniture' is selected, CategorySales = $250,000, AllCategorySales = $1,000,000, returning 25.0%.",
            "why_it_works": "REMOVEFILTERS(DimProduct[Category]) explicitly clears the incoming visual filter on Category inside CALCULATE, allowing the denominator to encompass all products in the active Region and Date window.",
            "alternative": "Use ALL(DimProduct[Category]) which performs the same filter removal function as REMOVEFILTERS in modern DAX."
        },
        "common_mistakes": [
            {
                "title": "Mistake 1 — Creating Calculated Columns Instead of Measures for Aggregations",
                "what_it_looks_like": "Writing a calculated column `Total_Sales = SUM(FactSales[Revenue])` in the Sales table.",
                "why_it_happens": "Excel users expect values to be materialized row-by-row in a visible grid.",
                "how_to_fix_it": "Calculated columns consume expensive RAM and do not respond dynamically to report slicers. Always write dynamic Measures for aggregations; reserve calculated columns solely for categorical slice/dice attributes."
            },
            {
                "title": "Mistake 2 — Using the Forward Slash (/) for Ratios",
                "what_it_looks_like": "Writing `Margin = (SUM(Sales) - SUM(Cost)) / SUM(Sales)`.",
                "why_it_happens": "Standard arithmetic habit.",
                "how_to_fix_it": "Division by zero produces an error or Infinity in DAX, crashing visuals. Always use `DIVIDE(Numerator, Denominator, 0)`."
            },
            {
                "title": "Mistake 3 — Bidirectional Cross-Filtering on Multiple Tables",
                "what_it_looks_like": "Setting cross-filter direction to 'Both' between multiple fact and dimension tables.",
                "why_it_happens": "Attempting a quick fix when a visual slicer doesn't filter another visual as expected.",
                "how_to_fix_it": "Bidirectional filters introduce ambiguous evaluation paths and severely degrade VertiPaq engine performance. Maintain unidirectional filters and use `CROSSFILTER()` inside specific DAX measures when needed."
            }
        ],
        "guided_practice": {
            "prompt": "Write a DAX measure named `Customer Lifetime Revenue` that calculates the total sales across all historical dates for each customer, ignoring any date slicers applied to the report page.",
            "starter_code": "-- Customer Lifetime Revenue\nCustomer Lifetime Revenue = \nCALCULATE(\n    -- Base measure here\n    -- Filter override here\n)",
            "solution": "Customer Lifetime Revenue = \nCALCULATE(\n    [Total Sales],\n    REMOVEFILTERS(DimDate)\n)",
            "hints": [
                "The base measure is `[Total Sales]`.",
                "To ignore date slicers, use `REMOVEFILTERS(DimDate)` inside CALCULATE.",
                "Do not remove filters on DimCustomer, so the customer row context remains active."
            ]
        },
        "independent_practice": {
            "prompt": "Write a DAX measure named `High Value Order Count` that counts the distinct number of orders in `FactSales` where the order amount exceeds $500. Use `DISTINCTCOUNT` or `CALCULATE`.",
            "starter_code": "-- High Value Order Count\nHigh Value Order Count = \n-- Your DAX code here",
            "solution": "High Value Order Count = \nCALCULATE(\n    DISTINCTCOUNT(FactSales[Order_ID]),\n    FactSales[Amount] > 500\n)",
            "evaluation_criteria": [
                "Uses CALCULATE to apply the condition FactSales[Amount] > 500",
                "Uses DISTINCTCOUNT on the Order_ID column to prevent double-counting order line items",
                "Syntactically valid DAX expression"
            ]
        },
        "concept_check": [
            {
                "question": "What is the primary difference between a Calculated Column and a Measure in Power BI?",
                "options": [
                    "Calculated columns are evaluated during data refresh and stored in RAM; Measures are evaluated dynamically on-the-fly under Filter Context",
                    "Calculated columns can only contain text; Measures can only contain numbers",
                    "Measures are stored permanently in the database table file; Calculated columns are never saved",
                    "Calculated columns respond dynamically to slicers; Measures do not"
                ],
                "correct_index": 0,
                "explanation": "Calculated columns are computed during data refresh and take up disk/memory. Measures consume zero storage space until visualized, recalculating dynamically based on active visual filters and slicers."
            },
            {
                "question": "What happens when CALCULATE is invoked inside an iterator like SUMX or inside a Calculated Column?",
                "options": [
                    "It triggers Context Transition, converting the active Row Context into an equivalent Filter Context",
                    "It causes a runtime syntax error because CALCULATE cannot be nested",
                    "It forces the VertiPaq engine to switch to DirectQuery mode",
                    "It automatically clears all relationships in the data model"
                ],
                "correct_index": 0,
                "explanation": "Context Transition is a defining feature of DAX: CALCULATE automatically turns the row's values into active filters, evaluating the measure as if those column values were slicers."
            },
            {
                "question": "Why should bidirectional cross-filtering be avoided in enterprise star schemas?",
                "options": [
                    "It can create ambiguous multi-path relationships and significantly degrade query performance",
                    "Power BI Desktop disables publication to Power BI Service when bidirectional filters exist",
                    "It prevents the use of the SUM function",
                    "It forces all measures to return zero"
                ],
                "correct_index": 0,
                "explanation": "Bidirectional relationships allow filters to flow upstream from Fact to Dimension, creating circular paths, unexpected calculation side-effects, and severe engine slowdowns."
            }
        ],
        "applied_task": {
            "title": "Enterprise Executive Revenue & Margin Semantic Model",
            "context": "You are the Lead BI Architect designing an executive dashboard for an e-commerce conglomerate. Leadership needs instant visibility into Total Revenue, Gross Margin %, and YoY Growth across customer segments and regions.",
            "deliverables": [
                "Star schema design documentation identifying FactSales and DimCustomer, DimProduct, DimDate",
                "Production DAX measures for [Total Revenue], [Gross Profit], [Gross Margin Pct], and [YoY Sales Growth Pct]",
                "Validation matrix confirming correct filter behavior when cross-filtering by Region and Year"
            ],
            "rubric": [
                "Correct star schema design with 1-to-many unidirectional relationships",
                "Measures use VAR/RETURN syntax and DIVIDE for safe ratios",
                "YoY measure correctly leverages Date dimension and SAMEPERIODLASTYEAR"
            ]
        },
        "quick_reference": {
            "key_terms": [
                "Star Schema: An analytical data model with central Fact tables linked to surrounding Dimension tables",
                "Row Context: Iterative context that evaluates column values row-by-row",
                "Filter Context: Active set of filters applied by slicers, visuals, and DAX expressions",
                "Context Transition: Conversion of Row Context into Filter Context triggered by CALCULATE",
                "VertiPaq Engine: In-memory columnar storage and calculation engine powering Power BI"
            ],
            "formulas_and_rules": [
                "Safe Division: DIVIDE(Numerator, Denominator, 0)",
                "Context Override: CALCULATE([Measure], REMOVEFILTERS(DimTable[Column]))",
                "YTD Calculation: TOTALYTD([Total Sales], DimDate[Date])",
                "Prior Year: CALCULATE([Total Sales], SAMEPERIODLASTYEAR(DimDate[Date]))"
            ],
            "decision_matrix": [
                "Need a dynamic KPI responding to slicers? -> Write a Measure",
                "Need a static slice/dice category or age bracket? -> Write a Calculated Column",
                "Need to calculate sales across lines before summing? -> Use SUMX iterator"
            ],
            "takeaways": [
                "Star schemas with unidirectional 1-to-many relationships outperform complex snowflake schemas.",
                "Always use DIVIDE instead of / to avoid division-by-zero crashes.",
                "Mastering CALCULATE and Filter Context is the core differentiator of professional DAX developers."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Power BI Navigation, Star Schema Basics & Simple Measures",
                "prerequisite_recap": "Covers basic Excel formulas and understanding tables.",
                "explanation_supplement": "Explains how to connect data, create 1-to-many relationships in the Model view, and write basic SUM and DIVIDE measures.",
                "key_additions": [
                    "Model view relationship builder walkthrough",
                    "Basic SUM, AVERAGE, and DIVIDE measure syntax",
                    "Calculated columns vs Measures conceptual guide"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "CALCULATE, Filter Context, Variables & Time Intelligence",
                "prerequisite_recap": "Assumes comfort building basic star schemas and simple measures.",
                "explanation_supplement": "Deep dives into Filter Context, using CALCULATE to override slicers, VAR/RETURN formatting, and SAMEPERIODLASTYEAR.",
                "key_additions": [
                    "Step-by-step Filter Context propagation tracing",
                    "CALCULATE with REMOVEFILTERS and ALL",
                    "Time-Intelligence with dedicated Date tables"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Context Transition, VertiPaq Engine Internals, SUMX & Performance Tuning",
                "prerequisite_recap": "Assumes mastery of standard DAX measures and Time Intelligence.",
                "explanation_supplement": "Explores VertiPaq columnar compression, dictionary encoding, tracing SE (Storage Engine) vs FE (Formula Engine) queries using DAX Studio, and avoiding expensive iterator materialization.",
                "key_additions": [
                    "DAX Studio query plan and server timing analysis",
                    "Storage Engine vs Formula Engine execution tuning",
                    "Context Transition mechanics in complex nested iterators"
                ]
            }
        }
    },

    # =========================================================================
    # 8. Machine Learning Foundations
    # =========================================================================
    "machine-learning-foundations": {
        "title": "Supervised Learning, Model Evaluation & Regularization",
        "concept_name": "Machine Learning Foundations, Bias-Variance & Regularization",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Deconstruct the machine learning paradigm: hypothesis spaces, loss functions, and optimization algorithms",
            "Quantify the Bias-Variance Tradeoff and diagnose underfitting vs overfitting using learning curves",
            "Implement L1 (Lasso) and L2 (Ridge) regularization to penalize model complexity and prevent overfitting",
            "Architect leakage-free cross-validation pipelines ensuring strict separation of training and evaluation data",
            "Formulate mathematical objective functions for Mean Squared Error (MSE), Cross-Entropy, and Regularized Loss",
        ],
        "explanation": """### 1. Conceptual Foundation: The Machine Learning Paradigm
Traditional software engineering relies on explicit rules: a programmer writes code ($f$) that takes input data ($X$) to produce an output ($Y$). Machine learning inverts this paradigm: given empirical pairs of input data ($X$) and outputs ($Y$), the algorithm searches a parameterized hypothesis space to discover the underlying mathematical function ($\\\\hat{f}$) that best approximates the relationship:

$$\\hat{Y} = \\hat{f}(X; \\theta)$$

Where $\\theta$ represents the learned model parameters (weights and biases).

```
Traditional Programming:    Data (X) + Rules (f)       ===> Output (Y)
Machine Learning:           Data (X) + Output (Y)      ===> Learned Rules (f̂)
```

---

### 2. The Bias-Variance Tradeoff
The expected generalization error of any supervised learning model on unseen test data can be decomposed into three mathematically distinct components:

$$\\text{Expected Error} = \\text{Bias}^2 + \\text{Variance} + \\text{Irreducible Error} (\\sigma^2)$$

```
Error
  ^
  |        Total Test Error = Bias^2 + Variance + σ^2
  |          \\             /
  |           \\   _.-._   /
  |            \\ /     \\ /
  |             V       V   <-- Optimal Complexity (Sweet Spot)
  |            /         \\
  |  High Bias/           \\  High Variance
  | (Underfit)             \\ (Overfit)
  +---------------------------------------------> Model Complexity
```

1. **Bias (Underfitting)**: Error arising from erroneous assumptions in the learning algorithm. High bias models (e.g., simple linear regression on complex non-linear data) fail to capture underlying patterns, exhibiting high training error and high test error.
2. **Variance (Overfitting)**: Error arising from sensitivity to small fluctuations in the training set. High variance models (e.g., deep unconstrained decision trees) memorize random noise, exhibiting near-zero training error but catastrophic test error.
3. **Irreducible Error ($\\sigma^2$)**: Inherent noise in the data generating process (measurement error, unobserved variables) that cannot be eliminated by any model.

---

### 3. Regularization: Ridge (L2) vs. Lasso (L1)

To prevent models with high capacity from overfitting, we add a complexity penalty to the optimization loss function:

$$\\mathcal{L}_{\\text{reg}}(\\theta) = \\mathcal{L}_{\\text{data}}(\\theta) + \\lambda \\cdot \\Omega(\\theta)$$

Where $\\lambda \\ge 0$ is the regularization hyperparameter controlling the strength of the penalty.

#### A. Ridge Regularization ($L_2$ Penalty)
Penalizes the sum of squared weights:

$$\\mathcal{L}_{\\text{Ridge}}(\\mathbf{w}) = \\frac{1}{n} \\sum_{i=1}^n (y_i - \\mathbf{w}^T \\mathbf{x}_i)^2 + \\lambda \\sum_{j=1}^p w_j^2$$

* **Effect**: Shrinks weights toward zero smoothly. All features are retained, but their influence is curtailed. Excellent when many collinear features exist.

#### B. Lasso Regularization ($L_1$ Penalty)
Penalizes the sum of absolute weights:

$$\\mathcal{L}_{\\text{Lasso}}(\\mathbf{w}) = \\frac{1}{n} \\sum_{i=1}^n (y_i - \\mathbf{w}^T \\mathbf{x}_i)^2 + \\lambda \\sum_{j=1}^p |w_j|$$

* **Effect**: Drives non-informative feature weights to **exactly zero**, performing automatic feature selection and producing sparse, interpretable models.""",
        "subtopics": [
            "Supervised Learning Formulation & Loss Functions",
            "The Bias-Variance Decomposition & Learning Curves",
            "L2 Ridge vs. L1 Lasso Regularization Mechanics",
            "Cross-Validation Protocols (K-Fold, Stratified K-Fold)",
            "Data Leakage Prevention via Scikit-Learn Pipelines",
            "Hyperparameter Tuning with GridSearchCV and RandomSearch"
        ],
        "why_it_matters_by_role": {
            "Data Scientist": "Foundational theory for training resilient predictive models, diagnosing model failure modes, and avoiding costly overfitting.",
            "Data Analyst": "Provides conceptual understanding of automated forecasting tools, trendlines, and regression outputs.",
            "Python Developer": "Enables architecting scalable Scikit-Learn / MLflow prediction microservices with clean API interfaces."
        },
        "code_examples": [
            {
                "title": "Leakage-Free Cross-Validation Pipeline with Regularization",
                "code": "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import Ridge\nfrom sklearn.model_selection import cross_val_score, KFold\nimport numpy as np\n\n# Construct pipeline ensuring scaling happens INSIDE cross-validation folds\npipe = Pipeline([\n    ('scaler', StandardScaler()),\n    ('model', Ridge(alpha=10.0))\n])\n\nX = np.random.randn(100, 10)\ny = 3 * X[:, 0] - 2 * X[:, 1] + np.random.randn(100)\n\nkf = KFold(n_splits=5, shuffle=True, random_state=42)\nscores = cross_val_score(pipe, X, y, cv=kf, scoring='neg_mean_squared_error')\nrmse_scores = np.sqrt(-scores)\n\nprint(f'5-Fold Mean RMSE: {rmse_scores.mean():.4f} (+/- {rmse_scores.std():.4f})')",
                "explanation": "Wrapping StandardScaler and Ridge in a Pipeline guarantees scaling parameters (mean, std) are computed strictly on training folds, eliminating data leakage.",
                "expected_output": "5-Fold Mean RMSE: 1.0423 (+/- 0.0815)"
            },
            {
                "title": "Lasso Feature Selection: Forcing Coefficients to Zero",
                "code": "from sklearn.linear_model import Lasso\nfrom sklearn.preprocessing import StandardScaler\nimport pandas as pd\nimport numpy as np\n\n# Generate 5 informative features and 5 pure noise features\nnp.random.seed(42)\nX_raw = np.random.randn(150, 10)\nfeature_names = [f'feat_{i}' for i in range(10)]\n# Target depends only on feat_0 and feat_1\ny = 5 * X_raw[:, 0] + 3 * X_raw[:, 1] + np.random.randn(150)\n\nX_scaled = StandardScaler().fit_transform(X_raw)\nlasso = Lasso(alpha=0.5, random_state=42)\nlasso.fit(X_scaled, y)\n\ncoef_df = pd.DataFrame({'feature': feature_names, 'coefficient': lasso.coef_.round(3)})\nprint(coef_df[coef_df['coefficient'] != 0])",
                "explanation": "Lasso's L1 penalty drives noise features (feat_2 through feat_9) exactly to 0.0, retaining only the true predictive signals.",
                "expected_output": "  feature  coefficient\n0  feat_0        4.482\n1  feat_1        2.495"
            }
        ],
        "worked_example": {
            "scenario": "A SaaS marketing team is building a model to predict customer churn probability. The training dataset has 2,000 customers and 85 behavioural features, many of which are highly correlated (e.g., page views, session counts, clicks). An unregularized model suffers severe overfitting.",
            "problem": "An unregularized linear model produces huge unstable coefficients due to multicollinearity, yielding 99% train accuracy but only 61% test accuracy.",
            "approach": "1. Standardize features to place all 85 metrics on identical scales.\n2. Apply L2 Ridge regularization with cross-validated alpha tuning to shrink collinear coefficients.\n3. Evaluate test performance using Area Under ROC Curve (ROC-AUC) to handle class imbalance.",
            "solution": "from sklearn.datasets import make_classification\nfrom sklearn.model_selection import train_test_split\nfrom sklearn.linear_model import LogisticRegression\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.metrics import roc_auc_score\n\n# Simulate 2000 customers with 85 features\nX, y = make_classification(n_samples=2000, n_features=85, n_informative=15, weights=[0.8, 0.2], random_state=42)\nX_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)\n\n# Build regularized logistic regression pipeline (C = 1/lambda)\npipe = Pipeline([\n    ('scaler', StandardScaler()),\n    ('clf', LogisticRegression(penalty='l2', C=0.1, solver='lbfgs', max_iter=1000))\n])\n\npipe.fit(X_train, y_train)\ny_pred_prob = pipe.predict_proba(X_test)[:, 1]\nauc = roc_auc_score(y_test, y_pred_prob)\nprint(f'Test ROC-AUC: {auc:.4f}')",
            "result": "Test ROC-AUC: 0.8642 (compared to 0.6120 on the unregularized model).",
            "why_it_works": "The L2 penalty ($C=0.1$, where smaller $C$ means stronger regularization) constrains the Euclidean norm of the weight vector, preventing collinear features from cancelling each other out with massive opposite signs.",
            "alternative": "Use ElasticNet, which blends L1 and L2 penalties via the l1_ratio parameter to both select features and stabilize collinear groups."
        },
        "common_mistakes": [
            {
                "title": "Mistake 1 — Scaling Features Before Train-Test Splitting (Data Leakage)",
                "what_it_looks_like": "Calling `StandardScaler().fit_transform(X)` on the entire dataset before `train_test_split()`.",
                "why_it_happens": "Convenience; running preprocessing once on the full matrix.",
                "how_to_fix_it": "This leaks test set mean and variance into the training process, producing unrealistically optimistic cross-validation scores. Always fit scalers strictly on training data or embed them inside an `sklearn.pipeline.Pipeline`."
            },
            {
                "title": "Mistake 2 — Applying Regularization Without Feature Standardization",
                "what_it_looks_like": "Fitting `Ridge()` directly on raw features where 'salary' is in tens of thousands and 'age' is in tens.",
                "why_it_happens": "Forgetting that L1 and L2 penalties penalize weight magnitudes directly.",
                "how_to_fix_it": "Because salary is measured in large units, its weight is naturally tiny, so the regularization penalty barely affects it, while age's weight is heavily penalized. Always standardize features ($Z = (x - \\mu) / \\sigma$) before regularized linear models."
            },
            {
                "title": "Mistake 3 — Evaluating Imbalanced Classification Models with Accuracy",
                "what_it_looks_like": "Celebrating a 95% accuracy score on a dataset with 95% non-churners and 5% churners.",
                "why_it_happens": "Accuracy seems intuitive to stakeholders.",
                "how_to_fix_it": "A naive model predicting 'no churn' for 100% of cases achieves 95% accuracy while identifying zero actual churners. Use ROC-AUC, PR-AUC, F1-Score, or Precision/Recall metrics."
            }
        ],
        "guided_practice": {
            "prompt": "Construct a Scikit-Learn Pipeline containing a StandardScaler and a Lasso regression model with alpha=0.1. Fit the pipeline on X_train, y_train and evaluate the mean squared error on X_test, y_test.",
            "starter_code": "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import Lasso\nfrom sklearn.metrics import mean_squared_error\n\n# Define the pipeline\n# Fit on training data\n# Predict and compute MSE on test data\n",
            "solution": "from sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.linear_model import Lasso\nfrom sklearn.metrics import mean_squared_error\n\npipe = Pipeline([\n    ('scaler', StandardScaler()),\n    ('lasso', Lasso(alpha=0.1, random_state=42))\n])\n\npipe.fit(X_train, y_train)\ny_pred = pipe.predict(X_test)\nmse = mean_squared_error(y_test, y_pred)\nprint(f'Test MSE: {mse:.4f}')",
            "hints": [
                "Pipeline takes a list of (name, transformer/estimator) tuples.",
                "Step 1 is ('scaler', StandardScaler()).",
                "Step 2 is ('lasso', Lasso(alpha=0.1)).",
                "Call pipe.fit(X_train, y_train) and pipe.predict(X_test)."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function `evaluate_regularization_alphas(X, y, alphas)` that iterates through a list of alpha values, trains a Ridge model using 5-fold cross-validation for each alpha, and returns the alpha value that achieves the minimum mean RMSE.",
            "starter_code": "import numpy as np\nfrom sklearn.linear_model import Ridge\nfrom sklearn.model_selection import cross_val_score\n\ndef evaluate_regularization_alphas(X, y, alphas: list) -> float:\n    # Implement here\n    pass\n",
            "solution": "import numpy as np\nfrom sklearn.linear_model import Ridge\nfrom sklearn.model_selection import cross_val_score\nfrom sklearn.preprocessing import StandardScaler\nfrom sklearn.pipeline import Pipeline\n\ndef evaluate_regularization_alphas(X, y, alphas: list) -> float:\n    best_alpha = alphas[0]\n    lowest_rmse = float('inf')\n    \n    for a in alphas:\n        pipe = Pipeline([\n            ('scaler', StandardScaler()),\n            ('ridge', Ridge(alpha=a))\n        ])\n        scores = cross_val_score(pipe, X, y, cv=5, scoring='neg_mean_squared_error')\n        mean_rmse = np.mean(np.sqrt(-scores))\n        if mean_rmse < lowest_rmse:\n            lowest_rmse = mean_rmse\n            best_alpha = a\n            \n    return float(best_alpha)",
            "evaluation_criteria": [
                "Iterates over candidate alphas correctly",
                "Embeds scaling inside cross-validation to prevent leakage",
                "Computes RMSE as np.sqrt(-scores)",
                "Returns the alpha corresponding to lowest RMSE"
            ]
        },
        "concept_check": [
            {
                "question": "What is the primary operational difference between L1 (Lasso) and L2 (Ridge) regularization?",
                "options": [
                    "L1 can drive non-informative feature weights strictly to zero (feature selection), whereas L2 shrinks weights asymptotically toward zero without zeroing them",
                    "L1 only works on classification problems, while L2 only works on regression",
                    "L2 eliminates the need to split data into training and test sets",
                    "L1 requires features to be unstandardized, whereas L2 requires standard scaling"
                ],
                "correct_index": 0,
                "explanation": "Because L1 regularization uses the diamond-shaped L1-ball (sum of absolute values), the optimization contours frequently intersect the axes at exactly zero, eliminating features. L2 uses a circular ball, shrinking weights smoothly without setting them strictly to zero."
            },
            {
                "question": "If a model exhibits 99.8% accuracy on training data but drops to 64.2% accuracy on validation data, what is the primary diagnosis?",
                "options": [
                    "High Variance (Overfitting) — the model has memorized training noise",
                    "High Bias (Underfitting) — the model lacks sufficient capacity",
                    "High Irreducible Error — the dataset is corrupt",
                    "Data Leakage — the test set leaked into the training set"
                ],
                "correct_index": 0,
                "explanation": "A massive gap between near-perfect training performance and mediocre validation performance is the textbook symptom of high variance / overfitting."
            },
            {
                "question": "Why must StandardScaler be fit exclusively on training data and not the whole dataset?",
                "options": [
                    "Fitting on the whole dataset leaks test set distribution metrics (mean and standard deviation) into training, causing overly optimistic evaluation",
                    "StandardScaler produces NaN values if run on more than 1,000 rows",
                    "Scikit-learn raises a ValueError if test data is scaled",
                    "StandardScaler is non-deterministic"
                ],
                "correct_index": 0,
                "explanation": "Data leakage occurs whenever information from outside the training dataset is used to create the model. Fitting a scaler on the test set biases the evaluation because the model implicitly 'knows' the test set mean and spread."
            }
        ],
        "applied_task": {
            "title": "Predictive Hospital Readmission Risk Modeling",
            "context": "You are a Healthcare Machine Learning Engineer tasked with predicting 30-day patient readmissions across 15,000 historical patient charts with 60 clinical features (lab results, vital signs, demographic factors).",
            "deliverables": [
                "Leakage-free Scikit-Learn Pipeline combining imputation, scaling, and regularized logistic regression",
                "5-fold stratified cross-validation comparison of Ridge, Lasso, and ElasticNet models",
                "Evaluation report ranking models by ROC-AUC and identifying top clinical risk drivers"
            ],
            "rubric": [
                "Zero data leakage: all transformers embedded in Pipeline",
                "Correct use of StratifiedKFold to preserve patient readmission class ratios",
                "Interprets model coefficients accurately to identify top positive and negative predictors"
            ]
        },
        "quick_reference": {
            "key_terms": [
                "Bias: Systematic error from over-simplified assumptions (causes underfitting)",
                "Variance: Sensitivity to random fluctuations in the training sample (causes overfitting)",
                "L1 Lasso: Absolute weight penalty; performs feature selection by setting weights to 0",
                "L2 Ridge: Squared weight penalty; smoothly shrinks weights to control multicollinearity",
                "Data Leakage: Unintentional sharing of test information with the training pipeline"
            ],
            "formulas_and_rules": [
                "Expected Error = Bias^2 + Variance + Irreducible Noise",
                "Ridge Loss: MSE + lambda * sum(w_j^2)",
                "Lasso Loss: MSE + lambda * sum(|w_j|)",
                "Z-Score: (x - mean) / std"
            ],
            "decision_matrix": [
                "Training error high, Test error high? -> Model has High Bias (Underfit); increase complexity",
                "Training error low, Test error high? -> Model has High Variance (Overfit); add regularization",
                "Many irrelevant features? -> Use L1 Lasso for feature selection",
                "Many correlated features? -> Use L2 Ridge to stabilize coefficients"
            ],
            "takeaways": [
                "Never report training error as proof of model quality.",
                "Always wrap preprocessing and estimators in an sklearn Pipeline to prevent data leakage.",
                "Standardize features before training any regularized linear model."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Machine Learning Workflow, Train/Test Split & Overfitting Intuition",
                "prerequisite_recap": "Covers basic Python data types and simple linear equations (y = mx + b).",
                "explanation_supplement": "Uses everyday analogies (memorizing exam questions vs learning underlying concepts) to explain train/test splits and why memorizing training data fails.",
                "key_additions": [
                    "Train/Test split visual diagram and rationale",
                    "Basic Scikit-Learn fit / predict workflow",
                    "Intuitive definition of overfitting"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "Bias-Variance Tradeoff, L1/L2 Regularization & Pipelines",
                "prerequisite_recap": "Assumes comfort with basic Scikit-Learn fit/predict and metrics.",
                "explanation_supplement": "Covers mathematical formulations of MSE loss, L1 vs L2 penalty geometries, and building leakage-free Scikit-Learn pipelines with cross-validation.",
                "key_additions": [
                    "Mathematical derivation of Bias-Variance decomposition",
                    "L1 Lasso vs L2 Ridge optimization penalty mechanics",
                    "Pipeline and StratifiedKFold implementation"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Convex Optimization, Coordinate Descent, ElasticNet & Bayesian Priors",
                "prerequisite_recap": "Assumes complete familiarity with standard regularized regression and cross-validation.",
                "explanation_supplement": "Explores optimization algorithms (Coordinate Descent for Lasso, Closed-form Normal Equations for Ridge), the Bayesian interpretation of L1/L2 regularization as Laplace vs Gaussian priors, and Double Descent phenomena in modern high-capacity models.",
                "key_additions": [
                    "Subgradient and coordinate descent optimization for non-differentiable L1 penalties",
                    "Bayesian perspective: Gaussian prior (Ridge) vs Laplacian prior (Lasso)",
                    "Double Descent curves in overparameterized deep learning regimes"
                ]
            }
        }
    },

    # =========================================================================
    # 9. Feature Engineering Pipelines
    # =========================================================================
    "feature-engineering-pipelines": {
        "title": "Feature Engineering, Encoding & Transformation Pipelines",
        "concept_name": "Feature Engineering Architecture, Encoding, Scaling & ColumnTransformers",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Architect modular scikit-learn ColumnTransformer pipelines combining distinct numerical, categorical, and text feature transformations",
            "Evaluate categorical encoding strategies: One-Hot, Ordinal, Target Encoding, and Weight of Evidence while avoiding target leakage",
            "Apply non-linear feature transformations (Logarithmic, Box-Cox, Yeo-Johnson) to stabilize variance and normalize skewed features",
            "Engineer interaction terms, polynomial combinations, and domain-informed aggregations without exploding feature dimensionality",
            "Eliminate data leakage during feature preprocessing by strictly computing transformer state on training folds only",
        ],
        "explanation": """### 1. Conceptual Foundation: Why Feature Engineering Drives Model Performance
In applied data science, algorithm selection is rarely the differentiator between a mediocre model and an enterprise-grade solution. The adage *"Better features beat better algorithms"* holds true across tabular domains. Feature engineering is the discipline of transforming raw, heterogeneous operational data (timestamps, categorical strings, continuous measurements, free text) into structured numerical representations that expose maximal predictive signal to downstream machine learning algorithms.

Raw real-world datasets typically present three architectural challenges:
1. **Heterogeneous Column Types**: A single customer record contains numeric balances, nominal categories ('tier': 'gold'), ordinal rankings ('credit_band': 'A'), and timestamps ('last_login').
2. **Non-Normal & Skewed Distributions**: Financial transactions and web traffic exhibit heavy power-law tails that degrade linear and distance-based estimators.
3. **Data Leakage Risks**: Fitting transformations (such as mean imputation or target encoding) across the entire dataset inadvertently injects future target information into training folds.

---

### 2. Categorical Encoding Taxonomy & Tradeoffs

```
+-----------------------------------------------------------------------------------------+
| Nominal (No Order)       | High-Cardinality (ZIP, IDs) | Ordinal (Inherent Order)       |
| -> One-Hot Encoding      | -> Target Encoding          | -> Ordinal Encoding            |
| -> Low cardinality (<15) | -> Regularized / K-Fold     | -> e.g. Low < Med < High       |
+-----------------------------------------------------------------------------------------+
```

#### A. One-Hot Encoding (OHE)
Maps each unique category to an independent binary vector ($[0, 1]$).
* **Strength**: Preserves non-linear categorical distinctions without imposing artificial ordering.
* **Failure Mode**: When applied to high-cardinality features (e.g., 500 ZIP codes), it expands matrix dimensionality catastrophically, inducing the *Curse of Dimensionality* and sparse memory waste. Always set `handle_unknown='ignore'`.

#### B. Target (Mean) Encoding
Replaces each categorical level with the expected value of the target variable $y$ for that level:

$$\\hat{S}_k = \\frac{n_k \\bar{y}_k + m \\cdot \\bar{y}_{\\text{global}}}{n_k + m}$$

Where $n_k$ is the count of observations in category $k$, $\\bar{y}_k$ is the category target mean, $\\bar{y}_{\\text{global}}$ is the overall population mean, and $m$ is a smoothing weight. Smoothing prevents rare categories from memorizing single target outcomes. Target encoding must always be computed out-of-fold to prevent catastrophic target leakage!

---

### 3. Continuous Transformations: Box-Cox & Yeo-Johnson

When numerical variables exhibit severe skewness, linear models, neural networks, and distance-based algorithms (KNN, SVM) suffer because extreme values dominate gradient updates. Power transforms stabilize variance and map distributions closer to a Gaussian bell curve:

#### Box-Cox Transformation (Strictly Positive $x > 0$):
$$x^{(\\lambda)} = \\begin{cases} \\frac{x^\\lambda - 1}{\\lambda} & \\text{if } \\lambda \\ne 0 \\\\ \\ln(x) & \\text{if } \\lambda = 0 \\end{cases}$$

#### Yeo-Johnson Transformation (Supports Zero & Negative Values):
Extends Box-Cox to allow zero and negative numbers, making it the industry standard for financial profit/loss and temperature metrics.""",
        "subtopics": [
            "ColumnTransformer & FeatureUnion Architecture",
            "One-Hot vs. Target vs. Ordinal Encoding",
            "Power Transforms: Box-Cox and Yeo-Johnson",
            "Interaction Features & Polynomial Expansions",
            "Temporal Feature Engineering (Cyclical Sine/Cosine Encoding)",
            "Preventing Target Leakage in Supervised Encoders"
        ],
        "why_it_matters_by_role": {
            "Data Scientist": "Directly responsible for extracting maximum predictive power from raw tabular records before feeding models.",
            "Data Analyst": "Enables engineering meaningful derived metrics, ratios, and cohort flags for downstream reporting.",
            "Python Developer": "Provides the blueprint for implementing clean scikit-learn transformers that run deterministically in production microservices."
        },
        "code_examples": [
            {
                "title": "Production ColumnTransformer for Heterogeneous Features",
                "code": "from sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nimport pandas as pd\n\n# Define feature groups\nnumeric_features = ['age', 'annual_spend', 'tenure_months']\ncategorical_features = ['subscription_tier', 'region']\n\n# Numeric sub-pipeline: Median Imputation + Scaling\nnumeric_transformer = Pipeline([\n    ('imputer', SimpleImputer(strategy='median')),\n    ('scaler', StandardScaler())\n])\n\n# Categorical sub-pipeline: Constant Imputation + One-Hot Encoding\ncategorical_transformer = Pipeline([\n    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),\n    ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))\n])\n\n# Combine into master preprocessor\npreprocessor = ColumnTransformer([\n    ('num', numeric_transformer, numeric_features),\n    ('cat', categorical_transformer, categorical_features)\n], remainder='drop')\n\n# Example usage\ndf = pd.DataFrame({\n    'age': [25, 42, None],\n    'annual_spend': [1200.0, 5400.0, 3100.0],\n    'tenure_months': [12, 48, 24],\n    'subscription_tier': ['Basic', 'Enterprise', 'Pro'],\n    'region': ['US', 'EU', 'US']\n})\nprocessed_data = preprocessor.fit_transform(df)\nprint(f'Processed Feature Matrix Shape: {processed_data.shape}')",
                "explanation": "Applies dedicated, leakage-free transformation sub-pipelines to numeric and categorical columns independently, then concatenates the results.",
                "expected_output": "Processed Feature Matrix Shape: (3, 8)"
            },
            {
                "title": "Cyclical Temporal Feature Engineering (Sine/Cosine Encoding)",
                "code": "import numpy as np\nimport pandas as pd\n\ndef encode_cyclical_time(df: pd.DataFrame, col: str, period: int) -> pd.DataFrame:\n    \"\"\"Encodes periodic temporal attributes (hour of day, month of year) into continuous cyclical signals.\"\"\"\n    df[f'{col}_sin'] = np.sin(2 * np.pi * df[col] / period)\n    df[f'{col}_cos'] = np.cos(2 * np.pi * df[col] / period)\n    return df\n\n# Hour of day (period = 24). Note that 23:00 and 00:00 are naturally continuous!\ntime_df = pd.DataFrame({'hour': [23, 0, 1, 12]})\nencoded_df = encode_cyclical_time(time_df, 'hour', 24)\nprint(encoded_df.round(3))",
                "explanation": "Mapping periodic attributes to sine and cosine prevents artificial discontinuities where hour 23 and hour 0 appear 23 units apart instead of 1 unit apart.",
                "expected_output": "   hour  hour_sin  hour_cos\n0    23    -0.259     0.966\n1     0     0.000     1.000\n2     1     0.259     0.966\n3    12     0.000    -1.000"
            }
        ],
        "worked_example": {
            "scenario": "An insurance pricing team is predicting auto collision risk. The dataset contains policyholder age, annual mileage, vehicle category, and driving violation count. The vehicle category feature has 45 distinct types, and annual mileage has severe right-skew.",
            "problem": "One-hot encoding vehicle category creates 45 sparse columns, and raw annual mileage extreme values distort linear risk models.",
            "approach": "1. Apply PowerTransformer (Yeo-Johnson) to normalize annual mileage.\n2. Apply TargetEncoder with smoothing to vehicle category to compress it into a single predictive continuous column.\n3. Create an interaction feature: violations_per_year_driving = violation_count / (age - 16).\n4. Package into an end-to-end Pipeline.",
            "solution": "import pandas as pd\nimport numpy as np\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import PowerTransformer, TargetEncoder\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.linear_model import Ridge\n\ndata = pd.DataFrame({\n    'age': [35, 50, 22, 65],\n    'mileage': [12000, 45000, 8000, 95000],\n    'violations': [1, 0, 3, 0],\n    'vehicle_type': ['Sedan', 'Commercial_Van', 'Coupe', 'SUV'],\n    'claim_cost': [450, 3200, 5800, 600]\n})\n\n# 1. Domain interaction term\ndata['violations_per_year'] = data['violations'] / (data['age'] - 16)\n\nX = data[['mileage', 'violations_per_year', 'vehicle_type']]\ny = data['claim_cost']\n\npreprocessor = ColumnTransformer([\n    ('num', PowerTransformer(method='yeo-johnson'), ['mileage', 'violations_per_year']),\n    ('cat', TargetEncoder(smooth='auto', cv=2), ['vehicle_type'])\n])\n\nfull_pipe = Pipeline([\n    ('prep', preprocessor),\n    ('model', Ridge(alpha=1.0))\n])\n\nfull_pipe.fit(X, y)\nprint('Pipeline successfully fitted without leakage.')",
            "result": "Pipeline successfully fitted without leakage. The 45 vehicle categories are compressed into a single smoothed target signal without dimensionality explosion.",
            "why_it_works": "PowerTransformer normalizes mileage skewness, TargetEncoder encodes high-cardinality vehicle types using out-of-fold target averages, and the domain interaction feature captures driver risk density.",
            "alternative": "Use CatBoost, which handles categorical features natively using ordered target encoding during tree splits."
        },
        "common_mistakes": [
            {
                "title": "Mistake 1 — Target Encoding on the Entire Dataset (Severe Target Leakage)",
                "what_it_looks_like": "Calculating `category_means = df.groupby('category')['target'].mean()` and mapping it back before train/test splitting.",
                "why_it_happens": "Simple to code in two lines of Pandas.",
                "how_to_fix_it": "This leaks the test set labels directly into the feature values, causing catastrophic overfitting. Always use Scikit-Learn's `TargetEncoder(cv=5)` inside a Pipeline to compute out-of-fold target statistics strictly on training folds."
            },
            {
                "title": "Mistake 2 — One-Hot Encoding High-Cardinality Columns Unconstrained",
                "what_it_looks_like": "Applying `pd.get_dummies(df, columns=['zip_code', 'merchant_id'])` producing 8,000 columns from 5,000 rows.",
                "why_it_happens": "Not checking cardinality before encoding.",
                "how_to_fix_it": "High-cardinality one-hot encoding causes memory bloat and models to overfit rare categories. Use frequency encoding, target encoding, or group rare categories into an 'Other' bucket using `min_frequency`."
            },
            {
                "title": "Mistake 3 — Forgetting `handle_unknown='ignore'` in OneHotEncoder",
                "what_it_looks_like": "Deploying a model that crashes with `ValueError: Found unknown categories [X] in column 0 during transform`.",
                "why_it_happens": "Default Scikit-Learn settings raise errors when test or production data contains unseen categories.",
                "how_to_fix_it": "Always instantiate `OneHotEncoder(handle_unknown='ignore')` for production pipelines so novel categories are safely encoded as all zeros."
            }
        ],
        "guided_practice": {
            "prompt": "Construct a ColumnTransformer that applies StandardScaler to `['income', 'credit_score']` and OneHotEncoder(handle_unknown='ignore') to `['home_ownership']`. Fit and transform a sample customer DataFrame.",
            "starter_code": "import pandas as pd\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\n\ndf = pd.DataFrame({\n    'income': [50000, 85000, 32000],\n    'credit_score': [710, 680, 790],\n    'home_ownership': ['RENT', 'MORTGAGE', 'RENT']\n})\n\n# Construct preprocessor\n# Transform df and print result\n",
            "solution": "import pandas as pd\nfrom sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\n\ndf = pd.DataFrame({\n    'income': [50000, 85000, 32000],\n    'credit_score': [710, 680, 790],\n    'home_ownership': ['RENT', 'MORTGAGE', 'RENT']\n})\n\npreprocessor = ColumnTransformer([\n    ('num', StandardScaler(), ['income', 'credit_score']),\n    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['home_ownership'])\n])\n\nresult = preprocessor.fit_transform(df)\nprint(result.round(3))",
            "hints": [
                "Define numeric features as a list: ['income', 'credit_score'].",
                "Define categorical features: ['home_ownership'].",
                "Use ColumnTransformer([('num', StandardScaler(), num_cols), ('cat', OneHotEncoder(...), cat_cols)]).",
                "Call preprocessor.fit_transform(df)."
            ]
        },
        "independent_practice": {
            "prompt": "Write a custom Scikit-Learn compatible transformer class `BinnedFeatureTransformer(columns, n_bins)` using BaseEstimator and TransformerMixin that discretizes specified numeric columns into equal-frequency quantiles using `pd.qcut`.",
            "starter_code": "from sklearn.base import BaseEstimator, TransformerMixin\nimport pandas as pd\n\nclass BinnedFeatureTransformer(BaseEstimator, TransformerMixin):\n    def __init__(self, columns: list, n_bins: int = 4):\n        self.columns = columns\n        self.n_bins = n_bins\n        \n    def fit(self, X, y=None):\n        # Implement here\n        return self\n        \n    def transform(self, X):\n        # Implement here\n        pass\n",
            "solution": "from sklearn.base import BaseEstimator, TransformerMixin\nimport pandas as pd\nimport numpy as np\n\nclass BinnedFeatureTransformer(BaseEstimator, TransformerMixin):\n    def __init__(self, columns: list, n_bins: int = 4):\n        self.columns = columns\n        self.n_bins = n_bins\n        self.bin_edges_ = {}\n        \n    def fit(self, X, y=None):\n        X_df = pd.DataFrame(X)\n        for col in self.columns:\n            _, edges = pd.qcut(X_df[col], q=self.n_bins, retbins=True, duplicates='drop')\n            self.bin_edges_[col] = edges\n        return self\n        \n    def transform(self, X):\n        X_out = pd.DataFrame(X).copy()\n        for col in self.columns:\n            edges = self.bin_edges_[col]\n            # Extend edges to -inf, +inf to handle unseen out-of-range test values\n            edges[0] = -np.inf\n            edges[-1] = np.inf\n            X_out[f'{col}_binned'] = pd.cut(X_out[col], bins=edges, labels=False, include_lowest=True)\n        return X_out",
            "evaluation_criteria": [
                "Inherits properly from BaseEstimator and TransformerMixin",
                "Stores quantile bin edges during fit() without referencing test data",
                "Applies pre-computed bin edges safely during transform()",
                "Handles boundary cases with infinite extensions"
            ]
        },
        "concept_check": [
            {
                "question": "Why should OneHotEncoder(handle_unknown='ignore') be specified in production preprocessing pipelines?",
                "options": [
                    "To prevent runtime crashes when production input contains novel categorical levels not present in training data",
                    "To automatically impute missing numeric values with the median",
                    "To convert categorical strings into natural language embeddings",
                    "To force all coefficients to equal 1.0"
                ],
                "correct_index": 0,
                "explanation": "In production, real users frequently provide new, rare, or misspelled categories not seen during training. Setting handle_unknown='ignore' outputs an all-zero vector for unseen categories instead of throwing a fatal ValueError."
            },
            {
                "question": "What is the primary danger of using Target (Mean) Encoding without out-of-fold cross-validation or smoothing?",
                "options": [
                    "Target leakage, where rare categories memorize their exact target labels, causing catastrophic overfitting",
                    "The encoded matrix becomes 100 times larger than One-Hot Encoding",
                    "The model is restricted to predicting only integer classes",
                    "Target encoding only works on continuous target variables"
                ],
                "correct_index": 0,
                "explanation": "If a rare category appears only once in the dataset with target=1, a naive target encoder assigns it 1.0. The model learns to rely heavily on this single observation, failing completely on new data."
            },
            {
                "question": "Why is cyclical encoding (sine and cosine transforms) necessary for time features like 'hour of day' (0-23)?",
                "options": [
                    "It ensures hour 23 and hour 0 are mathematically continuous and close to each other in vector space",
                    "It eliminates the need for neural network activation functions",
                    "It transforms the time feature into an integer between 0 and 100",
                    "It automatically accounts for daylight saving time adjustments"
                ],
                "correct_index": 0,
                "explanation": "In raw integer representation, 23:00 and 00:00 have a difference of 23 units despite being only 1 hour apart. Sine/cosine projection maps time to a 2D circle where 23:00 and 00:00 sit adjacent to each other."
            }
        ],
        "applied_task": {
            "title": "Production Real Estate Valuation Feature Engineering Pipeline",
            "context": "You are building an automated property valuation model for a digital mortgage platform. The raw database contains property age, square footage, neighborhood (180 distinct communities), school rating (1-10 ordinal), and transaction month.",
            "deliverables": [
                "Scikit-Learn ColumnTransformer handling numeric scaling, cyclical month encoding, and target encoding for neighborhood",
                "Domain feature engineering function generating 'price_per_sqft' proxy features and square_footage-to-age interaction ratios",
                "End-to-end evaluation comparing RMSE of baseline raw features vs engineered feature pipeline"
            ],
            "rubric": [
                "Zero data leakage: all encoders and scalers embedded in Pipeline",
                "Appropriate encoding choices: cyclical for month, smoothed target for neighborhood",
                "Clear documentation of engineered interaction features"
            ]
        },
        "quick_reference": {
            "key_terms": [
                "ColumnTransformer: Scikit-learn container allowing different preprocessing pipelines for different columns",
                "One-Hot Encoding: Mapping nominal categories to binary vectors",
                "Target Encoding: Replacing categories with regularized expected target values",
                "Power Transform: Non-linear mapping (Yeo-Johnson, Box-Cox) to stabilize variance and normalize skew",
                "Target Leakage: Injecting target information into input features during preprocessing"
            ],
            "formulas_and_rules": [
                "Box-Cox: x^(lambda) transformation for positive values",
                "Yeo-Johnson: Power transform supporting positive, zero, and negative values",
                "Cyclical Sine: sin(2 * pi * x / period)",
                "Cyclical Cosine: cos(2 * pi * x / period)"
            ],
            "decision_matrix": [
                "Low cardinality (<15 categories)? -> Use OneHotEncoder(handle_unknown='ignore')",
                "High cardinality (>50 categories)? -> Use TargetEncoder(cv=5, smooth='auto')",
                "Continuous feature with severe skewness? -> Use PowerTransformer(method='yeo-johnson')",
                "Periodic temporal feature (hours, months)? -> Use Sine/Cosine cyclical projection"
            ],
            "takeaways": [
                "Feature engineering delivers the highest ROI on model accuracy.",
                "Always embed transformers inside an sklearn Pipeline to prevent test leakage.",
                "Never use naive target encoding without regularization or out-of-fold cross-validation."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Data Types, One-Hot Encoding Basics & Simple Scaling",
                "prerequisite_recap": "Covers distinguishing numeric columns from string categories.",
                "explanation_supplement": "Explains why machine learning models require numerical matrices and demonstrates One-Hot Encoding and StandardScaler step-by-step.",
                "key_additions": [
                    "Why algorithms cannot process raw text categories",
                    "One-Hot Encoding walkthrough with small tables",
                    "StandardScaler vs MinMaxScaler comparison"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "ColumnTransformer, Power Transforms & Target Encoding",
                "prerequisite_recap": "Assumes comfort building basic Scikit-Learn models and train/test splits.",
                "explanation_supplement": "Covers modular ColumnTransformer architectures, Box-Cox/Yeo-Johnson power transforms, and out-of-fold TargetEncoder implementation.",
                "key_additions": [
                    "ColumnTransformer multi-pipeline architecture",
                    "Yeo-Johnson power transform math and implementation",
                    "Target encoding smoothing formulations"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Automated Feature Synthesis, Feature Importance Pruning & Embedding Layers",
                "prerequisite_recap": "Assumes complete familiarity with ColumnTransformers and target encoding.",
                "explanation_supplement": "Explores deep entity embeddings for categorical features, automated genetic feature synthesis (Symbolic Regression), and pruning collinear engineered features using SHAP value clustering.",
                "key_additions": [
                    "Entity embeddings for ultra-high cardinality categories",
                    "SHAP-based collinearity feature elimination",
                    "Real-time feature store integration patterns"
                ]
            }
        }
    },

    # =========================================================================
    # 10. Model Evaluation Metrics
    # =========================================================================
    "model-evaluation-metrics": {
        "title": "Model Evaluation, Cross-Validation & Metric Optimization",
        "concept_name": "Model Evaluation Metrics, Confusion Matrix, Precision/Recall & ROC-AUC",
        "difficulty": "Intermediate",
        "estimated_minutes": 35,
        "learning_objectives": [
            "Deconstruct the Confusion Matrix into True Positives, False Positives, True Negatives, and False Negatives",
            "Balance the Precision vs Recall tradeoff and select the optimal decision threshold for high-stakes business costs",
            "Interpret Receiver Operating Characteristic (ROC-AUC) and Precision-Recall (PR-AUC) curves across imbalanced distributions",
            "Calculate regression metrics: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and R-squared with domain interpretation",
            "Align algorithmic evaluation metrics with operational enterprise KPIs and financial utility functions",
        ],
        "explanation": """### 1. Conceptual Foundation: Beyond Naive Accuracy
In applied machine learning, evaluating a model simply by its overall accuracy (percentage of correct predictions) is one of the most dangerous anti-patterns in data science. In real-world enterprise scenarios—such as credit card fraud detection, cancer screening, factory defect triage, and customer churn—target classes are inherently imbalanced.

Consider an e-commerce platform processing 1,000,000 transactions daily, where 1,000 transactions (0.1%) are fraudulent:
* A completely useless model that classifies **every single transaction as legitimate** achieves **99.9% accuracy**.
* Despite near-perfect accuracy, the business incurs 100% of the fraud losses.

To evaluate models rigorously, practitioners deconstruct classification outcomes using the **Confusion Matrix** and choose metrics aligned with the asymmetric costs of errors.

---

### 2. The Binary Confusion Matrix & Derived Metrics

```
                            ACTUAL CLASS
                     Positive (1)     Negative (0)
                  +----------------+----------------+
    Positive (1)  | True Positive  | False Positive |  <-- Precision = TP / (TP + FP)
                  |     (TP)       |  (FP, Type I)  |
PREDICTED         +----------------+----------------+
CLASS             | False Negative | True Negative  |
    Negative (0)  |  (FN, Type II) |     (TN)       |
                  +----------------+----------------+
                          ^
                          |
             Recall = TP / (TP + FN)
             (Sensitivity / True Positive Rate)
```

#### A. Precision (Quality of Positive Alarm)
$$\\text{Precision} = \\frac{\\text{TP}}{\\text{TP} + \\text{FP}}$$
* **Core Question**: *"Of all instances the model flagged as positive, what percentage was actually positive?"*
* **When to prioritize**: When False Positives are expensive (e.g., spam filtering, where legitimate emails discarded in spam folders destroy user trust).

#### B. Recall / Sensitivity (Coverage of Actual Positives)
$$\\text{Recall} = \\frac{\\text{TP}}{\\text{TP} + \\text{FN}}$$
* **Core Question**: *"Of all actual positive cases in reality, what percentage did the model successfully catch?"*
* **When to prioritize**: When False Negatives are catastrophic (e.g., medical diagnostics, financial fraud, cybersecurity intrusion).

#### C. F1-Score & F-Beta (Harmonic Balance)
The arithmetic mean of Precision and Recall is misleading: if a model has Precision = 1.0 and Recall = 0.0, the arithmetic mean is 0.50. The **Harmonic Mean** penalizes extreme imbalance:

$$F_1 = 2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}} = \\frac{2 \\text{TP}}{2 \\text{TP} + \\text{FP} + \\text{FN}}$$

When business priorities skew toward recall over precision (or vice versa), the generalized $F_\\beta$ score is used:

$$F_\\beta = (1 + \\beta^2) \\frac{\\text{Precision} \\times \\text{Recall}}{(\\beta^2 \\times \\text{Precision}) + \\text{Recall}}$$

For fraud detection, $\\beta = 2$ ($F_2$-score) weights recall twice as heavily as precision.

---

### 3. Discrimination Curves: ROC-AUC vs. Precision-Recall AUC

Classification models do not output binary classes directly; they output a calibrated probability estimate $P(Y=1|X) \\in [0, 1]$. A decision threshold $\\tau$ (defaulting to 0.50) maps probabilities to binary decisions.

#### A. Receiver Operating Characteristic (ROC-AUC)
Plots **True Positive Rate** (Recall) against **False Positive Rate** ($FPR = FP / (FP + TN)$) across all possible thresholds $\\tau \\in [0, 1]$:
* **Interpretation**: The probability that the model ranks a randomly chosen positive instance higher than a randomly chosen negative instance.
* A random guessing model yields $AUC = 0.50$; a perfect classifier yields $AUC = 1.0$.
* **Caveat**: When negative cases outnumber positives 100:1, $FPR$ remains deceptively small even with large numbers of False Positives.

#### B. Precision-Recall Curve (PR-AUC)
Plots **Precision** against **Recall** across all thresholds:
* **The Gold Standard for Imbalanced Data**: Because PR curves ignore True Negatives ($TN$), they do not become deceptively optimistic on heavily imbalanced datasets. Baseline random guessing is equal to the positive prevalence rate (e.g., 0.01).""",
        "subtopics": [
            "The Confusion Matrix Anatomy (TP, FP, TN, FN)",
            "Precision vs. Recall Tradeoff & Decision Threshold Tuning",
            "F1-Score and Asymmetric F-Beta Optimization",
            "ROC-AUC vs. Precision-Recall (PR) Curves for Imbalanced Classes",
            "Continuous Regression Metrics: MAE, MSE, RMSE, and MAPE",
            "Aligning Algorithmic Metrics with Business Cost Matrices"
        ],
        "why_it_matters_by_role": {
            "Data Scientist": "Crucial for defending model reliability, calibrating classification thresholds, and avoiding costly misclassifications in production.",
            "Data Analyst": "Enables evaluating marketing campaigns, customer segmentation models, and reporting true conversion accuracy to business leaders.",
            "Python Developer": "Necessary for writing automated model regression tests, continuous evaluation monitors, and alerting on accuracy drift in production."
        },
        "code_examples": [
            {
                "title": "Comprehensive Classification Report & Threshold Tuning",
                "code": "from sklearn.metrics import classification_report, precision_recall_curve, roc_auc_score\nimport numpy as np\n\n# Simulated ground truth and model predicted probabilities\ny_true = np.array([0, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0])\ny_prob = np.array([0.1, 0.2, 0.15, 0.35, 0.85, 0.25, 0.65, 0.45, 0.2, 0.75, 0.9, 0.3, 0.8, 0.1, 0.4])\n\n# Standard threshold 0.50\ny_pred_default = (y_prob >= 0.50).astype(int)\nprint('=== Performance at Standard Threshold (0.50) ===')\nprint(classification_report(y_true, y_pred_default, target_names=['Negative', 'Positive']))\n\n# Compute Area Under ROC\nroc_auc = roc_auc_score(y_true, y_prob)\nprint(f'ROC-AUC Score: {roc_auc:.4f}')",
                "explanation": "Generates precision, recall, F1-score, and support for each class alongside ROC-AUC.",
                "expected_output": "=== Performance at Standard Threshold (0.50) ===\n              precision    recall  f1-score   support\n\n    Negative       1.00      1.00      1.00        10\n    Positive       1.00      1.00      1.00         5\n\n    accuracy                           1.00        15\n   macro avg       1.00      1.00      1.00        15\nweighted avg       1.00      1.00      1.00        15\n\nROC-AUC Score: 1.0000"
            },
            {
                "title": "Threshold Calibration Based on Financial Cost Matrix",
                "code": "def find_optimal_threshold(y_true, y_prob, cost_fp=50, cost_fn=500):\n    \"\"\"Finds the classification threshold that minimizes total financial loss.\"\"\"\n    thresholds = np.linspace(0.01, 0.99, 100)\n    best_thresh = 0.5\n    min_total_cost = float('inf')\n    \n    for t in thresholds:\n        y_pred = (y_prob >= t).astype(int)\n        fp = np.sum((y_pred == 1) & (y_true == 0))\n        fn = np.sum((y_pred == 0) & (y_true == 1))\n        total_cost = (fp * cost_fp) + (fn * cost_fn)\n        \n        if total_cost < min_total_cost:\n            min_total_cost = total_cost\n            best_thresh = t\n            \n    return best_thresh, min_total_cost\n\nopt_thresh, min_cost = find_optimal_threshold(y_true, y_prob, cost_fp=25, cost_fn=500)\nprint(f'Optimal Threshold: {opt_thresh:.2f} | Minimized Cost: ${min_cost}')",
                "explanation": "Because a False Negative (missed fraud) costs $500 while a False Positive (manual review) costs $25, lowering the threshold catches more fraud and minimizes dollar loss.",
                "expected_output": "Optimal Threshold: 0.46 | Minimized Cost: $0"
            }
        ],
        "worked_example": {
            "scenario": "A FinTech fraud engine evaluates 50,000 credit card transactions per hour. Fraud represents 0.2% of traffic. Missing a fraudulent transaction costs the company an average of $800 in chargebacks. Sending a transaction for manual review costs $15 in analyst time. The standard 0.50 threshold yields high precision but misses 35% of fraud.",
            "problem": "Using the default 0.50 decision threshold results in 35 False Negatives, costing $28,000 per hour in unrecovered fraud losses.",
            "approach": "1. Plot Precision-Recall curve to inspect model discrimination under class imbalance.\n2. Iterate through probability thresholds from 0.05 to 0.50.\n3. Compute total financial cost: Total Cost = (FP * $15) + (FN * $800).\n4. Select the cost-minimizing threshold.",
            "solution": "import numpy as np\nfrom sklearn.metrics import confusion_matrix\n\n# Simulated test set: 10,000 transactions, 20 actual fraud cases (0.2% prevalence)\nnp.random.seed(42)\ny_true = np.zeros(10000, dtype=int)\ny_true[:20] = 1\nnp.random.shuffle(y_true)\n\n# Model probability generator with good signal\ny_prob = np.random.beta(0.5, 20, size=10000)\ny_prob[y_true == 1] = np.random.beta(5, 2, size=20)\n\n# Evaluate threshold 0.50 vs 0.15\nfor thresh in [0.50, 0.15]:\n    y_pred = (y_prob >= thresh).astype(int)\n    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()\n    cost = (fp * 15) + (fn * 800)\n    recall = tp / (tp + fn)\n    print(f'Threshold {thresh:.2f} -> TP: {tp}, FP: {fp}, FN: {fn} | Recall: {recall:.1%} | Total Loss: ${cost:,}')",
            "result": "Threshold 0.50 -> TP: 14, FP: 2, FN: 6 | Recall: 70.0% | Total Loss: $4,830\nThreshold 0.15 -> TP: 19, FP: 28, FN: 1 | Recall: 95.0% | Total Loss: $1,220",
            "why_it_works": "Lowering the threshold from 0.50 to 0.15 increases False Positives from 2 to 28 (costing an extra $390 in review fees), but catches 5 additional fraud cases (saving $4,000 in chargebacks), reducing net loss by 74%.",
            "alternative": "Train the model directly using class-weighted loss (`class_weight='balanced'`) to penalize minority misclassifications during gradient descent."
        },
        "common_mistakes": [
            {
                "title": "Mistake 1 — Relying on Overall Accuracy for Imbalanced Problems",
                "what_it_looks_like": "Reporting '99.5% accuracy' on an anomaly detection problem with 0.5% anomalies.",
                "why_it_happens": "Accuracy is the most familiar metric to non-technical stakeholders.",
                "how_to_fix_it": "Always report balanced metrics: Precision, Recall, F1-Score, and PR-AUC. Never use raw accuracy as the primary evaluation KPI for imbalanced classes."
            },
            {
                "title": "Mistake 2 — Assuming 0.50 is the Mandatory Classification Threshold",
                "what_it_looks_like": "Accepting whatever `model.predict(X)` outputs without tuning probability thresholds.",
                "why_it_happens": "0.50 is the hardcoded default in `predict()` across Scikit-Learn estimators.",
                "how_to_fix_it": "0.50 is mathematically arbitrary. In high-cost FN scenarios (fraud, healthcare), calibrate the threshold downward (e.g., 0.15); in high-cost FP scenarios (spam), calibrate upward (e.g., 0.85)."
            },
            {
                "title": "Mistake 3 — Using ROC-AUC Instead of PR-AUC on Highly Imbalanced Data",
                "what_it_looks_like": "Presenting an ROC-AUC of 0.94 on a dataset with 1:1,000 positive ratio while the model produces 500 False Positives for every 1 True Positive.",
                "why_it_happens": "ROC-AUC divides FP by the massive pool of True Negatives, making False Positive Rate look artificially near zero.",
                "how_to_fix_it": "Use Precision-Recall AUC (Average Precision) whenever positive class prevalence is under 5%."
            }
        ],
        "guided_practice": {
            "prompt": "Given true labels `y_true = [1, 0, 1, 1, 0, 0, 1, 0]` and predicted labels `y_pred = [1, 0, 1, 0, 0, 1, 1, 0]`, calculate the confusion matrix components (TP, FP, TN, FN), and compute Precision and Recall manually.",
            "starter_code": "y_true = [1, 0, 1, 1, 0, 0, 1, 0]\ny_pred = [1, 0, 1, 0, 0, 1, 1, 0]\n\n# Calculate TP, FP, TN, FN\n# Compute precision = TP / (TP + FP)\n# Compute recall = TP / (TP + FN)\n",
            "solution": "y_true = [1, 0, 1, 1, 0, 0, 1, 0]\ny_pred = [1, 0, 1, 0, 0, 1, 1, 0]\n\ntp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 1)\nfp = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 1)\ntn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 0 and yp == 0)\nfn = sum(1 for yt, yp in zip(y_true, y_pred) if yt == 1 and yp == 0)\n\nprecision = tp / (tp + fp) if (tp + fp) > 0 else 0\nrecall = tp / (tp + fn) if (tp + fn) > 0 else 0\n\nprint(f'TP: {tp}, FP: {fp}, TN: {tn}, FN: {fn}')\nprint(f'Precision: {precision:.3f}, Recall: {recall:.3f}')",
            "hints": [
                "TP: y_true=1 and y_pred=1 (count: 3).",
                "FP: y_true=0 and y_pred=1 (count: 1).",
                "FN: y_true=1 and y_pred=0 (count: 1).",
                "TN: y_true=0 and y_pred=0 (count: 3).",
                "Precision = 3 / (3 + 1) = 0.75; Recall = 3 / (3 + 1) = 0.75."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function `calculate_regression_metrics(y_true, y_pred)` that returns a dictionary containing MAE, RMSE, and R-squared without relying on external libraries besides standard math and numpy.",
            "starter_code": "import numpy as np\n\ndef calculate_regression_metrics(y_true: list, y_pred: list) -> dict:\n    # Implement here\n    pass\n",
            "solution": "import numpy as np\n\ndef calculate_regression_metrics(y_true: list, y_pred: list) -> dict:\n    yt = np.array(y_true, dtype=float)\n    yp = np.array(y_pred, dtype=float)\n    \n    errors = yt - yp\n    mae = np.mean(np.abs(errors))\n    mse = np.mean(errors ** 2)\n    rmse = np.sqrt(mse)\n    \n    ss_res = np.sum(errors ** 2)\n    ss_tot = np.sum((yt - np.mean(yt)) ** 2)\n    r2 = 1.0 - (ss_res / ss_tot) if ss_tot != 0 else 0.0\n    \n    return {\n        'mae': round(float(mae), 4),\n        'rmse': round(float(rmse), 4),\n        'r2': round(float(r2), 4)\n    }",
            "evaluation_criteria": [
                "Correct mathematical implementation of MAE using np.abs()",
                "Correct RMSE using np.sqrt(np.mean(errors ** 2))",
                "Correct R2 using 1 - (ss_res / ss_tot)",
                "Handles division by zero edge cases safely"
            ]
        },
        "concept_check": [
            {
                "question": "In a cancer detection model where failing to identify a malignant tumor can lead to patient death, which metric should be maximized?",
                "options": [
                    "Recall (Sensitivity), to minimize False Negatives",
                    "Precision, to eliminate False Positives",
                    "Specificity, to ensure healthy patients are accurately diagnosed",
                    "Raw Accuracy across all patients"
                ],
                "correct_index": 0,
                "explanation": "A False Negative means a patient with cancer is told they are healthy, delaying treatment with life-threatening consequences. Maximizing Recall ensures nearly all actual cancer cases are identified for further biopsy."
            },
            {
                "question": "What is the primary advantage of the Precision-Recall (PR) Curve over the ROC Curve when evaluating fraud detection models with 0.1% positive prevalence?",
                "options": [
                    "PR curves focus exclusively on minority class predictions and are not distorted by a massive pool of True Negatives",
                    "PR curves are faster to compute by an order of magnitude",
                    "PR curves always yield a score between 0.90 and 1.00",
                    "ROC curves cannot be plotted if the dataset has fewer than 100,000 rows"
                ],
                "correct_index": 0,
                "explanation": "In ROC curves, the False Positive Rate denominator is (FP + TN). When TN is 999,000, even 1,000 False Positives produce an FPR of only ~0.001, making the model look deceptively near-perfect. PR curves evaluate Precision (TP / (TP + FP)) directly."
            },
            {
                "question": "Why is the harmonic mean used in the F1-Score instead of the arithmetic mean?",
                "options": [
                    "The harmonic mean drops toward zero if either Precision or Recall is low, preventing extreme imbalance from looking successful",
                    "The arithmetic mean cannot handle floating point numbers",
                    "The harmonic mean produces a linear scale between 0 and 100",
                    "The harmonic mean is required by SQL databases"
                ],
                "correct_index": 0,
                "explanation": "If a model predicts every transaction as positive, it achieves Recall = 1.0, but Precision = 0.01. The arithmetic mean would be ~0.505 (misleadingly moderate). The harmonic mean evaluates to ~0.02, correctly reflecting a poor model."
            }
        ],
        "applied_task": {
            "title": "FinTech Loan Default Risk Threshold Optimization",
            "context": "You are the Lead Risk Modeler for an online lending platform. Your team has trained a Gradient Boosting model predicting loan default probability on 25,000 loan applications. Each approved defaulted loan costs the bank $4,500, while rejecting a creditworthy borrower loses $350 in expected interest revenue.",
            "deliverables": [
                "Precision-Recall and ROC-AUC curve analysis across probability thresholds from 0.01 to 0.90",
                "Financial utility optimization curve identifying the exact probability threshold that maximizes net bank profitability",
                "Executive memo explaining why the traditional 0.50 threshold was suboptimal and presenting the expected quarterly revenue gains from the calibrated threshold"
            ],
            "rubric": [
                "Calculates cost matrix accurately ($4500 FN vs $350 FP)",
                "Selects optimal threshold based on minimum cost / maximum profit",
                "Delivers clear business-oriented justification to executive leadership"
            ]
        },
        "quick_reference": {
            "key_terms": [
                "True Positive (TP): Correctly identified positive case",
                "False Positive (FP): Type I error; negative case falsely alarmed as positive",
                "False Negative (FN): Type II error; actual positive case missed by the model",
                "Precision: TP / (TP + FP); accuracy of positive predictions",
                "Recall: TP / (TP + FN); percentage of actual positives captured",
                "PR-AUC: Area under Precision-Recall curve; best metric for extreme class imbalance"
            ],
            "formulas_and_rules": [
                "Precision = TP / (TP + FP)",
                "Recall = TP / (TP + FN)",
                "F1-Score = 2 * (Precision * Recall) / (Precision + Recall)",
                "RMSE = sqrt(mean((y_true - y_pred)^2))",
                "MAE = mean(|y_true - y_pred|)"
            ],
            "decision_matrix": [
                "False Negatives are life-threatening/costly (cancer, fraud)? -> Optimize for Recall; lower threshold",
                "False Positives are annoying/costly (spam, false arrest)? -> Optimize for Precision; raise threshold",
                "Class balance is extreme (<5% positives)? -> Use PR-AUC instead of ROC-AUC",
                "Regression with large outlier penalties? -> Use RMSE over MAE"
            ],
            "takeaways": [
                "Never rely on accuracy alone for imbalanced datasets.",
                "The 0.50 classification threshold is merely a convention, not an optimal choice.",
                "Always tie metric optimization back to real business dollars and error costs."
            ]
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Confusion Matrix Basics & Precision vs Recall Intuition",
                "prerequisite_recap": "Covers basic percentages and binary classification concepts.",
                "explanation_supplement": "Uses the airport metal detector and smoke alarm analogies to explain True Positives, False Alarms (FP), and Missed Threats (FN).",
                "key_additions": [
                    "Smoke alarm analogy of Precision vs Recall",
                    "Simple 2x2 confusion matrix grid diagram",
                    "Why 99% accuracy can be misleading"
                ]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "F1/F-Beta, ROC-AUC, PR-AUC & Threshold Calibration",
                "prerequisite_recap": "Assumes comfort with basic confusion matrix calculations.",
                "explanation_supplement": "Covers probability thresholds, plotting ROC vs PR curves, and calculating financial utility cost curves using Scikit-Learn.",
                "key_additions": [
                    "Precision-Recall vs ROC curve mathematical comparison",
                    "Threshold tuning code implementation",
                    "F-Beta asymmetric weighting"
                ]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Probability Calibration (Brier Score, Platt Scaling) & Multi-Class Cost Matrices",
                "prerequisite_recap": "Assumes complete mastery of ROC/PR curves and threshold calibration.",
                "explanation_supplement": "Explores probability calibration (Platt Scaling, Isotonic Regression), evaluating predicted confidence with Brier Score, and multi-class Bayesian decision theory under arbitrary loss matrices.",
                "key_additions": [
                    "Isotonic regression and Platt scaling for probability calibration",
                    "Brier score decomposition (reliability, resolution, uncertainty)",
                    "Bayesian decision theory under cost asymmetry"
                ]
            }
        }
    }
}
