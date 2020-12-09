import time
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class VideoTransmitter:
    def __init__(self, uniqueIdentifier, driver, server="https://192.168.0.131:8003/#/"):
        self.identifier = uniqueIdentifier
        self.server = server
        self.driver = driver

    def openBrowserAndHitLink(self):
        
        self.driver.get("https://192.168.0.131:8080/")
        print(self.driver.title)
        if(self.driver.title == "Privacy error"):
            print("Privacy Error")
            self.driver.find_element_by_id('details-button').click()
            self.driver.find_element_by_id('proceed-link').click()

        self.driver.get(self.server)
        print(self.driver.title)
        if(self.driver.title == "Privacy error"):
            print("Privacy Error")
            self.driver.find_element_by_id('details-button').click()
            self.driver.find_element_by_id('proceed-link').click()
        self.driver.find_element_by_name('username').send_keys("mayank31313@gmail.com")
        self.driver.find_element_by_name('password').send_keys("12345678")
        self.driver.find_element_by_id('submit').click()

    def close(self):
        self.driver.quit()

def createVideoTransmitter(identifier):
    options = Options()
    options.add_experimental_option("prefs", { \
        "profile.default_content_setting_values.media_stream_mic": 1,     # 1:allow, 2:block 
        "profile.default_content_setting_values.media_stream_camera": 1,  # 1:allow, 2:block
    })
    return VideoTransmitter(identifier, webdriver.Chrome(chrome_options=options))

if __name__ == "__main__":
    transmitter = createVideoTransmitter("hello")
    transmitter.openBrowserAndHitLink()
    input()
    transmitter.close()