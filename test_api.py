from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from chatgpt_selenium_automation.handler import ChatGPTAutomation
from chatgpt_selenium_automation.utils import get_url_info
from dotenv import load_dotenv
import os, sys, json
from typing import List

app = FastAPI()

# ChatGPT 자동화 설정
chrome_driver_path = r"C:\Users\leesu\Downloads\chromedriver-win64\chromedriver.exe"
chrome_path = r'"C:\Program Files\Google\Chrome\Application\chrome.exe"'
url, use_temporary_chat = get_url_info()
chatgpt = ChatGPTAutomation(chrome_path, chrome_driver_path, url=url, use_temporary_chat=False)


class BoxInfo(BaseModel):
    id: int
    x: float
    y: float
    bbox: List[float]
    text: str


class PageData(BaseModel):
    page_number: str
    box_infos: List[BoxInfo]


class BoxInfo(BaseModel):
    id: int
    x: float
    y: float
    bbox: List[float]
    text: str


class PageData(BaseModel):
    page_number: str
    box_infos: List[BoxInfo]


@app.post("/process_document")
async def process_document(image: UploadFile = File(...), page_data: str = Form(...)):
    # JSON 문자열을 파싱
    page_data_dict = json.loads(page_data)
    page_number = page_data_dict["page_number"]
    box_infos = [BoxInfo(**box) for box in page_data_dict["box_infos"]]

    # 이미지 저장
    image_path = f"./doc_parsing/image{page_number}.png"
    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())

    # ChatGPT에 이미지 업로드
    chatgpt.upload_file(os.path.abspath(image_path))

    # BoxInfo 데이터 전송
    box_infos_str = str([box.dict() for box in box_infos])
    chatgpt.send_prompt_to_chatgpt(box_infos_str)

    # ChatGPT 응답 받기
    response = chatgpt.return_chatgpt_conversation()[-1]

    # 대화 저장
    chatgpt.save_conversation("conversation.json")

    return {"response": response}


@app.on_event("shutdown")
def shutdown_event():
    chatgpt.quit()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
