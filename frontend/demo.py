import httpx
import gradio as gr
import os

WORKFLOW_API_BASE = os.getenv("WORKFLOW_API_BASE", "http://workflow:8080")

def append_user(message, chat_history, state):
    """
    Adds user's message immediately and clears input.
    """
    message = (message or "").strip()
    if not message:
        return "", chat_history or [], state
    new_history = (chat_history or []) + [[message, None]]
    return "", new_history, state

def stream_bot(chat_history, state):
    """
    Call the API and append bot’s response (can stream here).
    """
    try:
        payload = {"user_id": "demo-user", "message": chat_history[-1][0], "state": state}
        r = httpx.post(f"{WORKFLOW_API_BASE}/chat", json=payload, timeout=None)
        r.raise_for_status()
        data = r.json()
        bot = data.get("answer", "")
        new_state = data.get("state", None)
    except Exception as e:
        bot = f"Error: {e}"
        new_state = state

    chat_history[-1][1] = bot  # fill in the response
    return chat_history, new_state

with gr.Blocks() as demo:
    gr.Markdown("## Project Tracker Chat")
    chat = gr.Chatbot(height=520)
    msg = gr.Textbox(placeholder="Type your message…", lines=1, interactive=True)
    st = gr.State(None)

    # immediate append of user message
    submit = msg.submit(
        append_user, [msg, chat, st], [msg, chat, st], queue=False
    )
    submit.then(
        stream_bot, [chat, st], [chat, st]
    )

    # stream bot message
    send_btn = gr.Button("Send", variant="primary")
    click = send_btn.click(
        append_user, [msg, chat, st], [msg, chat, st], queue=False
    )
    click.then(
        stream_bot, [chat, st], [chat, st]
    )

demo.queue().launch()
