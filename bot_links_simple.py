import os
import re
from telegram import Update, MessageEntity
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# токен из переменных окружения Railway
TOKEN = os.getenv("TOKEN")

# регулярка для подстраховки
URL_RE = re.compile(r"(https?://[^\s]+|t\.me/[^\s]+|www\.[^\s]+)")

def extract_links_from_text(text: str):
    if not text:
        return []
    found = URL_RE.findall(text)
    cleaned = []
    for u in found:
        if u.startswith("www."):
            cleaned.append("http://" + u)
        elif u.startswith("t.me/"):
            cleaned.append("https://" + u)
        else:
            cleaned.append(u)
    return cleaned

def extract_links_from_message(msg):
    links = []

    entities = []
    if msg.entities:
        entities += msg.entities
    if getattr(msg, "caption_entities", None):
        entities += msg.caption_entities

    text_source = msg.text or msg.caption or ""

    for ent in entities:
        if ent.type == MessageEntity.TEXT_LINK and ent.url:
            links.append(ent.url)
        elif ent.type == MessageEntity.URL:
            start, end = ent.offset, ent.offset + ent.length
            links.append(text_source[start:end])

    regex_links = extract_links_from_text(text_source)
    for u in regex_links:
        if u not in links:
            links.append(u)

    return links

async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    links = extract_links_from_message(msg)

    if links:
        await msg.reply_text("\n".join(links))
    else:
        await msg.reply_text("Ссылок не нашёл.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, handle_forward))
    app.run_polling()

if __name__ == "__main__":
    main()
