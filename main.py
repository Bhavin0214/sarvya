# File: main.py

import customtkinter as ctk
from tkinter import ttk, messagebox
from modules.auth import LoginWindow
# Import all modules
from modules.dashboard import Dashboard
from modules.products import ProductsModule
from modules.suppliers import SuppliersModule
from modules.billing import BillingModule
from modules.customers import CustomersModule
from modules.payments import PaymentsModule
from database import db
# FIXED: Import ModernWidgets from the central utility file
from modules.gui_components import ModernWidgets

class SARVYAApp:
    def __init__(self):
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("SARVYA - Business Operating Software")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        
        # Initialize modern widgets
        self.widgets = ModernWidgets()
        
        # Configure modern theme
        self.setup_modern_theme()
        
        # Application state
        self.current_user = None
        self.current_module = None
        
        # Initialize database connection
        if not self.initialize_database():
            pass 
        
        # Show login screen
        self.show_login()
    
    def setup_modern_theme(self):
        """Setup modern SARVYA theme"""
        ctk.set_appearance_mode("light")
        self.colors = self.widgets.colors
    
    def initialize_database(self):
        """Initialize database connection"""
        if db.connect():
            print("✅ Database connected successfully")
            return True
        else:
            print("⚠️  Using demo mode - some features may be limited")
            return True
    
    def show_login(self):
        """Show modern login window"""
        self.clear_window()
        # CUSTOMIZATION: Set the root background to primary green for the login screen
        self.root.configure(fg_color=self.colors["primary"]) 
        LoginWindow(self.root, self.on_login_success)
    
    def on_login_success(self, user):
        """Handle successful login"""
        self.current_user = user
        print(f"✅ User logged in: {user['full_name']}")
        self.show_main_app()
    
    def show_main_app(self):
        """Show main application with modern sidebar"""
        self.clear_window()
        self.setup_modern_layout()
        self.show_dashboard()
    
    def setup_modern_layout(self):
        """Setup modern application layout"""
        # Main container - CUSTOMIZATION: Set to White and remove background border/padding
        # This will hold the sidebar (dark green) and the content frame (white)
        self.main_container = ctk.CTkFrame(self.root, fg_color=self.colors["background"])
        self.main_container.pack(fill="both", expand=True)
        
        # Modern sidebar
        self.setup_modern_sidebar()
        
        # Content area (already white)
        self.content_frame = ctk.CTkFrame(self.main_container, fg_color=self.colors["background"])
        self.content_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0) 
    
    def setup_modern_sidebar(self):
        """Setup modern sidebar"""
        self.sidebar = ctk.CTkFrame(
            self.main_container, 
            width=260,
            fg_color=self.colors["primary_dark"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo section
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=120)
        logo_frame.pack(fill="x", pady=(10, 0))
        
        # Main logo
        logo_text = ctk.CTkLabel(
            logo_frame,
            text="SARVYA",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="white"
        )
        logo_text.pack(pady=(20, 5))
        
        # Tagline
        tagline_text = ctk.CTkLabel(
            logo_frame,
            text="Business Operating Software",
            font=ctk.CTkFont(size=12),
            text_color="#A5D6A7"
        )
        tagline_text.pack(pady=(0, 15))
        
        # User info
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#2E7D32", corner_radius=8)
        user_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.current_user['full_name']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white"
        ).pack(pady=8)
        
        # Navigation
        self.setup_modern_navigation()
    
    def setup_modern_navigation(self):
        """Setup modern navigation"""
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Navigation items
        nav_items = [
            ("📊", "Dashboard", self.show_dashboard),
            ("📦", "Products", self.show_products),
            ("🏢", "Suppliers", self.show_suppliers),
            ("🧾", "Billing", self.show_billing),
            ("👥", "Customers", self.show_customers),
            ("💰", "Payments", self.show_payments),
        ]
        
        for icon, text, command in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=f"   {icon}  {text}",
                command=command,
                fg_color="transparent",
                hover_color="#2E7D32",
                text_color="white",
                anchor="w",
                height=45,
                font=ctk.CTkFont(size=14),
                corner_radius=8
            )
            btn.pack(fill="x", pady=3)
        
        # Logout button at bottom
        logout_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logout_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        
        ctk.CTkButton(
            logout_frame,
            text="🚪 Logout",
            command=self.logout,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            height=45,
            font=ctk.CTkFont(size=14)
        ).pack(fill="x")
        
    def show_dashboard(self):
        """Show dashboard module"""
        self.set_active_module("Dashboard")
        self.clear_content()
        Dashboard(self.content_frame, self) 
    
    def show_products(self):
        """Show products module"""
        self.set_active_module("Products")
        self.clear_content()
        ProductsModule(self.content_frame, self) 
    
    def show_suppliers(self):
        """Show suppliers module"""
        self.set_active_module("Suppliers")
        self.clear_content()
        SuppliersModule(self.content_frame, self) 
    
    def show_billing(self):
        """Show billing module"""
        self.set_active_module("Billing")
        self.clear_content()
        BillingModule(self.content_frame, self) 
    
    def show_customers(self):
        """Show customers module"""
        self.set_active_module("Customers")
        self.clear_content()
        CustomersModule(self.content_frame, self)
    
    def show_payments(self):
        """Show payments module"""
        self.set_active_module("Payments")
        self.clear_content()
        PaymentsModule(self.content_frame, self)
    
    def set_active_module(self, module_name):
        """Set active module"""
        self.current_module = module_name
        self.root.title(f"SARVYA - {module_name}")
    
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Handle user logout"""
        self.current_user = None
        self.current_module = None
        print("✅ User logged out")
        self.show_login()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    print("🚀 Starting SARVYA Business Operating Software...")
    app = SARVYAApp()
    app.run()