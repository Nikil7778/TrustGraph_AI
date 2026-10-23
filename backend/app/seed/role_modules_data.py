"""
Role-Specific Modular Learning Units & Authoritative Resource Registry (Phase 20).
Defines comprehensive, structured curriculum modules for:
- Data Scientist (Feature Engineering, Model Evaluation)
- Python Developer (Python Core, OOP Architecture, Error Handling, REST APIs, FastAPI, PyTest, Docker)
- Data Analyst (Power BI & DAX Modeling)
Also defines the zero-hallucination, verified external learning resources registry.
"""
from typing import List, Dict, Any

ADDITIONAL_LEARNING_MODULES_SEED: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 7. Data Analyst — Power BI & DAX Modeling
    # -------------------------------------------------------------------------
    {
        "slug": "power-bi-dax-modeling",
        "skill_name": "Power BI",
        "title": "Business Intelligence, DAX Modeling & Semantic Layers",
        "concept_name": "DAX Measures, Filter Context & Dimensional Modeling",
        "difficulty": "Intermediate",
        "estimated_minutes": 30,
        "order_index": 7,
        "prerequisite_concept_slugs": "sql-fundamentals",
        "target_role_name": "Data Analyst",
        "learning_objectives": [
            "Architect star-schema semantic data models distinguishing Fact tables from Conformed Dimensions",
            "Master DAX calculation engine mechanics: Row Context vs Filter Context and Context Transition",
            "Formulate robust executive KPIs using CALCULATE, FILTER, DIVIDE, and Time-Intelligence functions",
        ],
        "explanation": """### Dimensional Modeling & The DAX Engine
In enterprise business intelligence, relational databases are rarely visualized directly. Instead, Data Analysts transform transactional tables into a **Star Schema** consisting of:
1. **Fact Tables**: Dense transactional tables containing numerical measurements (e.g., `Sales`, `Order_Items`).
2. **Dimension Tables**: Descriptive lookup tables providing analytical context (e.g., `Customers`, `Products`, `Calendar`).

#### Row Context vs. Filter Context:
* **Row Context**: Exists during iteration (e.g., Calculated Columns or `SUMX`). It knows only the values in the current row.
* **Filter Context**: The active set of filters applied by report slicers, visuals, and DAX expressions. Measures are evaluated under Filter Context.

#### The Role of CALCULATE:
`CALCULATE(<expression>, <filter1>, <filter2>, ...)` is the single most vital function in DAX. It is the only function that can **modify** or **override** the incoming Filter Context. When called inside a Row Context, it triggers **Context Transition**, turning row values into active filters.

#### Safe Division in DAX:
Always use `DIVIDE(Numerator, Denominator, AlternateResult)` instead of the `/` operator to handle division by zero safely without errors.""",
        "key_rules": "- Build 1-to-many single-directional relationships from Dimension to Fact\n- Always calculate ratios using DIVIDE(), never the forward slash operator\n- Use CALCULATE to override or augment visual filter contexts",
        "common_mistakes": "- Creating bidirectional cross-filtering without necessity, causing ambiguous paths\n- Creating calculated columns when a dynamic measure was required\n- Forgetting that CALCULATE overrides existing visual filters",
        "worked_example": {
            "scenario": "An enterprise analytics team needs a DAX measure to calculate total sales revenue specifically for premium enterprise accounts, overriding any active visual segment slicers.",
            "code": "Enterprise Sales = \nCALCULATE(\n    SUM(FactSales[Revenue]),\n    DimCustomer[AccountTier] = \"Enterprise\",\n    DimCustomer[Status] = \"Active\"\n)",
            "reasoning": "1. SUM(FactSales[Revenue]) defines base numerical aggregation. 2. CALCULATE creates a new filter context. 3. Overrides visual slicers to restrict rows where AccountTier is Enterprise and Status is Active.",
            "expected_output": "| Region | Total Sales | Enterprise Sales |\n| :--- | :--- | :--- |\n| North America | $1,250,000 | $680,000 |\n| EMEA | $940,000 | $510,000 |"
        },
        "guided_practice": {
            "prompt": "Write a DAX measure named `Margin Pct` that calculates the gross margin percentage as (Total Revenue - Total Cost) / Total Revenue. Handle zero revenue safely using the DIVIDE function.",
            "starter_code": "-- Formulate gross margin percentage measure\nMargin Pct = \n-- Your DAX expression here",
            "solution": "Margin Pct = \nVAR TotalRev = SUM(FactSales[Revenue])\nVAR TotalCost = SUM(FactSales[Cost])\nVAR GrossProfit = TotalRev - TotalCost\nRETURN\nDIVIDE(GrossProfit, TotalRev, 0)",
            "hints": [
                "Step 1: Declare variables using VAR for TotalRev and TotalCost using SUM.",
                "Step 2: Calculate GrossProfit = TotalRev - TotalCost.",
                "Step 3: Return DIVIDE(GrossProfit, TotalRev, 0) to avoid division-by-zero errors."
            ]
        },
        "independent_practice": {
            "prompt": "Write a DAX measure named `High Value Orders Count` that counts the number of distinct orders in FactSales where the order line total exceeds $1,000.",
            "starter_code": "High Value Orders Count = \n-- Complete DAX measure",
            "solution": "High Value Orders Count = \nCALCULATE(\n    DISTINCTCOUNT(FactSales[OrderID]),\n    FactSales[LineTotal] > 1000\n)",
            "test_criteria": "Uses CALCULATE, DISTINCTCOUNT on OrderID, and filters LineTotal > 1000."
        },
        "concept_check": [
            {
                "question_text": "Why should you prefer the DAX `DIVIDE()` function over the standard `/` division operator?",
                "options": [
                    "DIVIDE() executes on the GPU for faster vectorization",
                    "DIVIDE() gracefully handles division by zero and returns a designated alternate result (or blank) instead of an error",
                    "The `/` operator is deprecated in modern Power BI releases",
                    "DIVIDE() automatically converts currency to USD"
                ],
                "correct": "DIVIDE() gracefully handles division by zero and returns a designated alternate result (or blank) instead of an error",
                "explanation": "Standard `/` throws an error on division by zero. DIVIDE() catches null/zero denominators safely."
            },
            {
                "question_text": "In a star schema data model, what is the best practice relationship direction between a Dimension table and a Fact table?",
                "options": [
                    "Bi-directional (Both directions)",
                    "1-to-many (Single direction: from Dimension to Fact)",
                    "Many-to-many with cross-filter enabled",
                    "1-to-1 strict relationship"
                ],
                "correct": "1-to-many (Single direction: from Dimension to Fact)",
                "explanation": "Single-direction 1-to-many relationships from Dimension to Fact avoid relationship ambiguity and ensure optimal query engine performance."
            },
            {
                "question_text": "What happens when `CALCULATE()` is evaluated inside an iterative row context (such as SUMX)?",
                "options": [
                    "It causes a syntax error",
                    "It triggers Context Transition, converting the current row context into an equivalent filter context",
                    "It resets all variables to null",
                    "It disables relationship propagation"
                ],
                "correct": "It triggers Context Transition, converting the current row context into an equivalent filter context",
                "explanation": "Context transition is a core DAX mechanism where CALCULATE transforms the values in the current row into active filters."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Analyst Executive Dashboard Architecture",
            "task_description": "Architect a star-schema analytical model with DAX KPI measures for monthly gross revenue, profit margin, and YoY growth percentage.",
            "starter_code": "-- Define DAX measures for executive reporting\nTotal Revenue = SUM(FactSales[Amount])\nYoY Growth = DIVIDE([Total Revenue] - CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(DimDate[Date])), CALCULATE([Total Revenue], SAMEPERIODLASTYEAR(DimDate[Date])), 0)",
            "rubrics": "Correctly defines measures using CALCULATE and DIVIDE, leverages date dimension for time intelligence, maintains star schema conventions."
        }
    },

    # -------------------------------------------------------------------------
    # 8. Data Scientist — Feature Engineering Pipelines
    # -------------------------------------------------------------------------
    {
        "slug": "feature-engineering-pipelines",
        "skill_name": "Machine Learning",
        "title": "Feature Engineering, Encoding & Transformation Pipelines",
        "concept_name": "Feature Preprocessing, Encoding & Leakage Prevention",
        "difficulty": "Intermediate",
        "estimated_minutes": 30,
        "order_index": 8,
        "prerequisite_concept_slugs": "python-pandas-pipelines,eda-workflow-data-profiling",
        "target_role_name": "Data Scientist",
        "learning_objectives": [
            "Construct reproducible scikit-learn ColumnTransformer and Pipeline architectures",
            "Apply optimal categorical encodings (One-Hot vs Ordinal vs Target Encoding) based on cardinality",
            "Prevent devastating data leakage by strictly fitting transformers only on training cross-validation splits",
        ],
        "explanation": """### The Science of Feature Engineering
Predictive model performance is fundamentally bounded by the quality and representation of input features. Raw tabular data contains categorical strings, non-normal distributions, and missing values that mathematical loss functions cannot ingest directly.

#### Preventing Data Leakage:
* **The Golden Rule**: Never fit any transformer (scaler, imputer, encoder) on test or validation data.
* Transforming the entire dataset before `train_test_split` leaks the global mean, standard deviation, and category distribution into the training set, producing deceptively high training metrics that collapse in production.

#### Categorical Encoding Strategy:
* **Nominal (Low Cardinality, < 10 values)**: Use `OneHotEncoder(handle_unknown='ignore', sparse_output=False)`.
* **Ordinal (Natural Rank)**: Use `OrdinalEncoder(categories=[['Low', 'Medium', 'High']])`.
* **High Cardinality (> 50 categories)**: Use Target Encoding with additive smoothing or frequency encoding.

#### Numerical Preprocessing:
* **Normal / Bell-shaped**: `StandardScaler` (z-score standardization).
* **Skewed with Outliers**: `RobustScaler` (median & interquartile range) or `PowerTransformer` (Yeo-Johnson).""",
        "key_rules": "- Fit transformers ONLY on training folds; transform test/production data\n- Wrap preprocessing and model in a scikit-learn Pipeline\n- Set handle_unknown='ignore' on OneHotEncoder for inference resilience",
        "common_mistakes": "- Calling fit_transform() on the entire dataset before train-test split\n- One-hot encoding high cardinality features (>1000 categories) causing dimensional explosion\n- Forgetting to impute missing values before applying StandardScaler",
        "worked_example": {
            "scenario": "A Data Scientist builds a leak-free preprocessing pipeline for customer credit risk modeling with mixed categorical and numerical features.",
            "code": "from sklearn.compose import ColumnTransformer\nfrom sklearn.pipeline import Pipeline\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\nfrom sklearn.impute import SimpleImputer\nfrom sklearn.linear_model import LogisticRegression\n\nnum_cols = ['age', 'income', 'credit_utilization']\ncat_cols = ['employment_type', 'home_ownership']\n\nnum_pipeline = Pipeline([\n    ('imputer', SimpleImputer(strategy='median')),\n    ('scaler', StandardScaler())\n])\n\ncat_pipeline = Pipeline([\n    ('imputer', SimpleImputer(strategy='most_frequent')),\n    ('encoder', OneHotEncoder(handle_unknown='ignore', sparse_output=False))\n])\n\npreprocessor = ColumnTransformer([\n    ('num', num_pipeline, num_cols),\n    ('cat', cat_pipeline, cat_cols)\n])\n\nmodel_pipeline = Pipeline([\n    ('prep', preprocessor),\n    ('classifier', LogisticRegression())\n])\n# model_pipeline.fit(X_train, y_train)",
            "reasoning": "1. Numerical pipeline imputes with median and standardizes. 2. Categorical pipeline imputes with mode and one-hot encodes. 3. ColumnTransformer merges transformations. 4. Master Pipeline encapsulates preprocessing and model.",
            "expected_output": "Pipeline(steps=[('prep', ColumnTransformer(...)), ('classifier', LogisticRegression())])"
        },
        "guided_practice": {
            "prompt": "Construct a scikit-learn ColumnTransformer that applies StandardScaler to numerical columns `['tenure', 'monthly_charges']` and OneHotEncoder to categorical column `['contract_type']`. Ensure unseen categories in test data do not cause an error.",
            "starter_code": "from sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\n\n# Construct preprocessor ColumnTransformer\npreprocessor = None",
            "solution": "from sklearn.compose import ColumnTransformer\nfrom sklearn.preprocessing import StandardScaler, OneHotEncoder\n\npreprocessor = ColumnTransformer([\n    ('num', StandardScaler(), ['tenure', 'monthly_charges']),\n    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['contract_type'])\n])",
            "hints": [
                "Step 1: Import ColumnTransformer from sklearn.compose.",
                "Step 2: Define tuple ('num', StandardScaler(), ['tenure', 'monthly_charges']).",
                "Step 3: Define tuple ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), ['contract_type'])."
            ]
        },
        "independent_practice": {
            "prompt": "Create an end-to-end Pipeline combining a ColumnTransformer (scaling `['features']`) with a RandomForestClassifier. Return the constructed pipeline object.",
            "starter_code": "from sklearn.pipeline import Pipeline\nfrom sklearn.ensemble import RandomForestClassifier\n\ndef build_pipeline(preprocessor):\n    # Return Pipeline combining preprocessor and RandomForestClassifier\n    pass",
            "solution": "from sklearn.pipeline import Pipeline\nfrom sklearn.ensemble import RandomForestClassifier\n\ndef build_pipeline(preprocessor):\n    return Pipeline([\n        ('preprocessor', preprocessor),\n        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))\n    ])",
            "test_criteria": "Uses Pipeline with 'preprocessor' step and 'classifier' RandomForestClassifier step."
        },
        "concept_check": [
            {
                "question_text": "What is the primary operational risk of calling `StandardScaler.fit_transform(X)` on the complete dataset before calling `train_test_split`?",
                "options": [
                    "It will cause an Out-Of-Memory error on datasets under 1GB",
                    "It causes data leakage by exposing the test set's distribution parameters (mean and variance) to the training set",
                    "StandardScaler only works on pandas Series, not DataFrames",
                    "Scikit-learn models automatically reject pre-scaled data"
                ],
                "correct": "It causes data leakage by exposing the test set's distribution parameters (mean and variance) to the training set",
                "explanation": "Fitting on the entire dataset incorporates test-set information into normalization parameters, creating optimistic training bias that fails on real-world test data."
            },
            {
                "question_text": "When deploying a production OneHotEncoder for inference, why is `handle_unknown='ignore'` essential?",
                "options": [
                    "It compresses the output matrix by 50%",
                    "It prevents runtime crashes when a new, previously unseen category is encountered in production requests",
                    "It converts text into embeddings automatically",
                    "It forces all features to sum to 1"
                ],
                "correct": "It prevents runtime crashes when a new, previously unseen category is encountered in production requests",
                "explanation": "By default, OneHotEncoder raises an error on unknown categories. Setting handle_unknown='ignore' outputs all zeros for unseen categories, preventing production server failures."
            },
            {
                "question_text": "Which feature transformation is most resilient to extreme numerical outliers?",
                "options": ["MinMaxScaler", "StandardScaler", "RobustScaler", "Normalizer"],
                "correct": "RobustScaler",
                "explanation": "RobustScaler removes the median and scales data according to the Interquartile Range (IQR), making it resistant to extreme outliers that distort mean and standard deviation."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Scientist Production ML Deployment",
            "task_description": "Build an end-to-end scikit-learn Pipeline with median imputation, robust scaling for numerical features, one-hot encoding for categorical features, and a gradient boosting classifier.",
            "starter_code": "def create_production_pipeline(num_cols, cat_cols):\n    # Construct leak-free pipeline\n    pass",
            "rubrics": "Uses ColumnTransformer, handles missing values, encapsulates model in Pipeline, sets handle_unknown on encoder."
        }
    },

    # -------------------------------------------------------------------------
    # 9. Data Scientist — Model Evaluation Metrics
    # -------------------------------------------------------------------------
    {
        "slug": "model-evaluation-metrics",
        "skill_name": "Machine Learning",
        "title": "Model Evaluation, Cross-Validation & Metric Optimization",
        "concept_name": "Metric Tradeoffs, Stratified Cross-Validation & Threshold Tuning",
        "difficulty": "Advanced",
        "estimated_minutes": 25,
        "order_index": 9,
        "prerequisite_concept_slugs": "machine-learning-foundations",
        "target_role_name": "Data Scientist",
        "learning_objectives": [
            "Evaluate imbalanced classification models using Precision-Recall curves and PR-AUC instead of misleading accuracy",
            "Implement StratifiedKFold cross-validation to preserve class proportions across training folds",
            "Calibrate decision probability thresholds to optimize business cost-utility tradeoffs",
        ],
        "explanation": """### The Fallacy of Accuracy in Production
In real-world data science, target classes are almost always imbalanced (e.g., 0.5% fraud, 3% disease incidence, 5% customer churn). A trivial classifier predicting the majority class achieves 99.5% accuracy while possessing zero diagnostic utility.

#### The Precision-Recall Spectrum:
* **Precision**: $\\frac{TP}{TP + FP}$ — "Out of all predicted positives, how many were truly positive?" Crucial when False Positives are expensive (e.g., spam filtering, content moderation).
* **Recall (Sensitivity)**: $\\frac{TP}{TP + FN}$ — "Out of all actual positives, how many did we capture?" Critical when False Negatives are catastrophic (e.g., medical diagnosis, fraud detection).
* **F1-Score**: Harmonic mean of Precision and Recall: $\\frac{2 \\times P \\times R}{P + R}$.

#### Decision Threshold Tuning:
Classifiers output probabilities via `predict_proba()`. The default threshold of `0.5` is arbitrary. By tuning the threshold:
* Lowering threshold (e.g., to `0.2`) increases **Recall** at the cost of more False Positives.
* Raising threshold (e.g., to `0.8`) increases **Precision** at the cost of missing true cases.

#### Cross-Validation Rigor:
Always use `StratifiedKFold` for classification to guarantee that every validation fold maintains the exact same target class ratio as the overall population.""",
        "key_rules": "- Never use raw accuracy as the sole evaluation metric on imbalanced datasets\n- Use StratifiedKFold for cross-validation on classification tasks\n- Tune decision thresholds based on explicit business loss matrices (cost of FP vs FN)",
        "common_mistakes": "- Evaluating models with ROC-AUC when positive class prevalence is under 1% (use PR-AUC instead)\n- Tuning hyperparameters directly on the test set instead of a cross-validation split\n- Accepting default 0.5 decision threshold without inspecting probability calibration",
        "worked_example": {
            "scenario": "A Data Scientist evaluates a loan default detection model on a 95:5 imbalanced dataset, optimizing the classification threshold to maximize F1-score.",
            "code": "from sklearn.model_selection import StratifiedKFold, cross_val_score\nfrom sklearn.metrics import precision_recall_curve, f1_score\nimport numpy as np\n\n# Stratified Cross-Validation\nskf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)\n# scores = cross_val_score(model, X, y, cv=skf, scoring='average_precision')\n\n# Threshold Optimization\n# probs = model.predict_proba(X_val)[:, 1]\n# precision, recall, thresholds = precision_recall_curve(y_val, probs)\n# f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)\n# best_idx = np.argmax(f1_scores)\n# optimal_threshold = thresholds[best_idx]",
            "reasoning": "1. StratifiedKFold ensures every fold contains 5% default cases. 2. Uses average_precision (PR-AUC) as scoring metric. 3. Sweeps decision thresholds to locate peak F1-score.",
            "expected_output": "Optimal Decision Threshold: 0.32 | Peak F1-Score: 0.74 (vs default 0.5 F1: 0.58)"
        },
        "guided_practice": {
            "prompt": "Write a Python function `evaluate_imbalanced_model(y_true, y_probs)` that computes and returns a dictionary with `roc_auc` and `pr_auc` (average precision score).",
            "starter_code": "from sklearn.metrics import roc_auc_score, average_precision_score\n\ndef evaluate_imbalanced_model(y_true, y_probs):\n    # Return dict with 'roc_auc' and 'pr_auc'\n    pass",
            "solution": "from sklearn.metrics import roc_auc_score, average_precision_score\n\ndef evaluate_imbalanced_model(y_true, y_probs):\n    return {\n        'roc_auc': float(roc_auc_score(y_true, y_probs)),\n        'pr_auc': float(average_precision_score(y_true, y_probs))\n    }",
            "hints": [
                "Step 1: Compute roc_auc_score(y_true, y_probs).",
                "Step 2: Compute average_precision_score(y_true, y_probs) for PR-AUC.",
                "Step 3: Return both in a dictionary."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function `convert_probs_to_predictions(probs, threshold=0.35)` that takes an array of positive class probabilities and returns binary integer predictions (0 or 1).",
            "starter_code": "import numpy as np\n\ndef convert_probs_to_predictions(probs, threshold=0.35):\n    # Convert probabilities to binary predictions\n    pass",
            "solution": "import numpy as np\n\ndef convert_probs_to_predictions(probs, threshold=0.35):\n    return (np.asarray(probs) >= threshold).astype(int)",
            "test_criteria": "Applies threshold comparison, returns numpy array or list of 0s and 1s."
        },
        "concept_check": [
            {
                "question_text": "On an extremely imbalanced dataset (e.g., 0.1% positive class), why is Precision-Recall AUC (PR-AUC) superior to ROC-AUC?",
                "options": [
                    "PR-AUC is faster to compute by an order of magnitude",
                    "ROC-AUC can present an overly optimistic assessment because False Positive Rate is diluted by the massive true negative count",
                    "ROC-AUC cannot be calculated if negative cases exceed 1,000",
                    "PR-AUC does not require probability predictions"
                ],
                "correct": "ROC-AUC can present an overly optimistic assessment because False Positive Rate is diluted by the massive true negative count",
                "explanation": "ROC-AUC's false positive rate ($FP / TN$) has a vast denominator ($TN$), making FPR appear negligible even with huge absolute numbers of false alarms. PR-AUC focuses directly on the minority positive class."
            },
            {
                "question_text": "In a cancer screening model where missing a malignancy (False Negative) is fatal, what metric must be prioritized?",
                "options": ["Precision", "Recall", "Overall Accuracy", "Specificity"],
                "correct": "Recall",
                "explanation": "Recall measures the percentage of actual positive cases detected. Maximizing recall minimizes fatal False Negatives."
            },
            {
                "question_text": "What is the purpose of using `StratifiedKFold` instead of standard `KFold`?",
                "options": [
                    "It sorts the dataset by date before splitting",
                    "It ensures each split contains approximately the same percentage of target class samples as the complete dataset",
                    "It eliminates duplicate rows across splits",
                    "It converts categorical variables automatically"
                ],
                "correct": "It ensures each split contains approximately the same percentage of target class samples as the complete dataset",
                "explanation": "Standard KFold can randomly assign all positive minority cases to one fold. StratifiedKFold maintains identical class proportions across every fold."
            }
        ],
        "applied_task": {
            "role_scenario": "Data Scientist Model Diagnostic Evaluation",
            "task_description": "Implement a diagnostic evaluation report calculating cross-validated PR-AUC, confusion matrix, and threshold optimization on an imbalanced classification dataset.",
            "starter_code": "def evaluate_fraud_model(X, y, classifier):\n    # Cross-validated evaluation and optimal threshold selection\n    pass",
            "rubrics": "Uses StratifiedKFold, reports PR-AUC, determines optimal threshold, outputs confusion matrix."
        }
    },

    # -------------------------------------------------------------------------
    # 10. Python Developer — Python Foundations: Syntax, Variables & Control Flow
    # -------------------------------------------------------------------------
    {
        "slug": "python-core-fundamentals",
        "skill_name": "Python Basics",
        "title": "Python Foundations: Syntax, Variables & Control Flow",
        "concept_name": "Variables, Primitive Types, Conditionals & Loops",
        "difficulty": "Beginner",
        "estimated_minutes": 25,
        "order_index": 10,
        "prerequisite_concept_slugs": "",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Master Python variable assignment, dynamic typing, and primitive data types (int, float, str, bool)",
            "Implement conditional branching logic using if, elif, else, and boolean logical operators",
            "Construct deterministic loops using for with range(), while loops, and loop control statements (break, continue)",
        ],
        "explanation": """### Python Foundations: Core Syntax & Flow Control
Python is an expressive, dynamically typed programming language designed for readability and developer efficiency. Before tackling object-oriented patterns or asynchronous APIs, you must master the core primitives and deterministic control flow.

#### Dynamic Typing & Primitive Types:
Python variables are dynamically typed references to objects. You do not declare variable types explicitly:
* **Integers & Floats**: `count = 42`, `rate = 0.05`
* **Strings**: `'single quotes'` or `"double quotes"`, supporting formatted f-strings: `f"Count: {count}"`
* **Booleans**: `True` and `False` (capitalized)
* **Type Conversion**: `int("123")`, `str(456)`, `float("3.14")`, `bool(1)`

#### Control Flow: Conditionals
Python uses strict 4-space indentation to define code blocks (no curly braces `{}`).
```python
if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
else:
    grade = "C"
```
Boolean operators include `and`, `or`, and `not`. Comparison operators include `==` (equality), `!=` (inequality), `<`, `<=`, `>`, `>=`.

#### Iteration: For Loops & While Loops
The `for` loop iterates over sequences or ranges:
```python
# Iterates 0, 1, 2, 3, 4
for i in range(5):
    if i == 2:
        continue  # skip to next iteration
    if i == 4:
        break     # exit loop immediately
```
The `while` loop executes as long as a condition evaluates to `True`.""",
        "key_rules": "- Indentation matters: Python uses exactly 4 spaces per block, never mix tabs and spaces\n- Use '==' for value equality comparison, '=' for variable assignment\n- Statements like if, elif, else, for, and while must end with a colon (:)",
        "common_mistakes": "- Forgetting the trailing colon on compound statements\n- Off-by-one errors with range(start, stop): range(1, 5) stops at 4, not 5\n- Using assignment operator '=' inside an if condition instead of '=='",
        "worked_example": {
            "scenario": "A backend service needs to validate incoming user registration data, verifying age thresholds and categorizing the user account tier.",
            "code": "def evaluate_registration(age: int, has_verified_email: bool) -> str:\n    if age < 18:\n        return 'REJECTED: Minimum age requirement is 18'\n    elif not has_verified_email:\n        return 'PENDING: Email verification required'\n    elif age >= 65:\n        return 'APPROVED: Senior Account Tier'\n    else:\n        return 'APPROVED: Standard Account Tier'\n\n# Test verification\nprint(evaluate_registration(25, True))  # APPROVED: Standard Account Tier",
            "reasoning": "1. Checks boundary condition age < 18 first. 2. Checks boolean condition for email verification. 3. Categorizes tier based on age threshold.",
            "expected_output": "APPROVED: Standard Account Tier"
        },
        "guided_practice": {
            "prompt": "Write a function `categorize_transaction(amount: float) -> str` that returns 'SMALL' for amounts <= 50, 'MEDIUM' for amounts <= 500, and 'LARGE' for amounts > 500.",
            "starter_code": "def categorize_transaction(amount: float) -> str:\n    # Implement conditional tier classification\n    pass",
            "solution": "def categorize_transaction(amount: float) -> str:\n    if amount <= 50:\n        return 'SMALL'\n    elif amount <= 500:\n        return 'MEDIUM'\n    else:\n        return 'LARGE'",
            "hints": [
                "Step 1: Check if amount <= 50 first.",
                "Step 2: Use elif amount <= 500 for the middle tier.",
                "Step 3: Use else to return 'LARGE'."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function `sum_even_numbers(n: int) -> int` that uses a for loop with range() to calculate the sum of all even integers from 2 up to n inclusive.",
            "starter_code": "def sum_even_numbers(n: int) -> int:\n    # Sum even numbers up to n\n    pass",
            "solution": "def sum_even_numbers(n: int) -> int:\n    total = 0\n    for num in range(2, n + 1, 2):\n        total += num\n    return total",
            "test_criteria": "Uses range with step 2 (or modulo % 2 check), sums even integers up to n inclusive, and returns integer total."
        },
        "concept_check": [
            {
                "question_text": "What is the output of `list(range(1, 5))` in Python?",
                "options": [
                    "[1, 2, 3, 4, 5]",
                    "[1, 2, 3, 4]",
                    "[0, 1, 2, 3, 4]",
                    "[2, 3, 4, 5]"
                ],
                "correct": "[1, 2, 3, 4]",
                "explanation": "In Python, range(start, stop) generates numbers up to but excluding the stop boundary. Therefore range(1, 5) yields 1, 2, 3, and 4."
            },
            {
                "question_text": "Which statement correctly checks if a variable `count` is between 10 and 20 inclusive?",
                "options": [
                    "if 10 <= count <= 20:",
                    "if count >= 10 && count <= 20:",
                    "if count between 10 and 20:",
                    "if 10 < count < 20:"
                ],
                "correct": "if 10 <= count <= 20:",
                "explanation": "Python supports chained comparison operators: `10 <= count <= 20` is valid and idiomatic (equivalent to `count >= 10 and count <= 20`). Python uses `and`, not `&&`."
            },
            {
                "question_text": "What happens if you use a single '=' instead of '==' in a Python conditional like `if x = 5:`?",
                "options": [
                    "x is assigned 5 and the condition evaluates to True",
                    "Python raises a SyntaxError at compile time",
                    "Python casts x to a boolean",
                    "x is compared to 5 with type coercion"
                ],
                "correct": "Python raises a SyntaxError at compile time",
                "explanation": "In Python, assignment (=) is a statement, not an expression, and causes a SyntaxError inside if conditions."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Backend Ingestion Validator",
            "task_description": "Implement a transaction processor function `audit_transactions(transactions: list) -> dict` that loops through numeric amounts, sums total valid transactions (amounts > 0), and counts flagged negative values.",
            "starter_code": "def audit_transactions(transactions: list) -> dict:\n    # Process transactions with loops and conditionals\n    pass",
            "rubrics": "Uses for loop, correctly checks amount > 0, tracks total_amount and flagged_count, returns dictionary with summary."
        }
    },

    # -------------------------------------------------------------------------
    # 11. Python Developer — Collections, Functions & Modular Code
    # -------------------------------------------------------------------------
    {
        "slug": "python-collections-functions",
        "skill_name": "Data Structures",
        "title": "Python Collections, Functions & Modular Code",
        "concept_name": "Lists, Dictionaries, Tuples, Sets & Functions",
        "difficulty": "Beginner",
        "estimated_minutes": 30,
        "order_index": 11,
        "prerequisite_concept_slugs": "python-core-fundamentals",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Manipulate core collections: lists (ordered, mutable), dictionaries (key-value, mutable), tuples (immutable), and sets (unique)",
            "Define modular functions with positional arguments, keyword arguments, default values, and explicit return statements",
            "Understand Python variable scope (LEGB rule) and structure reusable, testable code modules",
        ],
        "explanation": """### Python Collections & Reusable Functions
In backend development, data rarely arrives as isolated primitives. You process sequences of items, key-value configurations, and structured payloads using Python's built-in collections.

#### Core Python Collections:
1. **Lists (`[]`)**: Ordered, mutable sequences. Support indexing, slicing (`items[1:3]`), `.append()`, `.pop()`.
2. **Dictionaries (`{}`)**: Key-value hash tables. Fast $O(1)$ lookups by key. Use `.get(key, default)` to avoid `KeyError`.
3. **Tuples (`()`)**: Ordered, immutable sequences. Used for fixed records, multi-value returns, and dictionary keys.
4. **Sets (`set()`)**: Unordered collections of unique elements. Fast membership testing (`item in my_set`) and set operations (union, intersection).

#### Modular Functions:
Functions encapsulate reusable logic:
```python
def calculate_tax(subtotal: float, tax_rate: float = 0.08) -> float:
    \"\"\"Calculate total tax for a given subtotal.\"\"\"
    if subtotal < 0:
        raise ValueError("Subtotal cannot be negative")
    return round(subtotal * tax_rate, 2)
```

#### The Cardinal Rule of Default Arguments:
Never use a mutable object (`[]` or `{}`) as a default argument. Default arguments are evaluated once at function definition time. Always use `None` as the default and initialize the collection inside the function body.""",
        "key_rules": "- Use .get() when accessing dictionary keys that might not exist to prevent KeyErrors\n- Never use mutable defaults (def fn(items=[])): use def fn(items=None) instead\n- Tuples and strings are immutable; lists and dictionaries are mutable",
        "common_mistakes": "- Modifying a list while iterating over it in a for loop\n- Forgetting that sets are unordered and do not support positional indexing like s[0]\n- Assuming function parameters are pass-by-value; Python passes object references",
        "worked_example": {
            "scenario": "A backend service aggregates user metrics from a list of user profile dictionaries, calculating active user count and average age.",
            "code": "from typing import List, Dict, Any\n\ndef aggregate_user_metrics(users: List[Dict[str, Any]]) -> Dict[str, Any]:\n    active_count = 0\n    total_age = 0\n    \n    for user in users:\n        if user.get('is_active', False):\n            active_count += 1\n            total_age += user.get('age', 0)\n            \n    avg_age = round(total_age / active_count, 1) if active_count > 0 else 0.0\n    return {'active_users': active_count, 'average_age': avg_age}\n\n# Verification\nsample_users = [\n    {'name': 'Alice', 'age': 30, 'is_active': True},\n    {'name': 'Bob', 'age': 40, 'is_active': False},\n    {'name': 'Charlie', 'age': 20, 'is_active': True},\n]\nprint(aggregate_user_metrics(sample_users))",
            "reasoning": "1. Uses .get() for defensive dictionary access. 2. Iterates list of dicts. 3. Handles division by zero safely.",
            "expected_output": "{'active_users': 2, 'average_age': 25.0}"
        },
        "guided_practice": {
            "prompt": "Write a function `count_word_frequencies(words: list) -> dict` that counts how many times each word appears in the list and returns a dictionary mapping word to frequency count.",
            "starter_code": "def count_word_frequencies(words: list) -> dict:\n    # Implement frequency counter\n    pass",
            "solution": "def count_word_frequencies(words: list) -> dict:\n    counts = {}\n    for word in words:\n        counts[word] = counts.get(word, 0) + 1\n    return counts",
            "hints": [
                "Step 1: Initialize an empty dictionary `counts = {}`.",
                "Step 2: Iterate through each word in words.",
                "Step 3: Use `counts.get(word, 0) + 1` to increment the tally."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function `filter_unique_tags(tags_list: list) -> list` that accepts a list of string tags with duplicates, removes duplicates, and returns a sorted list of unique tags.",
            "starter_code": "def filter_unique_tags(tags_list: list) -> list:\n    # Deduplicate and sort tags\n    pass",
            "solution": "def filter_unique_tags(tags_list: list) -> list:\n    return sorted(list(set(tags_list)))",
            "test_criteria": "Uses set() to deduplicate tags, converts back to list, and returns sorted ascending order."
        },
        "concept_check": [
            {
                "question_text": "What is the safest way to retrieve the value for key 'email' from dictionary `user_data` when the key may not exist?",
                "options": [
                    "user_data['email']",
                    "user_data.get('email', None)",
                    "user_data.find('email')",
                    "user_data.index('email')"
                ],
                "correct": "user_data.get('email', None)",
                "explanation": "Calling `dict.get(key, default)` returns the default value (or None) if the key is missing, whereas `user_data['email']` raises a KeyError."
            },
            {
                "question_text": "Which collection type in Python enforces unique elements with fast $O(1)$ membership checking?",
                "options": [
                    "List",
                    "Tuple",
                    "Set",
                    "OrderedDict"
                ],
                "correct": "Set",
                "explanation": "A Set in Python is backed by a hash table, ensuring all elements are unique and providing average $O(1)$ lookup time for the `in` operator."
            },
            {
                "question_text": "Why should you avoid using `def append_item(item, container=[])` with a mutable list default?",
                "options": [
                    "Python will throw a SyntaxError",
                    "The single list instance is created once at function definition time and mutated across all subsequent calls",
                    "Lists cannot be used as function arguments in Python 3",
                    "The function becomes asynchronous"
                ],
                "correct": "The single list instance is created once at function definition time and mutated across all subsequent calls",
                "explanation": "Default parameter values are evaluated once when the function is defined. A mutable default like `[]` is shared across every call that does not provide a container."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Backend Product Catalog",
            "task_description": "Implement a catalog grouping function `group_products_by_category(products: list) -> dict` that takes product dictionaries with 'name', 'price', and 'category', and groups product names into lists indexed by category.",
            "starter_code": "def group_products_by_category(products: list) -> dict:\n    # Group products by category\n    pass",
            "rubrics": "Uses dictionaries and lists, groups product names under category keys, handles empty inputs gracefully."
        }
    },

    # -------------------------------------------------------------------------
    # 11. Python Developer — OOP Architecture & Clean Patterns
    # -------------------------------------------------------------------------
    {
        "slug": "python-oop-architecture",
        "skill_name": "OOP",
        "title": "Object-Oriented Design & Clean Architecture Patterns",
        "concept_name": "Encapsulation, Polymorphism, Composition & Abstract Base Classes",
        "difficulty": "Intermediate",
        "estimated_minutes": 30,
        "order_index": 12,
        "prerequisite_concept_slugs": "python-collections-functions",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Enforce interface contracts using Python's `abc.ABC` and `@abstractmethod` decorators",
            "Apply the Dependency Inversion Principle and favor Composition over Inheritance",
            "Encapsulate state cleanly using `@property` getters, setters, and Python dataclasses",
        ],
        "explanation": """### Clean Architecture in Backend Python
Professional Python backend development requires clean, decoupled architectures. Code that tightly couples business logic to concrete database queries or external third-party SDKs is fragile and untestable.

#### Abstract Base Classes (ABCs):
Python supports explicit interface contracts through `from abc import ABC, abstractmethod`. Any subclass inheriting from an `ABC` **must** implement all abstract methods; attempting to instantiate an incomplete subclass raises a `TypeError` at runtime.

```python
class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, amount: float, customer_id: str) -> str:
        \"\"\"Process payment and return transaction ID.\"\"\"
        pass
```

#### Composition Over Inheritance:
* **Inheritance ("Is-a")**: Tightly couples child classes to parent implementation details. Deep hierarchies become unmaintainable.
* **Composition ("Has-a")**: Inject dependencies into the constructor. A `CheckoutService` *has a* `PaymentGateway` and *has a* `NotificationService`.

#### Modern Python Dataclasses:
Use `@dataclass(frozen=True)` for immutable domain transfer objects (DTOs), reducing boilerplate `__init__`, `__repr__`, and `__eq__` implementations.""",
        "key_rules": "- Program to abstractions (ABCs), never directly to concrete implementations\n- Favor Composition over Inheritance to minimize class coupling\n- Use @property decorators to encapsulate validation logic on private attributes",
        "common_mistakes": "- Creating deep multi-level inheritance hierarchies instead of injecting composed components\n- Directly modifying private `_attribute` state from external code\n- Forgetting that an Abstract Base Class cannot be instantiated until all abstract methods are implemented",
        "worked_example": {
            "scenario": "A Python developer designs a decoupled notification architecture where the core domain service relies on an abstract interface, allowing effortless switching between Email and SMS providers.",
            "code": "from abc import ABC, abstractmethod\nfrom dataclasses import dataclass\n\n@dataclass\nclass NotificationMessage:\n    recipient: str\n    subject: str\n    body: str\n\nclass NotificationGateway(ABC):\n    @abstractmethod\n    def send(self, message: NotificationMessage) -> bool:\n        pass\n\nclass EmailGateway(NotificationGateway):\n    def send(self, message: NotificationMessage) -> bool:\n        print(f\"Dispatching email to {message.recipient}: {message.subject}\")\n        return True\n\nclass AlertService:\n    def __init__(self, gateway: NotificationGateway):\n        self._gateway = gateway  # Injected dependency\n\n    def notify_user(self, user_email: str, alert_text: str) -> bool:\n        msg = NotificationMessage(recipient=user_email, subject=\"Security Alert\", body=alert_text)\n        return self._gateway.send(msg)",
            "reasoning": "1. NotificationGateway defines abstract contract. 2. EmailGateway provides concrete implementation. 3. AlertService accepts any NotificationGateway via constructor dependency injection.",
            "expected_output": "True (EmailGateway dispatches without AlertService knowing email provider details)"
        },
        "guided_practice": {
            "prompt": "Create an Abstract Base Class `Repository(ABC)` with an `@abstractmethod` named `get_by_id(self, id: int) -> dict`. Then implement a concrete class `InMemoryRepository(Repository)` that stores and retrieves items from an internal dictionary.",
            "starter_code": "from abc import ABC, abstractmethod\n\nclass Repository(ABC):\n    # Define abstract get_by_id method\n    pass\n\nclass InMemoryRepository(Repository):\n    # Implement concrete storage and retrieval\n    pass",
            "solution": "from abc import ABC, abstractmethod\nfrom typing import Dict, Any, Optional\n\nclass Repository(ABC):\n    @abstractmethod\n    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:\n        pass\n\nclass InMemoryRepository(Repository):\n    def __init__(self):\n        self._storage = {}\n\n    def add(self, id: int, data: Dict[str, Any]) -> None:\n        self._storage[id] = data\n\n    def get_by_id(self, id: int) -> Optional[Dict[str, Any]]:\n        return self._storage.get(id)",
            "hints": [
                "Step 1: Inherit Repository from ABC.",
                "Step 2: Decorate get_by_id with @abstractmethod.",
                "Step 3: Implement get_by_id in InMemoryRepository returning self._storage.get(id)."
            ]
        },
        "independent_practice": {
            "prompt": "Implement a class `BankAccount` with private attribute `_balance`. Provide a `@property` getter for `balance` and a setter that raises `ValueError` if the new balance is negative.",
            "starter_code": "class BankAccount:\n    def __init__(self, initial_balance: float = 0.0):\n        self._balance = initial_balance\n\n    # Implement property getter and setter for balance",
            "solution": "class BankAccount:\n    def __init__(self, initial_balance: float = 0.0):\n        if initial_balance < 0:\n            raise ValueError(\"Initial balance cannot be negative\")\n        self._balance = initial_balance\n\n    @property\n    def balance(self) -> float:\n        return self._balance\n\n    @balance.setter\n    def balance(self, value: float) -> None:\n        if value < 0:\n            raise ValueError(\"Balance cannot be negative\")\n        self._balance = value",
            "test_criteria": "Uses @property and @balance.setter, raises ValueError on negative value."
        },
        "concept_check": [
            {
                "question_text": "What happens if a developer attempts to instantiate a class that inherits from `ABC` but does NOT implement all `@abstractmethod` methods?",
                "options": [
                    "Python instantiates it, but crashes if the missing method is called",
                    "Python raises a TypeError immediately upon instantiation: 'Can't instantiate abstract class with abstract methods'",
                    "Python automatically injects an empty dummy implementation",
                    "It defaults to the parent class implementation"
                ],
                "correct": "Python raises a TypeError immediately upon instantiation: 'Can't instantiate abstract class with abstract methods'",
                "explanation": "Python's ABC mechanism strictly blocks instantiation of incomplete subclasses, guaranteeing interface conformity at instantiation time."
            },
            {
                "question_text": "Why does modern software engineering recommend 'Composition over Inheritance'?",
                "options": [
                    "Composition runs faster on multi-core processors",
                    "Composition decouples components by injecting dependencies, making code more flexible and easier to test via mocking",
                    "Inheritance was removed in Python 3.10",
                    "Composition eliminates the need for unit tests"
                ],
                "correct": "Composition decouples components by injecting dependencies, making code more flexible and easier to test via mocking",
                "explanation": "Composition allows swapping behavior dynamically and injecting mock objects during unit testing without fighting rigid parent class hierarchies."
            },
            {
                "question_text": "What is the primary benefit of the `@property` decorator in Python?",
                "options": [
                    "It makes the method execute asynchronously",
                    "It exposes method access using attribute syntax while allowing validation and encapsulation behind the scenes",
                    "It serializes the object to JSON format",
                    "It caches the method result in Redis"
                ],
                "correct": "It exposes method access using attribute syntax while allowing validation and encapsulation behind the scenes",
                "explanation": "@property provides idiomatic attribute access syntax (obj.balance) while running underlying getter/setter logic that can enforce validation."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Developer Software Architecture",
            "task_description": "Architect a domain service layer using Abstract Base Classes, dependency injection, and clean separation between business logic and database persistence.",
            "starter_code": "def build_order_processing_service(repo, payment_gateway):\n    # Compose and return OrderService\n    pass",
            "rubrics": "Defines ABC interfaces, injects dependencies into service constructor, encapsulates state cleanly."
        }
    },

    # -------------------------------------------------------------------------
    # 12. Python Developer — Robust Error Handling
    # -------------------------------------------------------------------------
    {
        "slug": "python-error-handling-robustness",
        "skill_name": "Exception Handling",
        "title": "Robust Error Handling, Custom Exceptions & Logging",
        "concept_name": "Exception Hierarchies, Context Managers & Safe Failures",
        "difficulty": "Intermediate",
        "estimated_minutes": 25,
        "order_index": 13,
        "prerequisite_concept_slugs": "python-collections-functions",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Construct clear domain-specific custom exception hierarchies inheriting from `Exception`",
            "Master exception control flow: `try`, `except`, `else`, `finally`, and exception chaining (`from e`)",
            "Implement custom context managers using both class protocols (`__enter__`/`__exit__`) and `@contextmanager`",
        ],
        "explanation": """### Production Defensive Engineering
Robust backend systems must fail predictably and gracefully. Silently suppressing errors, returning `None` on failures, or catching broad `except Exception:` obscures bugs and corrupts data downstream.

#### Creating Custom Exception Hierarchies:
Always define a base domain exception for your service, then create specific child exceptions:
```python
class AppError(Exception):
    \"\"\"Base exception for all application errors.\"\"\"
    pass

class UserNotFoundError(AppError):
    def __init__(self, user_id: int):
        super().__init__(f\"User with ID {user_id} was not found.\")
        self.user_id = user_id

class InsufficientFundsError(AppError):
    pass
```

#### The `else` and `finally` Clauses:
* **`try`**: Wrap the minimal amount of code that could raise an exception.
* **`except SpecificError`**: Catch and handle exact exception types.
* **`else`**: Code that runs ONLY if the `try` block succeeded with zero exceptions.
* **`finally`**: Code that runs GUARANTEED (cleanup, closing sockets/files), whether an exception occurred or not.

#### Exception Chaining with `raise ... from e`:
When translating low-level database errors into domain exceptions, use `from` to preserve the original traceback for debugging:
```python
try:
    db.execute(query)
except sqlite3.OperationalError as err:
    raise DatabaseQueryError(\"Failed to query records\") from err
```""",
        "key_rules": "- Never use bare 'except:' or catch BaseException directly\n- Wrap only the code that might fail inside the try block\n- Use context managers (with) to ensure deterministic resource disposal",
        "common_mistakes": "- Catching Exception and doing 'pass' (silent failure), completely hiding critical bugs\n- Raising generic strings instead of Exception classes\n- Putting business logic inside the try block that should have been in the else block",
        "worked_example": {
            "scenario": "A Python backend engineer writes a custom transaction context manager that auto-commits on success and rolls back on failure with custom exception translation.",
            "code": "from contextlib import contextmanager\n\nclass TransactionError(Exception):\n    \"\"\"Raised when a database transaction fails.\"\"\"\n    pass\n\n@contextmanager\ndef transaction_scope(db_connection):\n    cursor = db_connection.cursor()\n    try:\n        yield cursor\n        db_connection.commit()\n    except Exception as exc:\n        db_connection.rollback()\n        raise TransactionError(f\"Transaction rolled back due to error: {exc}\") from exc\n    finally:\n        cursor.close()\n\n# Usage:\n# with transaction_scope(conn) as cur:\n#     cur.execute(\"UPDATE accounts SET balance = balance - 100 WHERE id = 1\")",
            "reasoning": "1. yield gives control to the with block. 2. If no exception, commits transaction. 3. If exception occurs, rolls back and raises custom TransactionError from original exception. 4. finally ensures cursor is closed.",
            "expected_output": "Clean commit on success; automatic rollback and TransactionError on failure"
        },
        "guided_practice": {
            "prompt": "Define a custom exception `ValidationError(Exception)` that stores an `error_code: str` attribute. Then write a function `validate_age(age: int)` that raises `ValidationError(\"Invalid age\", error_code=\"AGE_OUT_OF_BOUNDS\")` if age < 0 or age > 120.",
            "starter_code": "# Define ValidationError and validate_age function\nclass ValidationError(Exception):\n    pass\n\ndef validate_age(age: int) -> None:\n    pass",
            "solution": "class ValidationError(Exception):\n    def __init__(self, message: str, error_code: str):\n        super().__init__(message)\n        self.error_code = error_code\n\ndef validate_age(age: int) -> None:\n    if age < 0 or age > 120:\n        raise ValidationError(\"Age must be between 0 and 120\", error_code=\"AGE_OUT_OF_BOUNDS\")",
            "hints": [
                "Step 1: In ValidationError.__init__, call super().__init__(message) and set self.error_code = error_code.",
                "Step 2: In validate_age, check if age < 0 or age > 120.",
                "Step 3: If invalid, raise ValidationError with message and error_code."
            ]
        },
        "independent_practice": {
            "prompt": "Write a function `safe_divide(a: float, b: float) -> float` that catches `ZeroDivisionError`, logs or handles it, and returns `0.0`. If any other exception occurs, re-raise it.",
            "starter_code": "def safe_divide(a: float, b: float) -> float:\n    # Implement specific exception handling\n    pass",
            "solution": "def safe_divide(a: float, b: float) -> float:\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return 0.0",
            "test_criteria": "Catches only ZeroDivisionError, returns 0.0, allows other exceptions to propagate."
        },
        "concept_check": [
            {
                "question_text": "Why is writing `try: ... except: pass` considered one of the worst anti-patterns in Python?",
                "options": [
                    "It causes memory leaks in the Python garbage collector",
                    "It catches KeyboardInterrupt and system exit signals, silently masking bugs and preventing normal process termination",
                    "It forces Python into synchronous execution mode",
                    "It slows down Python by 10x"
                ],
                "correct": "It catches KeyboardInterrupt and system exit signals, silently masking bugs and preventing normal process termination",
                "explanation": "A bare except catches BaseException, including KeyboardInterrupt (Ctrl+C) and SystemExit, while completely swallowing real bugs without trace."
            },
            {
                "question_text": "In a `try ... except ... else ... finally` block, when does the `else` clause execute?",
                "options": [
                    "Always, right before finally",
                    "Only when an exception was caught and handled",
                    "Only when the try block completed successfully without raising any exceptions",
                    "When the finally block throws an error"
                ],
                "correct": "Only when the try block completed successfully without raising any exceptions",
                "explanation": "The else block runs only if no exception occurred in the try block, separating normal success handling from the guarded code."
            },
            {
                "question_text": "What does `raise CustomError() from original_err` accomplish?",
                "options": [
                    "It deletes original_err from memory",
                    "It chains the exceptions together, preserving original_err as the __cause__ for clear debugging tracebacks",
                    "It converts original_err into a string",
                    "It suppresses the custom error"
                ],
                "correct": "It chains the exceptions together, preserving original_err as the __cause__ for clear debugging tracebacks",
                "explanation": "Explicit exception chaining (raise X from Y) sets the __cause__ attribute, displaying both exceptions in the traceback for complete diagnostic clarity."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Backend Resiliency Layer",
            "task_description": "Build an exception handling and translation layer that wraps external HTTP API client calls into domain-specific exceptions with structured error codes.",
            "starter_code": "def safe_api_client_call(endpoint_func, *args, **kwargs):\n    # Wrap and translate network/HTTP errors\n    pass",
            "rubrics": "Uses custom exception hierarchy, preserves original traceback with from, logs contextual details."
        }
    },

    # -------------------------------------------------------------------------
    # 13. Python Developer — HTTP & REST Architecture Standards
    # -------------------------------------------------------------------------
    {
        "slug": "rest-api-design-architecture",
        "skill_name": "HTTP & REST APIs",
        "title": "HTTP Protocols & RESTful Architecture Standards",
        "concept_name": "HTTP Verbs, Status Codes, Idempotency & Resource Design",
        "difficulty": "Intermediate",
        "estimated_minutes": 25,
        "order_index": 14,
        "prerequisite_concept_slugs": "python-oop-architecture",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Structure clean REST resource URIs using hierarchical noun naming conventions",
            "Master HTTP status code semantics: 200, 201, 204, 400, 401, 403, 404, 422, 500",
            "Understand HTTP method idempotency and safe methods (GET, POST, PUT, PATCH, DELETE)",
        ],
        "explanation": """### Principles of RESTful API Design
Representational State Transfer (REST) is an architectural style centered on **resources** identified by URIs and manipulated using standard HTTP methods.

#### Resource URI Conventions:
* **Use Nouns, Not Verbs**: `/api/v1/orders` (Good) vs `/api/v1/createOrder` (Bad).
* **Plural Nouns**: `/api/v1/users/42/orders`.
* **Sub-resources for Relationships**: `/api/v1/courses/10/modules/3`.

#### HTTP Verbs & Idempotency:
* **Safe Method**: Does not mutate server state (`GET`, `HEAD`, `OPTIONS`).
* **Idempotent Method**: Making the same request 1 time or 100 times results in the **exact same server state**:
  * `GET`: Idempotent & Safe.
  * `PUT`: Idempotent (replaces entire target resource).
  * `DELETE`: Idempotent (deleting once or twice leaves resource absent).
  * `POST`: **NOT idempotent** (calling twice creates two separate records).
  * `PATCH`: Partially modifies resource (conditionally idempotent).

#### HTTP Status Codes:
* `200 OK`: Successful read or update.
* `201 Created`: Resource successfully created (must return new resource or Location header).
* `204 No Content`: Successful action with empty response body (typical for DELETE).
* `400 Bad Request`: Generic malformed client request.
* `401 Unauthorized`: Client is unauthenticated (missing or invalid token).
* `403 Forbidden`: Client is authenticated, but lacks permissions for this resource.
* `404 Not Found`: Target resource does not exist.
* `422 Unprocessable Entity`: Valid syntax, but semantic/schema validation failed.""",
        "key_rules": "- Resource URIs must be plural nouns; verbs belong in the HTTP method\n- Returning 200 with an error JSON body is a severe anti-pattern\n- 401 means unauthenticated; 403 means authenticated but unauthorized",
        "common_mistakes": "- Using GET for state-modifying actions like `/users/delete?id=5`\n- Confusing PUT (complete entity replacement) with PATCH (partial attribute update)\n- Returning 200 OK when an entity creation succeeded (use 201 Created)",
        "worked_example": {
            "scenario": "A backend engineer designs the standard REST API specification for an e-commerce order management subsystem.",
            "code": "# REST Resource Specification\n# 1. List orders:\n#    GET /api/v1/orders?status=active&limit=20 -> 200 OK\n# 2. Create order:\n#    POST /api/v1/orders -> 201 Created (Location: /api/v1/orders/108)\n# 3. Retrieve specific order:\n#    GET /api/v1/orders/108 -> 200 OK\n# 4. Update delivery address partially:\n#    PATCH /api/v1/orders/108 -> 200 OK (Body: {\"shipping_address\": \"...\"})\n# 5. Cancel / Delete order:\n#    DELETE /api/v1/orders/108 -> 204 No Content",
            "reasoning": "Adheres to RESTful nouns, uses proper HTTP verbs, differentiates partial update (PATCH) from full replace (PUT), returns accurate HTTP status codes.",
            "expected_output": "Clean RESTful API contract conforming to OpenAPI 3.0 standards"
        },
        "guided_practice": {
            "prompt": "Determine the correct HTTP verb and status code for each scenario: 1) Creating a new account, 2) Deleting an existing post, 3) Updating a user's avatar URL only.",
            "starter_code": "# Map scenarios to (HTTP_METHOD, STATUS_CODE)\nscenario_1 = None  # Create account\nscenario_2 = None  # Delete post\nscenario_3 = None  # Partial update avatar",
            "solution": "scenario_1 = ('POST', 201)\nscenario_2 = ('DELETE', 204)\nscenario_3 = ('PATCH', 200)",
            "hints": [
                "Creation uses POST with 201 Created.",
                "Deletion uses DELETE with 204 No Content.",
                "Partial update uses PATCH with 200 OK."
            ]
        },
        "independent_practice": {
            "prompt": "Write a Python function `get_status_for_auth(is_logged_in: bool, has_permission: bool) -> int` that returns 401 if not logged in, 403 if logged in but lacks permission, and 200 if authorized.",
            "starter_code": "def get_status_for_auth(is_logged_in: bool, has_permission: bool) -> int:\n    # Return HTTP status code\n    pass",
            "solution": "def get_status_for_auth(is_logged_in: bool, has_permission: bool) -> int:\n    if not is_logged_in:\n        return 401\n    if not has_permission:\n        return 403\n    return 200",
            "test_criteria": "Returns 401 when not logged in, 403 when no permission, 200 when authorized."
        },
        "concept_check": [
            {
                "question_text": "What is the crucial difference between HTTP `PUT` and `PATCH` methods?",
                "options": [
                    "PUT is for databases; PATCH is for static files",
                    "PUT replaces the entire resource representation; PATCH applies a partial update to specific fields",
                    "PATCH is idempotent; PUT is never idempotent",
                    "PUT cannot carry a request body"
                ],
                "correct": "PUT replaces the entire resource representation; PATCH applies a partial update to specific fields",
                "explanation": "PUT is defined by RFC 7231 as full replacement. Any fields omitted in a PUT body are typically reset. PATCH modifies only the specified fields."
            },
            {
                "question_text": "A client sends valid JSON with correct credentials, but attempts to edit an administrative setting reserved for superusers. What status code MUST be returned?",
                "options": ["401 Unauthorized", "403 Forbidden", "404 Not Found", "422 Unprocessable Entity"],
                "correct": "403 Forbidden",
                "explanation": "401 means the server does not know who the client is (unauthenticated). 403 means the server knows the client's identity, but explicitly forbids the action (unauthorized)."
            },
            {
                "question_text": "Which HTTP methods are classified as idempotent?",
                "options": [
                    "POST, PATCH",
                    "GET, PUT, DELETE, HEAD",
                    "POST, PUT",
                    "GET, POST"
                ],
                "correct": "GET, PUT, DELETE, HEAD",
                "explanation": "Idempotent methods guarantee that multiple identical requests produce the exact same server state. GET, PUT, and DELETE are idempotent; POST is not."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Backend API Architecture",
            "task_description": "Design an OpenAPI-compliant REST resource specification for a subscription billing API including endpoint URIs, request schemas, idempotency keys, and error responses.",
            "starter_code": "# Document subscription API endpoints and response codes\n# POST /subscriptions\n# GET /subscriptions/{id}",
            "rubrics": "Uses proper nouns, matches verbs to actions, assigns standard 2xx/4xx/5xx status codes."
        }
    },

    # -------------------------------------------------------------------------
    # 14. Python Developer — FastAPI Rest Endpoints
    # -------------------------------------------------------------------------
    {
        "slug": "fastapi-rest-endpoints",
        "skill_name": "FastAPI",
        "title": "FastAPI Production API Development, Pydantic & Async",
        "concept_name": "APIRouter, Pydantic Models, Dependency Injection & Async Endpoints",
        "difficulty": "Advanced",
        "estimated_minutes": 30,
        "order_index": 16,
        "prerequisite_concept_slugs": "rest-api-design-architecture,python-error-handling-robustness",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Construct modular FastAPI applications using `APIRouter` with prefix and tag organization",
            "Implement request validation and response serialization using Pydantic BaseModel schemas",
            "Leverage FastAPI's `Depends()` dependency injection system for scoped database sessions and authentication",
        ],
        "explanation": """### High-Performance Python APIs with FastAPI
FastAPI is the modern standard for Python backend development. Built on Starlette and Pydantic, it provides automatic OpenAPI documentation, asynchronous request handling, and type-safe dependency injection.

#### Pydantic Schemas vs. SQLAlchemy ORM Models:
* **SQLAlchemy Model**: Maps database tables and relational foreign keys to Python objects.
* **Pydantic Schema**: Defines the strict boundary contract for HTTP request inputs and response outputs.
* In Pydantic v2, use `model_config = ConfigDict(from_attributes=True)` so Pydantic can read attributes directly from ORM objects.

#### The Dependency Injection System:
FastAPI's `Depends()` is extraordinarily powerful. It resolves dependencies hierarchically:
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(\"/users/{user_id}\", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=\"User not found\")
    return user
```

#### Synchronous vs Asynchronous Handlers:
* If using standard blocking database drivers (like default SQLAlchemy SQLite/Postgres), declare endpoints with standard `def`. FastAPI runs them in an external threadpool.
* Only use `async def` if the underlying operations inside the handler use non-blocking `await` (e.g. `httpx.AsyncClient` or asyncpg). Blocking synchronous calls inside `async def` stall the entire event loop!""",
        "key_rules": "- Define separate Pydantic schemas for Request (Create/Update) and Response\n- Always scope database sessions via Depends(get_db) with a yield/finally pattern\n- Raise HTTPException with appropriate status_code for business logic errors",
        "common_mistakes": "- Performing blocking synchronous I/O operations inside an async def handler\n- Returning raw database models instead of Pydantic response_model schemas\n- Exposing sensitive internal fields (like password hashes) in response models",
        "worked_example": {
            "scenario": "A Python developer builds a complete production-grade FastAPI CRUD endpoint for user management with Pydantic validation and dependency injection.",
            "code": "from fastapi import APIRouter, Depends, HTTPException, status\nfrom pydantic import BaseModel, EmailStr, ConfigDict\nfrom typing import List\n\nrouter = APIRouter(prefix=\"/items\", tags=[\"Items\"])\n\nclass ItemCreate(BaseModel):\n    title: str\n    price: float\n    description: str = \"\"\n\nclass ItemResponse(ItemCreate):\n    id: int\n    is_available: bool = True\n    model_config = ConfigDict(from_attributes=True)\n\n# Simulated DB Dependency\ndef get_db_session():\n    db = {\"items\": {}}\n    try:\n        yield db\n    finally:\n        pass\n\n@router.post(\"/\", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)\ndef create_item(payload: ItemCreate, db = Depends(get_db_session)):\n    new_id = len(db[\"items\"]) + 1\n    item = ItemResponse(id=new_id, **payload.model_dump())\n    db[\"items\"][new_id] = item\n    return item",
            "reasoning": "1. Uses ItemCreate schema for input validation. 2. ItemResponse schema excludes sensitive data. 3. Depends(get_db_session) provides clean dependency injection. 4. Returns 201 Created on post.",
            "expected_output": "201 Created with JSON response matching ItemResponse schema"
        },
        "guided_practice": {
            "prompt": "Create a Pydantic schema `UserCreate` with `username: str` and `email: str`. Then write a FastAPI endpoint `@router.post('/users')` that returns the user data with `status_code=201`.",
            "starter_code": "from fastapi import APIRouter, status\nfrom pydantic import BaseModel\n\nrouter = APIRouter()\n\n# Define UserCreate schema\n# Define create_user endpoint",
            "solution": "from fastapi import APIRouter, status\nfrom pydantic import BaseModel, EmailStr\n\nrouter = APIRouter()\n\nclass UserCreate(BaseModel):\n    username: str\n    email: str\n\n@router.post('/users', status_code=status.HTTP_201_CREATED)\ndef create_user(payload: UserCreate):\n    return {\"username\": payload.username, \"email\": payload.email, \"id\": 1}",
            "hints": [
                "Step 1: Inherit UserCreate from BaseModel with username and email fields.",
                "Step 2: Add @router.post('/users', status_code=status.HTTP_201_CREATED).",
                "Step 3: Accept payload: UserCreate and return dictionary."
            ]
        },
        "independent_practice": {
            "prompt": "Write a FastAPI endpoint `@router.get('/products/{product_id}')` that accepts integer `product_id`. If `product_id <= 0`, raise `HTTPException(status_code=400, detail='Invalid product ID')`.",
            "starter_code": "from fastapi import APIRouter, HTTPException\n\nrouter = APIRouter()\n\n# Implement get_product endpoint",
            "solution": "from fastapi import APIRouter, HTTPException\n\nrouter = APIRouter()\n\n@router.get('/products/{product_id}')\ndef get_product(product_id: int):\n    if product_id <= 0:\n        raise HTTPException(status_code=400, detail='Invalid product ID')\n    return {'product_id': product_id, 'name': 'Widget'}",
            "test_criteria": "Uses router.get with path parameter, checks product_id <= 0, raises HTTPException(400)."
        },
        "concept_check": [
            {
                "question_text": "What is the primary danger of running blocking synchronous code (such as requests.get or time.sleep) inside an `async def` FastAPI handler?",
                "options": [
                    "It raises a SyntaxError at compile time",
                    "It blocks the single main event loop thread, preventing the server from handling all other concurrent client requests",
                    "It causes a database transaction rollback",
                    "FastAPI automatically converts it to threading"
                ],
                "correct": "It blocks the single main event loop thread, preventing the server from handling all other concurrent client requests",
                "explanation": "In an async event loop, blocking operations prevent the loop from switching to other concurrent tasks, causing the entire server to freeze for all clients."
            },
            {
                "question_text": "How does FastAPI's `Depends()` mechanism manage resource lifecycles (such as database sessions)?",
                "options": [
                    "It keeps the connection open indefinitely",
                    "If the dependency uses `yield`, FastAPI executes the code before yield prior to the route handler, and executes code after yield (cleanup) after the response is sent",
                    "It delegates cleanup to the operating system",
                    "It only works with Redis"
                ],
                "correct": "If the dependency uses `yield`, FastAPI executes the code before yield prior to the route handler, and executes code after yield (cleanup) after the response is sent",
                "explanation": "FastAPI dependencies supporting yield act as context managers: setup runs before the endpoint handler, and the finally block executes after response generation, guaranteeing session disposal."
            },
            {
                "question_text": "What is the purpose of setting `response_model=UserResponse` in a FastAPI route decorator?",
                "options": [
                    "It encrypts the response using HTTPS",
                    "It validates and filters the output data, stripping any fields not explicitly declared in UserResponse (such as password hashes)",
                    "It restricts requests to authenticated users only",
                    "It automatically creates a database table"
                ],
                "correct": "It validates and filters the output data, stripping any fields not explicitly declared in UserResponse (such as password hashes)",
                "explanation": "response_model guarantees that only authorized fields defined in the schema are serialized into JSON, preventing accidental data leaks."
            }
        ],
        "applied_task": {
            "role_scenario": "FastAPI Production Backend Microservice",
            "task_description": "Build an APIRouter module with dependency-injected database session, Pydantic v2 request/response validation, and 404/422 error handlers for a product catalog.",
            "starter_code": "def build_catalog_router(database_session_dep):\n    # Return configured APIRouter\n    pass",
            "rubrics": "Uses Pydantic schemas, injects db dependency, declares proper status codes, raises HTTPException on missing records."
        }
    },

    # -------------------------------------------------------------------------
    # 15. Python Developer — Automated Testing with PyTest
    # -------------------------------------------------------------------------
    {
        "slug": "pytest-automated-testing",
        "skill_name": "Testing & PyTest",
        "title": "Automated Unit Testing & Mocking with PyTest",
        "concept_name": "PyTest Fixtures, Parametrization, Mocking & Test Isolation",
        "difficulty": "Intermediate",
        "estimated_minutes": 25,
        "order_index": 15,
        "prerequisite_concept_slugs": "python-error-handling-robustness",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Construct isolated, repeatable test fixtures with setup and teardown using `@pytest.fixture`",
            "Run clean test matrices across multiple boundary inputs using `@pytest.mark.parametrize`",
            "Isolate external HTTP calls and database side-effects using `unittest.mock` and `mocker`",
        ],
        "explanation": """### The PyTest Standard in Python Engineering
High-velocity software engineering requires rock-solid automated test suites. PyTest is the undisputed testing standard in Python, offering clean assert syntax, powerful fixtures, parameterization, and mocking.

#### PyTest Fixtures & Scopes:
Fixtures provide repeatable test setups (e.g. database sessions, test clients, dummy models).
```python
@pytest.fixture(scope=\"function\")
def client():
    # Setup
    test_client = TestClient(app)
    yield test_client
    # Teardown (runs automatically after test completes)
```
Scopes include:
* `function` (default): Re-created for every test function, ensuring pure test isolation.
* `module`: Created once per test file.
* `session`: Created once across the entire test run (great for spinning up test Docker containers).

#### Parameterized Tests:
Instead of writing 10 separate test functions for edge cases, use `@pytest.mark.parametrize`:
```python
@pytest.mark.parametrize(\"input_val, expected\", [
    (\"valid@email.com\", True),
    (\"invalid-email\", False),
    (\"\", False),
])
def test_email_validation(input_val, expected):
    assert validate_email(input_val) == expected
```

#### Mocking External Dependencies:
Never make real HTTP calls to external payment gateways or third-party APIs during unit tests. Use `unittest.mock.patch` to simulate responses:
```python
@patch(\"app.services.payment.stripe.Charge.create\")
def test_checkout(mock_stripe):
    mock_stripe.return_value = {\"status\": \"succeeded\", \"id\": \"ch_123\"}
    # Test logic
```""",
        "key_rules": "- Unit tests must run completely offline without real external network calls\n- Use pytest fixtures to maintain pure test isolation between runs\n- Test both the happy path and negative failure edge cases (400, 404, 422)",
        "common_mistakes": "- Writing tests that depend on the execution order of other tests\n- Asserting on unmocked external APIs, causing flaky tests on network drops\n- Forgetting to clean up database state created during integration tests",
        "worked_example": {
            "scenario": "A Python backend engineer writes an automated test suite testing a FastAPI endpoint using PyTest and TestClient with mocked database responses.",
            "code": "import pytest\nfrom fastapi.testclient import TestClient\nfrom unittest.mock import MagicMock\nfrom app.main import app\n\n@pytest.fixture\ndef client():\n    return TestClient(app)\n\n@pytest.mark.parametrize(\"username, email, expected_status\", [\n    (\"validuser\", \"user@example.com\", 201),\n    (\"\", \"user@example.com\", 422),\n    (\"validuser\", \"invalid-email-format\", 422),\n])\ndef test_create_user_validation(client, username, email, expected_status):\n    response = client.post(\"/users\", json={\"username\": username, \"email\": email})\n    assert response.status_code == expected_status",
            "reasoning": "1. client fixture instantiates TestClient. 2. @pytest.mark.parametrize tests three separate payload scenarios in a single concise test function. 3. assert checks HTTP status.",
            "expected_output": "3 passed in 0.12s (100% test isolation)"
        },
        "guided_practice": {
            "prompt": "Write a parameterized PyTest test function `test_calculate_tax` testing `calculate_tax(amount, state)` with cases: (100, 'CA', 10.0), (100, 'TX', 6.25), and (100, 'OR', 0.0).",
            "starter_code": "import pytest\n\n# Implement parameterized test\ndef test_calculate_tax():\n    pass",
            "solution": "import pytest\n\ndef calculate_tax(amount, state):\n    rates = {'CA': 0.10, 'TX': 0.0625, 'OR': 0.0}\n    return amount * rates.get(state, 0.0)\n\n@pytest.mark.parametrize(\"amount, state, expected\", [\n    (100, 'CA', 10.0),\n    (100, 'TX', 6.25),\n    (100, 'OR', 0.0),\n])\ndef test_calculate_tax(amount, state, expected):\n    assert calculate_tax(amount, state) == pytest.approx(expected)",
            "hints": [
                "Step 1: Decorate with @pytest.mark.parametrize('amount, state, expected', [...]).",
                "Step 2: Add parameters to test function signature.",
                "Step 3: Assert calculate_tax(amount, state) == pytest.approx(expected)."
            ]
        },
        "independent_practice": {
            "prompt": "Create a PyTest fixture `dummy_user` that yields a dictionary `{'id': 1, 'role': 'admin'}` and cleans it up after test execution.",
            "starter_code": "import pytest\n\n# Create dummy_user fixture with yield\n@pytest.fixture\ndef dummy_user():\n    pass",
            "solution": "import pytest\n\n@pytest.fixture\ndef dummy_user():\n    user = {'id': 1, 'role': 'admin'}\n    yield user\n    user.clear()",
            "test_criteria": "Uses @pytest.fixture, yields dictionary, executes cleanup after yield."
        },
        "concept_check": [
            {
                "question_text": "What is the primary advantage of `@pytest.mark.parametrize` over writing multiple test functions with copy-pasted logic?",
                "options": [
                    "It compiles the code to WebAssembly",
                    "It runs each parameter set as an independent test report item while eliminating duplicate boilerplate",
                    "It ignores test failures automatically",
                    "It bypasses Pydantic validation"
                ],
                "correct": "It runs each parameter set as an independent test report item while eliminating duplicate boilerplate",
                "explanation": "Parametrization runs each case as a distinct test item. If one case fails, PyTest reports exactly which input failed while continuing to test the others."
            },
            {
                "question_text": "In a PyTest fixture with the `yield` statement, when does the code after `yield` execute?",
                "options": [
                    "Immediately before the test function starts",
                    "Concurrently in a background thread",
                    "After the test function finishes execution (teardown phase)",
                    "Only if the test fails"
                ],
                "correct": "After the test function finishes execution (teardown phase)",
                "explanation": "PyTest fixtures follow context manager semantics: code before yield runs during setup; code after yield runs during teardown, even if the test raised an assertion error."
            },
            {
                "question_text": "Why must external network requests (e.g., Stripe, SendGrid) always be mocked during unit testing?",
                "options": [
                    "Unit tests must be fast, deterministic, and isolated without relying on third-party uptime or network connectivity",
                    "Python does not support sockets in test runners",
                    "PyTest disables DNS resolution by default",
                    "HTTP requests are not permitted in Linux"
                ],
                "correct": "Unit tests must be fast, deterministic, and isolated without relying on third-party uptime or network connectivity",
                "explanation": "Real external calls introduce flakiness, latency, rate-limiting, and cost. Mocking guarantees deterministic tests that run in milliseconds."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Developer CI/CD Automated Test Pipeline",
            "task_description": "Write an automated test suite for an authentication and user management API verifying 200, 201, 401, 404, and 422 HTTP responses with mocked database sessions.",
            "starter_code": "def test_auth_and_user_flows(client, mock_db):\n    # Comprehensive test execution\n    pass",
            "rubrics": "Uses pytest fixtures, tests both valid and invalid payloads, asserts status codes and response bodies."
        }
    },

    # -------------------------------------------------------------------------
    # 16. Python Developer — Containerization & Docker Deployment
    # -------------------------------------------------------------------------
    {
        "slug": "docker-container-deployment",
        "skill_name": "Deployment & Docker",
        "title": "Containerization & Dockerfile Deployment Pipelines",
        "concept_name": "Multi-Stage Dockerfiles, Layer Caching & Container Security",
        "difficulty": "Advanced",
        "estimated_minutes": 25,
        "order_index": 17,
        "prerequisite_concept_slugs": "fastapi-rest-endpoints,pytest-automated-testing",
        "target_role_name": "Python Developer",
        "learning_objectives": [
            "Construct lean, secure multi-stage Dockerfiles minimizing production container attack surfaces",
            "Optimize Docker build cache performance by isolating dependency installation from source code copies",
            "Enforce production security best practices: non-root users, `.dockerignore`, and health check directives",
        ],
        "explanation": """### Containerizing Python Backend Services
In production cloud environments (AWS ECS, Kubernetes, Cloud Run), Python services run inside Docker containers. Writing efficient, secure Dockerfiles is a fundamental engineering competency.

#### Optimizing Docker Layer Caching:
Docker builds images in layers. If a layer hasn't changed, Docker reuses the cached layer:
1. **Bad Practice**: Copying all source code first, then running `pip install`:
   ```dockerfile
   COPY . /app
   RUN pip install -r requirements.txt # Runs on EVERY code change!
   ```
2. **Best Practice**: Copy dependency manifests first:
   ```dockerfile
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt # Cached until requirements.txt changes!
   COPY . .
   ```

#### Multi-Stage Builds:
Build tools (gcc, git, build-essential) are needed to compile C-extensions (like psycopg2 or numpy), but should NEVER exist in the production runtime container.
* **Stage 1 (Builder)**: Install compilers, build wheels.
* **Stage 2 (Runtime)**: Copy pre-built wheels into a slim runtime image (`python:3.11-slim`), reducing image size by 70%.

#### Container Security Essentials:
* **Never Run as Root**: Always create and switch to a non-root user (`USER appuser`).
* **Use `.dockerignore`**: Exclude `.git`, `__pycache__`, `.env`, and test artifacts.
* **Health Checks**: Add `HEALTHCHECK` directive so container orchestrators can detect stalled processes.""",
        "key_rules": "- Copy requirements.txt and install packages BEFORE copying application source code\n- Never run container processes as the default root user in production\n- Use a .dockerignore file to prevent leaking secrets and local virtual environments",
        "common_mistakes": "- Baking secrets or API keys into Dockerfile ENV or RUN instructions\n- Creating bloated multi-gigabyte images by using the full python:3.11 base image instead of slim\n- Forgetting to use --no-cache-dir on pip install, bloating the image layer with package tarballs",
        "worked_example": {
            "scenario": "A Python developer writes a production-grade multi-stage Dockerfile for a FastAPI backend application.",
            "code": "# Stage 1: Build stage\nFROM python:3.11-slim AS builder\nWORKDIR /app\nRUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential\nCOPY requirements.txt .\nRUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt\n\n# Stage 2: Final minimal runtime\nFROM python:3.11-slim\nWORKDIR /app\n\n# Create non-root user\nRUN useradd -m -u 1000 appuser\n\nCOPY --from=builder /app/wheels /wheels\nRUN pip install --no-cache /wheels/* && rm -rf /wheels\n\nCOPY . .\nUSER appuser\n\nEXPOSE 8000\nHEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1\nCMD [\"uvicorn\", \"app.main:app\", \"--host\", \"0.0.0.0\", \"--port\", \"8000\"]",
            "reasoning": "1. Multi-stage builder isolates compilation tools. 2. Final runtime image uses slim base. 3. Runs under non-root appuser. 4. Layer caching isolates dependencies from code changes.",
            "expected_output": "Slim, secure ~120MB production container image"
        },
        "guided_practice": {
            "prompt": "Write a `.dockerignore` file content that ignores `.git`, `.venv`, `__pycache__`, `.env`, and `*.pyc`.",
            "starter_code": "# Complete .dockerignore rules",
            "solution": ".git\n.venv\n__pycache__\n.env\n*.pyc\n.pytest_cache\n.coverage",
            "hints": [
                "Include version control: .git",
                "Include virtual environment: .venv",
                "Include bytecode: __pycache__ and *.pyc",
                "Include environment secrets: .env"
            ]
        },
        "independent_practice": {
            "prompt": "Write a Dockerfile instruction that creates a non-root user named `serviceuser` and switches to that user.",
            "starter_code": "# Add non-root user and switch user",
            "solution": "RUN useradd -m -u 1001 serviceuser\nUSER serviceuser",
            "test_criteria": "Uses useradd or adduser and USER directive."
        },
        "concept_check": [
            {
                "question_text": "Why should `COPY requirements.txt .` and `RUN pip install ...` occur BEFORE `COPY . .` in a Dockerfile?",
                "options": [
                    "Docker requires alphabetical ordering of instructions",
                    "To leverage Docker layer caching, so pip install is not re-executed every time application code changes",
                    "Python dependencies cannot run if source code is already present",
                    "It compiles the code to bytecode automatically"
                ],
                "correct": "To leverage Docker layer caching, so pip install is not re-executed every time application code changes",
                "explanation": "Docker invalidates cache from the first modified layer downwards. By copying requirements first, pip install remains cached across code changes."
            },
            {
                "question_text": "What is the primary security risk of running containerized processes as the default `root` user in production?",
                "options": [
                    "The container will consume double the memory",
                    "If a vulnerability permits a container breakout, the attacker immediately gains root host privileges",
                    "Root users cannot bind to port 8000",
                    "Python disables async I/O when running as root"
                ],
                "correct": "If a vulnerability permits a container breakout, the attacker immediately gains root host privileges",
                "explanation": "If a process inside a container running as root escapes via a container runtime exploit, the attacker possesses root access on the host node."
            },
            {
                "question_text": "What is the primary benefit of Multi-Stage Docker builds?",
                "options": [
                    "They allow running Windows and Linux in the same container",
                    "They separate heavy build tools from the final production runtime image, drastically reducing image size and attack surface",
                    "They eliminate the need for requirements.txt",
                    "They execute tests on multiple CPU architectures simultaneously"
                ],
                "correct": "They separate heavy build tools from the final production runtime image, drastically reducing image size and attack surface",
                "explanation": "Multi-stage builds leave compiler toolchains, package managers, and development headers behind, shipping only runtime binaries in a minimal image."
            }
        ],
        "applied_task": {
            "role_scenario": "Python Cloud Deployment Engineering",
            "task_description": "Write a complete production Dockerfile and docker-compose.yml configuration for a FastAPI application with PostgreSQL database and health checks.",
            "starter_code": "# Write Dockerfile specification\nFROM python:3.11-slim\n# Complete configuration",
            "rubrics": "Uses non-root user, multi-stage or cached layer structure, configures entrypoint uvicorn and health check."
        }
    },

    # -------------------------------------------------------------------------
    # 17. Data Analyst — Advanced SQL Window Functions & Analytics
    # -------------------------------------------------------------------------
    {
        "slug": "sql-window-functions-analytics",
        "skill_name": "SQL",
        "title": "Advanced SQL Window Functions, Ranking & Cohort Analysis",
        "concept_name": "Window Functions, Partitioning, Running Totals & Cohorts",
        "difficulty": "Advanced",
        "estimated_minutes": 35,
        "order_index": 18,
        "prerequisite_concept_slugs": "sql-fundamentals,sql-joins-mastery",
        "target_role_name": "Data Analyst",
        "learning_objectives": [
            "Construct non-collapsing analytical aggregates using the OVER (PARTITION BY ... ORDER BY ...) clause",
            "Distinguish ranking semantics: ROW_NUMBER() vs RANK() vs DENSE_RANK()",
            "Calculate inter-row temporal metrics using LAG() and LEAD() offsets for user retention analysis",
            "Build running totals and moving averages with sliding frame specifications (ROWS BETWEEN)",
        ],
        "subtopics": [
            {"id": "anatomy", "title": "1. Anatomy of the OVER Clause"},
            {"id": "partitioning", "title": "2. PARTITION BY vs. GROUP BY"},
            {"id": "ranking", "title": "3. ROW_NUMBER, RANK, and DENSE_RANK"},
            {"id": "navigation", "title": "4. LAG and LEAD Inter-Row Calculations"},
            {"id": "sliding-frames", "title": "5. Sliding Window Frames (ROWS BETWEEN)"},
            {"id": "worked-example", "title": "6. Real-World Retention Analysis Problem"},
            {"id": "common-mistakes", "title": "7. Common Window Function Pitfalls"},
            {"id": "quick-reference", "title": "8. Window Function Cheat Sheet"},
            {"id": "practice", "title": "9. Guided & Independent Practice Lab"},
            {"id": "concept-check", "title": "10. Formative Concept Check (4 Questions)"},
            {"id": "applied-task", "title": "11. Production Cohort Analysis Task"},
            {"id": "resources", "title": "12. Verified External SQL Documentation"},
        ],
        "why_it_matters_by_role": {
            "Data Analyst": "Window functions are the ultimate divider between junior data clerks and senior analytical powerhouses. Without window functions, computing month-over-month growth, rolling 7-day revenue, or identifying the top 3 purchases per customer requires complex, slow self-joins. Window functions calculate values across rows while preserving individual transactional records.",
            "Data Scientist": "In feature engineering for time-series and user behavior models, window functions create cumulative user aggregates, temporal lags, and recency features directly inside the database before feeding tabular models.",
            "Python Developer": "Understanding window functions allows backend developers to push heavy aggregation logic into relational engines, dramatically cutting network bandwidth and application memory overhead compared to in-memory Python loops."
        },
        "level_variations": {
            "Beginner": {
                "level": "Beginner",
                "focus": "Basic OVER () Syntax & ROW_NUMBER",
                "prerequisite_recap": "Assumes standard SELECT, WHERE, and JOIN knowledge.",
                "explanation_supplement": "Standard GROUP BY collapses multiple rows into a single summary row. Window functions, on the other hand, compute a running aggregate or rank while keeping every single original row in your result table.",
                "key_additions": ["Mental model: transparent sliding glass pane over rows", "OVER () empty window", "ROW_NUMBER() for pagination"]
            },
            "Intermediate": {
                "level": "Intermediate",
                "focus": "PARTITION BY, LAG/LEAD & Cumulative Totals",
                "prerequisite_recap": "Focuses on partitioning sub-cohorts and comparing current row against preceding rows.",
                "explanation_supplement": "Combining PARTITION BY with ORDER BY establishes a separate partition per group (e.g., per customer_id) and applies a running cumulative calculation down the ordered rows.",
                "key_additions": ["LAG() for period-over-period differences", "DENSE_RANK() without gaps", "PARTITION BY multiple columns"]
            },
            "Advanced": {
                "level": "Advanced",
                "focus": "Frame Specifications: ROWS vs RANGE & Performance",
                "prerequisite_recap": "Focuses on deep engine execution and memory optimization for big data warehouses.",
                "explanation_supplement": "Omitting frame specifications defaults to RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW, which can cause subtle duplicate-sorting bugs and quadratic memory usage. Explicitly declare ROWS BETWEEN for linear performance.",
                "key_additions": ["ROWS BETWEEN 6 PRECEDING AND CURRENT ROW for moving averages", "Spill-to-disk mitigation", "Qualify clauses in modern warehouses"]
            }
        },
        "explanation": """### The Power of SQL Window Functions
In traditional SQL aggregations with `GROUP BY`, rows are collapsed into summary groups. While useful for total sums, it eliminates individual row-level detail.

**Window functions** solve this by calculating aggregate or ranking values across a defined set of rows—termed a *window*—while **preserving every original row** in the final output.

#### 1. Core Syntax Anatomy
```sql
FUNCTION() OVER (
    [PARTITION BY partition_column]
    [ORDER BY sort_column ASC|DESC]
    [ROWS BETWEEN frame_start AND frame_end]
)
```

- **`PARTITION BY`**: Divides the dataset into independent logical groups (similar to GROUP BY, but rows are not collapsed).
- **`ORDER BY`**: Dictates the sequence in which the calculation progresses within each partition.
- **`Frame Specification`**: Declares exactly which surrounding rows are included (e.g., `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`).

#### 2. Ranking Functions Comparison
| Function | Duplicate Handling | Example Sequence (values: 100, 100, 80) |
| :--- | :--- | :--- |
| `ROW_NUMBER()` | Assigns arbitrary sequential integer | 1, 2, 3 |
| `RANK()` | Ties get same rank; skips next numbers | 1, 1, 3 |
| `DENSE_RANK()` | Ties get same rank; does NOT skip numbers | 1, 1, 2 |

#### 3. Temporal Navigation with LAG & LEAD
- `LAG(column, offset, default)`: Retrieves a value from *N* rows before the current row. Indispensable for computing month-over-month growth:
$$	ext{MoM Growth} = rac{	ext{Current Revenue} - 	ext{LAG}(	ext{Revenue})}{	ext{LAG}(	ext{Revenue})}$$
- `LEAD(column, offset, default)`: Retrieves a value from *N* rows ahead. Perfect for calculating duration between consecutive user actions.

#### 4. Running Totals & Moving Averages
```sql
SELECT
    order_date,
    amount,
    SUM(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_total,
    AVG(amount) OVER (
        ORDER BY order_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7day_avg
FROM orders;
```
""",
        "key_rules": "- Always specify ORDER BY inside OVER() when computing running totals or ranks\\n- Use DENSE_RANK() if you require continuous ranking sequences without numerical gaps\\n- Explicitly declare ROWS BETWEEN instead of relying on default RANGE frames to ensure linear runtime\\n- Remember that Window Functions execute AFTER WHERE and GROUP BY, so they cannot be filtered directly in WHERE (use CTEs)",
        "common_mistakes": "- Attempting to use window functions directly inside a WHERE clause (must wrap in a CTE or subquery)\\n- Forgetting ORDER BY in running sums, causing the function to sum the entire partition rather than a running total\\n- Confusing RANK() with DENSE_RANK() when calculating leaderboards\\n- Neglecting null handling in LAG/LEAD (always provide the 3rd argument default like 0)",
        "code_examples": [
            {
                "title": "Customer MoM Revenue Growth with LAG()",
                "language": "sql",
                "code": "WITH monthly_rev AS (\\n    SELECT \\n        DATE_TRUNC('month', order_date) AS order_month,\\n        SUM(revenue) AS monthly_sales\\n    FROM fact_orders\\n    GROUP BY 1\\n)\\nSELECT\\n    order_month,\\n    monthly_sales,\\n    LAG(monthly_sales, 1, monthly_sales) OVER (ORDER BY order_month) AS prev_month_sales,\\n    ROUND(\\n        ((monthly_sales - LAG(monthly_sales, 1, monthly_sales) OVER (ORDER BY order_month))::numeric / \\n        NULLIF(LAG(monthly_sales, 1, monthly_sales) OVER (ORDER BY order_month), 0)) * 100,\\n        2\\n    ) AS mom_growth_pct\\nFROM monthly_rev;",
                "explanation": "Calculates monthly aggregate sales in a CTE, then utilizes LAG() to compare current month against prior month and compute exact percentage uplift."
            }
        ],
        "worked_example": {
            "scenario": "A business analytics lead needs to identify the top 2 highest-value orders placed by each corporate account, along with the percentage of that account's total annual spend each order represents.",
            "code": "WITH ranked_orders AS (\\n    SELECT\\n        account_id,\\n        order_id,\\n        order_date,\\n        order_amount,\\n        DENSE_RANK() OVER (PARTITION BY account_id ORDER BY order_amount DESC) AS spend_rank,\\n        SUM(order_amount) OVER (PARTITION BY account_id) AS total_account_spend\\n    FROM fact_orders\\n)\\nSELECT\\n    account_id,\\n    order_id,\\n    order_amount,\\n    total_account_spend,\\n    ROUND((order_amount / total_account_spend) * 100, 2) AS pct_of_account_spend\\nFROM ranked_orders\\nWHERE spend_rank <= 2\\nORDER BY account_id, spend_rank;",
            "reasoning": "Step 1: Partition by account_id and rank orders by amount descending with DENSE_RANK(). Step 2: Compute account-wide total spend using SUM() OVER (PARTITION BY account_id). Step 3: Filter rank <= 2 in outer query.",
            "expected_output": "| account_id | order_id | order_amount | total_account_spend | pct_of_account_spend |\\n| :--- | :--- | :--- | :--- | :--- |\\n| 101 | ORD-9921 | $45,000 | $120,000 | 37.50% |\\n| 101 | ORD-9810 | $35,000 | $120,000 | 29.17% |"
        },
        "quick_reference": {
            "key_terms": [
                {"term": "Window Partition", "definition": "A subset of rows divided by PARTITION BY over which the function independently calculates."},
                {"term": "Running Total", "definition": "Cumulative summation from the start of the partition up to the current row."},
                {"term": "DENSE_RANK()", "definition": "Sequential integer ranking that does not skip numbers when ties occur."},
                {"term": "LAG() / LEAD()", "definition": "Offset navigation functions to access prior or subsequent row values without self-joins."}
            ],
            "formulas_rules": [
                "LAG Syntax: LAG(col, 1, default) OVER (PARTITION BY ... ORDER BY ...)",
                "Running sum: SUM(col) OVER (PARTITION BY group ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)",
                "To filter on window function results: wrap inside WITH cte AS (...) and filter in outer WHERE"
            ],
            "takeaways": [
                "Window functions never collapse row counts.",
                "Always wrap in a CTE when you need to filter on a rank or running total."
            ]
        },
        "guided_practice": {
            "prompt": "Write a SQL query using `ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC)` to select the highest-paid employee per department.",
            "starter_code": "-- Select highest paid employee per department\\nWITH ranked_emp AS (\\n    SELECT id, name, department_id, salary,\\n           -- Your ROW_NUMBER expression here\\n    FROM employees\\n)\\nSELECT id, name, department_id, salary FROM ranked_emp WHERE rnk = 1;",
            "solution": "WITH ranked_emp AS (\\n    SELECT id, name, department_id, salary,\\n           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk\\n    FROM employees\\n)\\nSELECT id, name, department_id, salary FROM ranked_emp WHERE rnk = 1;",
            "hints": [
                "Use ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) AS rnk",
                "Filter WHERE rnk = 1 in the outer query."
            ]
        },
        "independent_practice": {
            "prompt": "Write a query computing the 3-day rolling average revenue for an e-commerce platform using `AVG(revenue) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)`.",
            "starter_code": "-- Compute 3-day rolling average revenue\\nSELECT order_date, revenue,\\n       -- Your rolling average expression here\\nFROM daily_revenue;",
            "solution": "SELECT order_date, revenue,\\n       AVG(revenue) OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS rolling_3day_avg\\nFROM daily_revenue;",
            "test_criteria": "Uses AVG with OVER (ORDER BY order_date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)."
        },
        "concept_check": [
            {
                "question_text": "Why can you NOT filter a window function result directly in the WHERE clause of the same query block?",
                "options": [
                    "Window functions are evaluated in logical query processing after WHERE and GROUP BY have already executed",
                    "Window functions only support integers",
                    "SQL standards disallow CTEs with window functions",
                    "The database index cannot locate the column"
                ],
                "correct": "Window functions are evaluated in logical query processing after WHERE and GROUP BY have already executed",
                "explanation": "In standard SQL logical query processing, WHERE evaluates before SELECT window calculations. Filtering requires wrapping in a CTE or subquery."
            },
            {
                "question_text": "Given salaries [100k, 100k, 90k], what ranks are assigned by RANK() vs DENSE_RANK()?",
                "options": [
                    "RANK: 1, 1, 3 | DENSE_RANK: 1, 1, 2",
                    "RANK: 1, 2, 3 | DENSE_RANK: 1, 1, 1",
                    "RANK: 1, 1, 2 | DENSE_RANK: 1, 1, 3",
                    "Both assign 1, 1, 2"
                ],
                "correct": "RANK: 1, 1, 3 | DENSE_RANK: 1, 1, 2",
                "explanation": "RANK() skips rank numbers after a tie (leaving a gap), whereas DENSE_RANK() continues sequentially with no gaps."
            },
            {
                "question_text": "What does LAG(revenue, 1, 0) return for the very first row in a partition?",
                "options": [
                    "0 (the specified default value)",
                    "NULL",
                    "The current row revenue",
                    "A runtime syntax error"
                ],
                "correct": "0 (the specified default value)",
                "explanation": "Because no preceding row exists for the first element, LAG returns the 3rd argument default (0)."
            }
        ],
        "applied_task": {
            "role_scenario": "Enterprise SaaS Retention & Cohort Analysis",
            "task_description": "Analyze recurring monthly subscription revenue. Calculate user-level monthly spend and use LAG to identify expansion, contraction, or churned customers.",
            "starter_code": "-- Formulate cohort window query\\nSELECT user_id, billing_month, amount FROM subscriptions;",
            "rubrics": "Correctly partitions by user, orders by month, calculates delta using LAG, and classifies expansion vs contraction."
        }
    },
]


# =============================================================================
# Verified External Learning Resources Registry (Sections 12-16)
# Every URL is 100% real, verified, and points to authoritative documentation.
# Zero fabricated URLs.
# =============================================================================
LEARNING_RESOURCES_SEED: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # Python Developer Resources (Tier 1 Official Docs)
    # -------------------------------------------------------------------------
    {
        "title": "Python Official Tutorial: Classes & Object-Oriented Architecture",
        "provider": "Python Official Documentation",
        "url": "https://docs.python.org/3/tutorial/classes.html",
        "skill_name": "OOP",
        "concept_slug": "python-oop-architecture",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "Python Official Tutorial: Errors & Exceptions Handling",
        "provider": "Python Official Documentation",
        "url": "https://docs.python.org/3/tutorial/errors.html",
        "skill_name": "Exception Handling",
        "concept_slug": "python-error-handling-robustness",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 20,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "Python Official Tutorial: Data Structures & Generators",
        "provider": "Python Official Documentation",
        "url": "https://docs.python.org/3/tutorial/datastructures.html",
        "skill_name": "Python Basics",
        "concept_slug": "python-core-fundamentals",
        "role_name": "Python Developer",
        "difficulty": "Beginner",
        "resource_type": "Official Documentation",
        "estimated_minutes": 20,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "FastAPI Official Documentation: First Steps & Routing",
        "provider": "FastAPI Official Documentation",
        "url": "https://fastapi.tiangolo.com/tutorial/first-steps/",
        "skill_name": "FastAPI",
        "concept_slug": "fastapi-rest-endpoints",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "FastAPI Official Documentation: Request Body & Pydantic Validation",
        "provider": "FastAPI Official Documentation",
        "url": "https://fastapi.tiangolo.com/tutorial/body/",
        "skill_name": "FastAPI",
        "concept_slug": "fastapi-rest-endpoints",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 20,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "PyTest Official Documentation: Getting Started & Testing Best Practices",
        "provider": "PyTest Official Documentation",
        "url": "https://docs.pytest.org/en/stable/getting-started.html",
        "skill_name": "Testing & PyTest",
        "concept_slug": "pytest-automated-testing",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "MDN Web Docs: An Overview of HTTP Protocols & REST Standards",
        "provider": "MDN Web Docs",
        "url": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Overview",
        "skill_name": "HTTP & REST APIs",
        "concept_slug": "rest-api-design-architecture",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 20,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "Docker Official Documentation: Containerization & Quickstart",
        "provider": "Docker Official Documentation",
        "url": "https://docs.docker.com/get-started/",
        "skill_name": "Deployment & Docker",
        "concept_slug": "docker-container-deployment",
        "role_name": "Python Developer",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 30,
        "quality_rank": 1,
        "is_active": True,
    },

    # -------------------------------------------------------------------------
    # Data Analyst Resources (Tier 1 Official Docs)
    # -------------------------------------------------------------------------
    {
        "title": "PostgreSQL Documentation: SQL Tutorial & Relational Querying",
        "provider": "PostgreSQL Official Documentation",
        "url": "https://www.postgresql.org/docs/current/tutorial-sql.html",
        "skill_name": "SQL",
        "concept_slug": "sql-fundamentals",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "PostgreSQL Documentation: Table Expressions & Relational JOINs",
        "provider": "PostgreSQL Official Documentation",
        "url": "https://www.postgresql.org/docs/current/queries-table-expressions.html",
        "skill_name": "SQL JOINs",
        "concept_slug": "sql-joins-mastery",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "Microsoft Learn: Quickstart Learn DAX Basics in Power BI Desktop",
        "provider": "Microsoft Learn",
        "url": "https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-quickstart-learn-dax-basics",
        "skill_name": "Power BI",
        "concept_slug": "power-bi-dax-modeling",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 35,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "Pandas Official Documentation: Subsetting & Transforming Data",
        "provider": "Pandas Official Documentation",
        "url": "https://pandas.pydata.org/docs/getting_started/intro_tutorials/03_subset_data.html",
        "skill_name": "Python",
        "concept_slug": "python-pandas-pipelines",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },

    # -------------------------------------------------------------------------
    # Data Scientist Resources (Tier 1 Official Docs & Tier 2 Platforms)
    # -------------------------------------------------------------------------
    {
        "title": "scikit-learn Documentation: Dataset Transformations & Preprocessing",
        "provider": "scikit-learn Documentation",
        "url": "https://scikit-learn.org/stable/modules/preprocessing.html",
        "skill_name": "Machine Learning",
        "concept_slug": "feature-engineering-pipelines",
        "role_name": "Data Scientist",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 30,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "scikit-learn Documentation: Cross-Validation & Metric Evaluation",
        "provider": "scikit-learn Documentation",
        "url": "https://scikit-learn.org/stable/modules/cross_validation.html",
        "skill_name": "Machine Learning",
        "concept_slug": "model-evaluation-metrics",
        "role_name": "Data Scientist",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 30,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "scikit-learn Documentation: Supervised Learning Foundations",
        "provider": "scikit-learn Documentation",
        "url": "https://scikit-learn.org/stable/tutorial/basic/tutorial.html",
        "skill_name": "Machine Learning",
        "concept_slug": "machine-learning-foundations",
        "role_name": "Data Scientist",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 30,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "Kaggle Learn: Feature Engineering Pipelines Course",
        "provider": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn/feature-engineering",
        "skill_name": "Machine Learning",
        "concept_slug": "feature-engineering-pipelines",
        "role_name": "Data Scientist",
        "difficulty": "Intermediate",
        "resource_type": "Interactive Course",
        "estimated_minutes": 45,
        "quality_rank": 2,
        "is_active": True,
    },
    {
        "title": "Kaggle Learn: Intro to Machine Learning Hands-On",
        "provider": "Kaggle Learn",
        "url": "https://www.kaggle.com/learn/intro-to-machine-learning",
        "skill_name": "Machine Learning",
        "concept_slug": "machine-learning-foundations",
        "role_name": "Data Scientist",
        "difficulty": "Beginner",
        "resource_type": "Interactive Course",
        "estimated_minutes": 40,
        "quality_rank": 2,
        "is_active": True,
    },

    # -------------------------------------------------------------------------
    # Applied Statistics & Hypothesis Testing (Khan Academy, SciPy, GeeksforGeeks)
    # -------------------------------------------------------------------------
    {
        "title": "Khan Academy: Significance Tests & One-Sample Hypothesis Testing",
        "provider": "Khan Academy",
        "url": "https://www.khanacademy.org/math/statistics-probability/significance-tests-one-sample",
        "skill_name": "Statistics",
        "concept_slug": "statistics-hypothesis-testing",
        "role_name": "All",
        "difficulty": "Beginner",
        "resource_type": "Structured Course & Practice",
        "estimated_minutes": 35,
        "quality_rank": 2,
        "is_active": True,
    },
    {
        "title": "SciPy Official Documentation: Statistical Tests & Distributions (scipy.stats)",
        "provider": "SciPy Official Documentation",
        "url": "https://docs.scipy.org/doc/scipy/reference/stats.html",
        "skill_name": "Statistics",
        "concept_slug": "statistics-hypothesis-testing",
        "role_name": "All",
        "difficulty": "Intermediate",
        "resource_type": "Official Documentation",
        "estimated_minutes": 25,
        "quality_rank": 1,
        "is_active": True,
    },
    {
        "title": "GeeksforGeeks: P-Value in Statistics & Hypothesis Testing in Python",
        "provider": "GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/p-value/",
        "skill_name": "Statistics",
        "concept_slug": "statistics-hypothesis-testing",
        "role_name": "All",
        "difficulty": "Intermediate",
        "resource_type": "Educational Platform & Code Examples",
        "estimated_minutes": 20,
        "quality_rank": 2,
        "is_active": True,
    },
    # -------------------------------------------------------------------------
    # Core Verified Multi-Platform Learning Resources (Phase 21)
    # -------------------------------------------------------------------------
    {
        "title": "SQL JOIN: Complete Guide to Inner, Left, Right and Full Joins",
        "provider": "GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/sql-join-set-1-inner-left-right-and-full-joins/",
        "skill_name": "SQL JOINs",
        "concept_slug": "sql-joins-mastery",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 25,
        "quality_rank": 2,
        "description": "Learn INNER JOIN, LEFT JOIN, RIGHT JOIN and FULL OUTER JOIN with visual Venn diagrams and SQL syntax queries.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "W3Schools SQL Joins Interactive Reference",
        "provider": "W3Schools",
        "url": "https://www.w3schools.com/sql/sql_join.asp",
        "skill_name": "SQL JOINs",
        "concept_slug": "sql-joins-mastery",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 20,
        "quality_rank": 2,
        "description": "Hands-on interactive try-it-yourself exercises explaining table relationships and join operations.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "Joining Related Tables in Relational SQL",
        "provider": "Khan Academy",
        "url": "https://www.khanacademy.org/computing/computer-programming/sql/relational-queries-in-sql/a/joining-related-tables",
        "skill_name": "SQL JOINs",
        "concept_slug": "sql-joins-mastery",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Course",
        "estimated_minutes": 25,
        "quality_rank": 2,
        "description": "Foundational curriculum explaining relational database modeling, foreign keys, and multi-table queries.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "Coursera: SQL for Data Science — Joining Tables",
        "provider": "Coursera",
        "url": "https://www.coursera.org/learn/sql-for-data-science",
        "skill_name": "SQL JOINs",
        "concept_slug": "sql-joins-mastery",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Structured Course",
        "estimated_minutes": 45,
        "quality_rank": 2,
        "description": "University-backed coursework on writing production SQL joins and optimizing relational joins.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "DataCamp: Joining Data in Relational SQL",
        "provider": "DataCamp",
        "url": "https://www.datacamp.com/tutorial/joins-in-sql",
        "skill_name": "SQL JOINs",
        "concept_slug": "sql-joins-mastery",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 30,
        "quality_rank": 2,
        "description": "Interactive data science tutorial on inner joins, left joins, and semi-joins for real-world datasets.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "GeeksforGeeks: SQL Commands — DDL, DQL, DML & TCL",
        "provider": "GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/sql-ddl-dql-dml-dcl-tcl-commands/",
        "skill_name": "SQL",
        "concept_slug": "sql-fundamentals",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 20,
        "quality_rank": 2,
        "description": "Core guide to SELECT statements, filtering with WHERE, aggregate calculations, and grouping.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "W3Schools: SQL SELECT and Filtering Exercises",
        "provider": "W3Schools",
        "url": "https://www.w3schools.com/sql/sql_select.asp",
        "skill_name": "SQL",
        "concept_slug": "sql-fundamentals",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 20,
        "quality_rank": 2,
        "description": "Beginner reference with browser-based query execution for SELECT, WHERE, and ORDER BY.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "Khan Academy: Welcome to SQL & Relational Databases",
        "provider": "Khan Academy",
        "url": "https://www.khanacademy.org/computing/computer-programming/sql/sql-basics/v/welcome-to-sql",
        "skill_name": "SQL",
        "concept_slug": "sql-fundamentals",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Course",
        "estimated_minutes": 25,
        "quality_rank": 2,
        "description": "Gentle, interactive introduction to relational databases and table creation.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "Coursera: Introduction to Structured Query Language (SQL)",
        "provider": "Coursera",
        "url": "https://www.coursera.org/learn/intro-sql",
        "skill_name": "SQL",
        "concept_slug": "sql-fundamentals",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Structured Course",
        "estimated_minutes": 45,
        "quality_rank": 2,
        "description": "Academic foundation in database design, relational integrity, and standard SQL operations.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "DataCamp: Introduction to SQL for Data Analysis",
        "provider": "DataCamp",
        "url": "https://www.datacamp.com/courses/introduction-to-sql",
        "skill_name": "SQL",
        "concept_slug": "sql-fundamentals",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Course",
        "estimated_minutes": 30,
        "quality_rank": 2,
        "description": "Hands-on browser queries filtering, aggregating, and summarizing tabular data.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "GeeksforGeeks: Python Programming Language Syntax Guide",
        "provider": "GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/python-programming-language/",
        "skill_name": "Python Basics",
        "concept_slug": "python-core-fundamentals",
        "role_name": "Python Developer",
        "difficulty": "Beginner",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 25,
        "quality_rank": 2,
        "description": "Comprehensive reference covering Python variables, conditionals, loops, and built-in functions.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "W3Schools: Python Introduction and Syntax Exercises",
        "provider": "W3Schools",
        "url": "https://www.w3schools.com/python/python_intro.asp",
        "skill_name": "Python Basics",
        "concept_slug": "python-core-fundamentals",
        "role_name": "Python Developer",
        "difficulty": "Beginner",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 20,
        "quality_rank": 2,
        "description": "Simple, accessible code runner tutorials for fundamental Python syntax.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "Coursera: Programming for Everybody (Getting Started with Python)",
        "provider": "Coursera",
        "url": "https://www.coursera.org/learn/python",
        "skill_name": "Python Basics",
        "concept_slug": "python-core-fundamentals",
        "role_name": "Python Developer",
        "difficulty": "Beginner",
        "resource_type": "Structured Course",
        "estimated_minutes": 50,
        "quality_rank": 2,
        "description": "University of Michigan foundational programming course covering data structures and execution flow.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "DataCamp: Introduction to Python for Data Science",
        "provider": "DataCamp",
        "url": "https://www.datacamp.com/courses/intro-to-python-for-data-science",
        "skill_name": "Python Basics",
        "concept_slug": "python-core-fundamentals",
        "role_name": "Python Developer",
        "difficulty": "Beginner",
        "resource_type": "Interactive Course",
        "estimated_minutes": 30,
        "quality_rank": 2,
        "description": "Interactive coding challenges teaching Python lists, functions, and packages.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "GeeksforGeeks: Pandas Tutorial — Data Manipulation in Python",
        "provider": "GeeksforGeeks",
        "url": "https://www.geeksforgeeks.org/pandas-tutorial/",
        "skill_name": "Python",
        "concept_slug": "python-pandas-pipelines",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 30,
        "quality_rank": 2,
        "description": "Practical guide covering Series, DataFrames, indexing, grouping, and aggregations in Pandas.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "W3Schools: Python Pandas Module Guide & Examples",
        "provider": "W3Schools",
        "url": "https://www.w3schools.com/python/pandas/default.asp",
        "skill_name": "Python",
        "concept_slug": "python-pandas-pipelines",
        "role_name": "Data Analyst",
        "difficulty": "Beginner",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 20,
        "quality_rank": 2,
        "description": "Clean reference guide on reading CSVs, analyzing data, and cleaning empty values.",
        "verified": True,
        "is_active": True,
    },
    {
        "title": "DataCamp: Pandas DataFrame Tutorial",
        "provider": "DataCamp",
        "url": "https://www.datacamp.com/tutorial/pandas",
        "skill_name": "Python",
        "concept_slug": "python-pandas-pipelines",
        "role_name": "Data Analyst",
        "difficulty": "Intermediate",
        "resource_type": "Interactive Tutorial",
        "estimated_minutes": 35,
        "quality_rank": 2,
        "description": "Deep dive into creating, reshaping, and merging Pandas DataFrames.",
        "verified": True,
        "is_active": True,
    },
]

