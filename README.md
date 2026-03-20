# Sports Betting QA

Test automation framework for the [Single Bet Placement](https://qae-assignment-tau.vercel.app) application.

## Setup

Requires **Python 3.10+** and **Google Chrome**.

```bash
git clone https://github.com/sinankanat12/sports-betting-qa.git
cd sports-betting-qa
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running Tests

```bash
pytest tests/ -v                              # All tests
pytest -m api -v                              # API tests only
pytest -m e2e -v                              # E2E tests only
HEADLESS=false pytest -m e2e -v               # E2E with visible browser
```

## Project Structure

```
config/settings.py          — Environment config (base URL, user-id, timeouts)
api/betting_client.py       — API client wrapper (requests)
pages/                      — Page Object Model (Selenium)
tests/
  test_api_stake_validation.py  — API: stake boundary validation (9 cases)
  test_e2e_bet_placement.py     — E2E: critical bet placement journey
docs/
  test_plan.md              — Part A.1: 6 prioritized test scenarios
  bug_reports.md            — Part A.2: Defect reports
  strategy.md               — Part C: Strategy & recommendations
```

## Deliverables

| Part | File | Description |
|---|---|---|
| A.1 | [test_plan.md](docs/test_plan.md) | Test plan — 6 prioritized scenarios |
| A.2 | [bug_reports.md](docs/bug_reports.md) | Bug reports from execution & exploratory testing |
| B | `tests/` | Automation framework + 2 automated tests |
| C | [strategy.md](docs/strategy.md) | Strategy & scaling recommendations |
