import gspread
import pandas as pd

print("⏳ Menghubungkan FO ke Google Sheets...")
try:
    # 1. Autentikasi menggunakan file kunci JSON
    gc = gspread.service_account(filename='kunci_google.json')
    
    # 2. Buka file Google Sheets berdasarkan NAMANYA (Pastikan namanya persis)
    sheet_fo = gc.open('Section List FO') 
    worksheet_fo = sheet_fo.worksheet('After') # Nama tab sheet-nya
    
    # 3. Tarik semua datanya ke dalam Pandas DataFrame
    data_fo = worksheet_fo.get_all_values()
    headers_fo = data_fo.pop(0)
    df = pd.DataFrame(data_fo, columns=headers_fo)
    print("✅ Database FO berhasil ditarik dari Google Sheets!")
except Exception as e:
    print(f"❌ Error menghubungkan FO ke Google Sheets: {e}")
    exit()

def cari_data_fo_interaktif(keyword):
    """Mencari data berdasarkan SITE NAME atau TowerIndex untuk dijadikan tombol"""
    mask = df['NE Name'].str.contains(keyword, case=False, na=False) | \
           df['FE Name'].str.contains(keyword, case=False, na=False)
    
    hasil = df[mask]
    if hasil.empty:
        return None
    
    data_list = []
    for index, row in hasil.iterrows():
        section_name = str(row.get('Section Name', 'Tanpa Nama Section'))
        data_list.append({
            'id': str(index), 
            'section': section_name
        })
    return data_list

def get_detail_by_id(data_id):
    """Mengambil 1 baris data spesifik saat tombol diklik oleh user"""
    try:
        idx = int(data_id)
        row = df.loc[idx]
        
        lat_ne, lon_ne = str(row.get('Latitude NE', '')).strip().replace(',', '.'), str(row.get('Longitude NE', '')).strip().replace(',', '.')
        lat_fe, lon_fe = str(row.get('Latitude FE', '')).strip().replace(',', '.'), str(row.get('Longitude FE', '')).strip().replace(',', '.')
        
        pesan = f"📊 *DETAIL SECTION*\n\n"
        pesan += f"🔹 *Unicode*: {row.get('Unicode', '-')}\n"
        pesan += f"🔹 *Section Name*: {row.get('Section Name', '-')}\n"
        pesan += f"🔹 *NE Name*: {row.get('NE Name', '-')} (Tower {row.get('NE Tower Index', '-')})\n"
        pesan += f"🔹 *FE Name*: {row.get('FE Name', '-')} (Tower {row.get('FE Tower Index', '-')})\n"
        pesan += f"🔹 *Distance*: {row.get('Distance (KM)', '-')} KM\n"
        pesan += f"🔹 *Cable Type*: {row.get('Cable Type', '-')}\n"
        pesan += f"🔹 *Status Core*: Aktif {row.get('Core Active', '-')} / Total {row.get('Cable Capacity Installed (Core)', '-')}"
        
        map_ne, map_fe, rute_map = "", "", ""
        if lat_ne.lower() != 'nan' and lon_ne.lower() != 'nan' and lat_ne != '':
            map_ne = f"https://www.google.com/maps?q={lat_ne},{lon_ne}"
        if lat_fe.lower() != 'nan' and lon_fe.lower() != 'nan' and lat_fe != '':
            map_fe = f"https://www.google.com/maps?q={lat_fe},{lon_fe}"
        if map_ne and map_fe:
            rute_map = f"https://www.google.com/maps/dir/{lat_ne},{lon_ne}/{lat_fe},{lon_fe}"
            
        return {
            'pesan': pesan,
            'map_ne': map_ne,
            'map_fe': map_fe,
            'rute_map': rute_map
        }
    except Exception as e:
        return None