from PySide6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QObject,
    QThread,
    Signal,
)

import os
import time

from ui.home_page import HomePage

from version import APP_VERSION 

from core.pdf_reader import PDFReader

from core.excel_writer import ExcelWriter

from core.translator import Translator

from PySide6.QtWidgets import (
    QFileDialog,
    QGraphicsOpacityEffect,
    QLabel,
    QFrame,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QStatusBar,
    QHBoxLayout,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGraphicsBlurEffect,
)


class PDFWorker(QObject):

    finished = Signal(object, object, float)
    error = Signal(str)

    def __init__(self, pdf_reader, pdf_path):
        super().__init__()

        self.pdf_reader = pdf_reader
        self.pdf_path = pdf_path

    def run(self):

        start_time = time.perf_counter()

        try:

            products, table_data = self.pdf_reader.read(
                self.pdf_path
            )

            elapsed_time = (
                time.perf_counter() - start_time
            )

            self.finished.emit(
                products,
                table_data,
                elapsed_time
            )

        except Exception as error:

            self.error.emit(
                str(error)
            )


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setup_window()
        self.create_widgets()
        self.setup_layout()
        self.setup_statusbar()
        self.connect_signals()
        self.pdf_reader = PDFReader()
        self.translator = Translator()
        self.excel_writer = ExcelWriter()
        self.pdf_path = None
        self.details_queue = []
        self.details_total = 0
        self.details_timer = QTimer(self)
        self.details_timer.timeout.connect(self.show_next_detail)


    def show_next_detail(self):

        if self.details_queue:

            message = self.details_queue.pop(0)

            self.details_box.append(message)

        # ---------------------------------
        # Compteurs en direct
        # ---------------------------------

            if message.startswith("✅ "):

                self.live_translated += 1

                self.update_translation_summary()

            elif message.startswith("❌ "):

            # Une erreur DeepL n'est pas un produit inconnu
                if not message.startswith("❌ DeepL"):

                    self.live_unknown += 1

                    self.update_translation_summary()

        # ---------------------------------
        # Progression
        # ---------------------------------

            total = self.details_total
            remaining = len(self.details_queue)

            if total > 0:

                progress = int(
                    ((total - remaining) / total) * 100
                )

                self.set_progress(progress)

        else:

        # ---------------------------------
        # Conversion réellement terminée
        # ---------------------------------

            self.details_timer.stop()

            self.set_progress(100)

            self.btn_convert.setText(
                "✅ Conversion terminée"
            )

            self.btn_convert.setEnabled(True)

        # Ligne vide dans le résumé
            self.log("")

        # Une seule fois !
            self.log("📊 Fichier Excel créé")

        # Le bouton devient maintenant utilisable
            self.btn_open_excel.setEnabled(True)


    def setup_window(self):

        self.setWindowTitle("Supermarket Together Companion Tool")

        self.resize(1000, 650)

        self.setMinimumSize(900, 600)


    def create_widgets(self):

        self.log_box = QPlainTextEdit()

        self.log_box.setReadOnly(True)

        self.log_box.setPlaceholderText("Les informations apparaîtront ici...")

        self.details_box = QTextEdit()

        self.details_box.setReadOnly(True)

        self.lbl_log = QLabel("Résumé")

        self.lbl_details = QLabel("Journal détaillé")

        self.lbl_title = QLabel("Supermarket Together Companion Tool")

        self.header_frame = QFrame()

        self.lbl_title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        self.lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_subtitle = QLabel(
            "Convertissez automatiquement votre PDF en Excel traduit."
        )

        self.lbl_subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.lbl_subtitle.setStyleSheet("""
            color: gray;
            font-size: 12px;
        """)

        self.btn_select_pdf = QPushButton("Choisir un PDF")
        self.btn_convert = QPushButton("Convertir")
        self.btn_convert.setEnabled(False)

        self.btn_open_excel = QPushButton("📂 Ouvrir le fichier Excel")
        self.btn_open_excel.setEnabled(False)

        self.lbl_selected_file = QLabel("Aucun fichier sélectionné")
        self.lbl_selected_file.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_selected_file.setStyleSheet("""
            QLabel {
                padding: 12px;
                border-radius: 8px;
                color: #aaaaaa;
                background-color: #25282b;
                border: 1px solid #333333;
            }
                """)


    def setup_statusbar(self):
        self.status_bar = QStatusBar()

        # État de l'application à gauche
        self.status_bar.showMessage("Prêt")

        # Version de l'application à droite
        self.version_label = QLabel(f"Version {APP_VERSION}")
        self.status_bar.addPermanentWidget(self.version_label)

        self.setStatusBar(self.status_bar)


    def log(self, message):

        self.log_box.appendPlainText(message)


    def update_translation_summary(self):

        lines = self.log_box.toPlainText().splitlines()

        for index, line in enumerate(lines):

            if "produits traduits" in line:

                lines[index] = (
                    f"🌐 {self.live_translated} produits traduits."
                )

            elif "produits inconnus" in line:

                lines[index] = (
                    f"⚠️ {self.live_unknown} produits inconnus."
                )

        self.log_box.setPlainText(
            "\n".join(lines)
        )

                
    def details(self, message):

        self.details_queue.append(message)


    def connect_signals(self):

        self.btn_select_pdf.clicked.connect(self.select_pdf)

        self.btn_convert.clicked.connect(self.convert)

        self.btn_open_excel.clicked.connect(self.open_excel)
        # self.main_layout.addWidget(self.btn_open_excel)


    def convert(self):

        if not self.pdf_path:
            self.log("⚠ Aucun PDF sélectionné.")
            return

        conversion_start = time.perf_counter()

        # ---------------------------------
        # Réinitialisation de l'interface
        # ---------------------------------

        self.log_box.clear()
        self.details_timer.stop()
        self.details_queue.clear()
        self.details_box.clear()

        self.btn_convert.setEnabled(False)
        self.btn_convert.setText("Conversion en cours...")

        # Le bouton Excel reste visible,
        # mais désactivé pendant la conversion
        self.btn_open_excel.setVisible(True)
        self.btn_open_excel.setEnabled(False)

        self.set_progress(0)

        # Compteurs
        self.live_translated = 0
        self.live_unknown = 0
        self.live_total = 0

        # ---------------------------------
        # Récupération du PDF déjà analysé
        # ---------------------------------

        self.log("📄 Lecture du PDF...")

        try:

            products = self.cached_products
            table_data = self.cached_table_data

        except Exception as error:

            self.log("❌ Erreur lors de la récupération du PDF.")
            self.details(
                f"❌ Erreur PDF : {error}"
            )

            self.btn_convert.setEnabled(True)
            self.btn_convert.setText("Convertir")

            self.btn_open_excel.setEnabled(False)

            self.set_progress(0)

            return

        # ---------------------------------
        # Vérification des produits
        # ---------------------------------

        self.live_total = len(products)

        if self.live_total == 0:

            self.log(
                "⚠ Aucun produit détecté dans le PDF."
            )

            self.details(
                "❌ Aucun produit exploitable trouvé."
            )

            self.btn_convert.setEnabled(False)
            self.btn_convert.setText(
                "PDF non compatible"
            )

            self.btn_open_excel.setEnabled(False)

            self.set_progress(0)

            return

        # ---------------------------------
        # Résumé initial
        # ---------------------------------

        self.log(
            f"✅ {self.live_total} produits détectés"
        )

        self.log(
            "🌐 0 produits traduits."
        )

        self.log(
            "⚠️ 0 produits inconnus."
        )

        # ---------------------------------
        # Traductions
        # ---------------------------------

        translation_start = time.perf_counter()

        (
            products,
            translated_count,
            unknown_count,
            unknown_products,
            translation_results,
            translation_errors,
            new_translation_results
        ) = self.translator.translate(products)

        translation_time = (
            time.perf_counter() - translation_start
        )

        # ---------------------------------
        # Création du fichier Excel
        # ---------------------------------

        excel_start = time.perf_counter()

        output_path = os.path.join(
            "output",
            "supermarket_together.xlsx"
        )

        os.makedirs(
            "output",
            exist_ok=True
        )

        self.excel_writer.write(
            table_data,
            products,
            output_path
        )

        self.excel_output_path = os.path.abspath(
            output_path
        )

        excel_time = (
            time.perf_counter() - excel_start
        )

        # ---------------------------------
        # Erreurs DeepL éventuelles
        # ---------------------------------

        if translation_errors:

            self.details(
                "Erreurs rencontrées :"
            )

            self.details("")

            for error in translation_errors:

                self.details(
                    f"❌ DeepL : {error}"
                )

            self.details("")

        # ---------------------------------
        # CAS 1 :
        # Tout était déjà dans le cache
        # ---------------------------------

        if not new_translation_results:

            total_time = (
                time.perf_counter()
                - conversion_start
            )

            self.live_translated = translated_count
            self.live_unknown = unknown_count

            self.update_translation_summary()

            self.log("")

            self.log(
                "✅ Toutes les traductions "
                "sont déjà disponibles."
            )

            self.log(
                "📊 Fichier Excel créé"
            )

            self.details(
                f"✓ Traductions chargées depuis "
                f"le cache en {translation_time:.3f} s"
            )

            self.details(
                f"✓ Fichier Excel généré en "
                f"{excel_time:.3f} s"
            )

            self.details("")

            self.details(
                f"Temps total de conversion : "
                f"{total_time:.3f} s"
            )

            self.set_progress(100)

            self.btn_convert.setText(
                "Conversion terminée"
            )

            self.btn_convert.setEnabled(True)

            self.btn_open_excel.setEnabled(True)

            return

        # ---------------------------------
        # CAS 2 :
        # Nouvelles traductions effectuées
        # ---------------------------------

        for success, product_name in translation_results:

            if success:

                self.details(
                    f"✓ {product_name}"
                )

            else:

                self.details(
                    f"✗ {product_name}"
                )

        # ---------------------------------
        # Informations techniques
        # ---------------------------------

        self.details("")

        self.details(
            f"Traduction : "
            f"{translation_time:.3f} s"
        )

        self.details(
            f"Création Excel : "
            f"{excel_time:.3f} s"
        )

        # ---------------------------------
        # Lancement de l'animation
        # ---------------------------------

        self.details_total = len(
            self.details_queue
        )

        self.details_timer.start(40)


    def open_excel(self):

        if not hasattr(self, "excel_output_path"):
            return

        if not os.path.exists(self.excel_output_path):
            self.log("⚠ Fichier Excel introuvable.")
            return

        os.startfile(self.excel_output_path)


    def animate_pdf_selected(self):

        self.pdf_opacity_effect = QGraphicsOpacityEffect(
        self.lbl_selected_file
    )

        self.lbl_selected_file.setGraphicsEffect(
        self.pdf_opacity_effect
    )

        self.pdf_animation = QPropertyAnimation(
        self.pdf_opacity_effect,
        b"opacity"
    )

        self.pdf_animation.setDuration(500)

        self.pdf_animation.setStartValue(0.0)
        self.pdf_animation.setEndValue(1.0)

        self.pdf_animation.start()

        
    def select_pdf(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choisir un PDF",
            "",
            "Fichiers PDF (*.pdf)"
        )

        if not file_path:
            return

    # ---------------------------------
    # Nouveau fichier sélectionné
    # ---------------------------------

        self.pdf_path = file_path

        file_name = os.path.basename(file_path)

    # Remise à zéro de l'interface
        self.details_timer.stop()
        self.details_queue.clear()
        self.details_box.clear()
        self.log_box.clear()

        self.set_progress(0)

        self.btn_open_excel.setEnabled(False)

    # Tant que le PDF n'est pas validé :
    # impossible de lancer la conversion.
        self.btn_convert.setEnabled(False)
        self.btn_convert.setText("Vérification du PDF...")

        self.lbl_selected_file.setText(
            f"Vérification en cours...\n{file_name}"
        )

        self.status_bar.showMessage(
            "Vérification du document..."
        )

    # ---------------------------------
    # Vérification du PDF
    # ---------------------------------

        try:

            self.pdf_thread = QThread()

            self.pdf_worker = PDFWorker(
                self.pdf_reader,
                self.pdf_path
            )

            self.pdf_worker.moveToThread(
                self.pdf_thread
            )

            self.pdf_thread.started.connect(
                self.pdf_worker.run
            )

            self.pdf_worker.finished.connect(
                self.pdf_validation_finished
            )

            self.pdf_worker.error.connect(
                self.pdf_validation_error
            )

            self.pdf_worker.finished.connect(
                self.pdf_worker.deleteLater
            )

            self.pdf_worker.error.connect(
                self.pdf_worker.deleteLater
            )

            self.pdf_thread.finished.connect(
                self.pdf_thread.deleteLater
            )

            self.pdf_thread.start()

        except Exception:

            self.lbl_selected_file.setText(
                f"❌ PDF non compatible\n{file_name}"
            )

            self.lbl_selected_file.setStyleSheet("""
                QLabel {
                    padding: 12px;
                    border-radius: 8px;
                    color: #ffffff;
                    background-color: #5c2929;
                    border: 1px solid #a94442;
                    font-weight: bold;
            }
            """)

            self.btn_convert.setText(
                "PDF non compatible"
            )

            self.btn_convert.setEnabled(False)

            self.status_bar.showMessage(
                "Le document sélectionné ne peut pas être utilisé."
            )

            return


    # ---------------------------------
    # PDF valide
    # ---------------------------------

        self.lbl_selected_file.setStyleSheet("""
            QLabel {
                padding: 12px;
                border-radius: 8px;
                color: #ffffff;
                background-color: #214d36;
                border: 1px solid #31945f;
                font-weight: bold;
            }
        """)

        self.btn_convert.setText(
            "Convertir"
        )

        self.btn_convert.setEnabled(True)

        self.btn_convert.setStyleSheet("""
            QPushButton {
                background-color: #31945f;
                color: white;
                font-weight: bold;
            }
            
            QPushBuutton:hover {
                background-color: #38a86c;
            }
            """)

        self.animate_pdf_selected()


    def pdf_validation_finished(
        self,
        products,
        table_data,
        elapsed_time
    ):

        # Mise en cache du PDF analysé
        self.cached_products = products
        self.cached_table_data = table_data

        file_name = os.path.basename(
            self.pdf_path
        )

        # Aucun produit trouvé
        if not products:

            self.lbl_selected_file.setText(
                f"❌ PDF non compatible\n{file_name}"
            )

            self.btn_convert.setText(
                "PDF non compatible"
            )

            self.btn_convert.setEnabled(False)

            self.details_box.append(
                f"❌ Aucun produit détecté "
                f"({elapsed_time:.2f} s)"
            )

            self.status_bar.showMessage(
                "Aucun produit compatible détecté."
            )

        else:

            # PDF valide
            self.lbl_selected_file.setText(
                f"PDF compatible\n"
                f"{file_name}\n"
                f"{len(products)} produits détectés"
            )

            self.lbl_selected_file.setStyleSheet("""
                QLabel {
                    padding: 12px;
                    border-radius: 8px;
                    color: #ffffff;
                    background-color: #214d36;
                    border: 1px solid #31945f;
                    font-weight: bold;
                }
            """)

            self.btn_convert.setText(
                "Convertir"
            )

            self.btn_convert.setEnabled(True)

            self.btn_convert.setStyleSheet("""
                QPushButton {
                    background-color: #31945f;
                    color: white;
                    font-weight: bold;
                }

                QPushButton:hover {
                    background-color: #38a86c;
                }
            """)

            self.details_box.append(
                f"✓ PDF analysé en "
                f"{elapsed_time:.2f} secondes"
            )

            self.details_box.append(
                f"✓ {len(products)} produits détectés"
            )

            self.status_bar.showMessage(
                f"Document prêt à convertir — "
                f"{len(products)} produits détectés"
            )

            self.animate_pdf_selected()

        # Arrêt propre du thread
        self.pdf_thread.quit()


    def pdf_validation_error(self, error_message):

        file_name = os.path.basename(
            self.pdf_path
        )

        self.lbl_selected_file.setText(
            f"❌ PDF non compatible\n{file_name}"
        )

        self.lbl_selected_file.setStyleSheet("""
            QLabel {
                padding: 12px;
                border-radius: 8px;
                color: #ffffff;
                background-color: #5c2929;
                border: 1px solid #a94442;
                font-weight: bold;
            }
        """)

        self.btn_convert.setText(
            "PDF non compatible"
        )

        self.btn_convert.setEnabled(False)

        self.details_box.append(
            f"❌ Erreur pendant l'analyse : "
            f"{error_message}"
        )

        self.status_bar.showMessage(
            "Impossible d'analyser le document."
        )

        self.pdf_thread.quit()


    def setup_layout(self):

        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        self.main_layout = QVBoxLayout(
            central_widget
        )

        self.main_layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        self.main_layout.setSpacing(0)

        # -------------------------
        # Nouvelle page d'accueil
        # -------------------------

        self.home_page = HomePage(
            self
        )

        self.main_layout.addWidget(
            self.home_page
        )


    def set_progress(self, value):

            # On force une valeur comprise entre 0 et 100
            value = max(0, min(100, value))

            if value >= 100:

                self.btn_convert.setStyleSheet("""
                    QPushButton {
                        border: none;
                        border-radius: 8px;
                        padding: 15px;
                        font-weight: bold;
                        color: white;
                        background-color: #31945f;
                    }
                """)

                return

            # Conversion en valeur 0.00 -> 1.00
            position = value / 100.0

            # Petite séparation entre vert et gris
            next_position = min(position + 0.001, 1.0)

            # IMPORTANT : on force un format décimal propre pour Qt
            pos = f"{position:.3f}"
            next_pos = f"{next_position:.3f}"

            self.btn_convert.setStyleSheet(f"""
                QPushButton {{
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                    color: white;

                    background: qlineargradient(
                        x1:0, y1:0,
                        x2:1, y2:0,
                        stop:0 #31945f,
                        stop:{pos} #31945f,
                        stop:{next_pos} #606060,
                        stop:1 #606060
                    );
                }}
            """)
