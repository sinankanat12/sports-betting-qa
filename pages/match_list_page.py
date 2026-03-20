from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class MatchListPage(BasePage):
    # Locators
    MATCH_LIST = (By.ID, "match-list")
    MATCH_SECTION = (By.ID, "match-section")
    MATCH_LIST_LOADING = (By.ID, "match-list-loading")
    MATCH_CARDS = (By.CSS_SELECTOR, "#match-list > div")
    @staticmethod
    def odds_button(match_index, selection):
        """Get odds button locator for a match by index and selection (home/draw/away).

        Uses .oddsGrid class selector as the app does not provide test IDs for odds buttons.
        """
        selection_map = {"home": 1, "draw": 2, "away": 3}
        pos = selection_map[selection.lower()]
        return (
            By.CSS_SELECTOR,
            f"#match-list > div:nth-child({match_index}) .oddsGrid button:nth-child({pos})",
        )

    def wait_for_matches_loaded(self):
        self.find(self.MATCH_LIST)

    def get_match_count(self):
        return len(self.find_all(self.MATCH_CARDS))

    def select_odds(self, match_index, selection="home"):
        locator = self.odds_button(match_index, selection)
        self.click(locator)
