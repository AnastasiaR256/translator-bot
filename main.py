import aiohttp
import logging
from bs4 import BeautifulSoup
from telegram.ext import Application, MessageHandler, CommandHandler, ConversationHandler, filters
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from tokens import TG_TOKEN, TR_TOKEN
import re
import json
import os
from random import randrange
import codecs
import html

if not os.path.exists("logs"):
    os.mkdir("logs")
with open("test.json", "r") as file:
    test_json = file.read()
TEST = json.loads(test_json)
for i in range(len(TEST["test"])):
    TEST["test"][i]["question"] = codecs.decode(TEST["test"][i]["question"].replace("N", r"\N"), 'unicode_escape')


def setup_logger(name, log_file):
    handler = logging.FileHandler('logs/' + log_file, 'a', errors='namereplace')
    handler.setFormatter(logging.Formatter(fmt='[%(asctime)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


async def start(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': /start')
    bot_text = (f"Здравствуйте, {user.first_name}!\n"
                "Я бот-переводчик с русского на английский и обратно. Мои команды:\n"
                "/help – получить справку о боте\n"
                "/direction – выбрать направление перевода\n"
                "/context <слово|словосочетание> – получить примеры перевода слова или "
                "словосочетания в зависимости от контекста\n"
                "/translate <предложение> – получить перевод предложения\n"
                "/test – пройти тест на знание названий различных продуктов питания на английском языке")
    await update.message.reply_text(bot_text)
    logger.info('bot: ' + bot_text)


async def help_command(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': /help')
    bot_text = ("/help – получить справку о боте\n"
                "/direction – выбрать направление перевода\n"
                "/context <слово|словосочетание> – получить примеры перевода слова или "
                "словосочетания в зависимости от контекста\n"
                "/translate <предложение> – получить перевод предложения\n"
                "/test – пройти тест на знание названий различных продуктов питания на английском языке")
    await update.message.reply_text(bot_text)
    logger.info('bot: ' + bot_text)


async def direction_command(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': /direction')
    reply_keyboard = [['Английский –> русский'], ['Русский –> английский']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    bot_text = "Выберите направление перевода:"
    await update.message.reply_text(bot_text, reply_markup=markup)
    logger.info('bot: ' + bot_text + " [Английский –> русский][Русский –> английский]")


async def set_en_ru(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': Английский –> русский')
    context.user_data['lang'] = 'ru'
    bot_text = "Выбрано: английский –> русский"
    await update.message.reply_text(bot_text, reply_markup=ReplyKeyboardRemove())
    logger.info('bot: ' + bot_text)


async def set_ru_en(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': Русский –> английский')
    context.user_data['lang'] = 'en'
    bot_text = "Выбрано: русский –> английский"
    await update.message.reply_text(bot_text, reply_markup=ReplyKeyboardRemove())
    logger.info('bot: ' + bot_text)


async def context_command(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': ' + update.message.text)
    if not context.args:
        bot_text = "Нет аргумента команды. Использование: /context <слово|словосочетание>"
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
        return
    phrase = ' '.join(context.args).lower()
    lang = context.user_data.get('lang')
    if lang is None:
        context.user_data['lang'] = 'en'
        lang = 'en'
    if not (re.fullmatch(r"\b[а-я '-]+\b", phrase) or re.fullmatch(r"\b[a-z '-]+\b", phrase)):
        bot_text = f"'{phrase}' содержит неверные символы."
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
        return
    if re.fullmatch(r"\b[а-я '-]+\b", phrase) and lang == 'ru':
        bot_text = ("Текущее направление перевода: английский –> русский. " +
                    "Чтобы сменить направление перевода, воспользуйтесь /direction")
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
        return
    if re.fullmatch(r"\b[a-z '-]+\b", phrase) and lang == 'en':
        bot_text = ("Текущее направление перевода: русский –> английский. " +
                    "Чтобы сменить направление перевода, воспользуйтесь /direction")
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
        return
    if lang == 'en':
        url = f"https://context.reverso.net/перевод/русский-английский/{phrase.replace(' ', '+')}"
    else:
        url = f"https://context.reverso.net/перевод/английский-русский/{phrase.replace(' ', '+')}"
    headers = {'User-Agent': 'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16.2'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status == 200:
                text = await response.text()
            else:
                bot_text = "К сожалению, произошла ошибка соединения"
                await update.message.reply_text(bot_text)
                logger.info('bot: ' + bot_text)
                return
    soup = BeautifulSoup(text, "html.parser")
    example_section = soup.find('section', {'class': 'wide-container', 'id': 'examples-content'})
    examples = example_section.find_all('span', class_='text')
    if examples:
        max_number = len(examples) if len(examples) < 8 else 8
        for i in range(0, max_number, 2):
            text1 = examples[i].text.strip()
            for word in examples[i].find_all('em'):
                text1 = text1.replace(word.text, f"<u>{word.text}</u>")
            text2 = examples[i + 1].text.strip()
            for word in examples[i + 1].find_all('em'):
                text2 = text2.replace(word.text, f"<u>{word.text}</u>")
            bot_text = f"{text1} – {text2}"
            await update.message.reply_html(bot_text)
            logger.info('bot: ' + bot_text)
    else:
        bot_text = f"К сожалению, '{phrase}' не найдено."
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)


async def translate_command(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': ' + update.message.text)
    if not context.args:
        bot_text = "Нет аргумента команды. Использование: /translate <предложение>"
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
        return
    text = ' '.join(context.args)
    lang = context.user_data.get('lang')
    if lang is None:
        context.user_data['lang'] = 'en'
        lang = 'en'
    if lang == 'en':
        url = f"https://translation.googleapis.com/language/translate/v2/?key={TR_TOKEN}&q={text}&source=ru&target=en"
    else:
        url = f"https://translation.googleapis.com/language/translate/v2/?key={TR_TOKEN}&q={text}&source=en&target=ru"
    headers = {'User-Agent': 'Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16.2'}
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            if response.status == 200:
                json_response = await response.json()
            else:
                bot_text = "К сожалению, произошла ошибка соединения"
                await update.message.reply_text(bot_text)
                logger.info('bot: ' + bot_text)
                return
    data = json_response.get("data")
    if data is None:
        bot_text = "К сожалению, произошла ошибка переводчика"
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
        return
    answer = html.unescape(data["translations"][0]["translatedText"])
    await update.message.reply_text(answer)
    logger.info('bot: ' + answer)


async def unknown(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': ' + fr"{update.message.text}")


async def test_command(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': ' + update.message.text)
    context.user_data['questions'] = TEST["test"].copy()
    context.user_data['ratio'] = {"correct": 0, "all": 0}
    question = context.user_data['questions'].pop(randrange(len(context.user_data['questions'])))
    context.user_data['answer'] = question["answer"]
    bot_text = (
        "Это тест на знание названий различных продуктов питания на английском языке.\n"
        "Вы можете прервать выполнение теста, послав команду /stop.")
    await update.message.reply_text(bot_text)
    logger.info('bot: ' + bot_text)
    choice = TEST["test"].copy()
    for i in range(len(choice)):
        if choice[i]["question"] == question["question"]:
            choice.pop(i)
            break
    options = [choice[randrange(len(choice))]["answer"] for _ in range(3)]
    options.append(question["answer"])
    reply_keyboard = [[options.pop(randrange(len(options))) for _ in range(2)] for _ in range(2)]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    bot_text = question["question"]
    await update.message.reply_text(bot_text, reply_markup=markup)
    logger.info('bot: ' + bot_text)
    return 1


async def answer_handler(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': ' + update.message.text)
    context.user_data['ratio']['all'] += 1
    answer = update.message.text
    if answer == context.user_data['answer']:
        context.user_data['ratio']['correct'] += 1
        bot_text = "Это правильный ответ"
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
    else:
        bot_text = "Это неправильный ответ"
        await update.message.reply_text(bot_text)
        logger.info('bot: ' + bot_text)
    if context.user_data['questions']:
        question = context.user_data['questions'].pop(randrange(len(context.user_data['questions'])))
        context.user_data['answer'] = question["answer"]
        choice = TEST["test"].copy()
        for i in range(len(choice)):
            if choice[i]["question"] == question["question"]:
                choice.pop(i)
                break
        options = [choice[randrange(len(choice))]["answer"] for _ in range(3)]
        options.append(question["answer"])
        reply_keyboard = [[options.pop(randrange(len(options))) for _ in range(2)] for _ in range(2)]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        bot_text = question["question"]
        await update.message.reply_text(bot_text, reply_markup=markup)
        logger.info('bot: ' + bot_text)
        return 1
    else:
        bot_text = ("Тест завершен. Ваше количество правильных ответов: " +
                    str(context.user_data['ratio']["correct"]) + ' из ' + str(context.user_data['ratio']["all"]))
        await update.message.reply_text(bot_text, reply_markup=ReplyKeyboardRemove())
        logger.info('bot: ' + bot_text)
        context.user_data.pop("questions", None)
        context.user_data.pop("answer", None)
        context.user_data.pop("ratio", None)
        return ConversationHandler.END


async def stop_command(update, context):
    user = update.message.from_user
    if str(user.id) not in logging.Logger.manager.loggerDict:
        setup_logger(str(user.id), str(user.id) + '.log')
    logger = logging.getLogger(str(user.id))
    logger.info(user.first_name + ': ' + update.message.text)
    bot_text = ("Тест завершен досрочно. Ваше количество правильных ответов: " +
                str(context.user_data['ratio']["correct"]) + ' из ' + str(context.user_data['ratio']["all"]))
    await update.message.reply_text(bot_text, reply_markup=ReplyKeyboardRemove())
    logger.info('bot: ' + bot_text)
    context.user_data.pop("questions", None)
    context.user_data.pop("answer", None)
    context.user_data.pop("ratio", None)
    return ConversationHandler.END


def main():
    application = Application.builder().token(TG_TOKEN).build()
    application.add_handler(MessageHandler(filters.Text(['Английский –> русский']) & ~filters.COMMAND, set_en_ru))
    application.add_handler(MessageHandler(filters.Text(['Русский –> английский']) & ~filters.COMMAND, set_ru_en))
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('test', test_command)],
        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, answer_handler)],
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop_command)]
    )
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("direction", direction_command))
    application.add_handler(CommandHandler("context", context_command))
    application.add_handler(CommandHandler("translate", translate_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))
    application.run_polling()


if __name__ == '__main__':
    main()
