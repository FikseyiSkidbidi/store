import sys
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QMessageBox
from ui.main_window import ModernMainWindow
from database.db_manager import DatabaseManager
from reports.inventory_reports import InventoryReports
from exports.exporter import DataExporter
from database.models import ProductCategory

class StoreApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Store Management System")
        
        self.db = DatabaseManager()
        self.reports = InventoryReports(self.db)
        self.exporter = DataExporter(self.db)
        
        self.main_window = ModernMainWindow()
        
        self.main_window.show_message = self.show_message_box 
        
        self.connect_signals()
        self.load_initial_data()
        
    def show_message_box(self, title, text):
        QMessageBox.information(self.main_window, title, text)

    def connect_signals(self):
        self.main_window.add_product_btn.clicked.connect(self.add_product)
        self.main_window.refresh_products_btn.clicked.connect(self.refresh_products)
        self.main_window.process_sale_btn.clicked.connect(self.process_sale)
        self.main_window.add_supply_btn.clicked.connect(self.add_supply)
        self.main_window.add_customer_btn.clicked.connect(self.add_customer)
        
        # Отчеты и Экспорт
        self.main_window.sales_report_btn.clicked.connect(self.show_sales_report)
        self.main_window.inventory_report_btn.clicked.connect(self.show_inventory_report)
        self.main_window.export_excel_btn.clicked.connect(self.export_to_excel)
        self.main_window.export_action.triggered.connect(self.export_to_excel)
        
    def load_initial_data(self):
        self.refresh_products()
        self.update_ui_combos()
        
    def update_ui_combos(self):
        """Важно: сохраняем ID объектов в user_data комбобокса"""
        self.main_window.sale_product_combo.clear()
        self.main_window.sale_customer_combo.clear()
        self.main_window.supply_product_combo.clear()
        
        products = self.db.get_all_products()
        for p in products:
            text = f"{p.name} ({p.quantity} шт.)"
            self.main_window.sale_product_combo.addItem(text, p.id)
            self.main_window.supply_product_combo.addItem(text, p.id)
            
        customers = self.db.get_all_customers()
        self.main_window.sale_customer_combo.addItem("Гость", None)
        for c in customers:
            self.main_window.sale_customer_combo.addItem(c.name, c.id)

    def add_product(self):
        try:
            name = self.main_window.product_name_input.text().strip()
            cat_text = self.main_window.product_category_input.currentText()
            
            category = ProductCategory.OTHER
            for cat in ProductCategory:
                if cat.value == cat_text:
                    category = cat
                    break
            
            price = self.main_window.product_price_input.value()
            quantity = self.main_window.product_quantity_input.value()
            min_stock = self.main_window.product_min_stock_input.value()
            
            if not name:
                self.main_window.show_message("Ошибка", "Введите имя товара")
                return

            self.db.add_product(name, category, price, quantity, min_stock)
            self.main_window.show_message("Успех", "Товар добавлен")
            self.refresh_products()
            self.update_ui_combos()
            
            self.main_window.product_name_input.clear()
            self.main_window.product_price_input.setValue(0)
            
        except Exception as e:
            self.main_window.show_message("Ошибка", str(e))

    def refresh_products(self):
        products = self.db.get_all_products()
        table = self.main_window.products_table
        table.setRowCount(len(products))
        
        for row, p in enumerate(products):
            cat_val = p.category.value if hasattr(p.category, 'value') else str(p.category)
            
            table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            table.setItem(row, 1, QTableWidgetItem(p.name))
            table.setItem(row, 2, QTableWidgetItem(cat_val))
            table.setItem(row, 3, QTableWidgetItem(f"{p.price}"))
            table.setItem(row, 4, QTableWidgetItem(str(p.quantity)))
            table.setItem(row, 5, QTableWidgetItem(str(p.min_stock)))
            
            status = "В наличии"
            if p.quantity == 0: status = "Нет"
            elif p.quantity < p.min_stock: status = "Мало"
            table.setItem(row, 6, QTableWidgetItem(status))

    def refresh_supplies(self):
        """Обновление таблицы поставок"""
        table = self.main_window.supplies_table
        table.setRowCount(0)
        
        session = self.db.Session()
        try:
            # Получаем все поставки из базы
            from database.models import Supply
            supplies = session.query(Supply).all()
            
            for row, s in enumerate(supplies):
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(s.date.strftime('%d.%m.%Y %H:%M')))
                table.setItem(row, 1, QTableWidgetItem(s.product.name if s.product else "Удален"))
                table.setItem(row, 2, QTableWidgetItem(str(s.quantity)))
                table.setItem(row, 3, QTableWidgetItem(f"{s.cost} ₽"))
                table.setItem(row, 4, QTableWidgetItem(s.supplier))
        finally:
            session.close()

    def process_sale(self):
        try:
            # Получаем ID из скрытых данных комбобокса
            p_idx = self.main_window.sale_product_combo.currentIndex()
            c_idx = self.main_window.sale_customer_combo.currentIndex()
            
            if p_idx == -1: return

            product_id = self.main_window.sale_product_combo.itemData(p_idx)
            customer_id = self.main_window.sale_customer_combo.itemData(c_idx)
            qty = self.main_window.sale_quantity_spin.value()
            
            if qty <= 0:
                self.main_window.show_message("Ошибка", "Количество должно быть > 0")
                return

            self.db.record_sale(product_id, qty, customer_id)
            self.main_window.show_message("Успех", "Продажа оформлена")
            self.refresh_products()
            self.update_ui_combos()
            
        except Exception as e:
            self.main_window.show_message("Ошибка продажи", str(e))

    def add_supply(self):
        try:
            p_id = self.main_window.supply_product_combo.currentData()
            
            if p_id is None:
                self.main_window.show_message("Ошибка", "Выберите товар из списка")
                return

            supplier = self.main_window.supplier_input.text()
            qty = self.main_window.supply_quantity_spin.value()
            cost = self.main_window.supply_cost_input.value()
            
            if not supplier:
                self.main_window.show_message("Ошибка", "Введите имя поставщика")
                return

            self.db.add_supply(supplier, p_id, qty, cost)

            self.main_window.show_message("Успех", "Поставка оформлена")
            self.refresh_products()  
            self.refresh_supplies()  
            
        except Exception as e:
            self.main_window.show_message("Ошибка", f"Ошибка при добавлении поставки: {str(e)}")

    def add_customer(self):
        try:
            name = self.main_window.customer_name_input.text()
            phone = self.main_window.customer_phone_input.text()
            email = self.main_window.customer_email_input.text()
            
            if not name: return
            
            s = self.db.Session()
            from database.models import Customer
            new_c = Customer(name=name, phone=phone, email=email)
            s.add(new_c)
            s.commit()
            s.close()
            
            self.main_window.show_message("Успех", "Клиент добавлен")
            self.update_ui_combos()
        except Exception as e:
             self.main_window.show_message("Ошибка", str(e))

    def show_sales_report(self):
        report = self.reports.generate_sales_report()
        self.main_window.report_text.setPlainText(report)

    def show_inventory_report(self):
        report = self.reports.generate_inventory_report()
        self.main_window.report_text.setPlainText(report)

    def export_to_excel(self):
        try:
            file = self.exporter.export_to_excel()
            self.main_window.show_message("Экспорт", f"Файл сохранен: {file}")
        except Exception as e:
            self.main_window.show_message("Ошибка", f"Не удалось экспортировать: {e}")

    def run(self):
        self.main_window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    StoreApp().run()