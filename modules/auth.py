# File: modules/auth.py (FINAL ENHANCED with Animated Image)

import hashlib
import customtkinter as ctk
from PIL import Image, ImageTk, ImageDraw # Import ImageDraw for creating transparent versions
from database import db
import os 
import math # For sine/cosine easing (optional)

# ---------------------- CONFIGURATION ----------------------
# File path: Assumes namste.png is in the same directory as auth.py (modules/)
IMAGE_PATH = 'namste.jpg'

# Color Constants (Ensuring correct colors for your SARVYA theme)
COLOR_DARK_GREEN = "#1B5E20"    # Splash Screen Background / Button Hover
COLOR_MAIN_GREEN = "#2E7D32"    # Sign-In Button / Text
COLOR_WHITE = "#FFFFFF"         # Inner Frame / Login Background

# ---------------------- AUTHENTICATION CLASS ----------------------
class Authentication:
    # ... (Authentication class remains unchanged) ...
    def __init__(self):
        self.current_user = None

    def _hash_password_for_check(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def login(self, username, password):
        query = "SELECT user_id, username, password_hash, full_name, role, is_active FROM users WHERE username = %s AND is_active = TRUE"
        user = db.fetch_one(query, (username,))
        if user is None:
            return False, "Invalid username or password"
        entered_password_hash = self._hash_password_for_check(password)
        if entered_password_hash == user["password_hash"]:
            self.current_user = {
                "user_id": user["user_id"],
                "username": user["username"],
                "full_name": user["full_name"],
                "role": user["role"],
            }
            return True, "Login successful"
        else:
            return False, "Invalid username or password"

    def logout(self):
        self.current_user = None
        return True

    def get_current_user(self):
        return self.current_user


# ---------------------- NAMASTE ANIMATION CLASS ----------------------
class NamasteAnimation:
    def __init__(self, parent, on_complete):
        self.parent = parent
        self.on_complete = on_complete
        
        # Animation parameters
        self.ANIMATION_DURATION_MS = 5000  
        self.TYPING_SPEED_MS = 300         
        self.FADE_DURATION_MS = 1500       # <--- Image fade/scale duration (1.5s)
        self.FADE_STEPS = 30               # Number of steps for image animation
        self.current_step = 0
        
        self.current_char_index = 0
        self.FULL_TEXT = "NAMASTE"
        
        self.animation_id = None 
        
        self.create_animation_screen()

    def create_animation_screen(self):
        """Show splash image, inner white frame, and set up typing animation."""
        
        # 1. Outer Frame (Dark Green Background)
        self.container = ctk.CTkFrame(
            self.parent, fg_color=COLOR_DARK_GREEN, corner_radius=0
        )
        self.container.pack(fill="both", expand=True)

        # 2. Inner Frame (White Contrast Frame)
        self.inner_frame = ctk.CTkFrame(
            self.container, 
            fg_color=COLOR_WHITE, 
            width=500, 
            height=500, 
            corner_radius=20,
            border_width=0
        )
        self.inner_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.inner_frame.pack_propagate(False)

        # === IMAGE & TEXT SETUP ===
        image_to_load = IMAGE_PATH
        try:
            # Robust path checking
            if not os.path.exists(image_to_load):
                 image_to_load = os.path.join(os.path.dirname(__file__), IMAGE_PATH)
            
            self.original_image_pil = Image.open(image_to_load).resize((250, 250), Image.Resampling.LANCZOS).convert("RGBA")
            
            # Initial opaque version (will be resized/modified in animate_image)
            self.tk_image = ctk.CTkImage(light_image=self.original_image_pil, size=(250, 250))
        except Exception as e:
            print(f"⚠️ Error loading splash image '{image_to_load}':", e)
            self.tk_image = None
            self.original_image_pil = None
        
        # Image Label (inside the white frame) - starts invisible
        self.image_label = ctk.CTkLabel(
            self.inner_frame, 
            image=self.tk_image, 
            text="", 
            fg_color="transparent"
        )
        self.image_label.pack(pady=(50, 10)) 
        
        # NAMASTE Text Label (Typing effect - starts empty)
        self.namaste_label = ctk.CTkLabel(
            self.inner_frame,
            text="", 
            text_color=COLOR_MAIN_GREEN, 
            font=ctk.CTkFont(size=48, weight="bold", family="Arial"), 
            fg_color="transparent"
        )
        self.namaste_label.pack(pady=(20, 0)) 
        
        # 4. Welcome Tagline Frame
        tagline_frame = ctk.CTkFrame(self.inner_frame, fg_color="transparent")
        tagline_frame.pack(pady=(10, 50)) 

        ctk.CTkLabel(tagline_frame, text="Welcome to", text_color="#666666", 
                     font=ctk.CTkFont(size=14), fg_color="transparent").pack(side="left")
        ctk.CTkLabel(tagline_frame, text=" SARVYA", text_color=COLOR_MAIN_GREEN,
                     font=ctk.CTkFont(size=14, weight="bold"), fg_color="transparent").pack(side="left")
        
        # Start the image animation first
        self.parent.after(100, self.animate_image) 
        
        # Schedule the typing animation to start AFTER the image fade is complete
        self.parent.after(self.FADE_DURATION_MS + 200, self.animate_typing) 
        
        # Set a timer to finish the ENTIRE animation and show the login form
        self.parent.after(self.ANIMATION_DURATION_MS, self.fade_out_animation)
        
    def get_faded_image(self, original_img, alpha):
        """Creates a temporary image with reduced opacity (alpha is 0-255)."""
        temp_img = original_img.copy()
        temp_img.putalpha(alpha)
        return temp_img

    def animate_image(self):
        """Fades in and scales up the image."""
        if not self.original_image_pil:
            return
            
        if self.current_step < self.FADE_STEPS:
            progress = self.current_step / self.FADE_STEPS
            
            # 1. Fade-in Effect (Alpha from 0 to 255)
            alpha = int(255 * progress)
            faded_image_pil = self.get_faded_image(self.original_image_pil, alpha)
            
            # 2. Scale-up Effect (Scale from 90% to 100%)
            original_width, original_height = self.original_image_pil.size
            scale_factor = 0.9 + (0.1 * progress)
            new_width = int(original_width * scale_factor)
            new_height = int(original_height * scale_factor)
            
            scaled_image_pil = faded_image_pil.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Update the CTkImage object
            self.tk_image.configure(light_image=scaled_image_pil, size=(new_width, new_height))
            
            self.current_step += 1
            # Schedule the next step
            self.parent.after(int(self.FADE_DURATION_MS / self.FADE_STEPS), self.animate_image)
        else:
            # Ensure final state is 100% scale, fully opaque
            self.tk_image.configure(light_image=self.original_image_pil, size=self.original_image_pil.size)
            self.current_step = self.FADE_STEPS # Reset for safety

    def animate_typing(self):
        """Simulates a typing animation for 'NAMASTE' at the new slower pace."""
        
        if self.current_char_index < len(self.FULL_TEXT):
            
            # Type one character
            current_text = self.FULL_TEXT[:self.current_char_index + 1]
            self.namaste_label.configure(text=current_text)
            
            self.current_char_index += 1
            
            # Schedule the next character type using the increased delay
            self.animation_id = self.parent.after(self.TYPING_SPEED_MS, self.animate_typing)
        else:
            self.animation_id = None

    def fade_out_animation(self):
        """Starts the final cleanup and transition to the login form."""
        
        # Crucial fix to prevent TclError
        if self.animation_id:
            self.parent.after_cancel(self.animation_id)
            self.animation_id = None
            
        self.fade_alpha = 1.0
        self.fade_out()

    def fade_out(self):
        """Quickly destroys the splash screen container."""
        if self.fade_alpha > 0:
            # Slower fade-out for the final effect
            self.fade_alpha -= 0.15 
            self.parent.after(50, self.fade_out) 
        else:
            self.container.destroy()
            self.on_complete()


# ---------------------- LOGIN WINDOW CLASS ----------------------
class LoginWindow:
    def __init__(self, parent, on_login_success):
        self.parent = parent
        self.on_login_success = on_login_success
        self.auth = Authentication()
        self.show_namaste_animation()

    def show_namaste_animation(self):
        self.namaste_anim = NamasteAnimation(self.parent, self.show_login_form)

    def show_login_form(self):
        # Ensure the root background matches the surrounding area (Dark Green)
        self.parent.configure(fg_color=COLOR_DARK_GREEN) 
        
        # --- LOGIN FORM SETUP (Unchanged from previous versions) ---
        # Login Frame is white
        self.container = ctk.CTkFrame(
            self.parent, fg_color=COLOR_WHITE, width=400, height=500, corner_radius=15
        )
        self.container.pack(expand=True)
        self.container.pack_propagate(False)

        ctk.CTkLabel(self.container, text="SARVYA", font=ctk.CTkFont(size=32, weight="bold"), 
                     text_color=COLOR_MAIN_GREEN).pack(pady=(50, 10))
        ctk.CTkLabel(self.container, text="Business Operating Software", font=ctk.CTkFont(size=14), 
                     text_color="#666666").pack(pady=(0, 40))

        form_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        form_frame.pack(fill="x", padx=40, pady=20)

        # Username
        ctk.CTkLabel(form_frame, text="Username", font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#333333").pack(anchor="w", pady=(10, 5))
        self.username_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your username", 
                                           height=45, border_color=COLOR_MAIN_GREEN, fg_color="#F8F9FA")
        self.username_entry.pack(fill="x", pady=5)
        self.username_entry.insert(0, "admin")

        # Password
        ctk.CTkLabel(form_frame, text="Password", font=ctk.CTkFont(size=12, weight="bold"), 
                     text_color="#333333").pack(anchor="w", pady=(15, 5))
        self.password_entry = ctk.CTkEntry(form_frame, placeholder_text="Enter your password", show="•", 
                                           height=45, border_color=COLOR_MAIN_GREEN, fg_color="#F8F9FA")
        self.password_entry.pack(fill="x", pady=5)
        self.password_entry.insert(0, "admin123")
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        # Sign In Button
        self.login_button = ctk.CTkButton(
            form_frame,
            text="Sign In",
            command=self.attempt_login,
            height=45,
            fg_color=COLOR_MAIN_GREEN, 
            hover_color=COLOR_DARK_GREEN,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.login_button.pack(fill="x", pady=20)

        self.error_label = ctk.CTkLabel(form_frame, text="", text_color="#F44336", font=ctk.CTkFont(size=12))

        demo_frame = ctk.CTkFrame(self.container, fg_color="#E8F5E8", corner_radius=8)
        demo_frame.pack(fill="x", padx=40, pady=10)

        ctk.CTkLabel(demo_frame, text="Demo Credentials: admin / admin123", font=ctk.CTkFont(size=11), 
                     text_color=COLOR_MAIN_GREEN).pack(pady=8)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        self.error_label.pack_forget()

        success, message = self.auth.login(username, password)

        if success:
            self.on_login_success(self.auth.current_user)
        else:
            self.error_label.configure(text=message)
            self.error_label.pack(pady=10)
            self.password_entry.delete(0, "end")


auth = Authentication()