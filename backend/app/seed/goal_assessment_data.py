"""
Seed data for Phase 1 Goal -> Skill Maps and Diagnostic Assessment Questions.
Supports:
1. Java Backend Developer
2. Python Developer
3. Data Analyst
4. Full Stack Developer
5. AI/ML Engineer
"""

from typing import List, Dict, Any, Tuple

# Predefined Goals Specifications
PREDEFINED_GOALS = [
    {
        "name": "Java Backend Developer",
        "description": "High-performance enterprise services, Spring Boot microservices, relational persistence, and secure REST APIs.",
        "skills": [
            ("Java Basics", "Java Programming", "Core syntax, data types, control flow, loops, and basic memory model.", 90, 80, "Critical"),
            ("OOP", "Java Programming", "Inheritance, polymorphism, encapsulation, abstraction, and SOLID design principles.", 95, 85, "Critical"),
            ("Java Collections", "Java Programming", "List, Set, Map, Queue, Big-O complexity, iterators, and stream processing.", 95, 80, "Critical"),
            ("Exception Handling", "Java Programming", "Checked vs unchecked exceptions, try-catch-finally, and custom exception hierarchies.", 85, 75, "High"),
            ("Multithreading", "Java Programming", "Threads, concurrency, synchronization, ExecutorService, and thread safety.", 80, 70, "High"),
            ("SQL Basics", "Database & Storage", "DML/DDL, queries, aggregate functions, filtering, and indexing.", 90, 80, "Critical"),
            ("SQL JOINs", "Database & Storage", "Inner, left, right, outer, self, and cross joins across multi-table relational schemas.", 90, 85, "Critical"),
            ("Database Normalization", "Database & Storage", "1NF, 2NF, 3NF, BCNF, data integrity, and eliminating redundant anomalies.", 85, 75, "High"),
            ("Transactions", "Database & Storage", "ACID properties, isolation levels, pessimistic vs optimistic locking, and rollback.", 85, 75, "High"),
            ("HTTP & REST APIs", "Backend Architecture", "HTTP methods, status codes, RESTful resource modeling, request headers, and idempotency.", 95, 85, "Critical"),
            ("Spring Boot", "Backend Architecture", "Dependency injection, Spring MVC, Spring Data JPA, auto-configuration, and actuators.", 95, 80, "Critical"),
            ("Authentication & Security", "Backend Architecture", "JWT, OAuth2, session management, password hashing, and role-based access control.", 85, 75, "High"),
            ("Git", "Development & DevOps", "Version control, branching strategies, merges, rebases, and pull request workflows.", 85, 80, "High"),
            ("Unit Testing", "Development & DevOps", "JUnit 5, Mockito, test coverage, mocking dependencies, and automated test assertions.", 85, 75, "High"),
            ("Deployment & Docker", "Development & DevOps", "Containerization, Dockerfiles, environment variables, multi-stage builds, and cloud deployment.", 80, 70, "Medium"),
        ],
    },
    {
        "name": "Python Developer",
        "description": "Scalable web applications, asynchronous APIs, data modeling, automated testing, and backend microservices.",
        "skills": [
            ("Python Basics", "Python Core", "Syntax, dynamic typing, control flow, functions, lambdas, and scope resolution.", 95, 85, "Critical"),
            ("OOP", "Python Core", "Classes, dunder methods, inheritance, composition, and object-oriented architecture in Python.", 90, 80, "Critical"),
            ("Data Structures", "Python Core", "Lists, dictionaries, sets, tuples, generators, list comprehensions, and memory profiling.", 90, 80, "Critical"),
            ("Exception Handling", "Python Core", "Try-except-finally blocks, custom exception classes, and logging exceptions cleanly.", 85, 75, "High"),
            ("Concurrency", "Python Core", "Asyncio, coroutines, event loop, GIL trade-offs, and multi-processing pools.", 80, 70, "Medium"),
            ("SQL Basics", "Database & Storage", "Relational querying, schema modeling, constraints, and SQL transactions.", 85, 80, "High"),
            ("SQL JOINs", "Database & Storage", "Multi-table relational joins, null handling, and subquery query optimization.", 85, 80, "High"),
            ("Database Design", "Database & Storage", "Schema architecture, foreign keys, indexing strategies, and ORMs (SQLAlchemy).", 80, 75, "High"),
            ("FastAPI", "Backend Frameworks", "Pydantic validation, asynchronous endpoints, dependency injection, and OpenAPI generation.", 90, 85, "Critical"),
            ("HTTP & REST APIs", "Backend Architecture", "REST conventions, status codes, serialization, query params, and middleware.", 90, 85, "Critical"),
            ("Authentication & Security", "Backend Architecture", "OAuth2 with password bearer, JWT tokens, bcrypt password hashing, and CORS protection.", 80, 75, "High"),
            ("Git", "Development & DevOps", "Git version control, feature branches, merge conflicts, and commit hygiene.", 85, 80, "High"),
            ("Testing & PyTest", "Development & DevOps", "PyTest fixtures, mocking, parameterized tests, test coverage, and test automation.", 85, 80, "High"),
            ("Deployment & Docker", "Development & DevOps", "Docker containerization, Uvicorn production server, and cloud deployment basics.", 80, 70, "Medium"),
        ],
    },
    {
        "name": "Data Analyst",
        "description": "Analytic synthesis, SQL data wrangling, EDA, business intelligence, and executive reporting dashboards.",
        "skills": [
            ("SQL", "Database Querying", "Relational query filtering, aggregations, GROUP BY, and CTEs.", 90, 90, "Critical"),
            ("SQL JOINs", "Database Querying", "Inner, left, right, outer, self, and cross joins across multi-table schemas.", 95, 95, "Critical"),
            ("Python", "Programming & Data Manipulation", "Python data structures, Pandas pipelines, NumPy arrays, and vectorized operations.", 80, 80, "High"),
            ("Statistics", "Quantitative Analysis", "Descriptive & inferential statistics, probability, hypothesis testing, and p-values.", 75, 75, "Medium"),
            ("EDA", "Data Science Workflow", "Exploratory Data Analysis, missing value imputation, skewness, and outlier detection.", 85, 85, "High"),
            ("Data Visualization", "Business Intelligence & Reporting", "Chart design, visual perception principles, Matplotlib, Seaborn, and storytelling.", 90, 90, "Critical"),
            ("Power BI", "Business Intelligence & Reporting", "DAX calculations, relational data modeling, star schemas, and executive dashboards.", 85, 85, "Critical"),
            ("Machine Learning", "Predictive Modeling", "Basic classification, linear regression, and interpreting predictive indicators.", 30, 40, "Low"),
        ],
    },
    {
        "name": "Full Stack Developer",
        "description": "End-to-end web engineering, responsive client interfaces, REST/GraphQL services, and full stack deployment.",
        "skills": [
            ("HTML & CSS", "Frontend Engineering", "Semantic HTML5, CSS Flexbox/Grid, responsive design, and CSS animations.", 90, 85, "Critical"),
            ("JavaScript & TypeScript", "Frontend Engineering", "ES6+ syntax, asynchronous JS, TypeScript static typing, generics, and DOM.", 95, 85, "Critical"),
            ("React & Next.js", "Frontend Engineering", "Component state, hooks, Server Components, client routing, and rendering lifecycle.", 95, 85, "Critical"),
            ("Node.js & Express", "Backend Engineering", "Event loop, non-blocking I/O, Express routing, middleware, and backend API design.", 90, 80, "Critical"),
            ("HTTP & REST APIs", "Backend Architecture", "REST conventions, JSON payloads, headers, CORS, status codes, and API security.", 90, 85, "Critical"),
            ("SQL Basics", "Database & Storage", "Relational database schema, CRUD operations, indexing, and SQL queries.", 85, 80, "High"),
            ("SQL JOINs", "Database & Storage", "Relational joins, primary/foreign key connections, and query filtering.", 85, 80, "High"),
            ("Authentication & Security", "Backend Architecture", "JWT auth, sessions, cookie security, password hashing, and XSS/CSRF defense.", 85, 80, "High"),
            ("Git", "Development & DevOps", "Git version control, feature branches, pull requests, and collaborative code reviews.", 85, 80, "High"),
            ("Unit Testing", "Development & DevOps", "Jest, React Testing Library, API integration testing, and test assertions.", 80, 75, "Medium"),
            ("Deployment & Docker", "Development & DevOps", "Docker containerization, Vercel/cloud hosting, environment variables, and CI/CD.", 80, 75, "Medium"),
        ],
    },
    {
        "name": "AI/ML Engineer",
        "description": "Mathematical foundations, supervised/unsupervised machine learning, deep neural networks, and scalable MLOps.",
        "skills": [
            ("Python", "Programming & Data Manipulation", "Python pipelines, NumPy tensor operations, and optimized vector calculations.", 95, 90, "Critical"),
            ("Statistics", "Quantitative Analysis", "Probability distributions, Bayes theorem, hypothesis testing, and statistical estimation.", 90, 85, "Critical"),
            ("EDA", "Data Science Workflow", "Feature profiling, missing data strategies, feature scaling, and correlation matrices.", 85, 75, "High"),
            ("Machine Learning", "Predictive Modeling", "Supervised regression/classification, ensemble methods (XGBoost), and cross-validation.", 95, 90, "Critical"),
            ("Deep Learning", "Advanced Machine Learning", "Neural networks, PyTorch, backpropagation, CNNs, transformers, and loss functions.", 90, 85, "Critical"),
            ("MLOps", "Machine Learning Engineering", "Model tracking, MLflow, model registry, monitoring data drift, and automated pipelines.", 95, 85, "Critical"),
            ("SQL Basics", "Database Querying", "Relational feature queries, aggregating training datasets, and SQL wrangling.", 80, 75, "High"),
            ("Deployment & Docker", "Machine Learning Engineering", "Containerizing model inference, FastAPI model serving, and latency optimization.", 85, 80, "High"),
        ],
    },
]

# Targeted Diagnostic Questions for Goal Assessments
# 2-3 High quality questions per skill with options, correct answer, diff, explanation
SKILL_QUESTIONS_SPEC = {
    "Java Basics": [
        {
            "text": "What is the key difference between primitive types (e.g., int) and wrapper classes (e.g., Integer) in Java?",
            "options": [
                "Primitives store direct values on the stack; wrappers are heap objects that can be null and used in generics",
                "Primitives can be used as type arguments in Generics, whereas wrappers cannot",
                "Primitives always take more memory than wrapper classes",
                "Wrappers are mutable, whereas primitives are always immutable"
            ],
            "correct": "Primitives store direct values on the stack; wrappers are heap objects that can be null and used in generics",
            "diff": "Easy",
            "exp": "Primitive types store raw binary values directly on the stack, while wrapper classes instantiate Objects on the heap and allow null representation.",
        },
        {
            "text": "What will `System.out.println(10 + 20 + \"Hello\");` and `System.out.println(\"Hello\" + 10 + 20);` output in Java?",
            "options": [
                "30Hello and Hello1020",
                "30Hello and Hello30",
                "1020Hello and Hello1020",
                "Compilation error due to mixed types"
            ],
            "correct": "30Hello and Hello1020",
            "diff": "Medium",
            "exp": "Operations evaluate left-to-right. 10 + 20 evaluates to 30 before string concatenation, whereas 'Hello' + 10 converts 10 to a string first.",
        },
    ],
    "OOP": [
        {
            "text": "In object-oriented design, what is Polymorphism in Java?",
            "options": [
                "The ability of an object to take on many forms, allowing a subclass method to override a superclass method",
                "Hiding internal implementation details using private access modifiers",
                "Creating multiple classes in a single source file",
                "Inheriting code from multiple parent classes simultaneously"
            ],
            "correct": "The ability of an object to take on many forms, allowing a subclass method to override a superclass method",
            "diff": "Easy",
            "exp": "Polymorphism allows objects of different subtypes to be treated as instances of a common parent type, with runtime dispatch executing the overridden method.",
        },
        {
            "text": "Which SOLID principle states that high-level modules should not depend on low-level modules, but both should depend on abstractions?",
            "options": [
                "Dependency Inversion Principle (DIP)",
                "Single Responsibility Principle (SRP)",
                "Open/Closed Principle (OCP)",
                "Liskov Substitution Principle (LSP)"
            ],
            "correct": "Dependency Inversion Principle (DIP)",
            "diff": "Medium",
            "exp": "The Dependency Inversion Principle mandates that classes decouple by depending on interfaces or abstract classes rather than concrete implementations.",
        },
    ],
    "Java Collections": [
        {
            "text": "What is the average time complexity for `get(key)` and `put(key, value)` operations in a standard `java.util.HashMap`?",
            "options": ["O(1)", "O(log n)", "O(n)", "O(n log n)"],
            "correct": "O(1)",
            "diff": "Easy",
            "exp": "Assuming an evenly distributed hash function with minimal collisions, HashMap lookups and insertions operate in O(1) constant time.",
        },
        {
            "text": "Why should you override both `equals()` and `hashCode()` when using a custom object as a key in a `HashSet` or `HashMap`?",
            "options": [
                "If two objects are equal according to equals(), they must produce the same hashCode, or they cannot be found in bucket lookups",
                "Java will throw a NoSuchMethodError at runtime if hashCode() is omitted",
                "Overriding equals() automatically makes the object thread-safe",
                "It is only required if the class implements the Comparable interface"
            ],
            "correct": "If two objects are equal according to equals(), they must produce the same hashCode, or they cannot be found in bucket lookups",
            "diff": "Medium",
            "exp": "Hash collections determine the storage bucket using hashCode(). If two equal objects have different hashCodes, lookups will search the wrong bucket and fail.",
        },
    ],
    "Exception Handling": [
        {
            "text": "What distinguishes a Checked Exception from an Unchecked Exception in Java?",
            "options": [
                "Checked exceptions (subclasses of Exception except RuntimeException) must be declared or caught at compile-time",
                "Unchecked exceptions crash the JVM immediately without executing finally blocks",
                "Checked exceptions inherit directly from Error",
                "There is no difference; all exceptions in Java must be caught"
            ],
            "correct": "Checked exceptions (subclasses of Exception except RuntimeException) must be declared or caught at compile-time",
            "diff": "Easy",
            "exp": "Checked exceptions are verified by the Java compiler at compile time and mandate either a try-catch block or a throws declaration.",
        },
        {
            "text": "When will a `finally` block NOT execute in Java?",
            "options": [
                "If `System.exit(0)` is invoked or the JVM crashes",
                "If a return statement is executed in the try block",
                "If an uncaught RuntimeException occurs in the catch block",
                "If an OutOfMemoryError is thrown"
            ],
            "correct": "If `System.exit(0)` is invoked or the JVM crashes",
            "diff": "Medium",
            "exp": "A finally block always executes following try/catch blocks unless the JVM terminates abruptly (e.g. System.exit(), power failure, or OS SIGKILL).",
        },
    ],
    "Multithreading": [
        {
            "text": "What is the purpose of the `volatile` keyword in Java?",
            "options": [
                "Ensures changes to a variable are immediately visible across all threads by bypassing thread CPU caches",
                "Locks the object to ensure only one thread can modify it at a time (mutual exclusion)",
                "Makes the variable immutable and thread-safe",
                "Forces the variable to be serialized when written to disk"
            ],
            "correct": "Ensures changes to a variable are immediately visible across all threads by bypassing thread CPU caches",
            "diff": "Medium",
            "exp": "The volatile keyword guarantees memory visibility by reading from and writing directly to main memory rather than thread-local CPU caches.",
        },
        {
            "text": "What happens if two threads attempt to acquire locks on two shared resources in reverse order?",
            "options": [
                "A Deadlock condition can occur where neither thread can proceed",
                "The JVM automatically resolves the conflict and serializes the threads",
                "The thread with lower priority throws an IllegalStateException",
                "The garbage collector releases the oldest acquired lock"
            ],
            "correct": "A Deadlock condition can occur where neither thread can proceed",
            "diff": "Medium",
            "exp": "Acquiring locks in inconsistent orders causes circular wait, resulting in deadlock where both threads remain blocked indefinitely.",
        },
    ],
    "SQL Basics": [
        {
            "text": "Which SQL statement is used to remove duplicate rows from a query result set?",
            "options": ["SELECT DISTINCT", "SELECT UNIQUE", "GROUP ROW", "FILTER DUPLICATES"],
            "correct": "SELECT DISTINCT",
            "diff": "Easy",
            "exp": "SELECT DISTINCT filters out duplicate tuples across the selected columns from the resulting output.",
        },
        {
            "text": "What is the primary difference between `WHERE` and `HAVING` clauses in SQL?",
            "options": [
                "WHERE filters individual rows before aggregation; HAVING filters aggregated groups after GROUP BY",
                "WHERE works only on numeric columns; HAVING works on strings",
                "HAVING is executed before WHERE in the SQL query lifecycle",
                "WHERE cannot be used in queries that contain a JOIN"
            ],
            "correct": "WHERE filters individual rows before aggregation; HAVING filters aggregated groups after GROUP BY",
            "diff": "Medium",
            "exp": "The WHERE clause filters individual records before aggregation. HAVING filters grouped rows after GROUP BY evaluation.",
        },
    ],
    "Database Normalization": [
        {
            "text": "What is required for a relational database table to be in Third Normal Form (3NF)?",
            "options": [
                "It must be in 2NF and have no transitive functional dependencies between non-key attributes",
                "It must contain no NULL values in any column",
                "It must have exactly one foreign key referencing another table",
                "All text attributes must be indexed"
            ],
            "correct": "It must be in 2NF and have no transitive functional dependencies between non-key attributes",
            "diff": "Medium",
            "exp": "3NF requires meeting 2NF and ensuring that every non-prime attribute depends solely on the candidate key with no transitive dependencies.",
        },
    ],
    "Transactions": [
        {
            "text": "In the ACID transaction model, what does Atomicity guarantee?",
            "options": [
                "All operations within the transaction succeed completely, or the entire transaction is rolled back with no partial effects",
                "Transactions executing concurrently do not interfere with one another",
                "Data written by a committed transaction persists permanently even after power failure",
                "The database transitions between valid states adhering to schema rules"
            ],
            "correct": "All operations within the transaction succeed completely, or the entire transaction is rolled back with no partial effects",
            "diff": "Easy",
            "exp": "Atomicity ensures 'all-or-nothing' execution. If any operation within the transaction fails, the entire transaction is aborted.",
        },
    ],
    "HTTP & REST APIs": [
        {
            "text": "Which HTTP methods are defined as idempotent according to the HTTP/1.1 specification?",
            "options": [
                "GET, PUT, and DELETE",
                "POST, PUT, and PATCH",
                "POST and DELETE only",
                "GET and POST only"
            ],
            "correct": "GET, PUT, and DELETE",
            "diff": "Medium",
            "exp": "Idempotent methods can be called multiple times with the exact same side-effects as calling them once. GET, PUT, and DELETE are idempotent.",
        },
        {
            "text": "Which HTTP status code should be returned when a resource is successfully created via a POST request?",
            "options": ["201 Created", "200 OK", "204 No Content", "302 Found"],
            "correct": "201 Created",
            "diff": "Easy",
            "exp": "HTTP 201 Created signifies that the request succeeded and resulted in the creation of a new resource, often returning the resource URL in a Location header.",
        },
    ],
    "Spring Boot": [
        {
            "text": "In Spring Framework, what does Inversion of Control (IoC) mean?",
            "options": [
                "The framework manages the creation, configuration, and lifecycle of beans and injects dependencies rather than the developer creating them with `new`",
                "Child controllers take precedence over parent configurations",
                "Database transactions are inverted to run asynchronously",
                "Static methods can be overridden by dynamic proxies"
            ],
            "correct": "The framework manages the creation, configuration, and lifecycle of beans and injects dependencies rather than the developer creating them with `new`",
            "diff": "Easy",
            "exp": "IoC delegates the responsibility of instantiating, wiring, and managing objects (beans) to the Spring ApplicationContext container.",
        },
        {
            "text": "What is the primary difference between `@Component`, `@Service`, and `@Repository` in Spring Boot?",
            "options": [
                "@Service and @Repository are specialized @Component annotations; @Repository also enables automatic exception translation to DataAccessException",
                "@Service can only be used on interfaces, while @Component is for classes",
                "@Repository creates singleton beans, while @Component creates prototype beans",
                "They are purely decorative with no behavioral differences"
            ],
            "correct": "@Service and @Repository are specialized @Component annotations; @Repository also enables automatic exception translation to DataAccessException",
            "diff": "Medium",
            "exp": "@Service and @Repository are stereotype annotations that indicate architectural intent, and @Repository automatically translates persistence exceptions into Spring's DataAccessException hierarchy.",
        },
    ],
    "Authentication & Security": [
        {
            "text": "Why should password hashes stored in a database always include a cryptographic 'salt'?",
            "options": [
                "To defend against pre-computed rainbow table attacks and ensure identical passwords have unique stored hashes",
                "To encrypt passwords so administrators can decrypt them if lost",
                "To compress long passwords to fit into 32-character database columns",
                "To speed up hash computation during login verification"
            ],
            "correct": "To defend against pre-computed rainbow table attacks and ensure identical passwords have unique stored hashes",
            "diff": "Medium",
            "exp": "A unique random salt combined with slow hashing algorithms (like bcrypt or Argon2) prevents adversaries from using pre-computed rainbow tables.",
        },
        {
            "text": "What are the three parts of a JSON Web Token (JWT)?",
            "options": [
                "Header, Payload, and Signature",
                "Username, Password, and Role",
                "Issuer, Audience, and Expiry",
                "Public Key, Private Key, and Nonce"
            ],
            "correct": "Header, Payload, and Signature",
            "diff": "Easy",
            "exp": "A JWT consists of three Base64URL-encoded parts separated by dots: Header (metadata), Payload (claims), and Signature (cryptographic verification).",
        },
    ],
    "Git": [
        {
            "text": "What is the difference between `git merge` and `git rebase` when integrating feature branch changes?",
            "options": [
                "Git merge preserves branch history with a merge commit; git rebase replays feature commits on top of the base branch for a linear history",
                "Git rebase deletes modified files from the staging area",
                "Git merge cannot handle conflicts, whereas git rebase resolves all conflicts automatically",
                "Git merge runs only on remote repositories"
            ],
            "correct": "Git merge preserves branch history with a merge commit; git rebase replays feature commits on top of the base branch for a linear history",
            "diff": "Medium",
            "exp": "Merge retains the full chronological graph including a merge commit. Rebase rewrites history by applying commits one-by-one onto the new base tip.",
        },
    ],
    "Unit Testing": [
        {
            "text": "In unit testing, what is the core role of a Test Double or 'Mock' object?",
            "options": [
                "To simulate external dependencies (like databases or APIs) in isolation with pre-programmed behaviors and verifications",
                "To benchmark application performance under heavy load",
                "To run tests concurrently on multiple CPU cores",
                "To automatically generate production code from tests"
            ],
            "correct": "To simulate external dependencies (like databases or APIs) in isolation with pre-programmed behaviors and verifications",
            "diff": "Easy",
            "exp": "Mocks allow isolated unit testing of the class under test without coupling to real external databases, networks, or file systems.",
        },
    ],
    "Deployment & Docker": [
        {
            "text": "What is the main advantage of using multi-stage builds in a `Dockerfile`?",
            "options": [
                "It separates build-time dependencies (like compilers) from the final runtime image, drastically reducing image size and attack surface",
                "It enables running multiple container instances inside a single process",
                "It eliminates the need for container networking",
                "It allows running Windows and Linux containers simultaneously"
            ],
            "correct": "It separates build-time dependencies (like compilers) from the final runtime image, drastically reducing image size and attack surface",
            "diff": "Medium",
            "exp": "Multi-stage builds copy only the compiled binaries/artifacts into a lean production base image, stripping away heavy SDKs, source code, and build caches.",
        },
    ],
    "Python Basics": [
        {
            "text": "In Python, which of the following data types is mutable?",
            "options": ["List", "Tuple", "String", "Integer"],
            "correct": "List",
            "diff": "Easy",
            "exp": "Lists and dictionaries in Python are mutable (can be modified in-place). Tuples, strings, and integers are immutable.",
        },
        {
            "text": "What is the output of `[x**2 for x in range(4) if x % 2 == 0]` in Python?",
            "options": ["[0, 4]", "[0, 1, 4, 9]", "[4]", "[1, 9]"],
            "correct": "[0, 4]",
            "diff": "Easy",
            "exp": "range(4) yields 0, 1, 2, 3. The condition `x % 2 == 0` filters for 0 and 2. Squaring them produces [0, 4].",
        },
    ],
    "Data Structures": [
        {
            "text": "What is the worst-case time complexity of searching for an element in an unsorted array of size N?",
            "options": ["O(N)", "O(log N)", "O(1)", "O(N^2)"],
            "correct": "O(N)",
            "diff": "Easy",
            "exp": "In an unsorted array, a linear search must inspect up to all N elements in the worst case.",
        },
    ],
    "Concurrency": [
        {
            "text": "In CPython, what is the Global Interpreter Lock (GIL)?",
            "options": [
                "A mutex that allows only one native thread to execute Python bytecode at a time, limiting CPU-bound multithreading",
                "A security feature that prevents unauthorized script access to the filesystem",
                "A garbage collector mechanism that prevents memory fragmentation",
                "A network lock that serializes HTTP requests in web applications"
            ],
            "correct": "A mutex that allows only one native thread to execute Python bytecode at a time, limiting CPU-bound multithreading",
            "diff": "Medium",
            "exp": "The GIL ensures memory safety in CPython by permitting only one thread to execute Python bytecode simultaneously.",
        },
    ],
    "Database Design": [
        {
            "text": "What is the primary role of a Foreign Key constraint in relational database design?",
            "options": [
                "Enforces referential integrity by ensuring a child record points to an existing parent record",
                "Automatically encrypts foreign data columns",
                "Duplicates data to accelerate search queries across multiple disks",
                "Replaces the requirement for indexing columns"
            ],
            "correct": "Enforces referential integrity by ensuring a child record points to an existing parent record",
            "diff": "Easy",
            "exp": "Foreign keys maintain referential integrity between tables, preventing orphan records and invalid references.",
        },
    ],
    "FastAPI": [
        {
            "text": "How does FastAPI achieve high performance and automatic OpenAPI documentation generation?",
            "options": [
                "By leveraging Starlette for async routing and Pydantic for strict type validation and schema serialization",
                "By compiling Python code into C++ at runtime",
                "By using thread pools for every incoming synchronous request",
                "By caching all database queries in memory"
            ],
            "correct": "By leveraging Starlette for async routing and Pydantic for strict type validation and schema serialization",
            "diff": "Medium",
            "exp": "FastAPI builds directly on top of Starlette (for high-speed async HTTP) and Pydantic (for data validation and automatic OpenAPI/JSON-schema generation).",
        },
    ],
    "Testing & PyTest": [
        {
            "text": "In pytest, what is a `@pytest.fixture` used for?",
            "options": [
                "Providing reusable, modular setup and teardown dependencies to test functions",
                "Marking a test as permanently skipped",
                "Running tests in parallel across remote servers",
                "Mocking the Python interpreter version"
            ],
            "correct": "Providing reusable, modular setup and teardown dependencies to test functions",
            "diff": "Easy",
            "exp": "Fixtures define reusable baseline context, test data, and database connections that are injected into test functions.",
        },
    ],
    "HTML & CSS": [
        {
            "text": "In modern CSS layout, what is the key difference between Flexbox and CSS Grid?",
            "options": [
                "Flexbox is primarily 1-dimensional (row or column), while CSS Grid is 2-dimensional (rows and columns simultaneously)",
                "Flexbox is hardware-accelerated, whereas Grid is not",
                "Grid works only on desktop screens, while Flexbox is mobile-only",
                "Flexbox requires JavaScript to calculate child positions"
            ],
            "correct": "Flexbox is primarily 1-dimensional (row or column), while CSS Grid is 2-dimensional (rows and columns simultaneously)",
            "diff": "Easy",
            "exp": "Flexbox is designed for linear single-axis layout distribution, while CSS Grid handles complex two-dimensional spatial layouts.",
        },
    ],
    "JavaScript & TypeScript": [
        {
            "text": "What does the `async/await` syntax do in JavaScript?",
            "options": [
                "Provides syntactical sugar over Promises, allowing asynchronous code to be structured like synchronous code",
                "Executes the function on a separate background Web Worker thread",
                "Freezes the main UI thread until the promise resolves",
                "Converts JavaScript objects into binary JSON"
            ],
            "correct": "Provides syntactical sugar over Promises, allowing asynchronous code to be structured like synchronous code",
            "diff": "Easy",
            "exp": "async/await wraps Promise execution in clean readable syntax, pausing coroutine execution without blocking the browser event loop.",
        },
        {
            "text": "In TypeScript, what is the primary benefit of static type checking at compile time?",
            "options": [
                "Catches type mismatches, null reference errors, and API contract bugs before running in production",
                "Makes the compiled JavaScript code execute 10x faster in the browser",
                "Replaces the need for writing unit tests",
                "Automatically bundles assets for deployment"
            ],
            "correct": "Catches type mismatches, null reference errors, and API contract bugs before running in production",
            "diff": "Easy",
            "exp": "TypeScript analyzes code statically during compilation, catching bugs and verifying API contracts before runtime execution.",
        },
    ],
    "React & Next.js": [
        {
            "text": "In React 18 / Next.js App Router, what is the default rendering paradigm for components in the `app` directory?",
            "options": [
                "React Server Components (RSC) rendered on the server with zero client bundle overhead",
                "Client-side Single Page Application rendered solely in the browser",
                "Static HTML generated only at build time with no dynamic updates",
                "Web Components running inside shadow DOM"
            ],
            "correct": "React Server Components (RSC) rendered on the server with zero client bundle overhead",
            "diff": "Medium",
            "exp": "Next.js App Router components are Server Components by default, executing exclusively on the server and sending HTML/RSC payloads with zero client JavaScript.",
        },
    ],
    "Node.js & Express": [
        {
            "text": "Why is the Node.js event loop described as non-blocking?",
            "options": [
                "I/O operations (like file and network access) are delegated to the OS kernel/libuv thread pool, freeing the main thread to handle incoming requests",
                "Every incoming HTTP request spawns an independent native OS thread",
                "Node.js runs in an isolated virtual machine that bypasses CPU interrupts",
                "Database queries are executed synchronously in memory"
            ],
            "correct": "I/O operations (like file and network access) are delegated to the OS kernel/libuv thread pool, freeing the main thread to handle incoming requests",
            "diff": "Medium",
            "exp": "Node.js uses single-threaded asynchronous I/O via libuv. Slow operations are dispatched asynchronously so the event loop continues processing requests.",
        },
    ],
}
