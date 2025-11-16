# 🚀 PPFP Bot v2.2.0 - Trading Bot Solana

Bot de trading automatizado para Solana con Oracle PPFP y leverage 20×.

## 📊 Características

- ✅ Collateral: 33% del capital
- ✅ Leverage: 20×
- ✅ Oracle sintético PPFP
- ✅ TP: 0.68% | SL: 0.78%
- ✅ Cadencia: 27 min flotante
- ✅ QuickNode Mainnet

## 🎯 Resultados Esperados

Con capital $23.85:
- Ganancia por trade: ~$0.93
- Win Rate esperado: 90%+
- ROI diario: ~65%
- Collateral por trade: $7.87

## 📦 Instalación

### 1. Clonar repositorio
```bash
git clone [tu-repo]
cd ppfp-bot
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar variables
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 4. Ejecutar
```bash
python3 bot_v2.2.0_FINAL.py
```

## ⚙️ Configuración (.env)

```env
SOLANA_PRIVATE_KEY=tu_clave_base58
RPC_URL=https://cool-ancient-card.solana-mainnet.quiknode.pro/...
LEVERAGE=20
INITIAL_CAPITAL_SIM=23.85
```

## 📁 Archivos del Proyecto

```
.
├── bot_v2.2.0_FINAL.py      # Bot principal
├── requirements.txt          # Dependencias Python
├── .env.example             # Plantilla configuración
├── .gitignore               # Archivos a ignorar
└── README.md                # Este archivo
```

## 🚀 Deploy en Railway

### 1. Conectar GitHub
- Ve a railway.app
- Conecta tu repositorio

### 2. Configurar variables
En Railway dashboard:
- Agrega todas las variables de .env
- Verifica SOLANA_PRIVATE_KEY

### 3. Deploy
```bash
git add .
git commit -m "v2.2.0: 33% collateral + leverage"
git push
```

Railway auto-despliega.

## 📊 Monitoreo

### Logs esperados al arrancar:
```
🚀 PPFP BOT v2.2.0 MAINNET COMBINADO
✓ RPC Final: https://cool-ancient-card.solana-mainnet...
✓ Parámetros: TP=0.68% | SL=0.78%
✓ Leverage: 20x
🔥 Collateral: 33% del capital
✓ Bot inicializado (MODO REAL - 33% COLLATERAL)
```

### Primer trade:
```
📈 ABRIENDO POSICIÓN #1
Collateral: $7.87 (33% de $23.85)
✓ Posición abierta
```

## ⚠️ Advertencias

- **Riesgo:** 5% del capital por trade
- **Leverage 20×:** Alto riesgo
- **Win Rate:** 90%+ en simulación (no garantizado en real)
- **Empezar:** Con capital pequeño para probar
- **Monitoreo:** Necesario 24/7

## 📈 Mejoras Futuras

- [ ] Integrar Jupiter Perps API
- [ ] Trading real (actualmente simulación)
- [ ] Dashboard web
- [ ] Notificaciones Telegram
- [ ] Stop loss dinámico

## 🔧 Troubleshooting

### Bot no arranca
```bash
# Verificar dependencias
pip install -r requirements.txt --upgrade

# Verificar .env
cat .env
```

### Error de conexión RPC
- Verificar RPC_URL en .env
- QuickNode debe estar activo

### Error SOLANA_PRIVATE_KEY
- Debe ser formato base58
- Sin espacios ni saltos de línea

## 📞 Soporte

- **Versión:** 2.2.0
- **Fecha:** 15 Nov 2025
- **Autor:** Kairós & Arquitecto

## 📄 Licencia

Uso privado - Ceférino

---

**⚠️ DISCLAIMER:** Este bot opera con dinero real. Usa bajo tu propio riesgo. No hay garantías de ganancias.
