import logging
import tempfile
from typing import List, Tuple

import gradio as gr

from src.module.add_sentense import add_sentense
from src.module.create_answer import create_answer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
logger.addHandler(console_handler)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(chat)s")
console_handler.setFormatter(formatter)

# チャット履歴用
chat_history = []
# チャット履歴の一時保存先
tmp_file_path = ""


def chat(user_msg: str) -> List[Tuple[str, str]]:
    """
    全てのチャット履歴を返す

    Parameters
    ----------
    user_msg : str
        ユーザーのメッセージ

    Returns
    -------
    all_history : List[Tuple[str, str]]
        全てのチャット履歴

    """
    global chat_history
    answer = create_answer(add_sentense(user_msg))
    chat_history.append({"role": "user", "content": user_msg})
    chat_history.append({"role": "assistant", "content": answer})
    all_history = [(chat_history[i]["content"], chat_history[i + 1]["content"]) for i in range(0, len(chat_history) - 1, 2)]

    return all_history


def save_chat() -> gr.DownloadButton:
    """
    チャット履歴を保存

    Returns
    -------
    gr.DownloadButton
        ダウンロードボタン
    """
    global chat_history

    with open(tmp_file_path, mode="w", encoding="utf-8") as f:
        for i in range(0, len(chat_history) - 1, 2):
            f.write(f'User: {chat_history[i]["content"]}\n')
            f.write(f'Chatbot: {chat_history[i + 1]["content"]}\n\n')
    
    return gr.DownloadButton(label="チャット履歴を保存", value=tmp_file_path, icon="icon/download_button.svg")


def delete_chat() -> None:
    """
    クリアボタンが押されたときにチャット履歴を削除
    """
    global chat_history
    chat_history = []


with gr.Blocks(title="RAGチャットボット") as demo:
    chatbot = gr.Chatbot(label="RAGチャットボット", show_label=True, show_copy_button=True,
                         placeholder="こんにちは！\n私はXXXXXについての質問に答えるチャットボットです。\nさっそく、テキスト入力欄に質問を入力してみましょう。")

    msg = gr.Textbox(placeholder="質問を入力してください", label="テキスト入力欄", show_label=True, autofocus=True, show_copy_button=True)

    with gr.Row():
        download = gr.DownloadButton(label="チャット履歴を保存", icon="icon/download_button.svg")
        clear = gr.ClearButton(components=[msg, chatbot], value="チャット履歴を削除", icon="icon/clear_button.svg")

    msg.submit(fn=chat, inputs=msg, outputs=chatbot).then(fn=lambda: "", inputs=None, outputs=msg).then(fn=save_chat, outputs=download)

    clear.click(fn=delete_chat).then(fn=save_chat, outputs=download)


if __name__ == "__main__":
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix="chat_history_", suffix=".txt", dir=".") as tf:
        tmp_file_path = tf.name
        demo.launch(share=True)
