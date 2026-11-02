# File: modules/billing.py (FIXED VERSION)

import customtkinter as ctk
from tkinter import ttk, messagebox
from database import db
from datetime import datetime
import random
from num2words import num2words
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import webbrowser
from tkcalendar import DateEntry
import tkinter as tk

class BillingModule:
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.cart_items = []
        self.products = []
        self.customers = []
        self.categories = []
        self.setup_ui()
        self.load_categories()
        self.load_customers()
        self.load_products()
    
    def setup_ui(self):
        """Setup advanced billing UI"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="#F8F9FA")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="🧾 Billing & Invoices",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2E7D32"
        ).pack(side="left")
        
        # Action buttons in header
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")
        
        ctk.CTkButton(
            button_frame,
            text="📋 View Invoices",
            command=self.show_invoices_dialog,
            width=140,
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="➕ Add Customer",
            command=self.show_add_customer_dialog,
            width=140,
            height=40,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="right", padx=5)
        
        # Two column layout
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left column - Customer & Products
        left_frame = ctk.CTkFrame(content_frame, corner_radius=12, border_width=1, fg_color="white")
        left_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Customer section
        self.setup_customer_section(left_frame)
        
        # Products section
        self.setup_products_section(left_frame)
        
        # Right column - Cart & Totals
        right_frame = ctk.CTkFrame(content_frame, corner_radius=12, border_width=1, fg_color="white")
        right_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Cart section
        self.setup_cart_section(right_frame)
        
        # Totals section
        self.setup_totals_section(right_frame)
        
        self._update_cart_tree()
        self.update_totals()

    def setup_customer_section(self, parent):
        """Setup customer details section with enhanced features"""
        customer_frame = ctk.CTkFrame(parent, fg_color="transparent")
        customer_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(
            customer_frame,
            text="👤 Customer Details",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2E7D32"
        ).pack(anchor="w", pady=(0, 10))
        
        # Invoice number and date
        invoice_frame = ctk.CTkFrame(customer_frame, fg_color="transparent")
        invoice_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(invoice_frame, text="Invoice No:", width=80).pack(side="left")
        self.invoice_var = ctk.StringVar()
        self.invoice_entry = ctk.CTkEntry(invoice_frame, textvariable=self.invoice_var, height=35)
        self.invoice_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.generate_invoice_number()
        
        ctk.CTkLabel(invoice_frame, text="Date:", width=50).pack(side="left", padx=(20, 0))
        
        # Calendar date picker
        date_frame = ctk.CTkFrame(invoice_frame, fg_color="transparent", width=120, height=35)
        date_frame.pack(side="left", padx=(10, 0))
        date_frame.pack_propagate(False)
        
        # Create a tkinter frame inside CTkFrame for DateEntry
        date_tk_frame = tk.Frame(date_frame, bg="white")
        date_tk_frame.pack(fill="both", expand=True)
        
        self.date_entry = DateEntry(
            date_tk_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date_entry.set_date(datetime.now())
        self.date_entry.pack(fill="both", expand=True)
        
        # Payment status
        payment_frame = ctk.CTkFrame(customer_frame, fg_color="transparent")
        payment_frame.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(payment_frame, text="Payment Status:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        self.payment_status_var = ctk.StringVar(value="paid")
        payment_status_combo = ctk.CTkComboBox(
            payment_frame,
            variable=self.payment_status_var,
            values=["paid", "pending"],
            height=35,
            width=120
        )
        payment_status_combo.pack(side="left", padx=(10, 0))
        
        # Customer selection with search and suggestions
        customer_selection_frame = ctk.CTkFrame(customer_frame, fg_color="transparent")
        customer_selection_frame.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(customer_selection_frame, text="Select Customer:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        self.customer_var = ctk.StringVar()
        self.customer_combo = ctk.CTkComboBox(
            customer_selection_frame,
            variable=self.customer_var,
            values=[],
            height=35,
            command=self.on_customer_select
        )
        self.customer_combo.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        # Bind key release for customer search
        self.customer_combo.bind('<KeyRelease>', self.filter_customers)
        
        # New customer fields
        new_customer_frame = ctk.CTkFrame(customer_frame, fg_color="transparent")
        new_customer_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(new_customer_frame, text="New Customer Name:").pack(side="left")
        self.new_customer_name = ctk.CTkEntry(new_customer_frame, placeholder_text="Enter new customer name", height=35)
        self.new_customer_name.pack(side="left", fill="x", expand=True, padx=(10, 10))
        
        ctk.CTkLabel(new_customer_frame, text="Phone:").pack(side="left")
        self.new_customer_phone = ctk.CTkEntry(new_customer_frame, placeholder_text="Phone number", height=35, width=120)
        self.new_customer_phone.pack(side="left", padx=(10, 0))
        
        # Quick customer info display
        self.customer_info_label = ctk.CTkLabel(
            customer_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#6C757D",
            wraplength=400
        )
        self.customer_info_label.pack(anchor="w", pady=(5, 0))

    def setup_products_section(self, parent):
        """Setup products selection section with enhanced features"""
        products_frame = ctk.CTkFrame(parent, fg_color="transparent")
        products_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            products_frame,
            text="📦 Add Products",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2E7D32"
        ).pack(anchor="w", pady=(0, 10))
        
        # Category filter with suggestions
        category_frame = ctk.CTkFrame(products_frame, fg_color="transparent")
        category_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(category_frame, text="Category:").pack(side="left")
        self.category_var = ctk.StringVar()
        self.category_combo = ctk.CTkComboBox(
            category_frame,
            variable=self.category_var,
            values=["All Categories"],
            height=35,
            command=self.on_category_select
        )
        self.category_combo.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Product selection with search and auto-complete
        product_selection_frame = ctk.CTkFrame(products_frame, fg_color="transparent")
        product_selection_frame.pack(fill="x", pady=(15, 5))
        
        ctk.CTkLabel(product_selection_frame, text="Product:", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        self.product_var = ctk.StringVar()
        self.product_combo = ctk.CTkComboBox(
            product_selection_frame,
            variable=self.product_var,
            values=[],
            height=35
        )
        self.product_combo.pack(side="left", fill="x", expand=True, padx=(10, 0))
        
        # Bind product selection to auto-fill price
        self.product_combo.bind('<<ComboboxSelected>>', self.auto_fill_product_price)
        self.product_combo.bind('<KeyRelease>', self.filter_products)
        
        # Product info display
        self.product_info_frame = ctk.CTkFrame(products_frame, fg_color="#F8F9FA", corner_radius=8)
        self.product_info_frame.pack(fill="x", pady=10)
        
        self.product_info_label = ctk.CTkLabel(
            self.product_info_frame,
            text="Select a product to see details",
            font=ctk.CTkFont(size=11),
            text_color="#6C757D"
        )
        self.product_info_label.pack(padx=10, pady=8)
        
        # Quantity and price
        quantity_price_frame = ctk.CTkFrame(products_frame, fg_color="transparent")
        quantity_price_frame.pack(fill="x", pady=10)
        
        # Quantity
        ctk.CTkLabel(quantity_price_frame, text="Quantity:").pack(side="left")
        self.quantity_var = ctk.StringVar(value="1")
        self.quantity_entry = ctk.CTkEntry(quantity_price_frame, textvariable=self.quantity_var, width=80, height=35)
        self.quantity_entry.pack(side="left", padx=(10, 20))
        self.quantity_entry.bind('<KeyRelease>', self.calculate_item_total)
        
        # Price
        ctk.CTkLabel(quantity_price_frame, text="Price (₹):").pack(side="left")
        self.price_var = ctk.StringVar()
        self.price_entry = ctk.CTkEntry(quantity_price_frame, textvariable=self.price_var, width=100, height=35)
        self.price_entry.pack(side="left", padx=(10, 0))
        self.price_entry.bind('<KeyRelease>', self.calculate_item_total)
        
        # Item total
        ctk.CTkLabel(quantity_price_frame, text="Item Total:").pack(side="left", padx=(20, 0))
        self.item_total_var = ctk.StringVar(value="₹0.00")
        self.item_total_label = ctk.CTkLabel(
            quantity_price_frame,
            textvariable=self.item_total_var,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#2E7D32",
            width=80
        )
        self.item_total_label.pack(side="left", padx=(10, 0))
        
        # Add to cart button
        ctk.CTkButton(
            products_frame,
            text="➕ Add to Cart",
            command=self.add_to_cart,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(fill="x", pady=(10, 0))

    def setup_cart_section(self, parent):
        """Setup cart items section with enhanced features"""
        cart_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cart_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(
            cart_frame,
            text="🛒 Cart Items",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#2E7D32"
        ).pack(anchor="w", pady=(0, 10))
        
        # Cart table with white background
        cart_table_frame = ctk.CTkFrame(cart_frame, fg_color="white")
        cart_table_frame.pack(fill="both", expand=True)
        
        cart_columns = ("Product", "Category", "Price", "Qty", "Total", "Actions")
        self.cart_tree = ttk.Treeview(cart_table_frame, columns=cart_columns, show="headings", height=10)
        
        # Configure style
        style = ttk.Style()
        style.configure("Treeview", 
                       background="white",
                       foreground="black",
                       fieldbackground="white",
                       rowheight=25)
        style.configure("Treeview.Heading",
                       background="#f0f0f0",
                       foreground="black",
                       font=('Helvetica', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#4CAF50')])
        
        col_widths = [150, 100, 80, 60, 80, 80]
        for col, width in zip(cart_columns, col_widths):
            self.cart_tree.heading(col, text=col)
            self.cart_tree.column(col, width=width, anchor="center")
        
        self.cart_tree.column("Product", anchor="w")
        self.cart_tree.column("Price", anchor="e")
        self.cart_tree.column("Total", anchor="e")
        
        # Scrollbars
        cart_scroll_v = ttk.Scrollbar(cart_table_frame, orient="vertical", command=self.cart_tree.yview)
        cart_scroll_h = ttk.Scrollbar(cart_table_frame, orient="horizontal", command=self.cart_tree.xview)
        self.cart_tree.configure(yscrollcommand=cart_scroll_v.set, xscrollcommand=cart_scroll_h.set)
        
        self.cart_tree.pack(side="top", fill="both", expand=True)
        cart_scroll_v.pack(side="right", fill="y")
        cart_scroll_h.pack(side="bottom", fill="x")
        
        # Bind double-click to edit cart item
        self.cart_tree.bind('<Double-1>', self.edit_cart_item)
        
        # Cart actions
        cart_actions_frame = ctk.CTkFrame(cart_frame, fg_color="transparent")
        cart_actions_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            cart_actions_frame,
            text="✏️ Edit Selected",
            command=lambda: self.edit_cart_item(None),
            width=120,
            height=35,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            cart_actions_frame,
            text="🗑️ Remove Selected",
            command=self.remove_from_cart,
            width=140,
            height=35,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            cart_actions_frame,
            text="🚮 Clear Cart",
            command=self.clear_cart,
            width=100,
            height=35,
            fg_color="#F44336",
            hover_color="#D32F2F"
        ).pack(side="left")

    def setup_totals_section(self, parent):
        """Setup totals and actions section"""
        totals_frame = ctk.CTkFrame(parent, fg_color="transparent")
        totals_frame.pack(fill="x", padx=15, pady=15)
        
        # Totals display
        totals_display_frame = ctk.CTkFrame(totals_frame, fg_color="#F8F9FA", corner_radius=8)
        totals_display_frame.pack(fill="x", pady=(0, 15))
        
        self.subtotal_label = ctk.CTkLabel(
            totals_display_frame,
            text="Subtotal: ₹0.00",
            font=ctk.CTkFont(size=14),
            text_color="#6C757D"
        )
        self.subtotal_label.pack(anchor="e", padx=15, pady=5)
        
        self.tax_label = ctk.CTkLabel(
            totals_display_frame,
            text="Tax (18% GST): ₹0.00",
            font=ctk.CTkFont(size=14),
            text_color="#6C757D"
        )
        self.tax_label.pack(anchor="e", padx=15, pady=5)
        
        self.grand_total_label = ctk.CTkLabel(
            totals_display_frame,
            text="Grand Total: ₹0.00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2E7D32"
        )
        self.grand_total_label.pack(anchor="e", padx=15, pady=5)
        
        self.amount_words_label = ctk.CTkLabel(
            totals_display_frame,
            text="Zero Rupees Only",
            font=ctk.CTkFont(size=12, slant="italic"),
            text_color="#6C757D",
            wraplength=400
        )
        self.amount_words_label.pack(anchor="e", padx=15, pady=(0, 10))
        
        # Action buttons
        button_frame = ctk.CTkFrame(totals_frame, fg_color="transparent")
        button_frame.pack(fill="x")
        
        ctk.CTkButton(
            button_frame,
            text="📄 Generate & Download PDF",
            command=self.generate_invoice_pdf,
            height=45,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(fill="x", pady=5)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save Invoice",
            command=self.save_invoice,
            height=40,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(fill="x", pady=5)

    # ========== CORE FUNCTIONALITY METHODS ==========

    def load_categories(self):
        """Load product categories from database"""
        try:
            categories = db.fetch_all("SELECT category_id, category_name FROM categories ORDER BY category_name")
            self.categories = categories
            category_names = ["All Categories"] + [cat['category_name'] for cat in categories]
            self.category_combo.configure(values=category_names)
            self.category_combo.set("All Categories")
        except Exception as e:
            print(f"Error loading categories: {e}")

    def load_customers(self):
        """Load customers from database"""
        try:
            customers = db.fetch_all("SELECT customer_id, customer_name, phone, email FROM customers ORDER BY customer_name")
            self.customers = customers
            customer_names = [f"{cust['customer_name']} ({cust.get('phone', 'N/A')})" for cust in customers]
            self.customer_combo.configure(values=customer_names)
        except Exception as e:
            print(f"Error loading customers: {e}")

    def load_products(self):
        """Load products from database with proper error handling"""
        try:
            # Simple query without product_code
            query = """
            SELECT p.product_id, p.product_name, p.selling_price, 
                   p.current_stock, c.category_name
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.category_id 
            ORDER BY p.product_name
            """
            self.products = db.fetch_all(query)
            print(f"✅ Loaded {len(self.products)} products successfully")
            
            # Create product names for combobox
            product_names = []
            for p in self.products:
                product_name = f"{p['product_name']} (₹{p.get('selling_price', 0):.2f})"
                product_names.append(product_name)
            
            self.product_combo.configure(values=product_names)
            print(f"✅ Added {len(product_names)} products to combobox")
            
        except Exception as e:
            print(f"❌ Error loading products: {e}")
            # Fallback to empty list
            self.products = []
            self.product_combo.configure(values=[])
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")

    def generate_invoice_number(self):
        """Generate unique invoice number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_num = random.randint(100, 999)
        invoice_number = f"INV-{timestamp}-{random_num}"
        self.invoice_var.set(invoice_number)

    def on_category_select(self, choice):
        """Handle category selection"""
        self.filter_products()

    def on_customer_select(self, choice):
        """When customer is selected, show their information"""
        if not choice:
            return
        
        # Extract customer name from display text
        customer_name = choice.split(' (')[0]
        
        for customer in self.customers:
            if customer['customer_name'] == customer_name:
                info_text = f"📞 {customer.get('phone', 'N/A')}"
                if customer.get('email'):
                    info_text += f" | 📧 {customer['email']}"
                self.customer_info_label.configure(text=info_text)
                break

    def filter_customers(self, event=None):
        """Filter customers based on search input"""
        search_term = self.customer_combo.get().lower()
        if not search_term:
            self.load_customers()
            return
        
        filtered_customers = [cust for cust in self.customers 
                            if search_term in cust['customer_name'].lower() 
                            or search_term in cust.get('phone', '')]
        
        customer_names = [f"{cust['customer_name']} ({cust.get('phone', 'N/A')})" 
                         for cust in filtered_customers]
        self.customer_combo.configure(values=customer_names)

    def filter_products(self, event=None):
        """Filter products based on search input"""
        search_term = self.product_combo.get().lower()
        category = self.category_var.get()
        
        if not search_term and category == "All Categories":
            self.load_products()
            return
        
        filtered_products = self.products.copy()
        
        # Filter by category
        if category != "All Categories":
            filtered_products = [p for p in filtered_products 
                               if p.get('category_name') == category]
        
        # Filter by search term
        if search_term:
            filtered_products = [p for p in filtered_products 
                               if search_term in p['product_name'].lower()]
        
        product_names = [f"{p['product_name']} (₹{p.get('selling_price', 0):.2f})" 
                        for p in filtered_products]
        self.product_combo.configure(values=product_names)

    def auto_fill_product_price(self, event=None):
        """Auto-fill price when product is selected"""
        product_name = self.product_combo.get()
        if not product_name:
            return
        
        # Extract product name without price
        clean_product_name = product_name.split(' (₹')[0]
        
        for product in self.products:
            if product['product_name'] == clean_product_name:
                self.price_var.set(str(product.get('selling_price', 0)))
                self.calculate_item_total()
                
                # Show product info
                info_text = f"Stock: {product.get('current_stock', 0)} | "
                info_text += f"Category: {product.get('category_name', 'N/A')}"
                
                self.product_info_label.configure(text=info_text)
                break

    def calculate_item_total(self, event=None):
        """Calculate item total based on quantity and price"""
        try:
            quantity = float(self.quantity_var.get() or 0)
            price = float(self.price_var.get() or 0)
            total = quantity * price
            self.item_total_var.set(f"₹{total:.2f}")
        except ValueError:
            self.item_total_var.set("₹0.00")

    def add_to_cart(self):
        """Add product to cart"""
        try:
            product_name = self.product_combo.get()
            if not product_name:
                messagebox.showwarning("Warning", "Please select a product!")
                return
            
            # Extract product name without price
            clean_product_name = product_name.split(' (₹')[0]
            
            quantity = float(self.quantity_var.get() or 0)
            price = float(self.price_var.get() or 0)
            
            if quantity <= 0:
                messagebox.showwarning("Warning", "Please enter a valid quantity!")
                return
            
            if price <= 0:
                messagebox.showwarning("Warning", "Please enter a valid price!")
                return
            
            # Find product details
            product_details = None
            for product in self.products:
                if product['product_name'] == clean_product_name:
                    product_details = product
                    break
            
            if not product_details:
                messagebox.showerror("Error", "Product not found!")
                return
            
            # Add to cart
            cart_item = {
                'product_id': product_details['product_id'],
                'product_name': clean_product_name,
                'category_name': product_details.get('category_name', 'N/A'),
                'price': price,
                'quantity': quantity,
                'subtotal': quantity * price
            }
            
            self.cart_items.append(cart_item)
            self._update_cart_tree()
            self.update_totals()
            
            # Clear product selection
            self.product_combo.set('')
            self.price_var.set('')
            self.quantity_var.set('1')
            self.item_total_var.set('₹0.00')
            self.product_info_label.configure(text="Select a product to see details")
            
            messagebox.showinfo("Success", "✅ Product added to cart!")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for quantity and price!")

    def _update_cart_tree(self):
        """Update cart treeview"""
        # Clear existing items
        for item in self.cart_tree.get_children():
            self.cart_tree.delete(item)
        
        # Add cart items
        for item in self.cart_items:
            self.cart_tree.insert("", "end", values=(
                item['product_name'],
                item['category_name'],
                f"₹{item['price']:.2f}",
                item['quantity'],
                f"₹{item['subtotal']:.2f}",
                "✏️ Edit"
            ))

    def update_totals(self):
        """Update invoice totals"""
        subtotal = sum(item['subtotal'] for item in self.cart_items)
        tax = subtotal * 0.18  # 18% GST
        grand_total = subtotal + tax
        
        self.subtotal_label.configure(text=f"Subtotal: ₹{subtotal:.2f}")
        self.tax_label.configure(text=f"Tax (18% GST): ₹{tax:.2f}")
        self.grand_total_label.configure(text=f"Grand Total: ₹{grand_total:.2f}")
        
        # Convert to words
        if grand_total > 0:
            amount_words = num2words(grand_total, lang='en_IN').title() + " Rupees Only"
        else:
            amount_words = "Zero Rupees Only"
        self.amount_words_label.configure(text=amount_words)

    def remove_from_cart(self):
        """Remove selected item from cart"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to remove!")
            return
        
        selected_item = selection[0]
        item_index = self.cart_tree.index(selected_item)
        
        if 0 <= item_index < len(self.cart_items):
            self.cart_items.pop(item_index)
            self._update_cart_tree()
            self.update_totals()
            messagebox.showinfo("Success", "✅ Item removed from cart!")

    def clear_cart(self):
        """Clear all items from cart"""
        if not self.cart_items:
            messagebox.showinfo("Info", "Cart is already empty!")
            return
        
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear the cart?"):
            self.cart_items.clear()
            self._update_cart_tree()
            self.update_totals()
            messagebox.showinfo("Success", "✅ Cart cleared!")

    def edit_cart_item(self, event):
        """Edit selected cart item"""
        selection = self.cart_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit.")
            return
        
        selected_item = selection[0]
        item_index = self.cart_tree.index(selected_item)
        
        if item_index < len(self.cart_items):
            item = self.cart_items[item_index]
            
            # Create edit dialog
            dialog = ctk.CTkToplevel(self.parent)
            dialog.title("Edit Cart Item")
            dialog.geometry("400x300")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Center dialog
            dialog.update_idletasks()
            x = self.parent.winfo_x() + (self.parent.winfo_width() - 400) // 2
            y = self.parent.winfo_y() + (self.parent.winfo_height() - 300) // 2
            dialog.geometry(f"+{x}+{y}")
            
            main_frame = ctk.CTkFrame(dialog, fg_color="white")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                main_frame,
                text="✏️ Edit Cart Item",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#2E7D32"
            ).pack(pady=(0, 20))
            
            # Quantity
            quantity_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            quantity_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(quantity_frame, text="Quantity:", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            quantity_entry = ctk.CTkEntry(quantity_frame, height=35)
            quantity_entry.insert(0, str(item['quantity']))
            quantity_entry.pack(fill="x", pady=(5, 0))
            
            # Price
            price_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            price_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(price_frame, text="Price (₹):", font=ctk.CTkFont(weight="bold")).pack(anchor="w")
            price_entry = ctk.CTkEntry(price_frame, height=35)
            price_entry.insert(0, str(item['price']))
            price_entry.pack(fill="x", pady=(5, 0))
            
            # Buttons
            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(20, 0))
            
            def save_changes():
                try:
                    new_quantity = float(quantity_entry.get())
                    new_price = float(price_entry.get())
                    
                    if new_quantity <= 0 or new_price <= 0:
                        messagebox.showerror("Error", "Quantity and price must be positive numbers.")
                        return
                    
                    # Update cart item
                    self.cart_items[item_index]['quantity'] = new_quantity
                    self.cart_items[item_index]['price'] = new_price
                    self.cart_items[item_index]['subtotal'] = new_quantity * new_price
                    
                    self._update_cart_tree()
                    self.update_totals()
                    dialog.destroy()
                    messagebox.showinfo("Success", "✅ Cart item updated successfully!")
                    
                except ValueError:
                    messagebox.showerror("Error", "Please enter valid numbers for quantity and price.")
            
            ctk.CTkButton(
                button_frame,
                text="💾 Save Changes",
                command=save_changes,
                height=40,
                fg_color="#2E7D32",
                hover_color="#1B5E20"
            ).pack(side="left", padx=(0, 10), expand=True)
            
            ctk.CTkButton(
                button_frame,
                text="❌ Cancel",
                command=dialog.destroy,
                height=40,
                fg_color="#6C757D",
                hover_color="#5A6268"
            ).pack(side="right", expand=True)

    def save_invoice(self):
        """Save invoice to database with payment tracking"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty! Add some products first.")
            return
        
        customer_name = self.customer_combo.get().split(' (')[0] if self.customer_combo.get() else None
        if not customer_name and self.new_customer_name.get():
            customer_name = self.new_customer_name.get().strip()
        
        if not customer_name:
            messagebox.showerror("Error", "Please select or add a customer.")
            return
        
        try:
            # Get or create customer
            customer = db.fetch_one("SELECT customer_id FROM customers WHERE customer_name = %s", (customer_name,))
            customer_id = None
            
            if customer:
                customer_id = customer['customer_id']
            else:
                # Create new customer
                phone = self.new_customer_phone.get().strip()
                if not phone:
                    messagebox.showerror("Error", "Phone number is required for new customers.")
                    return
                
                # Check if phone already exists
                existing_phone = db.fetch_one("SELECT customer_id FROM customers WHERE phone = %s", (phone,))
                if existing_phone:
                    messagebox.showerror("Error", "Customer with this phone number already exists!")
                    return
                
                db.execute_query(
                    "INSERT INTO customers (customer_name, phone) VALUES (%s, %s)",
                    (customer_name, phone)
                )
                customer = db.fetch_one("SELECT customer_id FROM customers WHERE customer_name = %s", (customer_name,))
                customer_id = customer['customer_id']
                self.load_customers()  # Refresh customer list
            
            invoice_date = self.date_entry.get_date()
            payment_status = self.payment_status_var.get()
            
            # Calculate totals
            subtotal = sum(item['subtotal'] for item in self.cart_items)
            tax = subtotal * 0.18  # 18% GST
            grand_total = subtotal + tax
            
            # Save invoice
            invoice_query = """
            INSERT INTO invoices (invoice_number, customer_id, invoice_date, subtotal, tax_amount, grand_total, payment_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(invoice_query, (
                self.invoice_var.get(), customer_id, invoice_date, 
                subtotal, tax, grand_total, payment_status
            ))
            
            # Get the inserted invoice ID
            invoice_id = db.fetch_one("SELECT LAST_INSERT_ID() as id")['id']
            
            # Save invoice items - use minimal columns that exist
            for item in self.cart_items:
                try:
                    # Try with minimal columns first
                    item_query = """
                    INSERT INTO invoice_items (invoice_id, product_id, quantity, unit_price, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    db.execute_query(item_query, (
                        invoice_id, item.get('product_id'),
                        item['quantity'], item['price'], item['subtotal']
                    ))
                except Exception as e:
                    print(f"Error saving invoice item: {e}")
                    # Try alternative approach if the above fails
                    try:
                        item_query = """
                        INSERT INTO invoice_items (invoice_id, product_id, quantity, price, total)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        db.execute_query(item_query, (
                            invoice_id, item.get('product_id'),
                            item['quantity'], item['price'], item['subtotal']
                        ))
                    except Exception as e2:
                        messagebox.showerror("Error", f"Failed to save invoice items: {str(e2)}")
                        return
            
            messagebox.showinfo("Success", "✅ Invoice saved successfully!")
            
            # Generate PDF automatically
            self.generate_invoice_pdf()
            
            # Clear cart for next invoice
            self.clear_cart()
            self.generate_invoice_number()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to save invoice: {str(e)}")

    def generate_invoice_pdf(self):
        """Generate professional PDF invoice"""
        if not self.cart_items:
            messagebox.showwarning("Warning", "Cart is empty! Add some products first.")
            return
        
        try:
            filename = f"{self.invoice_var.get()}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Company header
            company_info = [
                ["SARVYA BUSINESS SOLUTIONS"],
                ["123 Business Street, City - 123456"],
                ["GSTIN: 07AABCU9603R1ZM", f"Invoice No: {self.invoice_var.get()}"],
                ["Phone: +91-9876543210", f"Date: {self.date_entry.get_date()}"]
            ]
            
            company_table = Table(company_info, colWidths=[300, 200])
            company_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 16),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(company_table)
            elements.append(Spacer(1, 20))
            
            # Customer information
            customer_name = self.customer_combo.get().split(' (')[0] if self.customer_combo.get() else self.new_customer_name.get()
            customer_phone = self.new_customer_phone.get() if self.new_customer_phone.get() else "N/A"
            
            customer_info = [
                ["Bill To:", f"Invoice No: {self.invoice_var.get()}"],
                [f"Name: {customer_name}", f"Date: {self.date_entry.get_date()}"],
                [f"Phone: {customer_phone}", f"Status: {self.payment_status_var.get().title()}"],
            ]
            
            customer_table = Table(customer_info, colWidths=[300, 200])
            customer_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ]))
            elements.append(customer_table)
            elements.append(Spacer(1, 20))
            
            # Items table
            items_data = [["Product", "Category", "Price", "Qty", "Total"]]
            for item in self.cart_items:
                items_data.append([
                    item['product_name'],
                    item['category_name'],
                    f"₹{item['price']:.2f}",
                    str(item['quantity']),
                    f"₹{item['subtotal']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[200, 100, 80, 60, 80])
            items_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 20))
            
            # Totals
            subtotal = sum(item['subtotal'] for item in self.cart_items)
            tax = subtotal * 0.18
            grand_total = subtotal + tax
            
            totals_data = [
                ["Subtotal:", f"₹{subtotal:.2f}"],
                ["Tax (18% GST):", f"₹{tax:.2f}"],
                ["Grand Total:", f"₹{grand_total:.2f}"]
            ]
            
            totals_table = Table(totals_data, colWidths=[400, 100])
            totals_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 12),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ]))
            elements.append(totals_table)
            
            # Amount in words
            amount_words = num2words(grand_total, lang='en_IN').title() + " Rupees Only"
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Amount in Words:</b> {amount_words}", styles['Normal']))
            
            # Footer
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("<i>Thank you for your business!</i>", styles['Italic']))
            elements.append(Paragraph("<i>Terms & Conditions: Goods once sold will not be taken back.</i>", styles['Italic']))
            
            # Build PDF
            doc.build(elements)
            
            # Open PDF
            webbrowser.open(filename)
            messagebox.showinfo("Success", f"✅ PDF invoice downloaded: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to generate PDF: {str(e)}")

    # ========== INVOICE MANAGEMENT METHODS ==========

    def show_invoices_dialog(self):
        """Show all invoices with download and management options"""
        try:
            dialog = ctk.CTkToplevel(self.parent)
            dialog.title("Invoice History")
            dialog.geometry("1000x600")
            dialog.transient(self.parent)
            dialog.grab_set()
            
            # Center the dialog
            dialog.update_idletasks()
            x = self.parent.winfo_x() + (self.parent.winfo_width() - 1000) // 2
            y = self.parent.winfo_y() + (self.parent.winfo_height() - 600) // 2
            dialog.geometry(f"+{x}+{y}")
            
            # Main container
            main_container = ctk.CTkFrame(dialog, fg_color="white")
            main_container.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                main_container,
                text="📋 Invoice History",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#2E7D32"
            ).pack(pady=(0, 15))
            
            # Search and filter frame
            search_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            search_frame.pack(fill="x", pady=(0, 15))
            
            # Search entry
            search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
            search_container.pack(side="left", fill="x", expand=True)
            
            ctk.CTkLabel(search_container, text="🔍", font=ctk.CTkFont(size=16)).pack(side="left")
            search_invoice_entry = ctk.CTkEntry(
                search_container, 
                placeholder_text="Search by invoice number, customer name, or phone...",
                height=40
            )
            search_invoice_entry.pack(side="left", fill="x", expand=True, padx=(10, 10))
            
            # Refresh button
            ctk.CTkButton(
                search_frame,
                text="🔄 Refresh",
                command=lambda: self.load_invoices_data(invoices_tree),
                width=100,
                height=40,
                fg_color="#6C757D",
                hover_color="#5A6268"
            ).pack(side="right")
            
            # Invoices table
            table_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            table_frame.pack(fill="both", expand=True)
            
            columns = ("Invoice No", "Date", "Customer", "Phone", "Amount", "Status", "Actions")
            invoices_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
            
            # Configure style
            style = ttk.Style()
            style.configure("Treeview", 
                           background="white",
                           foreground="black",
                           fieldbackground="white",
                           rowheight=25)
            style.configure("Treeview.Heading",
                           background="#f0f0f0",
                           foreground="black",
                           font=('Helvetica', 10, 'bold'))
            
            col_widths = [120, 100, 150, 120, 100, 80, 120]
            for col, width in zip(columns, col_widths):
                invoices_tree.heading(col, text=col)
                invoices_tree.column(col, width=width, anchor="center")
            
            invoices_tree.column("Customer", anchor="w")
            invoices_tree.column("Amount", anchor="e")
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=invoices_tree.yview)
            h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=invoices_tree.xview)
            invoices_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            invoices_tree.pack(side="top", fill="both", expand=True)
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            
            # Bind double-click to download invoice
            invoices_tree.bind('<Double-1>', lambda e: self.download_selected_invoice(invoices_tree))
            
            # Load invoices
            self.load_invoices_data(invoices_tree)
            
            # Action buttons frame
            action_frame = ctk.CTkFrame(main_container, fg_color="transparent")
            action_frame.pack(fill="x", pady=(15, 0))
            
            ctk.CTkButton(
                action_frame,
                text="📥 Download Selected",
                command=lambda: self.download_selected_invoice(invoices_tree),
                width=160,
                height=40,
                fg_color="#2196F3",
                hover_color="#1976D2"
            ).pack(side="left", padx=(0, 10))
            
            ctk.CTkButton(
                action_frame,
                text="🗑️ Delete Selected",
                command=lambda: self.delete_invoice(invoices_tree),
                width=120,
                height=40,
                fg_color="#F44336",
                hover_color="#D32F2F"
            ).pack(side="left", padx=(0, 10))
            
            ctk.CTkButton(
                action_frame,
                text="❌ Close",
                command=dialog.destroy,
                width=100,
                height=40,
                fg_color="#6C757D",
                hover_color="#5A6268"
            ).pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open invoice dialog: {str(e)}")

    def load_invoices_data(self, tree):
        """Load invoices data into treeview"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        try:
            query = """
            SELECT i.invoice_id, i.invoice_number, i.invoice_date, i.grand_total, i.payment_status,
                   c.customer_name, c.phone, c.email
            FROM invoices i
            JOIN customers c ON i.customer_id = c.customer_id
            ORDER BY i.invoice_date DESC
            """
            invoices = db.fetch_all(query)
            
            for invoice in invoices:
                status_display = invoice['payment_status'].title()
                
                tree.insert("", "end", values=(
                    invoice['invoice_number'],
                    invoice['invoice_date'].strftime('%Y-%m-%d') if isinstance(invoice['invoice_date'], datetime) else str(invoice['invoice_date']),
                    invoice['customer_name'],
                    invoice['phone'],
                    f"₹{invoice['grand_total']:.2f}",
                    status_display,
                    "📥 Download"
                ), tags=(invoice['invoice_id'],))
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to load invoices: {str(e)}")

    def download_selected_invoice(self, tree):
        """Download selected invoice as PDF"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an invoice to download.")
            return
        
        selected_item = selection[0]
        invoice_id = tree.item(selected_item)['tags'][0]
        
        try:
            # Get invoice details
            invoice = db.fetch_one("""
                SELECT i.*, c.customer_name, c.phone, c.email, c.address
                FROM invoices i
                JOIN customers c ON i.customer_id = c.customer_id
                WHERE i.invoice_id = %s
            """, (invoice_id,))
            
            if not invoice:
                messagebox.showerror("Error", "Invoice not found!")
                return
            
            # Get invoice items - use product name from products table
            items = db.fetch_all("""
                SELECT ii.*, p.product_name, c.category_name
                FROM invoice_items ii
                JOIN products p ON ii.product_id = p.product_id
                JOIN categories c ON p.category_id = c.category_id
                WHERE ii.invoice_id = %s
            """, (invoice_id,))
            
            # Generate PDF
            self.generate_existing_invoice_pdf(invoice, items)
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to download invoice: {str(e)}")

    def generate_existing_invoice_pdf(self, invoice, items):
        """Generate PDF for existing invoice from database"""
        try:
            filename = f"{invoice['invoice_number']}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Company header
            company_info = [
                ["SARVYA BUSINESS SOLUTIONS"],
                ["123 Business Street, City - 123456"],
                ["GSTIN: 07AABCU9603R1ZM", f"Invoice No: {invoice['invoice_number']}"],
                ["Phone: +91-9876543210", f"Date: {invoice['invoice_date']}"]
            ]
            
            company_table = Table(company_info, colWidths=[300, 200])
            company_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 16),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(company_table)
            elements.append(Spacer(1, 20))
            
            # Customer information
            customer_info = [
                ["Bill To:", f"Invoice No: {invoice['invoice_number']}"],
                [f"Name: {invoice['customer_name']}", f"Date: {invoice['invoice_date']}"],
                [f"Phone: {invoice['phone']}", f"Status: {invoice['payment_status'].title()}"],
                [f"Email: {invoice.get('email', 'N/A')}", ""]
            ]
            
            customer_table = Table(customer_info, colWidths=[300, 200])
            customer_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 12),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ]))
            elements.append(customer_table)
            elements.append(Spacer(1, 20))
            
            # Items table
            items_data = [["Product", "Category", "Price", "Qty", "Total"]]
            for item in items:
                items_data.append([
                    item['product_name'],
                    item['category_name'],
                    f"₹{item['unit_price']:.2f}",
                    str(item['quantity']),
                    f"₹{item['subtotal']:.2f}"
                ])
            
            items_table = Table(items_data, colWidths=[180, 100, 80, 60, 80])
            items_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
                ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
                ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
                ('ALIGN', (3, 0), (3, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ]))
            elements.append(items_table)
            elements.append(Spacer(1, 20))
            
            # Totals
            subtotal = sum(item['subtotal'] for item in items)
            tax = subtotal * 0.18
            grand_total = subtotal + tax
            
            totals_data = [
                ["Subtotal:", f"₹{subtotal:.2f}"],
                ["Tax (18% GST):", f"₹{tax:.2f}"],
                ["Grand Total:", f"₹{grand_total:.2f}"]
            ]
            
            totals_table = Table(totals_data, colWidths=[400, 100])
            totals_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 12),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
            ]))
            elements.append(totals_table)
            
            # Amount in words
            amount_words = num2words(grand_total, lang='en_IN').title() + " Rupees Only"
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Amount in Words:</b> {amount_words}", styles['Normal']))
            
            # Footer
            elements.append(Spacer(1, 30))
            elements.append(Paragraph("<i>Thank you for your business!</i>", styles['Italic']))
            elements.append(Paragraph("<i>Terms & Conditions: Goods once sold will not be taken back.</i>", styles['Italic']))
            
            # Build PDF
            doc.build(elements)
            
            # Open PDF
            webbrowser.open(filename)
            messagebox.showinfo("Success", f"✅ PDF invoice downloaded: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to generate PDF: {str(e)}")

    def delete_invoice(self, tree):
        """Delete selected invoice"""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an invoice to delete.")
            return
        
        selected_item = selection[0]
        invoice_id = tree.item(selected_item)['tags'][0]
        invoice_number = tree.item(selected_item)['values'][0]
        
        if messagebox.askyesno("Confirm Delete", 
                             f"Are you sure you want to delete invoice {invoice_number}?\n\nThis action cannot be undone!"):
            try:
                # Delete invoice items first
                db.execute_query("DELETE FROM invoice_items WHERE invoice_id = %s", (invoice_id,))
                # Delete invoice
                success = db.execute_query("DELETE FROM invoices WHERE invoice_id = %s", (invoice_id,))
                
                if success:
                    messagebox.showinfo("Success", "✅ Invoice deleted successfully!")
                    self.load_invoices_data(tree)
                else:
                    messagebox.showerror("Error", "❌ Failed to delete invoice!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to delete invoice: {str(e)}")

    # ========== CUSTOMER MANAGEMENT METHODS ==========

    def show_add_customer_dialog(self):
        """Show scrollable dialog to add new customer"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add New Customer")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 500) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 600) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Main container
        main_container = ctk.CTkFrame(dialog, fg_color="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_container,
            text="➕ Add New Customer",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 20))
        
        # Scrollable form container
        scrollable_frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent", height=400)
        scrollable_frame.pack(fill="both", expand=True)
        
        # Form fields
        name_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        name_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            name_frame, 
            text="Customer Name *", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w")
        name_entry = ctk.CTkEntry(
            name_frame, 
            placeholder_text="Enter customer full name",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        name_entry.pack(fill="x", pady=(8, 0))
        
        phone_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        phone_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            phone_frame, 
            text="Phone Number *", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w")
        phone_entry = ctk.CTkEntry(
            phone_frame, 
            placeholder_text="Enter 10-digit phone number",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        phone_entry.pack(fill="x", pady=(8, 0))
        
        email_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        email_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            email_frame, 
            text="Email Address", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w")
        email_entry = ctk.CTkEntry(
            email_frame, 
            placeholder_text="Enter email address (optional)",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        email_entry.pack(fill="x", pady=(8, 0))
        
        address_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        address_frame.pack(fill="x", pady=15)
        
        ctk.CTkLabel(
            address_frame, 
            text="Address", 
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w")
        address_text = ctk.CTkTextbox(
            address_frame,
            height=80,
            font=ctk.CTkFont(size=13)
        )
        address_text.pack(fill="x", pady=(8, 0))
        address_text.insert("1.0", "")
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(20, 0))
        
        def save_customer():
            name = name_entry.get().strip()
            phone = phone_entry.get().strip()
            email = email_entry.get().strip()
            address = address_text.get("1.0", "end-1c").strip()
            
            if not name:
                messagebox.showerror("Error", "Customer name is required!")
                return
            
            if not phone:
                messagebox.showerror("Error", "Phone number is required!")
                return
            
            # Validate phone number
            if not phone.isdigit() or len(phone) != 10:
                messagebox.showerror("Error", "Please enter a valid 10-digit phone number!")
                return
            
            try:
                # Check if customer already exists
                existing = db.fetch_one("SELECT customer_id FROM customers WHERE phone = %s", (phone,))
                if existing:
                    messagebox.showerror("Error", "Customer with this phone number already exists!")
                    return
                
                # Insert new customer
                query = """
                INSERT INTO customers (customer_name, phone, email, address) 
                VALUES (%s, %s, %s, %s)
                """
                success = db.execute_query(query, (
                    name, 
                    phone, 
                    email if email else None,
                    address if address else None
                ))
                
                if success:
                    messagebox.showinfo("Success", "✅ Customer added successfully!")
                    dialog.destroy()
                    self.load_customers()  # Refresh customer list
                    
                    # Auto-fill the new customer in billing form
                    self.new_customer_name.delete(0, 'end')
                    self.new_customer_phone.delete(0, 'end')
                    self.new_customer_name.insert(0, name)
                    self.new_customer_phone.insert(0, phone)
                    
                else:
                    messagebox.showerror("Error", "❌ Failed to add customer!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"❌ Failed to save customer: {str(e)}")
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=dialog.destroy,
            fg_color="#6C757D",
            hover_color="#5A6268",
            height=45,
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save Customer",
            command=save_customer,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(side="right", expand=True)
        
        name_entry.focus()
        dialog.wait_visibility()

# Required packages to install:
# pip install reportlab num2words tkcalendar