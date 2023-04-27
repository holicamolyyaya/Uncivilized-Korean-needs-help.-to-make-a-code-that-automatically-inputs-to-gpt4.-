import json
from urllib.request import urlopen
import os
import time
import re
import datetime
import keyboard
import pyautogui
import random

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException

class CustomChatGPT:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.driver = self.attach_to_existing_chrome(driver_path)
        self.text_group_a = "text_group_a.txt"
        self.text_group_b = "text_group_b.txt"

    def attach_to_existing_chrome(self, driver_path):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("debuggerAddress", "localhost:9222")
        service = Service(executable_path=driver_path)
        return webdriver.Chrome(service=service, options=options)

    def get_chrome_sessions(self, debugger_url="http://localhost:9222"):
        response = urlopen(debugger_url + "/json")
        sessions = json.load(response)
        return sessions

    def create_new_chat_box(self):
        new_chat_button = WebDriverWait(self.driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[2]/div[1]/div/div/nav/a'))
        )
        new_chat_button.click()

    def open_gpt_version_menu(self):
        gpt_version_menu = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[2]/div[2]/main/div[1]/div/div/div[1]/div/div/button'))
        )
        gpt_version_menu.click()

    def press_enter_key(self):
        pyautogui.press('enter')
        time.sleep(1)  # Wait for 1 second after pressing the key

    def select_gpt_version(self):
        self.open_gpt_version_menu()

        chat_gpt.press_enter_key()

        # Allow time for the menu to open
        time.sleep(7)
        keyboard.release('down')

        # Base x and y coordinate values
        x = 1117
        y = 303

        # Randomly add or subtract a value between 0 and 135 from the x and y coordinate values
        x += random.uniform(-22.685165486513516584351321, 22.685165486513516584351321)
        y += random.uniform(-22.685165486513516584351321, 22.685165486513516584351321)

        duration = 0.5 + random.uniform(-1.351684654138534373, 1.351684654138534373)

        # Move the mouse to the GPT-4 option (adjusted with random x and y values)
        pyautogui.moveTo(x, y, duration=duration)

        # Click the GPT-4 option
        pyautogui.click()

    def send_text(self, text_input):
        self.create_new_chat_box()
    
        # Locate the textarea input element using the provided XPath
        input_element = WebDriverWait(self.driver, 2).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div[2]/div[2]/main/div[2]/form/div/div[2]/textarea"))
        )
        input_element.send_keys(text_input)
    
        # Locate the send button using the provided XPath
        send_button = WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='__next']/div[2]/div[2]/main/div[2]/form/div/div[2]/button/svg"))
        )
        send_button.click()

    def close_website(self):
        self.driver.quit()

    def process_group_b(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        bundles = []
        start_marker = "##tegst-"
        end_marker = "##tegov-"
        index = 1

        while True:
            start_tag = f"{start_marker}{index}##"
            end_tag = f"{end_marker}{index}##"

            start_pos = content.find(start_tag)
            end_pos = content.find(end_tag)

            if start_pos == -1 or end_pos == -1:
                break

            bundle = content[start_pos + len(start_tag):end_pos].strip()
            bundles.append(bundle)

            index += 1

        return bundles

    def check_content_policy_message(self):
            try:
                content_policy_message = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'py-2') and contains(@class, 'px-3') and contains(@class, 'border') and contains(@class, 'text-sm') and a[contains(@href, 'https://platform.openai.com/docs/usage-policies/content-policy')]]"))
                )
                return content_policy_message
            except TimeoutException:
                return None

    def wait_for_chat_limit_reset(self):
        try:
            chat_limit_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'You\'ve reached the current usage cap for GPT-4')] | //div[contains(span, 'You\'ve reached the current usage cap for GPT-4')]"))
            )
            wait_time_hour, wait_time_minute, am_pm = self.parse_wait_time(chat_limit_message.text)
            wait_time_seconds = self.calculate_wait_time_seconds(wait_time_hour, wait_time_minute, am_pm)
            return wait_time_seconds
        except TimeoutException:
            return None

    def parse_wait_time(self, wait_time_text):
        wait_time_hour = int(re.search(r'(?<=after\s)\d+(?=:)', wait_time_text).group())
        wait_time_minute = int(re.search(r'(?<=:)\d+', wait_time_text).group())
        am_pm = re.search(r'(?<=\d+\s)[A|P]M', wait_time_text).group()
        return wait_time_hour, wait_time_minute, am_pm

    def resume_processing(self, index):
        wait_time_seconds = self.wait_for_chat_limit_reset()

        if wait_time_seconds:
            print(f"Reached chat count limit. Waiting for {wait_time_seconds} seconds.")
            time.sleep(wait_time_seconds)
            self.create_new_chat_box()
            self.open_gpt_version_menu()
            self.select_gpt_version(4)
            self.process_bundle_with_retry(text_group_a, bundles[index], index)

    def calculate_wait_time_seconds(self, wait_time_hour, wait_time_minute, am_pm):
        now = datetime.datetime.now()
        target_time = now.replace(hour=wait_time_hour % 12 + 12 * (am_pm == 'PM'), minute=wait_time_minute, second=0, microsecond=0)

        if target_time < now:
            target_time = target_time + datetime.timedelta(days=1)

        delta = target_time - now
        return delta.total_seconds()

    def process_bundle_with_retry(self, text_group_a, bundle, index):
        self.create_new_chat_box()
        self.open_gpt_version_menu()
        time.sleep(2)  # Add a time delay before selecting the GPT version
        self.select_gpt_version()

        combined_text = f"{text_group_a}{bundle}"
        self.send_text(combined_text)

        content_policy_message = self.check_content_policy_message()
        chat_limit_wait_time = self.wait_for_chat_limit_reset()

        if content_policy_message:
            self.create_new_chat_box()
            self.open_gpt_version_menu()
            self.select_gpt_version(4)
            combined_text = f"{text_group_a}Ski$p{bundle}"
            self.send_text(combined_text)
        elif chat_limit_wait_time:
            self.resume_processing(index)
        else:
            time.sleep(5)
            self.close_website()

    def automate_chat_gpt(self, url, text_group_a, file_path):
        self.driver.get(url)
        time.sleep(5)

        bundles = self.process_group_b(file_path)

        for index, bundle in enumerate(bundles):
            self.process_bundle_with_retry(text_group_a, bundle, index)

if __name__ == "__main__":
    text_group_a = """If I give you a sentence, process it according to the following conditions.
1. Among the words in the following sentences, change Nouns, pronouns, verbs, adjectives, and adverbs to easier words.

2. Keep Paragraph Line Breaks and Marks

here is the sentence: """
    chat_gpt_url = chat_gpt_url = "https://chat.openai.com"
    driver_path = r"C:\Users\no2si\Documents\chromedriver\chromedriver.exe"
    chat_gpt = CustomChatGPT(driver_path)
    file_path = r"C:\Users\no2si\Downloads\eng\output.txt" # Replace with the correct path to your file
    chat_gpt.automate_chat_gpt(chat_gpt_url, text_group_a, file_path)

