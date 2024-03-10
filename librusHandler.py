import logging

import common
import config

import os

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class LibrusHandler:
    """Handle connection and actions with Librus Synergia"""
    _librus_username = None
    _librus_password = None

    _error_screenshot_filename = os.path.abspath('./error.png')

    _cookie_button_class_name = 'modal-button__primary'
    _cookie_box_id = 'cookieBoxClose'

    _librus_menu_text = 'LIBRUS Synergia'
    _librus_menu_login_text = 'Zaloguj'
    _librus_login_frame = 'caLoginIframe'
    _login_username_id = 'Login'
    _login_password_id = 'Pass'
    _login_button_id = 'LoginBtn'
    _logged_user_id = 'user-section'

    _messages_table_line_class_name = 'line0'
    _messages_unread_xpath = '//td[@style="font-weight: bold;"]//a'
    _message_view_sender_xpath = '//html//body//div[3]//div[3]//form//div//div//table//tbody//tr//td[2]//table[2]//tbody//tr[1]//td[2]'
    _message_view_topic_xpath = '//html//body//div[3]//div[3]//form//div//div//table//tbody//tr//td[2]//table[2]//tbody//tr[2]//td[2]'
    _message_view_body_xpath ='//html//body//div[3]//div[3]//form//div//div//table//tbody//tr//td[2]/div'

    _schedule_form_name = 'formPrzegladajPlan'
    _schedule_next_week_xpath='//html//body//div[1]//div//div//div//form//table[1]//tbody//tr[1]//th//a[2]//img'
    _schedule_screenshot_filename = os.path.abspath('./schedule.png')

    _wait_timeout = 10
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

            common.simulate_human_delay()
            wait.until(lambda d: self.driver.find_element(By.CLASS_NAME, self._cookie_button_class_name).click() or True)
            common.simulate_human_delay()
            wait.until(lambda d: self.driver.find_element(By.LINK_TEXT, self._librus_menu_text).click() or True)
            common.simulate_human_delay()
            wait.until(lambda d: self.driver.find_element(By.LINK_TEXT, self._librus_menu_login_text).click() or True)

            wait.until(lambda d: self.driver.switch_to.frame(self._librus_login_frame) or True)
            common.simulate_human_delay()
            wait.until(
                lambda d:
                self.driver.find_element(By.ID, self._login_username_id).send_keys(self._librus_username) or True
            )
            common.simulate_human_delay()
            wait.until(
                lambda d:
                self.driver.find_element(By.ID, self._login_password_id).send_keys(self._librus_password) or True
            )
            common.simulate_human_delay()
            wait.until(lambda d: self.driver.find_element(By.ID, self._login_button_id).click() or True)

            wait.until(lambda d: self.driver.switch_to.default_content() or True)
            wait.until(lambda d: self.driver.find_element(By.ID, self._logged_user_id) or True)

        except TimeoutException as te:
            logging.error('LibrusHandler - Cannot login into librusSynergia! Check your credentials')
            self.driver.save_screenshot(self._error_screenshot_filename)
            raise RuntimeError(te)
        else:
            logging.info('LibrusHandler - Successfully logged into librusSynergia!')

    def get_unread_messages(self):
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
            common.simulate_human_delay()
            wait.until(lambda d: self.driver.find_element(By.ID, self._cookie_box_id).click() or True)

            wait.until(lambda d: self.driver.find_elements(By.CLASS_NAME, self._messages_table_line_class_name) or True)
            message_box = self.driver.find_element(By.XPATH, self._messages_unread_xpath)

            unread_messages = []
            try:
                while True:
                    unread_messages.append(self._get_message_data(message_box))
                    self.driver.get(config.LIBRUS_MESSAGES_PAGE)
                    common.simulate_human_delay()
                    wait.until(lambda d: self.driver.find_elements(By.CLASS_NAME, self._messages_table_line_class_name) or True)
                    message_box = self.driver.find_element(By.XPATH, self._messages_unread_xpath)
            except NoSuchElementException as te:
                # All messages were fetched
                return unread_messages

        except TimeoutException as te:
            logging.error('LibrusHandler - You are not logged. Cannot fetch messages')
            self.driver.save_screenshot(self._error_screenshot_filename)
            raise RuntimeError(te)
        except NoSuchElementException as te:
            logging.info('LibrusHandler - No new messages')
            return None

    def get_schedule(self, next_week=False):
        """Open schedule and return picture of it"""
        try:
            expected_errors = [NoSuchElementException, StaleElementReferenceException]

            logging.info('LibrusHandler - Get schedule from librusSynergia.')
            self.driver.get(config.LIBRUS_SCHEDULE_PAGE)
            common.simulate_human_delay()
            wait = WebDriverWait(
                self.driver,
                timeout=self._wait_timeout,
                poll_frequency=self._wait_poll_frequency,
                ignored_exceptions=expected_errors
            )
            if next_week:
                wait.until(lambda d: self.driver.find_element(By.XPATH, self._schedule_next_week_xpath).click() or True)
                common.simulate_human_delay()

            wait.until(lambda d: self.driver.find_element(By.NAME, self._schedule_form_name) or True)
            self.driver.save_screenshot(self._schedule_screenshot_filename)

            return self._schedule_screenshot_filename

        except TimeoutException as te:
            logging.error('LibrusHandler - You are not logged. Cannot fetch schedule')
            self.driver.save_screenshot(self._error_screenshot_filename)
            raise RuntimeError(te)

    def get_error_screenshot(self):
        return self._error_screenshot_filename

    def _get_message_data(self, message_box=None, url=None):
        """Open message, read it body and return as dict

            You can pass
            message_box (message Sender or Titel box from config.LIBRUS_MESSAGES_PAGE)
            url to window with message
        """
        try:
            expected_errors = [NoSuchElementException, StaleElementReferenceException]
            wait = WebDriverWait(
                self.driver,
                timeout=self._wait_timeout,
                poll_frequency=self._wait_poll_frequency,
                ignored_exceptions=expected_errors
            )

            if message_box is not None:
                logging.info(f'LibrusHandler - read message {message_box.text}')
                wait.until(lambda d: message_box.click() or True)
                common.simulate_human_delay()
            elif url is not None:
                logging.info(f'LibrusHandler - read message {url}')
                self.driver.get(url)
                common.simulate_human_delay()
            else:
                logging.error('LibrusHandler._get_message_data - message_box or url must be provided but were Nones')
                raise RuntimeError(
                    'LibrusHandler._get_message_data - message_box or url must be provided but were Nones')

            message_sender = wait.until(
                lambda d: self.driver.find_element(By.XPATH, self._message_view_sender_xpath).text or True
            )
            message_topic = wait.until(
                lambda d: self.driver.find_element(By.XPATH, self._message_view_topic_xpath).text or True
            )
            message_body = wait.until(
                lambda d: self.driver.find_element(By.XPATH, self._message_view_body_xpath).text or True
            )

            return {
                'sender': message_sender,
                'topic': message_topic,
                'body': message_body
            }

        except TimeoutException as te:
            logging.error('LibrusHandler - You are not logged. Cannot read message body')
            self.driver.save_screenshot(self._error_screenshot_filename)
            raise RuntimeError(te)
