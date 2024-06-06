# -- coding: utf-8 --
import os
import socket
import threading
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json


class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path, url=r"https://chat.openai.com", use_temporary_chat=False):
        """
        This constructor automates the following steps:
        1. Open a Chrome browser with remote debugging enabled at a specified URL.
        2. Prompt the user to complete the log-in/registration/human verification, if required.
        3. Connect a Selenium WebDriver to the browser instance after human verification is completed.

        :param chrome_path: file path to chrome.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        :param chrome_driver_path: file path to chromedriver.exe (ex. C:\\Users\\User\\...\\chromedriver.exe)
        """

        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path

        # url = r"https://chat.openai.com"
        print("Launching Chrome with remote debugging...")
        free_port = self.find_available_port()
        print(f"Launching Chrome with remote debugging on port {free_port}...")
        self.launch_chrome_with_remote_debugging(free_port, url + "&temporary-chat=true", headless=False)
        print("Waiting for the browser to open...")
        self.wait_for_human_verification()
        print("Connecting to the browser...")
        self.driver = self.setup_webdriver(port=free_port)
        if use_temporary_chat:
            new_url = url + "&temporary-chat=true"
            before = self.driver.window_handles
            self.driver.get(new_url)
            after = self.driver.window_handles
            print(list(set(after).difference(set(before))))
            if len(list(set(after).difference(set(before)))) > 0:
                self.driver.switch_to.window(list(set(after).difference(set(before)))[0])
            time.sleep(1)

        print("Connected to the browser successfully.")
        self.cookie = self.get_cookie()

    @staticmethod
    def find_available_port():
        """This function finds and returns an available port number on the local machine by creating a temporary
        socket, binding it to an ephemeral port, and then closing the socket."""

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    def launch_chrome_with_remote_debugging(self, port, url, headless=False):
        """Launches a new Chrome instance with remote debugging enabled on the specified port and navigates to the
        provided url"""

        def open_chrome():
            # --user-data-dir=remote-profile
            # user_data_dir = "C:/Users/leesu/AppData/Local/Google/Chrome/User Data"
            # user_data_dir = os.path.join(os.getcwd(), "remote-profile")
            # if not os.path.exists(user_data_dir):
            #     os.makedirs(user_data_dir)
            # --user-data-dir="{user_data_dir}"
            chrome_cmd = f'"{self.chrome_path}" --remote-debugging-port={port} {url}'
            chrome_cmd += f" --headless --disable-gpu --no-sandbox --disable-dev-shm-usage" if headless else ""
            # --disable-gpu --no-sandbox --disable-dev-shm-usage {url}
            os.system(chrome_cmd)

        self.chrome_thread = threading.Thread(target=open_chrome)
        self.chrome_thread.start()

    def setup_webdriver(self, port):
        """Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
        with remote debugging enabled on the specified port"""

        chrome_options = chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")

        # ChromeDriverManager를 사용하여 ChromeDriver 설치 및 서비스 설정
        service = ChromeService(ChromeDriverManager().install())

        # WebDriver 객체 생성
        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    # def setup_webdriver(self, port):
    #     """Initializes a Selenium WebDriver instance, connected to an existing Chrome browser
    #     with remote debugging enabled on the specified port"""

    #     chrome_options = webdriver.ChromeOptions()
    #     # chrome_options.binary_location = self.chrome_driver_path
    #     # chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
    #     service = ChromeService(ChromeDriverManager().install())
    #     driver = webdriver.Chrome(service=service, options=chrome_options)

    #     # driver = webdriver.Chrome(options=chrome_options)
    #     return driver

    def get_cookie(self):
        """
        Get chat.openai.com cookie from the running chrome instance.
        """
        cookies = self.driver.get_cookies()
        cookie = [elem for elem in cookies if elem["name"] == "__Secure-next-auth.session-token"][0]["value"]
        return cookie

    def send_prompt_to_chatgpt(self, prompt):
        """Sends a message to ChatGPT and waits for 20 seconds for the response"""
        input_box = self.driver.find_element(by=By.XPATH, value='//textarea[contains(@id, "prompt-textarea")]')
        self.driver.execute_script(f"arguments[0].value = '{prompt}';", input_box)
        input_box.send_keys(Keys.RETURN)
        input_box.submit()
        self.check_response_ended()

    def check_response_ended(self):
        start_time = time.time()
        timeout = 60  # 최대 60초 동안 대기

        send_button_selector = 'button[data-testid="fruitjuice-send-button"] svg'
        stop_button_selector = 'button[data-testid="fruitjuice-stop-button"] svg'

        time.sleep(3)  # 3초 대기 후 체크 시작

        while True:
            try:
                # send 버튼 확인
                send_buttons = self.driver.find_elements(By.CSS_SELECTOR, send_button_selector)
                stop_buttons = self.driver.find_elements(By.CSS_SELECTOR, stop_button_selector)

                if stop_buttons:
                    print("Stop button is present. Waiting for send button.")
                elif send_buttons:
                    print("Send button is present. Response has ended.")

                    # 클립보드 내용 가져오기
                    time.sleep(0.5)  # 클립보드 업데이트 대기

                    # 클립보드 내용 출력
                    break
                else:
                    print("Neither stop nor send button is present. Checking again.")
                    break

            except Exception as e:
                print(f"An error occurred: {e}")

            # 타임아웃 체크
            if time.time() - start_time > timeout:
                print("Response check timed out.")
                break

            time.sleep(1)  # 1초 대기 후 다시 확인

        time.sleep(2)  # 응답이 끝난 후 잠시 대기

    def return_chatgpt_conversation(self):
        """
        :return: returns a list of items, even items are the submitted questions (prompts) and odd items are chatgpt response
        """
        messages = self.driver.find_elements(By.CSS_SELECTOR, "div[data-message-id]")

        conversation = []
        last_user_message = None
        last_assistant_message = None

        for message in messages:
            author_role = message.get_attribute("data-message-author-role")
            if author_role == "user" and message != last_user_message:
                conversation.append(("user", message.text))
                last_user_message = message
            elif author_role == "assistant" and message != last_assistant_message:
                conversation.append(("assistant", message.text))
                last_assistant_message = message
        return conversation

    def save_conversation(self, file_name):
        """
        It saves the full chatgpt conversation of the tab open in chrome into a text file, with the following format:
            prompt: ...
            response: ...
            delimiter
            prompt: ...
            response: ...

        :param file_name: name of the file where you want to save
        """

        directory_name = "conversations"
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        chatgpt_conversation = self.return_chatgpt_conversation()

        # 데이터 구조 생성
        conversation_list = []
        for i in range(0, len(chatgpt_conversation), 2):
            if i + 1 < len(chatgpt_conversation):  # Ensure pairs of user and assistant messages
                conversation_entry = {"user": chatgpt_conversation[i][1], "assistant": chatgpt_conversation[i + 1][1]}
                conversation_list.append(conversation_entry)

        # JSON 파일로 저장
        with open(os.path.join(directory_name, file_name), "w", encoding="utf-8") as file:
            json.dump(conversation_list, file, ensure_ascii=False, indent=4)

    def return_last_response(self):
        """:return: the text of the last chatgpt response"""

        response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text-base")
        return response_elements[-1].text

    @staticmethod
    def wait_for_human_verification():
        print("You need to manually complete the log-in or the human verification if required.")

        while True:
            user_input = (
                input("Enter 'y' if you have completed the log-in or the human verification, or 'n' to check again: ")
                .lower()
                .strip()
            )

            if user_input == "y":
                print("Continuing with the automation process...")
                break
            elif user_input == "n":
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def quit(self):
        """Closes the browser and terminates the WebDriver session."""
        print("Closing the browser...")
        # for handle in self.driver.window_handles:
        #     self.driver.switch_to.window(handle)
        self.driver.close()
        # self.driver.quit()
