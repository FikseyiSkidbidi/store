from datetime import datetime, timedelta
from database.models import Sale, Product, Customer, Supply

class InventoryReports:
    """Генерация текстовых отчетов для UI"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def generate_sales_report(self, start_date=None, end_date=None):
        if not start_date:
            start_date = datetime.now() - timedelta(days=30)
        if not end_date:
            end_date = datetime.now()
        
        session = self.db.Session()
        try:
            sales = session.query(Sale).filter(
                Sale.date.between(start_date, end_date)
            ).all()
            
            if not sales:
                return "Нет данных о продажах за этот период."
            
            total_sum = sum(s.total for s in sales)
            
            report = f"ОТЧЕТ ПО ПРОДАЖАМ\n{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
            report += "=" * 40 + "\n"
            report += f"Всего продаж: {len(sales)}\n"
            report += f"Выручка: {total_sum:.2f} ₽\n\n"
            report += "Детализация:\n"
            
            for s in sales:
                p_name = s.product.name if s.product else "Удален"
                report += f"- {s.date.strftime('%d.%m %H:%M')} | {p_name} x{s.quantity} = {s.total:.2f}\n"
                
            return report
        finally:
            session.close()

    def generate_inventory_report(self):
        session = self.db.Session()
        try:
            products = session.query(Product).all()
            report = "СКЛАДСКОЙ ОТЧЕТ\n" + "=" * 40 + "\n"
            
            for p in products:
                cat_val = p.category.value if hasattr(p.category, 'value') else str(p.category)
                status = "OK"
                if p.quantity == 0: status = "ПУСТО"
                elif p.quantity < p.min_stock: status = "МАЛО"
                
                report += f"[{status}] {p.name} ({cat_val})\n"
                report += f"   Остаток: {p.quantity} шт. | Цена: {p.price} ₽\n"
                report += "-" * 20 + "\n"
                
            return report
        finally:
            session.close()
    
    def generate_financial_report(self):
        return "Финансовый отчет в разработке..."