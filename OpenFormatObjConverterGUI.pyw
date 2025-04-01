import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk

# -------------------------------
# Conversion Classes and Functions
# -------------------------------

class Vertex:
    def __init__(self, index, coordinates, normal, uv) -> None:
        self.index = index
        self.coordinates = coordinates
        self.normal = normal
        self.uv = uv
    
    def get_v(self):
        return "v " + " ".join(str(coord) for coord in self.coordinates)
    
    def get_vn(self):
        return "vn " + " ".join(str(norm) for norm in self.normal)
    
    def get_vt(self):
        return "vt " + " ".join(str(uv_coord) for uv_coord in self.uv)
    
    def get_index(self):
        return self.index

class Face:
    def __init__(self, vertices) -> None:
        self.vertices = vertices

    def get_f(self):
        # OBJ indices are 1-based so add 1 to each vertex index.
        return "f " + " ".join(
            f"{vert.get_index() + 1}/{vert.get_index() + 1}/{vert.get_index() + 1}" for vert in self.vertices
        )

class Mesh:
    def __init__(self, index) -> None:
        self.index = index
        self.vertex_offset = 0
        self.idx_data = []
        self.vert_data = []
        self.vertices = []
        self.faces = []
        self.material = None
    
    def set_vertex_offset(self, vertex_offset) -> None:
        self.vertex_offset = vertex_offset
    
    def add_idx(self, data) -> None:
        for id_str in data:
            if id_str.strip():
                try:
                    self.idx_data.append(int(id_str))
                except ValueError:
                    # Log or pass if conversion fails.
                    pass
    
    def add_vert(self, data) -> None:
        self.vert_data.append(data)
    
    def generate(self) -> None:
        vert_index = self.vertex_offset
        for raw_vert in self.vert_data:
            parts = raw_vert.split(" / ")
            coord = [float(c) for c in parts[0].split(" ")]
            normal = [float(n) for n in parts[1].split(" ")]
            uv = parts[3].split(" ")
            if len(uv) != 2:
                uv = parts[4].split(" ")
            # Flip the V coordinate
            uv = [float(uv[0]), -float(uv[1])]
            vertex = Vertex(vert_index, coord, normal, uv)
            self.vertices.append(vertex)
            vert_index += 1

        for i in range(0, len(self.idx_data), 3):
            try:
                v1 = self.vertices[self.idx_data[i]]
                v2 = self.vertices[self.idx_data[i + 1]]
                v3 = self.vertices[self.idx_data[i + 2]]
                face = Face([v1, v2, v3])
                self.faces.append(face)
            except IndexError:
                # Handle potential index errors gracefully.
                continue

class Material:
    def __init__(self, name) -> None:
        self.name = name
        self.Ka = [0, 0, 0]
        self.Kd = [0, 0, 0]
        self.Ks = [0, 0, 0]
        self.Ns = 0
        self.Ni = 0
        self.d = 0
        self.illum = 0
        self.map_Kd = ""
        self.map_bump = ""
        self.map_Ks = ""
    
    def generate(self):
        if not self.name:
            return ""
        mtl = "newmtl " + self.name + "\n"
        if self.map_Kd:
            mtl += "map_Kd " + self.map_Kd + "\n"
        if self.map_bump:
            mtl += "map_bump " + self.map_bump + "\n"
        if self.map_Ks:
            mtl += "map_Ks " + self.map_Ks + "\n"
        mtl += "\n"
        return mtl

class MaterialParser:
    def __init__(self, raw_shader_list) -> None:
        self.shaders = raw_shader_list
    
    def generate(self):
        materials = []
        for index, shader in enumerate(self.shaders):
            material = Material("MAT_" + str(index))
            material.map_Kd = shader  # Adjust if needed.
            materials.append(material)
        return materials

class MeshParser:
    def __init__(self, mesh_file_path, materials) -> None:
        self.materials = materials
        with open(mesh_file_path) as f:
            self.mesh_file_lines = f.read()
        self.meshes = []
    
    def generate(self, debug=False):
        self.mesh_file_lines = re.sub(r"\t", "", self.mesh_file_lines)
        depth = 0
        mesh = None
        in_idx = -1
        in_verts = -1
        mesh_index = -1
        for line in self.mesh_file_lines.splitlines():
            if "{" in line:
                depth += 1
            if "}" in line:
                depth -= 1
            if "mtl" in line.lower() or "geometry" in line.lower():
                if mesh is not None:
                    self.meshes.append(mesh)
                mesh_index += 1
                mesh = Mesh(mesh_index)
                try:
                    mesh.material = self.materials[mesh_index]
                except IndexError:
                    pass
            if "idx" in line.lower() or "indices" in line.lower():
                in_idx = depth + 1
                continue
            if "verts" in line.lower() or "vertices" in line.lower():
                in_verts = depth + 1
                continue
            if in_idx > 0:
                if depth < in_idx:
                    in_idx = -1
                if "{" not in line and "}" not in line:
                    mesh.add_idx(line.split(" "))
            if in_verts > 0:
                if depth < in_verts:
                    in_verts = -1
                if "{" not in line and "}" not in line:
                    mesh.add_vert(line)
        if mesh is not None:
            self.meshes.append(mesh)
        # Set vertex offsets for each mesh
        for i in range(len(self.meshes)):
            if i == 0:
                self.meshes[i].set_vertex_offset(0)
            else:
                offset = sum(len(self.meshes[j].vert_data) for j in range(i))
                self.meshes[i].set_vertex_offset(offset)
        for mesh in self.meshes:
            mesh.generate()

        # Build the OBJ file text
        obj = ""
        for mesh in self.meshes:
            for vert in mesh.vertices:
                obj += vert.get_v() + "\n"
        for mesh in self.meshes:
            for vert in mesh.vertices:
                obj += vert.get_vn() + "\n"
        for mesh in self.meshes:
            for vert in mesh.vertices:
                obj += vert.get_vt() + "\n"
        for mesh in self.meshes:
            if mesh.material is not None:
                obj += "usemtl " + mesh.material.name + "\n"
            for face in mesh.faces:
                obj += face.get_f() + "\n"

        vert_count = sum(len(mesh.vertices) for mesh in self.meshes)
        face_count = sum(len(mesh.faces) for mesh in self.meshes)
        material_count = sum(1 for mesh in self.meshes if mesh.material is not None)
        if debug:
            print("--------------------")
            print(f"Mesh count: {len(self.meshes)}")
            print(f"Vertex count: {vert_count}")
            print(f"Face count: {face_count}")
            print(f"Material count: {material_count}")
            print("--------------------")
        mtl = ""
        for material in self.materials:
            mtl += material.generate()
        return {"obj": obj, "mtl": mtl}

def parse_odr(lines):
    """
    Parses the contents of an ODR file and returns a dictionary with shaders, skeletons, and lodgroup data.
    """
    odr_data = {"shaders": [], "skeletons": [], "lodgroup": {}}
    shadinggroups = []
    regex_shadinggroup = r"(s|S)hadinggroup(\n|\s|){\n\t{0,1}(s|S)haders \d{1,999}\n\t{0,1}{\n\t{2}[^}]+}\n}"
    match_shadinggroup = re.search(regex_shadinggroup, lines)
    if match_shadinggroup:
        tmp_shadinggroups = match_shadinggroup[0]
        tmp_shadinggroups = re.sub(r"(s|S)hadinggroup(\n|\s|){\n\t{0,1}(s|S)haders \d{1,999}\n\t{0,1}{\n", "", tmp_shadinggroups)
        tmp_shadinggroups = re.sub(r"\n\t{0,2}}\n}", "", tmp_shadinggroups)
        tmp_shadinggroups = re.sub(r"\t", "", tmp_shadinggroups)
        tmp_shadinggroups = re.sub(r"\\", "/", tmp_shadinggroups)
        if tmp_shadinggroups:
            for shadinggroup in tmp_shadinggroups.splitlines():
                try:
                    shadinggroups.append(shadinggroup.split(" ")[1])
                except IndexError:
                    pass
    if not shadinggroups:
        sps_data = []
        depth = 0
        sps_name = ""
        in_shaders = -1
        previous_line = ""
        for line in lines.splitlines():
            if "{" in line:
                depth += 1
            if "}" in line:
                depth -= 1
            if "shaders" in line.lower():
                in_shaders = depth + 1
                continue
            if depth < in_shaders:
                in_shaders = -1
            if in_shaders != -1:
                if "{" in line and "{" not in previous_line:
                    sps_name = previous_line.strip()
                if "}" in line and sps_name:
                    sps_name = ""
                if sps_name and "{" not in line:
                    if "DiffuseSampler" in line:
                        sps_data.append(
                            re.sub(r"\\", "/", re.sub(line.split(" ")[0], "", line).lstrip()).replace(".otx", ".png")
                        )
            previous_line = line
        shadinggroups = sps_data
    odr_data["shaders"] = shadinggroups

    regex_skeletons = r"(s|S)kel(eton|)((\n|\s|){\n\t{0,1}[\w\.\s\t\\\-]+\n}|[ \w\\\.\d\-]+)"
    match_skeletons = re.search(regex_skeletons, lines)
    skeletons = ""
    if match_skeletons:
        skeletons = match_skeletons[0]
        skeletons = re.sub(r"(s|S)kel(eton|)(\n|\s|) *", "", skeletons)
        skeletons = re.sub(r"\n}", "", skeletons)
        skeletons = re.sub(r"\t", "", skeletons)
        skeletons = re.sub(r"\\", "/", skeletons)
    new_skeletons = [skel for skel in skeletons.splitlines() if skel.lower().endswith(".skel")]
    odr_data["skeletons"] = new_skeletons

    depth = 0
    in_lodgroup = -1
    lodgroup_lines = []
    for line in lines.splitlines():
        if "{" in line:
            depth += 1
        if "}" in line:
            depth -= 1
        if "lodgroup" in line.lower():
            in_lodgroup = depth + 1
            continue
        if in_lodgroup != -1:
            if depth < in_lodgroup:
                in_lodgroup = -1
            lodgroup_lines.append(line)
    lodgroup_lines = "\n".join(lodgroup_lines)
    regex_lod = r"(((h|H)igh)|((m|M)ed)|((l|L)ow)|((v|V)low)) [\d\.\w \\\-]+(\n\t+{\n\t+[\w\\\. \d]+\n\t+})*"
    match_lod = re.finditer(regex_lod, lodgroup_lines)
    if match_lod:
        for o in [x.group() for x in match_lod]:
            lod_type = o.split(" ")[0].lower()
            lod_value = ""
            if "{" in o:
                for t in o.split("\t"):
                    for tt in t.split(" "):
                        if tt.lower().endswith(".mesh"):
                            lod_value = re.sub(r"\\", "/", tt)
                            break
            else:
                for t in o.split(" "):
                    if t.lower().endswith(".mesh"):
                        lod_value = re.sub(r"\\", "/", t)
                        break
            if lod_value:
                odr_data["lodgroup"][lod_type] = lod_value
    return odr_data

def convert_file(input_file_path, log_func, settings):
    """
    Converts the given .odr file into OBJ and MTL files.
    The 'settings' dictionary can include custom options such as output_directory.
    """
    if not input_file_path.lower().endswith(".odr"):
        log_func("Error: Input file must have a .odr extension")
        return

    try:
        with open(input_file_path, "r") as f:
            raw_odr_lines = f.read()
    except Exception as e:
        log_func("Error reading file: " + str(e))
        return
    
    odr_data = parse_odr(raw_odr_lines)
    # Use the selected output directory from settings, if provided.
    output_dir = settings.get("output_directory", os.path.dirname(input_file_path))
    os.chdir(output_dir)
    input_name, _ = os.path.splitext(os.path.basename(input_file_path))
    output_files = []
    
    for lodgroup in odr_data["lodgroup"]:
        output_obj_name = input_name + "_" + lodgroup + ".obj"
        output_mtl_name = input_name + "_" + lodgroup + ".mtl"
        material_parser = MaterialParser(odr_data["shaders"])
        mesh_file_path = odr_data["lodgroup"][lodgroup]
        # In case the mesh file path is relative, make it relative to the input file.
        if not os.path.isabs(mesh_file_path):
            mesh_file_path = os.path.join(os.path.dirname(input_file_path), mesh_file_path)
        mesh_parser = MeshParser(mesh_file_path, material_parser.generate())
        model_data = mesh_parser.generate(True)
        obj_headers = "# Converted by OpenFormatConverter\n\n"
        obj_headers += f"mtllib {output_mtl_name}\n\n"
        mtl_headers = "# Converted by OpenFormatConverter\n\n"
        model_data["obj"] = obj_headers + model_data["obj"]
        model_data["mtl"] = mtl_headers + model_data["mtl"]
        try:
            with open(output_obj_name, "w") as f:
                f.write(model_data["obj"])
            with open(output_mtl_name, "w") as f:
                f.write(model_data["mtl"])
            output_files.append((output_obj_name, output_mtl_name))
            log_func(f"Created: {output_obj_name} and {output_mtl_name}")
        except Exception as e:
            log_func("Error writing output files: " + str(e))
    
    log_func("Conversion completed successfully!")

# -------------------------------
# Tkinter UI Code with Settings and Progress Bar
# -------------------------------

# Global settings dictionary
global_settings = {
    "output_directory": "",  # Leave empty to use same directory as input file
    "vertex_precision": 2      # Not yet applied in conversion, reserved for future use
}

class SettingsPanel(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("400x250")
        self.create_widgets()
    
    def create_widgets(self):
        # Output Directory Option
        tk.Label(self, text="Output Directory:").pack(pady=5)
        self.out_dir_entry = tk.Entry(self, width=40)
        self.out_dir_entry.pack(pady=5)
        tk.Button(self, text="Browse", command=self.select_directory).pack(pady=5)
        
        # Vertex Precision Option (reserved for future use)
        tk.Label(self, text="Vertex Precision:").pack(pady=5)
        self.precision_var = tk.IntVar(value=global_settings.get("vertex_precision", 2))
        tk.Spinbox(self, from_=1, to=10, textvariable=self.precision_var).pack(pady=5)
        
        # Save Button
        tk.Button(self, text="Save", command=self.save_settings).pack(pady=20)
    
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.out_dir_entry.delete(0, tk.END)
            self.out_dir_entry.insert(0, directory)
    
    def save_settings(self):
        global global_settings
        global_settings["output_directory"] = self.out_dir_entry.get().strip()
        global_settings["vertex_precision"] = self.precision_var.get()
        print("Settings saved:", global_settings)
        self.destroy()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OpenFormatConverter UI")
        self.geometry("700x500")
        self.create_widgets()
    
    def create_widgets(self):
        # Top Frame for File Selection and Settings
        top_frame = tk.Frame(self)
        top_frame.pack(pady=10)
        
        self.file_label = tk.Label(top_frame, text="No file selected", width=50)
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        self.select_button = tk.Button(top_frame, text="Select ODR File", command=self.select_file)
        self.select_button.pack(side=tk.LEFT, padx=5)
        
        self.settings_button = tk.Button(top_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side=tk.LEFT, padx=5)
        
        self.convert_button = tk.Button(top_frame, text="Convert", command=self.start_conversion, state=tk.DISABLED)
        self.convert_button.pack(side=tk.LEFT, padx=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self, orient=tk.HORIZONTAL, mode='indeterminate', length=400)
        self.progress.pack(pady=10)
        
        # Log Box
        self.log_box = scrolledtext.ScrolledText(self, width=80, height=20)
        self.log_box.pack(pady=10)
    
    def log(self, message):
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)
    
    def select_file(self):
        file_path = filedialog.askopenfilename(title="Select ODR File", filetypes=[("ODR Files", "*.odr")])
        if file_path:
            self.file_path = file_path
            self.file_label.config(text=file_path)
            self.convert_button.config(state=tk.NORMAL)
    
    def open_settings(self):
        SettingsPanel(self)
    
    def start_conversion(self):
        if hasattr(self, 'file_path'):
            self.log("Starting conversion for: " + self.file_path)
            self.convert_button.config(state=tk.DISABLED)
            self.progress.start(10)
            # Start conversion in a separate thread
            threading.Thread(target=self.run_conversion, daemon=True).start()
        else:
            messagebox.showerror("Error", "No file selected")
    
    def run_conversion(self):
        try:
            convert_file(self.file_path, self.log, global_settings)
        except Exception as e:
            self.log("An unexpected error occurred: " + str(e))
        finally:
            self.progress.stop()
            self.convert_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = App()
    app.mainloop()
