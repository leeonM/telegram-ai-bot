import telebot
import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


gemini_api_key = os.getenv("GEMINI_API_KEY")
telegram_token = os.getenv("TELEGRAM_TOKEN")


# Initialize the Telegram bot
bot = telebot.TeleBot(telegram_token, parse_mode=None)

# Configure the API key for Gemini
genai.configure(api_key=gemini_api_key)

def read_local_excel(file_path):
    """Read the local Excel file and return its content."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    excel_data = pd.ExcelFile(file_path)
    print(f"Loaded file '{file_path}' with sheet names: {excel_data.sheet_names}")
    return excel_data

def generate_gemini_response(chat_session, user_message, excel_data):
    """Generate a response using Gemini and include information from the Excel file if relevant."""
    # Send the user's message to Gemini and get the response
    response = chat_session.send_message(user_message)
    
    # Check if any sheet names (city names) are mentioned in the response
    response_text = response.text
    
    return response_text

# Define the path to the local Excel file
local_excel_path = "city-motives.xlsx"

# Read the local Excel file
excel_data = read_local_excel(local_excel_path)

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

# Initialize the Gemini model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="You are a friendly assistant who works as a nightlife tour guide for black events in different cities. Your job is to ask the user what they would like to do. When the user greets you, ask them what they would like to do and in which city. When you get a response, review the attached google sheet, specifically in the tab for the city they have specified, and provide some responses depending on what they're looking for, including the Instagram handle for each response. If there's nothing that matches in the sheet, just tell them you don't know what's available but will make sure to find out for next time.",
)

# Since files are now local, we don't need to wait for file processing
chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": ["hi"],
        },
        {
            "role": "model",
            "parts": [
                "Hey there! 👋 I'm your black nightlife tour guide. What are you looking for tonight or this weekend, and which city are you in? 🏙️ \n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "I'm in Paris from Friday to Monday, can you let me know what I can do on Friday night and Saturday evening and night, then let me know what options I have for the Sunday daytime",
            ],
        },
        {
            "role": "model",
            "parts": [
                "Okay, awesome! Paris sounds like a great choice for some Black orientated nightlife. 🇫🇷 Let's see what we can find for you. \n\n**For Friday night**\n\nYou have a few options:\n\n* **Deflower** is a great choice for a Friday night, especially if you're just passing by. It can get crowded, but the energy is always good.\n* **Cova** is another bottle service club that's popular on Fridays. It's known for its luxurious decor and lively atmosphere, similar to Tape London.\n* **L'Arc** is a good option if you're looking for a club with a retractable roof. It can get very table-centric, but the music is good.\n* **Kith/Sadelles** is a great spot for breakfast on Friday morning if you're looking for a more casual start to the day. \n\n**For Saturday evening and night:**\n\n* **Boum Boum** is a good choice if you're looking for a club that plays more hip hop. \n* **Cova** is also a popular option on Saturdays, with a similar vibe to Friday.\n* **L'Arc** is another good choice for Saturday night, especially if you're looking for a club with a retractable roof.\n* **Gypsi Motel** is hosting their \"Gypsi Twister\" event on Sunday night, featuring hip hop and afrobeats. \n\n**For Sunday daytime:**\n\n* **Sunday Groove** is a great choice for a casual Sunday day party with a terrace setting.\n* **Poppin events** is hosting a day party at Bluue Paris, a club with a swimming pool, on Saturdays.\n\n**Let me know which of these options sounds most appealing to you, and I can give you more information about specific events, timings, and how to book.** \n\n",
            ],
        },
    ]
)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    # Use the existing chat history to generate a response
    response_text = generate_gemini_response(chat_session, message.text, excel_data)
    bot.reply_to(message, response_text)

bot.infinity_polling()