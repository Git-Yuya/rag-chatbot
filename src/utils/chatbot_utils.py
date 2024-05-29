import logging
import os
from typing import Dict, List

from openai import OpenAI

from ..utils.helper import check_env_var

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)


def format_user_question(question: str) -> List[Dict[str, str]]:
    """
    ユーザーからの質問をChatGPTに渡すために、リクエストの形式に合わせて整形

    Parameters
    ----------
    question : str
        ユーザーからの質問

    Returns
    -------
    messages : List[Dict[str, str]]
        整形後のメッセージ
    """
    messages = [
        {"role": "system", "content": "あなたは優秀なアシスタントAIです。"},
        {"role": "user", "content": question}
    ]
    
    return messages


def get_openai_client() -> OpenAI:
    """
    OpenAI関連の環境変数が設定されているか確認
    OpenAIのクライアントを取得

    Returns
    -------
    openai_client : OpenAI
        OpenAIのクライアント
    """
    check_env_var("OPENAI_API_KEY")
    check_env_var("OPENAI_EMBEDDING_MODEL")
    check_env_var("OPENAI_CHAT_COMPLETION_MODEL")

    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    return openai_client
