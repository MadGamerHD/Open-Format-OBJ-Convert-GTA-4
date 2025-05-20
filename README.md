 polish

---

# OpenFormatConverter

**OpenFormatConverter** is a Python tool designed to convert proprietary `.odr` 3D model files (used in GTA IV for maps and weapons) into the widely supported `.obj` format, including `.mtl` material files. This makes it easy to import these models into any standard 3D modeling software.

---

## Features

* **ODR to OBJ/MTL Conversion**
  Convert `.odr` files into `.obj` geometry files and accompanying `.mtl` material files seamlessly.

* **Detailed Geometry Parsing**
  Extracts vertices, normals, UV coordinates, and faces, reconstructing models accurately.

* **Material Handling**
  Parses shaders and textures to generate correct material files, preserving texture mapping.

* **LOD & Skeleton Support**
  Handles Level of Detail groups and skeleton data for complex models.

* **User-Friendly GUI**
  Includes a simple Tkinter-based interface for easy file selection and conversion progress monitoring.

---

## Getting Started

1. **Installation**
   Make sure Python is installed. Clone this repo and install dependencies if necessary.

2. **Usage**
   Run the GUI with:

   ```bash
   python OpenFormatObjConverterGUI.pyw
   ```

   Select your `.odr` file through the GUI and start conversion. Output `.obj` and `.mtl` files will be saved alongside the original file.

3. **Customization**
   The codebase is modular, allowing easy modification or extension for other `.odr` variants or additional features.

---

### Notes

* Currently supports map and weapon models only. Vehicle models are not yet supported.
* No external DLL dependencies are required, keeping the tool lightweight and portable.
