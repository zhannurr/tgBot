import json
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем вопросы из JSON-файла
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

questions = load_questions()
user_data = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Запускает бота и подготавливает тест."""
    user_id = update.effective_user.id
    user_data[user_id] = {"current_question": 0, "score": 0, "active": True}  # Устанавливаем активный тест

    await update.message.reply_text(
        "Привет! Добро пожаловать в тест по фразеологизмам.\n"
        "Чтобы начать, нажмите 'Начать тест'.",
        reply_markup=ReplyKeyboardMarkup([["Начать тест"]], resize_keyboard=True)
    )

async def start_test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Сбрасывает данные и начинает тест заново."""
    user_id = update.effective_user.id
    user_data[user_id] = {"current_question": 0, "score": 0, "active": True}  # Сбрасываем прогресс
    await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Задает следующий вопрос пользователю."""
    user_id = update.effective_user.id
    data = user_data.get(user_id)

    if not data or "current_question" not in data:
        await start(update, context)
        return

    current_question = data["current_question"]

    if current_question >= len(questions):
        # Завершаем тест
        await update.message.reply_text(
            f"🎉 Тест завершен! Ваш результат: {data['score']} из {len(questions)}.\n\n"
            "Если хотите пройти тест снова, нажмите 'Начать тест'.",
            reply_markup=ReplyKeyboardMarkup([["Начать тест"]], resize_keyboard=True)
        )
        user_data[user_id]["active"] = False  # Деактивируем текущий тест
        return

    question = questions[current_question]
    options = [[opt] for opt in question["options"]]

    await update.message.reply_text(
        f"❓ {question['question']}",
        reply_markup=ReplyKeyboardMarkup(options, resize_keyboard=True, one_time_keyboard=True)
    )

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ответ пользователя и задает следующий вопрос."""
    user_id = update.effective_user.id
    data = user_data.get(user_id)

    if not data or not data.get("active", False):  # Проверяем, активен ли тест
        await update.message.reply_text("Тест завершен. Нажмите 'Начать тест', чтобы пройти его снова.")
        return

    current_question = data["current_question"]

    if current_question >= len(questions):
        await update.message.reply_text("Тест уже завершен. Нажмите 'Начать тест', чтобы пройти его снова.")
        return

    question = questions[current_question]
    user_answer = update.message.text.strip()

    if user_answer == question["answer"]:
        data["score"] += 1
        await update.message.reply_text("✅ Верно!")
    else:
        await update.message.reply_text(f"❌ Неправильно. Правильный ответ: {question['answer']}")

    data["current_question"] += 1
    user_data[user_id] = data

    await ask_question(update, context)

def main():
    """Запуск бота."""
    token = "7666959651:AAH5FQ4QhDVFJkfS88VMmNnDv_bZfduu2-s"

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Regex("^Начать тест$"), start_test))  # Запуск теста
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response))

    logger.info("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
