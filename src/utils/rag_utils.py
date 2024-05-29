import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import tiktoken
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import Vector

from ..utils.chatbot_utils import get_openai_client
from ..utils.helper import check_env_var

MAX_TOKEN_COUNT_FOR_SOURCE_TEXT = 4096

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)


def get_search_client() -> SearchClient:
    """
    Azure AI Search関連の環境変数が設定されているか確認
    Azure AI Searchのクライアントを取得

    Returns
    -------
    search_client : SearchClient
        Azure AI Searchのクライアント
    """
    check_env_var("AZURE_AI_SEARCH_ENDPOINT")
    check_env_var("AZURE_AI_SEARCH_API_KEY")
    check_env_var("AZURE_AI_SEARCH_INDEX_NAME")
    
    search_endpoint = os.environ.get("AZURE_AI_SEARCH_ENDPOINT")
    search_credential = AzureKeyCredential(os.environ.get("AZURE_AI_SEARCH_API_KEY"))
    index_name = os.environ.get("AZURE_AI_SEARCH_INDEX_NAME")
    search_client = SearchClient(
        endpoint=search_endpoint,
        credential=search_credential,
        index_name=index_name,
    )

    return search_client


def query_index_use_user_question(user_question: str) -> List[Dict[str, Any]]:
    """
    ユーザーの質問に関連するドキュメントをtopの数だけ返す

    Parameters
    ----------
    user_question : str
        ユーザーの質問

    Returns
    -------
    results : List[Dict[str, Any]]
        関連ドキュメント
    """
    search_client = get_search_client()
    try:
        results = search_client.search(
            search_text=user_question,
            vector=Vector(
                value=create_embedding(user_question),
                k=5,
                fields="contentVector",
            ),
            top=5,
        )
        return results
    except Exception:
        logger.error("Azure AI Searchから検索結果を取得する時にエラーが起きました。", exc_info=True)
        return None


def format_query_results(query_results: List[Dict[str, Any]]) -> Tuple[str, str]:
    """
    関連ドキュメントの情報を整形

    Parameters
    ----------
    query_results : List[Dict[str, Any]]
        関連ドキュメント

    Returns
    -------
    source_text : str
        整形後の関連ドキュメントの情報
    ref : str
        参考文献
    """
    source_text = ""
    ref = ""
    num_source = 0
    for i, result in enumerate(query_results):
        page = result["page"]
        subject = result["title"]
        contents = result["content"]

        if (
            calc_token_count(
                model=os.environ.get("OPENAI_CHAT_COMPLETION_MODEL"),
                text=source_text
                + f"[{i}] "
                + f"subject: {subject}, contents: {contents}"
                + "\n",
            )
            > MAX_TOKEN_COUNT_FOR_SOURCE_TEXT
        ):
            logger.info("MAX_TOKEN_COUNT_FOR_SOURCE_TEXT を超えました。")
            break

        source_text += f"[{i}] subject: {subject}, contents: {contents}\n"
        ref += f"スライド{page}「{subject}」\n"
        num_source += 1
    logger.debug(f"{num_source}個の関連ドキュメントを参照しました。")

    return source_text, ref


def calc_token_count(model: str, text: str) -> int:
    """
    テキストのトークン数を計算

    Parameters
    ----------
    model : str
        使用するChatGPTのモデル
    text : str
        トークン数を計算したいテキスト

    Returns
    -------
    token_count : int
        モデルに基づいて計算されたトークン数
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        token_count = len(encoding.encode(text))
        return token_count
    except Exception:
        logger.error(f"トークンカウントの計算中にエラーが発生しました。", exc_info=True)
        return 0


def create_response(message: Tuple[str, str]) -> str:
    """
    貰った質問に対して、OpenAIのChatGPTを使って返答を生成

    Parameters
    ----------
    message : Tuple[str, str]
        ユーザーの質問
    
    Returns
    -------
    message.content : str
        ChatGPTの返答
    """
    openai_client = get_openai_client()
    try:
        response = openai_client.chat.completions.create(
            messages=message,
            model=os.environ.get("OPENAI_CHAT_COMPLETION_MODEL", None),
        )
        message = response.choices[0].message
        return message.content
    except Exception:
        logger.error("ChatGPTから返答をもらう時にエラーが起きました。", exc_info=True)
        return None


def create_embedding(text: str) -> Optional[List[float]]:
    """
    テキストをベクトル埋め込みする

    Parameters
    ----------
    text : str
        ベクトル埋め込みするテキスト

    Returns
    -------
    response : Optional[List[float]]
        ベクトル埋め込みしたテキスト
    """
    openai_client = get_openai_client()
    try:
        response = (
            openai_client.embeddings.create(
                input=[text],
                model=os.environ.get("OPENAI_EMBEDDING_MODEL"),
            )
            .data[0]
            .embedding
        )
        return response
    except Exception:
        logger.error("ベクトル埋め込みの際にエラーが発生しました。", exc_info=True)
        return None
