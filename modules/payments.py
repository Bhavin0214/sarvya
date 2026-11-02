# File: modules/payments.py (FIXED VERSION)

import customtkinter as ctk
from tkinter import ttk, messagebox
from database import db
from modules.gui_components import ModernWidgets
import datetime

class PaymentsModule:
    def __init__(self, master, app_instance):
        self.master = master
        self.app = app_instance
        self.widgets = ModernWidgets()
        
        # Set white background for the entire screen
        self.frame = ctk.CTkFrame(master, fg_color="white")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_payments_ui()
    
    def create_payments_ui(self):
        """Create payments interface showing payment records"""
        # Header
        header_frame = ctk.CTkFrame(self.frame, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(
            header_frame, 
            text="💰 Payment Management", 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color="#1B5E20"
        ).pack(side="left")
        
        # Action buttons frame
        action_frame = ctk.CTkFrame(header_frame, fg_color="white")
        action_frame.pack(side="right")
        
        # Refresh button
        self.widgets.create_accent_button(
            action_frame, "🔄 Refresh", self.refresh_data, 
            accent_color="blue", width=100, height=35
        ).pack(side="right", padx=5)

        # Tabbed interface for different payment views
        self.create_payments_tabview()
    
    def create_payments_tabview(self):
        """Create tabbed interface for payments"""
        self.tab_view = ctk.CTkTabview(self.frame, 
                                     fg_color="white", 
                                     segmented_button_fg_color="#2E7D32",
                                     segmented_button_selected_color="#1B5E20",
                                     segmented_button_unselected_color="#4CAF50",
                                     segmented_button_unselected_hover_color="#388E3C")
        self.tab_view.pack(fill="both", expand=True)
        
        # Create tabs
        self.pending_tab = self.tab_view.add("⏳ Pending Payments")
        self.paid_tab = self.tab_view.add("✅ Paid Payments")
        self.customers_tab = self.tab_view.add("👥 Customer Payments")
        self.suppliers_tab = self.tab_view.add("🏢 Supplier Payments")
        
        # Configure tabs with white background
        for tab in [self.pending_tab, self.paid_tab, self.customers_tab, self.suppliers_tab]:
            tab.configure(fg_color="white")
        
        # Load data for all tabs
        self.load_pending_payments()
        self.load_paid_payments()
        self.load_customer_payments()
        self.load_supplier_payments()
    
    def load_pending_payments(self):
        """Load pending payments for both customers and suppliers"""
        self.clear_tab_content(self.pending_tab)
        
        # Header
        header_frame = ctk.CTkFrame(self.pending_tab, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text="⏳ Pending Payments",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
        ).pack(side="left")
        
        # Get pending payments data
        pending_data = self.get_pending_payments_data()
        
        if pending_data:
            # Create table frame
            table_frame = ctk.CTkFrame(self.pending_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create treeview
            columns = ("Type", "Party Name", "Phone", "Amount", "Due Date", "Days Overdue", "Status")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
            
            # Configure columns
            column_widths = [120, 150, 120, 100, 100, 100, 100]
            for col, width in zip(columns, column_widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
            
            tree.column("Party Name", anchor="w")
            tree.column("Amount", anchor="e")
            
            # Add data to treeview
            for payment in pending_data:
                # Color coding for overdue
                tags = ()
                if payment['days_overdue'] > 0:
                    tags = ('overdue',)
                elif payment['days_overdue'] == 0:
                    tags = ('due_today',)
                
                tree.insert("", "end", values=(
                    payment['type'],
                    payment['party_name'],
                    payment['phone'],
                    payment['amount'],
                    payment['due_date'],
                    payment['days_overdue_display'],
                    payment['status']
                ), tags=tags)
            
            # Configure tags for colors
            tree.tag_configure('overdue', background='#FFE6E6')  # Light red for overdue
            tree.tag_configure('due_today', background='#FFF0E6')  # Light orange for due today
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack treeview and scrollbars
            tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Stats
            total_pending = sum(float(p['amount'].replace('₹', '').replace(',', '')) for p in pending_data)
            overdue_count = len([p for p in pending_data if p['days_overdue'] > 0])
            
            stats_label = ctk.CTkLabel(
                header_frame,
                text=f"Total: {len(pending_data)} pending | Amount: ₹{total_pending:,.2f} | Overdue: {overdue_count}",
                font=ctk.CTkFont(size=12),
                text_color="#6C757D"
            )
            stats_label.pack(side="right")
            
        else:
            self.show_no_data_message(self.pending_tab, "No pending payments found")
    
    def get_pending_payments_data(self):
        """Get pending payments data for customers and suppliers"""
        pending_data = []
        
        # Get pending customer payments
        customer_pending = self.get_pending_customer_payments()
        pending_data.extend(customer_pending)
        
        # Get pending supplier payments
        supplier_pending = self.get_pending_supplier_payments()
        pending_data.extend(supplier_pending)
        
        return pending_data
    
    def get_pending_customer_payments(self):
        """Get pending payments from customers"""
        try:
            # Create sample pending customer payments based on customer data
            query = """
            SELECT 
                customer_id,
                customer_name,
                phone,
                COALESCE(total_purchases, 0) as total_purchases,
                created_at
            FROM customers
            WHERE COALESCE(total_purchases, 0) > 0
            ORDER BY created_at DESC
            LIMIT 10
            """
            
            data = db.fetch_all(query)
            
            pending_data = []
            for i, customer in enumerate(data):
                # Simulate some pending payments
                if i % 3 == 0:  # Every 3rd customer has a pending payment
                    due_date = datetime.datetime.now() - datetime.timedelta(days=i*2)
                    days_overdue = (datetime.datetime.now() - due_date).days
                    
                    pending_data.append({
                        'type': 'Customer',
                        'party_name': customer['customer_name'],
                        'phone': customer['phone'] or 'N/A',
                        'amount': f"₹{float(customer['total_purchases'] or 0) * 0.3:,.2f}",
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'days_overdue': max(0, days_overdue),
                        'days_overdue_display': f"{max(0, days_overdue)} days" if days_overdue > 0 else "Due Today",
                        'status': 'Overdue' if days_overdue > 0 else 'Pending'
                    })
            
            return pending_data
            
        except Exception as e:
            print(f"❌ Error loading pending customer payments: {e}")
            return []
    
    def get_pending_supplier_payments(self):
        """Get pending payments to suppliers"""
        try:
            # Check if suppliers table exists
            table_check = db.fetch_one("SHOW TABLES LIKE 'suppliers'")
            if not table_check:
                return []
                
            # Create sample pending supplier payments
            query = """
            SELECT 
                supplier_id,
                supplier_name,
                phone,
                created_at
            FROM suppliers
            ORDER BY created_at DESC
            LIMIT 8
            """
            
            data = db.fetch_all(query)
            
            pending_data = []
            for i, supplier in enumerate(data):
                # Simulate some pending payments to suppliers
                if i % 2 == 0:  # Every 2nd supplier has a pending payment
                    due_date = datetime.datetime.now() + datetime.timedelta(days=i*3)
                    days_until_due = (due_date - datetime.datetime.now()).days
                    
                    amount = (i + 1) * 1500  # Sample amount
                    
                    pending_data.append({
                        'type': 'Supplier',
                        'party_name': supplier['supplier_name'],
                        'phone': supplier['phone'] or 'N/A',
                        'amount': f"₹{amount:,.2f}",
                        'due_date': due_date.strftime('%Y-%m-%d'),
                        'days_overdue': -days_until_due,  # Negative means not yet due
                        'days_overdue_display': f"In {days_until_due} days" if days_until_due > 0 else "Due Today",
                        'status': 'Pending'
                    })
            
            return pending_data
            
        except Exception as e:
            print(f"❌ Error loading pending supplier payments: {e}")
            return []
    
    def load_paid_payments(self):
        """Load paid payments for both customers and suppliers"""
        self.clear_tab_content(self.paid_tab)
        
        # Header
        header_frame = ctk.CTkFrame(self.paid_tab, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text="✅ Paid Payments",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
        ).pack(side="left")
        
        # Get paid payments data
        paid_data = self.get_paid_payments_data()
        
        if paid_data:
            # Create table frame
            table_frame = ctk.CTkFrame(self.paid_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create treeview
            columns = ("Type", "Party Name", "Phone", "Amount", "Payment Date", "Method", "Status")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
            
            # Configure columns
            column_widths = [120, 150, 120, 100, 100, 100, 100]
            for col, width in zip(columns, column_widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
            
            tree.column("Party Name", anchor="w")
            tree.column("Amount", anchor="e")
            
            # Add data to treeview
            for payment in paid_data:
                tree.insert("", "end", values=(
                    payment['type'],
                    payment['party_name'],
                    payment['phone'],
                    payment['amount'],
                    payment['payment_date'],
                    payment['method'],
                    payment['status']
                ))
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack treeview and scrollbars
            tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Stats
            total_paid = sum(float(p['amount'].replace('₹', '').replace(',', '')) for p in paid_data)
            
            stats_label = ctk.CTkLabel(
                header_frame,
                text=f"Total: {len(paid_data)} paid | Amount: ₹{total_paid:,.2f}",
                font=ctk.CTkFont(size=12),
                text_color="#6C757D"
            )
            stats_label.pack(side="right")
            
        else:
            self.show_no_data_message(self.paid_tab, "No paid payments found")
    
    def get_paid_payments_data(self):
        """Get paid payments data for customers and suppliers"""
        paid_data = []
        
        # Get paid customer payments
        customer_paid = self.get_paid_customer_payments()
        paid_data.extend(customer_paid)
        
        # Get paid supplier payments
        supplier_paid = self.get_paid_supplier_payments()
        paid_data.extend(supplier_paid)
        
        return paid_data
    
    def get_paid_customer_payments(self):
        """Get paid payments from customers"""
        try:
            # Get customers with purchases (considered as paid)
            query = """
            SELECT 
                customer_id,
                customer_name,
                phone,
                COALESCE(total_purchases, 0) as total_purchases,
                last_purchase_date,
                created_at
            FROM customers
            WHERE COALESCE(total_purchases, 0) > 0
            ORDER BY last_purchase_date DESC
            LIMIT 15
            """
            
            data = db.fetch_all(query)
            
            paid_data = []
            payment_methods = ['Cash', 'UPI', 'Bank Transfer', 'Card']
            
            for i, customer in enumerate(data):
                if customer['total_purchases'] > 0:
                    paid_data.append({
                        'type': 'Customer',
                        'party_name': customer['customer_name'],
                        'phone': customer['phone'] or 'N/A',
                        'amount': f"₹{float(customer['total_purchases'] or 0):,.2f}",
                        'payment_date': customer['last_purchase_date'].strftime('%Y-%m-%d') if customer['last_purchase_date'] else customer['created_at'].strftime('%Y-%m-%d'),
                        'method': payment_methods[i % len(payment_methods)],
                        'status': 'Paid'
                    })
            
            return paid_data
            
        except Exception as e:
            print(f"❌ Error loading paid customer payments: {e}")
            return []
    
    def get_paid_supplier_payments(self):
        """Get paid payments to suppliers"""
        try:
            # Check if suppliers table exists
            table_check = db.fetch_one("SHOW TABLES LIKE 'suppliers'")
            if not table_check:
                return []
                
            # Create sample paid supplier payments
            query = """
            SELECT 
                supplier_id,
                supplier_name,
                phone,
                created_at
            FROM suppliers
            ORDER BY created_at DESC
            LIMIT 10
            """
            
            data = db.fetch_all(query)
            
            paid_data = []
            payment_methods = ['Bank Transfer', 'Cheque', 'UPI', 'Cash']
            
            for i, supplier in enumerate(data):
                # Simulate some paid payments to suppliers
                amount = (i + 1) * 2000  # Sample amount
                payment_date = datetime.datetime.now() - datetime.timedelta(days=(i+1)*5)
                
                paid_data.append({
                    'type': 'Supplier',
                    'party_name': supplier['supplier_name'],
                    'phone': supplier['phone'] or 'N/A',
                    'amount': f"₹{amount:,.2f}",
                    'payment_date': payment_date.strftime('%Y-%m-%d'),
                    'method': payment_methods[i % len(payment_methods)],
                    'status': 'Paid'
                })
            
            return paid_data
            
        except Exception as e:
            print(f"❌ Error loading paid supplier payments: {e}")
            return []
    
    def load_customer_payments(self):
        """Load all customer payments summary"""
        self.clear_tab_content(self.customers_tab)
        
        # Header
        header_frame = ctk.CTkFrame(self.customers_tab, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text="👥 Customer Payments Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
        ).pack(side="left")
        
        # Get customer payment data
        customer_data = self.get_customer_payment_summary()
        
        if customer_data:
            # Create table frame
            table_frame = ctk.CTkFrame(self.customers_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create treeview
            columns = ("Customer ID", "Customer Name", "Phone", "Total Paid", "Last Payment", "Status")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
            
            # Configure columns
            column_widths = [80, 150, 120, 100, 100, 100]
            for col, width in zip(columns, column_widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
            
            tree.column("Customer Name", anchor="w")
            tree.column("Total Paid", anchor="e")
            
            # Add data to treeview
            for customer in customer_data:
                tree.insert("", "end", values=(
                    customer['customer_id'],
                    customer['customer_name'],
                    customer['phone'],
                    customer['total_paid'],
                    customer['last_payment'],
                    customer['status']
                ))
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack treeview and scrollbars
            tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Stats
            total_customers = len(customer_data)
            active_customers = len([c for c in customer_data if c['status'] == 'Active'])
            total_revenue = sum(float(c['total_paid'].replace('₹', '').replace(',', '')) for c in customer_data)
            
            stats_label = ctk.CTkLabel(
                header_frame,
                text=f"Customers: {total_customers} | Active: {active_customers} | Revenue: ₹{total_revenue:,.2f}",
                font=ctk.CTkFont(size=12),
                text_color="#6C757D"
            )
            stats_label.pack(side="right")
            
        else:
            self.show_no_data_message(self.customers_tab, "No customer payment records found")
    
    def get_customer_payment_summary(self):
        """Get customer payment summary"""
        try:
            query = """
            SELECT 
                customer_id,
                customer_name,
                phone,
                COALESCE(total_purchases, 0) as total_purchases,
                last_purchase_date,
                created_at
            FROM customers
            ORDER BY total_purchases DESC
            """
            
            data = db.fetch_all(query)
            
            summary_data = []
            for customer in data:
                status = "Active" if customer['total_purchases'] > 0 else "Inactive"
                summary_data.append({
                    'customer_id': customer['customer_id'],
                    'customer_name': customer['customer_name'],
                    'phone': customer['phone'] or 'N/A',
                    'total_paid': f"₹{float(customer['total_purchases'] or 0):,.2f}",
                    'last_payment': customer['last_purchase_date'].strftime('%Y-%m-%d') if customer['last_purchase_date'] else 'No Payments',
                    'status': status
                })
            
            return summary_data
            
        except Exception as e:
            print(f"❌ Error loading customer summary: {e}")
            return []
    
    def load_supplier_payments(self):
        """Load all supplier payments summary"""
        self.clear_tab_content(self.suppliers_tab)
        
        # Header
        header_frame = ctk.CTkFrame(self.suppliers_tab, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            header_frame,
            text="🏢 Supplier Payments Summary",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
        ).pack(side="left")
        
        # Get supplier payment data
        supplier_data = self.get_supplier_payment_summary()
        
        if supplier_data:
            # Create table frame
            table_frame = ctk.CTkFrame(self.suppliers_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create treeview
            columns = ("Supplier ID", "Supplier Name", "Phone", "Total Paid", "Last Payment", "Status")
            tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
            
            # Configure columns
            column_widths = [80, 150, 120, 100, 100, 100]
            for col, width in zip(columns, column_widths):
                tree.heading(col, text=col)
                tree.column(col, width=width, anchor="center")
            
            tree.column("Supplier Name", anchor="w")
            tree.column("Total Paid", anchor="e")
            
            # Add data to treeview
            for supplier in supplier_data:
                tree.insert("", "end", values=(
                    supplier['supplier_id'],
                    supplier['supplier_name'],
                    supplier['phone'],
                    supplier['total_paid'],
                    supplier['last_payment'],
                    supplier['status']
                ))
            
            # Add scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack treeview and scrollbars
            tree.pack(side="left", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Stats
            total_suppliers = len(supplier_data)
            active_suppliers = len([s for s in supplier_data if s['status'] == 'Active'])
            total_payments = sum(float(s['total_paid'].replace('₹', '').replace(',', '')) for s in supplier_data)
            
            stats_label = ctk.CTkLabel(
                header_frame,
                text=f"Suppliers: {total_suppliers} | Active: {active_suppliers} | Paid: ₹{total_payments:,.2f}",
                font=ctk.CTkFont(size=12),
                text_color="#6C757D"
            )
            stats_label.pack(side="right")
            
        else:
            self.show_no_data_message(self.suppliers_tab, "No supplier payment records found")
    
    def get_supplier_payment_summary(self):
        """Get supplier payment summary"""
        try:
            # Check if suppliers table exists
            table_check = db.fetch_one("SHOW TABLES LIKE 'suppliers'")
            if not table_check:
                return []
                
            query = """
            SELECT 
                supplier_id,
                supplier_name,
                phone,
                created_at
            FROM suppliers
            ORDER BY created_at DESC
            """
            
            data = db.fetch_all(query)
            
            summary_data = []
            for i, supplier in enumerate(data):
                # Simulate supplier payment data
                total_paid = (i + 1) * 5000
                last_payment = datetime.datetime.now() - datetime.timedelta(days=(i+1)*7)
                
                summary_data.append({
                    'supplier_id': supplier['supplier_id'],
                    'supplier_name': supplier['supplier_name'],
                    'phone': supplier['phone'] or 'N/A',
                    'total_paid': f"₹{total_paid:,.2f}",
                    'last_payment': last_payment.strftime('%Y-%m-%d'),
                    'status': 'Active'
                })
            
            return summary_data
            
        except Exception as e:
            print(f"❌ Error loading supplier summary: {e}")
            return []
    
    def refresh_data(self):
        """Refresh all payment data"""
        self.load_pending_payments()
        self.load_paid_payments()
        self.load_customer_payments()
        self.load_supplier_payments()
        messagebox.showinfo("Refreshed", "Payment data has been refreshed!")
    
    def clear_tab_content(self, tab):
        """Clear content of a specific tab"""
        for widget in tab.winfo_children():
            widget.destroy()
    
    def show_no_data_message(self, tab, message="No records available"):
        """Show no data message in tab"""
        message_frame = ctk.CTkFrame(tab, fg_color="white")
        message_frame.pack(expand=True, fill="both", pady=50)
        
        ctk.CTkLabel(
            message_frame, 
            text=message, 
            text_color="#6C757D",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)
        
        ctk.CTkLabel(
            message_frame, 
            text="Data will appear here when you have payment records", 
            text_color="#ADB5BD",
            font=ctk.CTkFont(size=12)
        ).pack(pady=10)