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
print(url)
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, url=url, use_temporary_chat=False)

# Define a prompt and send it to chatgpt
print("Sending prompt to ChatGPT...")

import json

with open("./doc_parsing/page_all_openparse.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for page_number_str, page_node_data in data["pageBoxList"].items():
    if len(page_node_data) == 0:
        continue
    boxInfos = [
        dict(id=idx, x=boxinfo["x"], y=boxinfo["y"], bbox=boxinfo["bbox"], text=boxinfo["text"])
        for idx, boxinfo in enumerate(page_node_data)
    ]
    image_path = f"./doc_parsing/image{page_number_str}.png"
    chatgpt.upload_file(os.path.abspath(image_path))

    chatgpt.send_prompt_to_chatgpt(str(boxInfos))
    # Retrieve the last response from ChatGPT
    response = chatgpt.return_last_response()
    print(response)

# Save the conversation to a text file
file_name = "conversation.json"
chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
if input("Do you want to close the browser? (y/n): ").lower() == "y":
    chatgpt.quit()
