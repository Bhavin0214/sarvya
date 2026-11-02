# File: modules/dashboard.py

import customtkinter as ctk
from database import db
# FIXED: Import ModernWidgets from the central utility file
from modules.gui_components import ModernWidgets 

class Dashboard:
    def __init__(self, master, app_instance):
        self.master = master
        self.app = app_instance 
        self.widgets = ModernWidgets()
        
        self.frame = ctk.CTkFrame(master, fg_color="transparent")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.data = self.fetch_dashboard_data()
        self.create_dashboard_ui()
    
    def fetch_dashboard_data(self):
        """Fetch summary statistics from the database"""
        
        # If DB connection fails, return mock data
        if not db.connection or not db.connection.is_connected():
            return {
                'total_products': 45, 'total_customers': 120, 'total_suppliers': 15,
                'low_stock': 8, 'sales_today': 4500.50, 'pending_invoices': 3
            }

        data = {}
        # Fetching data and handling potential None results
        data['total_products'] = db.fetch_one("SELECT COUNT(*) AS count FROM products")['count'] or 0
        data['total_customers'] = db.fetch_one("SELECT COUNT(*) AS count FROM customers")['count'] or 0
        data['total_suppliers'] = db.fetch_one("SELECT COUNT(*) AS count FROM suppliers")['count'] or 0
        data['low_stock'] = db.fetch_one("SELECT COUNT(*) AS count FROM products WHERE current_stock <= min_stock_level")['count'] or 0
        data['sales_today'] = db.fetch_one("SELECT SUM(grand_total) AS total FROM invoices WHERE invoice_date = CURDATE()")['total'] or 0.00
        data['pending_invoices'] = db.fetch_one("SELECT COUNT(*) AS count FROM invoices WHERE payment_status = 'pending'")['count'] or 0
        
        return data

    def create_dashboard_ui(self):
        
        ctk.CTkLabel(
            self.frame,
            text="Dashboard Overview",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.widgets.colors["text_primary"],
            anchor="w"
        ).pack(fill="x", pady=(0, 20))
        
        metric_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        metric_frame.pack(fill="x", pady=10)
        
        # 1. Total Products (Clickable)
        self.widgets.create_metric_card(metric_frame, "Total Products", self.data['total_products'], "📦", "primary", command=self.app.show_products).grid(row=0, column=0, padx=15, pady=15)
        # 2. Total Customers (Clickable)
        self.widgets.create_metric_card(metric_frame, "Total Customers", self.data['total_customers'], "👥", "accent_blue", command=self.app.show_customers).grid(row=0, column=1, padx=15, pady=15)
        # 3. Total Suppliers (Clickable)
        self.widgets.create_metric_card(metric_frame, "Total Suppliers", self.data['total_suppliers'], "🏢", "accent_purple", command=self.app.show_suppliers).grid(row=0, column=2, padx=15, pady=15)
        # 4. Low Stock Alerts (Clickable)
        self.widgets.create_metric_card(metric_frame, "Low Stock Alerts", self.data['low_stock'], "🚨", "accent_red", command=self.app.show_products).grid(row=0, column=3, padx=15, pady=15)
        # 5. Sales Today (Clickable)
        self.widgets.create_metric_card(metric_frame, "Sales Today (₹)", f"₹{self.data['sales_today']:.2f}", "💰", "primary_light", command=self.app.show_billing).grid(row=1, column=0, padx=15, pady=15)
        # 6. Pending Invoices (Clickable)
        self.widgets.create_metric_card(metric_frame, "Pending Invoices", self.data['pending_invoices'], "⏱️", "accent_orange", command=self.app.show_payments).grid(row=1, column=1, padx=15, pady=15)

        for i in range(4):
            metric_frame.grid_columnconfigure(i, weight=1, uniform="group1")

        ctk.CTkLabel(
            self.frame,
            text="Recent Activity & Sales Chart Placeholder",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=self.widgets.colors["text_primary"],
            anchor="w"
        ).pack(fill="x", pady=(20, 10))
        
        activity_placeholder = ctk.CTkFrame(self.frame, fg_color=self.widgets.colors["surface"], height=300, corner_radius=12)
        activity_placeholder.pack(fill="both", expand=True)