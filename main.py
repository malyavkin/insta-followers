import logging
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

logger = logging.getLogger('eurotrip')
logger.setLevel(logging.INFO)
geckodriver_path = 'webdriver/geckodriver-osx'


class IGWebDriver(webdriver.Firefox):
    def __init__(self, login, password, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.login = login
        self.password = password

    def wait_for_elem(self, by, value, delay=20):
        my_elem = WebDriverWait(self, delay) \
            .until(ec.presence_of_element_located((by, value)))
        return my_elem

    def auth(self):
        login_url = 'https://www.instagram.com/accounts/login/'
        self.get(login_url)
        input_login_csss = 'div._t296e:nth-child(1) > div:nth-child(1) > input:nth-child(1)'
        input_passw_csss = 'div._t296e:nth-child(2) > div:nth-child(1) > input:nth-child(1)'
        button_login_csss = '._qv64e'
        input_login = self.wait_for_elem(By.CSS_SELECTOR, input_login_csss)
        input_passw = self.wait_for_elem(By.CSS_SELECTOR, input_passw_csss)
        button_login = self.wait_for_elem(By.CSS_SELECTOR, button_login_csss)
        input_login.send_keys(self.login)
        input_passw.send_keys(self.password)
        button_login.click()

        self.wait_for_elem(By.CSS_SELECTOR, 'html.logged-in')

    def get_user(self, username):
        profile_url = 'https://www.instagram.com/{}/'.format(username)
        self.get(profile_url)

    def scroll_popup(self, scrollable_container):

        def get_control_element():
            control_bottom = '._jfct1'
            return self.wait_for_elem(By.CSS_SELECTOR, control_bottom, delay=5)

        def get_children():
            return scrollable_container.find_elements_by_css_selector('li')

        last_height = scrollable_container.size['height']

        SCROLL_PAUSE_TIME = 1
        while True:

            # print('height: {}, children: {}'.format(last_height,
            #                                        len(get_children())))
            # Scroll down to bottom
            last_child = get_children()[-1]
            last_child.send_keys(Keys.NULL)
            last_child.send_keys(Keys.END)

            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = scrollable_container.size['height']
            try:
                get_control_element()
            except:

                # print('{} children'.format(len(get_children())))
                return get_children()
            last_height = new_height


def get_name_from_li(li):
    try:
        return li.find_elements(By.CSS_SELECTOR, 'a[href]')[1].text
    except IndexError:
        print('(cant find name in li)')


def main():
    login, password = os.environ['creds'].split(':')
    username = 'lekaitow'
    driver = IGWebDriver(login, password, executable_path=geckodriver_path)
    driver.auth()
    driver.get_user(username)

    followers_csss = '[href="/{}/followers/"]'.format(username)

    followers_link = driver.wait_for_elem(By.CSS_SELECTOR, followers_csss)
    followers_link.click()

    followers_list = driver.wait_for_elem(By.CSS_SELECTOR, '._8q670')
    children = driver.scroll_popup(followers_list)
    followers_names = list(map(get_name_from_li, children))

    driver.get_user(username)

    # ==== following
    following_csss = '[href="/{}/following/"]'.format(username)
    following_link = driver.wait_for_elem(By.CSS_SELECTOR, following_csss)
    following_link.click()
    following_list = driver.wait_for_elem(By.CSS_SELECTOR, '._8q670')
    children = driver.scroll_popup(following_list)
    following_names = list(map(get_name_from_li, children))

    # те кто фолловят не взаимно
    followers_not_following = [name for name in followers_names if name not in following_names]
    following_not_followers = [name for name in following_names if name not in followers_names]
    print("Кто фолловит не взаимно")
    print(followers_not_following)

    print("Кого фолловишь не взаимно")
    print(following_not_followers)


if __name__ == '__main__':
    main()
