import os
import re

campus = ["zona core", "campus uno", "campus matriz", "sector outsourcing"]

def validar_ip(ip):
    patron = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
    if re.match(patron, ip):
        partes = ip.split(".")
        return all(0 <= int(parte) <= 255 for parte in partes)
    return False

def mostrar_campus():
    print("\nLista de campus:")
    for i, c in enumerate(campus, 1):
        print(f"{i}. {c}")
    print()

def ver_dispositivos():
    mostrar_campus()
    try:
        opcion = int(input("Seleccione un campus para ver sus dispositivos: ")) - 1
        nombre_archivo = campus[opcion] + ".txt"
        if os.path.exists(nombre_archivo):
            with open(nombre_archivo, "r") as f:
                print("\n--- Dispositivos Registrados ---\n")
                print(f.read())
        else:
            print("📭 No hay dispositivos registrados en este campus.")
    except (IndexError, ValueError):
        print("⚠️ Opción inválida.")

def agregar_campus():
    nuevo = input("Nombre del nuevo campus: ").strip().lower()
    if nuevo and nuevo not in campus:
        campus.append(nuevo)
        print(f"🏫 Campus '{nuevo}' agregado correctamente.")
    else:
        print("⚠️ Nombre inválido o campus ya existe.")

def agregar_dispositivo():
    mostrar_campus()
    try:
        opcion = int(input("Seleccione campus para agregar dispositivo: ")) - 1
        nombre_archivo = campus[opcion] + ".txt"
    except (IndexError, ValueError):
        print("⚠️ Selección inválida.")
        return

    print("\nTipos de dispositivo:\n1. Router\n2. Switch\n3. Switch multicapa")
    tipo = input("Seleccione el tipo de dispositivo: ")

    nombre = input("Nombre del dispositivo: ").strip()

    ip = input("Ingrese la dirección IP del dispositivo: ").strip()
    while not validar_ip(ip):
        print("❗ IP inválida. Intente nuevamente.")
        ip = input("Ingrese una IP válida: ").strip()

    print("\nSeleccione la capa jerárquica:\n1. Núcleo\n2. Distribución\n3. Acceso")
    capa = input("Seleccione una opción: ")

    servicios = []
    if tipo in ["2", "3"]:
        print("\nSeleccione servicios (escriba el número, termine con 0):")
        opciones = {
            "1": "Datos",
            "2": "VLAN",
            "3": "Trunking",
            "4": "Enrutamiento" if tipo == "3" else None
        }
        for k, v in opciones.items():
            if v:
                print(f"{k}. {v}")
        while True:
            s = input("Servicio: ")
            if s == "0":
                break
            if s in opciones and opciones[s]:
                servicios.append(opciones[s])
    elif tipo == "1":
        print("\nServicio disponible:\n1. Enrutamiento\n2. Salir")
        if input("Seleccione una opción: ") == "1":
            servicios.append("Enrutamiento")

    with open(nombre_archivo, "a") as f:
        f.write("\n---------------------------------\n")
        tipo_str = {
            "1": "Router",
            "2": "Switch",
            "3": "Switch Multicapa"
        }.get(tipo, "Desconocido")
        f.write(f"{tipo_str}: {nombre}\n")
        f.write(f"IP: {ip}\n")
        f.write("Jerarquía: " + {
            "1": "Núcleo",
            "2": "Distribución",
            "3": "Acceso"
        }.get(capa, "No definida") + "\n")
        f.write("Servicios: " + ", ".join(servicios) + "\n")
        f.write("---------------------------------\n")
    print("✅ Dispositivo agregado correctamente.\n")

def menu():
    while True:
        print("\n🤖 ¿Qué desea hacer?")
        print("1. 📂 Ver los dispositivos")
        print("2. 🏫 Ver los campus")
        print("3. ➕ Añadir dispositivo")
        print("4. 🆕 Añadir campus")
        print("5. ❌ Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ver_dispositivos()
        elif opcion == "2":
            mostrar_campus()
        elif opcion == "3":
            agregar_dispositivo()
        elif opcion == "4":
            agregar_campus()
        elif opcion == "5":
            print("👋 Saliendo del programa.")
            break
        else:
            print("❌ Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    menu()