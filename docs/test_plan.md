# Part A.1 - Test Plan: Single Bet Placement

## Application Under Test
- **URL**: https://qae-assignment-tau.vercel.app
- **Feature**: Single Bet Placement
- **Reference**: Feature Specification — Single Bet Placement

---

### TC-01: Happy Path — Place a Single Bet Successfully

**Priority**: Critical

**Risk Rationale**: This is the core revenue-generating flow. If users cannot complete the end-to-end bet placement journey, the business loses direct income. Any regression here blocks the primary use case entirely. Covers requirements from Sections 2.1 (Match List), 2.2 (Bet Slip), 2.3 (Place Bet Interaction), and 2.4 (Success Receipt).

**Steps**:
1. Navigate to the application with valid user-id
2. Wait for match list to load (Ref: Section 2.1)
3. Click the "1" (Home) odds button on the first match (e.g., Manchester Utd vs Chelsea, odds 2.45)
4. Verify bet slip shows the selected match, selection ("Home"), correct odds, and available balance (Ref: Section 2.2 — "Shows entered stake, available balance, and computed potential payout")
5. Enter a valid stake: €5.00
6. Verify potential payout displays €12.25 (5.00 × 2.45) (Ref: Domain Context — "Payout: calculated as stake × odds")
7. Click "Place Bet" — verify button enters "Placing..." loading state (Ref: Section 2.3 — "button enters loading state")
8. Verify success receipt modal appears with all required fields (Ref: Section 2.4):
   - Bet ID (non-empty unique identifier)
   - Match details with correct team ordering: home team first (Ref: Domain Context — Match Ordering)
   - Selection (e.g., "Home")
   - Stake (€5.00)
   - Odds at placement (2.45)
   - Potential payout consistent with bet slip pre-placement value (Ref: Domain Context — "All values should be consistent with what was shown before placement")
   - Placement timestamp
9. Close modal — verify user returns to main flow without active selection (Ref: Section 2.4 — "Closing receipt returns user to main flow without active selection")
10. Verify balance decreased from €125.50 to €120.50 in both UI header and via API (Ref: Section 2.3 — "stake is deducted")

**Expected Result**: Bet is placed successfully. Receipt modal shows all required fields (Bet ID, Match, Selection, Stake, Odds, Payout, Timestamp). All receipt values are consistent with what was displayed in the bet slip before placement. Balance is deducted by the stake amount. Closing receipt clears active selection and returns user to main flow.

---

### TC-02: Stake Validation — Reject Invalid Stake Amounts

**Priority**: Critical

**Risk Rationale**: Stake boundaries protect the business from financial exposure (accepting bets above maximum of €100.00) and revenue loss (accepting bets below minimum of €1.00). If validation fails at either the UI or API layer, the system could process bets that violate business rules (Ref: Section 3, Section 4.1). Note: There is an inconsistency in the spec — Section 3 (Business Rules) defines stake min as "€1.00" and Section 4.4 (UI Error Messaging) states "Minimum stake is €1.00", but Section 4.1 (Stake Validation table) states "Minimum €1.01 (positive values)." The 1.01 value matches the minimum odds defined in Section 3 ("Minimum odds: 1.01"), suggesting this may be a spec typo where the odds minimum was inadvertently written in the stake validation row. This test uses €1.00 as the valid minimum per Section 3 and Section 4.4.

**Steps**:
1. Select any match and odds
2. Enter stake €0.99 (below minimum of €1.00, Ref: Section 3 — Stake min) → attempt to place bet
3. Enter stake €1.00 (exact minimum boundary, Ref: Section 3 — Stake min) → attempt to place bet
4. Enter stake €100.00 (exact maximum boundary, Ref: Section 3 — Stake max) → attempt to place bet
5. Enter stake €100.01 (above maximum of €100.00, Ref: Section 3 — Stake max) → attempt to place bet
6. Enter stake €1.999 (3 decimal places, exceeds precision limit, Ref: Section 3 — "Up to 2 decimal places") → attempt to place bet
7. Enter non-numeric text (e.g., "abc") → observe input behavior (Ref: Section 4.1 — "Must be numeric")
8. Enter negative value (e.g., "-5") → observe input behavior

**Expected Result**:
- €0.99: Error message "Minimum stake is €1.00" (Ref: Section 4.4), bet not placed
- €1.00: Bet accepted (valid minimum boundary per Section 3)
- €100.00: Bet accepted (valid maximum boundary per Section 3)
- €100.01: Error message "Maximum stake is €100.00" (Ref: Section 4.4), bet not placed
- €1.999: Error message about decimal precision, bet not placed
- Non-numeric/negative: Input rejected or clear error shown (Ref: Section 4.4 — "Stake input accepts numeric values with a single decimal separator and up to 2 decimal places")

---

### TC-03: Balance Boundary — Insufficient Funds Prevention

**Priority**: High

**Risk Rationale**: Users must not be able to bet more than their available balance (Ref: Section 4.1 — "Must not exceed available balance"). If this check fails, the system could allow negative balances, creating financial liability and potential abuse scenarios.

**Steps**:
1. Confirm starting balance is €125.50 (reset if needed via POST /api/reset-balance)
2. Select any match and odds
3. Enter stake €125.51 (exceeds balance by €0.01)
4. Click "Place Bet"
5. Verify error is displayed: "Insufficient balance" (Ref: Section 4.4)
6. Enter stake €125.50 (exactly equal to balance)
7. Click "Place Bet"
8. Verify bet is placed successfully
9. Verify balance is now €0.00

**Expected Result**: Stake exceeding balance is rejected with "Insufficient balance" error. Stake exactly equal to balance is accepted. Balance reaches €0.00 after successful placement.

---

### TC-04: Odds Selection Update and Bet Slip Controls

**Priority**: High

**Risk Rationale**: The spec states "Selecting a new odds button replaces the previous selection" and "Only one bet can be active at a time" (Ref: Section 2.1, 2.2). If the bet slip does not update when the user changes their selection, they could unknowingly place a bet on the wrong match or outcome — a trust and compliance issue. Additionally, Section 2.2 defines "Remove All" and per-selection remove (x) controls that must function correctly to allow users to clear their selections.

**Steps**:
1. Click "1" (Home) odds for the first match
2. Verify bet slip shows the first match with home selection and correct odds (Ref: Section 2.2 — "Shows one active selection at a time")
3. Click "X" (Draw) odds for a different match
4. Verify bet slip now shows the new match with draw selection and updated odds (Ref: Section 2.1 — "Clicking new odds replaces previous selection")
5. Verify the previous selection is no longer highlighted in the match list
6. Enter a stake and verify potential payout recalculates based on the new odds
7. Click per-selection remove (x) button — verify bet slip clears the selection (Ref: Section 2.2 — "per-selection remove (x)")
8. Select a new match odds, then click "Remove All" — verify bet slip is cleared entirely (Ref: Section 2.2 — "Remove All")

**Expected Result**: Bet slip always reflects the most recently selected match/outcome. Only one selection can be active at a time. Odds and payout update immediately upon selection change. Per-selection remove (x) and "Remove All" buttons clear the bet slip as expected.

---

### TC-05: Payout Calculation Accuracy Across Different Stakes

**Priority**: High

**Risk Rationale**: Payout = stake × odds is the fundamental betting formula (Ref: Domain Context — "Payout: calculated as stake × odds"). Incorrect calculations — even by a cent — undermine user trust and could result in financial discrepancies at scale. The receipt must be consistent with pre-placement values (Ref: Section 2.4).

**Steps**:
1. Select a match with known odds (e.g., Manchester Utd Home = 2.45)
2. Enter stake €1.00 → verify payout shows €2.45
3. Enter stake €10.00 → verify payout shows €24.50
4. Enter stake €50.00 → verify payout shows €122.50
5. Enter stake €99.99 → verify payout shows €244.98
6. Select a different match with different odds and repeat with stake €5.00
7. After placing a bet, verify receipt payout matches the pre-placement payout (Ref: Section 2.4 — receipt must show "Potential payout")

**Expected Result**: Displayed payout always equals stake × odds, rounded to 2 decimal places. Payout in the receipt modal matches the payout shown in the bet slip before placement.

---

### TC-06: Post-Bet Balance Consistency Between UI and API

**Priority**: Critical

**Risk Rationale**: Balance is a financial value shared across the header and the bet slip (Ref: Domain Context — "The balance is shared across the header and the bet slip"). The API balance (GET /api/balance) must stay in sync with the UI after each bet. If these go out of sync, users may see incorrect available funds — leading to failed bets, confusion, or potential exploitation.

**Steps**:
1. Note initial balance via API (`GET /api/balance`, Ref: Section 5.3) — expect €125.50
2. Verify UI header balance matches API balance (Ref: Domain Context — "The balance is shared across the header and the bet slip")
3. Verify bet slip also displays the same available balance (Ref: Section 2.2 — "Shows entered stake, available balance, and computed potential payout")
4. Place a bet with stake €10.00 via UI
5. After receipt modal closes (Ref: Section 2.3 — "stake is deducted"), verify header balance updates to €115.50 **without page refresh**
6. Verify bet slip balance also shows €115.50
7. Call `GET /api/balance` — verify API returns €115.50
8. Place another bet with stake €5.00
9. Verify header balance shows €110.50 without page refresh
10. Verify API balance returns €110.50

**Expected Result**: After each bet placement, the balance in the UI header, bet slip, and API response are all consistent and correctly reduced by the stake amount. Balance must update in the UI immediately after bet placement without requiring a page refresh.
