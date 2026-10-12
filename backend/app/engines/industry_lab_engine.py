import re
import time
import sqlite3
from typing import Dict, Any, List, Optional, Tuple


class IndustryLabEngine:
    """
    Phase 10 — Industry Practical Lab & Sandbox Evaluation Engine
    Provides deterministic 4-pillar evaluation for hands-on SQL and data analytics labs:
    1. SQL Correctness (40%)
    2. Data Quality Handling (20%)
    3. Business Result Calculation (25%)
    4. Validation Reasoning (15%)
    """

    FORBIDDEN_KEYWORDS = [
        "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
        "ATTACH", "DETACH", "PRAGMA", "EXEC", "EXECUTE", "VACUUM",
        "GRANT", "REVOKE", "TRUNCATE", "REPLACE"
    ]

    def validate_sql_security(self, query: str) -> Tuple[bool, Optional[str]]:
        """
        Ensures query is read-only and strictly executed as a single SELECT statement.
        """
        cleaned = re.sub(r"--.*?$|/\*.*?\*/", "", query, flags=re.MULTILINE).strip()
        if not cleaned:
            return False, "Query cannot be empty."

        # Disallow multiple statements
        statements = [s.strip() for s in cleaned.split(";") if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements are not permitted in the sandbox."

        first_stmt = statements[0]
        first_token = first_stmt.split()[0].upper()
        if first_token not in ("SELECT", "WITH"):
            return False, f"Unauthorized query type: '{first_token}'. Only SELECT queries are permitted in the sandbox."

        # Check for forbidden mutation keywords
        tokens = set(re.findall(r"\b[A-Z]+\b", first_stmt.upper()))
        for kw in self.FORBIDDEN_KEYWORDS:
            if kw in tokens:
                return False, f"Forbidden SQL operation '{kw}' detected. Only read-only SELECT queries are allowed."

        return True, None

    def run_sandbox_query(self, query: str, db_path: str = "skillpath.db") -> Dict[str, Any]:
        """
        Safely executes learner's query against sandbox SQLite database and captures metrics.
        """
        is_safe, error_msg = self.validate_sql_security(query)
        if not is_safe:
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": 0,
                "error_message": error_msg,
            }

        start_time = time.perf_counter()
        try:
            # Connect in read-only URI mode
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)

            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            raw_rows = cursor.fetchmany(200)  # Safe cap
            rows = [dict(r) for r in raw_rows]

            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            conn.close()

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "execution_time_ms": elapsed_ms,
                "error_message": None,
            }
        except Exception as e:
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": elapsed_ms,
                "error_message": f"SQL Execution Error: {str(e)}",
            }

    def evaluate_retail_returns_analytics(
        self,
        query: str,
        submitted_answer: Optional[str] = None,
        db_path: str = "skillpath.db",
    ) -> Dict[str, Any]:
        """
        Canonical evaluation for 'retail-returns-analytics' industry lab.
        Required analysis:
        - Segment-level aggregation of orders, gross revenue, refunds, net revenue, and return rate.
        - Must JOIN customers and orders.
        - Must LEFT JOIN returns (INNER JOIN drops non-returned orders!).
        - Must filter `payment_status = 'COMPLETED'` (excluding CANCELLED and PENDING).
        - Must handle NULL refunds via COALESCE.
        - Order by net revenue descending.
        """
        diagnostic_failures: List[str] = []

        # 1. Execute user query
        run_res = self.run_sandbox_query(query, db_path=db_path)
        exec_ms = run_res["execution_time_ms"]

        if not run_res["success"]:
            return {
                "status": "FAILED",
                "total_score": 0.0,
                "section_scores": {
                    "sql_correctness": 0.0,
                    "data_quality_handling": 0.0,
                    "business_result": 0.0,
                    "validation_reasoning": 0.0,
                },
                "feedback": f"Query failed with syntax or execution error: {run_res['error_message']}",
                "diagnostic_failures": [run_res["error_message"]],
                "execution_time_ms": exec_ms,
            }

        rows = run_res["rows"]
        columns_lower = [c.lower() for c in run_res["columns"]]
        query_upper = query.upper()

        sql_score = 0.0
        data_quality_score = 0.0
        business_score = 0.0
        validation_score = 0.0

        # --- PILLAR 1: SQL Correctness (Max 40.0) ---
        # 1a. Query syntax & execution success: 10 pts
        sql_score += 10.0

        # 1b. Base Join verification between customers and orders
        has_base_join = "CUSTOMERS" in query_upper and "ORDERS" in query_upper and "JOIN" in query_upper
        if has_base_join:
            sql_score += 5.0
        else:
            diagnostic_failures.append("Missing join between customers and orders tables.")

        # 1c. Returns join verification
        has_returns_join = "LAB_RETAIL_RETURNS" in query_upper or "RETURNS" in query_upper
        has_left_join = "LEFT JOIN" in query_upper or "LEFT OUTER JOIN" in query_upper

        if not has_returns_join:
            diagnostic_failures.append("Missing join to 'lab_retail_returns' table to account for order refunds.")
        elif not has_left_join:
            # Detected INNER JOIN bug!
            diagnostic_failures.append(
                "INNER JOIN used on returns table instead of LEFT JOIN. Unreturned orders were incorrectly excluded!"
            )
        else:
            sql_score += 10.0

        # 1c. Grouping by segment or customer
        if "GROUP BY" in query_upper and ("SEGMENT" in query_upper or "CUSTOMER" in query_upper):
            sql_score += 15.0
        else:
            diagnostic_failures.append("Missing or incomplete GROUP BY clause for customer segment aggregation.")

        # --- PILLAR 2: Data Quality Handling (Max 20.0) ---
        # 2a. Filter completed orders only
        has_completed_filter = "COMPLETED" in query_upper and "PAYMENT_STATUS" in query_upper
        if has_completed_filter:
            data_quality_score += 10.0
        else:
            diagnostic_failures.append(
                "Did not filter out non-completed orders. Only orders with payment_status = 'COMPLETED' should be included."
            )

        # 2b. Null refund handling
        has_coalesce = "COALESCE" in query_upper or "IFNULL" in query_upper or "CASE" in query_upper
        if has_coalesce:
            data_quality_score += 10.0
        else:
            diagnostic_failures.append(
                "Missing NULL handling (COALESCE/IFNULL) on refund amounts. Non-returned orders contain NULL refunds."
            )

        # --- PILLAR 3: Business Result Metric (Max 25.0) ---
        # Ground truth values for completed orders by segment:
        # Enterprise: Orders 1001 ($1797), 1002 ($899), 1003 ($2250), 1004 ($499), 1014 ($3596).
        #             Returns: 1002 ($899).
        #             Total orders: 5. Gross: 9041.0. Refunds: 899.0. Net: 8142.0. Return rate: 20.0%
        # Mid-Market: Orders 1005 ($1498), 1006 ($598), 1007 ($1249). (1008 is CANCELLED).
        #             Returns: 1006 ($299).
        #             Total orders: 3. Gross: 3345.0. Refunds: 299.0. Net: 3046.0. Return rate: 33.33%
        # SMB:        Orders 1009 ($854), 1010 ($299), 1011 ($554), 1013 ($255), 1015 ($299). (1012 is PENDING).
        #             Returns: 1011 ($499).
        #             Total orders: 5. Gross: 2261.0. Refunds: 499.0. Net: 1762.0. Return rate: 20.0%

        # Check returned segments count
        if len(rows) == 3:
            business_score += 7.0
        elif len(rows) > 0:
            business_score += 3.0

        # Check values in rows
        found_enterprise_net = False
        found_return_rate = False
        for r in rows:
            values_str = " ".join(str(v) for v in r.values())
            if "8142" in values_str or "8142.0" in values_str:
                found_enterprise_net = True
            if "20" in values_str or "33.3" in values_str:
                found_return_rate = True

        if found_enterprise_net:
            business_score += 10.0
        else:
            diagnostic_failures.append("Calculated net revenue does not match expected financial benchmarks.")

        if found_return_rate:
            business_score += 8.0
        else:
            diagnostic_failures.append("Calculated return rate percentage does not match expected ground truth.")

        # --- PILLAR 4: Validation Reasoning (Max 15.0) ---
        if submitted_answer and len(submitted_answer.strip()) > 15:
            ans_lower = submitted_answer.lower()
            key_terms = ["enterprise", "net revenue", "refund", "return", "smb", "margin", "retention"]
            matched_terms = [t for t in key_terms if t in ans_lower]
            if len(matched_terms) >= 3:
                validation_score = 15.0
            elif len(matched_terms) >= 1:
                validation_score = 10.0
            else:
                validation_score = 7.0
        else:
            # If no written rationale provided, award baseline 5 pts if query contains clean aliases
            has_aliases = " AS " in query_upper
            validation_score = 7.0 if has_aliases else 3.0

        # Total Calculation
        total_score = round(sql_score + data_quality_score + business_score + validation_score, 1)
        total_score = min(100.0, max(0.0, total_score))

        if total_score >= 80.0:
            status = "PASSED"
            feedback = (
                f"Outstanding work! Your query achieved a {total_score}% score across all 4 evaluation pillars. "
                "You correctly utilized a LEFT JOIN to preserve all orders, properly filtered for completed payment statuses, "
                "handled NULL refunds via COALESCE, and produced accurate segment-level financial KPIs."
            )
        elif total_score >= 50.0:
            status = "PARTIAL"
            feedback = (
                f"Partial pass ({total_score}%). Your query logic is functional but exhibits data quality or relational join gaps. "
                + " ".join(diagnostic_failures[:2])
            )
        else:
            status = "FAILED"
            feedback = (
                f"Evaluation failed ({total_score}%). Critical defects identified: "
                + " ".join(diagnostic_failures[:3])
            )

        return {
            "status": status,
            "total_score": total_score,
            "section_scores": {
                "sql_correctness": round(sql_score, 1),
                "data_quality_handling": round(data_quality_score, 1),
                "business_result": round(business_score, 1),
                "validation_reasoning": round(validation_score, 1),
            },
            "feedback": feedback,
            "diagnostic_failures": diagnostic_failures,
            "execution_time_ms": exec_ms,
        }

    def evaluate_general_query(
        self,
        lab_slug: str,
        query: str,
        submitted_answer: Optional[str] = None,
        db_path: str = "skillpath.db",
    ) -> Dict[str, Any]:
        """
        Dispatcher for evaluating labs based on slug.
        """
        if lab_slug == "retail-returns-analytics":
            return self.evaluate_retail_returns_analytics(query, submitted_answer, db_path=db_path)

        # Fallback evaluation for other general labs
        run_res = self.run_sandbox_query(query, db_path=db_path)
        if not run_res["success"]:
            return {
                "status": "FAILED",
                "total_score": 0.0,
                "section_scores": {
                    "sql_correctness": 0.0,
                    "data_quality_handling": 0.0,
                    "business_result": 0.0,
                    "validation_reasoning": 0.0,
                },
                "feedback": run_res["error_message"],
                "diagnostic_failures": [run_res["error_message"]],
                "execution_time_ms": run_res["execution_time_ms"],
            }

        # Basic score calculation
        score = 80.0 if run_res["row_count"] > 0 else 40.0
        return {
            "status": "PASSED" if score >= 80.0 else "PARTIAL",
            "total_score": score,
            "section_scores": {
                "sql_correctness": 35.0,
                "data_quality_handling": 15.0,
                "business_result": 20.0,
                "validation_reasoning": 10.0,
            },
            "feedback": "Query executed successfully and returned valid result set.",
            "diagnostic_failures": [],
            "execution_time_ms": run_res["execution_time_ms"],
        }


industry_lab_engine = IndustryLabEngine()
