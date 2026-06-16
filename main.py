import tkinter as tk
from tkinter import ttk, messagebox
import math
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

class CalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Basic, Scientific & Unit Calculator")
        self.root.geometry("450x800")
        self.root.resizable(False, False)
        
        # Theme variables
        self.current_theme = "light"
        self.themes = {
            "light": {
                "bg": "#f5f5f5",
                "fg": "#1a1a1a",
                "display_bg": "#f5f5f5",
                "display_fg": "#1a1a1a",
                "btn_num_bg": "white",
                "btn_op_bg": "#e0e0e0",
                "btn_sci_bg": "#f0f0f0",
                "btn_eq_bg": "#ff9500",
                "btn_eq_fg": "white",
                "menu_bg": "white",
                "menu_fg": "#1a1a1a",
                "border_color": "#d0d0d0"
            },
            "dark": {
                "bg": "#1a1a1a",
                "fg": "#ffffff",
                "display_bg": "#1a1a1a",
                "display_fg": "#ffffff",
                "btn_num_bg": "#2d2d2d",
                "btn_op_bg": "#3d3d3d",
                "btn_sci_bg": "#2d2d2d",
                "btn_eq_bg": "#ff9500",
                "btn_eq_fg": "white",
                "menu_bg": "#2d2d2d",
                "menu_fg": "#ffffff",
                "border_color": "#404040"
            }
        }
        
        # Variables
        self.current_mode = "basic"
        self.current_expression = ""
        self.history = []
        self.converter_category = "Length"
        self.angle_mode = tk.StringVar(value="rad")
        
        self.load_history()
        self.load_theme()
        self.create_main_layout()
        
    def create_main_layout(self):
        """Create the main layout with header and content area"""
        theme = self.themes[self.current_theme]
        
        self.header_frame = tk.Frame(self.root, bg=theme["bg"], height=60)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.title_label = tk.Label(
            self.header_frame, 
            text="", 
            font=('Segoe UI', 20, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Menu button with hamburger icon (☰)
        self.menu_btn = tk.Button(
            self.header_frame,
            text="☰",
            font=('Segoe UI', 22, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"],
            bd=0,
            cursor="hand2",
            command=self.show_mode_menu,
            activebackground=theme["btn_op_bg"],
            activeforeground=theme["fg"]
        )
        self.menu_btn.pack(side=tk.RIGHT, padx=5)
        
        self.content_frame = tk.Frame(self.root, bg=theme["bg"])
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.create_basic_calculator()
        
    def show_mode_menu(self):
        """Show popup menu with Basic Calculator, Scientific Calculator, Unit Converter"""
        theme = self.themes[self.current_theme]
        
        # Destroy existing menu if any
        if hasattr(self, '_mode_menu') and self._mode_menu.winfo_exists():
            self._mode_menu.destroy()
        
        menu = tk.Toplevel(self.root)
        self._mode_menu = menu
        menu.title("Menu")
        menu.overrideredirect(True)
        menu.configure(bg=theme["menu_bg"])
        menu.attributes("-topmost", True)
        
        # Position menu below the hamburger button
        menu.update_idletasks()
        btn_x = self.menu_btn.winfo_rootx()
        btn_y = self.menu_btn.winfo_rooty()
        btn_height = self.menu_btn.winfo_height()
        
        menu_width = 250
        menu_height = 150
        x = btn_x - menu_width + 50
        y = btn_y + btn_height + 5
        menu.geometry(f"{menu_width}x{menu_height}+{x}+{y}")
        
        # Add shadow-like border
        menu_frame = tk.Frame(menu, bg=theme["border_color"], bd=1, relief=tk.FLAT)
        menu_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        inner_frame = tk.Frame(menu_frame, bg=theme["menu_bg"])
        inner_frame.pack(fill=tk.BOTH, expand=True)
        
        # Basic Calculator button
        basic_btn = tk.Button(
            inner_frame,
            text="  Basic Calculator",
            font=('Segoe UI', 13, 'bold'),
            bg=theme["menu_bg"],
            fg=theme["menu_fg"],
            bd=0,
            pady=12,
            cursor="hand2",
            activebackground=theme["btn_op_bg"],
            activeforeground=theme["fg"],
            anchor='w',
            padx=15,
            command=lambda: [menu.destroy(), self.create_basic_calculator()]
        )
        basic_btn.pack(fill=tk.X)
        
        # Separator
        tk.Frame(inner_frame, bg=theme["border_color"], height=1).pack(fill=tk.X)
        
        # Scientific Calculator button
        sci_btn = tk.Button(
            inner_frame,
            text="  Scientific Calculator",
            font=('Segoe UI', 13, 'bold'),
            bg=theme["menu_bg"],
            fg=theme["menu_fg"],
            bd=0,
            pady=12,
            cursor="hand2",
            activebackground=theme["btn_op_bg"],
            activeforeground=theme["fg"],
            anchor='w',
            padx=15,
            command=lambda: [menu.destroy(), self.create_scientific_calculator()]
        )
        sci_btn.pack(fill=tk.X)
        
        # Separator
        tk.Frame(inner_frame, bg=theme["border_color"], height=1).pack(fill=tk.X)
        
        # Unit Converter button
        unit_btn = tk.Button(
            inner_frame,
            text="  Unit Converter",
            font=('Segoe UI', 13, 'bold'),
            bg=theme["menu_bg"],
            fg=theme["menu_fg"],
            bd=0,
            pady=12,
            cursor="hand2",
            activebackground=theme["btn_op_bg"],
            activeforeground=theme["fg"],
            anchor='w',
            padx=15,
            command=lambda: [menu.destroy(), self.create_unit_converter()]
        )
        unit_btn.pack(fill=tk.X)
        
        # Close menu when clicking outside
        menu.bind('<FocusOut>', lambda e: menu.destroy())
        self.root.bind('<Button-1>', lambda e: self._close_menu_if_outside(e, menu))
        
    def _close_menu_if_outside(self, event, menu):
        """Close menu if click is outside the menu"""
        if hasattr(self, '_mode_menu') and self._mode_menu.winfo_exists():
            mx = menu.winfo_rootx()
            my = menu.winfo_rooty()
            mw = menu.winfo_width()
            mh = menu.winfo_height()
            ex = event.x_root
            ey = event.y_root
            if not (mx <= ex <= mx + mw and my <= ey <= my + mh):
                menu.destroy()
        
    def create_basic_calculator(self):
        """Create basic calculator interface"""
        self.clear_content_frame()
        self.current_mode = "basic"
        self.title_label.config(text="Basic Calculator")
        theme = self.themes[self.current_theme]
        
        self.display_frame = tk.Frame(self.content_frame, bg=theme["display_bg"])
        self.display_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        self.display_label = tk.Label(
            self.display_frame,
            textvariable=self.display_var,
            font=('Segoe UI', 40, 'normal'),
            bg=theme["display_bg"],
            fg=theme["display_fg"],
            anchor='e',
            wraplength=430
        )
        self.display_label.pack(fill=tk.X, pady=20)
        
        self.buttons_frame = tk.Frame(self.content_frame, bg=theme["bg"])
        self.buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        button_config = {
            'font': ('Segoe UI', 20),
            'bd': 0,
            'width': 3,
            'height': 2,
            'relief': tk.FLAT,
            'cursor': 'hand2'
        }
        
        buttons = [
            ('AC', theme["btn_op_bg"], self.clear_all),
            ('%', theme["btn_op_bg"], lambda: self.on_button_click('%')),
            ('⌫', theme["btn_op_bg"], self.backspace),
            ('÷', theme["btn_op_bg"], lambda: self.on_button_click('/')),
            ('7', theme["btn_num_bg"], lambda: self.on_button_click('7')),
            ('8', theme["btn_num_bg"], lambda: self.on_button_click('8')),
            ('9', theme["btn_num_bg"], lambda: self.on_button_click('9')),
            ('×', theme["btn_op_bg"], lambda: self.on_button_click('*')),
            ('4', theme["btn_num_bg"], lambda: self.on_button_click('4')),
            ('5', theme["btn_num_bg"], lambda: self.on_button_click('5')),
            ('6', theme["btn_num_bg"], lambda: self.on_button_click('6')),
            ('-', theme["btn_op_bg"], lambda: self.on_button_click('-')),
            ('1', theme["btn_num_bg"], lambda: self.on_button_click('1')),
            ('2', theme["btn_num_bg"], lambda: self.on_button_click('2')),
            ('3', theme["btn_num_bg"], lambda: self.on_button_click('3')),
            ('+', theme["btn_op_bg"], lambda: self.on_button_click('+')),
            ('00', theme["btn_num_bg"], lambda: self.on_button_click('00')),
            ('0', theme["btn_num_bg"], lambda: self.on_button_click('0')),
            ('.', theme["btn_num_bg"], lambda: self.on_button_click('.')),
            ('=', theme["btn_eq_bg"], self.calculate),
        ]
        
        row = 0
        col = 0
        for text, bg_color, command in buttons:
            fg_color = theme["btn_eq_fg"] if bg_color == theme["btn_eq_bg"] else theme["fg"]
            btn = tk.Button(
                self.buttons_frame,
                text=text,
                bg=bg_color,
                fg=fg_color,
                command=command,
                **button_config
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
            
            self.buttons_frame.grid_rowconfigure(row, weight=1)
            self.buttons_frame.grid_columnconfigure(col, weight=1)
            
            col += 1
            if col > 3:
                col = 0
                row += 1
                
    def create_scientific_calculator(self):
        """Create scientific calculator interface"""
        self.clear_content_frame()
        self.current_mode = "scientific"
        self.title_label.config(text="Scientific Calculator")
        theme = self.themes[self.current_theme]
        
        self.display_frame = tk.Frame(self.content_frame, bg=theme["display_bg"])
        self.display_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        self.display_label = tk.Label(
            self.display_frame,
            textvariable=self.display_var,
            font=('Segoe UI', 28, 'normal'),
            bg=theme["display_bg"],
            fg=theme["display_fg"],
            anchor='e',
            wraplength=380
        )
        self.display_label.pack(fill=tk.X, pady=10)
        
        self.mode_indicator = tk.Label(
            self.display_frame,
            textvariable=self.angle_mode,
            font=('Segoe UI', 12),
            bg=theme["display_bg"],
            fg='#ff9500'
        )
        self.mode_indicator.pack(anchor='e')
        
        self.buttons_frame = tk.Frame(self.content_frame, bg=theme["bg"])
        self.buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        button_config = {
            'font': ('Segoe UI', 14),
            'bd': 0,
            'width': 4,
            'height': 2,
            'relief': tk.FLAT,
            'cursor': 'hand2'
        }
        
        buttons = [
            ('sin', theme["btn_sci_bg"], lambda: self.scientific_func('sin')),
            ('cos', theme["btn_sci_bg"], lambda: self.scientific_func('cos')),
            ('tan', theme["btn_sci_bg"], lambda: self.scientific_func('tan')),
            ('rad', theme["btn_sci_bg"], self.toggle_angle_mode),
            ('deg', theme["btn_sci_bg"], self.toggle_angle_mode),
            ('log', theme["btn_sci_bg"], lambda: self.scientific_func('log')),
            ('ln', theme["btn_sci_bg"], lambda: self.scientific_func('ln')),
            ('(', theme["btn_sci_bg"], lambda: self.on_button_click('(')),
            (')', theme["btn_sci_bg"], lambda: self.on_button_click(')')),
            ('1/x', theme["btn_sci_bg"], lambda: self.on_button_click('1/')),
            ('x!', theme["btn_sci_bg"], lambda: self.scientific_func('factorial')),
            ('AC', theme["btn_op_bg"], self.clear_all),
            ('%', theme["btn_op_bg"], lambda: self.on_button_click('%')),
            ('⌫', theme["btn_op_bg"], self.backspace),
            ('÷', theme["btn_op_bg"], lambda: self.on_button_click('/')),
            ('x^y', theme["btn_sci_bg"], lambda: self.on_button_click('**')),
            ('7', theme["btn_num_bg"], lambda: self.on_button_click('7')),
            ('8', theme["btn_num_bg"], lambda: self.on_button_click('8')),
            ('9', theme["btn_num_bg"], lambda: self.on_button_click('9')),
            ('×', theme["btn_op_bg"], lambda: self.on_button_click('*')),
            ('√', theme["btn_sci_bg"], lambda: self.scientific_func('sqrt')),
            ('4', theme["btn_num_bg"], lambda: self.on_button_click('4')),
            ('5', theme["btn_num_bg"], lambda: self.on_button_click('5')),
            ('6', theme["btn_num_bg"], lambda: self.on_button_click('6')),
            ('-', theme["btn_op_bg"], lambda: self.on_button_click('-')),
            ('π', theme["btn_sci_bg"], lambda: self.on_button_click(str(math.pi))),
            ('1', theme["btn_num_bg"], lambda: self.on_button_click('1')),
            ('2', theme["btn_num_bg"], lambda: self.on_button_click('2')),
            ('3', theme["btn_num_bg"], lambda: self.on_button_click('3')),
            ('+', theme["btn_op_bg"], lambda: self.on_button_click('+')),
            ('e', theme["btn_sci_bg"], lambda: self.on_button_click(str(math.e))),
            ('00', theme["btn_num_bg"], lambda: self.on_button_click('00')),
            ('0', theme["btn_num_bg"], lambda: self.on_button_click('0')),
            ('.', theme["btn_num_bg"], lambda: self.on_button_click('.')),
            ('=', theme["btn_eq_bg"], self.calculate),
        ]
        
        row = 0
        col = 0
        for text, bg_color, command in buttons:
            fg_color = theme["btn_eq_fg"] if bg_color == theme["btn_eq_bg"] else theme["fg"]
            btn = tk.Button(
                self.buttons_frame,
                text=text,
                bg=bg_color,
                fg=fg_color,
                command=command,
                **button_config
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
            
            self.buttons_frame.grid_rowconfigure(row, weight=1)
            self.buttons_frame.grid_columnconfigure(col, weight=1)
            
            col += 1
            if col > 4:
                col = 0
                row += 1
                
    def create_unit_converter(self):
        """Create unit converter interface"""
        self.clear_content_frame()
        self.current_mode = "converter"
        self.title_label.config(text="Unit Converter")
        theme = self.themes[self.current_theme]
        
        categories = [
            ("Length", "📏"),
            ("Area", "📐"),
            ("Volume", "📦"),
            ("Weight", "⚖️"),
            ("Temperature", "🌡️"),
            ("Speed", "⚡"),
            ("Pressure", ""),
            ("Power", "💡"),
            ("Number System", "🔢"),
        ]
        
        self.categories_frame = tk.Frame(self.content_frame, bg=theme["bg"])
        self.categories_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        row = 0
        col = 0
        for category, icon in categories:
            cat_frame = tk.Frame(
                self.categories_frame,
                bg=theme["btn_num_bg"],
                relief=tk.RAISED,
                bd=1
            )
            cat_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            icon_label = tk.Label(
                cat_frame,
                text=icon,
                font=('Segoe UI Emoji', 30),
                bg=theme["btn_num_bg"]
            )
            icon_label.pack(pady=(15, 5))
            
            name_label = tk.Label(
                cat_frame,
                text=category,
                font=('Segoe UI', 12),
                bg=theme["btn_num_bg"],
                fg=theme["fg"]
            )
            name_label.pack(pady=(0, 15))
            
            cat_frame.bind('<Button-1>', lambda e, cat=category: self.open_converter(cat))
            icon_label.bind('<Button-1>', lambda e, cat=category: self.open_converter(cat))
            name_label.bind('<Button-1>', lambda e, cat=category: self.open_converter(cat))
            
            self.categories_frame.grid_rowconfigure(row, weight=1)
            self.categories_frame.grid_columnconfigure(col, weight=1)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
                
    def open_converter(self, category: str):
        """Open specific converter for a category"""
        self.clear_content_frame()
        self.converter_category = category
        theme = self.themes[self.current_theme]
        
        back_btn = tk.Button(
            self.content_frame,
            text="← Back",
            font=('Segoe UI', 12),
            bg=theme["bg"],
            fg=theme["fg"],
            bd=0,
            cursor="hand2",
            command=self.create_unit_converter
        )
        back_btn.pack(anchor='w', pady=(0, 20))
        
        title_label = tk.Label(
            self.content_frame,
            text=f"{category} Converter",
            font=('Segoe UI', 20, 'bold'),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        title_label.pack(pady=(0, 30))
        
        if category == "Length":
            self.create_length_converter()
        elif category == "Area":
            self.create_area_converter()
        elif category == "Volume":
            self.create_volume_converter()
        elif category == "Weight":
            self.create_weight_converter()
        elif category == "Temperature":
            self.create_temperature_converter()
        elif category == "Speed":
            self.create_speed_converter()
        elif category == "Pressure":
            self.create_pressure_converter()
        elif category == "Power":
            self.create_power_converter()
        elif category == "Number System":
            self.create_number_system_converter()
        else:
            self.create_generic_converter(category)

    # --- NUMBER SYSTEM CONVERTER ---
    def create_number_system_converter(self):
        """Create Number System Converter"""
        theme = self.themes[self.current_theme]
        units = ["Decimal", "Binary", "Octal", "Hexadecimal"]
        
        from_frame = tk.Frame(self.content_frame, bg=theme["btn_num_bg"], relief=tk.RAISED, bd=2)
        from_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.from_unit_var = tk.StringVar(value=units[0])
        from_dropdown = ttk.Combobox(
            from_frame,
            textvariable=self.from_unit_var,
            values=units,
            font=('Segoe UI', 12),
            state='readonly'
        )
        from_dropdown.pack(fill=tk.X, padx=20, pady=15)
        
        self.from_value_var = tk.StringVar(value="0")
        from_entry = tk.Entry(
            from_frame,
            textvariable=self.from_value_var,
            font=('Segoe UI', 24, 'bold'),
            bg=theme["btn_num_bg"],
            fg=theme["fg"],
            bd=0
        )
        from_entry.pack(fill=tk.X, padx=20, pady=10)
        
        to_frame = tk.Frame(self.content_frame, bg=theme["btn_num_bg"], relief=tk.RAISED, bd=2)
        to_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.to_unit_var = tk.StringVar(value=units[1])
        to_dropdown = ttk.Combobox(
            to_frame,
            textvariable=self.to_unit_var,
            values=units,
            font=('Segoe UI', 12),
            state='readonly'
        )
        to_dropdown.pack(fill=tk.X, padx=20, pady=15)
        
        self.to_value_var = tk.StringVar(value="0")
        to_entry = tk.Entry(
            to_frame,
            textvariable=self.to_value_var,
            font=('Segoe UI', 24, 'bold'),
            bg=theme["btn_num_bg"],
            fg=theme["fg"],
            bd=0,
            state='readonly'
        )
        to_entry.pack(fill=tk.X, padx=20, pady=10)
        
        self.from_value_var.trace('w', lambda *args: self.convert_number_system())
        self.from_unit_var.trace('w', lambda *args: self.convert_number_system())
        self.to_unit_var.trace('w', lambda *args: self.convert_number_system())
        
        self.create_number_system_pad()
    
    def create_number_system_pad(self):
        """Create number pad for Number System converter"""
        theme = self.themes[self.current_theme]
        pad_frame = tk.Frame(self.content_frame, bg=theme["bg"])
        pad_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        button_config = {
            'font': ('Segoe UI', 18),
            'bd': 0,
            'width': 4,
            'height': 2,
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'bg': theme["btn_num_bg"],
            'fg': theme["fg"]
        }
        
        buttons = [
            ('AC', '#ff4444', lambda: self.from_value_var.set("0")),
            ('⌫', '#ffa500', self.number_system_backspace),
            ('A', theme["btn_op_bg"], lambda: self.number_system_input('A')),
            ('B', theme["btn_op_bg"], lambda: self.number_system_input('B')),
            ('7', theme["btn_num_bg"], lambda: self.number_system_input('7')),
            ('8', theme["btn_num_bg"], lambda: self.number_system_input('8')),
            ('9', theme["btn_num_bg"], lambda: self.number_system_input('9')),
            ('C', theme["btn_op_bg"], lambda: self.number_system_input('C')),
            ('4', theme["btn_num_bg"], lambda: self.number_system_input('4')),
            ('5', theme["btn_num_bg"], lambda: self.number_system_input('5')),
            ('6', theme["btn_num_bg"], lambda: self.number_system_input('6')),
            ('D', theme["btn_op_bg"], lambda: self.number_system_input('D')),
            ('1', theme["btn_num_bg"], lambda: self.number_system_input('1')),
            ('2', theme["btn_num_bg"], lambda: self.number_system_input('2')),
            ('3', theme["btn_num_bg"], lambda: self.number_system_input('3')),
            ('E', theme["btn_op_bg"], lambda: self.number_system_input('E')),
            ('0', theme["btn_num_bg"], lambda: self.number_system_input('0')),
            ('F', theme["btn_op_bg"], lambda: self.number_system_input('F')),
        ]
        
        row = 0
        col = 0
        for text, bg_color, command in buttons:
            btn = tk.Button(
                pad_frame,
                text=text,
                bg=bg_color,
                fg=theme["fg"] if bg_color != '#ff4444' else 'white',
                command=command,
                **button_config
            )
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
            pad_frame.grid_rowconfigure(row, weight=1)
            pad_frame.grid_columnconfigure(col, weight=1)
            col += 1
            if col > 3:
                col = 0
                row += 1
    
    def number_system_input(self, value: str):
        current = self.from_value_var.get()
        if current == "0":
            self.from_value_var.set(value)
        else:
            self.from_value_var.set(current + value)
    
    def number_system_backspace(self):
        current = self.from_value_var.get()
        if len(current) > 1:
            self.from_value_var.set(current[:-1])
        else:
            self.from_value_var.set("0")
    
    def convert_number_system(self):
        try:
            from_unit = self.from_unit_var.get()
            to_unit = self.to_unit_var.get()
            value_str = self.from_value_var.get()
            
            if from_unit == "Decimal":
                decimal_value = int(value_str, 10)
            elif from_unit == "Binary":
                decimal_value = int(value_str, 2)
            elif from_unit == "Octal":
                decimal_value = int(value_str, 8)
            elif from_unit == "Hexadecimal":
                decimal_value = int(value_str, 16)
            
            if to_unit == "Decimal":
                result = str(decimal_value)
            elif to_unit == "Binary":
                result = bin(decimal_value)[2:]
            elif to_unit == "Octal":
                result = oct(decimal_value)[2:]
            elif to_unit == "Hexadecimal":
                result = hex(decimal_value)[2:].upper()
            
            self.to_value_var.set(result)
        except ValueError:
            self.to_value_var.set("Error")
        except Exception:
            self.to_value_var.set("Error")

    # --- OTHER CONVERTERS ---
    def create_length_converter(self):
        units = ["Meters", "Kilometers", "Centimeters", "Millimeters", "Feet", "Inches", "Yards", "Miles"]
        factors = {
            "Meters": 1, "Kilometers": 1000, "Centimeters": 0.01, "Millimeters": 0.001,
            "Feet": 0.3048, "Inches": 0.0254, "Yards": 0.9144, "Miles": 1609.344
        }
        self.create_standard_converter_ui(units, factors)

    def create_area_converter(self):
        units = ["Square Meter (m²)", "Square Kilometer (km²)", "Square Centimeter (cm²)", 
                 "Square Millimeter (mm²)", "Square Inch (in²)", "Square Foot (ft²)", 
                 "Square Yard (yd²)", "Square Mile (mi²)", "Acre", "Hectare"]
        factors = {
            "Square Meter (m²)": 1, "Square Kilometer (km²)": 1e6,
            "Square Centimeter (cm²)": 1e-4, "Square Millimeter (mm²)": 1e-6,
            "Square Inch (in²)": 0.00064516, "Square Foot (ft²)": 0.092903,
            "Square Yard (yd²)": 0.836127, "Square Mile (mi²)": 2.59e6,
            "Acre": 4046.86, "Hectare": 10000
        }
        self.create_standard_converter_ui(units, factors)

    def create_volume_converter(self):
        units = ["Liter (L)", "Milliliter (mL)", "Cubic Meter (m³)", "Gallon (gal)", "Cup"]
        factors = {
            "Liter (L)": 1, "Milliliter (mL)": 0.001, "Cubic Meter (m³)": 1000,
            "Gallon (gal)": 3.78541, "Cup": 0.236588
        }
        self.create_standard_converter_ui(units, factors)

    def create_weight_converter(self):
        units = ["Kilograms", "Grams", "Milligrams", "Pounds", "Ounces"]
        factors = {
            "Kilograms": 1000, "Grams": 1, "Milligrams": 0.001,
            "Pounds": 453.592, "Ounces": 28.3495
        }
        self.create_standard_converter_ui(units, factors)

    def create_temperature_converter(self):
        units = ["Celsius", "Fahrenheit", "Kelvin"]
        self.create_generic_conversion_ui(units, self.convert_temperature)

    def create_speed_converter(self):
        units = ["m/s", "km/h", "mph", "knots"]
        factors = {"m/s": 1, "km/h": 0.277778, "mph": 0.44704, "knots": 0.514444}
        self.create_standard_converter_ui(units, factors)

    def create_pressure_converter(self):
        units = ["Pascal (Pa)", "Bar", "PSI", "Atmosphere (atm)"]
        factors = {"Pascal (Pa)": 1, "Bar": 100000, "PSI": 6894.76, "Atmosphere (atm)": 101325}
        self.create_standard_converter_ui(units, factors)

    def create_power_converter(self):
        units = ["Watt (W)", "Kilowatt (kW)", "Horsepower (hp)"]
        factors = {"Watt (W)": 1, "Kilowatt (kW)": 1000, "Horsepower (hp)": 745.7}
        self.create_standard_converter_ui(units, factors)

    def create_generic_converter(self, category: str):
        units = ["Unit 1", "Unit 2", "Unit 3"]
        self.create_generic_conversion_ui(units, None)

    def create_standard_converter_ui(self, units: list, factors: dict):
        theme = self.themes[self.current_theme]
        from_frame = tk.Frame(self.content_frame, bg=theme["btn_num_bg"], relief=tk.RAISED, bd=2)
        from_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.from_unit_var = tk.StringVar(value=units[0])
        self.from_factors = factors
        
        ttk.Combobox(from_frame, textvariable=self.from_unit_var, values=units, 
                    state='readonly', font=('Segoe UI', 12)).pack(fill=tk.X, padx=20, pady=15)
        
        self.from_value_var = tk.StringVar(value="1")
        tk.Entry(from_frame, textvariable=self.from_value_var, font=('Segoe UI', 24, 'bold'), 
                bg=theme["btn_num_bg"], fg=theme["fg"], bd=0).pack(fill=tk.X, padx=20, pady=10)
        
        to_frame = tk.Frame(self.content_frame, bg=theme["btn_num_bg"], relief=tk.RAISED, bd=2)
        to_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.to_unit_var = tk.StringVar(value=units[1] if len(units) > 1 else units[0])
        ttk.Combobox(to_frame, textvariable=self.to_unit_var, values=units, 
                    state='readonly', font=('Segoe UI', 12)).pack(fill=tk.X, padx=20, pady=15)
        
        self.to_value_var = tk.StringVar(value="0")
        tk.Entry(to_frame, textvariable=self.to_value_var, font=('Segoe UI', 24, 'bold'), 
                bg=theme["btn_num_bg"], fg=theme["fg"], bd=0, state='readonly').pack(fill=tk.X, padx=20, pady=10)
        
        self.from_value_var.trace('w', lambda *args: self.perform_linear_conversion())
        self.from_unit_var.trace('w', lambda *args: self.perform_linear_conversion())
        self.to_unit_var.trace('w', lambda *args: self.perform_linear_conversion())
        
        self.create_number_pad()

    def perform_linear_conversion(self):
        try:
            value = float(self.from_value_var.get())
            from_unit = self.from_unit_var.get()
            to_unit = self.to_unit_var.get()
            
            from_factor = self.from_factors[from_unit]
            to_factor = self.from_factors[to_unit]
            
            base_value = value * from_factor
            result = base_value / to_factor
            
            if result == 0:
                self.to_value_var.set("0")
            elif abs(result) < 0.0001 or abs(result) > 1e6:
                self.to_value_var.set(f"{result:.6e}")
            else:
                self.to_value_var.set(f"{result:.6g}")
        except ValueError:
            self.to_value_var.set("Error")

    def create_generic_conversion_ui(self, units: list, convert_func):
        theme = self.themes[self.current_theme]
        from_frame = tk.Frame(self.content_frame, bg=theme["btn_num_bg"], relief=tk.RAISED, bd=2)
        from_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.from_unit_var = tk.StringVar(value=units[0])
        ttk.Combobox(from_frame, textvariable=self.from_unit_var, values=units, 
                    font=('Segoe UI', 12), state='readonly').pack(fill=tk.X, padx=20, pady=15)
        
        self.from_value_var = tk.StringVar(value="0")
        tk.Entry(from_frame, textvariable=self.from_value_var, font=('Segoe UI', 24, 'bold'), 
                bg=theme["btn_num_bg"], fg=theme["fg"], bd=0).pack(fill=tk.X, padx=20, pady=10)
        
        to_frame = tk.Frame(self.content_frame, bg=theme["btn_num_bg"], relief=tk.RAISED, bd=2)
        to_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.to_unit_var = tk.StringVar(value=units[1] if len(units) > 1 else units[0])
        ttk.Combobox(to_frame, textvariable=self.to_unit_var, values=units, 
                    font=('Segoe UI', 12), state='readonly').pack(fill=tk.X, padx=20, pady=15)
        
        self.to_value_var = tk.StringVar(value="0")
        tk.Entry(to_frame, textvariable=self.to_value_var, font=('Segoe UI', 24, 'bold'), 
                bg=theme["btn_num_bg"], fg=theme["fg"], bd=0, state='readonly').pack(fill=tk.X, padx=20, pady=10)
        
        self.from_value_var.trace('w', lambda *args: self.perform_conversion(convert_func))
        self.from_unit_var.trace('w', lambda *args: self.perform_conversion(convert_func))
        self.to_unit_var.trace('w', lambda *args: self.perform_conversion(convert_func))
        
        self.create_number_pad()

    def create_number_pad(self):
        theme = self.themes[self.current_theme]
        pad_frame = tk.Frame(self.content_frame, bg=theme["bg"])
        pad_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        button_config = {
            'font': ('Segoe UI', 18),
            'bd': 0,
            'width': 4,
            'height': 2,
            'relief': tk.FLAT,
            'cursor': 'hand2',
            'bg': theme["btn_num_bg"],
            'fg': theme["fg"]
        }
        
        buttons = [
            ('AC', '#ff4444', lambda: self.from_value_var.set("0")),
            ('', '#ffa500', self.converter_backspace),
            ('.', theme["btn_num_bg"], lambda: self.converter_input('.')),
            ('7', theme["btn_num_bg"], lambda: self.converter_input('7')),
            ('8', theme["btn_num_bg"], lambda: self.converter_input('8')),
            ('9', theme["btn_num_bg"], lambda: self.converter_input('9')),
            ('4', theme["btn_num_bg"], lambda: self.converter_input('4')),
            ('5', theme["btn_num_bg"], lambda: self.converter_input('5')),
            ('6', theme["btn_num_bg"], lambda: self.converter_input('6')),
            ('1', theme["btn_num_bg"], lambda: self.converter_input('1')),
            ('2', theme["btn_num_bg"], lambda: self.converter_input('2')),
            ('3', theme["btn_num_bg"], lambda: self.converter_input('3')),
            ('0', theme["btn_num_bg"], lambda: self.converter_input('0')),
        ]
        
        row = 0
        col = 0
        for text, bg_color, command in buttons:
            btn = tk.Button(pad_frame, text=text, bg=bg_color, fg=theme["fg"] if bg_color != '#ff4444' else 'white', 
                          command=command, **button_config)
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='nsew')
            pad_frame.grid_rowconfigure(row, weight=1)
            pad_frame.grid_columnconfigure(col, weight=1)
            col += 1
            if col > 3:
                col = 0
                row += 1

    def converter_input(self, value: str):
        current = self.from_value_var.get()
        if current == "0":
            self.from_value_var.set(value)
        else:
            self.from_value_var.set(current + value)
    
    def converter_backspace(self):
        current = self.from_value_var.get()
        if len(current) > 1:
            self.from_value_var.set(current[:-1])
        else:
            self.from_value_var.set("0")
            
    def convert_temperature(self):
        try:
            value = float(self.from_value_var.get())
            from_unit = self.from_unit_var.get()
            to_unit = self.to_unit_var.get()
            
            if from_unit == "Celsius":
                celsius = value
            elif from_unit == "Fahrenheit":
                celsius = (value - 32) * 5/9
            else:
                celsius = value - 273.15
                
            if to_unit == "Celsius":
                result = celsius
            elif to_unit == "Fahrenheit":
                result = (celsius * 9/5) + 32
            else:
                result = celsius + 273.15
                
            self.to_value_var.set(f"{result:.2f}")
        except ValueError:
            self.to_value_var.set("0")
            
    def perform_conversion(self, convert_func):
        if convert_func:
            convert_func()

    # --- CALCULATOR FUNCTIONS ---
    def on_button_click(self, value: str):
        if value in ['+', '-', '*', '/', '%', '**', '.', '(' , ')']:
            self.current_expression += value
        elif value == '00':
            if self.current_expression and self.current_expression != '0':
                self.current_expression += '00'
        else:
            if self.current_expression == '0':
                self.current_expression = value
            else:
                self.current_expression += value
                
        self.display_var.set(self.current_expression)
        
    def clear_all(self):
        self.current_expression = ""
        self.display_var.set("0")
        
    def backspace(self):
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            if not self.current_expression:
                self.current_expression = "0"
            self.display_var.set(self.current_expression)
            
    def calculate(self):
        try:
            expression = self.current_expression
            
            expression = expression.replace('π', str(math.pi))
            expression = expression.replace('e', str(math.e))
            
            if self.current_mode == "scientific" and self.angle_mode.get() == 'deg':
                expression = self._convert_trig_for_degrees(expression)
            
            result = eval(expression, {"__builtins__": None}, {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "asin": math.asin, "acos": math.acos, "atan": math.atan,
                "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
                "pi": math.pi, "e": math.e, "factorial": math.factorial
            })
            
            self.add_to_history(f"{self.current_expression} = {result}")
            
            self.current_expression = str(result)
            self.display_var.set(self.current_expression)
        except Exception as e:
            self.display_var.set("Error")
            self.current_expression = ""
    
    def _convert_trig_for_degrees(self, expr):
        expr = expr.replace('sin(', 'math.sin(math.radians(')
        expr = expr.replace('cos(', 'math.cos(math.radians(')
        expr = expr.replace('tan(', 'math.tan(math.radians(')
        return expr
            
    def scientific_func(self, func: str):
        if func == 'sin':
            self.current_expression += "sin("
        elif func == 'cos':
            self.current_expression += "cos("
        elif func == 'tan':
            self.current_expression += "tan("
        elif func == 'log':
            self.current_expression += "log("
        elif func == 'ln':
            self.current_expression += "ln("
        elif func == 'sqrt':
            self.current_expression += "sqrt("
        elif func == 'factorial':
            self.current_expression += "factorial("
        
        self.display_var.set(self.current_expression)
            
    def toggle_angle_mode(self):
        if self.angle_mode.get() == "rad":
            self.angle_mode.set("deg")
        else:
            self.angle_mode.set("rad")

    # --- MENU AND NAVIGATION ---
    def show_menu(self):
        """Show menu popup with History and Settings"""
        theme = self.themes[self.current_theme]
        menu = tk.Toplevel(self.root)
        menu.title("Menu")
        menu.geometry("220x120")
        menu.resizable(False, False)
        
        x = self.root.winfo_x() + 280
        y = self.root.winfo_y() + 70
        menu.geometry(f"+{x}+{y}")
        
        menu.overrideredirect(True)
        menu.configure(bg=theme["menu_bg"])
        
        history_btn = tk.Button(
            menu, text="📜 History", font=('Segoe UI', 12), 
            bg=theme["menu_bg"], fg=theme["menu_fg"], bd=0, pady=10, 
            cursor="hand2", activebackground=theme["btn_op_bg"],
            activeforeground=theme["fg"], anchor='w', padx=20,
            command=lambda: [menu.destroy(), self.show_history()]
        )
        history_btn.pack(fill=tk.X, pady=2)
        
        settings_btn = tk.Button(
            menu, text="⚙️ Settings", font=('Segoe UI', 12), 
            bg=theme["menu_bg"], fg=theme["menu_fg"], bd=0, pady=10, 
            cursor="hand2", activebackground=theme["btn_op_bg"],
            activeforeground=theme["fg"], anchor='w', padx=20,
            command=lambda: [menu.destroy(), self.show_settings()]
        )
        settings_btn.pack(fill=tk.X, pady=2)
        
        menu.bind('<Button-1>', lambda e: menu.destroy())
        
    def show_history(self):
        """Show calculation history"""
        theme = self.themes[self.current_theme]
        history_window = tk.Toplevel(self.root)
        history_window.title("📜 History")
        history_window.geometry("400x450")
        history_window.resizable(False, False)
        
        x = self.root.winfo_x() + 25
        y = self.root.winfo_y() + 150
        history_window.geometry(f"400x450+{x}+{y}")
        history_window.configure(bg=theme["bg"])
        
        title_frame = tk.Frame(history_window, bg=theme["bg"])
        title_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(title_frame, text="📜 Calculation History", 
                font=('Segoe UI', 18, 'bold'), bg=theme["bg"], fg=theme["fg"]).pack()
        
        listbox_frame = tk.Frame(history_window, bg=theme["bg"])
        listbox_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        history_listbox = tk.Listbox(listbox_frame, font=('Segoe UI', 11),
            bg=theme["btn_num_bg"], fg=theme["fg"],
            selectbackground=theme["btn_eq_bg"], selectforeground="white",
            yscrollcommand=scrollbar.set, relief=tk.FLAT, bd=1)
        history_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=history_listbox.yview)
        
        if self.history:
            for item in reversed(self.history[-50:]):
                history_listbox.insert(tk.END, f"  {item}")
        else:
            history_listbox.insert(tk.END, "  📭 No history yet")
            
        btn_frame = tk.Frame(history_window, bg=theme["bg"])
        btn_frame.pack(fill=tk.X, padx=15, pady=10)
        
        clear_btn = tk.Button(btn_frame, text="🗑️ Clear History", font=('Segoe UI', 11), 
            bg='#ff4444', fg='white', bd=0, pady=10, cursor="hand2",
            command=lambda: [self.clear_history(), history_listbox.delete(0, tk.END), 
                           history_listbox.insert(tk.END, "   No history yet")])
        clear_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        close_btn = tk.Button(btn_frame, text="❌ Close", font=('Segoe UI', 11), 
            bg=theme["btn_op_bg"], fg=theme["fg"], bd=0, pady=10, cursor="hand2",
            command=history_window.destroy)
        close_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
    def show_settings(self):
        """Show settings dialog with theme toggle"""
        theme = self.themes[self.current_theme]
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ Settings")
        settings_window.geometry("350x300")
        settings_window.resizable(False, False)
        
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 200
        settings_window.geometry(f"350x300+{x}+{y}")
        settings_window.configure(bg=theme["bg"])
        
        tk.Label(settings_window, text="⚙️ Settings", font=('Segoe UI', 20, 'bold'),
                bg=theme["bg"], fg=theme["fg"]).pack(pady=20)
        
        theme_frame = tk.Frame(settings_window, bg=theme["bg"])
        theme_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(theme_frame, text="🎨 Theme:", font=('Segoe UI', 14, 'bold'),
                bg=theme["bg"], fg=theme["fg"]).pack(anchor='w')
        
        btn_frame = tk.Frame(theme_frame, bg=theme["bg"])
        btn_frame.pack(fill=tk.X, pady=10)
        
        light_btn = tk.Button(btn_frame, text="☀️ Light", font=('Segoe UI', 12),
            bg='#ffffff' if self.current_theme == "light" else theme["btn_num_bg"],
            fg='#1a1a1a', bd=2 if self.current_theme == "light" else 0,
            relief=tk.RAISED if self.current_theme == "light" else tk.FLAT,
            cursor="hand2", command=lambda: self.set_theme("light", settings_window))
        light_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        dark_btn = tk.Button(btn_frame, text="🌙 Dark", font=('Segoe UI', 12),
            bg='#2d2d2d' if self.current_theme == "dark" else theme["btn_num_bg"],
            fg='#ffffff' if self.current_theme == "dark" else theme["fg"],
            bd=2 if self.current_theme == "dark" else 0,
            relief=tk.RAISED if self.current_theme == "dark" else tk.FLAT,
            cursor="hand2", command=lambda: self.set_theme("dark", settings_window))
        dark_btn.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        tk.Label(settings_window, text=f"Current: {'☀️ Light' if self.current_theme == 'light' else '🌙 Dark'} Mode",
                font=('Segoe UI', 11), bg=theme["bg"], fg=theme["fg"]).pack(pady=10)
        
        tk.Label(settings_window, text="🔢 Decimal Precision: Auto",
                font=('Segoe UI', 11), bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        
        tk.Label(settings_window, text=f"📐 Angle Mode: {self.angle_mode.get().upper()}",
                font=('Segoe UI', 11), bg=theme["bg"], fg=theme["fg"]).pack(pady=5)
        
        close_btn = tk.Button(settings_window, text="❌ Close", font=('Segoe UI', 12), 
            bg=theme["btn_op_bg"], fg=theme["fg"], bd=0, pady=10, cursor="hand2",
            command=settings_window.destroy)
        close_btn.pack(fill=tk.X, padx=30, pady=20)
    
    def set_theme(self, theme_name: str, settings_window=None):
        self.current_theme = theme_name
        self.save_theme()
        self.create_main_layout()
        if settings_window:
            settings_window.destroy()
            
    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def add_to_history(self, entry: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.append(f"[{timestamp}] {entry}")
        self.save_history()
        
    def clear_history(self):
        self.history = []
        self.save_history()
        
    def save_history(self):
        try:
            with open('calculator_history.json', 'w') as f:
                json.dump(self.history, f)
        except:
            pass
            
    def load_history(self):
        try:
            if os.path.exists('calculator_history.json'):
                with open('calculator_history.json', 'r') as f:
                    self.history = json.load(f)
        except:
            self.history = []
    
    def save_theme(self):
        try:
            with open('calculator_theme.json', 'w') as f:
                json.dump({"theme": self.current_theme}, f)
        except:
            pass
    
    def load_theme(self):
        try:
            if os.path.exists('calculator_theme.json'):
                with open('calculator_theme.json', 'r') as f:
                    data = json.load(f)
                    self.current_theme = data.get("theme", "light")
        except:
            self.current_theme = "light"


def main():
    root = tk.Tk() 
    app = CalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()