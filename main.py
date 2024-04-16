import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
import random
import json
import time
from datetime import datetime

class VKBotInterface():
    def __init__(self, master):
        self.master = master
        master.title("VK Bot Interface")

        self.status_label = tk.Label(master, text="Bot Status: Waiting for input")
        self.status_label.pack()

        self.log_text = scrolledtext.ScrolledText(master, width=50, height=10)
        self.log_text.pack()

        button_width = 20

        self.start_button = tk.Button(master, text="Start Bot", command=self.start_bot, width=button_width)
        self.start_button.pack()

        self.stop_button = tk.Button(master, text="Stop Bot", command=self.stop_bot, state=tk.DISABLED,
                                     width=button_width)
        self.stop_button.pack()

        self.restart_button = tk.Button(master, text="Restart Bot", command=self.restart_bot, state=tk.DISABLED,
                                        width=button_width)
        self.restart_button.pack()

        self.bot_thread = None
        self.is_running = False

    def start_bot(self):
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.restart_button.config(state=tk.NORMAL)

        self.bot_thread = threading.Thread(target=self.run_bot)
        self.bot_thread.start()

    def stop_bot(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.restart_button.config(state=tk.DISABLED)

    def restart_bot(self):
        self.stop_bot()
        self.start_bot()

    def run_bot(self):
        try:
            self.log_text.insert(tk.END, "Bot started...\n")
            self.update_status("Bot Status: Running")

            token = get_token_from_file()
            vk_session = vk_api.VkApi(token=token)
            vk = vk_session.get_api()
            longpoll = VkLongPoll(vk_session)
            hello = get_text_hello()

            for event in longpoll.listen():
                if not self.is_running:
                    break

                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    user_data = get_or_create_user_data(vk, event.user_id)
                    user_id = event.user_id
                    message_time = datetime.fromtimestamp(event.timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    message_text = f"Received message from user {user_id} at {message_time}: {event.text}\n"
                    self.log_text.insert(tk.END, message_text)
                    self.log_text.see(tk.END)  # Прокрутка до конца
                    self.log_text.update()
                    if user_data['process'] == 'StartQuiz':
                        with open("question.json", "r", encoding='utf-8') as file:
                            questions_data = json.load(file)

                        current_question_id = str(user_data['current_question'])
                        current_question = questions_data['questions'][current_question_id]
                        correct_answer = current_question['correct_answer']
                        explanation_correct = current_question['explanation_correct']
                        explanation_incorrect = current_question['explanation_incorrect']

                        if event.text.lower() == correct_answer.lower():
                            send_message(vk, event.user_id, explanation_correct)
                        else:
                            send_message(vk, event.user_id, explanation_incorrect)

                        user_data['current_question'] += 1
                        save_user_data(event.user_id, user_data)

                        if user_data['current_question'] <= len(questions_data['questions']):
                            current_question_id = str(user_data['current_question'])
                            current_question = questions_data['questions'][current_question_id]
                            answers_text = "\n".join(
                                [f"{i + 1}) {answer}" for i, answer in enumerate(current_question['answers'])])
                            question_text = f"{current_question_id}. {current_question['question']}\n{answers_text}"
                            keyboard = create_keyboard([
                                [{"action": {"type": "text", "payload": "{}", "label": answer}}] for answer in
                                current_question['answers']
                            ], color="primary")

                            send_message(vk, event.user_id, question_text, keyboard)
                        else:
                            send_message(vk, event.user_id,
                                         "Спасибо за участие в викторине! Чтобы узнать итоги розыгрыша, "
                                         "приходи на АгитБригады 27 апреля. Ждём тебя 😉")
                            user_data['process'] = 'Finished'
                            save_user_data(event.user_id, user_data)
                            with open("finished.txt", "a", encoding='utf-8') as file:
                                file.write(
                                    f"{user_data['name']} {user_data['surname']}\nID: {user_data['id']}\n\n")
                    elif event.text.lower() == "начать викторину" and user_data['process'] == 'new':
                        user_data['process'] = 'StartQuiz'
                        user_data['current_question'] = 1
                        save_user_data(event.user_id, user_data)
                        with open("question.json", "r", encoding='utf-8') as file:
                            questions_data = json.load(file)

                        current_question_id = str(user_data['current_question'])
                        current_question = questions_data['questions'][current_question_id]
                        answers_text = "\n".join(
                            [f"{i + 1}) {answer}" for i, answer in enumerate(current_question['answers'])])
                        question_text = f"{current_question_id}. {current_question['question']}\n{answers_text}"
                        keyboard = create_keyboard([
                            [{"action": {"type": "text", "payload": "{}", "label": answer}}] for answer in
                            current_question['answers']
                        ], color="primary")

                        send_message(vk, event.user_id, question_text, keyboard)
                    elif user_data['process'] == 'Finished':
                        goodbye_message = get_text_goodbye()
                        send_message(vk, event.user_id, goodbye_message)
                    elif 'привет' in event.text.lower() or 'начать' in event.text.lower():
                        keyboard = create_keyboard(
                            [[{"action": {"type": "text", "payload": "{}", "label": "Начать викторину"}}]],
                            color="positive")
                        send_message(vk, event.user_id, hello.replace('{first_name}', user_data['name']),
                                     keyboard)
                    else:
                        send_message(vk, event.user_id,
                                     f"Привет, {user_data['name']}, кажется, я тебя уже тут видел!")

        except Exception as e:
            messagebox.showerror("Error", f"Bot crashed with error: {e}")
            self.update_status("Bot Status: Crashed")
            time.sleep(10)

    def update_status(self, status):
        self.status_label.config(text=status)
        self.master.update()

def get_or_create_user_data(vk, user_id):
    user_data = get_user_data(user_id)
    if user_data is None:
        user_info = vk.users.get(user_id=user_id)[0]
        user_data = {
            "id": user_info["id"],
            "name": user_info["first_name"],
            "surname": user_info["last_name"],
            "process": "new",
            "current_question": 1
        }
        save_user_data(user_id, user_data)
    return user_data

def send_message(vk, user_id, message, keyboard=None):
    vk.messages.send(
        user_id=user_id,
        message=message,
        random_id=generate_random_id(),
        keyboard=keyboard
    )

def create_keyboard(buttons, color="primary"):
    keyboard = {
        "one_time": True,
        "buttons": buttons
    }
    for row in keyboard["buttons"]:
        for button in row:
            button["color"] = color
    return json.dumps(keyboard)

def get_text_hello():
    with open("HelloMessage.txt", "r", encoding='utf-8') as file:
        return file.read().strip()

def get_text_goodbye():
    with open("GoodbyeMessage.txt", "r", encoding='utf-8') as file:
        return file.read().strip()

def get_token_from_file():
    with open("token.txt", "r") as file:
        return file.read().strip()

def generate_random_id():
    return random.getrandbits(31) * random.choice([1, -1])

def get_user_data(user_id):
    try:
        with open("users.json", "r", encoding='utf-8') as file:
            users_data = json.load(file)
    except FileNotFoundError:
        users_data = {}
    return users_data.get(str(user_id), None)

def save_user_data(user_id, user_data):
    try:
        with open("users.json", "r", encoding='utf-8') as file:
            users_data = json.load(file)
    except FileNotFoundError:
        users_data = {}
    users_data[str(user_id)] = user_data
    with open("users.json", "w", encoding='utf-8') as file:
        json.dump(users_data, file, ensure_ascii=False)

def main():
    root = tk.Tk()
    my_bot = VKBotInterface(root)
    root.mainloop()

if __name__ == "__main__":
    main()
