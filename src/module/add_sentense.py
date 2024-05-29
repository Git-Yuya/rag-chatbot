import logging
from typing import Tuple

from ..utils.rag_utils import (format_query_results,
                                query_index_use_user_question)

MAX_TOKEN_COUNT_FOR_SOURCE_TEXT = 4096

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)


def add_sentense(question: str) -> Tuple[str, str]:
    """
    ユーザーの質問に関連する文献を追加

    Parameters
    ----------
    question : str
        ユーザーの質問

    Returns
    -------
    question_with_source : str
        ユーザーの質問に関連するドキュメントを追加した文章
    ref : str
        参考文献
    """
    query_results = query_index_use_user_question(question)
    source_text, ref = format_query_results(query_results)
    question_with_source = f"[質問]:{question}\n[参考文献]:{source_text}"

    return question_with_source, ref
