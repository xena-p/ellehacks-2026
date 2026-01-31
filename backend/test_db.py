#!/usr/bin/env python
import os
import django

# Load Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from game.models import TestItem

def test_database():
    print("Testing database connection...")

    # Create a test record
    item = TestItem.objects.create(name="Hello Neon")
    print(f"Created record: id={item.id}, name={item.name}")

    # Fetch all records
    all_items = TestItem.objects.all()
    print(f"Total records in TestItem table: {all_items.count()}")
    print("Records:")
    for i in all_items:
        print(f"- id={i.id}, name={i.name}")

if __name__ == "__main__":
    test_database()
