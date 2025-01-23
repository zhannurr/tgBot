from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Вопросы и ответы для теста
questions = [
    {
        "question": "Какой фразеологизм обозначает способность находить общий язык?",
        "options": ["Ушки на макушке", "Ключ к сердцу", "Водить за нос"],
        "answer": "Ключ к сердцу"
    },
    {
        "question": "Что значит 'взять быка за рога' в деловой среде?",
        "options": ["Преодолевать трудности", "Избегать ответственности", "Обдумывать решение"],
        "answer": "Преодолевать трудности"
    },
    {
        "question": "Какой фразеологизм означает дать обещание и выполнить его?",
        "options": ["Бросить слова на ветер", "Завязать узел", "Держать слово"],
        "answer": "Держать слово"
    }
]

user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"current_question": 0, "score": 0}
    
    await update.message.reply_text(
        "Добро пожаловать в тест по фразеологизмам для делового этикета! \nДавайте начнем!\n",
        reply_markup=ReplyKeyboardMarkup([
            ["Начать тест"]
        ], resize_keyboard=True)
    )

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = user_data.get(user_id, {})

    current_question = data.get("current_question", 0)

    if current_question >= len(questions):
        await update.message.reply_text(
            f"Тест завершен! Ваш результат: {data['score']} из {len(questions)}"
        )
        return

    question = questions[current_question]
    options = question["options"]

    await update.message.reply_text(
        question["question"],
        reply_markup=ReplyKeyboardMarkup([options], resize_keyboard=True)
    )

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = user_data.get(user_id, {})

    current_question = data.get("current_question", 0)
    if current_question >= len(questions):
        await update.message.reply_text("Тест уже завершен. Начните заново, если хотите пройти снова.")
        return

    question = questions[current_question]
    user_answer = update.message.text

    if user_answer == question["answer"]:
        data["score"] += 1
        await update.message.reply_text("Правильно!")
    else:
        await update.message.reply_text(f"Неправильно. Правильный ответ: {question['answer']}")

    data["current_question"] += 1
    user_data[user_id] = data
    
    await ask_question(update, context)

def main():
    application = Application.builder().token("7666959651:AAH5FQ4QhDVFJkfS88VMmNnDv_bZfduu2-s").build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Начать тест$"), ask_question))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    application.run_polling()

if __name__ == "__main__":
    main()
