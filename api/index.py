from flask import Flask, request, jsonify
import logging
import subprocess
import threading

app = Flask(__name__)

# إعدادات التصحيح
logging.basicConfig(level=logging.DEBUG)

# وظيفة لتشغيل البوت في عملية منفصلة
def run_bot():
    bot_code = '''
import telebot
from telebot import types
import requests

# استبدل 'YOUR_BOT_TOKEN' برمز البوت الخاص بك
BOT_TOKEN = '7955976147:AAEeuL9uUrFFGbfCbxlHVrtCMUNncPvs3k8'
bot = telebot.TeleBot(BOT_TOKEN)

# قائمة بالأعضاء المكتمين
muted_users = set()

# قائمة بالأعضاء المطرودين
banned_users = set()

# قفل الشات
chat_locked = False

# وظيفة للتحقق من صلاحيات المستخدم
def is_admin(chat_id, user_id):
    admins = bot.get_chat_administrators(chat_id)
    for admin in admins:
        if admin.user.id == user_id:
            return True
    return False

# وظيفة للتحقق من أن المستخدم ليس مالك البوت
def is_not_bot_owner(user_id):
    return user_id != bot.get_me().id

# وظيفة للتحقق من أن المستخدم ليس مالك المجموعة
def is_not_group_owner(chat_id, user_id):
    chat = bot.get_chat(chat_id)
    return user_id != chat.id

# وظيفة لإرسال تفاعل على الرسالة
def send_reaction(chat_id, message_id, emoji, is_big=False):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMessageReaction"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reaction": [{"type": "emoji", "emoji": emoji}],
        "is_big": is_big
    }
    requests.post(url, json=payload)

# بدء البوت
@bot.message_handler(commands=['start'])
def start(message):
    send_reaction(message.chat.id, message.message_id, "👨‍💻", is_big=True)
    bot.reply_to(message, "*مرحبًا! أنا بوت حماية المياو 🐱*\\n*استخدم الأوامر التالية لإدارة المجموعة:*\\n- كتم\\n- طرد\\n- رفع [كلمة]\\n- قفل شات\\n- ألعاب", parse_mode="Markdown")

# ميزة كتم عضو
@bot.message_handler(func=lambda message: "كتم" in message.text)
def mute_user(message):
    if is_admin(message.chat.id, message.from_user.id):
        user_to_mute = message.reply_to_message.from_user
        muted_users.add(user_to_mute.id)
        bot.reply_to(message, f"*تم كتم العضو [{user_to_mute.first_name}](tg://user?id={user_to_mute.id})* 🚫", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*ليس لديك صلاحية للقيام بذلك!* ❌", parse_mode="Markdown")

# ميزة طرد عضو
@bot.message_handler(func=lambda message: "طرد" in message.text)
def ban_user(message):
    if is_admin(message.chat.id, message.from_user.id):
        user_to_ban = message.reply_to_message.from_user
        if is_not_bot_owner(user_to_ban.id) and is_not_group_owner(message.chat.id, user_to_ban.id):
            banned_users.add(user_to_ban.id)
            bot.kick_chat_member(message.chat.id, user_to_ban.id)
            bot.reply_to(message, f"*تم طرد العضو [{user_to_ban.first_name}](tg://user?id={user_to_ban.id})* 🚪", parse_mode="Markdown")
        else:
            bot.reply_to(message, "*لا يمكن طرد هذا العضو!* ❌", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*ليس لديك صلاحية للقيام بذلك!* ❌", parse_mode="Markdown")

# ميزة رفع مع أي كلمة
@bot.message_handler(func=lambda message: "رفع" in message.text)
def promote_with_word(message):
    if is_admin(message.chat.id, message.from_user.id):
        user_to_promote = message.reply_to_message.from_user
        word = message.text.split("رفع")[1].strip()
        bot.reply_to(message, f"*تم رفع [{user_to_promote.first_name}](tg://user?id={user_to_promote.id}) {word}* 😏\\n*وايموجيات مناسبة:* 🤪🐴🐄", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*ليس لديك صلاحية للقيام بذلك!* ❌", parse_mode="Markdown")

# ميزة قفل الشات
@bot.message_handler(func=lambda message: "قفل شات" in message.text)
def lock_chat(message):
    if is_admin(message.chat.id, message.from_user.id):
        global chat_locked
        chat_locked = True
        bot.reply_to(message, "*تم قفل الشات بالكامل يا سيدي ميو 😏*", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*ليس لديك صلاحية للقيام بذلك!* ❌", parse_mode="Markdown")

# ميزة إلغاء قفل الشات
@bot.message_handler(func=lambda message: "فتح شات" in message.text)
def unlock_chat(message):
    if is_admin(message.chat.id, message.from_user.id):
        global chat_locked
        chat_locked = False
        bot.reply_to(message, "*تم فتح الشات يا سيدي ميو 😊*", parse_mode="Markdown")
    else:
        bot.reply_to(message, "*ليس لديك صلاحية للقيام بذلك!* ❌", parse_mode="Markdown")

# ميزة حذف رسائل الأعضاء المكتمين
@bot.message_handler(func=lambda message: message.from_user.id in muted_users)
def delete_muted_user_messages(message):
    bot.delete_message(message.chat.id, message.message_id)

# ميزة حذف رسائل الأعضاء المطرودين
@bot.message_handler(func=lambda message: message.from_user.id in banned_users)
def delete_banned_user_messages(message):
    bot.delete_message(message.chat.id, message.message_id)

# ميزة حذف رسائل الأعضاء عند قفل الشات
@bot.message_handler(func=lambda message: chat_locked and not is_admin(message.chat.id, message.from_user.id))
def delete_messages_when_chat_locked(message):
    bot.delete_message(message.chat.id, message.message_id)

# ميزة الألعاب
@bot.message_handler(func=lambda message: "ألعاب" in message.text)
def games(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎲 لعبة النرد", callback_data="dice"))
    markup.add(types.InlineKeyboardButton("🎯 لعبة السهام", callback_data="dart"))
    bot.reply_to(message, "*اختر لعبة:*", reply_markup=markup, parse_mode="Markdown")

# معالجة الألعاب
@bot.callback_query_handler(func=lambda call: True)
def handle_games(call):
    if call.data == "dice":
        bot.send_dice(call.message.chat.id, emoji="🎲")
    elif call.data == "dart":
        bot.send_dice(call.message.chat.id, emoji="🎯")

# تفاعل البوت مع كل الرسائل
@bot.message_handler(func=lambda message: True)
def react_to_messages(message):
    # تفاعل مع الرسالة
    send_reaction(message.chat.id, message.message_id, "👍")

    # رد على كلمة "عادي"
    if "عادي" in message.text:
        bot.reply_to(message, "*مو عادي!* 😠", parse_mode="Markdown")

    # رد على كلمة "المطور"
    if "المطور" in message.text:
        bot.reply_to(message, "*معلومات المطور:*\\n*الحساب:* [@SE_P_6](https://t.me/SE_P_6)", parse_mode="Markdown")

# بدء تشغيل البوت
bot.polling(none_stop=True)
'''

    # تشغيل البوت في عملية منفصلة
    subprocess.run(["python3", "-c", bot_code])

@app.route('/run-code', methods=['GET'])
def run_code():
    try:
        # تشغيل البوت في خيط منفصل
        bot_thread = threading.Thread(target=run_bot)
        bot_thread.start()

        # إرجاع النتيجة
        return jsonify({'status': 'success', 'message': 'تم تشغيل البوت بنجاح!'})
    except Exception as e:
        logging.error(f'حدث خطأ: {e}')
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
