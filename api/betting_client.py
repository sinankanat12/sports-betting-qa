import requests

from config.settings import API_BASE_URL, USER_ID


class BettingClient:
    def __init__(self, base_url=API_BASE_URL, user_id=USER_ID):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "x-user-id": user_id,
            "Content-Type": "application/json",
        })

    def get_matches(self):
        return self.session.get(f"{self.base_url}/matches")

    def get_balance(self):
        return self.session.get(f"{self.base_url}/balance")

    def place_bet(self, match_id, selection, stake):
        payload = {"matchId": match_id, "selection": selection, "stake": stake}
        return self.session.post(f"{self.base_url}/place-bet", json=payload)

    def place_bet_raw(self, payload):
        """Send arbitrary payload to place-bet endpoint for negative testing."""
        return self.session.post(f"{self.base_url}/place-bet", json=payload)

    def reset_balance(self):
        return self.session.post(f"{self.base_url}/reset-balance")
