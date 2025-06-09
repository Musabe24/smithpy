Interactive Smith-Chart written in Python.

This repository contains a basic GUI application using `tkinter`.
Run the app with:

```bash
python3 smith_gui.py
```

The GUI shows two Smith Charts on the left: the upper one displays the
impedance plane while the lower one shows the corresponding admittance
plane. On the right is a list of components with a small circuit sketch.
Inductors, capacitors and now also
resistors can be added either in series or parallel by entering values
like `10 nH`, `50 uF` or `75`. Transmission lines and stubs ask for
their characteristic impedance so that different `Z0` values can be used. Lengths can be entered either in degrees or as the fraction `l/\u03bb`. The entry may include a trailing `\u00b0` or `\u03bb`, e.g. `90\u00b0` or `0.25 \u03bb`. The chart updates automatically.
The circuit sketch shows the source on the left and the load `Z_A` on the right.
Components are drawn starting at the load so their order matches the impedance calculations.
`Z_A` accepts complex values such as `75+30j` so arbitrary
loads can be matched. The frequency entry expects MHz and the chart
normalization `Z0` can be set in the upper-right panel. Components are
added through a single dialog window and may be edited later by
double-clicking their entry in the list. Value sliders inside these
dialogs let you change component parameters while the resulting
impedance path is previewed live on the Smith Chart. Each dialog offers
fields to set the slider's minimum and maximum values so you can adjust
the range to your needs. Slider resolution adapts automatically to the
selected range so even small values can be tuned precisely. Constant resistance and reactance lines on the
chart are labeled for easier reference.
Impedance transformations are drawn as smooth arcs that follow the
actual trajectory on the chart rather than straight lines. The
calculation now uses many intermediate steps so even long arcs remain
accurate.
