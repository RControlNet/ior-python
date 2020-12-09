import time
import sys

from selenium import webdriver

class VideoTransmitter:
    def __init__(self, uniqueIdentifier, driver, server="https://localhost:8001/#/"):
        self.identifier = uniqueIdentifier
        self.server = server
        self.driver = driver

    def openBrowserAndHitLink(self):
        self.driver.get(self.server + self.identifier)
        print(self.driver.title)
        if(self.driver.title == "Privacy error"):
            print("Privacy Error")
            self.driver.find_element_by_id('details-button').click()
            self.driver.find_element_by_id('proceed-link').click()

    def close(self):
        self.driver.quit()

def createVideoTransmitter(identifier):
    return VideoTransmitter(identifier, webdriver.Edge("C:\\Users\\Asus\\git\\ior-python\\ior_research\\utils\\drivers\\msedgedriver.exe"))

if __name__ == "__main__":
    transmitter = createVideoTransmitter("hello")
    transmitter.openBrowserAndHitLink()
    input()
    transmitter.close()