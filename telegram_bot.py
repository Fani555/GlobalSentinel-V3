# ================================================================================
# GLOBALSENTINEL V3: LIVE TELEGRAM BOT COMPLIANCE & DECISION ENGINE
# ================================================================================
# Author: Kaggle Capstone Project Participant
# Description: Wrapper to run the Autonomous GlobalSentinel V3 Trading Agent
#              as a live Telegram Bot. Serves text metrics and synthesizes audio 
#              voice notes dynamically on Telegram. Includes a lightweight HTTP
#              keep-alive port binding for free Render web service hosting.
# ================================================================================
import os
import sys
import datetime
import threading
import http.server
import socketserver
import telebot
from autonomous_sentinel import execute_autonomous_agent, fetch_market_rates, TradingObservation, Portfolio, sorted_actions, C, DISCLAIMERS, START_MAPPINGS, AUDIO_CAPTIONS
# ==============================================================================
# CONFIGURATION & INITIALIZATION
# ==============================================================================
# Access Telegram Token from environment variables (configured on Render dashboard)
TOKEN = os.environ.get("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
bot = telebot.TeleBot(TOKEN)
# Initialize a persistent mock portfolio for the live bot session
bot_portfolio = Portfolio(cash_usd=10000.0)
bot_portfolio.holdings["BTC"] = 0.05
bot_portfolio.holdings["EUR"] = 1000.0
print("GlobalSentinel Telegram Bot initialization complete.")
# ==============================================================================
# TELEGRAM BOT COMMAND HANDLERS
# ==============================================================================
def format_telegram_report(command, lang, simulated_date=None):
    """Executes the autonomous agent logic and formats the output cleanly for Telegram."""
    # Temporarily capture stdout to route agent logs to text
    from io import StringIO
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    
    # Run the autonomous engine logic
    execute_autonomous_agent(command=command, target_lang=lang, sim_date=sim_date, portfolio=bot_portfolio)
    
    sys.stdout = old_stdout
    raw_logs = mystdout.getvalue()
    
    # Clean ANSI terminal color escape codes for clean Telegram chat markdown
    for color_tag in [C.GREEN, C.RED, C.YELLOW, C.BLUE, C.CYAN, C.MAGENTA, C.WHITE, C.RESET, C.BRIGHT]:
        if color_tag:
            raw_logs = raw_logs.replace(color_tag, "")
            
    return raw_logs
def get_target_lang(message):
    """Helper to detect language flags or fall back to English."""
    text = message.text.lower()
    for lang in ["ur", "ar", "de", "ru", "es", "sw", "zh", "tr"]:
        if f" {lang}" in text or text.endswith(f"_{lang}"):
            return lang
    return "en"
@bot.message_handler(commands=['start'])
def handle_start(message):
    lang = get_target_lang(message)
    welcome_text = format_telegram_report("/start", lang)
    bot.reply_to(message, welcome_text)
@bot.message_handler(commands=['forex', 'crypto', 'stock', 'intel', 'news'])
def handle_standard_commands(message):
    command = "/" + message.text.split()[0].replace("/", "")
    lang = get_target_lang(message)
    
    # Parse simulated weekend if keyword "weekend" is typed
    sim_date = None
    if "weekend" in message.text.lower():
        # Set to simulated Saturday (June 27, 2026)
        sim_date = datetime.datetime(2026, 6, 27, 12, 0, 0)
        
    report = format_telegram_report(command, lang, sim_date)
    bot.send_message(message.chat.id, f"```\n{report}\n```", parse_mode="Markdown")
    # Node 5: Audio voice note transmission
    audio_path = f"globalsentinel_audio_{lang}.mp3"
    if os.path.exists(audio_path):
        try:
            with open(audio_path, 'rb') as audio_file:
                bot.send_voice(message.chat.id, audio_file, caption=f"Node 5 Audio Broadcast ({lang.upper()})")
        except Exception as e:
            print(f"Error sending audio: {e}")
@bot.message_handler(commands=['tech', 'shadow', 'shock'])
def handle_shadow_commands(message):
    command = "$" + message.text.split()[0].replace("/", "").replace("$", "")
    lang = get_target_lang(message)
    
    sim_date = None
    if "weekend" in message.text.lower():
        sim_date = datetime.datetime(2026, 6, 27, 12, 0, 0)
    report = format_telegram_report(command, lang, sim_date)
    bot.send_message(message.chat.id, f"```\n{report}\n```", parse_mode="Markdown")
    
    audio_path = f"globalsentinel_audio_{lang}.mp3"
    if os.path.exists(audio_path):
        try:
            with open(audio_path, 'rb') as audio_file:
                bot.send_voice(message.chat.id, audio_file)
        except Exception as e:
            print(f"Error sending audio: {e}")
# ==============================================================================
# KEEP-ALIVE HTTP SERVER FOR RENDER COMPLIANCE
# ==============================================================================
class KeepAliveHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"GlobalSentinel Telegram Bot is active and running.")
def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    with socketserver.TCPServer(("", port), KeepAliveHandler) as httpd:
        print(f"Keep-alive web server online on port {port}")
        httpd.serve_forever()
if __name__ == "__main__":
    if TOKEN == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        print("ERROR: Please configure the TELEGRAM_TOKEN environment variable.")
        sys.exit(1)
        
    # Start Keep-Alive Server in a daemon thread so Render port binding doesn't timeout
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()
    print("Telegram polling engine initiated...")
    bot.infinity_polling()
