"""
fastfood_gui.py — A simple Tkinter-based fast-food ordering application.

Users can pick menu items, adjust quantities, and submit their order.
"""

import tkinter as tk
from tkinter import messagebox, ttk

# ---------------------------------------------------------------------------
# Menu data
# ---------------------------------------------------------------------------

MENU = {
    "Burgers": [
        ("Classic Burger", 5.99),
        ("Cheeseburger", 6.49),
        ("Double Smash Burger", 8.99),
        ("Veggie Burger", 6.99),
    ],
    "Sides": [
        ("Small Fries", 2.49),
        ("Large Fries", 3.49),
        ("Onion Rings", 3.99),
        ("Coleslaw", 1.99),
    ],
    "Drinks": [
        ("Cola (M)", 1.99),
        ("Cola (L)", 2.49),
        ("Lemonade", 2.29),
        ("Water", 0.99),
    ],
    "Desserts": [
        ("Ice Cream Cone", 1.49),
        ("Milkshake", 3.49),
        ("Apple Pie", 1.99),
    ],
}

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------


class FastFoodApp(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Fast Food Order System")
        self.resizable(False, False)
        self._configure_styles()

        # Keep one IntVar per menu item to hold the selected quantity
        self._qty_vars: dict[str, tk.IntVar] = {}

        self._build_ui()
        self._refresh_order_summary()

    # ------------------------------------------------------------------
    # Style helpers
    # ------------------------------------------------------------------

    def _configure_styles(self) -> None:
        self.configure(bg="#f5f5f5")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Header.TLabel",
            font=("Helvetica", 18, "bold"),
            background="#d62300",
            foreground="white",
            padding=10,
        )
        style.configure(
            "Category.TLabel",
            font=("Helvetica", 11, "bold"),
            background="#f5f5f5",
        )
        style.configure("Item.TLabel", font=("Helvetica", 10), background="#f5f5f5")
        style.configure(
            "Price.TLabel",
            font=("Helvetica", 10),
            background="#f5f5f5",
            foreground="#555555",
        )
        style.configure("Total.TLabel", font=("Helvetica", 12, "bold"), background="#f5f5f5")
        style.configure("Order.TFrame", background="#ffffff", relief="solid")
        style.configure(
            "Submit.TButton",
            font=("Helvetica", 11, "bold"),
            foreground="white",
            background="#d62300",
            padding=8,
        )
        style.map("Submit.TButton", background=[("active", "#a81b00")])
        style.configure("Clear.TButton", font=("Helvetica", 10), padding=6)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        # ── Header ──────────────────────────────────────────────────────
        header = ttk.Label(self, text="🍔  Fast Food Order System", style="Header.TLabel", anchor="center")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")

        # ── Menu panel (left) ────────────────────────────────────────────
        menu_frame = ttk.Frame(self, padding=12)
        menu_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=10)

        menu_title = ttk.Label(menu_frame, text="Menu", style="Category.TLabel", font=("Helvetica", 13, "bold"))
        menu_title.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        ttk.Label(menu_frame, text="Item", style="Category.TLabel").grid(row=1, column=0, sticky="w")
        ttk.Label(menu_frame, text="Price", style="Category.TLabel").grid(row=1, column=1, sticky="e", padx=(20, 0))
        ttk.Label(menu_frame, text="Qty", style="Category.TLabel").grid(row=1, column=2, sticky="e", padx=(20, 0))

        ttk.Separator(menu_frame, orient="horizontal").grid(row=2, column=0, columnspan=3, sticky="ew", pady=4)

        current_row = 3
        for category, items in MENU.items():
            # Category heading
            ttk.Label(menu_frame, text=category, style="Category.TLabel").grid(
                row=current_row, column=0, columnspan=3, sticky="w", pady=(8, 2)
            )
            current_row += 1

            for name, price in items:
                var = tk.IntVar(value=0)
                self._qty_vars[name] = var
                var.trace_add("write", lambda *_: self._refresh_order_summary())

                ttk.Label(menu_frame, text=name, style="Item.TLabel").grid(row=current_row, column=0, sticky="w")
                ttk.Label(menu_frame, text=f"${price:.2f}", style="Price.TLabel").grid(
                    row=current_row, column=1, sticky="e", padx=(20, 0)
                )
                spinbox = ttk.Spinbox(
                    menu_frame,
                    from_=0,
                    to=20,
                    textvariable=var,
                    width=4,
                    command=self._refresh_order_summary,
                )
                spinbox.grid(row=current_row, column=2, sticky="e", padx=(20, 0), pady=2)
                current_row += 1

        # ── Order summary panel (right) ─────────────────────────────────
        summary_outer = ttk.Frame(self, padding=12)
        summary_outer.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=10)

        ttk.Label(summary_outer, text="Your Order", style="Category.TLabel", font=("Helvetica", 13, "bold")).pack(
            anchor="w", pady=(0, 8)
        )

        # Scrollable text widget for the order lines
        order_frame = ttk.Frame(summary_outer, style="Order.TFrame")
        order_frame.pack(fill="both", expand=True)

        self._order_text = tk.Text(
            order_frame,
            width=32,
            height=20,
            state="disabled",
            font=("Courier", 10),
            bg="#ffffff",
            relief="flat",
            wrap="word",
        )
        scrollbar = ttk.Scrollbar(order_frame, orient="vertical", command=self._order_text.yview)
        self._order_text.configure(yscrollcommand=scrollbar.set)
        self._order_text.pack(side="left", fill="both", expand=True, padx=4, pady=4)
        scrollbar.pack(side="right", fill="y")

        # Total label
        self._total_label = ttk.Label(summary_outer, text="Total: $0.00", style="Total.TLabel")
        self._total_label.pack(anchor="e", pady=(8, 4))

        # Name entry
        name_frame = ttk.Frame(summary_outer)
        name_frame.pack(fill="x", pady=(4, 0))
        ttk.Label(name_frame, text="Name:", style="Item.TLabel").pack(side="left")
        self._name_var = tk.StringVar()
        ttk.Entry(name_frame, textvariable=self._name_var, width=20).pack(side="left", padx=(6, 0))

        # Buttons
        btn_frame = ttk.Frame(summary_outer)
        btn_frame.pack(fill="x", pady=(10, 0))

        ttk.Button(btn_frame, text="Clear All", style="Clear.TButton", command=self._clear_order).pack(
            side="left", expand=True, fill="x", padx=(0, 4)
        )
        ttk.Button(btn_frame, text="Submit Order", style="Submit.TButton", command=self._submit_order).pack(
            side="left", expand=True, fill="x"
        )

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

    # ------------------------------------------------------------------
    # Business logic
    # ------------------------------------------------------------------

    def _get_order_lines(self) -> list[tuple[str, int, float]]:
        """Return a list of (item_name, qty, unit_price) for items with qty > 0."""
        lines = []
        for category, items in MENU.items():
            for name, price in items:
                qty = self._qty_vars[name].get()
                if qty > 0:
                    lines.append((name, qty, price))
        return lines

    def _refresh_order_summary(self) -> None:
        """Update the order text widget and total label."""
        lines = self._get_order_lines()
        total = sum(qty * price for _, qty, price in lines)

        self._order_text.configure(state="normal")
        self._order_text.delete("1.0", "end")

        if lines:
            self._order_text.insert("end", f"{'Item':<22}{'Qty':>3}{'Price':>7}\n")
            self._order_text.insert("end", "-" * 32 + "\n")
            for name, qty, price in lines:
                subtotal = qty * price
                self._order_text.insert("end", f"{name:<22}{qty:>3}  ${subtotal:>5.2f}\n")
        else:
            self._order_text.insert("end", "No items selected yet.\n")

        self._order_text.configure(state="disabled")
        self._total_label.configure(text=f"Total: ${total:.2f}")

    def _clear_order(self) -> None:
        """Reset all quantities to zero."""
        for var in self._qty_vars.values():
            var.set(0)
        self._name_var.set("")
        self._refresh_order_summary()

    def _submit_order(self) -> None:
        """Validate and submit the current order."""
        lines = self._get_order_lines()
        if not lines:
            messagebox.showwarning("No Items", "Please add at least one item to your order.")
            return

        name = self._name_var.get().strip()
        if not name:
            messagebox.showwarning("Name Required", "Please enter your name before submitting.")
            return

        total = sum(qty * price for _, qty, price in lines)
        summary_lines = [f"  {name:<22} x{qty}  ${qty * price:.2f}" for name, qty, price in lines]
        summary = "\n".join(summary_lines)

        messagebox.showinfo(
            "Order Confirmed",
            f"Thank you, {name}! 🎉\n\nYour order:\n{summary}\n\n"
            f"{'─' * 36}\n  Total: ${total:.2f}\n\nYour food will be ready shortly!",
        )
        self._clear_order()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = FastFoodApp()
    app.mainloop()
