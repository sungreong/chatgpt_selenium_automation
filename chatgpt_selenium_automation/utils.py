from dotenv import load_dotenv
import os


def get_url_info():
    load_dotenv()
    url = r"https://chat.openai.com/"
    if os.getenv("TEMPORARY_CHAT").lower() == "true":
        use_temporary_chat = True
    else:
        use_temporary_chat = False

    if os.getenv("ROOM_ID", None) is not None:
        room_id = os.getenv("ROOM_ID")
        if not use_temporary_chat:
            roolm_api = f"/c/{room_id}"
        else:
            roolm_api = "/"
    else:
        roolm_api = "/"
    assert os.getenv("MODEL") in os.getenv("MODEL_LIST").split(","), "MODEL must be in MODEL_LIST"
    model = os.getenv("MODEL")
    model_api = f"?model={model}"
    url = url + roolm_api + model_api
    return url, use_temporary_chat
