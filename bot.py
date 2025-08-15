import json
import requests
from fastapi import FastAPI, Request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ===== إعدادات البوت =====
TOKEN = "6217434623:AAE2uWujlffjWAG_pZuAIsNigRcSJFJmhuY"
ADMIN_ID = 5581457665
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = f"https://boteleinsta.onrender.com{WEBHOOK_PATH}"

# ===== FastAPI =====
app = FastAPI()

# ===== تطبيق البوت =====
bot_app = Application.builder().token(TOKEN).build()

# ===== تحميل أو إنشاء ملف الحسابات =====
def load_accounts():
    try:
        with open("accounts.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"instagram": [], "telegram": []}

def save_accounts(data):
    with open("accounts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

accounts_data = load_accounts()

# ===== لوحة المالك =====
def main_menu():
    keyboard = []

    if accounts_data["instagram"]:
        keyboard.append([InlineKeyboardButton("📸 حسابات إنستغرام 📸", callback_data="title_insta")])
        for acc in accounts_data["instagram"]:
            keyboard.append([InlineKeyboardButton(acc, callback_data=f"insta_{acc}")])

    if accounts_data["telegram"]:
        keyboard.append([InlineKeyboardButton("💬 حسابات تيليجرام 💬", callback_data="title_tg")])
        for acc in accounts_data["telegram"]:
            keyboard.append([InlineKeyboardButton(acc, callback_data=f"tg_{acc}")])

    keyboard.append([InlineKeyboardButton("⚙️ الإعدادات", callback_data="settings")])
    keyboard.append([InlineKeyboardButton("ℹ️ المساعدة", callback_data="help")])
    return InlineKeyboardMarkup(keyboard)

# ===== رسالة توقف البوت للمستخدمين =====
def stopped_message():
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 تواصل مع المالك", url="https://t.me/e2E12")]
    ])
    return "⛔😂 البوت متوقف للأبـد", keyboard

# ===== أمر /start =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        await update.message.reply_text("👋 أهلاً بك يا Batman! اختر ما يحلو لك🩵💎:", reply_markup=main_menu())
    else:
        text, keyboard = stopped_message()
        await update.message.reply_text(text, reply_markup=keyboard)

# ===== أوامر إضافة وحذف الحسابات =====
async def add_insta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الحساب بعد الأمر.")
        return
    acc = context.args[0]
    if acc not in accounts_data["instagram"]:
        accounts_data["instagram"].append(acc)
        save_accounts(accounts_data)
        await update.message.reply_text(f"✅ تمت إضافة حساب إنستغرام: {acc}")
    else:
        await update.message.reply_text("⚠️ الحساب موجود بالفعل.")

async def remove_insta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الحساب بعد الأمر.")
        return
    acc = context.args[0]
    if acc in accounts_data["instagram"]:
        accounts_data["instagram"].remove(acc)
        save_accounts(accounts_data)
        await update.message.reply_text(f"🗑️ تم حذف حساب إنستغرام: {acc}")
    else:
        await update.message.reply_text("⚠️ الحساب غير موجود.")

async def add_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الحساب بعد الأمر.")
        return
    acc = context.args[0]
    if acc not in accounts_data["telegram"]:
        accounts_data["telegram"].append(acc)
        save_accounts(accounts_data)
        await update.message.reply_text(f"✅ تمت إضافة حساب تيليجرام: {acc}")
    else:
        await update.message.reply_text("⚠️ الحساب موجود بالفعل.")

async def remove_tg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الحساب بعد الأمر.")
        return
    acc = context.args[0]
    if acc in accounts_data["telegram"]:
        accounts_data["telegram"].remove(acc)
        save_accounts(accounts_data)
        await update.message.reply_text(f"🗑️ تم حذف حساب تيليجرام: {acc}")
    else:
        await update.message.reply_text("⚠️ الحساب غير موجود.")

# ===== الرد على أزرار المالك =====
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        text, keyboard = stopped_message()
        await query.edit_message_text(text, reply_markup=keyboard)
        return

    data = query.data
    if data.startswith("insta_"):
        account = data.replace("insta_", "")
        await query.edit_message_text(f"📸 إدارة حساب إنستغرام: {account}", reply_markup=main_menu())
    elif data.startswith("tg_"):
        account = data.replace("tg_", "")
        await query.edit_message_text(f"💬 إدارة حساب تيليجرام: {account}", reply_markup=main_menu())
    elif data == "settings":
        await query.edit_message_text("⚙️ إعدادات البوت:\n- اللغة: العربية\n- الإشعارات: مفعلة", reply_markup=main_menu())
    elif data == "help":
        await query.edit_message_text("ℹ️ المساعدة:\n- استخدم الأزرار للتحكم في حساباتك😂.", reply_markup=main_menu())
    else:
        await query.edit_message_text("📋 القائمة الرئيسية:", reply_markup=main_menu())

# ===== استقبال Webhook =====
@app.post(WEBHOOK_PATH)
async def webhook_handler(request: Request):
    data = await request.json()
    update = Update.de_json(data, bot_app.bot)
    await bot_app.process_update(update)
    return {"status": "ok"}

# ===== ضبط Webhook عند التشغيل =====
@app.on_event("startup")
async def set_webhook():
    resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo").json()
    current_url = resp.get("result", {}).get("url", "")
    if current_url != WEBHOOK_URL:
        requests.get(f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}")
        print(f"✅ Webhook تم ضبطه على {WEBHOOK_URL}")
    else:
        print(f"✅ Webhook مضبوط مسبقًا على {WEBHOOK_URL}")

# ===== إضافة Handlers =====
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("add_insta", add_insta))
bot_app.add_handler(CommandHandler("remove_insta", remove_insta))
bot_app.add_handler(CommandHandler("add_tg", add_tg))
bot_app.add_handler(CommandHandler("remove_tg", remove_tg))
bot_app.add_handler(CallbackQueryHandler(button_handler))
