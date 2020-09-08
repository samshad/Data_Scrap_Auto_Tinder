from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from Auth.auth import password, email
from bs4 import BeautifulSoup
import csv
import random


class AutoTinder:
    """Initializing Class"""
    def __init__(self):
        self.email = email
        self.password = password
        self.cur_data = dict()

        # Configuring the browser
        webdriver_path = 'chromedriver_win32/chromedriver.exe'
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        # chrome_options.add_argument("start-maximized")  # For full screen browser window
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-notifications")

        # Pass the argument 1 to allow and 2 to block
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        self.driver = webdriver.Chrome(webdriver_path, options=chrome_options)

    """Log in to Tinder with facebook account"""
    def login(self):
        self.driver.get('https://tinder.com')

        cookies_accept_btn = self.driver.find_element_by_xpath(
            '//*[@id="content"]/div/div[2]/div/div/div[1]/button/span')
        cookies_accept_btn.click()

        delay = 5
        try:
            fb_btn = WebDriverWait(self.driver, delay).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="modal-manager"]/div/div/div[1]/div/div[3]/span/div[2]/button')))
            fb_btn.click()

            sleep(3)
            base_window = self.driver.window_handles[0]
            self.driver.switch_to.window(self.driver.window_handles[1])

            email_input = self.driver.find_element_by_xpath('//*[@id="email"]')
            email_input.send_keys(self.email)

            password_input = self.driver.find_element_by_xpath('//*[@id="pass"]')
            password_input.send_keys(self.password)

            login_btn = self.driver.find_element_by_xpath('//*[@id="u_0_0"]')
            login_btn.click()

            self.driver.switch_to.window(base_window)

            try:
                location_allow = WebDriverWait(self.driver, delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')))
                location_allow.click()
            except TimeoutException:
                print("Location allow button Loading took too much time!")

            try:
                notification_allow = WebDriverWait(self.driver, delay).until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//*[@id="modal-manager"]/div/div/div/div/div[3]/button[1]')))
                notification_allow.click()
            except TimeoutException:
                print("Notification button Loading took too much time!")

            print("Login done successfully!!!")

        except TimeoutException:
            print("Facebook login button Loading took too much time!")

    """Like someone's profile"""
    def like(self):
        try:
            like_btn = self.driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/div[4]/button')
            like_btn.click()
            return
        except:
            pass

        try:
            like_btn = self.driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div[2]/div/div/div[4]/button')
            like_btn.click()
        except:
            pass

    """Dislike someone's profile"""
    def dislike(self):
        try:
            dislike_btn = self.driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[2]/div[2]/button')
            dislike_btn.click()
            return
        except:
            pass

        try:
            dislike_btn = self.driver.find_element_by_xpath(
                '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div[2]/div/div/div[2]/button')
            dislike_btn.click()
        except:
            pass

    """Refresh the current web page"""
    def reload(self):
        self.driver.refresh()

    """Collect data from the profile"""
    def get_data(self):
        try:
            expand_btn = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div/div[1]/div[3]/div[6]/button')
                    ))
            expand_btn.click()
            sleep(2)

            # get html of the page for parsing data
            html = BeautifulSoup(self.driver.page_source)

            name = html.find('h1', {"class": 'Fz($xl) Fw($bold) Fxs(1) Flw(w) Pend(8px) M(0) D(i)'}).text
            age = html.find('span', {"class": 'Whs(nw) Fz($l)'}).text
            bio = ''

            try:
                bio = self.driver.find_element_by_xpath(
                    '//*[@id="content"]/div/div[1]/div/main/div[1]/div/div/div[1]/div[1]/div/div[2]/div[2]/div').text
            except:
                pass

            tags = html.findAll('div', {"class": 'Bdrs(100px)'})
            extras = html.findAll('div', {"class": 'Us(t) Va(m) D(ib) My(2px) NetWidth(100%,20px) C($c-secondary)'})

            lives_in = html.find('div', {"class": 'Us(t) Va(m) D(ib) My(2px) NetWidth(100%,20px) C($c-secondary) Ell'})
            if lives_in:
                lives_in = lives_in.text
            else:
                lives_in = ''
            lives_in = ''.join([x.strip() for x in lives_in.split('Lives in')])

            if len(tags) > 0:
                print("\nTags:")
                print(', '.join([tag.text for tag in tags]))

            print("\nExtra length: ", len(extras))
            for extra in extras:
                print(extra.text)

            self.cur_data['name'] = name
            self.cur_data['age'] = age
            self.cur_data['lives_in'] = lives_in
            self.cur_data['bio'] = bio
            self.cur_data['tags'] = ', '.join([tag.text for tag in tags])
            self.cur_data['extras'] = ', '.join([extra.text for extra in extras])

            self.write_csv()

            distance = ''
            gender = ''
            for extra in extras:
                tmp = extra.text.split(' ')
                if len(tmp) > 1 and tmp[1] == 'kilometers':
                    distance = tmp[0]
                for t in tmp:
                    if t.lower() == 'man' or t.lower() == 'woman':
                        gender = t.lower()

            self.cur_data['distance'] = int(distance)
            self.cur_data['gender'] = gender

            print('Name: ', name.strip(), '\n', 'Age: ', age.strip(), '\n', 'Bio: ', bio.strip(),
                  '\nLives in: ', lives_in, '\nDistance: ', distance, '\nGender: ', gender)

        except TimeoutException:
            print("Name, Age Loading took too much time!")

    """Append collected data to csv file"""
    def write_csv(self):
        d = [self.cur_data['name'], self.cur_data['age'], self.cur_data['lives_in'], self.cur_data['bio']
             , self.cur_data['tags'], self.cur_data['extras']]
        with open('data.csv', 'a', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(d)

    """Automate the scraping for specific iteration"""
    def scrap(self, count):
        for i in range(count):
            self.get_data()
            self.write_csv()
            # self.dislike()  # Use dislike for avoiding repetition of profiles
            self.reload()

    """Run Tinder Auto bot for specified intervals"""
    def auto_tinder(self, count):
        for _ in range(count):
            sleep(3)
            try:
                self.get_data()
                self.write_csv()
                self.get_auto_decision()
            except:
                self.reload()

    """Take personal decision whether like or dislike"""
    def get_auto_decision(self):
        if self.cur_data['distance'] < 500:
            if self.cur_data['gender'] == 'man':
                self.dislike()
            else:
                if len(self.cur_data['bio']) < 1 and len(self.cur_data['tags']) < 1 and len(
                        self.cur_data['extras']) < 20:
                    luck = int(random.random() * 100)
                    if luck <= 25:
                        self.dislike()
                    else:
                        self.like()
                else:
                    self.like()
        else:
            self.dislike()


"""if __name__ == '__main__':
    bot = AutoTinder()
    bot.login()"""

