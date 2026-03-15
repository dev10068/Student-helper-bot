from telebot import types
import google.generativeai as genai
import os

# --- CONFIGURATION ---
# Yeh keys hum Koyeb ki settings (Environment Variables) mein daalenge
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# AI Setup
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# User ki preferences yaad rakhne ke liye temporary memory
user_prefs = {}

# --- 1. START COMMAND ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    btn1 = types.KeyboardButton('English 🇬🇧')
    btn2 = types.KeyboardButton('Hindi 🇮🇳')
    btn3 = types.KeyboardButton('Hinglish 🇮🇳🇬🇧')
    
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, "Welcome! Please select your language / अपनी भाषा चुनें:", reply_markup=markup)

# --- 2. LANGUAGE SELECTION ---
@bot.message_handler(func=lambda message: message.text in ['English 🇬🇧', 'Hindi 🇮🇳', 'Hinglish 🇮🇳🇬🇧'])
def set_language(message):
    lang = message.text
    user_prefs[message.chat.id] = {'lang': lang}
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    # Language ke hisab se buttons dikhana
    if lang == 'English 🇬🇧':
        markup.add('Math ➕', 'Chemistry 🧪', 'Physics 🍎')
        bot.send_message(message.chat.id, "Great! Now select your Subject:", reply_markup=markup)
    elif lang == 'Hindi 🇮🇳':
        markup.add('गणित ➕', 'रसायन विज्ञान 🧪', 'भौतिक विज्ञान 🍎')
        bot.send_message(message.chat.id, "Uttam! Ab apna Vishay (Subject) chunein:", reply_markup=markup)
    else: # Hinglish
        markup.add('Math ➕', 'Chemistry 🧪', 'Physics 🍎')
        bot.send_message(message.chat.id, "Perfect! Ab apna Subject select karein:", reply_markup=markup)

# --- 3. SUBJECT SELECTION ---
@bot.message_handler(func=lambda message: message.text in ['Math ➕', 'Chemistry 🧪', 'Physics 🍎', 'गणित ➕', 'रसायन विज्ञान 🧪', 'भौतिक विज्ञान 🍎'])
def set_subject(message):
    chat_id = message.chat.id
    if chat_id in user_prefs:
        user_prefs[chat_id]['subject'] = message.text
        lang = user_prefs[chat_id]['lang']
        
        # Confirmation message in selected language
        if lang == 'English 🇬🇧':
            bot.send_message(chat_id, f"I am ready for {message.text}. Send your question now (Text only).")
        elif lang == 'Hindi 🇮🇳':
            bot.send_message(chat_id, f"Main {message.text} ke liye taiyar hoon. Ab apna sawal bhejein.")
        else:
            bot.send_message(chat_id, f"Main {message.text} ke liye ready hoon. Ab apna question bhejein.")

# --- 4. SOLVING THE QUESTION ---
@bot.message_handler(func=lambda message: True)
def solve_question(message):
    chat_id = message.chat.id
    
    # Check if user has completed the setup
    if chat_id not in user_prefs or 'subject' not in user_prefs[chat_id]:
        bot.reply_to(message, "Please use /start to select Language and Subject first!")
        return

    lang = user_prefs[chat_id]['lang']
    subj = user_prefs[chat_id]['subject']

    try:
        # Prompt for the AI
        prompt = (f"You are an expert teacher. Solve this {subj} question for a student. "
                  f"Language: {lang}. "
                  f"Style: Keep it VERY BASIC, simple, and step-by-step for a beginner. "
                  f"Question: {message.text}")
        
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
        
    except Exception as e:
        bot.reply_to(message, "Sorry, I am having trouble connecting to my brain. Please try again in 1 minute!")

# --- START BOT ---
print("Bot is running...")
bot.polling()
