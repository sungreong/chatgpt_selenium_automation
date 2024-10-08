from chatgpt_selenium_automation.handler import ChatGPTAutomation
from chatgpt_selenium_automation.utils import get_url_info
from dotenv import load_dotenv
import os, sys

# Define the path where the chrome driver is installed on your computer
# chrome_driver_path = r"C:\Users\<user>\Downloads\chromedriver-win64\chromedriver.exe"
chrome_driver_path = r"C:\Users\leesu\Downloads\chromedriver-win64\chromedriver.exe"

# the sintax r'"..."' is required because the space in "Program Files" in the chrome path
chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
url, use_temporary_chat = get_url_info()
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, url=url, use_temporary_chat=use_temporary_chat)

# Define a prompt and send it to chatgpt
print("Sending prompt to ChatGPT...")
for prompt in ["안녕하세요!", "오늘 날씨가 어때요?", "무엇을 도와드릴까요?"]:
    # 파일 업로드
    chatgpt.send_prompt_to_chatgpt(prompt)
    # Retrieve the last response from ChatGPT
    response = chatgpt.return_last_response()
    print(response)

# Save the conversation to a text file
file_name = "conversation.json"
chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
if input("Do you want to close the browser? (y/n): ").lower() == "y":
    chatgpt.quit()
