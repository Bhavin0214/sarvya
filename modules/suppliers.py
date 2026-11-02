# File: modules/suppliers.py (FIXED VERSION - Filters Working)

import customtkinter as ctk
from tkinter import ttk, messagebox
from database import db
from modules.gui_components import ModernWidgets
import datetime

class SuppliersModule:
    def __init__(self, master, app_instance):
        self.master = master
        self.app = app_instance
        self.widgets = ModernWidgets()
        self.current_filters = {}
        
        self.frame = ctk.CTkFrame(master, fg_color="#F8F9FA")
        self.frame.pack(fill="both", expand=True)
        
        self.create_suppliers_ui()
        self.load_supplier_data()
    
    def create_suppliers_ui(self):
        """Setup enhanced suppliers UI"""
        # Header
        header_frame = ctk.CTkFrame(self.frame, fg_color="transparent", height=80)
        header_frame.pack(fill="x", padx=20, pady=10)
        header_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            header_frame,
            text="🏢 Supplier Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#2E7D32"
        ).pack(side="left")
        
        # Action buttons
        button_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        button_frame.pack(side="right")
        
        self.widgets.create_accent_button(
            button_frame, "📊 Stats", self.show_supplier_stats, "purple", 100, 40
        ).pack(side="right", padx=5)
        
        self.widgets.create_primary_button(
            button_frame, "+ Add Supplier", self.show_add_supplier_form, 140, 40
        ).pack(side="right", padx=5)
        
        # Search and Filters
        self.setup_advanced_filters()
        
        # Main content area
        self.setup_suppliers_table()
    
    def setup_advanced_filters(self):
        """Setup search and filter options"""
        filter_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # Search entry with icon
        search_container = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_container.pack(side="left", fill="x", expand=True)
        
        # Search icon and entry in same row
        search_row = ctk.CTkFrame(search_container, fg_color="transparent")
        search_row.pack(fill="x")
        
        ctk.CTkLabel(
            search_row,
            text="🔍",
            font=ctk.CTkFont(size=16),
            text_color="#6C757D",
            width=30
        ).pack(side="left")
        
        self.search_entry = ctk.CTkEntry(
            search_row,
            placeholder_text="Search suppliers by name, company, phone...",
            height=40
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=(10, 0))
        self.search_entry.bind('<KeyRelease>', self.search_suppliers)
    
    def setup_suppliers_table(self):
        """Setup suppliers table with action buttons"""
        table_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        table_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Stats frame
        stats_frame = ctk.CTkFrame(table_container, fg_color="transparent", height=30)
        stats_frame.pack(fill="x", pady=(0, 10))
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12),
            text_color="#6C757D"
        )
        self.stats_label.pack(side="left")
        
        # Action buttons
        action_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        action_frame.pack(side="right")
        
        ctk.CTkButton(
            action_frame,
            text="Edit Selected",
            command=self.edit_supplier,
            width=100,
            height=30,
            fg_color="#FF9800",
            hover_color="#F57C00"
        ).pack(side="left", padx=(5, 2))
        
        ctk.CTkButton(
            action_frame,
            text="Delete Selected",
            command=self.delete_supplier,
            width=100,
            height=30,
            fg_color="#DC3545",
            hover_color="#C82333"
        ).pack(side="left", padx=(2, 5))
        
        # Table
        columns = ("ID", "Supplier Name", "Company", "Phone", "Email", "GST No", "Address")
        self.suppliers_tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        col_widths = [50, 150, 150, 120, 150, 100, 200]
        for col, width in zip(columns, col_widths):
            self.suppliers_tree.heading(col, text=col)
            self.suppliers_tree.column(col, width=width, anchor="center")
        
        # Custom alignments
        self.suppliers_tree.column("Supplier Name", anchor="w")
        self.suppliers_tree.column("Company", anchor="w")
        self.suppliers_tree.column("Address", anchor="w")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.suppliers_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient="horizontal", command=self.suppliers_tree.xview)
        self.suppliers_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.suppliers_tree.pack(side="top", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        self.suppliers_tree.bind('<Double-1>', lambda e: self.edit_supplier())
    
    def load_supplier_data(self):
        """Load suppliers data"""
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        # Simple query matching your database schema
        query = """
        SELECT 
            supplier_id, supplier_name, company_name, phone, 
            email, gst_number, address
        FROM suppliers
        ORDER BY supplier_name
        """
        suppliers = db.fetch_all(query)
        
        for supplier in suppliers:
            self.suppliers_tree.insert("", "end", values=(
                supplier['supplier_id'],
                supplier['supplier_name'],
                supplier['company_name'] or "N/A",
                supplier['phone'] or "N/A",
                supplier['email'] or "N/A",
                supplier['gst_number'] or "N/A",
                supplier['address'] or "N/A"
            ))
        
        self.update_stats(suppliers)
    
    def update_stats(self, suppliers):
        """Update statistics label"""
        total_suppliers = len(suppliers)
        
        self.stats_label.configure(
            text=f"Total Suppliers: {total_suppliers}"
        )
    
    def search_suppliers(self, event=None):
        """Search suppliers with multiple criteria"""
        search_term = self.search_entry.get().strip().lower()
        
        if not search_term:
            self.load_supplier_data()
            return
        
        # Build search query
        query = """
        SELECT 
            supplier_id, supplier_name, company_name, phone, 
            email, gst_number, address
        FROM suppliers
        WHERE supplier_name LIKE %s OR company_name LIKE %s OR phone LIKE %s
        ORDER BY supplier_name
        """
        
        search_pattern = f"%{search_term}%"
        filtered_suppliers = db.fetch_all(query, (search_pattern, search_pattern, search_pattern))
        
        # Update table with filtered results
        for item in self.suppliers_tree.get_children():
            self.suppliers_tree.delete(item)
        
        for supplier in filtered_suppliers:
            self.suppliers_tree.insert("", "end", values=(
                supplier['supplier_id'],
                supplier['supplier_name'],
                supplier['company_name'] or "N/A",
                supplier['phone'] or "N/A",
                supplier['email'] or "N/A",
                supplier['gst_number'] or "N/A",
                supplier['address'] or "N/A"
            ))
        
        self.update_stats(filtered_suppliers)
    
    def clear_filters(self):
        """Clear all filters"""
        self.search_entry.delete(0, 'end')
        self.load_supplier_data()
    
    def show_add_supplier_form(self):
        """Show add supplier dialog"""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Add New Supplier")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 500) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 600) // 2
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
            text="Add New Supplier",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 15))
        
        # Scrollable form container
        scrollable_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color="transparent",
            width=460,
            height=400
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Form fields
        form_entries = {}
        
        fields = [
            ("Supplier Name *", "text"),
            ("Company Name", "text"),
            ("Phone Number", "text"),
            ("Email Address", "text"),
            ("GST Number", "text"),
            ("Address", "textarea")
        ]
        
        for label, field_type in fields:
            ctk.CTkLabel(
                scrollable_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#333333"
            ).pack(anchor="w", pady=(10, 5))
            
            if field_type == "text":
                entry = ctk.CTkEntry(
                    scrollable_frame,
                    placeholder_text=f"Enter {label.replace('*', '').strip()}",
                    height=35
                )
                entry.pack(fill="x", pady=(0, 10))
                form_entries[label] = entry
            elif field_type == "textarea":
                textarea = ctk.CTkTextbox(
                    scrollable_frame,
                    height=80
                )
                textarea.pack(fill="x", pady=(0, 10))
                form_entries[label] = textarea
        
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
            text="Save Supplier",
            command=lambda: self.save_supplier(form_entries, dialog),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40
        ).pack(side="right", expand=True)
        
        # Set focus to first field
        first_field = list(form_entries.values())[0]
        first_field.focus()
        
        dialog.wait_visibility()
    
    def save_supplier(self, form_entries, dialog):
        """Save new supplier to database"""
        try:
            # Get form values
            supplier_name = form_entries["Supplier Name *"].get().strip()
            company_name = form_entries["Company Name"].get().strip()
            phone = form_entries["Phone Number"].get().strip()
            email = form_entries["Email Address"].get().strip()
            gst_number = form_entries["GST Number"].get().strip()
            address = form_entries["Address"].get("1.0", "end-1c").strip()
            
            if not supplier_name:
                messagebox.showerror("Error", "Supplier name is required!")
                return
            
            # Insert supplier
            query = """
            INSERT INTO suppliers 
            (supplier_name, company_name, phone, email, gst_number, address)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            success = db.execute_query(query, (
                supplier_name, company_name, phone, email, gst_number, address
            ))
            
            if success:
                messagebox.showinfo("Success", "Supplier added successfully!")
                dialog.destroy()
                self.load_supplier_data()
            else:
                messagebox.showerror("Error", "Failed to add supplier!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save supplier: {str(e)}")
    
    def edit_supplier(self, event=None):
        """Edit selected supplier"""
        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to edit!")
            return
        
        item = self.suppliers_tree.item(selection[0])
        supplier_id = item['values'][0]
        
        # Fetch supplier details
        supplier = db.fetch_one("SELECT * FROM suppliers WHERE supplier_id = %s", (supplier_id,))
        
        if not supplier:
            messagebox.showerror("Error", "Supplier not found!")
            return
        
        # Show edit dialog
        self.show_edit_supplier_dialog(supplier)
    
    def show_edit_supplier_dialog(self, supplier):
        """Show edit supplier dialog with pre-filled data"""
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Edit Supplier")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.master.winfo_x() + (self.master.winfo_width() - 500) // 2
        y = self.master.winfo_y() + (self.master.winfo_height() - 600) // 2
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
            text=f"Edit Supplier: {supplier['supplier_name']}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#2E7D32"
        ).pack(pady=(0, 15))
        
        # Scrollable form container
        scrollable_frame = ctk.CTkScrollableFrame(
            main_container, 
            fg_color="transparent",
            width=460,
            height=400
        )
        scrollable_frame.pack(fill="both", expand=True)
        
        # Form fields
        form_entries = {}
        
        fields = [
            ("Supplier Name *", "text", supplier['supplier_name']),
            ("Company Name", "text", supplier['company_name'] or ""),
            ("Phone Number", "text", supplier['phone'] or ""),
            ("Email Address", "text", supplier['email'] or ""),
            ("GST Number", "text", supplier['gst_number'] or ""),
            ("Address", "textarea", supplier['address'] or "")
        ]
        
        for label, field_type, default_value in fields:
            ctk.CTkLabel(
                scrollable_frame,
                text=label,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#333333"
            ).pack(anchor="w", pady=(10, 5))
            
            if field_type == "text":
                entry = ctk.CTkEntry(
                    scrollable_frame,
                    placeholder_text=f"Enter {label.replace('*', '').strip()}",
                    height=35
                )
                entry.insert(0, default_value)
                entry.pack(fill="x", pady=(0, 10))
                form_entries[label] = entry
            elif field_type == "textarea":
                textarea = ctk.CTkTextbox(
                    scrollable_frame,
                    height=80
                )
                textarea.insert("1.0", default_value)
                textarea.pack(fill="x", pady=(0, 10))
                form_entries[label] = textarea
        
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
            text="Update Supplier",
            command=lambda: self.update_supplier(supplier['supplier_id'], form_entries, dialog),
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            height=40
        ).pack(side="right", expand=True)
        
        dialog.wait_visibility()
    
    def update_supplier(self, supplier_id, form_entries, dialog):
        """Update existing supplier in database"""
        try:
            # Get form values
            supplier_name = form_entries["Supplier Name *"].get().strip()
            company_name = form_entries["Company Name"].get().strip()
            phone = form_entries["Phone Number"].get().strip()
            email = form_entries["Email Address"].get().strip()
            gst_number = form_entries["GST Number"].get().strip()
            address = form_entries["Address"].get("1.0", "end-1c").strip()
            
            if not supplier_name:
                messagebox.showerror("Error", "Supplier name is required!")
                return
            
            # Update supplier
            query = """
            UPDATE suppliers 
            SET supplier_name = %s, company_name = %s, phone = %s, 
                email = %s, gst_number = %s, address = %s
            WHERE supplier_id = %s
            """
            
            success = db.execute_query(query, (
                supplier_name, company_name, phone, email, gst_number, address, supplier_id
            ))
            
            if success:
                messagebox.showinfo("Success", "Supplier updated successfully!")
                dialog.destroy()
                self.load_supplier_data()
            else:
                messagebox.showerror("Error", "Failed to update supplier!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update supplier: {str(e)}")
    
    def delete_supplier(self):
        """Delete selected supplier with confirmation"""
        selection = self.suppliers_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a supplier to delete!")
            return
        
        item = self.suppliers_tree.item(selection[0])
        supplier_id = item['values'][0]
        supplier_name = item['values'][1]
        
        # Check if supplier has purchase history
        purchase_check = db.fetch_one(
            "SELECT COUNT(*) as count FROM purchases WHERE supplier_id = %s", 
            (supplier_id,)
        )
        
        warning_msg = f"Are you sure you want to delete '{supplier_name}'?"
        if purchase_check and purchase_check['count'] > 0:
            warning_msg += f"\n\n⚠️ Warning: This supplier has {purchase_check['count']} purchase records. Deleting it may affect your purchase history."
        
        if messagebox.askyesno("Confirm Delete", warning_msg):
            success = db.execute_query("DELETE FROM suppliers WHERE supplier_id = %s", (supplier_id,))
            
            if success:
                messagebox.showinfo("Success", "Supplier deleted successfully!")
                self.load_supplier_data()
            else:
                messagebox.showerror("Error", "Failed to delete supplier! It might be referenced in purchase records.")
    
    def show_supplier_stats(self):
        """Show supplier statistics"""
        total_suppliers = db.fetch_one("SELECT COUNT(*) as count FROM suppliers")
        if total_suppliers:
            total_count = total_suppliers['count']
        else:
            total_count = 0
        
        stats_text = f"""
📊 Supplier Statistics:

• Total Suppliers: {total_count}
        """
        
        messagebox.showinfo("Supplier Statistics", stats_text)