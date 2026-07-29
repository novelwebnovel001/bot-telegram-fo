import gspread
import pandas as pd
import re

print("⏳ Menghubungkan NE ke Google Sheets...")
try:
    gc = gspread.service_account(filename='kunci_google.json')
    
    # Buka file Google Sheets berdasarkan NAMANYA
    sheet_ne = gc.open('Database_NE')
    worksheet_ne = sheet_ne.worksheet('NE') # Nama tab sheet-nya
    
    data_ne = worksheet_ne.get_all_values()
    headers_ne = data_ne.pop(0)
    df = pd.DataFrame(data_ne, columns=headers_ne)
    print("✅ Database NE berhasil ditarik dari Google Sheets!")
except Exception as e:
    print(f"❌ Error membaca file Database NE: {e}")
    exit()

def format_wa(phone):
    phone = str(phone).strip()
    if phone.lower() == 'nan' or phone == '0' or phone == '' or phone == '-':
        return '-'
    digits = re.sub(r'\D', '', phone)
    if not digits: return '-'
    if digits.startswith('0'): digits = '62' + digits[1:]
    return f"https://wa.me/{digits}"

def cari_ne_interaktif(keyword):
    mask = df['SITE NAME '].str.contains(keyword, case=False, na=False) | \
           df['TowerIndex'].str.contains(keyword, case=False, na=False)
    
    hasil = df[mask]
    if hasil.empty: return None
    
    data_list = []
    for index, row in hasil.iterrows():
        site_name = str(row.get('SITE NAME ', 'Tanpa Nama'))
        tower_index = str(row.get('TowerIndex', '-'))
        data_list.append({
            'id': str(index), 
            'label': f"{site_name} | {tower_index}"
        })
    return data_list

def get_detail_ne_by_id(data_id):
    try:
        idx = int(data_id)
        row = df.loc[idx]
        
        lat = str(row.get('Latitude decimal', '')).strip().replace(',', '.')
        lon = str(row.get('Longitude decimal', '')).strip().replace(',', '.')
        
        map_link = ""
        if lat.lower() != 'nan' and lon.lower() != 'nan' and lat != '' and lon != '':
            map_link = f"https://www.google.com/maps?q={lat},{lon}"
            
        wa_rts = format_wa(row.get('RTS PHONE'))
        wa_cm = format_wa(row.get('CM PHONE'))
        wa_pm = format_wa(row.get('PM PHONE'))
        wa_pm2 = format_wa(row.get('PM PHONE 2'))
        
        pesan = f"📡 *DETAIL SITE NE*\n\n"
        pesan += f"🔹 *SITE NAME*: {row.get('SITE NAME ', '-')}\n"
        pesan += f"🔹 *TowerIndex*: {row.get('TowerIndex', '-')}\n"
        pesan += f"🔹 *Tower Owner*: {row.get('Tower Owner', '-')}\n"
        pesan += f"🔹 *ID TP*: {row.get('ID TP', '-')}\n"
        pesan += f"🔹 *Cluster*: {row.get('Cluster', '-')}\n\n"
        
        pesan += f"👥 *CONTACT PERSON*\n"
        pesan += f"👤 *RTS NAME*: {row.get('RTS NAME', '-')}\n"
        pesan += f"📞 *RTS PHONE*: {wa_rts if wa_rts != '-' else row.get('RTS PHONE', '-')}\n\n"
        
        pesan += f"👤 *CM NAME*: {row.get('CM NAME', '-')}\n"
        pesan += f"📞 *CM PHONE*: {wa_cm if wa_cm != '-' else row.get('CM PHONE', '-')}\n\n"
        
        pesan += f"👤 *PM NAME*: {row.get('PM NAME', '-')}\n"
        pesan += f"📞 *PM PHONE*: {wa_pm if wa_pm != '-' else row.get('PM PHONE', '-')}\n\n"
        
        if str(row.get('PM NAME 2', '-')).lower() not in ['nan', '', '-']:
            pesan += f"👤 *PM NAME 2*: {row.get('PM NAME 2', '-')}\n"
            pesan += f"📞 *PM PHONE 2*: {wa_pm2 if wa_pm2 != '-' else row.get('PM PHONE 2', '-')}\n\n"
        
        pesan += f"⚙️ *TECHNICAL DETAILS*\n"
        pesan += f"🔹 *Router ID*: {row.get('Router ID', '-')}\n"
        pesan += f"🔹 *CSR Ring*: {row.get('CSR Ring', '-')}\n"
        pesan += f"🔹 *CSR Type (SPOF/FL)*: {row.get('CSR Type (SPOF/FL)', '-')}\n"
            
        return {'pesan': pesan, 'map_link': map_link}
    except Exception as e:
        return None