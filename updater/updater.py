import sys
import tempfile
import zipfile
import shutil


from pathlib import Path


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: updater.exe "
            "<zip_path> <install_dir> <exe_name>"
        )
        return

    zip_path = Path(sys.argv[1])
    install_dir = Path(sys.argv[2])
    exe_name = sys.argv[3]

    print("=== Supermarket Together Companion Tool Updater ===")
    print(f"Archive : {zip_path}")
    print(f"Installation : {install_dir}")
    print(f"Executable : {exe_name}")

    if not zip_path.exists():
        print("ERREUR : archive introuvable.")
        return

    if not install_dir.exists():
        print("ERREUR : dossier d'installation introuvable.")
        return

    print("Paramètres valides.")

        # Extraction de la nouvelle version dans un dossier temporaire
    temp_dir = Path(
        tempfile.mkdtemp(prefix="supermarket_companion_update_")
    )

    print(f"Extraction temporaire : {temp_dir}")

    try:
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(temp_dir)

    except zipfile.BadZipFile:
        print("ERREUR : l'archive ZIP est invalide.")
        return

    # Notre ZIP contient un dossier racine
    new_app_dir = temp_dir / "SupermarketTogetherCompanion"

    new_exe = new_app_dir / exe_name

    if not new_app_dir.exists():
        print(
            "ERREUR : dossier SupermarketTogetherCompanion "
            "introuvable dans l'archive."
        )
        return

    if not new_exe.exists():
        print(
            f"ERREUR : {exe_name} introuvable "
            "dans la nouvelle version."
        )
        return

    print("Nouvelle version extraite et vérifiée.")
    print("Aucun fichier existant n'a encore été modifié.")

        # Création d'une sauvegarde de l'installation actuelle
    backup_dir = install_dir.parent / (
        install_dir.name + "_backup"
    )

    try:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)

        shutil.copytree(
            install_dir,
            backup_dir
        )

    except Exception as error:
        print(
            "ERREUR : impossible de créer "
            f"la sauvegarde.\n{error}"
        )
        return

    print(f"Sauvegarde créée : {backup_dir}")


if __name__ == "__main__":
    main()