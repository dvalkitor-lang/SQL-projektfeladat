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
cursor.execute("DROP TABLE IF EXISTS hutopanelek")
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
)
df_adagok['Vége_DÁTUM'] = pd.to_datetime(
    df_adagok['Vége_DÁTUM'],
    format='%Y.%m.%d'
)
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
# adatok beolvasása dataframebe
# adagok tábla létrehozása
#cursor.execute('''
#CREATE TABLE adagok (
#	ADAGSZÁM	INTEGER PRIMARY KEY,
#	Kezdet	TEXT,
#	year INTEGER,
#	class	TEXT,
#	average	REAL
#	)
#	'''
#   )
df_hutopanelek.head(10).to_excel('modified.xlsx', index=False)
conn.close()