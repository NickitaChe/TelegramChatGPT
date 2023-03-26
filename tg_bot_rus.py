import telebot
import time
import os
import openai

from googletrans import Translator

bot = telebot.TeleBot(os.getenv("TELEBOT_KEY"))
openai.api_key = os.getenv("OPENAI_API_KEY")
model = "davinci:ft-personal:your-model-name-2023-03-26-21-39-39"
stop_symbols = "###"



translator = Translator()

users = {}


def _get_user(id):
    user = users.get(id, {'id': id, 'last_text': '', 'last_prompt_time': 0})
    users[id] = user
    return user


def _process_rq(user_id, rq):
    user = _get_user(user_id)
    last_text = user['last_text']
    # if last prompt time > 10 minutes ago - drop context
    if time.time() - user['last_prompt_time'] > 600:
        last_text = ''
        user['last_prompt_time'] = 0
        user['last_text'] = ''

    if rq and len(rq) > 0 and len(rq) < 1000:
        inc_detect = translator.detect(rq)
        if inc_detect.lang == 'ru':
            eng_rq = translator.translate(rq, dest='en', src='ru').text
            print(f">>> ({user_id}) {rq} -> {eng_rq}")
            rq = eng_rq
        else:
            print(f">>> ({user_id}) {rq}")

        # truncate to 1000 symbols from the end
        prompt = f"{last_text}Q: {rq} ->"[-1000:]
        print("Sending to OpenAI: " + prompt)
        completion = openai.Completion.create(
            engine=model,
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=stop_symbols,
            temperature=0.5,
        )
        eng_ans = completion['choices'][0]['text'].strip()
        if "->" in eng_ans:
            eng_ans = eng_ans.split("->")[0].strip()
        ans = eng_ans
        if inc_detect.lang == 'ru':
            rus_ans = translator.translate(eng_ans, dest='ru', src='en').text
            print(f"<<< ({user_id}) {ans} -> {rus_ans}")
            ans = rus_ans
        else:
            print(f"<<< ({user_id}) {ans}")
        user['last_text'] = prompt + " " + eng_ans + stop_symbols
        user['last_prompt_time'] = time.time()
        return ans
    else:
        user['last_prompt_time'] = 0
        user['last_text'] = ''
        return "!!! Error! Please use simple short texts"



@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user = _get_user(message.from_user.id)
    user['last_prompt_time'] = 0
    user['last_text'] = ''
    bot.reply_to(message, f"Started! (History cleared). Using model {model}")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    user_id = message.from_user.id
    rq = message.text
    ans = _process_rq(user_id, rq)
    bot.send_message(message.chat.id, ans)


if __name__ == '__main__':
    bot.polling()
