import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from datetime import datetime


class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def show_message(self, title, text):
        QMessageBox.information(self, title, text)

    def setup_ui(self):
        """Настройка современного интерфейса"""
        self.setWindowTitle("Store Management System v2.0")
        self.setGeometry(100, 100, 1400, 800)

        # Стиль (без изменений, скопирован из вашего файла)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QWidget { font-family: 'Segoe UI', Arial; font-size: 12px; }
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton#danger { background-color: #f44336; }
            QPushButton#danger:hover { background-color: #d32f2f; }
            QTabWidget::pane { border: 1px solid #ddd; background-color: white; border-radius: 6px; }
            QTabBar::tab { background-color: #e8e8e8; padding: 8px 16px; margin-right: 2px; border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: white; font-weight: bold; }
            QTableWidget { background-color: white; border: 1px solid #ddd; gridline-color: #eee; }
            QTableWidget::item { padding: 4px; }
            QHeaderView::section { background-color: #f8f9fa; padding: 8px; border: 1px solid #dee2e6; font-weight: bold; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { padding: 6px; border: 1px solid #ddd; border-radius: 4px; background-color: white; }
            QGroupBox { font-weight: bold; border: 2px solid #4CAF50; border-radius: 6px; margin-top: 10px; padding-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px 0 5px; }
        """)

        self.create_menu()
        self.create_tabs()
        self.create_status_bar()

    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Файл')
        export_action = QAction('Экспорт данных', self)
        file_menu.addAction(export_action)
        self.export_action = export_action  # Save ref

        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def create_tabs(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.products_tab = self.create_products_tab()
        self.tab_widget.addTab(self.products_tab, "📦 Товары")

        self.sales_tab = self.create_sales_tab()
        self.tab_widget.addTab(self.sales_tab, "💰 Продажи")

        self.supply_tab = self.create_supply_tab()
        self.tab_widget.addTab(self.supply_tab, "🚚 Поставки")

        self.customers_tab = self.create_customers_tab()
        self.tab_widget.addTab(self.customers_tab, "👥 Клиенты")

        self.reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(self.reports_tab, "📊 Отчеты")

    def create_products_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        control_panel = QGroupBox("Управление товарами")
        control_layout = QHBoxLayout()
        self.add_product_btn = QPushButton("➕ Добавить товар")
        self.edit_product_btn = QPushButton("✏️ Редактировать")
        self.delete_product_btn = QPushButton("🗑️ Удалить", objectName="danger")
        self.refresh_products_btn = QPushButton("🔄 Обновить")
        control_layout.addWidget(self.add_product_btn)
        control_layout.addWidget(self.edit_product_btn)
        control_layout.addWidget(self.delete_product_btn)
        control_layout.addWidget(self.refresh_products_btn)
        control_layout.addStretch()
        control_panel.setLayout(control_layout)

        form_panel = QGroupBox("Добавить/Изменить товар")
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("Название:"), 0, 0)
        self.product_name_input = QLineEdit()
        form_layout.addWidget(self.product_name_input, 0, 1)
        form_layout.addWidget(QLabel("Категория:"), 1, 0)
        self.product_category_input = QComboBox()
        self.product_category_input.addItems(["Электроника", "Одежда", "Продукты", "Книги", "Другое"])
        form_layout.addWidget(self.product_category_input, 1, 1)
        form_layout.addWidget(QLabel("Цена:"), 2, 0)
        self.product_price_input = QDoubleSpinBox()
        self.product_price_input.setRange(0, 1000000)
        self.product_price_input.setPrefix("₽ ")
        form_layout.addWidget(self.product_price_input, 2, 1)
        form_layout.addWidget(QLabel("Количество:"), 3, 0)
        self.product_quantity_input = QSpinBox()
        self.product_quantity_input.setRange(0, 10000)
        form_layout.addWidget(self.product_quantity_input, 3, 1)
        form_layout.addWidget(QLabel("Минимальный запас:"), 4, 0)
        self.product_min_stock_input = QSpinBox()
        self.product_min_stock_input.setRange(0, 1000)
        form_layout.addWidget(self.product_min_stock_input, 4, 1)
        form_panel.setLayout(form_layout)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels(
            ["ID", "Название", "Категория", "Цена", "Количество", "Минимум", "Статус"])
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addWidget(control_panel)
        layout.addWidget(form_panel)
        layout.addWidget(self.products_table)
        tab.setLayout(layout)
        return tab

    def create_sales_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        sales_control = QGroupBox("Новая продажа")
        sales_layout = QGridLayout()

        sales_layout.addWidget(QLabel("Товар:"), 0, 0)
        self.sale_product_combo = QComboBox()
        sales_layout.addWidget(self.sale_product_combo, 0, 1)

        sales_layout.addWidget(QLabel("Количество:"), 1, 0)
        self.sale_quantity_spin = QSpinBox()
        self.sale_quantity_spin.setRange(1, 1000)
        sales_layout.addWidget(self.sale_quantity_spin, 1, 1)

        sales_layout.addWidget(QLabel("Клиент:"), 2, 0)
        self.sale_customer_combo = QComboBox()
        sales_layout.addWidget(self.sale_customer_combo, 2, 1)

        self.process_sale_btn = QPushButton("💳 Оформить продажу")
        sales_layout.addWidget(self.process_sale_btn, 3, 0, 1, 2)
        sales_control.setLayout(sales_layout)

        self.sales_history_table = QTableWidget()
        self.sales_history_table.setColumnCount(6)
        self.sales_history_table.setHorizontalHeaderLabels(["ID", "Дата", "Товар", "Количество", "Сумма", "Клиент"])

        layout.addWidget(sales_control)
        layout.addWidget(QLabel("<b>История продаж:</b>"))
        layout.addWidget(self.sales_history_table)
        tab.setLayout(layout)
        return tab

    def create_supply_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        supply_form = QGroupBox("Новая поставка")
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Поставщик:"), 0, 0)
        self.supplier_input = QLineEdit()
        form_layout.addWidget(self.supplier_input, 0, 1)

        form_layout.addWidget(QLabel("Товар:"), 1, 0)
        self.supply_product_combo = QComboBox()
        form_layout.addWidget(self.supply_product_combo, 1, 1)

        form_layout.addWidget(QLabel("Количество:"), 2, 0)
        self.supply_quantity_spin = QSpinBox()
        self.supply_quantity_spin.setRange(1, 10000)
        form_layout.addWidget(self.supply_quantity_spin, 2, 1)

        form_layout.addWidget(QLabel("Стоимость поставки:"), 3, 0)
        self.supply_cost_input = QDoubleSpinBox()
        self.supply_cost_input.setPrefix("₽ ")
        form_layout.addWidget(self.supply_cost_input, 3, 1)

        self.add_supply_btn = QPushButton("📦 Добавить поставку")
        form_layout.addWidget(self.add_supply_btn, 4, 0, 1, 2)
        supply_form.setLayout(form_layout)

        self.supplies_table = QTableWidget()
        self.supplies_table.setColumnCount(6)
        self.supplies_table.setHorizontalHeaderLabels(["ID", "Дата", "Поставщик", "Товар", "Количество", "Стоимость"])

        layout.addWidget(supply_form)
        layout.addWidget(QLabel("<b>История поставок:</b>"))
        layout.addWidget(self.supplies_table)
        tab.setLayout(layout)
        return tab

    def create_customers_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        customer_form = QGroupBox("Добавить клиента")
        form_layout = QGridLayout()

        form_layout.addWidget(QLabel("Имя:"), 0, 0)
        self.customer_name_input = QLineEdit()
        form_layout.addWidget(self.customer_name_input, 0, 1)
        form_layout.addWidget(QLabel("Телефон:"), 1, 0)
        self.customer_phone_input = QLineEdit()
        form_layout.addWidget(self.customer_phone_input, 1, 1)
        form_layout.addWidget(QLabel("Email:"), 2, 0)
        self.customer_email_input = QLineEdit()
        form_layout.addWidget(self.customer_email_input, 2, 1)
        form_layout.addWidget(QLabel("Скидка %:"), 3, 0)
        self.customer_discount_spin = QSpinBox()
        self.customer_discount_spin.setRange(0, 50)
        self.customer_discount_spin.setSuffix(" %")
        form_layout.addWidget(self.customer_discount_spin, 3, 1)

        self.add_customer_btn = QPushButton("👤 Добавить клиента")
        form_layout.addWidget(self.add_customer_btn, 4, 0, 1, 2)
        customer_form.setLayout(form_layout)

        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(5)
        self.customers_table.setHorizontalHeaderLabels(["ID", "Имя", "Телефон", "Email", "Скидка"])

        layout.addWidget(customer_form)
        layout.addWidget(QLabel("<b>Список клиентов:</b>"))
        layout.addWidget(self.customers_table)
        tab.setLayout(layout)
        return tab

    def create_reports_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        reports_panel = QGroupBox("Генерация отчетов")
        reports_layout = QGridLayout()

        self.sales_report_btn = QPushButton("📈 Отчет по продажам")
        self.inventory_report_btn = QPushButton("📦 Отчет по инвентарю")
        self.financial_report_btn = QPushButton("💰 Финансовый отчет")
        self.export_excel_btn = QPushButton("📊 Экспорт в Excel")

        reports_layout.addWidget(self.sales_report_btn, 0, 0)
        reports_layout.addWidget(self.inventory_report_btn, 0, 1)
        reports_layout.addWidget(self.financial_report_btn, 1, 0)
        reports_layout.addWidget(self.export_excel_btn, 1, 1)
        reports_panel.setLayout(reports_layout)

        stats_panel = QGroupBox("Статистика магазина")
        stats_layout = QGridLayout()
        self.total_sales_label = QLabel("Общие продажи: ₽0")
        self.total_profit_label = QLabel("Прибыль: ₽0")
        self.total_products_label = QLabel("Товаров на складе: 0")
        self.low_stock_label = QLabel("Товаров с низким запасом: 0")

        stats_layout.addWidget(self.total_sales_label, 0, 0)
        stats_layout.addWidget(self.total_profit_label, 0, 1)
        stats_layout.addWidget(self.total_products_label, 1, 0)
        stats_layout.addWidget(self.low_stock_label, 1, 1)
        stats_panel.setLayout(stats_layout)

        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)

        layout.addWidget(reports_panel)
        layout.addWidget(stats_panel)
        layout.addWidget(QLabel("<b>Отчет:</b>"))
        layout.addWidget(self.report_text)
        tab.setLayout(layout)
        return tab

    def create_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готово")