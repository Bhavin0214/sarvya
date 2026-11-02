# File: modules/customers.py

import customtkinter as ctk
from tkinter import messagebox
from database import db
from modules.gui_components import ModernWidgets, CustomTableView, ModernFormFrame

class CustomersModule:
    def __init__(self, master, app_instance):
        self.master = master
        self.app = app_instance
        self.widgets = ModernWidgets()
        
        # Set white background for the entire screen
        self.frame = ctk.CTkFrame(master, fg_color="white")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_crm_ui()
    
    def create_crm_ui(self):
        """Create comprehensive CRM interface"""
        # Header with CRM title
        header_frame = ctk.CTkFrame(self.frame, fg_color="white")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # Main title
        ctk.CTkLabel(
            header_frame, 
            text="CRM - Customer Relationship Management", 
            font=ctk.CTkFont(size=26, weight="bold"), 
            text_color="#1B5E20"
        ).pack(side="left")
        
        # Action buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="white")
        button_frame.pack(side="right")
        
        self.widgets.create_accent_button(
            button_frame, "📊 Analytics", self.show_analytics, 
            accent_color="blue", width=120
        ).pack(side="left", padx=5)
        
        self.widgets.create_accent_button(
            button_frame, "📱 WhatsApp Group", self.setup_whatsapp_broadcast, 
            accent_color="green", width=160
        ).pack(side="left", padx=5)
        
        self.widgets.create_accent_button(
            button_frame, "🔄 Refresh", self.load_crm_data, 
            accent_color="orange", width=100
        ).pack(side="left", padx=5)

        # Customer Metrics Cards
        self.create_metrics_section()
        
        # Customer Data Table
        self.create_customer_table_section()
    
    def create_metrics_section(self):
        """Create metrics cards for customer insights"""
        metrics_frame = ctk.CTkFrame(self.frame, fg_color="white")
        metrics_frame.pack(fill="x", pady=(0, 20))
        
        # Get metrics data
        metrics = self.get_customer_metrics()
        
        # Total Customers
        self.widgets.create_metric_card(
            metrics_frame, "Total Customers", metrics['total_customers'],
            icon="👥", color_scheme="primary", width=200, height=120
        ).pack(side="left", padx=10)
        
        # Repeat Customers
        self.widgets.create_metric_card(
            metrics_frame, "Repeat Customers", metrics['repeat_customers'],
            icon="🔄", color_scheme="accent_blue", width=200, height=120
        ).pack(side="left", padx=10)
        
        # New Customers
        self.widgets.create_metric_card(
            metrics_frame, "Active Customers", metrics['active_customers'],
            icon="✅", color_scheme="accent_orange", width=200, height=120
        ).pack(side="left", padx=10)
        
        # Total Revenue
        self.widgets.create_metric_card(
            metrics_frame, "Total Revenue", f"₹{metrics['total_revenue']:.2f}",
            icon="💰", color_scheme="accent_purple", width=200, height=120
        ).pack(side="left", padx=10)
        
        # Recent Activity
        self.widgets.create_metric_card(
            metrics_frame, "Recent Activity", metrics['recent_activity'],
            icon="📈", color_scheme="accent_yellow", width=200, height=120
        ).pack(side="left", padx=10)
    
    def get_customer_metrics(self):
        """Get comprehensive customer metrics using existing columns"""
        try:
            # Total customers
            total_query = "SELECT COUNT(*) as total FROM customers"
            total_result = db.fetch_one(total_query)
            total_customers = total_result['total'] if total_result else 0
            
            # Customers with purchases (repeat customers)
            repeat_query = """
            SELECT COUNT(*) as repeat_count 
            FROM customers 
            WHERE total_purchases > 0
            """
            repeat_result = db.fetch_one(repeat_query)
            repeat_customers = repeat_result['repeat_count'] if repeat_result else 0
            
            # Customers with recent activity (using last_purchase_date)
            active_query = """
            SELECT COUNT(*) as active_count 
            FROM customers 
            WHERE last_purchase_date IS NOT NULL
            """
            active_result = db.fetch_one(active_query)
            active_customers = active_result['active_count'] if active_result else 0
            
            # Total revenue from all customers
            revenue_query = "SELECT SUM(total_purchases) as total_revenue FROM customers"
            revenue_result = db.fetch_one(revenue_query)
            total_revenue = revenue_result['total_revenue'] if revenue_result and revenue_result['total_revenue'] else 0
            
            # Recent activity (customers with purchases in last 30 days)
            recent_query = """
            SELECT COUNT(*) as recent_count 
            FROM customers 
            WHERE last_purchase_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """
            recent_result = db.fetch_one(recent_query)
            recent_activity = recent_result['recent_count'] if recent_result else 0
            
            return {
                'total_customers': total_customers,
                'repeat_customers': repeat_customers,
                'active_customers': active_customers,
                'total_revenue': total_revenue,
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return {
                'total_customers': 0,
                'repeat_customers': 0,
                'active_customers': 0,
                'total_revenue': 0,
                'recent_activity': 0
            }
    
    def create_customer_table_section(self):
        """Create the main customer data table"""
        # Tab view for different customer views
        self.tab_view = ctk.CTkTabview(self.frame, 
                                     fg_color="white", 
                                     segmented_button_fg_color="#2E7D32",
                                     segmented_button_selected_color="#1B5E20",
                                     segmented_button_unselected_color="#4CAF50",
                                     segmented_button_unselected_hover_color="#388E3C")
        self.tab_view.pack(fill="both", expand=True)
        
        # Create tabs
        self.all_customers_tab = self.tab_view.add("👥 All Customers")
        self.repeat_customers_tab = self.tab_view.add("🔄 Repeat Customers")
        self.active_customers_tab = self.tab_view.add("✅ Active Customers")
        self.customer_analysis_tab = self.tab_view.add("📊 Customer Analysis")
        
        # Configure tabs with white background
        for tab in [self.all_customers_tab, self.repeat_customers_tab, 
                   self.active_customers_tab, self.customer_analysis_tab]:
            tab.configure(fg_color="white")
        
        # Load data for all tabs
        self.load_crm_data()
    
    def load_crm_data(self):
        """Load all CRM data"""
        self.load_all_customers()
        self.load_repeat_customers()
        self.load_active_customers()
        self.load_customer_analysis()
    
    def load_all_customers(self):
        """Load all customers using existing database structure"""
        self.clear_tab_content(self.all_customers_tab)
        
        query = """
        SELECT 
            customer_id,
            customer_name,
            phone,
            email,
            address,
            total_purchases,
            last_purchase_date,
            created_at
        FROM customers
        ORDER BY customer_name
        """
        
        data = db.fetch_all(query)
        
        if data:
            for item in data:
                # Format purchases as currency
                item['total_purchases'] = f"₹{float(item['total_purchases'] or 0):.2f}"
                
                # Format dates
                if item['last_purchase_date']:
                    item['last_purchase_date'] = item['last_purchase_date'].strftime('%Y-%m-%d')
                else:
                    item['last_purchase_date'] = 'No Purchases'
                
                if item['created_at']:
                    item['created_at'] = item['created_at'].strftime('%Y-%m-%d')
                else:
                    item['created_at'] = 'N/A'
                
                # Add customer type based on purchases
                purchases = float(item['total_purchases'].replace('₹', '').replace(',', ''))
                item['customer_type'] = 'Repeat' if purchases > 0 else 'New'
                item['purchase_count'] = '1+' if purchases > 0 else '0'
            
            columns = [
                "customer_id", "customer_name", "phone", "email", 
                "customer_type", "total_purchases", "last_purchase_date", "created_at"
            ]
            
            # Create table with white background
            table_frame = ctk.CTkFrame(self.all_customers_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Create custom table view with white theme
            self.all_customers_table = CustomTableViewWhite(
                table_frame, 
                columns=columns, 
                data=data, 
                on_select_callback=self.show_customer_details
            )
            self.all_customers_table.pack(fill="both", expand=True)
        else:
            self.show_no_data_message(self.all_customers_tab)
    
    def load_repeat_customers(self):
        """Load customers with purchases"""
        self.clear_tab_content(self.repeat_customers_tab)
        
        query = """
        SELECT 
            customer_id,
            customer_name,
            phone,
            email,
            total_purchases,
            last_purchase_date,
            created_at
        FROM customers
        WHERE total_purchases > 0
        ORDER BY total_purchases DESC
        """
        
        data = db.fetch_all(query)
        
        if data:
            for item in data:
                item['total_purchases'] = f"₹{float(item['total_purchases']):.2f}"
                if item['last_purchase_date']:
                    item['last_purchase_date'] = item['last_purchase_date'].strftime('%Y-%m-%d')
                else:
                    item['last_purchase_date'] = 'N/A'
                if item['created_at']:
                    item['created_at'] = item['created_at'].strftime('%Y-%m-%d')
                else:
                    item['created_at'] = 'N/A'
            
            columns = [
                "customer_id", "customer_name", "phone", "email",
                "total_purchases", "last_purchase_date", "created_at"
            ]
            
            table_frame = ctk.CTkFrame(self.repeat_customers_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            CustomTableViewWhite(
                table_frame, 
                columns=columns, 
                data=data, 
                on_select_callback=self.show_customer_details
            ).pack(fill="both", expand=True)
        else:
            self.show_no_data_message(self.repeat_customers_tab, "No repeat customers found")
    
    def load_active_customers(self):
        """Load customers with recent activity"""
        self.clear_tab_content(self.active_customers_tab)
        
        query = """
        SELECT 
            customer_id,
            customer_name,
            phone,
            email,
            total_purchases,
            last_purchase_date
        FROM customers
        WHERE last_purchase_date IS NOT NULL
        ORDER BY last_purchase_date DESC
        """
        
        data = db.fetch_all(query)
        
        if data:
            for item in data:
                item['total_purchases'] = f"₹{float(item['total_purchases'] or 0):.2f}"
                if item['last_purchase_date']:
                    item['last_purchase_date'] = item['last_purchase_date'].strftime('%Y-%m-%d %H:%M')
                else:
                    item['last_purchase_date'] = 'N/A'
            
            columns = [
                "customer_id", "customer_name", "phone", "email",
                "total_purchases", "last_purchase_date"
            ]
            
            table_frame = ctk.CTkFrame(self.active_customers_tab, fg_color="white")
            table_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            CustomTableViewWhite(
                table_frame, 
                columns=columns, 
                data=data, 
                on_select_callback=self.show_customer_details
            ).pack(fill="both", expand=True)
        else:
            self.show_no_data_message(self.active_customers_tab, "No active customers found")
    
    def load_customer_analysis(self):
        """Load customer analysis data"""
        self.clear_tab_content(self.customer_analysis_tab)
        
        # Create analysis frame
        analysis_frame = ctk.CTkFrame(self.customer_analysis_tab, fg_color="white")
        analysis_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Customer Segmentation
        seg_frame = ctk.CTkFrame(analysis_frame, fg_color="white")
        seg_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            seg_frame,
            text="📊 Customer Segmentation",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
        ).pack(anchor="w")
        
        # Get segmentation data
        segmentation = self.get_customer_segmentation()
        
        for segment, count in segmentation.items():
            seg_item = ctk.CTkFrame(seg_frame, fg_color="#F8F9FA", corner_radius=8)
            seg_item.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(
                seg_item,
                text=f"{segment}: {count} customers",
                font=ctk.CTkFont(size=14),
                text_color="#495057"
            ).pack(padx=15, pady=8, anchor="w")
        
        # Purchase Analysis
        purchase_frame = ctk.CTkFrame(analysis_frame, fg_color="white")
        purchase_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            purchase_frame,
            text="💰 Purchase Analysis",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#1B5E20"
        ).pack(anchor="w")
        
        # Get purchase analysis
        purchase_data = self.get_purchase_analysis()
        
        for analysis, value in purchase_data.items():
            analysis_item = ctk.CTkFrame(purchase_frame, fg_color="#F8F9FA", corner_radius=8)
            analysis_item.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(
                analysis_item,
                text=f"{analysis}: {value}",
                font=ctk.CTkFont(size=14),
                text_color="#495057"
            ).pack(padx=15, pady=8, anchor="w")
    
    def get_customer_segmentation(self):
        """Get customer segmentation data"""
        try:
            # High value customers (> ₹5000)
            high_value_query = "SELECT COUNT(*) as count FROM customers WHERE total_purchases > 5000"
            high_value = db.fetch_one(high_value_query)['count']
            
            # Medium value customers (₹1000 - ₹5000)
            medium_value_query = "SELECT COUNT(*) as count FROM customers WHERE total_purchases BETWEEN 1000 AND 5000"
            medium_value = db.fetch_one(medium_value_query)['count']
            
            # Low value customers (< ₹1000)
            low_value_query = "SELECT COUNT(*) as count FROM customers WHERE total_purchases < 1000 AND total_purchases > 0"
            low_value = db.fetch_one(low_value_query)['count']
            
            # No purchases
            no_purchase_query = "SELECT COUNT(*) as count FROM customers WHERE total_purchases = 0 OR total_purchases IS NULL"
            no_purchase = db.fetch_one(no_purchase_query)['count']
            
            return {
                "High Value Customers (>₹5000)": high_value,
                "Medium Value Customers (₹1000-5000)": medium_value,
                "Low Value Customers (<₹1000)": low_value,
                "No Purchases Yet": no_purchase
            }
        except Exception as e:
            print(f"Error in segmentation: {e}")
            return {
                "High Value Customers": 0,
                "Medium Value Customers": 0,
                "Low Value Customers": 0,
                "No Purchases Yet": 0
            }
    
    def get_purchase_analysis(self):
        """Get purchase analysis data"""
        try:
            # Total revenue
            total_rev_query = "SELECT SUM(total_purchases) as total FROM customers"
            total_revenue = db.fetch_one(total_rev_query)['total'] or 0
            
            # Average purchase value
            avg_query = "SELECT AVG(total_purchases) as avg FROM customers WHERE total_purchases > 0"
            avg_purchase = db.fetch_one(avg_query)['avg'] or 0
            
            # Customers with multiple purchases (estimated)
            multi_query = "SELECT COUNT(*) as count FROM customers WHERE total_purchases > (SELECT AVG(total_purchases) FROM customers WHERE total_purchases > 0)"
            multi_purchase = db.fetch_one(multi_query)['count']
            
            # Recent activity (last 30 days)
            recent_query = "SELECT COUNT(*) as count FROM customers WHERE last_purchase_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
            recent_activity = db.fetch_one(recent_query)['count']
            
            return {
                f"Total Revenue: ₹{total_revenue:,.2f}": "",
                f"Average Purchase: ₹{avg_purchase:.2f}": "",
                f"Frequent Customers: {multi_purchase}": "",
                f"Recent Activity (30 days): {recent_activity}": ""
            }
        except Exception as e:
            print(f"Error in purchase analysis: {e}")
            return {
                "Total Revenue: ₹0.00": "",
                "Average Purchase: ₹0.00": "",
                "Frequent Customers: 0": "",
                "Recent Activity: 0": ""
            }
    
    def show_customer_details(self, values):
        """Show detailed customer information"""
        customer_id = values[0]
        customer_name = values[1]
        
        # Get customer information using existing columns
        query = """
        SELECT 
            customer_id,
            customer_name,
            phone,
            email,
            address,
            total_purchases,
            last_purchase_date,
            created_at
        FROM customers
        WHERE customer_id = %s
        """
        
        customer_data = db.fetch_one(query, (customer_id,))
        
        if customer_data:
            # Calculate customer value
            total_purchases = float(customer_data['total_purchases'] or 0)
            customer_type = "Repeat Customer" if total_purchases > 0 else "New Customer"
            value_tier = "High Value" if total_purchases > 5000 else "Medium Value" if total_purchases > 1000 else "Low Value" if total_purchases > 0 else "No Purchases"
            
            details = f"""
📋 Customer Details:

👤 Name: {customer_data['customer_name']}
📞 Phone: {customer_data['phone'] or 'N/A'}
📧 Email: {customer_data['email'] or 'N/A'}
🏠 Address: {customer_data.get('address', 'N/A')}

💰 Purchase Summary:
• Total Spent: ₹{total_purchases:,.2f}
• Value Tier: {value_tier}
• Last Purchase: {customer_data['last_purchase_date'].strftime('%Y-%m-%d') if customer_data['last_purchase_date'] else 'No purchases'}
• Since: {customer_data['created_at'].strftime('%Y-%m-%d') if customer_data.get('created_at') else 'N/A'}

📊 Customer Type: {customer_type}
            """
            
            messagebox.showinfo(f"Customer: {customer_name}", details)
    
    def show_analytics(self):
        """Show customer analytics"""
        # Get comprehensive analytics
        total_customers = db.fetch_one("SELECT COUNT(*) as total FROM customers")['total']
        customers_with_purchases = db.fetch_one("SELECT COUNT(*) as total FROM customers WHERE total_purchases > 0")['total']
        total_revenue = db.fetch_one("SELECT SUM(total_purchases) as total FROM customers")['total'] or 0
        avg_purchase = db.fetch_one("SELECT AVG(total_purchases) as avg FROM customers WHERE total_purchases > 0")['avg'] or 0
        
        analytics_info = f"""
📊 Customer Analytics:

• Total Customers: {total_customers}
• Customers with Purchases: {customers_with_purchases}
• Conversion Rate: {(customers_with_purchases/total_customers*100) if total_customers > 0 else 0:.1f}%
• Total Revenue: ₹{total_revenue:,.2f}
• Average Purchase: ₹{avg_purchase:.2f}

📈 Customer Value Segments:
• High Value (>₹5,000): {self.get_customer_segmentation()['High Value Customers (>₹5000)']}
• Medium Value (₹1,000-5,000): {self.get_customer_segmentation()['Medium Value Customers (₹1000-5000)']}
• Low Value (<₹1,000): {self.get_customer_segmentation()['Low Value Customers (<₹1000)']}
        """
        
        messagebox.showinfo("CRM Analytics", analytics_info)
    
    def setup_whatsapp_broadcast(self):
        """Setup WhatsApp broadcast group with customer numbers"""
        try:
            # Get all customer phone numbers
            query = "SELECT phone, customer_name, total_purchases FROM customers WHERE phone IS NOT NULL AND phone != ''"
            customers = db.fetch_all(query)
            
            if not customers:
                messagebox.showinfo("WhatsApp Broadcast", "No customer phone numbers found in database.")
                return
            
            # Separate customers by value
            high_value = [c for c in customers if float(c['total_purchases'] or 0) > 5000]
            medium_value = [c for c in customers if 1000 <= float(c['total_purchases'] or 0) <= 5000]
            low_value = [c for c in customers if 0 < float(c['total_purchases'] or 0) < 1000]
            no_purchase = [c for c in customers if float(c['total_purchases'] or 0) == 0]
            
            # Format numbers for display
            numbers_text = f"""
High Value Customers ({len(high_value)}):
{chr(10).join([f"• {c['customer_name']}: {c['phone']} (₹{float(c['total_purchases'] or 0):.2f})" for c in high_value])}

Medium Value Customers ({len(medium_value)}):
{chr(10).join([f"• {c['customer_name']}: {c['phone']} (₹{float(c['total_purchases'] or 0):.2f})" for c in medium_value])}

Low Value Customers ({len(low_value)}):
{chr(10).join([f"• {c['customer_name']}: {c['phone']} (₹{float(c['total_purchases'] or 0):.2f})" for c in low_value])}

No Purchase Yet ({len(no_purchase)}):
{chr(10).join([f"• {c['customer_name']}: {c['phone']}" for c in no_purchase])}
            """
            
            # Create WhatsApp broadcast message
            message = f"""
📱 WhatsApp Broadcast Group Setup

Total Customers with Phone: {len(customers)}

Customer Segments:
{numbers_text}

Marketing Tips:
• Send exclusive offers to High Value customers
• Send reminder offers to Medium Value customers  
• Send welcome offers to Low Value customers
• Send introductory offers to No Purchase customers

To create broadcast lists:
1. Open WhatsApp Web
2. Create separate broadcast lists for each segment
3. Add numbers manually
4. Send targeted marketing messages
            """
            
            messagebox.showinfo("WhatsApp Broadcast Setup", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to setup WhatsApp broadcast: {e}")
    
    def clear_tab_content(self, tab):
        """Clear content of a specific tab"""
        for widget in tab.winfo_children():
            widget.destroy()
    
    def show_no_data_message(self, tab, message="No data available"):
        """Show no data message in tab"""
        ctk.CTkLabel(
            tab, 
            text=message, 
            text_color="#6C757D",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True, pady=50)


class CustomTableViewWhite(ctk.CTkFrame):
    """Modern Table View with White Theme for better visibility"""
    def __init__(self, master, columns, data, on_select_callback=None, **kwargs):
        super().__init__(master, fg_color="white", **kwargs)
        self.columns = columns
        self.data = data
        self.on_select_callback = on_select_callback

        # Import ttk for Treeview
        from tkinter import ttk
        
        # Configure style for Treeview with white theme
        style = ttk.Style()
        style.theme_use("default")
        
        # White theme colors
        bg_color = "white"
        text_color = "#212121"
        header_bg = "#E9ECEF" 
        header_fg = "#212121"
        selected_bg = "#81C784"
        border_color = "#DEE2E6"
        
        style.configure("White.Treeview", 
                        background=bg_color,
                        foreground=text_color,
                        rowheight=35,
                        fieldbackground=bg_color,
                        bordercolor=border_color,
                        borderwidth=1,
                        font=('Segoe UI', 11))
        
        style.map('White.Treeview', 
                 background=[('selected', selected_bg)],
                 foreground=[('selected', 'white')])
        
        style.configure("White.Treeview.Heading", 
                        font=('Segoe UI', 12, 'bold'),
                        background=header_bg,
                        foreground=header_fg,
                        relief="flat",
                        borderwidth=1)
        
        style.map("White.Treeview.Heading", 
                 background=[('active', '#DEE2E6')])
        
        # Create Treeview with white theme
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style="White.Treeview")
        
        # Define column headings with better formatting
        for col in columns:
            display_name = col.replace('_', ' ').title()
            if col.lower() == 'customer_id':
                self.tree.column(col, anchor="center", width=80, stretch=False)
                self.tree.heading(col, text="ID")
            elif 'amount' in col.lower() or 'purchases' in col.lower():
                self.tree.column(col, anchor="e", width=120, stretch=False)
                self.tree.heading(col, text=display_name)
            elif 'date' in col.lower():
                self.tree.column(col, anchor="center", width=120, stretch=False)
                self.tree.heading(col, text=display_name)
            elif 'phone' in col.lower() or 'email' in col.lower():
                self.tree.column(col, anchor="center", width=150, stretch=False)
                self.tree.heading(col, text=display_name)
            elif 'type' in col.lower():
                self.tree.column(col, anchor="center", width=100, stretch=False)
                self.tree.heading(col, text="Type")
            else:
                self.tree.column(col, anchor="w", width=180)
                self.tree.heading(col, text=display_name)
        
        # Insert data
        self.insert_data()
        
        # Add Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        
        # Pack treeview
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Bind selection event
        if self.on_select_callback:
            self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

    def insert_data(self):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert new data
        for item in self.data:
            values = [item.get(col, "") for col in self.columns]
            self.tree.insert('', 'end', values=values)

    def update_data(self, new_data):
        self.data = new_data
        self.insert_data()
        
    def _on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            if self.on_select_callback:
                self.on_select_callback(values)