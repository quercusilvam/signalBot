import logging

import common
import config
import time

import sys

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class LibrusHandler:
    """Handle connection and actions with Librus Synergia"""
    _librus_username = None
    _librus_password = None

    _cookie_button_class_name = 'modal-button__primary'
    _librus_menu_text = 'LIBRUS Synergia'
    _librus_menu_login_text = 'Zaloguj'
    _librus_login_frame = 'caLoginIframe'
    _login_username_id = 'Login'
    _login_password_id = 'Pass'
    _login_button_id = 'LoginBtn'
    _logged_user_id = 'user-section'

    _messages_table_line_class_name = 'line0'
    _messages_unread_xpath = '//td[@style="font-weight: bold;"]//a'

    _wait_timeout = 5
    _wait_poll_frequency = .2

    driver = None

    def __init__(self, username, password):
        self._librus_username = username
        self._librus_password = password
        self.driver = common.init_webdriver()
        self._log_into_librus()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        common.destroy_webdriver(self.driver)

    def _log_into_librus(self):
        """Try to log into librusSynergia with given username/password"""
        try:
            expected_errors = [NoSuchElementException, StaleElementReferenceException]

            logging.info('LibrusHandler - Try to log into LibrusSynergia')
            self.driver.get(config.LIBRUS_LOGIN_PAGE)
            wait = WebDriverWait(
                self.driver,
                timeout=self._wait_timeout,
                poll_frequency=self._wait_poll_frequency,
                ignored_exceptions=expected_errors
            )

            wait.until(lambda d: self.driver.find_element(By.CLASS_NAME, self._cookie_button_class_name).click() or True)
            wait.until(lambda d: self.driver.find_element(By.LINK_TEXT, self._librus_menu_text).click() or True)
            wait.until(lambda d: self.driver.find_element(By.LINK_TEXT, self._librus_menu_login_text).click() or True)

            wait.until(lambda d: self.driver.switch_to.frame(self._librus_login_frame) or True)
            wait.until(
                lambda d:
                self.driver.find_element(By.ID, self._login_username_id).send_keys(self._librus_username) or True
            )
            wait.until(
                lambda d:
                self.driver.find_element(By.ID, self._login_password_id).send_keys(self._librus_password) or True
            )
            wait.until(lambda d: self.driver.find_element(By.ID, self._login_button_id).click() or True)

            wait.until(lambda d: self.driver.switch_to.default_content() or True)
            wait.until(lambda d: self.driver.find_element(By.ID, self._logged_user_id) or True)

        except TimeoutException as te:
            logging.error('LibrusHandler - Cannot login into librusSynergia! Check your credentials')
            raise RuntimeError(te)
        else:
            logging.info('LibrusHandler - Successfully logged into librusSynergia!')

    def get_new_message(self):
        """Return all unread messages as dict"""
        try:
            expected_errors = [NoSuchElementException, StaleElementReferenceException]

            logging.info('LibrusHandler - Get new messages from librusSynergia.')
            self.driver.get(config.LIBRUS_MESSAGES_PAGE)
            wait = WebDriverWait(
                self.driver,
                timeout=self._wait_timeout,
                poll_frequency=self._wait_poll_frequency,
                ignored_exceptions=expected_errors
            )
            wait.until(lambda d: self.driver.find_element(By.ID, self._logged_user_id) or True)

            wait.until(lambda d: self.driver.find_elements(By.CLASS_NAME, self._messages_table_line_class_name) or True)
            messages_text = self.driver.find_elements(By.XPATH, self._messages_unread_xpath)

            unread_messages = []
            # First item is sender, second message topic - so convert it to list of dicts (messages)
            for i in range(0, len(messages_text), 2):
                unread_messages.append({
                    'sender': messages_text[i].text,
                    'topic': messages_text[i+1].text}
                )
            return unread_messages

        except TimeoutException as te:
            logging.error('LibrusHandler - You are not logged. Cannot fetch messages')
            raise RuntimeError(te)
        except NoSuchElementException as te:
            logging.info('LibrusHandler - No new messages')
            return None
