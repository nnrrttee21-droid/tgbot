import logging
import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
Application, CommandHandler, MessageHandler,
CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)

BOT_TOKEN = “8684899203:AAEE-flZ2t-JNEC3exysaxVHoapp8dtw0A4”
ALLOWED_USER_ID = 8380308811
GMAIL_ADDRESS = “nnrrttee21@gmail.com”
GMAIL_APP_PASSWORD = “afbwocqajrzfazht”

TARGET_EMAILS = [
“abuse@telegram.org”,
“security@telegram.org”,
“recover@telegram.org”,
“support@telegram.org”
]

CHOOSE_ACTION = 0
ENTER_SUBJECT = 1
ENTER_BODY = 2
ENTER_COUNT = 3
CONFIRM_SEND = 4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(**name**)

def is_allowed(update: Update) -> bool:
return update.effective_user.id == ALLOWED_USER_ID

def send_emails(subject: str, body: str, count: int):
success = 0
fail = 0
ctx = ssl.create_default_context()
try:
server = smtplib.SMTP(“smtp.gmail.com”, 587, timeout=30)
server.starttls(context=ctx)
server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
for _ in range(count):
for email in TARGET_EMAILS:
try:
msg = MIMEMultipart()
msg[“From”] = GMAIL_ADDRESS
msg[“To”] = email
msg[“Subject”] = subject
msg.attach(MIMEText(body, “plain”, “utf-8”))
server.sendmail(GMAIL_ADDRESS, email, msg.as_string())
success += 1
except Exception as e:
logger.error(f”Ошибка {email}: {e}”)
fail += 1
server.quit()
except Exception as e:
logger.error(f”Ошибка подключения: {e}”)
fail += count * len(TARGET_EMAILS)
return success, fail

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_allowed(update):
return
keyboard = [[InlineKeyboardButton(“📩 Отправить жалобу”, callback_data=“send_complaint”)]]
await update.message.reply_text(
“👋 Добро пожаловать!\n\n”
“Бот отправляет жалобы на адреса Telegram:\n”
“• abuse@telegram.org\n”
“• security@telegram.org\n”
“• recover@telegram.org\n”
“• support@telegram.org\n\n”
“Нажмите кнопку ниже, чтобы начать:”,
reply_markup=InlineKeyboardMarkup(keyboard)
)
return CHOOSE_ACTION

async def send_complaint_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
if query.from_user.id != ALLOWED_USER_ID:
return
await query.message.reply_text(“📋 *Выберите тему*\n\nНапишите тему письма:”, parse_mode=“Markdown”)
return ENTER_SUBJECT

async def enter_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_allowed(update):
return
subject = update.message.text.strip()
context.user_data[“subject”] = subject
await update.message.reply_text(
f”📝 *Шаблон письма создан*\n\n*Тема:* {subject}\n\nТеперь напишите подробно жалобу с ссылками на нарушение:”,
parse_mode=“Markdown”
)
return ENTER_BODY

async def enter_body(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_allowed(update):
return
context.user_data[“body”] = update.message.text.strip()
keyboard = [
[
InlineKeyboardButton(“1”, callback_data=“count_1”),
InlineKeyboardButton(“5”, callback_data=“count_5”),
InlineKeyboardButton(“10”, callback_data=“count_10”),
InlineKeyboardButton(“50”, callback_data=“count_50”),
],
[
InlineKeyboardButton(“100”, callback_data=“count_100”),
InlineKeyboardButton(“250”, callback_data=“count_250”),
InlineKeyboardButton(“500”, callback_data=“count_500”),
InlineKeyboardButton(“1000”, callback_data=“count_1000”),
],
[InlineKeyboardButton(“✏️ Ввести своё число”, callback_data=“count_custom”)]
]
await update.message.reply_text(
“🔢 *Выберите количество отправок:*\n_(число × 4 письма на все адреса)_”,
reply_markup=InlineKeyboardMarkup(keyboard),
parse_mode=“Markdown”
)
return ENTER_COUNT

async def choose_count_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
if query.from_user.id != ALLOWED_USER_ID:
return
if query.data == “count_custom”:
await query.message.reply_text(“✏️ Введите своё число отправок:”)
return ENTER_COUNT
count = int(query.data.replace(“count_”, “”))
context.user_data[“count”] = count
return await show_confirm(query.message, context, count)

async def enter_custom_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_allowed(update):
return
try:
count = int(update.message.text.strip())
if count < 1:
raise ValueError
context.user_data[“count”] = count
return await show_confirm(update.message, context, count)
except ValueError:
await update.message.reply_text(“❌ Введите корректное число (целое, больше 0):”)
return ENTER_COUNT

async def show_confirm(message, context, count):
subject = context.user_data.get(“subject”, “”)
body = context.user_data.get(“body”, “”)
total = count * len(TARGET_EMAILS)
preview = body[:200] + “…” if len(body) > 200 else body
keyboard = [[
InlineKeyboardButton(“✅ Отправить”, callback_data=“confirm_send”),
InlineKeyboardButton(“❌ Отменить”, callback_data=“confirm_cancel”)
]]
await message.reply_text(
f”📬 *Подтверждение отправки*\n\n”
f”*Тема:* {subject}\n”
f”*Жалоба:* {preview}\n\n”
f”*Получатели:* все 4 адреса Telegram\n”
f”*Повторений:* {count}\n”
f”*Итого писем:* {total}\n\n”
f”Подтвердите отправку:”,
reply_markup=InlineKeyboardMarkup(keyboard),
parse_mode=“Markdown”
)
return CONFIRM_SEND

async def confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
query = update.callback_query
await query.answer()
if query.from_user.id != ALLOWED_USER_ID:
return
if query.data == “confirm_cancel”:
await query.message.reply_text(“❌ Отправка отменена.\n\nНапишите /start чтобы начать заново.”)
context.user_data.clear()
return ConversationHandler.END

```
subject = context.user_data.get("subject")
body = context.user_data.get("body")
count = context.user_data.get("count")

await query.message.reply_text(f"⏳ Отправляю {count * len(TARGET_EMAILS)} писем... Подождите.")

loop = asyncio.get_event_loop()
success, fail = await loop.run_in_executor(None, send_emails, subject, body, count)

await query.message.reply_text(
    f"✅ *Отправка завершена!*\n\n📤 Успешно: {success}\n❌ Ошибок: {fail}\n\nНапишите /start чтобы отправить ещё.",
    parse_mode="Markdown"
)
context.user_data.clear()
return ConversationHandler.END
```

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
if not is_allowed(update):
return
context.user_data.clear()
await update.message.reply_text(“❌ Отменено. Напишите /start для начала.”)
return ConversationHandler.END

def main():
app = Application.builder().token(BOT_TOKEN).build()
conv_handler = ConversationHandler(
entry_points=[
CommandHandler(“start”, start),
CallbackQueryHandler(send_complaint_callback, pattern=”^send_complaint$”)
],
states={
CHOOSE_ACTION: [CallbackQueryHandler(send_complaint_callback, pattern=”^send_complaint$”)],
ENTER_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_subject)],
ENTER_BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_body)],
ENTER_COUNT: [
CallbackQueryHandler(choose_count_callback, pattern=”^count_”),
MessageHandler(filters.TEXT & ~filters.COMMAND, enter_custom_count)
],
CONFIRM_SEND: [CallbackQueryHandler(confirm_callback, pattern=”^confirm_”)],
},
fallbacks=[CommandHandler(“cancel”, cancel)],
allow_reentry=True
)
app.add_handler(conv_handler)
logger.info(“Бот запущен!”)
app.run_polling()

if **name** == “**main**”:
main()
