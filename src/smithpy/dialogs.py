"""Dialog components for smithpy GUI."""

import math
import tkinter as tk
from tkinter import ttk, messagebox

from .parsing import parse_lc_value, parse_length, parse_ohm_value


class ComponentDialog(tk.Toplevel):
    """Dialog to create or edit a component with slider preview."""

    def __init__(self, master, ctype, data=None, index=None):
        super().__init__(master)
        self.res = None
        self.ctype = ctype
        self.index = index
        self.master_app = master
        self.transient(master)
        self.grab_set()
        self.title(f"{ctype} parameters")
        self.build_widgets(data or {})
        self.protocol("WM_DELETE_WINDOW", self.cancel)

    def calc_resolution(self, mn, mx):
        span = mx - mn
        if span <= 0:
            return 1.0
        exp = math.floor(math.log10(abs(span))) - 2
        return 10 ** exp

    def build_widgets(self, data):
        row = 0
        if self.ctype in ("L", "C", "R"):
            lbl = "Value (e.g., 10 nH)" if self.ctype in ("L", "C") else "Value (Ohm)"
            ttk.Label(self, text=lbl).grid(row=row, column=0)
            self.val_entry = ttk.Entry(self)
            self.val_entry.grid(row=row, column=1)
            self.val_entry.insert(0, data.get("disp", ""))
            row += 1
            ttk.Label(self, text="Slider min").grid(row=row, column=0)
            self.min_entry = ttk.Entry(self, width=6)
            self.min_entry.grid(row=row, column=1)
            self.min_entry.insert(0, str(data.get("min", 0)))
            row += 1
            ttk.Label(self, text="Slider max").grid(row=row, column=0)
            self.max_entry = ttk.Entry(self, width=6)
            self.max_entry.grid(row=row, column=1)
            self.max_entry.insert(0, str(data.get("max", 100)))
            row += 1
            mn = float(self.min_entry.get())
            mx = float(self.max_entry.get())
            res = self.calc_resolution(mn, mx)
            self.scale = tk.Scale(self, from_=mn, to=mx, resolution=res,
                                  orient="horizontal", command=self.on_slider)
            self.scale.grid(row=row, column=0, columnspan=2, sticky="we")
            if "value" in data:
                if self.ctype == "L":
                    self.scale.set(data["value"] * 1e9)
                elif self.ctype == "C":
                    self.scale.set(data["value"] * 1e12)
                else:
                    self.scale.set(data["value"])
            row += 1
            ttk.Button(self, text="Update Range", command=self.update_scale_range).grid(row=row, column=0, columnspan=2)
            row += 1
            ttk.Label(self, text="Orientation").grid(row=row, column=0)
            self.orient = tk.StringVar(value=data.get("orient", "series"))
            ttk.OptionMenu(self, self.orient, "series", "series", "shunt").grid(row=row, column=1)
        elif self.ctype == "TL":
            ttk.Label(self, text="Length").grid(row=row, column=0)
            self.len_entry = ttk.Entry(self)
            self.len_entry.grid(row=row, column=1)
            self.len_entry.insert(0, data.get("len_disp", ""))
            row += 1
            mode = data.get("len_mode", "deg")
            to_val = 180 if mode == "deg" else 0.5
            ttk.Label(self, text="Slider min").grid(row=row, column=0)
            self.min_entry = ttk.Entry(self, width=6)
            self.min_entry.grid(row=row, column=1)
            self.min_entry.insert(0, str(data.get("min", 0)))
            row += 1
            ttk.Label(self, text="Slider max").grid(row=row, column=0)
            self.max_entry = ttk.Entry(self, width=6)
            self.max_entry.grid(row=row, column=1)
            self.max_entry.insert(0, str(data.get("max", to_val)))
            row += 1
            mn = float(self.min_entry.get())
            mx = float(self.max_entry.get())
            res = self.calc_resolution(mn, mx)
            if mode == "deg":
                res = max(res, 1)
            self.scale = tk.Scale(self, from_=mn, to=mx, resolution=res,
                                  orient="horizontal", command=self.on_slider)
            self.scale.grid(row=row, column=0, columnspan=2, sticky="we")
            if "length" in data:
                val = data["length"] if mode == "deg" else data["length"] / 360.0
                self.scale.set(val)
            row += 1
            ttk.Button(self, text="Update Range", command=self.update_scale_range).grid(row=row, column=0, columnspan=2)
            row += 1
            ttk.Label(self, text="Mode").grid(row=row, column=0)
            self.len_mode = tk.StringVar(value=data.get("len_mode", "deg"))
            ttk.OptionMenu(self, self.len_mode, mode, "deg", "lambda").grid(row=row, column=1)
            row += 1
            ttk.Label(self, text="Z0 (Ohm)").grid(row=row, column=0)
            self.z0_entry = ttk.Entry(self)
            self.z0_entry.grid(row=row, column=1)
            self.z0_entry.insert(0, str(data.get("z0", getattr(self.master, 'z0', 50))))
        elif self.ctype == "STUB":
            ttk.Label(self, text="Length").grid(row=row, column=0)
            self.len_entry = ttk.Entry(self)
            self.len_entry.grid(row=row, column=1)
            self.len_entry.insert(0, data.get("len_disp", ""))
            row += 1
            mode = data.get("len_mode", "deg")
            to_val = 180 if mode == "deg" else 0.5
            ttk.Label(self, text="Slider min").grid(row=row, column=0)
            self.min_entry = ttk.Entry(self, width=6)
            self.min_entry.grid(row=row, column=1)
            self.min_entry.insert(0, str(data.get("min", 0)))
            row += 1
            ttk.Label(self, text="Slider max").grid(row=row, column=0)
            self.max_entry = ttk.Entry(self, width=6)
            self.max_entry.grid(row=row, column=1)
            self.max_entry.insert(0, str(data.get("max", to_val)))
            row += 1
            mn = float(self.min_entry.get())
            mx = float(self.max_entry.get())
            res = self.calc_resolution(mn, mx)
            if mode == "deg":
                res = max(res, 1)
            self.scale = tk.Scale(self, from_=mn, to=mx, resolution=res,
                                  orient="horizontal", command=self.on_slider)
            self.scale.grid(row=row, column=0, columnspan=2, sticky="we")
            if "length" in data:
                val = data["length"] if mode == "deg" else data["length"] / 360.0
                self.scale.set(val)
            row += 1
            ttk.Button(self, text="Update Range", command=self.update_scale_range).grid(row=row, column=0, columnspan=2)
            row += 1
            ttk.Label(self, text="Mode").grid(row=row, column=0)
            self.len_mode = tk.StringVar(value=data.get("len_mode", "deg"))
            ttk.OptionMenu(self, self.len_mode, mode, "deg", "lambda").grid(row=row, column=1)
            row += 1
            ttk.Label(self, text="Z0 (Ohm)").grid(row=row, column=0)
            self.z0_entry = ttk.Entry(self)
            self.z0_entry.grid(row=row, column=1)
            self.z0_entry.insert(0, str(data.get("z0", getattr(self.master, 'z0', 50))))
            row += 1
            ttk.Label(self, text="Type").grid(row=row, column=0)
            self.kind = tk.StringVar(value=data.get("kind", "open"))
            ttk.OptionMenu(self, self.kind, self.kind.get(), "open", "short").grid(row=row, column=1)
        ttk.Button(self, text="OK", command=self.ok).grid(row=row+1, column=0)
        ttk.Button(self, text="Cancel", command=self.cancel).grid(row=row+1, column=1)

    def ok(self):
        try:
            if self.ctype in ("L", "C", "R"):
                val_str = self.val_entry.get()
                if self.ctype == "R":
                    val = parse_ohm_value(val_str)
                else:
                    val = parse_lc_value(val_str)
                self.res = {
                    "value": val,
                    "disp": val_str,
                    "orient": self.orient.get(),
                    "min": float(self.min_entry.get()),
                    "max": float(self.max_entry.get()),
                }
            elif self.ctype == "TL":
                val_str = self.len_entry.get()
                mode = self.len_mode.get()
                length, disp = parse_length(val_str, "deg" if mode == "deg" else "lambda")
                self.res = {
                    "length": length,
                    "len_disp": val_str,
                    "len_mode": mode,
                    "z0": float(self.z0_entry.get()),
                    "disp": disp,
                    "min": float(self.min_entry.get()),
                    "max": float(self.max_entry.get()),
                }
            elif self.ctype == "STUB":
                val_str = self.len_entry.get()
                mode = self.len_mode.get()
                length, disp = parse_length(val_str, "deg" if mode == "deg" else "lambda")
                self.res = {
                    "length": length,
                    "len_disp": val_str,
                    "len_mode": mode,
                    "z0": float(self.z0_entry.get()),
                    "kind": self.kind.get(),
                    "disp": disp,
                    "min": float(self.min_entry.get()),
                    "max": float(self.max_entry.get()),
                }
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return
        self.destroy()

    def cancel(self):
        self.res = None
        self.destroy()
        self.master_app.update_point()

    def update_scale_range(self):
        """Apply min/max from entries to the slider."""
        try:
            mn = float(self.min_entry.get())
            mx = float(self.max_entry.get())
            if mx <= mn:
                raise ValueError
            res = self.calc_resolution(mn, mx)
            if getattr(self, 'len_mode', None) and self.len_mode.get() == 'deg':
                res = max(res, 1)
            self.scale.config(from_=mn, to=mx, resolution=res)
        except Exception:
            messagebox.showerror("Error", "Invalid range")

    def on_slider(self, val):
        """Update entry from slider and preview impedance."""
        try:
            if self.ctype == "L":
                disp = f"{float(val):.4g} nH"
                value = float(val) * 1e-9
                self.val_entry.delete(0, tk.END)
                self.val_entry.insert(0, disp)
                comp = {"type": "L", "value": value, "disp": disp, "orient": self.orient.get()}
            elif self.ctype == "C":
                disp = f"{float(val):.4g} pF"
                value = float(val) * 1e-12
                self.val_entry.delete(0, tk.END)
                self.val_entry.insert(0, disp)
                comp = {"type": "C", "value": value, "disp": disp, "orient": self.orient.get()}
            elif self.ctype == "R":
                disp = f"{float(val):.4g}"
                value = float(val)
                self.val_entry.delete(0, tk.END)
                self.val_entry.insert(0, disp)
                comp = {"type": "R", "value": value, "disp": disp, "orient": self.orient.get()}
            elif self.ctype in ("TL", "STUB"):
                mode = self.len_mode.get()
                if mode == "deg":
                    length = float(val)
                    disp = f"{length:.2f}\u00b0"
                else:
                    length = float(val) * 360.0
                    disp = f"{float(val):.4g} \u03bb"
                self.len_entry.delete(0, tk.END)
                self.len_entry.insert(0, disp)
                comp = {
                    "type": self.ctype,
                    "length": length,
                    "len_disp": disp,
                    "len_mode": mode,
                    "z0": float(self.z0_entry.get()),
                    "disp": disp,
                }
                if self.ctype == "STUB":
                    comp["kind"] = self.kind.get()
            else:
                return
            self.master_app.preview_update(comp, self.index)
        except Exception:
            pass

__all__ = ["ComponentDialog"]
