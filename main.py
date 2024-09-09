import json
import vk_api
from vk_api.bot_longpoll import VkBotEventType, VkBotLongPoll
from datetime import datetime
import time
import requests
import pandas as pd
import config

current_datetime = datetime.now()

def parse_excel(file): 
    block = {}
    xl = pd.read_excel(file)
    num_columns = len(xl.columns)
    print(f"Количество столбцов: {num_columns // 2}")

    for cols in range(0, num_columns, 2):
        for row in range(len(xl)):
            key_cell = xl.iloc[row, cols]
            value_cell = xl.iloc[row, cols + 1]

            if not pd.isnull(key_cell):
                keys = key_cell.lower().split(" <> ")
                for key in keys:
                    block[key] = value_cell

    return block

def send_text(vk_session, current_id, supporting_text, keyboard_used=None): 
    attributes = {
        'chat_id': current_id,
        'message': supporting_text,
        'random_id': 0
    }

    if keyboard_used:
        attributes["keyboard"] = keyboard_used.get_keyboard()

    vk_session.method('messages.send', attributes)

def send_text_chat(vk_session, current_id, peer_id, id_message, supporting_text, keyboard_used=None): 
    query_json = json.dumps({"peer_id": peer_id, "conversation_message_ids": [id_message], "is_reply": True})
    attributes = {
        'chat_id': current_id,
        'message': supporting_text,
        'forward': query_json, 
        'random_id': 0
    }

    if keyboard_used:
        attributes["keyboard"] = keyboard_used.get_keyboard()

    vk_session.method('messages.send', attributes)

def is_in_text(words, checked_text):
    return any(trigger in checked_text for trigger in trigger_lists.get(words, []))

def is_all_in_text(words, checked_text):
    return all(trigger == checked_text for trigger in trigger_lists.get(words, []))

def main(block):
    token = config.token 
    vk_session = vk_api.VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, config.group_id)
    vk = vk_session.get_api()
    print("Loaded") 
    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            message = event.object.message['text'].lower()
            if event.from_chat:
                user_id = event.chat_id
                user_id_true = event.object.message['from_id']
                peer_id = event.message.peer_id
                id_message = event.message['conversation_message_id']

                user = vk_session.method("users.get", {"user_ids": user_id_true})
                fullname = user[0].get('first_name', 'bot') + ' ' + user[0].get('last_name', '')

                print(f"{time.strftime('%H:%M:%S')} в беседе от: {fullname}:\n{message}")

                if 'что такое ' in message:
                    part2 = message.split("что такое ")
                    for a in part2[1:]: 
                        curr = "что такое"
                        mass = a.split()
                        reply = "Нет такой команды"
                        for word in mass:
                            curr += f" {word}"
                            if curr in block:
                                reply = block[curr]
                                break

                        if curr != "что такое":
                            send_text_chat(vk_session, user_id, peer_id, id_message, f"{fullname} спрашивал {curr}: \n{reply}")
                            print(f"{time.strftime('%H:%M:%S')} в беседе от BOT:\n{fullname} спрашивал {curr}: \n{reply}")

if __name__ == "__main__":
    block = parse_excel("blocks.xlsx")
    while True:
        try:
            print("Loading...")
            main(block)
        except (requests.exceptions.RequestException, vk_api.exceptions.ApiHttpError, vk_api.exceptions.ApiError) as e:
            print(f"VK server refresh, 5 seconds delay to reconnect: {e}")
            time.sleep(5)

