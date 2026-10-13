# Sqlite kezeléséhez modul
import sqlite3
# dataframe beolvasásához
import pandas as pd
# kapcsolódás az adatbázishoz, connector létrehozása
conn = sqlite3.connect('koho.db')
# adatok módosításához cursor létrehozása
cursor = conn.cursor()
# adagok tábla eldobása amennyiben létezik (szükséges, mert újra létrehozzuk a táblát)
cursor.execute("DROP TABLE IF EXISTS adagok")
# hutopanelek tábla eldobása amennyiben létezik (szükséges, mert újra létrehozzuk a táblát)
cursor.execute("DROP TABLE IF EXISTS Hűtőpanelek")
# adatok beolvasása dataframebe
df_adagok = pd.read_csv(
    'adagok.csv',
    sep=';',
    encoding='cp852')
df_hutopanelek = pd.read_csv(
    'hűtőpanelek.csv',
    sep=';')
# adagok tábla float oszlopainak int-té alakítása
df_adagok['ADAGSZÁM'] = df_adagok['ADAGSZÁM'].astype('Int64')
df_adagok['ADAGKÖZI IDŐ'] = df_adagok['ADAGKÖZI IDŐ'].astype('Int64')
df_adagok['ADAGIDŐ'] = df_adagok['ADAGIDŐ'].astype('Int64')
# adagok tábla dátum oszlopok sqlite dátumfüggvényeihez kompatibilis formátumúvá alakítása
df_adagok['Kezdet_DÁTUM'] = pd.to_datetime(
    df_adagok['Kezdet_DÁTUM'],
    format='%Y.%m.%d'
).dt.strftime('%Y-%m-%d')
df_adagok['Vége_DÁTUM'] = pd.to_datetime(
    df_adagok['Vége_DÁTUM'],
    format='%Y.%m.%d'
).dt.strftime('%Y-%m-%d')
# adagok tábla idő oszlopok átalakítása sqlite időkezeléséhez
df_adagok['Kezdet_IDŐ'] = pd.to_datetime(
    df_adagok['Kezdet_IDŐ'],
    format='%H:%M:%S'
).dt.strftime('%H:%M:%S')
df_adagok['Vége_IDŐ'] = pd.to_datetime(
    df_adagok['Vége_IDŐ'],
    format='%H:%M:%S'
).dt.strftime('%H:%M:%S')
# hutopenelek tábla TIME oszlopai megfelelő dátum és időre alakítása
for oszlop in df_hutopanelek.columns:
    if oszlop.endswith('Time'):
        df_hutopanelek[oszlop] = pd.to_datetime(
            df_hutopanelek[oszlop],
            format='%Y.%m.%d %H:%M:%S'
        ).dt.strftime('%Y-%m-%d %H:%M:%S')
print(df_adagok)
print(df_hutopanelek)
# adagok tábla létrehozása
cursor.execute('''
CREATE TABLE adagok (
"ADAGSZÁM"	INTEGER PRIMARY KEY,
"Kezdet_DÁTUM"	TEXT,
"Kezdet_IDŐ" TEXT,
"Vége_DÁTUM"	TEXT,
"Vége_IDŐ"  TEXT,
"ADAGKÖZI IDŐ"	INTEGER,
"ADAGIDŐ" INTEGER
)'''
)
#adagok tábla feltöltése az adatokkal
df_adagok.to_sql('adagok',con=conn,if_exists='append',index=False, )
# Hűtőpanelek tábla létrehozása
tabla_nev = "Hűtőpanelek"
oszlopok = []
for i in range(1, 16):
    oszlopok.append(f'"Panel hőfok {i} [°C] Time" TEXT')
    oszlopok.append(f'"Panel hőfok {i} [°C] ValueY" REAL')
sql = f'''
CREATE TABLE "{tabla_nev}" (
    {', '.join(oszlopok)}
)
'''
cursor.execute(sql)
# Hűtőpanelek tábla feltöltése az adatokkal
df_hutopanelek.to_sql('Hűtőpanelek',con=conn,if_exists='append',index=False, )
conn.close()
#---------------------------------------------------
#---------------------------------------------------
#---------------------------------------------------