# File: modules/products.py (FIXED VERSION MATCHING YOUR SCHEMA)

import customtkinter as ctk
from tkinter import ttk, messagebox
from database import db
from modules.gui_components import ModernWidgets
import datetime

class ProductsModule:
    def __init__(self, parent, app_instance):
        self.parent = parent
        self.app = app_instance
        self.widgets = ModernWidgets()
        self.current_filters = {}
        self.setup_ui()
        self.load_categories()
        self.load_products()
    
    def setup_ui(self):
        """Setup products UI matching database schema"""
        main_frame = ctk.CTkFrame(self.parent, fg_color="#F8F9FA")
        main_frame.pack(fill="both", expand=True)
        
        # Header
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="📦 Product Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2E7D32"
        ).pack(side="left")
        
        # Action buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")
        
        self.widgets.create_primary_button(
            button_frame, "+ Add Product", self.show_add_product_dialog, 140, 40
        ).pack(side="right", padx=5)
        
        # Search and Filters
        self.setup_advanced_filters(main_frame)
        
        # Products table
        self.setup_enhanced_table(main_frame)
        
        # Stock alerts panel
        self.setup_stock_alerts(main_frame)
    
    def setup_advanced_filters(self, parent):
        """Setup search and filter options"""
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent", height=60)
        filter_frame.pack(fill="x", padx=20, pady=10)
        filter_frame.pack_propagate(False)
        
        # Search entry
        search_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_container.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            search_container,
            text="🔍",
            font=ctk.CTkFont(size=16),
            text_color="#6C757D"
        ).pack(side="left", padx=(0, 10))
        
        self.search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Search products by name, category, description...",
            height=40,
            width=300
        )
        self.search_entry.pack(side="left", fill="x", expand=True)
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        # Filter buttons
        filter_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_container.pack(side="right")
        
        # Category filter
        ctk.CTkLabel(filter_container, text="Category:", text_color="#6C757D").pack(side="left", padx=(0, 5))
        self.category_filter = ctk.CTkComboBox(
            filter_container,
            values=["All Categories"],
            width=150,
            height=35,
            command=self.apply_filters
        )
        self.category_filter.pack(side="left", padx=5)
        
        # Stock status filter
        ctk.CTkLabel(filter_container, text="Stock:", text_color="#6C757D").pack(side="left", padx=(10, 5))
        self.stock_filter = ctk.CTkComboBox(
            filter_container,
            values=["All", "In Stock", "Low Stock", "Out of Stock"],
            width=120,
            height=35,
            command=self.apply_filters
        )
        self.stock_filter.pack(side="left", padx=5)
        
        # Clear filters button
        ctk.CTkButton(
            filter_container,
            text="Clear Filters",
            command=self.clear_filters,
            fg_color="transparent",
            border_color="#6C757D",
            border_width=1,
            text_color="#6C757D",
            hover_color="#E9ECEF",
            width=100,
            height=35
        ).pack(side="left", padx=5)
    
    def setup_enhanced_table(self, parent):
        """Setup products table with action buttons"""
        table_container = ctk.CTkFrame(parent, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Table header with stats
        stats_frame = ctk.CTkFrame(table_container, fg_color="transparent", height=30)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color="#6C757D"
        )
        self.stats_label.pack(side="left")
        
        # Action buttons for table operations
        action_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        ctk.CTkButton(
            action_frame,
            text="Edit Selected",
            command=self.edit_product,
            width=100,
            height=30,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=(5, 2))
        
        ctk.CTkButton(
            action_frame,
            text="Delete Selected",
            command=self.delete_product,
            width=100,
            height=30,
            fg_color="#DC3545",
            hover_color="#C82333"
        ).pack(side="left", padx=(2, 5))
        
        ctk.CTkButton(
            action_frame,
            text="Update Stock",
            command=self.update_stock,
            width=100,
            height=30,
            fg_color="#2196F3",
            hover_color="#1976D2"
        ).pack(side="left", padx=(2, 5))
        
        # Table columns matching your database schema
        columns = ("ID", "Product Name", "Category", "Serial No", "Purchase Price", "Selling Price", "Current Stock", "Min Stock", "Max Stock", "Status", "Active")
        self.products_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=12)
        
        col_widths = [50, 180, 120, 120, 90, 90, 80, 70, 70, 80, 60]
        for col, width in zip(columns, col_widths):
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=width, anchor="center")
        
        # Custom alignments
        self.products_tree.column("Product Name", anchor="w")
        self.products_tree.column("Serial No", anchor="w")
        self.products_tree.column("Purchase Price", anchor="e")
        self.products_tree.column("Selling Price", anchor="e")
        
        # Configure tags for status colors
        self.products_tree.tag_configure('in_stock', background='#E8F5E8')
        self.products_tree.tag_configure('low_stock', background='#FFF3CD')
        self.products_tree.tag_configure('out_of_stock', background='#F8D7DA')
        self.products_tree.tag_configure('inactive', background='#F5F5F5')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.products_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.products_tree.xview)
        self.products_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.products_tree.pack(side="top", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind double-click to edit
        self.products_tree.bind('<Double-1>', lambda e: self.edit_product())
    
    def setup_stock_alerts(self, parent):
        """Setup stock alerts panel"""
        alerts_frame = ctk.CTkFrame(parent, fg_color="transparent", height=100)
        alerts_frame.pack(fill="x", padx=20, pady=10)
        
        self.alerts_container = ctk.CTkFrame(alerts_frame, fg_color="transparent")
        self.alerts_container.pack(fill="x")
    
    def load_categories(self):
        """Load categories for filter dropdown"""
        categories = db.fetch_all("SELECT category_id, category_name FROM categories ORDER BY category_name")
        category_list = ["All Categories"] + [cat['category_name'] for cat in categories]
        if hasattr(self, 'category_filter'):
            self.category_filter.configure(values=category_list)
        return categories
    
    def load_products(self):
        """Load products into table - FIXED to match your database schema"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # Query matching your exact database schema
        query = """
        SELECT 
            p.product_id, p.product_name, c.category_name, 
            p.serial_number, p.purchase_price, p.selling_price, 
            p.current_stock, p.min_stock_level, p.max_stock_level, p.is_active
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        ORDER BY p.product_name
        """
        products = db.fetch_all(query)
        
        for product in products:
            stock_status = self.get_stock_status(product['current_stock'], product['min_stock_level'])
            status_color = self.get_status_color(stock_status, product['is_active'])
            active_status = "Yes" if product['is_active'] else "No"
            serial_number = product.get('serial_number', 'N/A') or 'N/A'
            
            # Insert product data matching your database columns
            self.products_tree.insert("", "end", values=(
                product['product_id'],
                product['product_name'],
                product.get('category_name', 'N/A'),
                serial_number,
                f"₹{product['purchase_price']:.2f}",
                f"₹{product['selling_price']:.2f}",
                product['current_stock'],
                product['min_stock_level'],
                product.get('max_stock_level', 'N/A'),
                stock_status,
                active_status
            ), tags=(status_color,))
        
        self.update_stats(products)
        self.load_stock_alerts()
    
    def get_stock_status(self, current_stock, min_stock):
        """Determine stock status"""
        if current_stock == 0:
            return "Out of Stock"
        elif current_stock <= min_stock:
            return "Low Stock"
        else:
            return "In Stock"
    
    def get_status_color(self, status, is_active):
        """Get tag color for status"""
        if not is_active:
            return "inactive"
            
        color_map = {
            "In Stock": "in_stock",
            "Low Stock": "low_stock",
            "Out of Stock": "out_of_stock"
        }
        return color_map.get(status, "in_stock")
    
    def update_stats(self, products):
        """Update statistics label"""
        total_products = len(products)
        active_products = sum(1 for p in products if p['is_active'])
        low_stock = sum(1 for p in products if p['current_stock'] <= p['min_stock_level'] and p['current_stock'] > 0 and p['is_active'])
        out_of_stock = sum(1 for p in products if p['current_stock'] == 0 and p['is_active'])
        total_value = sum(p['purchase_price'] * p['current_stock'] for p in products if p['is_active'])
        
        self.stats_label.configure(
            text=f"Total: {total_products} products ({active_products} active) | Low Stock: {low_stock} | Out of Stock: {out_of_stock} | Inventory Value: ₹{total_value:,.2f}"
        )
    
    def load_stock_alerts(self):
        """Load and display stock alerts"""
        for widget in self.alerts_container.winfo_children():
            widget.destroy()
        
        query = """
        SELECT product_name, current_stock, min_stock_level 
        FROM products 
        WHERE current_stock <= min_stock_level AND is_active = TRUE
        ORDER BY current_stock ASC 
        LIMIT 5
        """
        alerts = db.fetch_all(query)
        
        if alerts:
            ctk.CTkLabel(
                self.alerts_container,
                text="🚨 Stock Alerts:",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#DC3545"
            ).pack(anchor="w")
            
            for alert in alerts:
                alert_text = f"{alert['product_name']} - Only {alert['current_stock']} left (min: {alert['min_stock_level']})"
                ctk.CTkLabel(
                    self.alerts_container,
                    text=alert_text,
                    font=ctk.CTkFont(size=12),
                    text_color="#856404"
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                self.alerts_container,
                text="✅ All products are sufficiently stocked",
                font=ctk.CTkFont(size=12),
                text_color="#28A745"
            ).pack(anchor="w")
    
    def search_products(self, event=None):
        """Enhanced search with multiple criteria"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term and not self.current_filters:
            self.load_products()
            return
        
        self.apply_filters()
    
    def apply_filters(self, event=None):
        """Apply all active filters"""
        conditions = []
        params = []
        
        # Search term filter
        search_term = self.search_entry.get().strip()
        if search_term:
            conditions.append("(p.product_name LIKE %s OR c.category_name LIKE %s OR p.serial_number LIKE %s OR p.description LIKE %s)")
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        # Category filter
        category = self.category_filter.get()
        if category and category != "All Categories":
            conditions.append("c.category_name = %s")
            params.append(category)
        
        # Stock status filter
        stock_status = self.stock_filter.get()
        if stock_status != "All":
            if stock_status == "In Stock":
                conditions.append("p.current_stock > p.min_stock_level AND p.is_active = TRUE")
            elif stock_status == "Low Stock":
                conditions.append("p.current_stock <= p.min_stock_level AND p.current_stock > 0 AND p.is_active = TRUE")
            elif stock_status == "Out of Stock":
                conditions.append("p.current_stock = 0 AND p.is_active = TRUE")
        
        # Build query
        query = """
        SELECT 
            p.product_id, p.product_name, c.category_name, 
            p.serial_number, p.purchase_price, p.selling_price, 
            p.current_stock, p.min_stock_level, p.max_stock_level, p.is_active
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.category_id
        """
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY p.product_name"
        
        # Execute filtered query
        filtered_products = db.fetch_all(query, params)
        
        # Update table with filtered results
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        for product in filtered_products:
            stock_status = self.get_stock_status(product['current_stock'], product['min_stock_level'])
            status_color = self.get_status_color(stock_status, product['is_active'])
            active_status = "Yes" if product['is_active'] else "No"
            serial_number = product.get('serial_number', 'N/A') or 'N/A'
            
            self.products_tree.insert("", "end", values=(
                product['product_id'],
                product['product_name'],
                product.get('category_name', 'N/A'),
                serial_number,
                f"₹{product['purchase_price']:.2f}",
                f"₹{product['selling_price']:.2f}",
                product['current_stock'],
                product['min_stock_level'],
                product.get('max_stock_level', 'N/A'),
                stock_status,
                active_status
            ), tags=(status_color,))
        
        self.update_stats(filtered_products)
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_entry.delete(0, 'end')
        self.category_filter.set("All Categories")
        self.stock_filter.set("All")
        self.load_products()
    
    def show_add_product_dialog(self):
        """Show add product dialog matching your database schema"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Add New Product")
        dialog.geometry("500x700")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 500) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 700) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Bring to front
        dialog.lift()
        dialog.focus_force()
        
        # Main container
        main_container = ctk.CTkFrame(dialog, fg_color="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_container,
            text="Add New Product",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2E7D32"
        )
        title_label.pack(pady=(0, 15))
        
        # Scrollable form container
        scrollable_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color="transparent",
            width=460,
            height=500
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Form fields
        self.form_entries = {}
        
        # Product Name
        ctk.CTkLabel(
            scrollable_frame,
            text="Product Name *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(10, 5))
        
        self.form_entries["Product Name"] = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="Enter product name",
            height=35,
            width=400
        )
        self.form_entries["Product Name"].pack(fill="x", pady=(0, 10))
        
        # Category Section
        category_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        category_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            category_frame,
            text="Category *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(0, 5))
        
        # Category selection row
        category_selection_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        category_selection_frame.pack(fill="x")
        
        # Get current categories
        current_categories = [cat['category_name'] for cat in self.load_categories()]
        self.form_entries["Category"] = ctk.CTkComboBox(
            category_selection_frame,
            values=current_categories,
            height=35,
            width=300
        )
        self.form_entries["Category"].pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # Add New Category Button
        ctk.CTkButton(
            category_selection_frame,
            text="+ New",
            command=lambda: self.show_add_category_dialog(dialog),
            width=60,
            height=35,
            fg_color="#6C757D",
            hover_color="#5A6268"
        ).pack(side="right")
        
        # Serial Number
        ctk.CTkLabel(
            scrollable_frame,
            text="Serial Number",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(15, 5))
        
        self.form_entries["Serial Number"] = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="Enter serial number (optional)",
            height=35,
            width=400
        )
        self.form_entries["Serial Number"].pack(fill="x", pady=(0, 10))
        
        # Description
        ctk.CTkLabel(
            scrollable_frame,
            text="Description",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(10, 5))
        
        self.form_entries["Description"] = ctk.CTkTextbox(
            scrollable_frame,
            height=80,
            width=400
        )
        self.form_entries["Description"].pack(fill="x", pady=(0, 10))
        
        # Pricing Section
        pricing_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        pricing_frame.pack(fill="x", pady=(15, 0))
        
        # Purchase Price
        ctk.CTkLabel(
            pricing_frame,
            text="Purchase Price (₹) *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.form_entries["Purchase Price"] = ctk.CTkEntry(
            pricing_frame,
            placeholder_text="0.00",
            height=35
        )
        self.form_entries["Purchase Price"].grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        # Selling Price
        ctk.CTkLabel(
            pricing_frame,
            text="Selling Price (₹) *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.form_entries["Selling Price"] = ctk.CTkEntry(
            pricing_frame,
            placeholder_text="0.00",
            height=35
        )
        self.form_entries["Selling Price"].grid(row=1, column=1, sticky="ew")
        
        pricing_frame.grid_columnconfigure(0, weight=1)
        pricing_frame.grid_columnconfigure(1, weight=1)
        
        # Stock Section
        stock_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        stock_frame.pack(fill="x", pady=(15, 0))
        
        # Current Stock
        ctk.CTkLabel(
            stock_frame,
            text="Current Stock *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.form_entries["Current Stock"] = ctk.CTkEntry(
            stock_frame,
            placeholder_text="0",
            height=35
        )
        self.form_entries["Current Stock"].grid(row=1, column=0, sticky="ew", padx=(0, 10))
        
        # Minimum Stock Level
        ctk.CTkLabel(
            stock_frame,
            text="Minimum Stock Level *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.form_entries["Minimum Stock Level"] = ctk.CTkEntry(
            stock_frame,
            placeholder_text="5",
            height=35
        )
        self.form_entries["Minimum Stock Level"].grid(row=1, column=1, sticky="ew")
        
        stock_frame.grid_columnconfigure(0, weight=1)
        stock_frame.grid_columnconfigure(1, weight=1)
        
        # Max Stock Level
        ctk.CTkLabel(
            scrollable_frame,
            text="Maximum Stock Level",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(15, 5))
        
        self.form_entries["Maximum Stock Level"] = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="100 (optional)",
            height=35
        )
        self.form_entries["Maximum Stock Level"].pack(fill="x", pady=(0, 15))
        
        # Active Status
        active_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        active_frame.pack(fill="x", pady=(10, 10))
        
        self.form_entries["Is Active"] = ctk.CTkCheckBox(
            active_frame,
            text="Product is active (available for sale)",
            checkbox_width=20,
            checkbox_height=20,
            font=ctk.CTkFont(size=12),
            text_color="#333333"
        )
        self.form_entries["Is Active"].pack(anchor="w")
        self.form_entries["Is Active"].select()  # Default to active
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="#6C757D",
            hover_color="#5A6268",
            height=40
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="Save Product",
            command=lambda: self.save_product(dialog),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40
        ).pack(side="right", expand=True)
        
        # Set focus to first field
        self.form_entries["Product Name"].focus()
        
        # Wait for the window to appear
        dialog.wait_visibility()
    
    def show_add_category_dialog(self, parent_dialog):
        """Show dialog to add new category"""
        dialog = ctk.CTkToplevel(parent_dialog)
        dialog.title("Add New Category")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(parent_dialog)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = parent_dialog.winfo_x() + (parent_dialog.winfo_width() - 400) // 2
        y = parent_dialog.winfo_y() + (parent_dialog.winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Form content
        form_frame = ctk.CTkFrame(dialog, fg_color="white")
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            form_frame,
            text="Add New Category",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 20))
        
        ctk.CTkLabel(
            form_frame,
            text="Category Name *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(0, 5))
        
        category_name_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter category name",
            height=35
        )
        category_name_entry.pack(fill="x", pady=(0, 20))
        
        def save_category():
            category_name = category_name_entry.get().strip()
            if not category_name:
                messagebox.showerror("Error", "Category name is required!")
                return
            
            try:
                # Check if category already exists
                existing = db.fetch_one("SELECT category_name FROM categories WHERE category_name = %s", (category_name,))
                if existing:
                    messagebox.showerror("Error", "Category already exists!")
                    return
                
                # Insert new category
                db.execute_query("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
                
                # Refresh categories list
                current_categories = [cat['category_name'] for cat in self.load_categories()]
                self.form_entries["Category"].configure(values=current_categories)
                self.form_entries["Category"].set(category_name)
                
                messagebox.showinfo("Success", "Category added successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add category: {str(e)}")
        
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="#6C757D",
            hover_color="#5A6268",
            height=40
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="Add Category",
            command=save_category,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40
        ).pack(side="right", expand=True)
        
        category_name_entry.focus()
    
    def save_product(self, dialog):
        """Save new product to database - FIXED to match your schema"""
        try:
            # Get form values
            product_name = self.form_entries["Product Name"].get().strip()
            category = self.form_entries["Category"].get()
            serial_number = self.form_entries["Serial Number"].get().strip()
            description = self.form_entries["Description"].get("1.0", "end-1c").strip()
            purchase_price = float(self.form_entries["Purchase Price"].get() or 0)
            selling_price = float(self.form_entries["Selling Price"].get() or 0)
            current_stock = int(self.form_entries["Current Stock"].get() or 0)
            min_stock_level = int(self.form_entries["Minimum Stock Level"].get() or 5)
            max_stock_level = self.form_entries["Maximum Stock Level"].get().strip()
            is_active = self.form_entries["Is Active"].get()
            
            if not product_name:
                messagebox.showerror("Error", "Product name is required!")
                return
            
            if not category:
                messagebox.showerror("Error", "Category is required!")
                return
            
            # Get category ID
            category_result = db.fetch_one("SELECT category_id FROM categories WHERE category_name = %s", (category,))
            if not category_result:
                messagebox.showerror("Error", "Selected category not found!")
                return
            
            category_id = category_result['category_id']
            
            # Handle max_stock_level (can be empty)
            max_stock_level_value = int(max_stock_level) if max_stock_level else None
            
            # Insert product - MATCHING YOUR EXACT DATABASE SCHEMA
            query = """
            INSERT INTO products 
            (product_name, category_id, serial_number, description, purchase_price, 
             selling_price, current_stock, min_stock_level, max_stock_level, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            success = db.execute_query(query, (
                product_name, category_id, 
                serial_number if serial_number else None,
                description if description else None,
                purchase_price, selling_price, 
                current_stock, min_stock_level, max_stock_level_value,
                is_active, datetime.datetime.now()
            ))
            
            if success:
                messagebox.showinfo("Success", "Product added successfully!")
                dialog.destroy()
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to add product!")
                
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for prices and stock!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {str(e)}")
    
    def edit_product(self, event=None):
        """Edit selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to edit!")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        
        # Fetch product details
        product = db.fetch_one("""
            SELECT p.*, c.category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.category_id 
            WHERE p.product_id = %s
        """, (product_id,))
        
        if not product:
            messagebox.showerror("Error", "Product not found!")
            return
        
        # Show edit dialog
        self.show_edit_product_dialog(product)
    
    def show_edit_product_dialog(self, product):
        """Show edit product dialog with pre-filled data"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Edit Product")
        dialog.geometry("500x700")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 500) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 700) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Bring to front
        dialog.lift()
        dialog.focus_force()
        
        # Main container
        main_container = ctk.CTkFrame(dialog, fg_color="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_container,
            text=f"Edit Product: {product['product_name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 15))
        
        # Scrollable form container
        scrollable_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color="transparent",
            width=460,
            height=500
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Form fields
        form_entries = {}
        
        # Product Name
        ctk.CTkLabel(
            scrollable_frame,
            text="Product Name *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(10, 5))
        
        form_entries["Product Name"] = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="Enter product name",
            height=35,
            width=400
        )
        form_entries["Product Name"].pack(fill="x", pady=(0, 10))
        form_entries["Product Name"].insert(0, product['product_name'])
        
        # Category Section
        category_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        category_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(
            category_frame,
            text="Category *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(0, 5))
        
        # Category selection row
        category_selection_frame = ctk.CTkFrame(category_frame, fg_color="transparent")
        category_selection_frame.pack(fill="x")
        
        # Get current categories
        current_categories = [cat['category_name'] for cat in self.load_categories()]
        form_entries["Category"] = ctk.CTkComboBox(
            category_selection_frame,
            values=current_categories,
            height=35,
            width=300
        )
        form_entries["Category"].pack(side="left", fill="x", expand=True, padx=(0, 10))
        form_entries["Category"].set(product.get('category_name', ''))
        
        # Add New Category Button
        ctk.CTkButton(
            category_selection_frame,
            text="+ New",
            command=lambda: self.show_add_category_dialog(dialog),
            width=60,
            height=35,
            fg_color="#6C757D",
            hover_color="#5A6268"
        ).pack(side="right")
        
        # Serial Number
        ctk.CTkLabel(
            scrollable_frame,
            text="Serial Number",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(15, 5))
        
        form_entries["Serial Number"] = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="Enter serial number (optional)",
            height=35,
            width=400
        )
        form_entries["Serial Number"].pack(fill="x", pady=(0, 10))
        if product.get('serial_number'):
            form_entries["Serial Number"].insert(0, product['serial_number'])
        
        # Description
        ctk.CTkLabel(
            scrollable_frame,
            text="Description",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(10, 5))
        
        form_entries["Description"] = ctk.CTkTextbox(
            scrollable_frame,
            height=80,
            width=400
        )
        form_entries["Description"].pack(fill="x", pady=(0, 10))
        if product.get('description'):
            form_entries["Description"].insert("1.0", product['description'])
        
        # Pricing Section
        pricing_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        pricing_frame.pack(fill="x", pady=(15, 0))
        
        # Purchase Price
        ctk.CTkLabel(
            pricing_frame,
            text="Purchase Price (₹) *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        form_entries["Purchase Price"] = ctk.CTkEntry(
            pricing_frame,
            placeholder_text="0.00",
            height=35
        )
        form_entries["Purchase Price"].grid(row=1, column=0, sticky="ew", padx=(0, 10))
        form_entries["Purchase Price"].insert(0, str(product['purchase_price']))
        
        # Selling Price
        ctk.CTkLabel(
            pricing_frame,
            text="Selling Price (₹) *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        form_entries["Selling Price"] = ctk.CTkEntry(
            pricing_frame,
            placeholder_text="0.00",
            height=35
        )
        form_entries["Selling Price"].grid(row=1, column=1, sticky="ew")
        form_entries["Selling Price"].insert(0, str(product['selling_price']))
        
        pricing_frame.grid_columnconfigure(0, weight=1)
        pricing_frame.grid_columnconfigure(1, weight=1)
        
        # Stock Section
        stock_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        stock_frame.pack(fill="x", pady=(15, 0))
        
        # Current Stock
        ctk.CTkLabel(
            stock_frame,
            text="Current Stock *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        form_entries["Current Stock"] = ctk.CTkEntry(
            stock_frame,
            placeholder_text="0",
            height=35
        )
        form_entries["Current Stock"].grid(row=1, column=0, sticky="ew", padx=(0, 10))
        form_entries["Current Stock"].insert(0, str(product['current_stock']))
        
        # Minimum Stock Level
        ctk.CTkLabel(
            stock_frame,
            text="Minimum Stock Level *",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        form_entries["Minimum Stock Level"] = ctk.CTkEntry(
            stock_frame,
            placeholder_text="5",
            height=35
        )
        form_entries["Minimum Stock Level"].grid(row=1, column=1, sticky="ew")
        form_entries["Minimum Stock Level"].insert(0, str(product['min_stock_level']))
        
        stock_frame.grid_columnconfigure(0, weight=1)
        stock_frame.grid_columnconfigure(1, weight=1)
        
        # Max Stock Level
        ctk.CTkLabel(
            scrollable_frame,
            text="Maximum Stock Level",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(15, 5))
        
        form_entries["Maximum Stock Level"] = ctk.CTkEntry(
            scrollable_frame,
            placeholder_text="100 (optional)",
            height=35
        )
        form_entries["Maximum Stock Level"].pack(fill="x", pady=(0, 15))
        if product.get('max_stock_level'):
            form_entries["Maximum Stock Level"].insert(0, str(product['max_stock_level']))
        
        # Active Status
        active_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        active_frame.pack(fill="x", pady=(10, 10))
        
        form_entries["Is Active"] = ctk.CTkCheckBox(
            active_frame,
            text="Product is active (available for sale)",
            checkbox_width=20,
            checkbox_height=20,
            font=ctk.CTkFont(size=12),
            text_color="#333333"
        )
        form_entries["Is Active"].pack(anchor="w")
        if product['is_active']:
            form_entries["Is Active"].select()
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="#6C757D",
            hover_color="#5A6268",
            height=40
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="Update Product",
            command=lambda: self.update_product(product['product_id'], form_entries, dialog),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40
        ).pack(side="right", expand=True)
        
        # Set focus to first field
        form_entries["Product Name"].focus()
        form_entries["Product Name"].select_range(0, 'end')
        
        dialog.wait_visibility()

    def update_product(self, product_id, form_entries, dialog):
        """Update existing product in database"""
        try:
            # Get form values
            product_name = form_entries["Product Name"].get().strip()
            category = form_entries["Category"].get()
            serial_number = form_entries["Serial Number"].get().strip()
            description = form_entries["Description"].get("1.0", "end-1c").strip()
            purchase_price = float(form_entries["Purchase Price"].get() or 0)
            selling_price = float(form_entries["Selling Price"].get() or 0)
            current_stock = int(form_entries["Current Stock"].get() or 0)
            min_stock_level = int(form_entries["Minimum Stock Level"].get() or 5)
            max_stock_level = form_entries["Maximum Stock Level"].get().strip()
            is_active = form_entries["Is Active"].get()
            
            if not product_name:
                messagebox.showerror("Error", "Product name is required!")
                return
            
            if not category:
                messagebox.showerror("Error", "Category is required!")
                return
            
            # Get category ID
            category_result = db.fetch_one("SELECT category_id FROM categories WHERE category_name = %s", (category,))
            if not category_result:
                messagebox.showerror("Error", "Selected category not found!")
                return
            
            category_id = category_result['category_id']
            
            # Handle max_stock_level (can be empty)
            max_stock_level_value = int(max_stock_level) if max_stock_level else None
            
            # Update product
            query = """
            UPDATE products 
            SET product_name = %s, category_id = %s, serial_number = %s, description = %s,
                purchase_price = %s, selling_price = %s, current_stock = %s, 
                min_stock_level = %s, max_stock_level = %s, is_active = %s, updated_at = %s
            WHERE product_id = %s
            """
            
            success = db.execute_query(query, (
                product_name, category_id, 
                serial_number if serial_number else None,
                description if description else None,
                purchase_price, selling_price, 
                current_stock, min_stock_level, max_stock_level_value,
                is_active, datetime.datetime.now(), product_id
            ))
            
            if success:
                messagebox.showinfo("Success", "Product updated successfully!")
                dialog.destroy()
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to update product!")
                
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for prices and stock!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")

    def delete_product(self):
        """Delete selected product with confirmation"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to delete!")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        
        # Check if product has sales history
        sales_check = db.fetch_one(
            "SELECT COUNT(*) as count FROM invoice_items WHERE product_id = %s", 
            (product_id,)
        )
        
        warning_msg = f"Are you sure you want to delete '{product_name}'?"
        if sales_check and sales_check['count'] > 0:
            warning_msg += f"\n\n⚠️ Warning: This product has {sales_check['count']} sales records. Deleting it may affect your sales reports."
        
        if messagebox.askyesno("Confirm Delete", warning_msg):
            success = db.execute_query("DELETE FROM products WHERE product_id = %s", (product_id,))
            
            if success:
                messagebox.showinfo("Success", "Product deleted successfully!")
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to delete product! It might be referenced in sales records.")

    def update_stock(self):
        """Update stock for selected product"""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product to update stock!")
            return
        
        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        current_stock = item['values'][6]  # Current stock value
        
        # Show stock update dialog
        self.show_stock_update_dialog(product_id, product_name, current_stock)

    def show_stock_update_dialog(self, product_id, product_name, current_stock):
        """Dialog for updating stock"""
        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Update Stock")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - 400) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - 250) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Bring to front
        dialog.lift()
        dialog.focus_force()
        
        # Main container
        main_container = ctk.CTkFrame(dialog, fg_color="white")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_container,
            text=f"Update Stock: {product_name}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 15))
        
        # Current stock info
        ctk.CTkLabel(
            main_container,
            text=f"Current Stock: {current_stock}",
            font=ctk.CTkFont(size=14),
            text_color="#6C757D"
        ).pack(pady=(0, 10))
        
        # Stock adjustment
        ctk.CTkLabel(
            main_container,
            text="Stock Adjustment:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(10, 5))
        
        adjustment_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        adjustment_frame.pack(fill="x", pady=(0, 10))
        
        # Radio buttons for adjustment type
        adjustment_type = ctk.StringVar(value="set")
        
        ctk.CTkRadioButton(
            adjustment_frame,
            text="Set to specific value",
            variable=adjustment_type,
            value="set"
        ).pack(anchor="w")
        
        ctk.CTkRadioButton(
            adjustment_frame,
            text="Add/Subtract from current",
            variable=adjustment_type,
            value="adjust"
        ).pack(anchor="w")
        
        # Stock value entry
        ctk.CTkLabel(
            main_container,
            text="Stock Value:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#333333"
        ).pack(anchor="w", pady=(10, 5))
        
        stock_entry = ctk.CTkEntry(
            main_container,
            placeholder_text="Enter stock value",
            height=35
        )
        stock_entry.pack(fill="x", pady=(0, 20))
        stock_entry.insert(0, str(current_stock))
        
        # Buttons
        button_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        button_frame.pack(fill="x")
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            fg_color="#6C757D",
            hover_color="#5A6268",
            height=40
        ).pack(side="left", padx=(0, 10), expand=True)
        
        ctk.CTkButton(
            button_frame,
            text="Update Stock",
            command=lambda: self.save_stock_update(product_id, stock_entry.get(), adjustment_type.get(), dialog),
            fg_color="#2196F3",
            hover_color="#1976D2",
            height=40
        ).pack(side="right", expand=True)
        
        stock_entry.focus()
        stock_entry.select_range(0, 'end')
        dialog.wait_visibility()

    def save_stock_update(self, product_id, stock_value, adjustment_type, dialog):
        """Save stock update to database"""
        try:
            stock_value = int(stock_value)
            
            if adjustment_type == "set":
                new_stock = stock_value
            else:  # adjust
                current_stock = db.fetch_one("SELECT current_stock FROM products WHERE product_id = %s", (product_id,))
                if current_stock:
                    new_stock = current_stock['current_stock'] + stock_value
                else:
                    messagebox.showerror("Error", "Could not retrieve current stock!")
                    return
            
            if new_stock < 0:
                messagebox.showerror("Error", "Stock cannot be negative!")
                return
            
            # Update stock in database
            success = db.execute_query(
                "UPDATE products SET current_stock = %s WHERE product_id = %s",
                (new_stock, product_id)
            )
            
            if success:
                messagebox.showinfo("Success", f"Stock updated successfully! New stock: {new_stock}")
                dialog.destroy()
                self.load_products()
            else:
                messagebox.showerror("Error", "Failed to update stock!")
                
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for stock!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update stock: {str(e)}")