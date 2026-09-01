# Orbit Konnect — Customer Automated Test Suite

## Purpose

This suite converts the Customer Module manual Swagger checks into repeatable
pytest tests.

It uses a disposable SQLite database and FastAPI dependency overrides. It
does not connect to the Orbit Konnect development database.

## Coverage

- Customer schema validation
- Whitespace normalization
- Unknown-field rejection
- `is_active` protection
- Customer creation
- Duplicate phone
- Duplicate email
- Company/tenant scoping
- Customer retrieval
- Missing customer
- Customer update
- Clearing email
- Deactivation persistence
- Activation persistence
- Pagination

## Install test dependencies

From the Orbit Konnect project root:

```bash
python -m pip install pytest httpx
```

## Run all Customer tests

```bash
python -m pytest -q
```

## Run only schema tests

```bash
python -m pytest tests/unit/test_customer_schema.py -q
```

## Run only API tests

```bash
python -m pytest tests/integration/test_customer_api.py -q
```

## Important

The API tests override:

- `backend.app.dependencies.database.get_db`
- `backend.app.dependencies.auth.get_current_user`

The real JWT authentication implementation is therefore not being tested by
these Customer tests. Authentication should have its own test suite.

The authenticated test identity is represented by a small test object carrying
`company_id`. This directly exercises the Customer router's tenant-scoping
behavior without requiring real JWT generation.

The test database is separate from the development database.

## Expected result

A clean run should finish with all tests passing and zero failures.
