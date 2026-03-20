"""
API Test - Stake Validation Business Rules

Tests that the API correctly validates stake amounts and selection parameters,
independent of the UI layer.

Selection rationale: Business rules must be enforced at the API level regardless
of the client. Even if the UI is bypassed (e.g., via cURL or a modified client),
invalid bets should be rejected. This is critical for financial integrity.
"""

import pytest


VALID_MATCH_ID = "premier-league-manutd-chelsea"
VALID_SELECTION = "HOME"


@pytest.mark.api
class TestAPIStakeValidation:

    def test_stake_below_minimum_rejected(self, api_client):
        """Stake below 1.00 should return 422 with invalid_stake_min error."""
        resp = api_client.place_bet(VALID_MATCH_ID, VALID_SELECTION, 0.99)
        assert resp.status_code == 422
        body = resp.json()
        assert body["error"] == "invalid_stake_min"

    def test_stake_above_maximum_rejected(self, api_client):
        """Stake above 100.00 should return 422 with invalid_stake_max error."""
        resp = api_client.place_bet(VALID_MATCH_ID, VALID_SELECTION, 100.01)
        assert resp.status_code == 422
        body = resp.json()
        assert body["error"] == "invalid_stake_max"

    def test_stake_invalid_precision_rejected(self, api_client):
        """Stake with more than 2 decimal places should return 422."""
        resp = api_client.place_bet(VALID_MATCH_ID, VALID_SELECTION, 1.999)
        assert resp.status_code == 422
        body = resp.json()
        assert body["error"] == "invalid_stake_precision"

    def test_invalid_selection_rejected(self, api_client):
        """Non-enum selection value should return 422."""
        resp = api_client.place_bet(VALID_MATCH_ID, "INVALID", 5.00)
        assert resp.status_code == 422
        body = resp.json()
        assert body["error"] == "invalid_selection"

    def test_missing_match_id_rejected(self, api_client):
        """Missing matchId should return 422."""
        resp = api_client.place_bet_raw({"selection": VALID_SELECTION, "stake": 5.00})
        assert resp.status_code == 422
        body = resp.json()
        assert body["error"] == "invalid_match_id"

    def test_invalid_match_id_rejected(self, api_client):
        """Non-existent matchId should return 422."""
        resp = api_client.place_bet("nonexistent-match-xyz", VALID_SELECTION, 5.00)
        assert resp.status_code == 422
        body = resp.json()
        assert body["error"] == "invalid_match"

    def test_valid_bet_accepted(self, api_client):
        """Valid bet should return 200 with bet confirmation."""
        resp = api_client.place_bet(VALID_MATCH_ID, VALID_SELECTION, 5.00)
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Bet placed successfully"
        assert body["matchId"] == VALID_MATCH_ID
        assert body["selection"] == VALID_SELECTION
        assert body["stake"] == 5.00
        assert body["odds"] == 2.45
        assert body["payout"] == round(5.00 * 2.45, 2)

    def test_stake_at_exact_minimum_accepted(self, api_client):
        """Stake at exactly 1.00 (minimum boundary) should be accepted."""
        resp = api_client.place_bet(VALID_MATCH_ID, VALID_SELECTION, 1.00)
        assert resp.status_code == 200

    def test_stake_at_exact_maximum_accepted(self, api_client):
        """Stake at exactly 100.00 (maximum boundary) should be accepted."""
        resp = api_client.place_bet(VALID_MATCH_ID, VALID_SELECTION, 100.00)
        assert resp.status_code == 200
