# ================================================================================
# GLOBALSENTINEL V3: AUTONOMOUS TRADING AGENT - NODE 4 & 5
# ================================================================================
# Author: Kaggle Capstone Project Participant
# Description: Fully autonomous algorithmic trading agent that evaluates market 
#              states (observations), scores available actions using heuristics, 
#              and auto-executes trades under dynamic temporal compliance rules.
# ================================================================================
import datetime
import sys
import os
import random
import urllib.request
import json
from collections import defaultdict
# ==============================================================================
# OPTIONAL SYSTEM DEPENDENCIES & COMPATIBILITY LAYER
# ==============================================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    HAS_COLORAMA = True
except ImportError:
    HAS_COLORAMA = False
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
# Reconfigure stdout to support UTF-8 on Windows consoles to print flags and Urdu/Arabic text without crashing
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
# ==============================================================================
# TERMINAL TEXT STYLING UTILITY (FALLS BACK GRACEFULLY TO PLAIN TEXT)
# ==============================================================================
class ColorStyle:
    def __init__(self):
        self.GREEN = Fore.GREEN if HAS_COLORAMA else ""
        self.RED = Fore.RED if HAS_COLORAMA else ""
        self.YELLOW = Fore.YELLOW if HAS_COLORAMA else ""
        self.BLUE = Fore.BLUE if HAS_COLORAMA else ""
        self.CYAN = Fore.CYAN if HAS_COLORAMA else ""
        self.MAGENTA = Fore.MAGENTA if HAS_COLORAMA else ""
        self.WHITE = Fore.WHITE if HAS_COLORAMA else ""
        self.RESET = Style.RESET_ALL if HAS_COLORAMA else ""
        self.BRIGHT = Style.BRIGHT if HAS_COLORAMA else ""
C = ColorStyle()
# Multilingual Start Mappings
START_MAPPINGS = {
    "en": "Welcome. Global Sentinel Autonomous Engine is online.",
    "ur": "خوش آمدید۔ گلوبل سینٹینل خود مختار انجن آن لائن ہے۔",
    "ar": "مرحباً. محرك غلوبال سينتينيل الذاتي متصل الآن.",
    "de": "Willkommen. Die Global Sentinel Autonomous Engine ist online.",
    "ru": "Добро пожаловать. Движок Global Sentinel Autonomous v seti.",
    "es": "Bienvenido. El motor autónomo Global Sentinel está en línea.",
    "sw": "Karibu. Injini ya Autonomous Global Sentinel iko mtandaoni.",
    "zh": "欢迎。Global Sentinel 自主引擎已上线。",
    "tr": "Hoş geldiniz. Global Sentinel Otonom Motoru çevrimiçi."
}
# Multilingual System Disclaimer Mappings (English and Urdu)
DISCLAIMERS = {
    "Rule_A": {
        "en": "⚠️ Markets are closed for the weekend. Rates reflect last Friday closing prices.",
        "ur": "⚠️ مارکیٹس اختتامِ ہفتہ کی وجہ سے بند ہیں۔ ریٹس گزشتہ جمعہ کے اختتامی قیمتوں کو ظاہر کرتے ہیں۔"
    },
    "Rule_B": {
        "en": "⚠️ Crypto markets operate 24/7. Assets are highly volatile. Monitor parameters.",
        "ur": "⚠️ کرپٹو مارکیٹس 24/7 فعال رہتی ہیں۔ اثاثے شدید اتار چڑھاؤ کے تابع ہیں۔"
    },
    "Rule_C": {
        "en": "⚠️ Geopolitical event registered on weekend. Structural market volatility will translate to Forex and Stocks upon Monday opening bells.",
        "ur": "⚠️ اختتامِ ہفتہ پر جیو پولیٹیکل واقعہ رجسٹر ہوا ہے۔ مارکیٹ کا یہ اتار چڑھاؤ پیر کو فاریکس اور اسٹاکس اوپن ہونے پر منتقل ہوگا۔"
    }
}
# 25 Fiat Corridors Mock Database (Fallback)
FIAT_CORRIDORS = [
    ("USD/EUR", "🇺🇸 / 🇪🇺", 0.92), ("USD/GBP", "🇺🇸 / 🇬🇧", 0.79), ("USD/JPY", "🇺🇸 / 🇯🇵", 156.40),
    ("USD/CAD", "🇺🇸 / 🇨🇦", 1.37), ("USD/AUD", "🇺🇸 / 🇦🇺", 1.51), ("USD/CHF", "🇺🇸 / 🇨🇭", 0.90),
    ("USD/CNY", "🇺🇸 / 🇨🇳", 7.24), ("USD/INR", "🇺🇸 / 🇮🇳", 83.50), ("USD/MXN", "🇺🇸 / 🇲🇽", 18.45),
    ("USD/ZAR", "🇺🇸 / 🇿🇦", 18.20), ("USD/BRL", "🇺🇸 / 🇧🇷", 5.40), ("USD/SGD", "🇺🇸 / 🇸🇬", 1.35),
    ("USD/NZD", "🇺🇸 / 🇳🇿", 1.63), ("USD/HKD", "🇺🇸 / 🇭🇰", 7.81), ("USD/SEK", "🇺🇸 / 🇸🇪", 10.50),
    ("USD/NOK", "🇺🇸 / 🇳🇴", 10.60), ("USD/KRW", "🇺🇸 / 🇰🇷", 1385.00), ("USD/TRY", "🇺🇸 / 🇹🇷", 32.80),
    ("USD/SAR", "🇺🇸 / 🇸🇦", 3.75), ("USD/AED", "🇺🇸 / 🇦🇪", 3.67), ("USD/EGP", "🇺🇸 / 🇪🇬", 47.80),
    ("USD/ARS", "🇺🇸 / 🇦🇷", 910.00), ("USD/PKR", "🇺🇸 / 🇵🇰", 278.50), ("USD/RUB", "🇺🇸 / 🇷🇺", 89.20),
    ("USD/THB", "🇺🇸 / 🇹🇭", 36.70)
]
# Audio captions standard templates
AUDIO_CAPTIONS = {
    "/start": "Welcome. Global Sentinel Autonomous Engine is online.",
    "/forex": "The Forex data list is extensive. Please review live rates directly on the terminal screen logs.",
    "/crypto": "Crypto matrix is active. Bitcoin is currently at {btc} USD and Ethereum is at {eth} USD.",
    "/stock": "Global market index data is active. Review screen logs for performance metrics.",
    "/intel": "Strategic intelligence active. Spot Gold is currently trading at {gold} USD and Crude Oil is at {oil} USD.",
    "/news": "News volume filter is active. Terminal system nodes are isolating geopolitical intelligence.",
    "$tech": "Advanced technology matrix is active. Check hardware supply chain and chip manufacturing logs.",
    "$shadow": "Shadow liquidity logs are active. Institutional block trade data is displayed.",
    "$shock": "⚠️ Critical market anomaly registered. Geopolitical shock freeze active. Strategic risk analysis initiated."
}
# ==============================================================================
# OBJECT-ORIENTED AGENT DESIGN & DECISION METRICS (Inspired by Kaggle Simulator)
# ==============================================================================
class TradingObservation:
    """Structure encapsulating full market state at the execution timestamp."""
    def __init__(self, sim_date=None, command="/crypto"):
        self.timestamp = sim_date if sim_date else datetime.datetime.now()
        self.day_name = self.timestamp.strftime("%A")
        self.command = command
        self.market_status, self.enforced_rule = self.get_temporal_status()
        self.rates = {}
        self.risk_factor = 1.0  # Normalized multiplier for volatility calculation
    def get_temporal_status(self):
        """Node 4 Temporal Trigger Engine validation."""
        is_weekend = self.day_name in ["Saturday", "Sunday"]
        if is_weekend:
            if self.command in ["/forex", "/stock", "/intel", "/news"]:
                return "closed_weekend", "Rule_A"
            elif self.command == "/crypto":
                return "crypto_24_7", "Rule_B"
            elif self.command == "$shock":
                return "shock_weekend_freeze", "Rule_C"
            else:
                return "closed_weekend", None
        else:
            if self.command == "/crypto":
                return "crypto_24_7", "Rule_B"
            else:
                return "open", None
class Portfolio:
    """Class representing the agent's asset holdings."""
    def __init__(self, cash_usd=10000.0):
        self.cash = cash_usd
        # Holdings dictionary mapping Asset Name -> Quantity held
        self.holdings = defaultdict(float)
    def display(self):
        print(f"\n{C.CYAN}--- PORTFOLIO BALANCE LOG ---{C.RESET}")
        print(f"  💵 Cash Reserve  : ${self.cash:,.2f} USD")
        for asset, qty in self.holdings.items():
            if qty > 0:
                print(f"  🪙 {asset.ljust(13)}: {qty:.4f}")
class TradeAction:
    """Represents a scored transaction decision."""
    def __init__(self, action_type, asset, target_qty, price, score=0):
        self.type = action_type # "BUY", "SELL", "HOLD", "HEDGE"
        self.asset = asset
        self.qty = target_qty
        self.price = price
        self.score = score
    def __repr__(self):
        return f"{self.type} {self.qty:.4f} {self.asset} @ ${self.price:.2f} (Utility Score: {self.score})"
# ==============================================================================
# HEURISTIC UTILITY SCORING ENGINE
# ==============================================================================
def action_utility_score(action: TradeAction, obs: TradingObservation, portfolio: Portfolio) -> int:
    """
    Heuristical valuation model to grade a potential trade action.
    Inspired by 'pokemon_score' design parameters.
    """
    score = 1000 # Baseline score
    
    # 1. Enforce temporal compliance penalties
    if obs.market_status == "closed_weekend":
        if action.asset in ["EUR", "GBP", "JPY", "CAD", "AUD", "GOLD", "OIL"]:
            # Extreme penalty: Do not trade closed standard assets during weekends
            score -= 10000
    
    if obs.market_status == "shock_weekend_freeze":
        if action.type == "HEDGE":
            # High priority: Hedge exposure immediately during anomaly states
            score += 8000
        elif action.type == "BUY":
            score -= 3000  # Deprioritize purchases during freeze
            
    # 2. Evaluate Portfolio metrics
    if action.type == "BUY":
        cost = action.price * action.qty
        if cost > portfolio.cash:
            score -= 20000  # Disallow unaffordable trades
        else:
            # Prefer purchasing assets when holding cash reserves
            score += int((portfolio.cash / 10000.0) * 100)
            
    elif action.type == "SELL":
        if portfolio.holdings[action.asset] < action.qty:
            score -= 20000  # Disallow short selling beyond holdings
        else:
            # Encourage profit taking if volatility increases
            score += int(obs.risk_factor * 150)
    # 3. Asset Specific Priorities (Rule B override)
    if action.asset in ["BTC", "ETH"]:
        score += 500  # Base utility preference for continuous digital assets
        if obs.market_status == "crypto_24_7":
            score += 1500  # Boost scoring during weekends where options are restricted
            
    return score
# ==============================================================================
# CORE EXECUTION LOOP (THE AUTONOMOUS AGENT)
# ==============================================================================
def fetch_market_rates():
    """Fetches real-time market pricing via Coinbase & Open Exchange Rates APIs."""
    rates = {"BTC": 65000.0, "ETH": 3500.0, "EUR": 0.92, "GBP": 0.79, "JPY": 156.4, "GOLD": 2350.0}
    
    # Live Coinbase crypto query
    try:
        req_btc = urllib.request.Request("https://api.coinbase.com/v2/prices/BTC-USD/spot", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_btc, timeout=3) as res:
            rates["BTC"] = float(json.loads(res.read().decode())['data']['amount'])
    except Exception:
        pass
    # Live Forex exchange rate query
    try:
        with urllib.request.urlopen("https://open.er-api.com/v6/latest/USD", timeout=3) as res:
            forex_rates = json.loads(res.read().decode()).get('rates', {})
            for cur in ["EUR", "GBP", "JPY"]:
                if cur in forex_rates:
                    rates[cur] = round(forex_rates[cur], 4)
    except Exception:
        pass
        
    return rates
def execute_autonomous_agent(command="/crypto", target_lang="en", sim_date=None, portfolio=None):
    """
    Main autonomous agent iteration loop. Analyzes observation, scores actions, 
    and commits changes.
    """
    if portfolio is None:
        portfolio = Portfolio()
        # Seed initial portfolio holdings
        portfolio.holdings["BTC"] = 0.05
        portfolio.holdings["EUR"] = 1000.0
    # 1. Capture system state (Observation)
    obs = TradingObservation(sim_date, command)
    obs.rates = fetch_market_rates()
    
    if obs.market_status == "shock_weekend_freeze":
        obs.risk_factor = 2.5
    elif obs.market_status == "crypto_24_7":
        obs.risk_factor = 1.5
    # 2. Declare Invocation status reports
    print("\n" + "="*70)
    print(f"{C.BRIGHT}{C.MAGENTA}GLOBALSENTINEL AUTONOMOUS AGENT DECISION LOG{C.RESET}")
    print(f"{C.WHITE}System Clock  : {C.RESET}{obs.timestamp.strftime('%Y-%m-%d %H:%M:%S')} ({obs.day_name})")
    print(f"{C.WHITE}Input Gate    : {C.RESET}{command}")
    print(f"{C.WHITE}Market Context: {C.RESET}{C.YELLOW if 'weekend' in obs.market_status else C.GREEN}{obs.market_status.upper()}{C.RESET}")
    print(f"{C.WHITE}Risk Multiplier: {C.RESET}{obs.risk_factor}x")
    print("="*70)
    portfolio.display()
    # 3. Generate possible actions options lists
    candidate_options = [
        TradeAction("BUY", "BTC", 0.01, obs.rates["BTC"]),
        TradeAction("BUY", "ETH", 0.1, obs.rates["ETH"]),
        TradeAction("BUY", "EUR", 500, 1.0 / obs.rates["EUR"]),
        TradeAction("SELL", "BTC", 0.02, obs.rates["BTC"]),
        TradeAction("SELL", "EUR", 400, 1.0 / obs.rates["EUR"]),
        TradeAction("HEDGE", "BTC", 0.05, obs.rates["BTC"]), # Hedging strategy option
    ]
    # Evaluate heuristic score for each option
    for action in candidate_options:
        action.score = action_utility_score(action, obs, portfolio)
    # 4. Sorting logic: Choose option in descending order of utility score (autonomous decisions)
    sorted_actions = sorted(candidate_options, key=lambda x: x.score, reverse=True)
    print(f"\n{C.GREEN}--- DECISION MATRIX SCORING METRICS ---{C.RESET}")
    for act in sorted_actions:
        color = C.RED if act.score < 0 else C.GREEN if act.score > 1200 else C.YELLOW
        print(f"  Option: {repr(act)} -> {color}[SCORE: {act.score}]{C.RESET}")
    # 5. Commit top scoring valid decisions (> 0 utility score threshold)
    best_decision = sorted_actions[0]
    execution_msg = ""
    
    if best_decision.score > 0:
        print(f"\n{C.GREEN}✔ [AUTO-EXECUTE] committing highest utility action...{C.RESET}")
        print(f"  ↳ Executing: {best_decision}")
        
        if best_decision.type == "BUY":
            cost = best_decision.price * best_decision.qty
            portfolio.cash -= cost
            portfolio.holdings[best_decision.asset] += best_decision.qty
            execution_msg = f"Autonomous engine committed BUY transaction for {best_decision.qty:.4f} {best_decision.asset}."
        elif best_decision.type == "SELL":
            credit = best_decision.price * best_decision.qty
            portfolio.cash += credit
            portfolio.holdings[best_decision.asset] -= best_decision.qty
            execution_msg = f"Autonomous engine committed SELL transaction for {best_decision.qty:.4f} {best_decision.asset}."
        elif best_decision.type == "HEDGE":
            execution_msg = f"Autonomous engine successfully activated risk HEDGING parameters for {best_decision.asset}."
    else:
        print(f"\n{C.YELLOW}⚠ [HOLD STATE] No valid trading utility options satisfy threshold metrics.{C.RESET}")
        execution_msg = "Market parameters indicate execution lock. Holding current portfolios."
    # Updated portfolio metrics
    portfolio.display()
    # 6. Apply Node 5 translation rules & disclaimers
    disclaimer_text = ""
    if obs.enforced_rule:
        dis_lang = target_lang if target_lang in ["en", "ur"] else "en"
        disclaimer_text = DISCLAIMERS[obs.enforced_rule].get(dis_lang, DISCLAIMERS[obs.enforced_rule]["en"])
    # Node 5 synthesis text formatting
    audio_base = AUDIO_CAPTIONS.get(command, "Autonomous cycle run complete.")
    if "{btc}" in audio_base:
        audio_base = audio_base.format(btc=obs.rates["BTC"], eth=obs.rates["ETH"])
    elif "{gold}" in audio_base:
        audio_base = audio_base.format(gold=obs.rates["GOLD"], oil=obs.rates["OIL"])
    # Synthesize base report and update action report
    synthesis_payload = f"{START_MAPPINGS.get(target_lang, START_MAPPINGS['en'])} {audio_base} {execution_msg}"
    if disclaimer_text:
        synthesis_payload += f" {disclaimer_text}"
    play_audio_payload(synthesis_payload, lang=target_lang)
def play_audio_payload(text, lang="en"):
    """Node 5 Text-To-Speech audio synthesizer engine."""
    print(f"\n{C.CYAN}--- NODE 5: AUDIO BROADCAST ENGINE ---{C.RESET}")
    print(f"{C.WHITE}Language:{C.RESET} {lang.upper()}")
    print(f"{C.WHITE}Audio Script:{C.RESET} \"{text}\"")
    
    if HAS_GTTS:
        try:
            filename = f"globalsentinel_audio_{lang}.mp3"
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(filename)
            print(f"{C.GREEN}✔ Audio compiled and saved successfully to {filename}{C.RESET}")
        except Exception as e:
            print(f"{C.YELLOW}⚠ Audio synthesis error: {e}{C.RESET}")
    else:
        print(f"{C.YELLOW}⚠ gTTS not detected. Run 'pip install gTTS' for audio compiling.{C.RESET}")
if __name__ == "__main__":
    print(f"{C.BRIGHT}{C.GREEN}Initializing GlobalSentinel Autonomous Trading Agent...{C.RESET}")
    
    # Test Scenario 1: Weekday trading scenario (USD/EUR, Crypto, etc. allowed)
    # June 29, 2026 is a Monday
    monday = datetime.datetime(2026, 6, 29, 12, 0, 0)
    execute_autonomous_agent("/crypto", "en", monday)
    
    # Test Scenario 2: Weekend forex lock scenario (Rule A blocks EUR, shifts focus to Crypto)
    # June 27, 2026 is a Saturday
    saturday = datetime.datetime(2026, 6, 27, 12, 0, 0)
    execute_autonomous_agent("/forex", "en", saturday)
    # Test Scenario 3: Weekend geopolitical shock scenario (Rule C prioritizes HEDGE)
    execute_autonomous_agent("$shock", "ur", saturday)
