# File: modules/gui_components.py

import customtkinter as ctk
from tkinter import ttk, messagebox
import hashlib # For potential hash utility

class ModernWidgets:
    """Modern widgets with enhanced styling and color theme, moved here to prevent circular imports."""
    
    def __init__(self):
        # Modern color theme
        self.colors = {
            # Primary Greens (Brand Colors)
            "primary_dark": "#1B5E20",    # Dark Green
            "primary": "#2E7D32",         # Main Green
            "primary_light": "#4CAF50",   # Light Green
            "primary_extra_light": "#81C784", # Extra Light Green
            
            # Accent Colors
            "accent_orange": "#FF9800",   # Vibrant Orange
            "accent_blue": "#2196F3",     # Professional Blue
            "accent_yellow": "#FFC107",   # Bright Yellow
            "accent_red": "#F44336",      # Alert Red
            "accent_purple": "#9C27B0",   # Premium Purple
            "accent_green": "#4CAF50",    # Success Green
            
            # Neutral Colors
            "background": "#FFFFFF",      # Pure White
            "surface": "#F8F9FA",         # Light Surface
            "surface_dark": "#E9ECEF",    # Darker Surface
            "border": "#DEE2E6",          # Border Color
            
            # Text Colors
            "text_primary": "#212121",    # Primary Text
            "text_secondary": "#6C757D",  # Secondary Text
            "text_light": "#FFFFFF",      # Light Text
        }

    def darken_color(self, color, factor=0.8):
        """Darken a color by factor"""
        if color.startswith("#"):
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                r = int(r * factor)
                g = int(g * factor)
                b = int(b * factor)
                return f"#{r:02x}{g:02x}{b:02x}"
            except ValueError:
                return color
        return color

    def create_modern_card(self, parent, title=None, width=280, height=150, has_shadow=True, padding=15):
        """Create a modern card with enhanced styling"""
        card = ctk.CTkFrame(
            parent,
            width=width,
            height=height,
            fg_color=self.colors["surface"],
            border_color=self.colors["border"] if has_shadow else "transparent",
            border_width=1 if has_shadow else 0,
            corner_radius=12
        )
        
        if title:
            title_label = ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=self.colors["text_primary"]
            )
            title_label.pack(pady=padding)
        
        return card

    def create_metric_card(self, parent, title, value, icon="📊", color_scheme="primary", 
                          width=260, height=140, command=None, trend=None, trend_value=None):
        """Create a beautiful metric card with trend indicators"""
        card = self.create_modern_card(parent, width=width, height=height)
        
        # Add hover effect for clickability
        if command:
            card.bind("<Button-1>", lambda e: command())
            card.bind("<Enter>", lambda e: card.configure(fg_color=self.colors["surface_dark"]))
            card.bind("<Leave>", lambda e: card.configure(fg_color=self.colors["surface"]))
            card.configure(cursor="hand2")
        
        # Content frame
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Icon and Title
        top_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        top_frame.pack(fill="x")
        
        # Icon
        icon_label = ctk.CTkLabel(
            top_frame,
            text=icon,
            font=ctk.CTkFont(size=20),
            text_color=self.colors[color_scheme] if color_scheme in self.colors else self.colors["primary"],
            width=40
        )
        icon_label.pack(side="left")
        
        # Title
        title_label = ctk.CTkLabel(
            top_frame,
            text=title,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.colors["text_secondary"],
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Trend indicator
        if trend:
            trend_icon = "↗️" if trend == "up" else "↘️"
            trend_color = "#4CAF50" if trend == "up" else "#F44336"
            trend_label = ctk.CTkLabel(
                top_frame,
                text=f"{trend_icon} {trend_value}%",
                font=ctk.CTkFont(size=10),
                text_color=trend_color
            )
            trend_label.pack(side="right")
        
        # Value
        value_label = ctk.CTkLabel(
            content_frame,
            text=str(value),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors["text_primary"]
        )
        value_label.pack(expand=True)
        
        # Bind children to propagate the click event to the parent card
        if command:
            for widget in [content_frame, top_frame, icon_label, title_label, value_label]:
                widget.bind("<Button-1>", lambda e: command())
                widget.configure(cursor="hand2")
        
        return card

    def create_search_bar(self, parent, placeholder="Search...", on_search=None, width=300):
        """Create a modern search bar"""
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=placeholder,
            width=width,
            height=40,
            border_color=self.colors["border"],
            fg_color=self.colors["surface"]
        )
        search_entry.pack(side="left")
        
        if on_search:
            search_btn = ctk.CTkButton(
                search_frame,
                text="🔍",
                width=50,
                height=40,
                fg_color=self.colors["primary"],
                hover_color=self.colors["primary_dark"],
                command=lambda: on_search(search_entry.get())
            )
            search_btn.pack(side="left", padx=(5, 0))
        
        return search_frame

    def create_primary_button(self, parent, text, command, width=140, height=45):
        """Create a modern primary button"""
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_dark"],
            text_color=self.colors["text_light"],
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        )
        return btn

    def create_accent_button(self, parent, text, command, accent_color="orange", width=140, height=45):
        """Create a colored accent button"""
        color_map = {
            "orange": self.colors["accent_orange"],
            "blue": self.colors["accent_blue"],
            "yellow": self.colors["accent_yellow"],
            "red": self.colors["accent_red"],
            "purple": self.colors["accent_purple"],
            "green": self.colors["accent_green"]
        }
        
        color = color_map.get(accent_color, self.colors["accent_orange"])
        
        btn = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=width,
            height=height,
            fg_color=color,
            hover_color=self.darken_color(color),
            text_color=self.colors["text_light"],
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10
        )
        return btn

    def create_status_badge(self, parent, text, status="active"):
        """Create a status badge"""
        status_colors = {
            "active": self.colors["primary"],
            "inactive": self.colors["text_secondary"],
            "pending": self.colors["accent_orange"],
            "completed": self.colors["accent_blue"],
            "warning": self.colors["accent_yellow"],
            "error": self.colors["accent_red"],
            "success": self.colors["accent_green"],
        }
        
        color = status_colors.get(status, self.colors["text_secondary"])
        
        badge = ctk.CTkLabel(
            parent,
            text=text.upper(),
            text_color="white",
            fg_color=color,
            corner_radius=8,
            font=ctk.CTkFont(size=10, weight="bold"),
            width=80,
            height=24
        )
        
        return badge


class CustomTableView(ctk.CTkFrame):
    """Modern Table View using ttk.Treeview"""
    def __init__(self, master, columns, data, on_select_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.columns = columns
        self.data = data
        self.on_select_callback = on_select_callback

        # Configure style for Treeview (Modern Look)
        style = ttk.Style()
        style.theme_use("default")
        
        bg_color = self.cget("fg_color")
        text_color = "#212121"
        header_bg = "#E9ECEF" 
        selected_bg = "#81C784"
        
        style.configure("Treeview", 
                        background=bg_color,
                        foreground=text_color,
                        rowheight=30,
                        fieldbackground=bg_color,
                        bordercolor="#DEE2E6",
                        borderwidth=1)
        style.map('Treeview', background=[('selected', selected_bg)])
        
        style.configure("Treeview.Heading", 
                        font=("Roboto", 11, "bold"),
                        background=header_bg,
                        foreground=text_color,
                        relief="flat")
        style.map("Treeview.Heading", 
                 background=[('active', '#DEE2E6')])
        
        # Create Treeview
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style="Treeview")
        
        # Define column headings
        for i, col in enumerate(columns):
            if col.lower().endswith('_id'):
                 self.tree.column(col, anchor="center", width=50, stretch=False)
                 self.tree.heading(col, text="ID")
            else:
                self.tree.heading(col, text=col.replace('_', ' ').title())
                self.tree.column(col, anchor="w", width=150)
            
        # Insert data
        self.insert_data()
        
        # Add Scrollbar
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Bind selection event
        if self.on_select_callback:
            self.tree.bind('<<TreeviewSelect>>', self._on_tree_select)

    def insert_data(self):
        # Clear existing data
        self.tree.delete(*self.tree.get_children())
        
        # Insert new data
        for item in self.data:
            # item is a dict, need to map to column order
            values = [item.get(col, "") for col in self.columns]
            self.tree.insert('', 'end', values=values)

    def update_data(self, new_data):
        self.data = new_data
        self.insert_data()
        
    def _on_tree_select(self, event):
        selected_item = self.tree.focus()
        if selected_item:
            # Get the values of the selected row
            values = self.tree.item(selected_item, 'values')
            if self.on_select_callback:
                self.on_select_callback(values)


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
            if col.lower() == 'customer_id' or col.lower().endswith('_id'):
                self.tree.column(col, anchor="center", width=80, stretch=False)
                self.tree.heading(col, text="ID")
            elif 'amount' in col.lower() or 'price' in col.lower() or 'total' in col.lower():
                self.tree.column(col, anchor="e", width=120, stretch=False)
                self.tree.heading(col, text=display_name)
            elif 'date' in col.lower():
                self.tree.column(col, anchor="center", width=120, stretch=False)
                self.tree.heading(col, text=display_name)
            elif 'phone' in col.lower() or 'email' in col.lower():
                self.tree.column(col, anchor="center", width=150, stretch=False)
                self.tree.heading(col, text=display_name)
            elif 'type' in col.lower() or 'status' in col.lower():
                self.tree.column(col, anchor="center", width=100, stretch=False)
                self.tree.heading(col, text=display_name)
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


class ModernFormFrame(ctk.CTkFrame):
    """Base frame for Add/Edit forms with modern styling"""
    def __init__(self, master, title, widgets, submit_command, **kwargs):
        super().__init__(master, fg_color="white", corner_radius=12, **kwargs)
        self.widgets = ModernWidgets() # Initialize widgets internally
        
        # Title
        ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#212121"
        ).pack(pady=(20, 10))
        
        # Scrollable container for many fields
        scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=30, pady=(0, 10))
        
        # Form fields container
        form_container = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        form_container.pack(fill="x")
        
        self.entries = {}
        row = 0
        for label_text, widget_type in widgets:
            # Label
            ctk.CTkLabel(
                form_container,
                text=label_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#333333"
            ).grid(row=row, column=0, padx=5, pady=(10, 2), sticky="w")
            
            # Widget
            if widget_type == 'entry':
                entry = ctk.CTkEntry(
                    form_container,
                    placeholder_text=f"Enter {label_text.lower()}",
                    height=40,
                    border_color="#DEE2E6",
                    fg_color="#F8F9FA"
                )
                entry.grid(row=row, column=1, padx=5, pady=(10, 2), sticky="ew")
                self.entries[label_text] = entry
            
            row += 1
            
        form_container.grid_columnconfigure(1, weight=1)

        # Action buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 30))
        
        # Submit Button
        submit_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=submit_command,
            height=40,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8
        )
        submit_btn.pack(side="left", padx=5, expand=True)

    def get_values(self):
        """Returns a dictionary of all form values"""
        values = {}
        for label, entry in self.entries.items():
            values[label] = entry.get()
        return values