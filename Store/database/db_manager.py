from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from database.models import Base, Product, Customer, Sale, Supply, ProductCategory


class DatabaseManager:
    """Менеджер базы данных магазина"""

    def __init__(self, db_url="sqlite:///store.db"):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.create_tables()

    def create_tables(self):
        """Создать таблицы в базе данных"""
        Base.metadata.create_all(self.engine)

    def add_product(self, name, category, price, quantity=0, min_stock=10,
                    barcode=None, description=None):
        """Добавить товар"""
        session = self.Session()
        try:
            product = Product(
                name=name,
                category=category,
                price=price,
                quantity=quantity,
                min_stock=min_stock,
                barcode=barcode,
                description=description
            )
            session.add(product)
            session.commit()
            session.refresh(product)
            return product
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_products(self):
        """Получить все товары"""
        session = self.Session()
        try:
            return session.query(Product).all()
        finally:
            session.close()

    def get_product_by_id(self, product_id):
        session = self.Session()
        try:
            return session.query(Product).get(product_id)
        finally:
            session.close()

    def get_customer_by_id(self, customer_id):
        session = self.Session()
        try:
            return session.query(Customer).get(customer_id)
        finally:
            session.close()

    def add_customer(self, name, phone, email, discount=0.0):
        session = self.Session()
        try:
            customer = Customer(
                name=name,
                phone=phone,
                email=email,
                discount=discount
            )
            session.add(customer)
            session.commit()
            session.refresh(customer)
            return customer
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_customers(self):
        session = self.Session()
        try:
            return session.query(Customer).all()
        finally:
            session.close()

    def record_sale(self, product_id, quantity, customer_id=None):
        """Записать продажу"""
        session = self.Session()
        try:
            product = session.query(Product).get(product_id)
            if not product:
                raise Exception("Товар не найден")
            if product.quantity < quantity:
                raise Exception(f"Недостаточно товара. В наличии: {product.quantity}")

            customer = None
            if customer_id:
                customer = session.query(Customer).get(customer_id)

            total = product.price * quantity
            if customer and customer.discount > 0:
                total = total * (1 - customer.discount / 100)

            sale = Sale(
                product_id=product_id,
                customer_id=customer_id,
                quantity=quantity,
                price=product.price,
                total=total,
                date=datetime.now()
            )

            product.quantity -= quantity

            if customer:
                customer.total_purchases += total

            session.add(sale)
            session.commit()
            session.refresh(sale)
            return sale
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def add_supply(self, supplier, product_id, quantity, cost):
        session = self.Session()
        try:
            supply = Supply(
                supplier=supplier,
                product_id=product_id,
                quantity=quantity,
                cost=cost,
                date=datetime.now()
            )

            product = session.query(Product).get(product_id)
            if product:
                product.quantity += quantity

            session.add(supply)
            session.commit()
            session.refresh(supply)
            return supply
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_low_stock_products(self):
        session = self.Session()
        try:
            return session.query(Product).filter(
                Product.quantity < Product.min_stock
            ).all()
        finally:
            session.close()

    def get_total_sales_amount(self, start_date=None, end_date=None):
        session = self.Session()
        try:
            query = session.query(func.sum(Sale.total))
            if start_date and end_date:
                query = query.filter(and_(Sale.date >= start_date, Sale.date <= end_date))
            return query.scalar() or 0
        finally:
            session.close()