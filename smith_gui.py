import tkinter as tk
from tkinter import messagebox
import re
import math

PI2 = 2 * 3.141592653589793
# number of intermediate points for each component
TRACE_STEPS = 100


def parse_lc_value(text):
    """Parse a value like '10 nH' or '50 uF'."""
    if not text:
        raise ValueError("empty value")
    text = text.strip()
    m = re.match(r"([0-9.]+)\s*([pnufm]?)[HhFf]", text)
    if not m:
        raise ValueError("invalid format")
    num = float(m.group(1))
    prefix = m.group(2).lower()
    mult = {
        'p': 1e-12,
        'n': 1e-9,
        'u': 1e-6,
        'f': 1e-15,
        'm': 1e-3,
        '': 1.0,
    }[prefix]
    return num * mult

def parse_length(value, mode):
    """Return length in degrees and a display string.

    The input may contain a trailing degree sign or the lambda symbol, so
    both ``90`` and ``90°`` are accepted for degrees and values like
    ``0.25`` or ``0.25 λ`` work for ``l/λ`` input.
    """
    value = value.strip().replace("°", "").replace("\u03bb", "")
    if mode == "deg":
        deg = float(value)
        return deg, f"{deg}\u00b0"
    frac = float(value)
    deg = frac * 360.0
    return deg, f"{frac} \u03bb"


def parse_ohm_value(text):
    """Parse a resistor value in ohms."""
    if not text:
        raise ValueError("empty value")
    text = text.strip().lower()
    m = re.match(r"([0-9.]+)", text)
    if not m:
        raise ValueError("invalid format")
    return float(m.group(1))


def parse_complex_impedance(text):
    """Parse a complex impedance string like '50+30j'."""
    if not text:
        raise ValueError("empty load impedance")
    t = text.replace(' ', '')
    try:
        return complex(t)
    except Exception as e:
        raise ValueError("invalid complex impedance") from e


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
            tk.Label(self, text=lbl).grid(row=row, column=0)
            self.val_entry = tk.Entry(self)
            self.val_entry.grid(row=row, column=1)
            self.val_entry.insert(0, data.get("disp", ""))
            row += 1
            tk.Label(self, text="Slider min").grid(row=row, column=0)
            self.min_entry = tk.Entry(self, width=6)
            self.min_entry.grid(row=row, column=1)
            self.min_entry.insert(0, str(data.get("min", 0)))
            row += 1
            tk.Label(self, text="Slider max").grid(row=row, column=0)
            self.max_entry = tk.Entry(self, width=6)
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
            tk.Button(self, text="Update Range", command=self.update_scale_range).grid(row=row, column=0, columnspan=2)
            row += 1
            tk.Label(self, text="Orientation").grid(row=row, column=0)
            self.orient = tk.StringVar(value=data.get("orient", "series"))
            tk.OptionMenu(self, self.orient, "series", "shunt").grid(row=row, column=1)
        elif self.ctype == "TL":
            tk.Label(self, text="Length").grid(row=row, column=0)
            self.len_entry = tk.Entry(self)
            self.len_entry.grid(row=row, column=1)
            self.len_entry.insert(0, data.get("len_disp", ""))
            row += 1
            mode = data.get("len_mode", "deg")
            to_val = 180 if mode == "deg" else 0.5
            tk.Label(self, text="Slider min").grid(row=row, column=0)
            self.min_entry = tk.Entry(self, width=6)
            self.min_entry.grid(row=row, column=1)
            self.min_entry.insert(0, str(data.get("min", 0)))
            row += 1
            tk.Label(self, text="Slider max").grid(row=row, column=0)
            self.max_entry = tk.Entry(self, width=6)
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
            tk.Button(self, text="Update Range", command=self.update_scale_range).grid(row=row, column=0, columnspan=2)
            row += 1
            tk.Label(self, text="Mode").grid(row=row, column=0)
            self.len_mode = tk.StringVar(value=data.get("len_mode", "deg"))
            tk.OptionMenu(self, self.len_mode, "deg", "lambda").grid(row=row, column=1)
            row += 1
            tk.Label(self, text="Z0 (Ohm)").grid(row=row, column=0)
            self.z0_entry = tk.Entry(self)
            self.z0_entry.grid(row=row, column=1)
            self.z0_entry.insert(0, str(data.get("z0", getattr(self.master, 'z0', 50))))
        elif self.ctype == "STUB":
            tk.Label(self, text="Length").grid(row=row, column=0)
            self.len_entry = tk.Entry(self)
            self.len_entry.grid(row=row, column=1)
            self.len_entry.insert(0, data.get("len_disp", ""))
            row += 1
            mode = data.get("len_mode", "deg")
            to_val = 180 if mode == "deg" else 0.5
            tk.Label(self, text="Slider min").grid(row=row, column=0)
            self.min_entry = tk.Entry(self, width=6)
            self.min_entry.grid(row=row, column=1)
            self.min_entry.insert(0, str(data.get("min", 0)))
            row += 1
            tk.Label(self, text="Slider max").grid(row=row, column=0)
            self.max_entry = tk.Entry(self, width=6)
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
            tk.Button(self, text="Update Range", command=self.update_scale_range).grid(row=row, column=0, columnspan=2)
            row += 1
            tk.Label(self, text="Mode").grid(row=row, column=0)
            self.len_mode = tk.StringVar(value=data.get("len_mode", "deg"))
            tk.OptionMenu(self, self.len_mode, "deg", "lambda").grid(row=row, column=1)
            row += 1
            tk.Label(self, text="Z0 (Ohm)").grid(row=row, column=0)
            self.z0_entry = tk.Entry(self)
            self.z0_entry.grid(row=row, column=1)
            self.z0_entry.insert(0, str(data.get("z0", getattr(self.master, 'z0', 50))))
            row += 1
            tk.Label(self, text="Type").grid(row=row, column=0)
            self.kind = tk.StringVar(value=data.get("kind", "open"))
            tk.OptionMenu(self, self.kind, "open", "short").grid(row=row, column=1)
        tk.Button(self, text="OK", command=self.ok).grid(row=row+1, column=0)
        tk.Button(self, text="Cancel", command=self.cancel).grid(row=row+1, column=1)

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

class SmithChartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Interactive Smith Chart")

        # data
        self.components = []  # list of component dicts
        self.freq = 1e9  # 1 GHz for calculations
        self.z0 = 50.0
        self.za = 50+0j

        # layout
        left = tk.Frame(self)
        right = tk.Frame(self)
        left.pack(side="left", fill="both", expand=True)
        right.pack(side="right", fill="y")

        top_canvas = tk.Frame(left)
        bottom_canvas = tk.Frame(left)
        top_canvas.pack(fill="both", expand=True)
        bottom_canvas.pack(fill="both", expand=True)

        # settings
        settings = tk.Frame(right)
        settings.pack(fill="x")
        tk.Label(settings, text="Freq [MHz]").grid(row=0, column=0)
        self.freq_entry = tk.Entry(settings, width=12)
        self.freq_entry.grid(row=0, column=1)
        self.freq_entry.insert(0, str(self.freq / 1e6))
        tk.Label(settings, text="Z0").grid(row=0, column=2)
        self.z0_entry = tk.Entry(settings, width=6)
        self.z0_entry.grid(row=0, column=3)
        self.z0_entry.insert(0, str(self.z0))

        tk.Label(settings, text="Z_A").grid(row=1, column=0)
        self.za_entry = tk.Entry(settings, width=12)
        self.za_entry.grid(row=1, column=1, columnspan=3, sticky="we")
        self.za_entry.insert(0, "50+0j")
        tk.Button(settings, text="Apply", command=self.apply_settings).grid(row=0, column=4, rowspan=2, sticky="ns")

        self.canvas = tk.Canvas(top_canvas, width=600, height=300, bg="white")
        self.canvas.pack(fill="both", expand=True)
        self.adm_canvas = tk.Canvas(bottom_canvas, width=600, height=300, bg="white")
        self.adm_canvas.pack(fill="both", expand=True)

        self.comp_listbox = tk.Listbox(right, width=40)
        self.comp_listbox.pack(fill="y")
        self.comp_listbox.bind("<Double-Button-1>", self.edit_component)

        self.circ_canvas = tk.Canvas(right, width=200, height=120, bg="white")
        self.circ_canvas.pack(fill="x")

        btn_frame = tk.Frame(right)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="Add Resistor", command=self.add_resistor).pack(fill="x")
        tk.Button(btn_frame, text="Add Inductor", command=self.add_inductor).pack(fill="x")
        tk.Button(btn_frame, text="Add Capacitor", command=self.add_capacitor).pack(fill="x")
        tk.Button(btn_frame, text="Add TL", command=self.add_tline).pack(fill="x")
        tk.Button(btn_frame, text="Add Stub", command=self.add_stub).pack(fill="x")
        tk.Button(btn_frame, text="Remove Last", command=self.remove_last).pack(fill="x")

        self.draw_chart()
        self.update_point()
        self.draw_circuit()

    def draw_one_chart(self, canvas, mode="impedance"):
        canvas.delete("all")
        w = int(canvas["width"])
        h = int(canvas["height"])
        center = w // 2, h // 2
        radius = min(w, h) // 2 - 10
        cx, cy = center
        r = radius
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r)
        canvas.create_line(cx - r, cy, cx + r, cy, fill="lightgray")
        canvas.create_line(cx, cy - r, cx, cy + r, fill="lightgray")
        if mode == "impedance":
            canvas.create_text(cx + r + 15, cy, text="Re(z/Z0)", anchor="w")
            canvas.create_text(cx - r - 15, cy, text="-Re(z/Z0)", anchor="e")
            canvas.create_text(cx, cy - r - 15, text="Im(z/Z0)", anchor="s")
            canvas.create_text(cx, cy + r + 15, text="-Im(z/Z0)", anchor="n")
        else:
            canvas.create_text(cx + r + 15, cy, text="Re(y/Y0)", anchor="w")
            canvas.create_text(cx - r - 15, cy, text="-Re(y/Y0)", anchor="e")
            canvas.create_text(cx, cy - r - 15, text="Im(y/Y0)", anchor="s")
            canvas.create_text(cx, cy + r + 15, text="-Im(y/Y0)", anchor="n")
        for val in [0.2, 0.5, 1, 2, 5]:
            cr = r / (1 + val)
            off = r * val / (1 + val)
            canvas.create_oval(cx + off - cr, cy - cr, cx + off + cr, cy + cr, outline="lightgray")
            canvas.create_text(cx + off + cr + 15, cy, text=f"r={val}", anchor="w", fill="gray")
        for val in [0.2, 0.5, 1, 2, 5]:
            cr = r / val
            canvas.create_arc(cx - cr, cy - cr, cx + cr, cy + cr, start=90, extent=180, style='arc', outline="lightgray")
            canvas.create_arc(cx - cr, cy - cr, cx + cr, cy + cr, start=-90, extent=180, style='arc', outline="lightgray")
            canvas.create_text(cx, cy - cr - 10, text=f"+jx={val}", fill="gray")
            canvas.create_text(cx, cy + cr + 10, text=f"-jx={val}", fill="gray")
        return center, radius

    def draw_chart(self):
        self.center, self.radius = self.draw_one_chart(self.canvas, "impedance")
        self.center_y, self.radius_y = self.draw_one_chart(self.adm_canvas, "admittance")
        self.point = self.canvas.create_oval(self.center[0], self.center[1], self.center[0], self.center[1], fill="red")
        self.adm_point = self.adm_canvas.create_oval(self.center_y[0], self.center_y[1], self.center_y[0], self.center_y[1], fill="red")

    def add_inductor(self):
        dlg = ComponentDialog(self, "L", index=len(self.components))
        self.wait_window(dlg)
        if dlg.res:
            comp = {"type": "L", **dlg.res}
            self.components.append(comp)
            self.comp_listbox.insert(tk.END, f"L {comp['orient']} = {comp['disp']}")
            self.update_point()
            self.draw_circuit()

    def add_resistor(self):
        dlg = ComponentDialog(self, "R", index=len(self.components))
        self.wait_window(dlg)
        if dlg.res:
            comp = {"type": "R", **dlg.res}
            self.components.append(comp)
            self.comp_listbox.insert(tk.END, f"R {comp['orient']} = {comp['disp']}")
            self.update_point()
            self.draw_circuit()

    def add_capacitor(self):
        dlg = ComponentDialog(self, "C", index=len(self.components))
        self.wait_window(dlg)
        if dlg.res:
            comp = {"type": "C", **dlg.res}
            self.components.append(comp)
            self.comp_listbox.insert(tk.END, f"C {comp['orient']} = {comp['disp']}")
            self.update_point()
            self.draw_circuit()

    def add_tline(self):
        dlg = ComponentDialog(self, "TL", index=len(self.components))
        self.wait_window(dlg)
        if dlg.res:
            comp = {"type": "TL", **dlg.res}
            self.components.append(comp)
            self.comp_listbox.insert(tk.END, f"TL {comp['disp']} Z0={comp['z0']}")
            self.update_point()
            self.draw_circuit()

    def add_stub(self):
        dlg = ComponentDialog(self, "STUB", index=len(self.components))
        self.wait_window(dlg)
        if dlg.res:
            comp = {"type": "STUB", **dlg.res}
            self.components.append(comp)
            self.comp_listbox.insert(tk.END, f"Stub {comp['kind']} {comp['disp']} Z0={comp['z0']}")
            self.update_point()
            self.draw_circuit()

    def remove_last(self):
        if self.components:
            self.components.pop()
            self.comp_listbox.delete(tk.END)
            self.update_point()
            self.draw_circuit()

    def apply_settings(self):
        try:
            self.freq = float(self.freq_entry.get()) * 1e6
            self.z0 = float(self.z0_entry.get())
            self.za = parse_complex_impedance(self.za_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Invalid frequency, Z0 or Z_A")
            return
        self.draw_chart()
        self.update_point()
        self.draw_circuit()

    def edit_component(self, event):
        sel = self.comp_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        comp = self.components[idx]
        dlg = ComponentDialog(self, comp["type"], comp, index=idx)
        self.wait_window(dlg)
        if dlg.res:
            for k, v in dlg.res.items():
                comp[k] = v
            # update listbox text
            if comp["type"] in ("L", "C", "R"):
                text = f"{comp['type']} {comp['orient']} = {comp['disp']}"
            elif comp["type"] == "TL":
                text = f"TL {comp['disp']} Z0={comp['z0']}"
            else:
                text = f"Stub {comp['kind']} {comp['disp']} Z0={comp['z0']}"
            self.comp_listbox.delete(idx)
            self.comp_listbox.insert(idx, text)
            self.update_point()
            self.draw_circuit()

    def preview_update(self, temp_comp, index):
        comps = self.components[:]
        if index is None or index >= len(comps):
            comps.append(temp_comp)
        else:
            comps[index] = temp_comp
        self.update_point(comps)

    def compute_trace(self, Z_start, comp, steps=TRACE_STEPS):
        """Return a list of impedances along the path for component."""
        res = []
        w = PI2 * self.freq
        typ = comp.get("type")
        for i in range(1, steps + 1):
            t = i / steps
            if typ == "L":
                L = comp["value"]
                if comp.get("orient") == "series":
                    Z = Z_start + 1j * w * L * t
                else:
                    Y = 1 / Z_start + (-1j / (w * L)) * t
                    Z = 1 / Y
            elif typ == "C":
                C = comp["value"]
                if comp.get("orient") == "series":
                    Z = Z_start + (-1j / (w * C)) * t
                else:
                    Y = 1 / Z_start + 1j * w * C * t
                    Z = 1 / Y
            elif typ == "R":
                R = comp["value"]
                if comp.get("orient") == "series":
                    Z = Z_start + R * t
                else:
                    Y = 1 / Z_start + (1 / R) * t
                    Z = 1 / Y
            elif typ == "TL":
                beta_l = math.radians(comp["length"]) * t
                Z0 = comp.get("z0", self.z0)
                Z = Z0 * (Z_start + 1j * Z0 * math.tan(beta_l)) / (
                    Z0 + 1j * Z_start * math.tan(beta_l)
                )
            elif typ == "STUB":
                beta_l = math.radians(comp["length"]) * t
                Z0 = comp.get("z0", self.z0)
                if comp["kind"] == "short":
                    Zin = 1j * Z0 * math.tan(beta_l)
                else:
                    Zin = -1j * Z0 / math.tan(beta_l)
                Y = 1 / Z_start + 1 / Zin
                Z = 1 / Y
            else:
                Z = Z_start
            res.append(Z)
        return res

    def update_point(self, components=None):
        comps = components if components is not None else self.components
        Z = self.za
        pts_z = []
        pts_y = []
        cx, cy = self.center
        cyx, cyy = self.center_y
        r = self.radius
        ry = self.radius_y
        gamma = (Z - self.z0) / (Z + self.z0)
        pts_z.append((cx + gamma.real * r, cy - gamma.imag * r))
        Y = 1 / Z if Z != 0 else complex('inf')
        gamma_y = (Y - 1/self.z0) / (Y + 1/self.z0) if Y != complex('inf') else complex(1)
        pts_y.append((cyx + gamma_y.real * ry, cyy - gamma_y.imag * ry))
        for comp in comps:
            trace = self.compute_trace(Z, comp)
            for Zt in trace:
                gamma = (Zt - self.z0) / (Zt + self.z0)
                pts_z.append((cx + gamma.real * r, cy - gamma.imag * r))
                Yt = 1 / Zt if Zt != 0 else complex('inf')
                gamma_y = (Yt - 1/self.z0) / (Yt + 1/self.z0) if Yt != complex('inf') else complex(1)
                pts_y.append((cyx + gamma_y.real * ry, cyy - gamma_y.imag * ry))
            Z = trace[-1]

        self.canvas.delete("trace")
        self.adm_canvas.delete("trace")
        for i in range(len(pts_z)-1):
            self.canvas.create_line(*pts_z[i], *pts_z[i+1], fill="blue", tags="trace", smooth=True)
        for i in range(len(pts_y)-1):
            self.adm_canvas.create_line(*pts_y[i], *pts_y[i+1], fill="blue", tags="trace", smooth=True)

        x, y = pts_z[-1]
        self.canvas.coords(self.point, x-5, y-5, x+5, y+5)
        x, y = pts_y[-1]
        self.adm_canvas.coords(self.adm_point, x-5, y-5, x+5, y+5)

    def draw_circuit(self):
        c = self.circ_canvas
        c.delete("all")
        w = c.winfo_reqwidth()
        y = 60
        src_x = 15
        load_x = w - 15
        c.create_line(src_x, y, load_x, y)
        c.create_oval(src_x-5, y-5, src_x+5, y+5)
        c.create_text(src_x, y+15, text="Src")
        c.create_rectangle(load_x-10, y-10, load_x+10, y+10)
        c.create_text(load_x, y+20, text=f"Z_A\n{self.za_entry.get()}")
        # draw components starting at the load and moving toward the source
        x = load_x - 20
        for comp in self.components:
            if comp["type"] in ("L", "C", "R", "TL") and comp.get("orient") == "shunt":
                # draw shunt element below the line
                c.create_line(x, y, x, y+20)
                c.create_rectangle(x-10, y+20, x+10, y+40)
                label = comp["type"] + "\n" + comp.get("disp", "")
                if comp["type"] == "TL":
                    label = f"TL\n{comp['disp']}\nZ0={comp.get('z0', self.z0)}"
                c.create_text(x, y+30, text=label)
            else:
                # series element
                c.create_rectangle(x-40, y-10, x, y+10)
                if comp["type"] == "TL":
                    txt = f"TL\n{comp['disp']}\nZ0={comp.get('z0', self.z0)}"
                elif comp["type"] == "STUB":
                    c.create_line(x-20, y, x-20, y+20)
                    c.create_rectangle(x-30, y+20, x-10, y+40)
                    txt = f"Stub {comp['kind']}\n{comp['disp']}\nZ0={comp.get('z0', self.z0)}"
                    c.create_text(x-20, y+30, text=txt)
                    x -= 40
                    continue
                else:
                    txt = f"{comp['type']}\n{comp.get('disp','')}"
                c.create_text(x-20, y, text=txt)
                x -= 40
        c.create_line(src_x+10, y, x, y)

if __name__ == "__main__":
    app = SmithChartApp()
    app.mainloop()
