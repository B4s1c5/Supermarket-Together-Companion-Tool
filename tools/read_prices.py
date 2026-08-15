from pathlib import Path
import json
import re

from es3_modifier.main import decrypt_aes_128_cbc


SAVE_DIRECTORY = Path(
    r"C:\Users\Quentin\AppData\LocalLow\DDTNL\Supermarket Together"
)


def find_latest_save():
    saves = []

    pattern = re.compile(
        r"StoreFile0Day(\d+)\.es3$"
    )

    for file in SAVE_DIRECTORY.glob("StoreFile0Day*.es3"):

        match = pattern.match(file.name)

        if match:
            day = int(match.group(1))
            saves.append((day, file))

    if not saves:
        return None, None

    day, file = max(
        saves,
        key=lambda item: item[0]
    )

    return day, file

PASSWORD = "g#asojrtg@omos)^yq"


def main():

    print()
    print("=" * 100)
    print(" SUPERMARKET TOGETHER - EXTRACTION DES PRIX DU JEUDI")
    print("=" * 100)
    print()

    print("[+] Recherche de la sauvegarde la plus récente...")
    print()

    save_day, save_file = find_latest_save()

    if save_file is None:
        print("[ERREUR] Aucune sauvegarde StoreFile0DayXX.es3 trouvée.")
        return

    print(
        f"[OK] Sauvegarde sélectionnée : {save_file.name}"
    )

    print(
        f"[OK] Jour détecté : Day {save_day}"
    )

    print(
        f"[OK] Taille : {save_file.stat().st_size:,} octets"
    )

    print()

    encrypted_data = save_file.read_bytes()

    print(f"[OK] Fichier : {save_file}")
    print(f"[OK] Taille  : {len(encrypted_data):,} octets")
    print()

    # ------------------------------------------------------------------
    # Déchiffrement AES
    # ------------------------------------------------------------------

    print("[+] Déchiffrement AES-128-CBC...")

    try:
        decrypted_data = decrypt_aes_128_cbc(
            encrypted_data,
            PASSWORD,
        )
    except Exception as exc:
        print("[ERREUR] Déchiffrement impossible :")
        print(exc)
        return

    print("[OK] Déchiffrement réussi.")
    print()

    # ------------------------------------------------------------------
    # Conversion UTF-8
    # ------------------------------------------------------------------

    text = decrypted_data.decode("utf-8")

    # ------------------------------------------------------------------
    # Correction du format Easy Save / PlayMaker
    # ------------------------------------------------------------------

    print("[+] Vérification du format Easy Save...")

    malformed_false = text.count(
        '"__type" : "bool"false'
    )

    malformed_true = text.count(
        '"__type" : "bool"true'
    )

    text = text.replace(
        '"__type" : "bool"false',
        '"__type" : "bool", "value" : false',
    )

    text = text.replace(
        '"__type" : "bool"true',
        '"__type" : "bool", "value" : true',
    )

    float_pattern = re.compile(
        r'"__type"\s*:\s*"float"'
        r'(-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)'
    )

    text, malformed_floats = float_pattern.subn(
        r'"__type" : "float", "value" : \1',
        text,
    )

    int_pattern = re.compile(
        r'"__type"\s*:\s*"int"'
        r'(-?\d+)'
    )

    text, malformed_ints = int_pattern.subn(
        r'"__type" : "int", "value" : \1',
        text,
    )

    # PlayMaker sérialise les chaînes ainsi :
    #
    #     "__type" : "string""Bonjour"
    #
    # ou pour une chaîne vide :
    #
    #     "__type" : "string""
    #
    # On transforme cela en :
    #
    #     "__type" : "string", "value" : "Bonjour"

    string_pattern = re.compile(
        r'("__type"\s*:\s*"string")'
        r'("(?:\\.|[^"\\])*")'
    )

    text, malformed_strings = string_pattern.subn(
        r'\1, "value" : \2',
        text,
    )

    print(
        f"    Booléens 'false' mal formés : {malformed_false}"
    )

    print(
        f"    Booléens 'true' mal formés  : {malformed_true}"
    )

    print(
        f"    Floats mal formés            : {malformed_floats}"
    )

    print(
        f"    Entiers mal formés            : {malformed_ints}"
    )

    print(
        f"    Strings mal formées          : {malformed_strings}"
    )

    # PlayMaker sérialise également les entiers ainsi :
    #
    #     "__type" : "int"3
    #
    # devient :
    #
    #     "__type" : "int", "value" : 3

    int_pattern = re.compile(
        r'"__type"\s*:\s*"int"'
        r'(-?\d+)'
    )

    text, malformed_ints = int_pattern.subn(
        r'"__type" : "int", "value" : \1',
        text,
    )
    
    # ------------------------------------------------------------------
    # Lecture JSON
    # ------------------------------------------------------------------

    print("[+] Lecture du JSON Easy Save...")

    try:
        data = json.loads(text)

    except json.JSONDecodeError as exc:

        print()
        print("[ERREUR] Le JSON est toujours invalide.")
        print(f"    Ligne    : {exc.lineno}")
        print(f"    Colonne  : {exc.colno}")
        print(f"    Position : {exc.pos}")
        print(f"    Message  : {exc.msg}")
        print()

        start = max(0, exc.pos - 200)
        end = min(len(text), exc.pos + 200)

        print(text[start:end])

        return

    print("[OK] JSON Easy Save chargé.")
    print()

    # ------------------------------------------------------------------
    # Vérification du jour
    # ------------------------------------------------------------------

    day = data.get("Day", {}).get("value")

    print(
        f"[INFO] Jour de la sauvegarde : Day {day}"
    )

    # ------------------------------------------------------------------
    # Jour de la semaine
    # ------------------------------------------------------------------

    weekdays = {
        0: "DIM",
        1: "LUN",
        2: "MAR",
        3: "MER",
        4: "JEU",
        5: "VEN",
        6: "SAM",
    }

    weekday = weekdays[day % 7]

    print(
        f"[INFO] Jour de la semaine : {weekday}"
    )

    # ------------------------------------------------------------------
    # ProductPlayerPricing
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print("PRODUCT PLAYER PRICING")
    print("=" * 100)

    player_pricing = data.get(
        "ProductPlayerPricing"
    )

    if player_pricing is None:
        print("[ERREUR] ProductPlayerPricing introuvable.")
        return

    player_prices = player_pricing["value"]["array"]

    print(
        f"Nombre de prix : {len(player_prices)}"
    )

    print()

    for product_id, price_data in enumerate(player_prices):

        price = price_data["value"]

        print(
            f"ID {product_id:<4} → {price}"
        )

    # ------------------------------------------------------------------
    # TierInflation
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print("TIER INFLATION")
    print("=" * 100)

    tier_data = data.get("TierInflation")

    if tier_data is None:
        print("[ERREUR] TierInflation introuvable.")
        return

    tier_inflation = tier_data["value"]["array"]

    print(
        f"Nombre de tiers : {len(tier_inflation)}"
    )

    print()

    for tier, inflation_data in enumerate(tier_inflation):

        inflation = inflation_data["value"]

        print(
            f"Tier {tier:<4} → {inflation}"
        )

    # ------------------------------------------------------------------
    # UnlockedProductTiers
    # ------------------------------------------------------------------

    print()
    print("=" * 100)
    print("UNLOCKED PRODUCT TIERS")
    print("=" * 100)

    unlocked_data = data.get(
        "UnlockedProductTiers"
    )

    if unlocked_data is None:
        print("[ERREUR] UnlockedProductTiers introuvable.")
        return

    unlocked_tiers = unlocked_data["value"]["array"]

    print(
        f"Nombre de tiers : {len(unlocked_tiers)}"
    )

    print()

    for tier, unlocked_data_item in enumerate(unlocked_tiers):

        unlocked = unlocked_data_item["value"]

        print(
            f"Tier {tier:<4} → {unlocked}"
        )

    print()
    print("=" * 100)
    print("FIN DE L'EXTRACTION")
    print("=" * 100)


def search_gameday():

    from pathlib import Path
    import re

    dll_path = Path(
        r"C:\SteamLibrary\steamapps\common\Supermarket Together\Supermarket Together_Data\Managed\Assembly-CSharp.dll"
    )

    print()
    print("=" * 100)
    print(" RECHERCHE DE GAMEDAY DANS ASSEMBLY-CSharp")
    print("=" * 100)
    print()

    if not dll_path.exists():
        print("[ERREUR] Assembly-CSharp.dll introuvable.")
        return

    data = dll_path.read_bytes()

    print(f"[OK] DLL : {dll_path}")
    print(f"[OK] Taille : {len(data):,} octets")
    print()

    for encoding in ("utf-8", "utf-16-le"):

        text = data.decode(
            encoding,
            errors="ignore"
        )

        print(
            f"--- Recherche avec {encoding} ---"
        )

        matches = list(
            re.finditer(
                r"selectedDay",
                text,
                re.IGNORECASE
            )
        )

        print(
            f"Occurrences : {len(matches)}"
        )

        for match in matches[:50]:

            start = max(
                0,
                match.start() - 150
            )

            end = min(
                len(text),
                match.end() + 250
            )

            context = text[start:end]

            context = context.replace(
                "\x00",
                ""
            )

            print()
            print(
                f"Position : {match.start()}"
            )
            print(
                context
            )

        print()


if __name__ == "__main__":
    main()