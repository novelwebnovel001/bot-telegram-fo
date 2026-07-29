import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Impor fungsi dari bot_logic.py (Untuk Section FO)
from bot_logic import cari_data_fo_interaktif, get_detail_by_id

# Impor fungsi dari bot_logic_ne.py (Untuk Database NE)
from bot_logic_ne import cari_ne_interaktif, get_detail_ne_by_id

# Token Bot dan ID Grup
TOKEN = '1227333086:AAGftTplCuDbU_PQTuROLu1Rr_rsZRQZah4' 
TARGET_CHAT_ID = -5144697482  

bot = telebot.TeleBot(TOKEN)
print("🤖 [BOT AKTIF] Mode: Pencarian Section FO & Database NE (Max 95 Data)")

# =================================================================
# FITUR 1: PENCARIAN SECTION FO (Ketik: Cari [kata kunci])
# =================================================================
@bot.message_handler(func=lambda message: message.chat.id == TARGET_CHAT_ID and message.text and message.text.lower().startswith('cari '))
def proses_pencarian_fo(message):
    keyword = message.text[5:].strip()
    print(f"\n👉 Mencari Section FO: '{keyword}'")
    
    hasil_list = cari_data_fo_interaktif(keyword)
    if not hasil_list:
        bot.reply_to(message, f"Maaf, Section FO untuk '{keyword}' tidak ditemukan.")
        return
        
    markup = InlineKeyboardMarkup()
    markup.row_width = 1 
    
    # Batas maksimal diubah menjadi 95
    limit = min(len(hasil_list), 95) 
    for i in range(limit):
        item = hasil_list[i]
        btn = InlineKeyboardButton(text=f"📁 {item['section']}", callback_data=f"sec_{item['id']}")
        markup.add(btn)
        
    teks_balasan = f"🔍 Menemukan *{len(hasil_list)}* data Section FO untuk '{keyword}'.\n👇 *Silakan klik:* "
    
    # Keterangan jika data lebih dari 95
    if len(hasil_list) > 95:
        teks_balasan += "\n_(Hanya menampilkan 95 hasil pertama)_"
        
    bot.send_message(message.chat.id, teks_balasan, reply_markup=markup, parse_mode='Markdown')

# Menangkap klik tombol Section FO
@bot.callback_query_handler(func=lambda call: call.data.startswith('sec_'))
def respon_tombol_fo_diklik(call):
    if call.message.chat.id != TARGET_CHAT_ID: return
    data_id = call.data.split('_')[1]
    detail = get_detail_by_id(data_id)
    
    if detail:
        markup_link = InlineKeyboardMarkup()
        tombol_baris_1 = []
        if detail['map_ne']: tombol_baris_1.append(InlineKeyboardButton(text="📍 Lokasi NE", url=detail['map_ne']))
        if detail['map_fe']: tombol_baris_1.append(InlineKeyboardButton(text="📍 Lokasi FE", url=detail['map_fe']))
        if tombol_baris_1: markup_link.add(*tombol_baris_1)
        if detail['rute_map']: markup_link.add(InlineKeyboardButton(text="🗺️ Buka Rute Jalan (NE ➔ FE)", url=detail['rute_map']))
        
        bot.send_message(call.message.chat.id, detail['pesan'], reply_markup=markup_link, parse_mode='Markdown')
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id, "❌ Maaf, data FO gagal dimuat.")

# =================================================================
# FITUR 2: PENCARIAN DATABASE NE (Ketik: Carine [kata kunci])
# =================================================================
@bot.message_handler(func=lambda message: message.chat.id == TARGET_CHAT_ID and message.text and message.text.lower().startswith(('carine ', '/carine ')))
def proses_pencarian_ne(message):
    # Pisahkan spasi pertama untuk mengambil kata kuncinya saja
    keyword = message.text.split(' ', 1)[1].strip()
    print(f"\n👉 Mencari Database NE: '{keyword}'")
    
    hasil_list = cari_ne_interaktif(keyword)
    if not hasil_list:
        bot.reply_to(message, f"Maaf, data NE untuk '{keyword}' tidak ditemukan.")
        return
        
    markup = InlineKeyboardMarkup()
    markup.row_width = 1 
    
    # Batas maksimal diubah menjadi 95
    limit = min(len(hasil_list), 95) 
    for i in range(limit):
        item = hasil_list[i]
        btn = InlineKeyboardButton(text=f"📡 {item['label']}", callback_data=f"ne_{item['id']}")
        markup.add(btn)
        
    teks_balasan = f"🔍 Menemukan *{len(hasil_list)}* data NE untuk '{keyword}'.\n👇 *Silakan klik SITE:* "
    
    # Keterangan jika data lebih dari 95
    if len(hasil_list) > 95:
        teks_balasan += "\n_(Hanya menampilkan 95 hasil pertama)_"
        
    bot.send_message(message.chat.id, teks_balasan, reply_markup=markup, parse_mode='Markdown')

# Menangkap klik tombol Database NE
@bot.callback_query_handler(func=lambda call: call.data.startswith('ne_'))
def respon_tombol_ne_diklik(call):
    if call.message.chat.id != TARGET_CHAT_ID: return
    data_id = call.data.split('_')[1]
    detail = get_detail_ne_by_id(data_id)
    
    if detail:
        markup_link = InlineKeyboardMarkup()
        if detail['map_link']: 
            markup_link.add(InlineKeyboardButton(text="📍 Buka Lokasi Google Maps", url=detail['map_link']))
        
        bot.send_message(call.message.chat.id, detail['pesan'], reply_markup=markup_link, parse_mode='Markdown', disable_web_page_preview=True)
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id, "❌ Maaf, data NE gagal dimuat.")

# =================================================================
# JALANKAN BOT
# =================================================================
bot.infinity_polling(timeout=60, long_polling_timeout=60)