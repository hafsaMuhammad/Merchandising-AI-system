"""
Management command to seed the database with demo data.

Usage: python manage.py seed_demo
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.stores.models import Store, Product, StoreProduct
from apps.visits.models import Visit
from datetime import date, timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with demo stores, products, users and visits"

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding demo data...")

        # Admin
        admin, _ = User.objects.get_or_create(
            username="admin",
            defaults={"email": "admin@shelfscan.io", "role": "admin", "is_staff": True, "is_superuser": True}
        )
        admin.set_password("admin123")
        admin.save()

        # Agents
        agents = []
        for i in range(1, 4):
            agent, _ = User.objects.get_or_create(
                username=f"agent{i}",
                defaults={"email": f"agent{i}@shelfscan.io", "role": "agent",
                          "first_name": f"Agent", "last_name": f"#{i}"}
            )
            agent.set_password("agent123")
            agent.save()
            agents.append(agent)

        # Stores
        stores_data = [
            {"name": "CityMart Downtown", "code": "CMD01", "address": "12 Tahrir Sq", "city": "Cairo"},
            {"name": "FreshStop Heliopolis", "code": "FSH02", "address": "44 Nozha St", "city": "Cairo"},
            {"name": "MegaMart Alexandria", "code": "MMA03", "address": "7 Corniche Rd", "city": "Alexandria"},
        ]
        stores = []
        for s in stores_data:
            store, _ = Store.objects.get_or_create(code=s["code"], defaults=s)
            stores.append(store)

        # Products
        products_data = [
            ("Coca-Cola 330ml", "CC330", "Coca-Cola", "Beverages"),
            ("Pepsi 500ml", "PP500", "Pepsi", "Beverages"),
            ("Lay's Classic Chips", "LYS001", "Lay's", "Snacks"),
            ("Pringles Original", "PRG001", "Pringles", "Snacks"),
            ("Nescafé Gold 200g", "NSC200", "Nestlé", "Hot Drinks"),
            ("Lipton Yellow Label", "LPT100", "Unilever", "Hot Drinks"),
        ]
        products = []
        for name, sku, brand, cat in products_data:
            p, _ = Product.objects.get_or_create(sku=sku, defaults={
                "name": name, "brand": brand, "category": cat
            })
            products.append(p)

        # Assign products to stores
        for store in stores:
            for product in random.sample(products, k=4):
                StoreProduct.objects.get_or_create(store=store, product=product,
                                                   defaults={"expected_facing": random.randint(1, 4)})

        # Visits
        for i, store in enumerate(stores):
            Visit.objects.get_or_create(
                agent=agents[i % len(agents)],
                store=store,
                scheduled_date=date.today() + timedelta(days=i),
                defaults={"status": "planned"}
            )

        self.stdout.write(self.style.SUCCESS(
            f"Done! Created {len(agents)} agents, {len(stores)} stores, {len(products)} products."
        ))
        self.stdout.write("Login: admin / admin123  |  agent1 / agent123")
