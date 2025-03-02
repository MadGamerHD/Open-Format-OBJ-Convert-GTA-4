# OpenFormatConverter

**OpenFormatConverter** is a Python-based tool designed to convert 3D model files from the proprietary `.odr` format to the widely supported `.obj` format, complete with corresponding material files (`.mtl`). It parses model data—including vertices, normals, UV coordinates, faces, and materials—and reconstructs them into a clean, standardized OBJ file.

## Features

- **ODR to OBJ/MTL Conversion:**  
  Seamlessly converts `.odr` files into a pair of `.obj` and `.mtl` files that can be imported into most 3D modeling software.

- **Detailed Geometry Parsing:**  
  Extracts vertex, normal, and texture coordinate data, and constructs faces with correct indexing to maintain model integrity.

- **Material Handling:**  
  Automatically processes shader and texture information to generate material files, ensuring that textures are correctly mapped.

- **LOD & Skeleton Parsing:**  
  Supports parsing for Level of Detail (LOD) groups and skeletons, making it a robust option for complex models.

- **User-Friendly Tkinter Interface:**  
  A built-in graphical user interface (GUI) allows users to easily select `.odr` files and monitor conversion progress, making it accessible even for those new to command-line tools.

## Getting Started

1. **Installation:**  
   Ensure you have Python installed. Clone the repository and install any dependencies if needed.

2. **Usage:**  
   Run the tool using:
   ```bash
   OpenFormatObjConverterGUI.pyw
   ```
   Use the GUI to select an `.odr` file and initiate conversion. The converted `.obj` and `.mtl` files will be saved in the same directory as the original file.

3. **Customization:**  
   The source code is modular, making it easy to adjust parsing logic for different variants of the `.odr` format or extend functionality.
