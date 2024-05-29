import logging
from typing import Tuple

from ..utils.chatbot_utils import format_user_question
from ..utils.rag_utils import create_response

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)


def create_answer(question_with_ref: Tuple[str, str]) -> str:
    """
    ChatGPTのAPIを利用して、ユーザーの質問に対する回答を生成

    Parameters
    ----------
    question_with_ref : Tuple[str, str]
        ユーザーの質問と参考文献

    Returns
    -------
    answer_with_ref : strs
        回答と参考文献
    """
    question, ref = question_with_ref
    messages = format_user_question(question)
    answer = create_response(messages)
    answer_with_ref = f"{answer} \n\n\n参考文献:\n{ref}"

    return answer_with_ref
