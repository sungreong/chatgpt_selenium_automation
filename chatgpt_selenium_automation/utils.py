from dotenv import load_dotenv
import os


def get_url_info():
    load_dotenv()
    url = r"https://chat.openai.com/"

    # TEMPORARY_CHAT 환경 변수가 없거나 'true'가 아니면 False로 설정
    use_temporary_chat = os.getenv("TEMPORARY_CHAT", "").lower() == "true"
    roolm_api = ""
    if os.getenv("GROUP_ID", None) is not None:
        group_id = os.getenv("GROUP_ID")
        roolm_api = f"/g/{group_id}"

    # if os.getenv("ROOM_ID", None) is not None:
    #     room_id = os.getenv("ROOM_ID")
    #     if not use_temporary_chat:
    #         roolm_api = f"/c/{room_id}"
    #     else:
    #         roolm_api = "/"
    # else:
    #     roolm_api = "/"
    if os.getenv("ROOM_ID", None) is not None:
        ROOM_ID = os.getenv("ROOM_ID")
        container_api = f"/c/{ROOM_ID}"
    else:
        container_api = ""
    assert os.getenv("MODEL") in os.getenv("MODEL_LIST", "").split(","), "MODEL must be in MODEL_LIST"
    model = os.getenv("MODEL")
    model_api = f"?model={model}"
    url = url + roolm_api + container_api + model_api
    return url, use_temporary_chat
