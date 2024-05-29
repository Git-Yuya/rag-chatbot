import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
console_handler.setFormatter(formatter)

def check_env_var(env_var: str) -> None:
    """
    環境変数が設定されているか確認

    Parameters
    ----------
    env_var : str
        確認したい環境変数名
    
    """
    try:
        if env_var in os.environ:
            logger.debug(f"{env_var} の環境変数が設定されています。")
        else:
            raise KeyError(f"{env_var} の環境変数が設定されていません。")
    except KeyError as e:
        logger.error(f"KeyError: {e}")
        raise
