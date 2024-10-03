import json
import os
from fastapi.testclient import TestClient
from test_api import app

client = TestClient(app)


def test_process_document():
    # 샘플 데이터 로드
    with open("./doc_parsing/page_all_openparse.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 첫 번째 페이지 데이터 사용
    page_number = next(iter(data["pageBoxList"]))
    page_node_data = data["pageBoxList"][page_number]

    if len(page_node_data) == 0:
        print(f"페이지 {page_number}에 데이터가 없습니다. 다음 페이지를 시도합니다.")
        return

    # BoxInfo 데이터 준비
    box_infos = [
        {"id": idx, "x": boxinfo["x"], "y": boxinfo["y"], "bbox": boxinfo["bbox"], "text": boxinfo["text"]}
        for idx, boxinfo in enumerate(page_node_data)
    ]

    # 이미지 파일 준비
    image_path = f"./doc_parsing/image{page_number}.png"
    if not os.path.exists(image_path):
        print(f"이미지 파일이 없습니다: {image_path}")
        return

    # API 요청 데이터 준비
    with open(image_path, "rb") as image_file:
        files = {
            "image": ("image.png", image_file, "image/png"),
            "page_data": (None, json.dumps({"page_number": page_number, "box_infos": box_infos})),
        }

        # API 요청 보내기
        response = client.post("/process_document", files=files)

    # 응답 확인
    assert response.status_code == 200
    assert "response" in response.json()
    print("테스트 성공!")
    print(response.json())
    print("ChatGPT 응답:", response.json()["response"])
    print("2 step")
    page_number = next(iter(data["pageBoxList"]))
    page_node_data = data["pageBoxList"][page_number]

    if len(page_node_data) == 0:
        print(f"페이지 {page_number}에 데이터가 없습니다. 다음 페이지를 시도합니다.")
        return

    # BoxInfo 데이터 준비
    box_infos = [
        {"id": idx, "x": boxinfo["x"], "y": boxinfo["y"], "bbox": boxinfo["bbox"], "text": boxinfo["text"]}
        for idx, boxinfo in enumerate(page_node_data)
    ]

    # 이미지 파일 준비
    image_path = f"./doc_parsing/image{page_number}.png"
    if not os.path.exists(image_path):
        print(f"이미지 파일이 없습니다: {image_path}")
        return

    # API 요청 데이터 준비
    with open(image_path, "rb") as image_file:
        files = {
            "image": ("image.png", image_file, "image/png"),
            "page_data": (None, json.dumps({"page_number": page_number, "box_infos": box_infos})),
        }

        # API 요청 보내기
        response = client.post("/process_document", files=files)

    # 응답 확인
    assert response.status_code == 200
    assert "response" in response.json()
    print("테스트 성공!")
    print(response.json())
    print("ChatGPT 응답:", response.json()["response"])


if __name__ == "__main__":
    test_process_document()
