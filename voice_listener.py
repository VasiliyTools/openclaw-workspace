import logging
import os
import json
import tempfile
import subprocess
from vosk import Model, KaldiRecognizer
import wave
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN env var")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "vosk-model")
if not os.path.isdir(MODEL_PATH):
    raise RuntimeError(f"Vosk model not found at {MODEL_PATH}")

logger.info("Loading Vosk model...")
model = Model(MODEL_PATH)
logger.info("Model loaded")

COMMAND_LOG = os.path.join(os.path.dirname(__file__), "commands.log")

def recognize_speech(wav_path: str) -> str:
    wf = wave.open(wav_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
        raise ValueError("WAV file must be 16kHz mono 16-bit")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            pass
    res = json.loads(rec.FinalResult())
    return res.get("text", "").strip()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь голосовое сообщение.")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    if not voice:
        return
    file = await context.bot.get_file(voice.file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as ogg_file:
        ogg_path = ogg_file.name
        await file.download_to_drive(ogg_path)
    wav_path = ogg_path.replace(".ogg", ".wav")
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", ogg_path,
            "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le",
            wav_path
        ], check=True, capture_output=True)
        text = recognize_speech(wav_path)
        if not text:
            await update.message.reply_text("Не удалось распознать речь.")
            return
        keyboard = [
            [
                InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm:{text}"),
                InlineKeyboardButton("❌ Отклонить", callback_data=f"reject:{text}")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Вы сказали: «{text}». Все верно?",
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.exception("Error processing voice")
        await update.message.reply_text(f"Ошибка: {e}")
    finally:
        try:
            os.remove(ogg_path)
            os.remove(wav_path)
        except OSError:
            pass

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("confirm:"):
        text = data.split(":", 1)[1]
        with open(COMMAND_LOG, "a", encoding="utf-8") as f:
            f.write(f"{update.effective_user.id} | {text}\n")
        await query.edit_message_text(text=f"✅ Выполнено: {text}")
    elif data.startswith("reject:"):
        text = data.split(":", 1)[1]
        await query.edit_message_text(text=f"❌ Игнорировано: {text}")

def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(CallbackQueryHandler(button))
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == "__main__":
    main()
