import sqlite3
import pandas as pd
from datetime import datetime


# A Pandas minden oszlopot megjelenít.
pd.set_option("display.max_columns", None)

# Szélesebb megjelenítést állítunk be a konzolon.
pd.set_option("display.width", 200)


# Kapcsolódunk az SQLite adatbázishoz.
conn = sqlite3.connect("koho.db")
cursor = conn.cursor()


# Töröljük a korábban létrehozott táblákat.
cursor.execute("DROP TABLE IF EXISTS adagok")
cursor.execute('DROP TABLE IF EXISTS "Hűtőpanelek"')


# Beolvassuk az Adagok.csv fájlt.
df_adagok = pd.read_csv(
    "Adagok.csv",
    sep=";",
    encoding="cp852"
)


# Eltároljuk az eredeti sorok számát.
eredeti_sorok = len(df_adagok)

# Eltávolítjuk a teljesen üres sorokat.
df_adagok = df_adagok.dropna(how="all")

# Eltároljuk a tisztítás utáni sorok számát.
tisztitott_sorok = len(df_adagok)


print("\nADATMINŐSÉG\n")

print("Adagok.csv eredeti sorainak száma:", eredeti_sorok)
print("Üres sorok eltávolítása után:", tisztitott_sorok)

print(
    "Eltávolított üres sorok száma:",
    eredeti_sorok - tisztitott_sorok
)


# Egész szám típusúvá alakítjuk a szükséges oszlopokat.
df_adagok["ADAGSZÁM"] = df_adagok["ADAGSZÁM"].astype("Int64")
df_adagok["ADAGKÖZI IDŐ"] = df_adagok["ADAGKÖZI IDŐ"].astype("Int64")
df_adagok["ADAGIDŐ"] = df_adagok["ADAGIDŐ"].astype("Int64")


# Egységes formátumra alakítjuk a dátumokat.
df_adagok["Kezdet_DÁTUM"] = pd.to_datetime(
    df_adagok["Kezdet_DÁTUM"],
    format="%Y.%m.%d"
).dt.strftime("%Y-%m-%d")

df_adagok["Vége_DÁTUM"] = pd.to_datetime(
    df_adagok["Vége_DÁTUM"],
    format="%Y.%m.%d"
).dt.strftime("%Y-%m-%d")


# Egységes formátumra alakítjuk az időpontokat.
df_adagok["Kezdet_IDŐ"] = pd.to_datetime(
    df_adagok["Kezdet_IDŐ"],
    format="%H:%M:%S"
).dt.strftime("%H:%M:%S")

df_adagok["Vége_IDŐ"] = pd.to_datetime(
    df_adagok["Vége_IDŐ"],
    format="%H:%M:%S"
).dt.strftime("%H:%M:%S")


print("\nADAGOK.CSV\n")

print(df_adagok)

print(
    "\nAdagok.csv sorainak száma:",
    len(df_adagok)
)

print(
    "Adagok.csv oszlopainak száma:",
    len(df_adagok.columns)
)


# Létrehozzuk az adagok táblát.
cursor.execute("""
CREATE TABLE adagok (
    "ADAGSZÁM" INTEGER PRIMARY KEY,
    "Kezdet_DÁTUM" TEXT NOT NULL,
    "Kezdet_IDŐ" TEXT NOT NULL,
    "Vége_DÁTUM" TEXT NOT NULL,
    "Vége_IDŐ" TEXT NOT NULL,
    "ADAGKÖZI IDŐ" INTEGER,
    "ADAGIDŐ" INTEGER
)
""")


# Az adagok adatait SQL INSERT paranccsal töltjük be.
for _, sor in df_adagok.iterrows():

    cursor.execute("""
        INSERT INTO adagok (
            "ADAGSZÁM",
            "Kezdet_DÁTUM",
            "Kezdet_IDŐ",
            "Vége_DÁTUM",
            "Vége_IDŐ",
            "ADAGKÖZI IDŐ",
            "ADAGIDŐ"
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        int(sor["ADAGSZÁM"]),
        sor["Kezdet_DÁTUM"],
        sor["Kezdet_IDŐ"],
        sor["Vége_DÁTUM"],
        sor["Vége_IDŐ"],
        int(sor["ADAGKÖZI IDŐ"]),
        int(sor["ADAGIDŐ"])
    ))


# Elmentjük az adatbázis módosításait.
conn.commit()


# SQL SELECT segítségével visszaolvassuk az adagokat.
cursor.execute("""
SELECT *
FROM adagok
ORDER BY "ADAGSZÁM"
""")

eredmenyek = cursor.fetchall()


print("\nSQL SELECT eredménye:")

for sor in eredmenyek:
    print(sor)


# Beolvassuk a hűtőpanel-méréseket.
df_hutopanelek = pd.read_csv(
    "Hűtőpanelek.csv",
    sep=";"
)
print("\nHŰTŐPANEL OSZLOPOK\n")

for oszlop in df_hutopanelek.columns:
    print(oszlop)

# Egységes formátumra alakítjuk a mérési időpontokat.
for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("Time"):

        df_hutopanelek[oszlop] = pd.to_datetime(
            df_hutopanelek[oszlop],
            format="%Y.%m.%d %H:%M:%S"
        ).dt.strftime("%Y-%m-%d %H:%M:%S")


# Számokká alakítjuk a hőmérsékleti értékeket.
for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("ValueY"):

        df_hutopanelek[oszlop] = (
            df_hutopanelek[oszlop]
            .astype(str)
            .str.replace(",", ".", regex=False)
        )

        df_hutopanelek[oszlop] = pd.to_numeric(
            df_hutopanelek[oszlop],
            errors="coerce"
        )


print("\nHŰTŐPANELEK.CSV\n")

print(df_hutopanelek)

print(
    "\nHűtőpanelek.csv sorainak száma:",
    len(df_hutopanelek)
)

print(
    "Hűtőpanelek.csv oszlopainak száma:",
    len(df_hutopanelek.columns)
)


# Ellenőrizzük a Hűtőpanelek hiányzó értékeit.
print("\nHŰTŐPANELEK ADATMINŐSÉG ELLENŐRZÉSE\n")

print("Hiányzó értékek:")

van_hianyzo = False

for oszlop in df_hutopanelek.columns:

    hianyzo = df_hutopanelek[oszlop].isna().sum()

    if hianyzo > 0:

        print(
            oszlop,
            "- hiányzó értékek száma:",
            hianyzo
        )

        van_hianyzo = True


# Jelezzük, ha nem található hiányzó érték.
if not van_hianyzo:
    print("Nincs hiányzó érték.")


# Megszámoljuk a duplikált sorokat.
duplikalt_sorok = df_hutopanelek.duplicated().sum()

print(
    "\nDuplikált sorok száma:",
    duplikalt_sorok
)


# Kiszámítjuk a hőmérsékleti adatok minimumát, maximumát és átlagát.
print("\nHőmérsékleti értékek ellenőrzése:")

for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("ValueY"):

        minimum = df_hutopanelek[oszlop].min()
        maximum = df_hutopanelek[oszlop].max()
        atlag = df_hutopanelek[oszlop].mean()

        print("\n", oszlop)
        print("Minimum:", round(minimum, 2), "°C")
        print("Maximum:", round(maximum, 2), "°C")
        print("Átlag:", round(atlag, 2), "°C")


# Megkeressük a választott tartományon kívüli hőmérsékleteket.
print("\nGyanús hőmérsékleti értékek:")

for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("ValueY"):

        gyanus = df_hutopanelek[
            (df_hutopanelek[oszlop] < 0) |
            (df_hutopanelek[oszlop] > 100)
        ]

        if len(gyanus) > 0:

            print(
                oszlop,
                "- gyanús értékek száma:",
                len(gyanus)
            )

        else:

            print(
                oszlop,
                "- nincs gyanús érték"
            )


# Ellenőrizzük a hibás vagy hiányzó mérési időpontokat.
print("\nIdőpontok ellenőrzése:")

for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("Time"):

        idopontok = pd.to_datetime(
            df_hutopanelek[oszlop],
            errors="coerce"
        )

        hibas_idopontok = idopontok.isna().sum()

        print(
            oszlop,
            "- hibás vagy hiányzó időpontok:",
            hibas_idopontok
        )


# Ellenőrizzük a mérési időpontok sorrendjét.
print("\nIdőrend ellenőrzése:")

for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("Time"):

        idopontok = pd.to_datetime(
            df_hutopanelek[oszlop],
            errors="coerce"
        )

        if idopontok.is_monotonic_increasing:

            print(
                oszlop,
                "- időrend rendben"
            )

        else:

            print(
                oszlop,
                "- FIGYELEM: az időpontok nincsenek sorrendben"
            )


print(
    "\nA Hűtőpanelek adatminőség-ellenőrzése befejeződött."
)
# Normalizáljuk a hűtőpanel-adatokat.
normalizalt_adatok = []

for oszlop in df_hutopanelek.columns:

    if oszlop.endswith("Time"):

        value_oszlop = oszlop.replace("Time", "ValueY")

        if value_oszlop in df_hutopanelek.columns:

            panel_szam = int(
                oszlop.split("Panel hőfok ")[1].split(" ")[0]
            )

            panel_adatok = pd.DataFrame({
                "panel_szam": panel_szam,
                "idopont": df_hutopanelek[oszlop],
                "homerseklet": df_hutopanelek[value_oszlop]
            })

            normalizalt_adatok.append(panel_adatok)

df_meresek = pd.concat(
    normalizalt_adatok,
    ignore_index=True
)

print("\nNORMALIZÁLT HŰTŐPANEL-ADATOK\n")

print(df_meresek)

print(
    "\nNormalizált mérések száma:",
    len(df_meresek)
)

print(
    "Panelek száma:",
    df_meresek["panel_szam"].nunique()
)

print(
    "Panelek:",
    sorted(df_meresek["panel_szam"].unique())
)

print(
    "Hiányzó értékek száma:",
    df_meresek.isna().sum().sum()
)

print(
    "Duplikált mérések száma:",
    df_meresek.duplicated().sum()
)

print("\nMérések száma panelenként:")

print(
    df_meresek["panel_szam"]
    .value_counts()
    .sort_index()
)

# Betöltjük a normalizált hűtőpanel-méréseket az adatbázisba.
df_meresek.to_sql(
    "Hűtőpanelek",
    con=conn,
    if_exists="replace",
    index=False
)


# Elmentjük az adatbázis módosításait.
conn.commit()


# Lekérdezzük az adatbázisban található adagok számát.
cursor.execute("""
SELECT COUNT(*)
FROM adagok
""")

rekordok_szama = cursor.fetchone()[0]


print("\nADATBÁZIS ELLENŐRZÉSE\n")

print(
    "Az adatbázisban lévő adagok száma:",
    rekordok_szama
)


# Lekérdezzük az adatbázisban található hűtőpanel-mérések számát.
cursor.execute("""
SELECT COUNT(*)
FROM "Hűtőpanelek"
""")

hutopanel_rekordok = cursor.fetchone()[0]

print(
    "Az adatbázisban lévő hűtőpanel-mérések száma:",
    hutopanel_rekordok
)
# Indexet hozunk létre az időpont szerinti keresések gyorsításához.
cursor.execute("""
CREATE INDEX IF NOT EXISTS idx_hutopanelek_idopont
ON "Hűtőpanelek" (idopont)
""")

conn.commit()

# Lekérdezzük az adatbázisban található adagszámokat.
cursor.execute("""
SELECT "ADAGSZÁM"
FROM adagok
ORDER BY "ADAGSZÁM"
""")

adagszamok = cursor.fetchall()


print("\nAz adatbázisban lévő adagszámok:")

for adagszam in adagszamok:
    print(adagszam[0])


# Lekérjük az időtartamok ellenőrzéséhez szükséges adatokat.
cursor.execute("""
SELECT
    "ADAGSZÁM",
    "Kezdet_DÁTUM",
    "Kezdet_IDŐ",
    "Vége_DÁTUM",
    "Vége_IDŐ",
    "ADAGIDŐ"
FROM adagok
ORDER BY "ADAGSZÁM"
""")

adagok = cursor.fetchall()


# Ellenőrizzük az adagok kezdési és befejezési időpontjait.
print("\nIDŐTARTAMOK ELLENŐRZÉSE\n")

for adag in adagok:

    adagszam = adag[0]

    kezdet_szoveg = adag[1] + " " + adag[2]
    vege_szoveg = adag[3] + " " + adag[4]

    kezdet = datetime.strptime(
        kezdet_szoveg,
        "%Y-%m-%d %H:%M:%S"
    )

    vege = datetime.strptime(
        vege_szoveg,
        "%Y-%m-%d %H:%M:%S"
    )

    if kezdet < vege:

        kulonbseg = vege - kezdet

        szamitott_percek = int(
            kulonbseg.total_seconds() / 60
        )

        # A 120 percnél hosszabb adagokat külön jelöljük.
        if szamitott_percek > 120:

            print(
                adagszam,
                "FIGYELEM - hosszú időtartam:",
                szamitott_percek,
                "perc"
            )

        else:

            print(
                adagszam,
                "rendben - időtartam:",
                szamitott_percek,
                "perc"
            )

    else:

        print(
            adagszam,
            "HIBÁS IDŐPONT"
        )


# Összehasonlítjuk a tárolt ADAGIDŐ értékét a kiszámított időtartammal.
print("\nADAGIDŐ ELLENŐRZÉSE\n")

for adag in adagok:

    adagszam = adag[0]

    kezdet_szoveg = adag[1] + " " + adag[2]
    vege_szoveg = adag[3] + " " + adag[4]

    csv_adagido = adag[5]

    kezdet = datetime.strptime(
        kezdet_szoveg,
        "%Y-%m-%d %H:%M:%S"
    )

    vege = datetime.strptime(
        vege_szoveg,
        "%Y-%m-%d %H:%M:%S"
    )

    szamitott_percek = int(
        (vege - kezdet).total_seconds() / 60
    )

    if szamitott_percek == csv_adagido:

        print(
            adagszam,
            "ADAGIDŐ rendben"
        )

    else:

        print(
            adagszam,
            "ELTÉRÉS!",
            "CSV:",
            csv_adagido,
            "Számított:",
            szamitott_percek
        )


# Bezárjuk az adatbázis-kapcsolatot.
conn.close()


print(
    "\nAz adatbázis létrehozása és ellenőrzése befejeződött."
)