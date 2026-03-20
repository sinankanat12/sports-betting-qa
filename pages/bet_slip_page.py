from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class BetSlipPage(BasePage):
    # Bet slip locators
    BET_SLIP = (By.ID, "bet-slip")
    STAKE_INPUT = (By.ID, "bet-slip-stake-input")
    PLACE_BET_BUTTON = (By.ID, "bet-slip-place-bet")
    POTENTIAL_PAYOUT = (By.ID, "bet-slip-potential-payout")
    TOTAL_STAKE = (By.ID, "bet-slip-total-stake")
    REMOVE_ALL = (By.ID, "bet-slip-remove-all")
    BET_SLIP_BALANCE = (By.ID, "bet-slip-balance")

    # Success modal locators
    SUCCESS_MODAL = (By.ID, "modal-success")
    SUCCESS_BET_ID = (By.ID, "modal-success-bet-id")
    SUCCESS_MATCH = (By.ID, "modal-success-match")
    SUCCESS_STAKE = (By.ID, "modal-success-stake")
    SUCCESS_ODDS = (By.ID, "modal-success-odds")
    SUCCESS_PAYOUT = (By.ID, "modal-success-payout")
    SUCCESS_CLOSE = (By.ID, "modal-success-close")

    # Error modal locators
    ERROR_MODAL = (By.ID, "modal-error")
    ERROR_MESSAGE = (By.ID, "modal-error-message")
    ERROR_CLOSE = (By.ID, "modal-error-close")

    def enter_stake(self, amount):
        self.type_text(self.STAKE_INPUT, str(amount))

    def click_place_bet(self):
        self.click(self.PLACE_BET_BUTTON)

    def get_potential_payout(self):
        return self.get_text(self.POTENTIAL_PAYOUT)

    def get_balance_text(self):
        return self.get_text(self.BET_SLIP_BALANCE)

    def is_place_bet_enabled(self):
        btn = self.find(self.PLACE_BET_BUTTON)
        return btn.is_enabled() and "Disabled" not in btn.get_attribute("class")

    # Success modal
    def wait_for_success_modal(self):
        self.find(self.SUCCESS_MODAL)

    def get_receipt_bet_id(self):
        return self.get_text(self.SUCCESS_BET_ID)

    def get_receipt_match(self):
        return self.get_text(self.SUCCESS_MATCH)

    def get_receipt_stake(self):
        return self.get_text(self.SUCCESS_STAKE)

    def get_receipt_odds(self):
        return self.get_text(self.SUCCESS_ODDS)

    def get_receipt_payout(self):
        return self.get_text(self.SUCCESS_PAYOUT)

    def close_success_modal(self):
        self.click(self.SUCCESS_CLOSE)
