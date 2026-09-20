# daily-practice


An AI-assisted daily practice log. Each day a GitHub Actions workflow asks Claude
for one small exercise (Python, Pandas or SQL) with a solution and tests, and
commits it under `YYYY/MM/`.

## How it works
- `scripts/generate.py` picks a topic from a rotating curriculum and calls the Claude API.
- `.github/workflows/daily.yml` runs it on a schedule and commits the result.

## Topics covered
Python fundamentals, Pandas data cleaning and reshaping, and SQL (joins, window
functions, CTEs).

## My notes
Add what you learned or changed here as you go.
