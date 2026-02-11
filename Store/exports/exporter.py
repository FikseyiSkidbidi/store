import pandas as pd
from sqlalchemy import desc
from database.models import Product, Sale, Customer, Supply

class DataExporter:
    """Модуль для экспорта данных в Excel"""
    
    def __init__(self, db_manager):
        self.db = db_manager

    def export_to_excel(self, filename='store_export.xlsx'):
        session = self.db.Session()
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                
                # --- 1. ТОВАРЫ ---
                products_data = []
                products = session.query(Product).all()
                for p in products:
                    cat_val = p.category.value if hasattr(p.category, 'value') else str(p.category)
                    products_data.append({
                        'ID': p.id,
                        'Название': p.name,
                        'Категория': cat_val,
                        'Цена': p.price,
                        'Количество': p.quantity,
                        'Мин. запас': p.min_stock,
                        'Суммарная стоимость': p.price * p.quantity
                    })
                if products_data:
                    pd.DataFrame(products_data).to_excel(writer, sheet_name='Товары', index=False)

                # --- 2. ПРОДАЖИ ---
                sales_data = []
                sales = session.query(Sale).order_by(desc(Sale.date)).all()
                for s in sales:
                    sales_data.append({
                        'ID': s.id,
                        'Дата': s.date.strftime('%Y-%m-%d %H:%M'),
                        'Товар': s.product.name if s.product else "Удален",
                        'Клиент': s.customer.name if s.customer else "Гость",
                        'Количество': s.quantity,
                        'Сумма': s.total
                    })
                if sales_data:
                    pd.DataFrame(sales_data).to_excel(writer, sheet_name='Продажи', index=False)

                # --- 3. КЛИЕНТЫ ---
                customers_data = []
                customers = session.query(Customer).all()
                for c in customers:
                    customers_data.append({
                        'ID': c.id,
                        'Имя': c.name,
                        'Телефон': c.phone,
                        'Покупки': c.total_purchases
                    })
                if customers_data:
                    pd.DataFrame(customers_data).to_excel(writer, sheet_name='Клиенты', index=False)

        # --- 4. ПОСТАВКИ ---
                supplies_data = []
                supplies = session.query(Supply).all()
                for s in supplies:
                    supplies_data.append({
                        'Дата': s.date.strftime('%Y-%m-%d %H:%M'),
                        'Поставщик': s.supplier,
                        'Товар': s.product.name if s.product else "Удален",
                        'Количество': s.quantity,
                        'Стоимость': s.cost
                    })
                if supplies_data:
                    pd.DataFrame(supplies_data).to_excel(writer, sheet_name='Поставки', index=False)

            return filename
        except Exception as e:
            raise e
        finally:
            session.close()