# chatgpt_selenium_automation

ChatGPT Automation is a Python project that aims to automate interactions with OpenAI's ChatGPT using Selenium WebDriver. Currently, it requires human interaction for log-in and human verification. It handles launching Chrome, connecting to ChatGPT, sending prompts, and retrieving responses. This tool can be useful for experimenting with ChatGPT or building similar web automation tools.


[Michelangelo27/chatgpt_selenium_automation Github](https://github.com/Michelangelo27/chatgpt_selenium_automation) 에 코드에서 일부 수정 작업 진행함.

- converation room 에서 이어서 작성하게 하기
- agent가 대화 생성 완료 체크하는 로직 수정하기
- 모델 선택해서 사용할 수 있게 하기 
- 임시 채팅방을 통해 기록 남기지 않고 대화하기
- extension으로 인해서 chrome 여러 tab이 존재할 때 모두 종료하는 로직 추가 (전부 다 꺼지는 오류로 수정)

## Prerequisites

1. Install the library: pip install [git+https://github.com/Michelangelo27/chatgpt_selenium_automation.git](https://github.com/sungreong/chatgpt_selenium_automation.git)
2. Download the appropriate version of `chromedriver.exe` and save it to a known location on your system.
3. chrome이 켜져있는 상태에서 하면 잘 안되는 이슈가 있어서 크롬창을 모두 끄고 해야 작동함.
4. 초기에 화면이 정상적으로 뜨고 나서 작업을 진행해야 하기 때문에 일부 대기 시간이 필요함.
5. [chrome driver 공식 링크](https://developer.chrome.com/docs/chromedriver/downloads) 에서 현재 자신이 사용하고 있는 chrome 버전과 동일한 버전으로 설치해야 함.

## Example Usage

.env file 
```
TEMPORARY_CHAT=false
# ROOM_ID= (특정 converation 에서 작업하고 싶은 경우)
MODEL=text-davinci-002-render-sha # (gpt3.5) 매일 바뀔 수 있을 것 같음
MODEL_LIST=text-davinci-002-render-sha,gpt-4o,gpt-4
```

```python
from chatgpt_selenium_automation.handler import ChatGPTAutomation
from chatgpt_selenium_automation.utils import get_url_info

# Define the path where the chrome driver is installed on your computer
chrome_driver_path = r"C:\Users\user\Desktop\chromedriver.exe"

# the sintax r'"..."' is required because the space in "Program Files" in the chrome path
chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'

url, use_temporary_chat = get_url_info()
# Create an instance
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path,url=url,use_temporary_chat=use_temporary_chat)

# Define a prompt and send it to chatgpt
prompt = "오늘 날씨 알려줘!"
chatgpt.send_prompt_to_chatgpt(prompt)

# Retrieve the last response from ChatGPT
response = chatgpt.return_last_response()
print(response)

# Save the conversation to a text file
file_name = "conversation.json"
chatgpt.save_conversation(file_name)

# Close the browser and terminate the WebDriver session
chatgpt.quit()
   ```
   
   
## Note 

After instantiating the ChatGPTAutomation class, chrome will open up to chatgpt page, it will require you to manually complete the register/ log-in / Human-verification. After that, you must tell the program to continue, in the console type 'y'. After Those steps, the program will be able to continue autonomously.

## Note on Changing Tabs or Conversations

Please be aware that changing tabs or switching to another conversation while the script is running might cause errors or lead to the methods being applied to unintended chats. For optimal results and to avoid unintended consequences, it is recommended to avoid to manually interact with the browser (after the log-in/human verification) while the automation script is running.

   
   
## Note on Errors and Warnings

While running the script, you may see some error messages or warnings in the console, such as:
- DevTools listening on ws://...
- INFO: Created TensorFlow Lite XNNPACK delegate for CPU.
- ERROR: Couldn't read tbsCertificate as SEQUENCE
- ERROR: Failed parsing Certificate
   

These messages are related to the underlying libraries or the browser, and you can safely ignore them if the script works as expected. If you encounter any issues with the script, please ensure that you have installed the correct dependencies and are using the correct ChromeDriver version compatible with your Chrome browser.

   
   

