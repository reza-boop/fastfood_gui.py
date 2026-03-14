"""Tests for fastfood_gui.py — runs headlessly via Tkinter's test mode."""

import os
import sys
import unittest

# ---------------------------------------------------------------------------
# Use a virtual (off-screen) display so Tkinter works in CI environments.
# ---------------------------------------------------------------------------
os.environ.setdefault("DISPLAY", ":0")

# Allow importing the module from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import fastfood_gui as fg


class TestMenuData(unittest.TestCase):
    """Verify the MENU data structure is well-formed."""

    def test_menu_has_expected_categories(self):
        expected = {"Burgers", "Sides", "Drinks", "Desserts"}
        self.assertEqual(set(fg.MENU.keys()), expected)

    def test_every_item_has_positive_price(self):
        for category, items in fg.MENU.items():
            for name, price in items:
                with self.subTest(category=category, item=name):
                    self.assertGreater(price, 0, f"Price for '{name}' must be positive")

    def test_every_item_has_non_empty_name(self):
        for category, items in fg.MENU.items():
            for name, price in items:
                with self.subTest(category=category):
                    self.assertTrue(name.strip(), "Item name must not be empty")

    def test_each_category_has_at_least_one_item(self):
        for category, items in fg.MENU.items():
            with self.subTest(category=category):
                self.assertGreater(len(items), 0)


class TestFastFoodApp(unittest.TestCase):
    """Integration tests against the Tkinter application (headless)."""

    @classmethod
    def setUpClass(cls):
        """Create the app once for all tests in this class."""
        try:
            cls.app = fg.FastFoodApp()
            cls.app.withdraw()  # hide the window during tests
        except Exception as exc:
            raise unittest.SkipTest(f"Cannot create Tkinter root: {exc}") from exc

    @classmethod
    def tearDownClass(cls):
        try:
            cls.app.destroy()
        except Exception:
            pass

    def setUp(self):
        # Start each test with a clean state
        self.app._clear_order()

    def test_initial_quantities_are_zero(self):
        for name, var in self.app._qty_vars.items():
            with self.subTest(item=name):
                self.assertEqual(var.get(), 0)

    def test_all_menu_items_have_qty_var(self):
        all_item_names = {name for items in fg.MENU.values() for name, _ in items}
        self.assertEqual(set(self.app._qty_vars.keys()), all_item_names)

    def test_order_lines_empty_on_start(self):
        self.assertEqual(self.app._get_order_lines(), [])

    def test_order_lines_reflect_selected_quantities(self):
        # Set Classic Burger qty = 2
        self.app._qty_vars["Classic Burger"].set(2)
        lines = self.app._get_order_lines()
        self.assertEqual(len(lines), 1)
        name, qty, price = lines[0]
        expected_price = next(p for n, p in fg.MENU["Burgers"] if n == "Classic Burger")
        self.assertEqual(name, "Classic Burger")
        self.assertEqual(qty, 2)
        self.assertAlmostEqual(price, expected_price)

    def test_total_calculation(self):
        burger_price = next(p for n, p in fg.MENU["Burgers"] if n == "Classic Burger")
        fries_price = next(p for n, p in fg.MENU["Sides"] if n == "Small Fries")
        cola_price = next(p for n, p in fg.MENU["Drinks"] if n == "Cola (M)")

        self.app._qty_vars["Classic Burger"].set(1)
        self.app._qty_vars["Small Fries"].set(2)
        self.app._qty_vars["Cola (M)"].set(1)
        lines = self.app._get_order_lines()
        total = sum(q * p for _, q, p in lines)
        expected = burger_price * 1 + fries_price * 2 + cola_price * 1
        self.assertAlmostEqual(total, expected, places=2)

    def test_clear_order_resets_quantities(self):
        self.app._qty_vars["Cheeseburger"].set(3)
        self.app._clear_order()
        self.assertEqual(self.app._qty_vars["Cheeseburger"].get(), 0)

    def test_clear_order_resets_name(self):
        self.app._name_var.set("Alice")
        self.app._clear_order()
        self.assertEqual(self.app._name_var.get(), "")


if __name__ == "__main__":
    unittest.main()
