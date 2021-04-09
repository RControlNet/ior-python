import time
import os
from ior_research.utils.consts import VIDEO_SERVER
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from ior_research.utils import loadConfig

class VideoTransmitter:
    def __init__(self, driver, server=None):
        if server is None:
            server = VIDEO_SERVER

        self.server = server
        self.driver = driver

    def checkBrowserAlive(self):
        try:
            print(self.driver.current_url)
            return True
        except:
            return False

    def openBrowserAndHitLink(self):
        data = loadConfig()
        username = data['username']
        password = data['password']
        self.driver.get(self.server)

        print(self.driver.title)
        if(self.driver.title == "Privacy error"):
            self.driver.find_element_by_id('details-button').click()
            self.driver.find_element_by_id('proceed-link').click()
        self.driver.find_element_by_name('username').send_keys(username)
        self.driver.find_element_by_name('password').send_keys(password)
        self.driver.find_element_by_id('submit').click()

    def close(self):
        self.driver.quit()

def createVideoTransmitter(audio=True, video=True):
    options = Options()
    prefs = {
        "profile.default_content_setting_values.media_stream_camera": 2,  # 1:allow, 2:block
        "profile.default_content_setting_values.media_stream_mic": 2
    }
    if audio:
        prefs["profile.default_content_setting_values.media_stream_mic"] = 1
    if video:
        prefs["profile.default_content_setting_values.media_stream_camera"] = 1

    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=options)

    return VideoTransmitter(driver)

if __name__ == "__main__":
    os.environ['RCONTROLNET'] = "../../config/iorConfigs.config"

    transmitter = createVideoTransmitter()
    transmitter.openBrowserAndHitLink()
    input()
    transmitter.close()