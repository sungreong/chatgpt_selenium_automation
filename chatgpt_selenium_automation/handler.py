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
import psutil
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options


class ChatGPTAutomation:

    def __init__(self, chrome_path, chrome_driver_path, url=r"https://chat.openai.com", use_temporary_chat=False):
        self.chrome_path = chrome_path
        self.chrome_driver_path = chrome_driver_path
        self.url = url

        print("기존 Chrome 인스턴스 종료 중...")
        self.close_existing_chrome_instances()
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"시도 {attempt + 1}/{max_retries}: Chrome 초기화 중...")
                free_port = self.find_available_port()
                print(f"포트 {free_port}에서 원격 디버깅으로 Chrome 실행 중...")
                self.launch_chrome_with_remote_debugging(free_port, self.url, headless=False)
                print("브라우저가 열릴 때까지 대기 중...")
                time.sleep(5)  # 브라우저가 완전히 열릴 때까지 대기

                print("브라우저에 연결 중...")
                self.driver = self.setup_webdriver(port=free_port)

                # 명시적 대기 추가
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                print("첫 번째 페이지 로드 중...")
                self.driver.get(self.url)
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                print("브라우저에 성공적으로 연결되었습니다.")
                self.cookie = self.get_cookie(max_retries=3)
                if self.cookie is None:
                    print("쿠키를 찾지 못했습니다. 로그인이 필요할 수 있습니다.")
                    self.close_existing_chrome_instances()
                    time.sleep(5)
                    continue

                break  # 성공적으로 초기화되면 루프 종료
            except WebDriverException as e:
                print(f"Chrome 초기화 중 오류 발생: {e}")
                if attempt == max_retries - 1:
                    raise Exception("Chrome 초기화에 실패했습니다. 최대 재시도 횟수를 초과했습니다.")
                else:
                    print("5초 후 재시도합니다...")
                    time.sleep(5)

        if use_temporary_chat:
            new_url = self.url + "&temporary-chat=true"
            self.driver.get(new_url)
            time.sleep(1)

        print("브라우저에 성공적으로 연결되었습니다.")
        self.cookie = self.get_cookie()

        if self.cookie:
            print("쿠키를 성공적으로 찾았습니다.")
        else:
            print("경고: 쿠키를 찾지 못했습니다. 로그인이 필요할 수 있습니다.")

    def close_existing_chrome_instances(self):
        for proc in psutil.process_iter(["name", "cmdline"]):
            try:
                if proc.info["name"] == "chrome.exe":
                    cmdline = proc.cmdline()
                    # Selenium으로 실행된 Chrome 인스턴스 확인
                    if any("--remote-debugging-port" in arg for arg in cmdline):
                        print(f"Selenium Chrome 인스턴스 종료 중: PID {proc.pid}")
                        for child in proc.children(recursive=True):
                            child.terminate()
                        proc.terminate()
                        proc.wait(timeout=5)  # 프로세스가 종료될 때까지 최대 5초 대기
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        time.sleep(2)  # 프로세스 종료를 위한 추가 대기 시간
        print("Selenium Chrome 인스턴스 종료 완료")

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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")

        service = ChromeService(ChromeDriverManager().install())

        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver

    def get_cookie(self, max_retries=30, retry_interval=2):
        """
        ChatGPT 웹사이트에서 필요한 쿠키를 가져옵니다.
        최대 max_retries * retry_interval 초 동안 재시도합니다.
        """
        for _ in range(max_retries):
            cookies = self.driver.get_cookies()
            auth_cookie = next(
                (
                    cookie
                    for cookie in cookies
                    if cookie["name"].startswith("__Secure") and "session" in cookie["name"]
                ),
                None,
            )

            if auth_cookie:
                print(f"인증 쿠키를 찾았습니다: {auth_cookie['name']}")
                return auth_cookie["value"]

            print("인증 쿠키를 찾지 못했습니다. 다시 시도합니다...")
            time.sleep(retry_interval)

        print("경고: 인증 쿠키를 찾지 못했습니다. 로그인이 필요할 수 있습니다.")
        return None

    def wait_for_page_load(self, timeout=30):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("페이지 로딩 완료")
        except TimeoutException:
            print("페이지 로딩 시간 초과")

    def upload_file(self, file_path):
        """특정 파일을 업로드하는 메서드"""
        print("파일 업로드 중...")
        try:

            # 파일 업로드 버튼 찾기
            # upload_button = WebDriverWait(self.driver, 20).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, "button[aria-label='파일 첨부']"))
            # )

            # 파일 경로가 유효한지 확인
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
            print("파일 경로 확인 완료")

            # 파일 입력 요소 찾기 (일반적으로 숨겨져 있음)
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            print("파일 입력 요소 찾기 완료")

            # JavaScript를 사용하여 파일 입력 요소를 표시
            self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
            print("파일 입력 요소 표시 완료")
            # 파일 경로 전송
            file_input.send_keys(file_path)
            print("파일 경로 전송 완료")
            # 파일 업로드 완료를 기다림 (필요에 따라 조정)
            # WebDriverWait(self.driver, 10).until(
            #     EC.presence_of_element_located(
            #         (By.XPATH, "//div[contains(text(), '업로드 완료') or contains(text(), 'Upload complete')]")
            #     )
            # )
            time.sleep(3)
            existing_file_divs = WebDriverWait(self.driver, 5).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div[class*='group relative inline-block text-sm text-token-text-primary']")
                )
            )
            print("=" * 20)
            print(existing_file_divs)
            print("=" * 20)
            for div in existing_file_divs[:-1]:
                try:
                    remove_button = div.find_element(
                        By.CSS_SELECTOR,
                        "button.absolute.right-1.top-1.-translate-y-1\\/2.translate-x-1\\/2.rounded-full.border.border-token-border-heavy.bg-token-main-surface-secondary.p-0\\.5.text-token-text-primary.transition-colors.hover\\:opacity-100.group-hover\\:opacity-100.md\\:opacity-0",
                    )
                    remove_button.click()
                    print("기존 파일 제거 완료")
                    time.sleep(0.5)  # 각 파일 제거 후 잠시 대기
                except Exception as e:
                    print(f"파일 제거 중 오류 발생: {e}")
            if existing_file_divs:
                time.sleep(1)  # 모든 파일 제거 후 추가로 대기
            else:
                print("제거할 기존 파일이 없습니다.")
            # print("=" * 20)
            # print(existing_file_divs)
            # print("=" * 20)
            print(f"파일 업로드 완료: {file_path}")

        except Exception as e:
            print(f"파일 업로드 중 오류 발생: {e}")
            print(f"오류 타입: {type(e)}")
            print(f"오류 발생 위치: {e.__traceback__.tb_lineno}")
            self.driver.save_screenshot("file_upload_error.png")
        finally:
            # 파일 입력 요소를 다시 숨김
            self.driver.execute_script("arguments[0].style.display = 'none';", file_input)

    def send_prompt_to_chatgpt(self, prompt):
        """Sends a message to ChatGPT and waits for the response"""
        try:
            print(f"메시지 전송: {prompt}")
            # 새로운 입력 영역 찾기
            input_box = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.ID, "prompt-textarea"))
            )

            # 입력 영역이 상호작용 가능한 상태가 될 때까지 대기
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "prompt-textarea")))
            # JavaScript를 사용하여 텍스트 입력
            self.driver.execute_script(
                """
                var element = arguments[0];
                element.innerHTML = arguments[1];
                var event = new Event('input', { bubbles: true });
                element.dispatchEvent(event);
            """,
                input_box,
                f"<p>{prompt}</p>",
            )

            # 전송 버튼 찾기 및 클릭
            send_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='send-button']"))
            )

            # JavaScript를 사용하여 버튼 클릭
            try:
                self.driver.execute_script("arguments[0].click();", send_button)
            except ElementClickInterceptedException:
                print("버튼 클릭이 차단되었습니다. 다른 방법을 시도합니다.")
                # 다른 클릭 방법 시도
                self.driver.execute_script(
                    """
                    var event = new MouseEvent('click', {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    arguments[0].dispatchEvent(event);
                """,
                    send_button,
                )

            self.check_response_ended()
        except TimeoutException:
            print("시간 초과: 요소를 찾을 수 없거나 클릭할 수 없습니다.")
            self.driver.save_screenshot("timeout_error.png")
        except Exception as e:
            print(f"메시지 전송 중 오류 발생: {e}")
            self.driver.save_screenshot("error_screenshot.png")

    def check_response_ended(self):
        start_time = time.time()
        timeout = 60  # 최대 60초 동안 대기

        send_button_selector = 'button[data-testid="send-button"]'

        time.sleep(3)  # 3초 대기 후 체크 시작

        while True:
            try:
                # send 버튼 확인
                send_button = self.driver.find_element(By.CSS_SELECTOR, send_button_selector)

                if send_button.get_attribute("disabled") is None:
                    print("Send button is enabled. Response has ended.")
                else:
                    print("Send button is disabled. Waiting for response to complete.")
                    break

            except Exception as e:
                print(f"버튼을 찾는 중 오류 발생: {e}")

            # 타임아웃 체크
            if time.time() - start_time > timeout:
                print("응답 확인 시간 초과.")
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

    # def return_last_response(self):
    #     """:return: the text of the last chatgpt response"""

    #     response_elements = self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text-base")
    #     return response_elements[-1].text

    def return_last_response(self):
        """마지막 ChatGPT 응답의 텍스트를 반환합니다."""
        try:
            # 여러 가지 선택자를 시도합니다.
            selectors = ["div.text-base", "div[data-message-author-role='assistant']", "div.markdown", "div.prose"]

            for selector in selectors:
                response_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if response_elements:
                    return response_elements[-1].text

            # 모든 선택자가 실패하면 페이지 소스를 확인합니다.
            print("Warning: 응답 요소를 찾을 수 없습니다. 페이지 소스를 확인합니다.")
            self.driver.save_screenshot("page_source_error.png")
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)

            return "응답을 찾을 수 없습니다. 페이지 소스를 확인하세요."
        except Exception as e:
            print(f"응답을 가져오는 중 오류 발생: {e}")
            return f"오류: {e}"

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
                time.sleep(10)
                break
            elif user_input == "n":
                print("Waiting for you to complete the human verification...")
                time.sleep(5)  # You can adjust the waiting time as needed
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def quit(self):
        """브라우저를 닫고 WebDriver 세션을 종료합니다."""
        print("브라우저를 종료하는 중...")
        try:
            # 모든 창을 닫습니다
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                self.driver.close()

            # WebDriver 세션을 종료합니다
            self.driver.quit()
            print("브라우저가 성공적으로 종료되었습니다.")
        except Exception as e:
            print(f"브라우저 종료 중 오류 발생: {e}")
        finally:
            # Chrome 프로세스를 강제 종료합니다 (Windows 기준)
            try:
                os.system("taskkill /f /im chrome.exe")
                print("Chrome 프로세스를 강제 종료했습니다.")
            except Exception as e:
                print(f"Chrome 프로세스 강제 종료 중 오류 발생: {e}")
