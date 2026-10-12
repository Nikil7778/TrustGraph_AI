import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.role import Role, RoleSkill
from app.models.skill import Skill
from app.models.user import User, UserSkill
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentAttempt
from app.models.activity import LearningActivity
from app.models.evidence import SkillEvidence
from app.models.roadmap import Roadmap, RoadmapStep
from app.models.project import Project, ProjectAttempt
from app.models.industry_lab import IndustryLab, IndustryLabTask, IndustryLabAttempt


def seed_database(db: Session) -> None:
    """
    Idempotent seed script to populate database with benchmark Data Science roles,
    competencies, 7 diagnostic assessments with 70 questions, and demo learner Alex Mercer.
    """
    # 1. Seed Roles
    roles_data = [
        {"name": "Data Analyst", "description": "Analytic synthesis, SQL data wrangling, EDA, and executive dashboards."},
        {"name": "Data Scientist", "description": "Statistical modeling, Python predictive analytics, machine learning pipelines."},
        {"name": "ML Engineer", "description": "Production ML model deployment, MLOps, deep learning, scalable feature engineering."},
    ]

    role_objs = {}
    for r in roles_data:
        existing = db.query(Role).filter(Role.name == r["name"]).first()
        if not existing:
            existing = Role(name=r["name"], description=r["description"])
            db.add(existing)
            db.commit()
            db.refresh(existing)
        role_objs[r["name"]] = existing

    # 2. Seed Skills
    skills_data = [
        {"name": "Python", "category": "Programming & Data Manipulation", "description": "Python data structures, Pandas, and NumPy pipelines."},
        {"name": "SQL", "category": "Database Querying", "description": "Relational query filtering, aggregations, and CTEs."},
        {"name": "SQL JOINs", "category": "Database Querying", "description": "Inner, outer, self, and cross joins across multi-table schema."},
        {"name": "Statistics", "category": "Quantitative Analysis", "description": "Descriptive & inferential statistics, hypothesis testing."},
        {"name": "EDA", "category": "Data Science Workflow", "description": "Exploratory Data Analysis, missing value treatment, outlier detection."},
        {"name": "Data Visualization", "category": "Business Intelligence & Reporting", "description": "Chart design, Matplotlib, Seaborn, and visual communication."},
        {"name": "Power BI", "category": "Business Intelligence & Reporting", "description": "DAX calculations, data modeling, executive dashboards."},
        {"name": "Machine Learning", "category": "Predictive Modeling", "description": "Supervised & unsupervised ML algorithms, model evaluation."},
    ]

    skill_objs = {}
    for s in skills_data:
        existing = db.query(Skill).filter(Skill.name == s["name"]).first()
        if not existing:
            existing = Skill(name=s["name"], category=s["category"], description=s["description"])
            db.add(existing)
            db.commit()
            db.refresh(existing)
        skill_objs[s["name"]] = existing

    # 3. Seed RoleSkills (Data Analyst benchmark)
    da_role = role_objs["Data Analyst"]
    da_benchmarks = [
        ("Python", 80, 80, "High"),
        ("SQL", 85, 85, "High"),
        ("SQL JOINs", 90, 80, "High"),
        ("Statistics", 75, 75, "Medium"),
        ("EDA", 85, 85, "High"),
        ("Data Visualization", 80, 80, "High"),
        ("Power BI", 75, 70, "High"),
        ("Machine Learning", 40, 50, "Low"),
    ]

    for skill_name, importance, required_level, ind_rel in da_benchmarks:
        skill = skill_objs[skill_name]
        rs = db.query(RoleSkill).filter_by(role_id=da_role.id, skill_id=skill.id).first()
        if not rs:
            rs = RoleSkill(
                role_id=da_role.id,
                skill_id=skill.id,
                importance_score=importance,
                industry_relevance=ind_rel,
                required_level=required_level,
            )
            db.add(rs)
        else:
            rs.importance_score = importance
            rs.industry_relevance = ind_rel
            rs.required_level = required_level
    db.commit()

    # 4. Seed Demo Learner (Alex Mercer)
    alex = db.query(User).filter(User.email == "alex.mercer@example.com").first()
    if not alex:
        alex = User(
            name="Alex Mercer",
            email="alex.mercer@example.com",
            experience_level="Intermediate",
            target_role_id=da_role.id,
            weekly_learning_hours=12,
            learning_goal="Transition to Senior Data Analyst position",
        )
        db.add(alex)
        db.commit()
        db.refresh(alex)

    # 5. Seed Alex Mercer Skill DNA
    alex_dna_scores = [
        ("Python", 85.0, 92.0, 88.0, 14),
        ("SQL", 76.0, 78.0, 74.0, 9),
        ("SQL JOINs", 42.0, 45.0, 40.0, 3),  # Critical Skill Debt
        ("Statistics", 81.0, 85.0, 82.0, 11),
        ("EDA", 65.0, 68.0, 62.0, 6),
        ("Data Visualization", 70.0, 72.0, 68.0, 5),
        ("Power BI", 38.0, 40.0, 35.0, 2),  # Skill Debt
        ("Machine Learning", 35.0, 35.0, 30.0, 1),
    ]

    for skill_name, level, conf, acc, ev_count in alex_dna_scores:
        skill = skill_objs[skill_name]
        us = db.query(UserSkill).filter_by(user_id=alex.id, skill_id=skill.id).first()
        if not us:
            us = UserSkill(
                user_id=alex.id,
                skill_id=skill.id,
                skill_level=level,
                confidence=conf,
                accuracy=acc,
                difficulty="Intermediate",
                recency="2 days ago" if level > 70 else "1 week ago",
                evidence_score=ev_count * 5.0,
                last_assessed_at=datetime.utcnow(),
            )
            db.add(us)
    db.commit()

    # 6. Seed Assessments & 10 Deterministic Questions per skill (7 Skills = 70 Questions)
    assessments_spec = [
        {
            "skill_name": "SQL JOINs",
            "title": "SQL Join & Relational Queries Assessment",
            "description": "Diagnostic assessment evaluating inner, left, right, full, and self joins across relational schemas.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which SQL JOIN returns all records from the left table and matched records from the right table?",
                    "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
                    "correct": "LEFT JOIN",
                    "diff": "Easy",
                    "exp": "LEFT JOIN preserves all rows from the left table regardless of matching right table rows.",
                },
                {
                    "text": "What happens to rows in a LEFT JOIN when there is no matching record in the right table?",
                    "options": ["The left row is dropped", "The right columns display NULL values", "An error is raised", "The join converts to an INNER JOIN"],
                    "correct": "The right columns display NULL values",
                    "diff": "Easy",
                    "exp": "Unmatched right-side columns are populated with NULL values.",
                },
                {
                    "text": "Which clause is used to filter aggregated results produced after a JOIN and GROUP BY?",
                    "options": ["WHERE", "HAVING", "ORDER BY", "FILTER"],
                    "correct": "HAVING",
                    "diff": "Easy",
                    "exp": "HAVING filters aggregated grouped records, whereas WHERE filters individual rows prior to grouping.",
                },
                {
                    "text": "If Table A has 5 rows and Table B has 10 rows, how many rows will a CROSS JOIN return?",
                    "options": ["5", "10", "15", "50"],
                    "correct": "50",
                    "diff": "Medium",
                    "exp": "CROSS JOIN produces a Cartesian product (5 * 10 = 50 rows).",
                },
                {
                    "text": "How do you join a table to itself in SQL to find employee-manager relationships?",
                    "options": ["SELF JOIN using aliased table names", "CROSS JOIN with GROUP BY", "FULL OUTER JOIN without ON clause", "UNION ALL"],
                    "correct": "SELF JOIN using aliased table names",
                    "diff": "Medium",
                    "exp": "A table is joined to itself by referencing it twice with distinct aliases (e.g., e AS emp JOIN e AS mgr).",
                },
                {
                    "text": "What is the primary difference between UNION and UNION ALL after combining joined queries?",
                    "options": ["UNION ALL removes duplicate rows", "UNION removes duplicate rows; UNION ALL keeps duplicates", "UNION works only on integers", "UNION ALL is slower than UNION"],
                    "correct": "UNION removes duplicate rows; UNION ALL keeps duplicates",
                    "diff": "Medium",
                    "exp": "UNION performs duplicate elimination, whereas UNION ALL concatenates all rows directly.",
                },
                {
                    "text": "Which join type returns ONLY rows that have matching values in both tables?",
                    "options": ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL JOIN"],
                    "correct": "INNER JOIN",
                    "diff": "Medium",
                    "exp": "INNER JOIN filters out rows that do not satisfy the join predicate in both tables.",
                },
                {
                    "text": "In PostgreSQL/MySQL, what is the outcome of joining on a column containing NULL values?",
                    "options": ["NULL matches NULL", "NULL does not match NULL (NULL = NULL evaluates to UNKNOWN)", "It throws a syntax error", "It performs an implicit CROSS JOIN"],
                    "correct": "NULL does not match NULL (NULL = NULL evaluates to UNKNOWN)",
                    "diff": "Hard",
                    "exp": "In standard SQL, NULL = NULL evaluates to UNKNOWN, so rows with NULL join keys will not match in INNER JOIN.",
                },
                {
                    "text": "When executing a LEFT JOIN with a WHERE condition on the right table (e.g. WHERE right.status = 'active'), what does the query effectively convert into?",
                    "options": ["A CROSS JOIN", "An INNER JOIN (unless IS NULL is handled)", "A FULL OUTER JOIN", "A Subquery"],
                    "correct": "An INNER JOIN (unless IS NULL is handled)",
                    "diff": "Hard",
                    "exp": "Filtering a right table column in WHERE filters out NULLs generated by un-matched left rows, converting the LEFT JOIN into an INNER JOIN.",
                },
                {
                    "text": "How does USING(customer_id) differ from ON a.customer_id = b.customer_id in an INNER JOIN?",
                    "options": ["USING requires different column names", "USING eliminates duplicate customer_id columns from SELECT * output", "USING is only supported in SQLite", "ON is faster"],
                    "correct": "USING eliminates duplicate customer_id columns from SELECT * output",
                    "diff": "Hard",
                    "exp": "USING(col) coalesces the join column into a single output column when executing SELECT *.",
                },
            ],
        },
        {
            "skill_name": "Python",
            "title": "Python Data Wrangling & Pandas Assessment",
            "description": "Diagnostic evaluation covering Pandas DataFrames, NumPy vectorization, and data transformation.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which Pandas function is used to read a CSV file into a DataFrame?",
                    "options": ["pd.read_csv()", "pd.import_csv()", "pd.load_csv()", "pd.open_csv()"],
                    "correct": "pd.read_csv()",
                    "diff": "Easy",
                    "exp": "pd.read_csv() parses CSV files into a Pandas DataFrame.",
                },
                {
                    "text": "What is the primary difference between df.loc[] and df.iloc[] in Pandas?",
                    "options": ["df.loc uses integer position; df.iloc uses labels", "df.loc uses label indexers; df.iloc uses integer position indexers", "df.loc is for rows; df.iloc is for columns", "They are identical"],
                    "correct": "df.loc uses label indexers; df.iloc uses integer position indexers",
                    "diff": "Easy",
                    "exp": "loc selects data by index labels, whereas iloc selects by integer positional offsets.",
                },
                {
                    "text": "Which Pandas method removes duplicate rows from a DataFrame?",
                    "options": ["df.drop_duplicates()", "df.remove_duplicates()", "df.unique()", "df.distinct()"],
                    "correct": "df.drop_duplicates()",
                    "diff": "Easy",
                    "exp": "df.drop_duplicates() returns a DataFrame with duplicate rows removed.",
                },
                {
                    "text": "How do you fill missing NaN values in a Pandas Series with a constant value 0?",
                    "options": ["series.fillna(0)", "series.replace_na(0)", "series.dropna(0)", "series.clean(0)"],
                    "correct": "series.fillna(0)",
                    "diff": "Medium",
                    "exp": "fillna() replaces NaN values with the specified scalar value or method.",
                },
                {
                    "text": "Which Pandas operation aggregates data across groups defined by categorical keys?",
                    "options": ["df.aggregate()", "df.groupby()", "df.pivot()", "df.sort_values()"],
                    "correct": "df.groupby()",
                    "diff": "Medium",
                    "exp": "groupby() splits data into groups for application of aggregate functions like sum() or mean().",
                },
                {
                    "text": "What does df.apply(lambda x: x.max() - x.min()) execute when axis=0?",
                    "options": ["Calculates range for each row", "Calculates range for each column", "Applies string formatting", "Returns scalar total"],
                    "correct": "Calculates range for each column",
                    "diff": "Medium",
                    "exp": "axis=0 applies the function independently across column series.",
                },
                {
                    "text": "Which Pandas method merges two DataFrames based on a shared key column?",
                    "options": ["pd.concat()", "pd.merge()", "pd.append()", "pd.combine()"],
                    "correct": "pd.merge()",
                    "diff": "Medium",
                    "exp": "pd.merge() performs relational join operations on DataFrames.",
                },
                {
                    "text": "What is memory-efficient method to convert string column with few unique values in Pandas?",
                    "options": ["astypes('category')", "astype('int64')", "astype('object')", "to_dense()"],
                    "correct": "astypes('category')",
                    "diff": "Hard",
                    "exp": "Categorical dtype reduces memory usage for low-cardinality string columns.",
                },
                {
                    "text": "What does df.assign() return in Pandas pipeline chaining?",
                    "options": ["In-place mutated DataFrame", "New DataFrame with new columns assigned", "Series of column names", "Tuple of DataFrames"],
                    "correct": "New DataFrame with new columns assigned",
                    "diff": "Hard",
                    "exp": "df.assign() returns a new DataFrame copy with added/modified columns, facilitating method chaining.",
                },
                {
                    "text": "What occurs when performing vectorized operation df['A'] + df['B'] when indices do not align?",
                    "options": ["Throws ValueError", "Pandas aligns by index labels, inserting NaNs for unaligned indices", "Truncates longer DataFrame", "Uses integer positions"],
                    "correct": "Pandas aligns by index labels, inserting NaNs for unaligned indices",
                    "diff": "Hard",
                    "exp": "Pandas automatically aligns series by index label prior to computation.",
                },
            ],
        },
        {
            "skill_name": "SQL",
            "title": "SQL Querying & Data Extraction Assessment",
            "description": "Evaluation of core relational SQL queries, filtering, aggregation, and subqueries.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which SQL keyword is used to retrieve distinct values from a column?",
                    "options": ["UNIQUE", "DISTINCT", "DIFFERENT", "SINGLE"],
                    "correct": "DISTINCT",
                    "diff": "Easy",
                    "exp": "SELECT DISTINCT removes duplicate rows from the query output.",
                },
                {
                    "text": "Which operator filters rows matching a pattern using wildcards like % or _?",
                    "options": ["MATCH", "LIKE", "CONTAINS", "SEARCH"],
                    "correct": "LIKE",
                    "diff": "Easy",
                    "exp": "LIKE operator compares string columns against wildcard patterns.",
                },
                {
                    "text": "What does the aggregate function COUNT(*) return?",
                    "options": ["Number of non-null values in first column", "Total number of rows in the table/result", "Sum of all numerical values", "Number of distinct columns"],
                    "correct": "Total number of rows in the table/result",
                    "diff": "Easy",
                    "exp": "COUNT(*) counts all rows matching the predicate, including NULLs.",
                },
                {
                    "text": "What is the purpose of the SQL clause GROUP BY?",
                    "options": ["Sort output rows alphabetically", "Group rows that have the same values into summary rows", "Filter individual rows prior to selection", "Create a virtual view"],
                    "correct": "Group rows that have the same values into summary rows",
                    "diff": "Medium",
                    "exp": "GROUP BY aggregates data rows into summary buckets for aggregate functions.",
                },
                {
                    "text": "Which SQL window function assigns a rank to each row within a partition without gaps?",
                    "options": ["RANK()", "DENSE_RANK()", "ROW_NUMBER()", "PERCENT_RANK()"],
                    "correct": "DENSE_RANK()",
                    "diff": "Medium",
                    "exp": "DENSE_RANK() assigns consecutive rank numbers without leaving gaps after ties.",
                },
                {
                    "text": "How do CTEs (Common Table Expressions) begin in standard SQL?",
                    "options": ["CREATE CTE name AS", "WITH name AS (...)", "DEFINE CTE name", "SELECT CTE name"],
                    "correct": "WITH name AS (...)",
                    "diff": "Medium",
                    "exp": "CTEs are defined using the WITH clause prior to the main query.",
                },
                {
                    "text": "Which SQL clause limits the number of rows returned by a query?",
                    "options": ["TOP / LIMIT", "WHERE", "GROUP BY", "HAVING"],
                    "correct": "TOP / LIMIT",
                    "diff": "Medium",
                    "exp": "LIMIT (or TOP in SQL Server) restricts result set row counts.",
                },
                {
                    "text": "What does COALESCE(val1, val2, val3) return in SQL?",
                    "options": ["Sum of all non-null values", "First non-null expression in the argument list", "True if all values match", "Concatenated string"],
                    "correct": "First non-null expression in the argument list",
                    "diff": "Hard",
                    "exp": "COALESCE returns the first non-NULL expression among its arguments.",
                },
                {
                    "text": "What distinguishes a Correlated Subquery from a Standard Subquery?",
                    "options": ["A correlated subquery executes independently once", "A correlated subquery references columns from the outer query and executes per outer row", "A correlated subquery returns only boolean values", "A correlated subquery requires UNION"],
                    "correct": "A correlated subquery references columns from the outer query and executes per outer row",
                    "diff": "Hard",
                    "exp": "Correlated subqueries depend on outer query column values.",
                },
                {
                    "text": "What is the effect of EXPLAIN ANALYZE in PostgreSQL?",
                    "options": ["Modifies query plan dynamically", "Executes the statement and returns actual execution time and node counts", "Syntax validation without running query", "Creates database indexes"],
                    "correct": "Executes the statement and returns actual execution time and node counts",
                    "diff": "Hard",
                    "exp": "EXPLAIN ANALYZE executes the query to report actual cost and time execution stats.",
                },
            ],
        },
        {
            "skill_name": "Statistics",
            "title": "Applied Inferential & Descriptive Statistics Assessment",
            "description": "Evaluation of mean, median, standard deviation, hypothesis testing, and p-values.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which measure of central tendency is least sensitive to extreme outliers?",
                    "options": ["Mean", "Median", "Mode", "Standard Deviation"],
                    "correct": "Median",
                    "diff": "Easy",
                    "exp": "The median represents the 50th percentile and is robust against extreme skewed outliers.",
                },
                {
                    "text": "What does a p-value less than alpha (e.g. 0.05) indicate in hypothesis testing?",
                    "options": ["Fail to reject the null hypothesis", "Reject the null hypothesis (statistically significant result)", "Accept the null hypothesis as true", "The test was executed incorrectly"],
                    "correct": "Reject the null hypothesis (statistically significant result)",
                    "diff": "Easy",
                    "exp": "p < 0.05 indicates observed evidence is unlikely under the null hypothesis.",
                },
                {
                    "text": "What does standard deviation measure in a dataset?",
                    "options": ["The middle value of dataset", "The spread or dispersion of data points around the mean", "The total count of data points", "The probability of error"],
                    "correct": "The spread or dispersion of data points around the mean",
                    "diff": "Easy",
                    "exp": "Standard deviation measures average variation from the mean.",
                },
                {
                    "text": "What is a Type I error in statistical hypothesis testing?",
                    "options": ["Failing to reject a false null hypothesis", "Rejecting a true null hypothesis (False Positive)", "Calculating incorrect mean", "Using small sample size"],
                    "correct": "Rejecting a true null hypothesis (False Positive)",
                    "diff": "Medium",
                    "exp": "Type I error occurs when a true null hypothesis is incorrectly rejected.",
                },
                {
                    "text": "What does Central Limit Theorem state about sample means as sample size n increases?",
                    "options": ["Sample mean becomes zero", "Distribution of sample means approaches a normal distribution regardless of population shape", "Standard deviation increases", "Data becomes uniform"],
                    "correct": "Distribution of sample means approaches a normal distribution regardless of population shape",
                    "diff": "Medium",
                    "exp": "CLT guarantees sampling distribution of mean approaches normal as n grows large.",
                },
                {
                    "text": "What range of values can Pearson correlation coefficient r take?",
                    "options": ["0 to 100", "-1.0 to +1.0", "-infinity to +infinity", "0.0 to 1.0"],
                    "correct": "-1.0 to +1.0",
                    "diff": "Medium",
                    "exp": "Pearson r ranges between -1 (perfect negative) and +1 (perfect positive correlation).",
                },
                {
                    "text": "Which statistical test compares means of two independent sample groups?",
                    "options": ["Chi-Square Test", "Two-Sample t-Test", "ANOVA", "Linear Regression"],
                    "correct": "Two-Sample t-Test",
                    "diff": "Medium",
                    "exp": "Two-sample t-test evaluates mean differences between two independent groups.",
                },
                {
                    "text": "What does Interquartile Range (IQR) represent?",
                    "options": ["Difference between maximum and minimum value", "Difference between 75th percentile (Q3) and 25th percentile (Q1)", "Ratio of mean to standard deviation", "Variance squared"],
                    "correct": "Difference between 75th percentile (Q3) and 25th percentile (Q1)",
                    "diff": "Hard",
                    "exp": "IQR = Q3 - Q1, covering middle 50% of data values.",
                },
                {
                    "text": "What does a 95% Confidence Interval for a mean mean?",
                    "options": ["95% of data values fall inside interval", "If experiment is repeated 100 times, ~95 of computed intervals will contain true population mean", "There is a 95% probability sample is exact", "Null hypothesis is 95% true"],
                    "correct": "If experiment is repeated 100 times, ~95 of computed intervals will contain true population mean",
                    "diff": "Hard",
                    "exp": "CI reflects long-run frequentist coverage of intervals containing true population parameter.",
                },
                {
                    "text": "What is the primary assumption of ANOVA testing when comparing 3+ group means?",
                    "options": ["Groups have equal variances (homoscedasticity) and normal distributions", "Groups have zero correlation", "Sample size is exactly equal to 30", "Data is non-numerical"],
                    "correct": "Groups have equal variances (homoscedasticity) and normal distributions",
                    "diff": "Hard",
                    "exp": "ANOVA assumes normality, independent samples, and variance homogeneity across groups.",
                },
            ],
        },
        {
            "skill_name": "EDA",
            "title": "Exploratory Data Analysis Diagnostic",
            "description": "Evaluation of outlier detection, missing value treatment, and feature distribution analysis.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which plot is ideal for visualizing the distribution and quartiles of a continuous numerical variable?",
                    "options": ["Scatter Plot", "Box Plot", "Line Chart", "Pie Chart"],
                    "correct": "Box Plot",
                    "diff": "Easy",
                    "exp": "Box plots show median, IQR, whiskers, and individual outliers.",
                },
                {
                    "text": "How is an outlier defined in standard Box Plot IQR method?",
                    "options": ["Value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR", "Value outside +/- 1 standard deviation", "Value equal to zero", "Value in top 10% of dataset"],
                    "correct": "Value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR",
                    "diff": "Easy",
                    "exp": "1.5 * IQR rule identifies mild/extreme data outliers.",
                },
                {
                    "text": "What is skewness in data distribution analysis?",
                    "options": ["Measure of symmetry of distribution around mean", "Measure of kurtosis height", "Number of duplicate rows", "Correlation between two features"],
                    "correct": "Measure of symmetry of distribution around mean",
                    "diff": "Easy",
                    "exp": "Skewness quantifies asymmetry of data distribution tail.",
                },
                {
                    "text": "What technique replaces missing values with mean/median or predicted values?",
                    "options": ["Data Imputation", "Data Normalization", "One-Hot Encoding", "Binning"],
                    "correct": "Data Imputation",
                    "diff": "Medium",
                    "exp": "Imputation replaces missing values with statistically computed substitutes.",
                },
                {
                    "text": "Which correlation heat map metric measures non-linear monotonic relationships between variables?",
                    "options": ["Pearson correlation", "Spearman rank correlation", "Covariance", "Standard error"],
                    "correct": "Spearman rank correlation",
                    "diff": "Medium",
                    "exp": "Spearman assesses monotonic relationships using rank orders.",
                },
                {
                    "text": "What problem occurs when independent features in a model are highly correlated with each other?",
                    "options": ["Multicollinearity", "Heteroscedasticity", "Overfitting", "Underfitting"],
                    "correct": "Multicollinearity",
                    "diff": "Medium",
                    "exp": "Multicollinearity distorts regression coefficient estimates due to feature redundancy.",
                },
                {
                    "text": "What does a histogram display on its vertical Y axis?",
                    "options": ["Frequency / Count of data points in each bin", "Mean value of variables", "Cumulative percentage", "Feature correlation"],
                    "correct": "Frequency / Count of data points in each bin",
                    "diff": "Medium",
                    "exp": "Histograms count observations falling within continuous interval bins.",
                },
                {
                    "text": "When data is right-skewed (positively skewed), what is true regarding mean and median?",
                    "options": ["Mean > Median", "Mean < Median", "Mean == Median", "Median is undefined"],
                    "correct": "Mean > Median",
                    "diff": "Hard",
                    "exp": "Positive right skew pulls the mean rightward higher than median.",
                },
                {
                    "text": "What does the pairplot / scatter matrix visualization evaluate during EDA?",
                    "options": ["Pairwise bivariate relationships between all numerical features", "Time-series trend lines", "Categorical bar frequencies", "Missing value percentage"],
                    "correct": "Pairwise bivariate relationships between all numerical features",
                    "diff": "Hard",
                    "exp": "Pairplots display matrix of scatter plots for pairwise feature analysis.",
                },
                {
                    "text": "Why should missingness mechanisms (MCAR, MAR, MNAR) be evaluated before dropping missing rows?",
                    "options": ["Dropping MNAR data introduces selection bias into model insights", "MCAR data cannot be imputed", "MAR data requires scaling", "It is required by Python syntax"],
                    "correct": "Dropping MNAR data introduces selection bias into model insights",
                    "diff": "Hard",
                    "exp": "Missing Not At Random (MNAR) data removal alters underlying dataset representation.",
                },
            ],
        },
        {
            "skill_name": "Data Visualization",
            "title": "Data Visualization & Dashboard Design Assessment",
            "description": "Evaluation of chart selection, visual hierarchy, color design, and dashboard communication.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "Which chart type is most appropriate for displaying change over continuous time intervals?",
                    "options": ["Line Chart", "Pie Chart", "Treemap", "Scatter Plot"],
                    "correct": "Line Chart",
                    "diff": "Easy",
                    "exp": "Line charts display temporal trends across continuous time series.",
                },
                {
                    "text": "Why are 3D pie charts generally discouraged in professional analytics dashboards?",
                    "options": ["Distorts perspective making slices difficult to accurately compare", "Uses too much GPU memory", "Supported only in Excel", "Cannot show 2 slices"],
                    "correct": "Distorts perspective making slices difficult to accurately compare",
                    "diff": "Easy",
                    "exp": "3D perspective skews visual area, deceiving human perception of proportions.",
                },
                {
                    "text": "What chart type is best for showing composition of hierarchical data using nested rectangles?",
                    "options": ["Treemap", "Bar Chart", "Box Plot", "Histogram"],
                    "correct": "Treemap",
                    "diff": "Easy",
                    "exp": "Treemaps display hierarchical proportions using nested rectangular areas.",
                },
                {
                    "text": "What visual design principle ensures key performance metrics immediately draw user attention?",
                    "options": ["Visual Hierarchy", "Chartjunk", "Rainbow Color Palette", "Gridline Density"],
                    "correct": "Visual Hierarchy",
                    "diff": "Medium",
                    "exp": "Visual hierarchy organizes elements by size, contrast, and position to guide focus.",
                },
                {
                    "text": "When comparing 15 categorical items, which orientation of bar chart is most readable?",
                    "options": ["Horizontal Bar Chart", "Vertical Column Chart", "Pie Chart", "Donut Chart"],
                    "correct": "Horizontal Bar Chart",
                    "diff": "Medium",
                    "exp": "Horizontal bar charts leave space for long category labels without text rotation.",
                },
                {
                    "text": "What color palette choice is recommended for colorblind accessibility in analytics?",
                    "options": ["Avoid red-green contrast; use blue-orange or high contrast palettes", "Use neon colors", "Use shades of red only", "Disable legends"],
                    "correct": "Avoid red-green contrast; use blue-orange or high contrast palettes",
                    "diff": "Medium",
                    "exp": "Deuteranopia/Protanopia colorblindness affects red-green distinction.",
                },
                {
                    "text": "What term coined by Edward Tufte describes non-data ink or decorative elements in charts?",
                    "options": ["Chartjunk", "Data Density", "Lie Factor", "Sparkline"],
                    "correct": "Chartjunk",
                    "diff": "Medium",
                    "exp": "Chartjunk refers to unnecessary decorative clutter that distracts from data.",
                },
                {
                    "text": "What does Edward Tufte's Data-Ink Ratio advocate?",
                    "options": ["Maximize proportion of ink devoted to displaying actual data information", "Use maximum color background shading", "Include 3D borders", "Hide chart titles"],
                    "correct": "Maximize proportion of ink devoted to displaying actual data information",
                    "diff": "Hard",
                    "exp": "Data-Ink Ratio = (Data-Ink) / (Total Ink used in graphic); higher ratio improves clarity.",
                },
                {
                    "text": "Which chart type effectively displays relationship between two numerical variables and a third categorical dimension?",
                    "options": ["Scatter plot with color-coded categorical markers", "Pie Chart", "Single KPI Card", "Bar Chart"],
                    "correct": "Scatter plot with color-coded categorical markers",
                    "diff": "Hard",
                    "exp": "Scatter plots map X and Y coordinates with color/shape hue for categorical grouping.",
                },
                {
                    "text": "What is the primary danger of truncating Y-axis baseline to start above zero in a Bar Chart?",
                    "options": ["Exaggerates relative differences between bar heights", "Causes data calculation errors", "Hides column labels", "Converts bars into lines"],
                    "correct": "Exaggerates relative differences between bar heights",
                    "diff": "Hard",
                    "exp": "Bar height encodes magnitude from zero; truncating Y-axis visually misleads comparison.",
                },
            ],
        },
        {
            "skill_name": "Power BI",
            "title": "Power BI DAX & Data Modeling Diagnostic",
            "description": "Evaluation of Power BI relationships, DAX measures, calculated columns, and filter context.",
            "difficulty": "Intermediate",
            "questions": [
                {
                    "text": "What is the primary difference between a Calculated Column and a DAX Measure in Power BI?",
                    "options": ["Calculated columns are evaluated row-by-row during data refresh and stored in memory; Measures are evaluated dynamically on query filter context", "Measures are stored on disk; columns are dynamic", "Calculated columns work only on text", "They are identical"],
                    "correct": "Calculated columns are evaluated row-by-row during data refresh and stored in memory; Measures are evaluated dynamically on query filter context",
                    "diff": "Easy",
                    "exp": "Calculated columns occupy RAM memory per row, whereas Measures compute dynamically during visual rendering.",
                },
                {
                    "text": "Which DAX function alters the current filter context during measure calculation?",
                    "options": ["CALCULATE()", "SUM()", "FILTER()", "ALL()"],
                    "correct": "CALCULATE()",
                    "diff": "Easy",
                    "exp": "CALCULATE() evaluates an expression in a modified filter context.",
                },
                {
                    "text": "What type of data schema is recommended as best practice for Power BI data modeling?",
                    "options": ["Star Schema (Fact table surrounded by Dimension tables)", "Single flat 500-column table", "Normalized 3NF relational schema", "Network graph schema"],
                    "correct": "Star Schema (Fact table surrounded by Dimension tables)",
                    "diff": "Easy",
                    "exp": "Star schema optimizes VertiPaq engine compression and DAX query performance.",
                },
                {
                    "text": "What does the DAX function ALL(Table[Column]) return?",
                    "options": ["Returns all rows/values ignoring any filters applied to that column", "Returns empty table", "Filters values by current slicer", "Sorts table ascending"],
                    "correct": "Returns all rows/values ignoring any filters applied to that column",
                    "diff": "Medium",
                    "exp": "ALL removes existing filter context from specified table or columns.",
                },
                {
                    "text": "What is the function of Power Query (M language) in Power BI?",
                    "options": ["Data extraction, transformation, cleaning, and ETL loading", "Creating DAX measures", "Designing report layouts", "Managing user row-level security"],
                    "correct": "Data extraction, transformation, cleaning, and ETL loading",
                    "diff": "Medium",
                    "exp": "Power Query handles ETL data transformation before loading into tabular model.",
                },
                {
                    "text": "Which DAX function counts non-blank rows in a column?",
                    "options": ["COUNT()", "COUNTA()", "COUNTROWS()", "COUNTBLANK()"],
                    "correct": "COUNT()",
                    "diff": "Medium",
                    "exp": "COUNT counts non-blank numbers/dates in a column; COUNTROWS counts table rows.",
                },
                {
                    "text": "What is Row-Level Security (RLS) used for in Power BI?",
                    "options": ["Restricting data row access for given users based on DAX role filters", "Encrypting database disk", "Formatting report colors", "Speeding up query refresh"],
                    "correct": "Restricting data row access for given users based on DAX role filters",
                    "diff": "Medium",
                    "exp": "RLS restricts user access to specific rows in report data models.",
                },
                {
                    "text": "What does DAX Context Transition describe in Power BI?",
                    "options": ["Transformation of row context into equivalent filter context using CALCULATE", "Moving report from Desktop to Service", "Converting DirectQuery to Import mode", "Changing column data types"],
                    "correct": "Transformation of row context into equivalent filter context using CALCULATE",
                    "diff": "Hard",
                    "exp": "CALCULATE transforms existing row context into active filter context.",
                },
                {
                    "text": "What is difference between USERELATIONSHIP() and standard relationship in DAX?",
                    "options": ["USERELATIONSHIP activates an inactive secondary relationship for duration of DAX calculation", "USERELATIONSHIP creates a new physical column", "USERELATIONSHIP works only on text keys", "USERELATIONSHIP disables all measures"],
                    "correct": "USERELATIONSHIP activates an inactive secondary relationship for duration of DAX calculation",
                    "diff": "Hard",
                    "exp": "USERELATIONSHIP forces CALCULATE to use a designated inactive model relationship.",
                },
                {
                    "text": "What is VertiPaq engine in Power BI?",
                    "options": ["In-memory columnar database storage and compression engine", "JavaScript rendering library", "Gateway connector", "File exporter"],
                    "correct": "In-memory columnar database storage and compression engine",
                    "diff": "Hard",
                    "exp": "VertiPaq is the columnar in-memory database engine powering Power BI tabular models.",
                },
            ],
        },
    ]

    for spec in assessments_spec:
        skill = skill_objs[spec["skill_name"]]
        assm = db.query(Assessment).filter_by(skill_id=skill.id).first()
        if not assm:
            assm = Assessment(
                title=spec["title"],
                description=spec["description"],
                skill_id=skill.id,
                difficulty=spec["difficulty"],
            )
            db.add(assm)
            db.commit()
            db.refresh(assm)

        # Seed 10 deterministic questions
        for q_data in spec["questions"]:
            q_exists = db.query(AssessmentQuestion).filter_by(
                assessment_id=assm.id, question_text=q_data["text"]
            ).first()

            if not q_exists:
                q = AssessmentQuestion(
                    assessment_id=assm.id,
                    question_text=q_data["text"],
                    options=json.dumps(q_data["options"]),
                    correct_answer=q_data["correct"],
                    difficulty=q_data["diff"],
                    explanation=q_data["exp"],
                )
                db.add(q)
        db.commit()

    # 7. Seed Initial Evidence Audit Log
    evidences_data = [
        ("Python", "Diagnostic Assessment #2", "ASSESSMENT", 85.0, "Verified Python data structure proficiency."),
        ("Statistics", "Practice Lab Module #4", "PRACTICE", 81.0, "Executed hypothesis testing script."),
        ("SQL", "Diagnostic Assessment #1", "ASSESSMENT", 76.0, "Verified relational filtering and aggregation."),
        ("SQL JOINs", "Relational Query Quiz", "ASSESSMENT", 42.0, "Attempted multi-table query assessment; join syntax errors detected."),
        ("EDA", "EDA Assessment #5", "ASSESSMENT", 65.0, "Assessed exploratory data analysis and outlier detection."),
        ("Data Visualization", "Chart Design Lab #6", "PRACTICE", 70.0, "Completed visual communication and chart selection lab."),
        ("Power BI", "DAX Dashboard Quiz #7", "ASSESSMENT", 38.0, "Evaluated DAX measures and filter context modeling."),
        ("Machine Learning", "ML Foundations Intro", "COURSE", 35.0, "Completed introductory scikit-learn tutorial."),
    ]

    for s_name, src, ev_type, score, desc in evidences_data:
        skill = skill_objs[s_name]
        existing_ev = db.query(SkillEvidence).filter_by(user_id=alex.id, skill_id=skill.id, source=src).first()
        if not existing_ev:
            ev = SkillEvidence(
                user_id=alex.id,
                skill_id=skill.id,
                source=src,
                evidence_type=ev_type,
                score=score,
                description=desc,
            )
            db.add(ev)
    db.commit()

    # 8. Seed Initial Roadmap
    roadmap = db.query(Roadmap).filter_by(user_id=alex.id, status="active").first()
    if not roadmap:
        roadmap = Roadmap(
            user_id=alex.id,
            target_role_id=da_role.id,
            version=1,
            status="active",
        )
        db.add(roadmap)
        db.commit()
        db.refresh(roadmap)

        steps_data = [
            (1, skill_objs["Python"].id, "Python Fundamentals & Data Structs", "lesson", "Verified", "verified", "Demonstrated 85% mastery across 14 assessment modules.", 30),
            (2, skill_objs["SQL"].id, "SQL Fundamentals & Basic Filtering", "lesson", "Verified", "verified", "Verified with 76% demonstrated baseline accuracy.", 45),
            (3, skill_objs["SQL JOINs"].id, "SQL JOIN Rescue Challenge", "challenge", "Critical", "current", "Skill Debt detected: 38% deficit from Data Analyst target requirement.", 35),
            (4, skill_objs["SQL JOINs"].id, "Real-World SQL Query Task", "task", "High", "next", "Practical application on e-commerce transaction dataset.", 45),
            (5, skill_objs["SQL JOINs"].id, "Post-Task SQL Reassessment", "reassessment", "High", "upcoming", "Update Skill DNA baseline after hands-on task evaluation.", 20),
            (6, skill_objs["EDA"].id, "Exploratory Data Analysis Lab", "challenge", "Medium", "upcoming", "Target role requires 85% proficiency; current evidence is 65%.", 60),
            (7, skill_objs["Power BI"].id, "Power BI Dashboard Challenge", "challenge", "High", "upcoming", "Resolve 32% skill debt in Business Intelligence reporting.", 90),
        ]

        for idx, s_id, title, stype, prio, stat, reason, mins in steps_data:
            step = RoadmapStep(
                roadmap_id=roadmap.id,
                skill_id=s_id,
                title=title,
                step_type=stype,
                priority=prio,
                status=stat,
                reason=reason,
                order_index=idx,
                estimated_minutes=mins,
            )
            db.add(step)
        db.commit()

    # 9. Seed Projects
    proj = db.query(Project).filter_by(title="Retail Sales Retention & Cohort Analysis").first()
    if not proj:
        proj = Project(
            title="Retail Sales Retention & Cohort Analysis",
            description="Real-world data science project analyzing customer lifetime value and churn drivers.",
            skill_id=skill_objs["Python"].id,
            difficulty="Intermediate",
            estimated_minutes=240,
            project_type="Portfolio",
        )
        db.add(proj)
        db.commit()

    # 10. Seed Industry Labs
    lab1 = db.query(IndustryLab).filter_by(slug="retail-returns-analytics").first()
    if not lab1:
        lab1 = IndustryLab(
            slug="retail-returns-analytics",
            title="E-Commerce Customer Retention & Returns Analytics",
            description="Hands-on relational SQL sandbox analyzing multi-table retail transactional data, missing return reasons, and financial KPIs by customer segment.",
            target_role_id=da_role.id,
            primary_skill_id=skill_objs["SQL JOINs"].id,
            difficulty="Intermediate",
            estimated_minutes=45,
            business_context=(
                "The Executive VP of E-Commerce has observed an escalation in customer refund requests and wants "
                "a segment-level breakdown of Gross Revenue, Total Refunds, Net Realized Revenue, and Return Rate (%). "
                "Because orders can have 0 returns, an INNER JOIN excludes non-returned orders, resulting in heavily biased metrics. "
                "Write clean queries using LEFT JOINs, NULL handling, and status filtering to produce verifiable executive KPIs."
            ),
            datasets_info=json.dumps({
                "tables": ["lab_retail_customers", "lab_retail_orders", "lab_retail_order_items", "lab_retail_products", "lab_retail_returns"]
            }),
        )
        db.add(lab1)
        db.commit()
        db.refresh(lab1)

        t1 = IndustryLabTask(
            lab_id=lab1.id,
            task_order=1,
            task_type="DATA_PROFILING",
            title="Inspect Schema & Payment Statuses",
            prompt="Review customer accounts and identify order payment status values.",
            requirements="Filter out CANCELLED and PENDING orders from revenue metrics.",
            expected_output_desc="Recognize status categories: COMPLETED, CANCELLED, PENDING.",
            weight=1.0,
        )
        t2 = IndustryLabTask(
            lab_id=lab1.id,
            task_order=2,
            task_type="SQL_QUERY",
            title="Customer Segment Net Revenue & Return Rate",
            prompt="Calculate total orders, gross revenue, total refunds, net revenue, and return rate (%) per customer segment.",
            requirements="JOIN customers and orders, LEFT JOIN returns, filter payment_status = 'COMPLETED', handle NULLs with COALESCE.",
            expected_output_desc="Segment-level financial summary table ordered by Net Revenue descending.",
            weight=2.0,
        )
        t3 = IndustryLabTask(
            lab_id=lab1.id,
            task_order=3,
            task_type="BUSINESS_ANALYSIS",
            title="Executive Synthesis & Risk Deduction",
            prompt="Provide business rationale explaining which segment represents highest financial impact from returns.",
            requirements="Provide analytical summary of segment performance and return rate implications.",
            expected_output_desc="Written deduction identifying segment return trends.",
            weight=1.0,
        )
        db.add_all([t1, t2, t3])
        db.commit()

    lab2 = db.query(IndustryLab).filter_by(slug="saas-mrr-churn").first()
    if not lab2:
        lab2 = IndustryLab(
            slug="saas-mrr-churn",
            title="SaaS Subscription Churn & LTV Analysis",
            description="Evaluate customer subscription lifecycles, active users, and monthly recurring revenue degradation.",
            target_role_id=da_role.id,
            primary_skill_id=skill_objs["SQL"].id,
            difficulty="Beginner",
            estimated_minutes=30,
            business_context="Investigate monthly customer retention and churn rates across SaaS subscription tiers.",
            datasets_info=json.dumps({"tables": ["lab_retail_customers", "lab_retail_orders"]}),
        )
        db.add(lab2)
        db.commit()


def reset_alex_mercer(db: Session) -> None:
    """
    Resets demo learner Alex Mercer to the clean baseline state.
    """
    alex = db.query(User).filter(User.email == "alex.mercer@example.com").first()
    if not alex:
        return

    # Delete non-seed assessment attempts, project attempts, and lab attempts
    db.query(AssessmentAttempt).filter_by(user_id=alex.id).delete()
    db.query(ProjectAttempt).filter_by(user_id=alex.id).delete()
    db.query(IndustryLabAttempt).filter_by(user_id=alex.id).delete()

    seed_sources = [
        "Diagnostic Assessment #2", "Practice Lab Module #4",
        "Diagnostic Assessment #1", "Relational Query Quiz",
        "EDA Assessment #5", "Chart Design Lab #6",
        "DAX Dashboard Quiz #7", "ML Foundations Intro"
    ]
    db.query(SkillEvidence).filter(
        SkillEvidence.user_id == alex.id,
        ~SkillEvidence.source.in_(seed_sources)
    ).delete()

    alex_dna_scores = [
        ("Python", 85.0, 92.0, 88.0, 14),
        ("SQL", 76.0, 78.0, 74.0, 9),
        ("SQL JOINs", 42.0, 45.0, 40.0, 3),
        ("Statistics", 81.0, 85.0, 82.0, 11),
        ("EDA", 65.0, 68.0, 62.0, 6),
        ("Data Visualization", 70.0, 72.0, 68.0, 5),
        ("Power BI", 38.0, 40.0, 35.0, 2),
        ("Machine Learning", 35.0, 35.0, 30.0, 1),
    ]

    for s_name, level, conf, acc, ev_count in alex_dna_scores:
        skill = db.query(Skill).filter_by(name=s_name).first()
        if skill:
            us = db.query(UserSkill).filter_by(user_id=alex.id, skill_id=skill.id).first()
            if us:
                us.skill_level = level
                us.confidence = conf
                us.accuracy = acc
                us.evidence_score = ev_count * 5.0

    from app.services.roadmap_service import roadmap_service
    roadmap_service.rebuild_user_roadmap(db, alex.id)
    db.commit()


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
        print("Database tables initialized and 70 diagnostic assessment questions successfully seeded!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
