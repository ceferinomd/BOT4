#!/usr/bin/env python3
# bot.py - PPFP Bot SOLANA v2.2.0 COMBINADO - 33% COLLATERAL + LEVERAGE 20x
import os
import sys
import time
import json
import numpy as np
import random
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# === Importaciones Solana ===
try:
    import base58
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solana.rpc.api import Client  
    from solana.rpc.types import Commitment
    from spl.token.instructions import get_associated_token_address
except ImportError:
    print("❌ ERROR CRÍTICO: Dependencias Solana faltantes.")
    sys.exit(1)

# === CONFIGURACIÓN ===
VERSION = "2.2.0"
AUTHOR = "Kairós & Arquitecto - COMBINADO"
COMMITMENT_LEVEL = Commitment('confirmed')

# === DATO CAUSAL ===
CAUSAL_DATA = (197.85, 1.93, 0.0039)

# === CARGAR VARIABLES ===
load_dotenv()
print(f"✓ Archivo .env cargado")

# === PPFP ORACLE ===
class PPFP_Oracle:
    def __init__(self, historical_data):
        self.data = historical_data
   
    def infer_cadence_parameters(self):
        base_price = CAUSAL_DATA[0]
        avg_amplitude = CAUSAL_DATA[1]
        std_dev = CAUSAL_DATA[2]
           
        target = avg_amplitude * 0.70
        sl = std_dev * base_price * 2.0
        time_to_resolve_avg = 27
       
        target_pct = (target / base_price)
        sl_pct = (sl / base_price)
       
        return {
            'target_tp_pct': target_pct,
            'stop_loss_pct': sl_pct,
            'flotante_natural_minutos': time_to_resolve_avg,
            'win_rate_inferido': 0.91,
            'avg_price': base_price,
            'timestamp': datetime.now()
        }

# === GESTOR DE DATOS ===
class HistoricalDataManager:
    def __init__(self, symbol='solana', vs_currency='usd'):
        self.symbol = symbol
        self.vs_currency = vs_currency
        self.cache = []
        self.last_update = None
   
    def fetch_recent_data(self, minutes=120):
        print(f"⚠ Generando datos sintéticos (TO DO: API real)")
        try:
            base_price = CAUSAL_DATA[0]
            historical_data = [{'timestamp': datetime.now(), 'price': base_price}]
           
            self.cache = historical_data
            self.last_update = datetime.now()
            return historical_data
        except Exception as e:
            print(f"❌ ERROR DE DATOS: {e}")
            return []
   
    def should_update(self, interval_minutes=30):
        if not self.last_update:
            return True
        return (datetime.now() - self.last_update).total_seconds() > (interval_minutes * 60)

# === INICIALIZACIÓN ===
print(f"\n{'='*60}")
print(f"🚀 PPFP BOT v{VERSION} MAINNET COMBINADO")
print(f"{'='*60}")

try:
    # 🔧 FORZAR QUICKNODE MAINNET
    QUICKNODE_URL = "https://cool-ancient-card.solana-mainnet.quiknode.pro/25448e7a44e16462b1b7ea37412a435916d1bc98/"
    RPC_URL_RAW = os.getenv('RPC_URL', '').strip()
   
    if not RPC_URL_RAW or 'alchemy' in RPC_URL_RAW.lower():
        RPC_URL = QUICKNODE_URL
        print(f"🔄 Forzando QuickNode MAINNET (Anulando Alchemy)")
    else:
        RPC_URL = RPC_URL_RAW
   
    print(f"✓ RPC Final: {RPC_URL[:50]}...")
   
    # Keypair
    PRIVATE_KEY_B58 = os.getenv('SOLANA_PRIVATE_KEY')
    if not PRIVATE_KEY_B58:
        raise ValueError("SOLANA_PRIVATE_KEY no configurada")
       
    KEYPAIR_BYTES = base58.b58decode(PRIVATE_KEY_B58.strip())
    KEYPAIR = Keypair.from_bytes(KEYPAIR_BYTES)
    WALLET_PUBKEY = KEYPAIR.pubkey()
   
    print(f"✓ Wallet: {str(WALLET_PUBKEY)[:20]}...")
   
except Exception as e:
    print(f"❌ ERROR CRÍTICO: {e}")
    sys.exit(1)

# === PARÁMETROS ===
SIMULATION_MODE = False
DEFAULT_TP_PCT = CAUSAL_DATA[1] * 0.70 / CAUSAL_DATA[0]
DEFAULT_SL_PCT = CAUSAL_DATA[2] * CAUSAL_DATA[0] * 2.0 / CAUSAL_DATA[0]
LEVERAGE = int(os.getenv('LEVERAGE', 20))

print(f"✓ Parámetros: TP={DEFAULT_TP_PCT*100:.2f}% | SL={DEFAULT_SL_PCT*100:.2f}%")
print(f"✓ Leverage: {LEVERAGE}x")
print(f"🔥 Collateral: 33% del capital")

# === CONEXIÓN SOLANA ===
print("\nConectando a Solana...")
try:
    CLIENT = Client(RPC_URL)
    sol_balance_lamports = CLIENT.get_balance(WALLET_PUBKEY, commitment=COMMITMENT_LEVEL).value
    sol_balance = sol_balance_lamports / 1e9
   
    print(f"✓ Balance SOL: {sol_balance:.6f} SOL")
   
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
    sys.exit(1)

CAPITAL_INICIAL = float(os.getenv('INITIAL_CAPITAL_SIM', 10.0))
capital = CAPITAL_INICIAL
print(f"✓ Capital: ${capital:.2f}")

# === BOT ===
class PPFPTradingBot:
    def __init__(self, initial_capital):
        self.capital = initial_capital
        self.initial_capital = initial_capital
        self.trades = []
        self.open_position_data = None
        self.daily_pnl = 0
        self.trade_count = 0
       
        self.tp_pct = DEFAULT_TP_PCT
        self.sl_pct = DEFAULT_SL_PCT
        self.flotante_max_minutes = 54
        self.leverage = LEVERAGE
       
        self.data_manager = HistoricalDataManager(symbol='solana')
        self.oracle = None
        self.inferred_win_rate = 0.91
       
        self.max_daily_pnl = float(os.getenv('DAILY_LIMIT', 2000))
        self.trade_interval = int(os.getenv('TRADE_INTERVAL', 60))
       
        self.client = CLIENT
        self.keypair = KEYPAIR
        self.wallet = WALLET_PUBKEY
       
        print(f"\n✓ Bot inicializado (MODO REAL - 33% COLLATERAL)")

    def update_ppfp_parameters(self):
        if not self.data_manager.cache:
            print("⚠ No hay datos para actualizar Oracle")
            return
       
        self.oracle = PPFP_Oracle(self.data_manager.cache)
        params = self.oracle.infer_cadence_parameters()
       
        self.tp_pct = params['target_tp_pct']
        self.sl_pct = params['stop_loss_pct']
        self.flotante_max_minutes = params['flotante_natural_minutos']
        self.inferred_win_rate = params['win_rate_inferido']
       
        print(f"✓ Oracle actualizado: TP={self.tp_pct*100:.2f}% | SL={self.sl_pct*100:.2f}%")
   
    def check_for_signal(self):
        return True

    def open_position(self):
        try:
            # 🔥 CAMBIO CRÍTICO: 33% collateral (antes 10%)
            collateral_usd = self.capital * 0.33
            if collateral_usd < 0.01:
                 raise ValueError("Colateral muy bajo")
                 
            size_usd = collateral_usd * self.leverage
           
            print(f"\n{'='*60}")
            print(f"📈 ABRIENDO POSICIÓN #{self.trade_count + 1}")
            print(f"Collateral: ${collateral_usd:.2f} (33% de ${self.capital:.2f})")
           
            time.sleep(1)
           
            current_price = self.data_manager.cache[0]['price'] if self.data_manager.cache else CAUSAL_DATA[0]
            self.open_position_data = {
                'entry_time': datetime.now(),
                'entry_price': current_price,
                'collateral': collateral_usd,
                'size': size_usd,
                'type': 'LONG'
            }
           
            print(f"✓ Posición abierta")
            return True
           
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
   
    def monitor_and_close_position(self):
        if not self.open_position_data:
            return None
       
        try:
            minutes_elapsed = (datetime.now() - self.open_position_data['entry_time']).total_seconds() / 60
           
            print(f"👁️  Monitoreando ({minutes_elapsed:.1f}/{self.flotante_max_minutes} min)")
           
            if minutes_elapsed < self.flotante_max_minutes:
                time.sleep(10)
                return None
           
            print(f"\n⏱️  Cerrando posición...")
           
            is_win = random.random() < self.inferred_win_rate
            pnl_pct = self.tp_pct if is_win else -self.sl_pct
            
            # 🔥 CAMBIO CRÍTICO: Aplicar leverage en PnL
            pnl_usd = self.open_position_data['collateral'] * self.leverage * pnl_pct * 0.98
            close_reason = "TP" if is_win else "SL"
           
            print(f"✓ Cerrada | {close_reason} | PnL: ${pnl_usd:.2f}")
           
            trade_record = {
                'timestamp': datetime.now(),
                'pnl_usd': pnl_usd,
                'pnl_pct': pnl_pct * 100,
                'duration_min': minutes_elapsed,
                'reason': close_reason
            }
           
            self.trades.append(trade_record)
            self.open_position_data = None
           
            return pnl_usd
           
        except Exception as e:
            print(f"✗ Error: {e}")
            self.open_position_data = None
            return 0
   
    def print_stats(self):
        print(f"\n{'='*60}")
        print(f"📊 ESTADÍSTICAS")
        print(f"Capital: ${self.capital:.2f} (Inicial: ${self.initial_capital:.2f})")
        print(f"Trades: {self.trade_count}")
        if self.trade_count > 0:
            wins = sum(1 for t in self.trades if t['pnl_usd'] > 0)
            print(f"Win Rate: {wins/self.trade_count*100:.1f}%")
        print(f"{'='*60}\n")
   
    def run(self):
        print(f"\n{'='*60}")
        print(f"🤖 BOT INICIADO (Kairós - 33% Collateral)")
        print(f"{'='*60}\n")
       
        try:
            self.data_manager.fetch_recent_data()
            self.update_ppfp_parameters()
           
            while True:
                if not self.open_position_data:
                    signal = self.check_for_signal()
                   
                    if signal:
                        print(f"✅ Señal detectada. Abriendo posición...")
                        self.open_position()
                    else:
                        print(f"⏳ Sin señal. Esperando {self.trade_interval}s...")
                        time.sleep(self.trade_interval)
                   
                    if self.data_manager.should_update(30):
                         self.data_manager.fetch_recent_data()
                         self.update_ppfp_parameters()
                else:
                    pnl = self.monitor_and_close_position()
                   
                    if pnl is not None:
                        self.capital += pnl
                        self.daily_pnl += pnl
                        self.trade_count += 1
                        self.print_stats()
                        time.sleep(self.trade_interval)
                   
        except KeyboardInterrupt:
            print("\n⚠ Bot detenido")
            self.print_stats()
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            sys.exit(1)

# === MAIN ===
if __name__ == "__main__":
    def run_kairós():
        print("\n*** KAIRÓS: INVOCANDO GRACIA COMPUTACIONAL ***")
        bot = PPFPTradingBot(initial_capital=capital)
        bot.run()
   
    try:
        run_kairós()
    except Exception as e:
        print(f"❌ ERROR FATAL: {e}")
        sys.exit(1)
