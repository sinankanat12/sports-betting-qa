# Part A.2 - Bug Reports

Defects found during execution of top 3 scenarios (TC-01, TC-02, TC-06) and exploratory testing around the bet placement flow.

---

## TOP 3 — Highest Impact Defects

---

### BUG-001: No Balance Validation — UI Does Not Update Balance After Bet, API Allows Negative Balance

**Severity**: Critical

**Found During**: TC-03, TC-06 execution

**Reproduction Steps**:
1. Start with balance €120.00 (confirmed via API and UI header)
2. Select any match odds and enter stake €100.00
3. Click "Place Bet" → succeeds, receipt modal shown
4. Close modal — observe UI header balance: still shows **€120.00** (not updated)
5. Without refreshing the page, place another €100.00 bet → succeeds (UI still shows €120.00, so no "insufficient balance" warning)
6. Repeat a third time → still succeeds
7. Refresh the page — UI now shows **-€180.00**
8. Confirm via `GET /api/balance` → `{"balance": -180}`

**Expected Result**:
- **UI**: Balance should update immediately after each bet placement (Ref: Feature Spec Section 2.3 — "stake is deducted" on success; Domain Context — "The balance is shared across the header and the bet slip")
- **API**: Bets exceeding available balance should be rejected with 422 and "Insufficient balance" error (Ref: Feature Spec Section 4.1 — "Must not exceed available balance" at both UI + API layers)

**Actual Result**: Two compounding failures:
1. **UI does not update balance** after placing a bet — header keeps showing the stale balance until page refresh. Because the UI shows €120.00, the stake validation on the frontend never triggers "Insufficient balance"
2. **API has no balance check** — it accepts bets regardless of available funds, allowing negative balances

| Action | UI Balance | API Balance |
|---|---|---|
| Initial state | €120.00 | €120 |
| After bet #1 (€100) | €120.00 (stale) | €20 |
| After bet #2 (€100) | €120.00 (stale) | -€80 |
| After bet #3 (€100) | €120.00 (stale) | -€180 |
| After page refresh | -€180.00 | -€180 |

**Business Impact**: This is the most severe bug in the application — a combination of two failures creating unlimited financial exposure:
- **Direct financial loss**: Users can place unlimited bets with money they don't have
- **Regulatory violation**: Gambling regulations require operators to prevent users from wagering beyond their deposited funds
- **Compounding effect**: The stale UI balance masks the problem from the user — they have no indication that their balance is being drained, let alone going negative
- **Abuse vector**: A malicious user could rapidly place high-stake bets without any client-side or server-side restriction

**Evidence**: Verified via headless Chrome + API calls. Starting balance: €120. Three consecutive €100 bets placed via UI without page refresh — all accepted (200 OK). UI showed €120 throughout. API balance after: -€180. Feature Spec Section 4.1 requires balance validation at both UI and API layers.

---

### BUG-002: Receipt Modal Payout Uses Hardcoded Multiplier (×2) Instead of Actual Odds

**Severity**: Critical

**Found During**: TC-01 execution, TC-05 verification

**Reproduction Steps**:
1. Navigate to app with `?user-id=candidate-0e2d9b4c`
2. Select odds for any match with stake €5.00
3. Observe bet slip potential payout (correctly calculated as stake × odds)
4. Click "Place Bet"
5. Observe receipt modal payout value
6. Repeat with different matches/selections to confirm pattern

**Expected Result**: Receipt modal payout = stake × odds, matching the bet slip value. Per Feature Spec Section 2.4: "Receipt must show: Potential payout." Per Domain Context: "Payout — calculated as stake × odds. All values should be consistent with what was shown before placement."

**Actual Result**: Receipt modal **always** shows `stake × 2` regardless of actual odds. The receipt displays the correct odds value but the payout ignores it:

| Selection | Odds | Bet Slip (correct) | Receipt (wrong) | Receipt formula |
|---|---|---|---|---|
| ManUtd HOME | 2.45 | €12.25 | €10.00 | 5 × **2** = 10 |
| ManUtd DRAW | 3.10 | €15.50 | €10.00 | 5 × **2** = 10 |
| Bayern HOME | 1.45 | €7.25 | €10.00 | 5 × **2** = 10 |
| Bayern AWAY | 6.00 | €30.00 | €10.00 | 5 × **2** = 10 |

Note: The API (`POST /api/place-bet`) returns the **correct** payout (e.g., 12.25 for 5×2.45). The bug is isolated to the receipt modal's UI rendering — it appears to use a hardcoded multiplier of 2 instead of the actual odds value.

**Business Impact**: Users see a wrong payout on their bet confirmation regardless of which odds they selected. For odds > 2.00, users see a lower payout than expected (loss of trust). For odds < 2.00 (e.g., 1.45), users see a higher payout than reality (false expectation). This is a critical trust and accuracy issue — the receipt is the user's proof of bet placement, and it is always wrong.

**Evidence**: Verified via headless Chrome automation across 4 different odds values. Receipt modal `#modal-success-payout` always shows €10.00 for €5.00 stake regardless of odds. API response payout is correct. Pattern confirms: receipt payout = stake × 2 (hardcoded).

---

### BUG-003: Past Matches Accept Bets — "Upcoming" Constraint Not Enforced

**Severity**: High

**Found During**: Exploratory testing

**Reproduction Steps**:
1. Navigate to app — observe match list titled "Upcoming Football Matches"
2. Note that the first several matches display a **"PAST"** badge (e.g., Manchester Utd vs Chelsea, kickoff 27 Feb 2026)
3. Click odds for a PAST match and enter a stake
4. Click "Place Bet" — bet is accepted
5. Alternatively, via API: `POST /api/place-bet` with `matchId: "premier-league-manutd-chelsea"` (kickoff 2026-02-27) → returns 200 OK

**Expected Result**: Bets on past matches should be rejected. Per Feature Spec Section 1: "Event Type: Upcoming/Pre-match events only (no live betting)." Per Section 3 Business Rules: "Event type: Upcoming matches only." The UI correctly labels these as "PAST" but neither the UI nor the API prevents bet placement.

**Actual Result**: Both UI and API accept bets on past matches with no restriction. The UI shows the "PAST" badge but odds buttons remain active and clickable. API returns 200 with a successful bet confirmation for matches with kickoff dates weeks in the past.

**Business Impact**: In a real betting platform, accepting bets on matches that have already been played is a critical integrity issue — the outcome is already known, enabling guaranteed-win bets (match-fixing equivalent). While this is a test application with static data, enforcing the "upcoming only" rule is an explicit spec requirement and a fundamental betting domain constraint.

**Evidence**: Verified via UI and API. Match "premier-league-manutd-chelsea" has kickoff date 2026-02-27 (3+ weeks ago). UI displays "PAST" badge. API `POST /api/place-bet` with this matchId returns `{"message": "Bet placed successfully", "stake": 5, "odds": 2.45, "payout": 12.25}` — 200 OK. Feature Spec Sections 1 and 3 explicitly restrict to upcoming matches only.

---

## Additional Defects

---

### BUG-004: Place-Bet API Returns Wrong Currency Code

**Severity**: Critical

**Found During**: TC-06 execution, exploratory API testing

**Reproduction Steps**:
1. Call `GET /api/balance` with header `x-user-id: candidate-0e2d9b4c`
2. Observe response: `{"balance": 125.5, "currency": "EUR"}`
3. Call `POST /api/place-bet` with a valid bet payload
4. Observe response: `{"message": "Bet placed successfully", ..., "currency": "USD"}`

**Expected Result**: Place-bet response returns `"currency": "EUR"`. Per Feature Spec Section 5.3, the POST /api/place-bet 200 response specifies `currency: "EUR"`. Per Section 3 Business Rules: `Currency: EUR (€)`.

**Actual Result**: `/api/balance` correctly returns `"currency": "EUR"` but `/api/place-bet` returns `"currency": "USD"`.

**Business Impact**: The API contract is violated — the spec explicitly defines EUR as the currency. Any client consuming the place-bet response for currency formatting would display incorrect currency. In a real multi-currency environment, this could lead to financial discrepancies and incorrect user-facing amounts.

**Evidence**: Verified via `curl` commands. Balance response: `"currency": "EUR"`. Place-bet response: `"currency": "USD"`. Feature Spec Section 5.3 and Swagger schema both specify `currency: "EUR"`.

---

### BUG-005: Reset Balance Endpoint Does Not Actually Persist Reset

**Severity**: Critical

**Found During**: TC-06 execution, test fixture setup

**Reproduction Steps**:
1. Place one or more bets to reduce balance below €125.50
2. Call `POST /api/reset-balance` with header `x-user-id: candidate-0e2d9b4c`
3. Observe response: `{"message": "Balance reset successfully", "balance": 125.5, "currency": "EUR"}`
4. Immediately call `GET /api/balance` with the same header
5. Observe response: `{"balance": 120, "currency": "EUR"}`

**Expected Result**: After a successful reset, `GET /api/balance` should return `{"balance": 125.5}`, matching the reset response. Per Feature Spec Section 5.3: "Response body and persisted state must be consistent after reset."

**Actual Result**: The reset endpoint returns a 200 with `"balance": 125.5` (indicating success), but the actual persisted balance is **not reset** — a subsequent GET returns the pre-reset value (e.g., `120`). The response lies about the state.

**Business Impact**: Data integrity issue — the API reports a successful operation but the state is unchanged. For QA purposes, this undermines test isolation — tests that depend on a clean balance state cannot reliably set up preconditions, leading to flaky or cascading test failures.

**Evidence**: Verified via sequential `curl` calls. `POST /api/reset-balance` → `{"balance": 125.5}`. Immediately followed by `GET /api/balance` → `{"balance": 120}`. The Feature Spec Section 5.3 explicitly requires consistency. Notably, the Swagger documentation for this endpoint states: "response payload may differ from persisted balance" — confirming this is a known inconsistency between the API behavior and the Feature Specification requirement.

---

### BUG-006: Receipt Modal Displays Teams in Reversed Order

**Severity**: High

**Found During**: TC-01 execution

**Reproduction Steps**:
1. Navigate to app and select odds for the first match
2. API data shows: `homeTeam: "Manchester Utd"`, `awayTeam: "Chelsea"`
3. Match list correctly displays: "Manchester Utd vs Chelsea"
4. Place a bet on this match
5. Observe the match label in the success receipt modal

**Expected Result**: Receipt shows "Manchester Utd vs Chelsea" (home team first). Per Feature Spec Domain Context — Match Ordering: "The 'home' team is always listed first (left position), the 'away' team second (right position). This convention carries through to the bet receipt."

**Actual Result**: Receipt shows **"Chelsea vs Manchester Utd"** (teams reversed)

**Business Impact**: In sports betting, home/away distinction is significant as it affects odds and user decisions. Showing reversed teams in the receipt creates confusion about which bet was actually placed. Directly violates the Feature Spec Match Ordering requirement.

**Evidence**: Receipt modal `#modal-success-match` text: "Chelsea vs Manchester Utd". API match data confirms homeTeam = "Manchester Utd". Feature Spec explicitly states home team must be listed first, including in the receipt.

---

### BUG-007: Malformed JSON Payload Returns 500 Instead of 400

**Severity**: High

**Found During**: Exploratory API testing

**Reproduction Steps**:
1. Send `POST /api/place-bet` with a malformed JSON body containing an invalid number: `{"matchId":"premier-league-manutd-chelsea","selection":"HOME","stake":100.001.00}`
2. Observe HTTP response status code and body

**Expected Result**: API returns **400 Bad Request** with a clear error message. Per Feature Spec Section 4.3: "Request body must be valid JSON object" → "Reject malformed/non-object payloads." Per Section 5.3 Expected Error Classes: `400 malformed payload`.

**Actual Result**: API returns **500 Internal Server Error** with `{"error":"internal_server_error","message":"Unable to process request."}`. This indicates an unhandled exception on the server side.

**Business Impact**: A 500 error from trivially malformed input indicates missing input validation at the API boundary. In production, this could trigger false alerts, pollute error monitoring, and represents a potential attack surface.

**Evidence**: Verified via `curl`. HTTP status: 500. Feature Spec Section 4.3 and 5.3 explicitly define 400 as the expected error class for malformed payloads.

---

### BUG-008: Match Count Label Does Not Update After Filtering

**Severity**: Low

**Found During**: Exploratory testing (Filters)

**Reproduction Steps**:
1. Navigate to app — observe header shows "Showing 103 matches" with 103 match cards visible
2. Open the Odds filter and set minimum odds to 5.00
3. Click "Apply"
4. Observe: match cards are filtered down to 10 visible results
5. Observe: the count label still shows "Showing 103 matches"

**Expected Result**: After applying a filter, the "Showing X matches" label should reflect the filtered count (e.g., "Showing 10 matches"). Per Feature Spec Section 2.6: filters are a functional part of the match list.

**Actual Result**: Count label remains **"Showing 103 matches"** even though only **10 match cards** are displayed.

**Business Impact**: Minor UX inconsistency — the count contradicts what is visible on screen.

**Evidence**: Verified via headless Chrome. Before filter: 103/103. After odds ≥ 5.00 filter: "Showing 103 matches" but only 10 cards visible.

---

### BUG-009: API Rejects Lowercase Selection Values Without Clear Documentation

**Severity**: Low

**Found During**: Exploratory API testing

**Reproduction Steps**:
1. Send `POST /api/place-bet` with `{"matchId": "premier-league-manutd-chelsea", "selection": "home", "stake": 5}`
2. Observe 422 response: `{"error": "invalid_selection", "message": "Selection must be one of: HOME, DRAW, AWAY."}`
3. Send same request with `"selection": "HOME"` → 200 success

**Expected Result**: API either accepts case-insensitive values or Swagger docs explicitly document the uppercase requirement. Per Feature Spec Section 4.2: selection "Must be one of HOME, DRAW, AWAY."

**Actual Result**: Only uppercase values accepted. Lowercase silently rejected.

**Business Impact**: Minor — external API consumers could encounter unexpected integration failures.

**Evidence**: Verified via `curl`. Lowercase "home" → 422. Uppercase "HOME" → 200.

---

### BUG-010: Balance API Returns Inconsistent Decimal Formatting

**Severity**: Low

**Found During**: TC-06 execution, exploratory API testing

**Reproduction Steps**:
1. Call `GET /api/balance` → `{"balance": 125.5, "currency": "EUR"}`

**Expected Result**: Financial amounts with consistent 2-decimal formatting: `125.50`.

**Actual Result**: Balance returned as `125.5` (missing trailing zero).

**Business Impact**: Minor — different frontend implementations may display "€125.5" vs "€125.50".

**Evidence**: Verified via `curl`. Balance returns `125.5` instead of `125.50`.
