import os
import subprocess

def main():
    print("=== Creador de Proyectos Astro ===")
    project_name = input("Ingresa el nombre de la carpeta del proyecto: ").strip()
    
    if not project_name:
        print("El nombre no puede estar vacío.")
        return
        
    preferred_dir = r"E:\Programacion\Github" # Hola random de internet, esta ruta me funciona a mi, sientete libre de cambiarla
                                              # A una ruta existente en tu dispositivo, saludos :D
    if os.path.exists(preferred_dir):
        default_dir = preferred_dir
    else:
        default_dir = os.getcwd()
        
    print(f"\nDirectorio base por defecto: {default_dir}")
    print("Opciones:")
    print(" - Presiona [Enter] para usar el directorio por defecto.")
    print(" - Escribe 'b' para buscar una carpeta usando el explorador de archivos.")
    print(" - O simplemente escribe una ruta manualmente.")
    base_dir_input = input("Tu elección: ").strip()
    
    if base_dir_input.lower() == 'b':
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True) # Hace que la ventana aparezca al frente
        selected_dir = filedialog.askdirectory(title="Selecciona la carpeta base para el proyecto")
        root.destroy()
        
        if not selected_dir:
            print("Operación cancelada. Usando el directorio por defecto.")
            base_dir = default_dir
        else:
            base_dir = selected_dir
    else:
        base_dir = base_dir_input if base_dir_input else default_dir
    
    if not os.path.exists(base_dir):
        print(f"Error: La ruta base '{base_dir}' no existe.")
        return
        
    project_path = os.path.join(base_dir, project_name)
    
    if os.path.exists(project_path):
        print(f"Error: La carpeta '{project_path}' ya existe. Por favor, elige otro nombre.")
        return

    print(f"\nCreando proyecto en: {project_path}")
    print("Configuraciones: Template Minimal, Instalando dependencias, Sin repositorio git...")
    
    # Comando para crear el proyecto Astro
    create_cmd = [
        "pnpm", "create", "astro", project_path,
        "--template", "minimal",
        "--install",
        "--no-git",
        "--yes"
    ]
    
    try:
        # shell=True es útil en Windows para que reconozca comandos de pnpm
        subprocess.run(create_cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"\nError al ejecutar la creación del proyecto: {e}")
        return
        
    print("\n¡Proyecto base creado exitosamente!")
    
    # Preguntar por integraciones adicionales
    print("\n--- Frameworks de UI ---")
    print("1. React")
    print("2. Preact")
    print("3. Svelte")
    print("4. Vue")
    print("5. SolidJS")
    print("6. Ninguno")
    print("¡Puedes elegir varios separándolos por comas! (Ej: 1,3,4)")
    ui_choice = input("¿Deseas instalar frameworks de UI?: ").strip()
    
    print("\n--- Herramientas Extra ---")
    tailwind_choice = input("¿Deseas instalar Tailwind CSS? (s/n): ").strip().lower()
    mdx_choice = input("¿Deseas instalar MDX (para usar componentes en Markdown)? (s/n): ").strip().lower()
    sitemap_choice = input("¿Deseas instalar Sitemap (para generación automática de sitemap.xml)? (s/n): ").strip().lower()
    
    integrations = []
    
    ui_map = {"1": "react", "2": "preact", "3": "svelte", "4": "vue", "5": "solid"}
    
    # Procesar múltiples elecciones separadas por coma
    choices = [c.strip() for c in ui_choice.split(',')]
    for choice in choices:
        if choice in ui_map and ui_map[choice] not in integrations:
            integrations.append(ui_map[choice])
        
    if tailwind_choice == "s":
        integrations.append("tailwind")
    if mdx_choice == "s":
        integrations.append("mdx")
    if sitemap_choice == "s":
        integrations.append("sitemap")
        
    if integrations:
        print(f"\nInstalando integraciones ({', '.join(integrations)})...")
        # Comando para añadir integraciones automáticamente
        add_cmd = ["pnpm", "astro", "add"] + integrations + ["--yes"]
        try:
            subprocess.run(add_cmd, cwd=project_path, check=True, shell=True)
            print("Integraciones instaladas correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"\nError al instalar las integraciones: {e}")
            
    # Crear estructura de carpetas en src
    print("\nConfigurando estructura de carpetas en src...")
    src_path = os.path.join(project_path, "src")
    
    # Asegurarnos de que src exista, aunque la plantilla minimal debería crearla
    os.makedirs(src_path, exist_ok=True)
    
    folders_to_create = ["assets", "pages", "styles"]
    
    for folder in folders_to_create:
        folder_path = os.path.join(src_path, folder)
        os.makedirs(folder_path, exist_ok=True)
        print(f" - Creada carpeta: src/{folder}")
        
    print(f"\n=== ¡Todo listo! ===")
    print(f"Tu proyecto de Astro te espera en: {project_path}")

if __name__ == "__main__":
    main()
