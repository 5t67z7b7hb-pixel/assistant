# SQL Documentation

**Domain:** Relational databases and SQL  
**Purpose:** A practical introduction to modeling, querying, and safely
maintaining relational data. SQL syntax and features vary by database; verify
examples against the database engine and version in use.

## What SQL is

Structured Query Language (SQL) is used to define, read, and modify data in
relational database systems. A relational database organizes data into tables
with rows and columns. Tables can be related through keys, and constraints
help ensure that stored data remains valid.

SQL is declarative: a query describes the desired result, while the database
engine chooses an execution plan. SQL is standardized, but database products
provide different data types, functions, and extensions.

## Tables, keys, and constraints

Design tables around distinct entities and define how they relate. A primary
key uniquely identifies a row. A foreign key references a key in another
table and can enforce referential integrity. `NOT NULL`, `UNIQUE`, `CHECK`,
and foreign-key constraints express rules in the database itself.

```sql
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    ordered_at TIMESTAMP NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL CHECK (total_amount >= 0)
);
```

Exact type names, identity-column syntax, and constraint options differ
between systems. Choose types that represent the domain accurately; use a
fixed-precision numeric type for monetary values rather than binary floating
point.

## Reading data

`SELECT` retrieves rows. Specify the columns needed, filter with `WHERE`, and
use `ORDER BY` when result order matters. `LIMIT` is common but not universal;
some databases use different syntax.

```sql
SELECT customer_id, name
FROM customers
WHERE email LIKE '%@example.com'
ORDER BY name;
```

Use joins to combine related rows. An `INNER JOIN` returns matching rows;
`LEFT JOIN` keeps every row from the left side and fills unmatched right-side
columns with `NULL`.

```sql
SELECT c.name, o.order_id, o.ordered_at, o.total_amount
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
WHERE o.total_amount >= 100
ORDER BY o.ordered_at DESC;
```

Aggregate functions such as `COUNT`, `SUM`, `AVG`, `MIN`, and `MAX` summarize
rows. `GROUP BY` forms groups and `HAVING` filters those groups:

```sql
SELECT customer_id, COUNT(*) AS order_count, SUM(total_amount) AS lifetime_total
FROM orders
GROUP BY customer_id
HAVING COUNT(*) >= 2;
```

`WHERE` filters individual rows before grouping; `HAVING` filters the
aggregated groups. Be deliberate about `NULL`: it represents an unknown or
missing value, and comparisons with it do not behave like ordinary equality.
Use `IS NULL` or `IS NOT NULL` to test for it.

## Adding and changing data

`INSERT` adds rows, `UPDATE` changes rows, and `DELETE` removes rows. Include
an explicit column list in inserts and a restrictive condition when changing
or deleting selected rows.

```sql
INSERT INTO customers (customer_id, email, name)
VALUES (101, 'asha@example.com', 'Asha');

UPDATE customers
SET name = 'Asha Rao'
WHERE customer_id = 101;
```

Before running an `UPDATE` or `DELETE`, check that its `WHERE` condition
identifies the intended rows. Omitting `WHERE` applies the operation to every
row in the table.

## Transactions

A transaction groups related changes into a unit. The ACID properties
describe common transaction guarantees: atomicity, consistency, isolation,
and durability. Use a transaction when partial completion would leave data
in an invalid state.

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 25.00
WHERE account_id = 1;

UPDATE accounts
SET balance = balance + 25.00
WHERE account_id = 2;

COMMIT;
```

If a step fails, roll back rather than committing a partial operation.
Transaction syntax, isolation levels, and locking behavior vary by database;
handle errors in application code and follow the engine's transaction API.

## Safe application queries

Pass user-provided values as bound parameters using the database driver's
parameterized-query interface. Do not build SQL by concatenating input into
the query string; parameterization helps prevent SQL injection and handles
quoting and data types correctly.

```python
cursor.execute(
    "SELECT customer_id, name FROM customers WHERE email = ?",
    (email,),
)
```

The placeholder shown is used by some drivers, including Python's SQLite
driver. Other drivers use different placeholder styles; follow the selected
driver's documentation. Parameters represent values, not SQL identifiers.
For dynamic table names, column names, or sort direction, use a strict
allowlist and construct the query only from trusted choices.

Use least-privilege database accounts, restrict access to the data needed by
the application, protect credentials, and avoid logging sensitive query
values. Validate authorization in application code; a query parameter alone
does not determine whether a user is allowed to access a record.

## Indexes and query performance

An index can speed up filtering, joining, or ordering on selected columns, at
the cost of storage and additional work during writes. Index columns that
match real query patterns rather than indexing every column.

Use the database's query-plan tools (for example, `EXPLAIN`) to understand how
a query is executed. Check row counts, join conditions, selected columns, and
filter selectivity. Avoid assuming that an index will always be used or that
a query's performance is portable between engines.

## Schema changes and reliability

Manage schema changes through reviewed, versioned migrations. Make changes
that can be applied consistently across environments, plan for existing data,
and consider deployment order when application versions and schemas change
independently. Back up important data and test migrations on representative
data before production use.

Use constraints to protect core invariants, handle database errors explicitly,
and test both successful operations and failure cases. Keep database-specific
SQL isolated when portability is important, and test against the actual
database engine used in deployment.

## Common pitfalls

- Relying on row order without `ORDER BY`.
- Comparing `NULL` with `=` instead of using `IS NULL`.
- Using `SELECT *` when only a few columns are needed.
- Forgetting that joins can multiply rows when relationships are one-to-many.
- Updating or deleting rows without confirming the `WHERE` condition.
- Concatenating untrusted input into SQL statements.
- Assuming SQL dialects, data types, transaction behavior, or placeholders
  are identical across database products.

## Further reading

- PostgreSQL documentation: https://www.postgresql.org/docs/
- SQLite documentation: https://www.sqlite.org/docs.html
- Python `sqlite3` documentation: https://docs.python.org/3/library/sqlite3.html
