import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class VideoTransmitter:
    """
    Class responsible for managing the Browser and Video Stream, from client side
    """
    def __init__(self, driver, server):
        """
        :param server: Chrome WebDriver Object
        """
        self.credentials = None
        self.server = server
        self.driver = driver
        
    def setCredentials(self,credentials):
        self.credentials = credentials

    def checkBrowserAlive(self):
        try:
            self.driver.current_url
            return True
        except:
            return False

    def openBrowserAndHitLink(self):
        self.driver.get(self.server)
        if(self.driver.title == "Privacy error"):
            self.driver.find_element_by_id('details-button').click()
            self.driver.find_element_by_id('proceed-link').click()
        self.driver.find_element_by_name('username').send_keys(self.credentials.username)
        self.driver.find_element_by_name('password').send_keys(self.credentials.password)
        self.driver.find_element_by_id('submit').click()

    def close(self):
        self.driver.quit()

def createVideoTransmitter(audio=True, video=True, serverPath=None):
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

    return VideoTransmitter(driver,server=serverPath)

if __name__ == "__main__":
    os.environ['RCONTROLNET'] = "../../config/iorConfigs.config"

    transmitter = createVideoTransmitter()
    transmitter.openBrowserAndHitLink()
    input()
    transmitter.close()