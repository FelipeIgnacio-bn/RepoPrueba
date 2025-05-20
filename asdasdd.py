import re
import os
from time import sleep
from datetime import datetime
import json # Para trabajar con archivos JSON
import ipaddress # Importado para validación de IP robusta

# 🌈 Paleta de colores y estilos
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

# --- Variables Globales ---
CARPETA_DATOS = "datos"
NOMBRE_ARCHIVO_JSON = "datos_dispositivos.json"
ARCHIVO_JSON = os.path.join(CARPETA_DATOS, NOMBRE_ARCHIVO_JSON)

USUARIOS_PERMITIDOS = {
    "Emanuel": "admin",
    "Felipe": "admin",
    "Nicolás": "admin"
}

# 🔧 Definición de constantes y validaciones
SERVICIOS_VALIDOS = {
    'DNS': '🔍 DNS',
    'DHCP': '🌐 DHCP',
    'WEB': '🕸️ Servicio Web',
    'BD': '🗃️ Base de Datos',
    'CORREO': '✉️ Servicio de Correo',
    'VPN': '🛡️ VPN'
}

TIPOS_DISPOSITIVO = {
    'PC': '💻 PC',
    'SERVIDOR':'🖧 Servidor',
    'ROUTER': '📶 Router',
    'SWITCH': '🔀 Switch',
    'FIREWALL': '🔥 Firewall',
    'IMPRESORA': '🖨️ Impresora'
}

CAPAS_RED = {
    'NUCLEO': '💎 Núcleo (Core)',
    'DISTRIBUCION': '📦 Distribución',
    'ACCESO': '🔌 Acceso',
    'TRANSPORTE': '🚢 Transporte',
    'APLICACION': '📱 Aplicación',
    'FISICA': '🔗 Física',
    'ENLACE_DATOS': '🔗 Enlace de Datos',
    'RED': '🌐 Red' # Añadida capa de Red genérica
}

VLAN_ID_MIN = 1
VLAN_ID_MAX = 4094


# 🎨 Diseño de la interfaz
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_titulo(titulo):
    limpiar_pantalla()
    print(f"{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{titulo.center(70)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}\n")

def mostrar_mensaje(mensaje, tipo="info"):
    icono = ""
    color = Color.BLUE
    if tipo == "error":
        icono = "❌ "
        color = Color.RED
    elif tipo == "exito":
        icono = "✅ "
        color = Color.GREEN
    elif tipo == "advertencia":
        icono = "⚠️ "
        color = Color.YELLOW
    elif tipo == "info":
        icono = "ℹ️ "
    print(f"{color}{Color.BOLD}{icono}{mensaje}{Color.END}\n")

def mostrar_progreso(mensaje="Cargando", duracion_total=1, pasos=20):
    """Muestra una barra de progreso animada."""
    limpiar_pantalla()
    print(f"\n{Color.CYAN}{mensaje}...{Color.END}")
    for i in range(pasos + 1):
        porcentaje = int((i / pasos) * 100)
        barra = '█' * i + ' ' * (pasos - i)
        print(f"\r{Color.GREEN}[{barra}] {porcentaje}%{Color.END}", end="")
        sleep(duracion_total / pasos)
    print("\n")
    sleep(0.5) # Pequeña pausa después de completar

# --- Gestión de Archivo JSON ---
def cargar_datos_json():
    """Carga los datos desde el archivo JSON. Si no existe la carpeta o el archivo, los crea."""
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    if not os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            return datos
    except (json.JSONDecodeError, FileNotFoundError):
        mostrar_mensaje(f"Error al cargar {ARCHIVO_JSON}. Se creará uno nuevo.", "advertencia")
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return []

def guardar_datos_json(dispositivos):
    """Guarda los datos en el archivo JSON."""
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump(dispositivos, f, ensure_ascii=False, indent=4)
    except IOError:
        mostrar_mensaje(f"Error: No se pudo guardar en {ARCHIVO_JSON}", "error")

# --- Funciones de Exportación ---
def exportar_a_txt(dispositivos):
    """Exporta la información de los dispositivos a un archivo TXT en la carpeta 'reportes'."""
    CARPETA_REPORTES = "reportes"
    NOMBRE_BASE_ARCHIVO_TXT = "reporte_dispositivos.txt"
    
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos para exportar.", "advertencia")
        sleep(2)
        return

    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    ruta_completa_archivo_txt = os.path.join(CARPETA_REPORTES, NOMBRE_BASE_ARCHIVO_TXT)

    mostrar_progreso(f"Exportando a {ruta_completa_archivo_txt}", 1.5)
    try:
        with open(ruta_completa_archivo_txt, 'w', encoding='utf-8') as f:
            f.write("=" * 70 + "\n")
            f.write("INFORME DE DISPOSITIVOS DE RED\n")
            f.write("=" * 70 + "\n")
            f.write(f"Fecha de Exportación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de Dispositivos: {len(dispositivos)}\n")
            f.write("-" * 70 + "\n\n")

            for i, disp_dict in enumerate(dispositivos, 1):
                f.write(f"Dispositivo #{i}\n")
                f.write("-" * 30 + "\n")
                for clave, valor in disp_dict.items():
                    valor_limpio = re.sub(r'\033\[[0-9;]*[mK]', '', str(valor))
                    if clave == "VLANS":
                        f.write(f"{clave.replace('_', ' ').capitalize()}:\n")
                        if isinstance(valor, list) and valor:
                            for vlan_info in valor:
                                f.write(f"  - ID: {vlan_info.get('id')}, Nombre: {vlan_info.get('nombre', 'N/A')}\n")
                        else:
                            f.write("  Ninguna\n")
                    else:
                        f.write(f"{clave.replace('_', ' ').capitalize()}: {valor_limpio}\n")
                f.write("\n" + "-" * 70 + "\n\n")

            f.write("FIN DEL INFORME\n")
            f.write("=" * 70 + "\n")
        mostrar_mensaje(f"Datos exportados exitosamente a '{ruta_completa_archivo_txt}'", "exito")
    except IOError:
        mostrar_mensaje(f"Error: No se pudo escribir en el archivo '{ruta_completa_archivo_txt}'", "error")
    input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")


# --- Validaciones Específicas ---
def validar_formato_ip(ip_str):
    ip_str = ip_str.strip()
    if not ip_str:
        raise ValueError("La dirección IP no puede estar vacía.")
    if ' ' in ip_str:
        raise ValueError("La dirección IP no debe contener espacios en blanco.")
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            octetos = ip_str.split('.')
            primer_octeto = int(octetos[0])
            if primer_octeto == 0: raise ValueError("IPv4: El primer octeto no puede ser 0.")
            if primer_octeto == 127: raise ValueError("IPv4: IPs 127.x.x.x reservadas para loopback.")
            if primer_octeto >= 224:
                if primer_octeto < 240: raise ValueError("IPv4: IPs 224.x.x.x a 239.x.x.x reservadas para multicast.")
                else: raise ValueError("IPv4: IPs >= 240.x.x.x reservadas para uso futuro.")
            if ip_str == "255.255.255.255": raise ValueError("IPv4: IP 255.255.255.255 reservada para broadcast.")
            return "IPv4"
        elif isinstance(ip_obj, ipaddress.IPv6Address):
            return "IPv6"
    except ValueError as e:
        raise ValueError(f"Formato de IP incorrecto: {e}")
    return None

def validar_mascara_red_ipv4(mascara_str):
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", mascara_str):
        raise ValueError("Formato incorrecto de máscara IPv4 (X.X.X.X).")
    octetos_int = [int(o) for o in mascara_str.split('.')]
    if any(not (0 <= octeto <= 255) for octeto in octetos_int):
        raise ValueError("Octetos de máscara IPv4 deben estar entre 0-255.")
    binario_completo = "".join([bin(o)[2:].zfill(8) for o in octetos_int])
    if '01' in binario_completo:
        raise ValueError("Máscara IPv4 inválida (bits '1' no contiguos).")
    if mascara_str == "0.0.0.0":
        raise ValueError("Máscara IPv4 0.0.0.0 no es válida para asignación.")
    return True

def obtener_clase_y_mascara_predeterminada_ipv4(ip_str):
    try:
        primer_octeto = int(ip_str.split('.')[0])
    except: return None, None
    if 1 <= primer_octeto <= 126: return 'A', '255.0.0.0'
    elif 128 <= primer_octeto <= 191: return 'B', '255.255.0.0'
    elif 192 <= primer_octeto <= 223: return 'C', '255.255.255.0'
    return None, None

def validar_nombre(nombre):
    if not re.match(r'^[a-zA-Z0-9\-\.\s]+$', nombre):
        raise ValueError("Nombre solo admite letras, números, espacios, '-' y '.'")
    if len(nombre) > 50: raise ValueError("Nombre no debe exceder 50 caracteres.")
    return True

def validar_servicios(servicios):
    for servicio in servicios:
        if servicio not in SERVICIOS_VALIDOS.values():
            raise ValueError(f"Servicio inválido: {servicio}")
    return True

def validar_vlan_id(vlan_id_str):
    vlan_id_str = vlan_id_str.strip()
    if not vlan_id_str.isdigit():
        raise ValueError("ID de VLAN debe ser un número.")
    vlan_id = int(vlan_id_str)
    if not (VLAN_ID_MIN <= vlan_id <= VLAN_ID_MAX):
        raise ValueError(f"ID de VLAN debe estar entre {VLAN_ID_MIN} y {VLAN_ID_MAX}.")
    return vlan_id

def validar_vlan_nombre(vlan_nombre_str):
    vlan_nombre_str = vlan_nombre_str.strip()
    if not vlan_nombre_str: # Permitir nombres vacíos si se desea, o añadir validación
        return "N/A" # Opcional: nombre por defecto si está vacío
    if not re.match(r'^[a-zA-Z0-9\-\s_]+$', vlan_nombre_str):
        raise ValueError("Nombre de VLAN solo admite letras, números, espacios, guiones y guiones bajos.")
    if len(vlan_nombre_str) > 30:
        raise ValueError("Nombre de VLAN no debe exceder 30 caracteres.")
    return vlan_nombre_str

# --- Representación de Dispositivos ---
def crear_dispositivo_dict(tipo, nombre, ip=None, mascara_red=None, ip_type=None, capa=None, servicios=None, vlans=None):
    try:
        validar_nombre(nombre)
        if servicios: validar_servicios(servicios)

        dispositivo_dict = {"TIPO": tipo, "NOMBRE": nombre}
        if ip:
            dispositivo_dict["IP"] = ip
            dispositivo_dict["IP_TYPE"] = ip_type
            if mascara_red and ip_type == "IPv4":
                dispositivo_dict["MÁSCARA"] = mascara_red
        if capa: dispositivo_dict["CAPA"] = capa
        dispositivo_dict["SERVICIOS"] = ' '.join(sorted(list(set(servicios)))) if servicios else "Ninguno"
        dispositivo_dict["VLANS"] = sorted(vlans, key=lambda v: v['id']) if vlans else [] # Almacena lista de dicts VLAN

        return dispositivo_dict
    except ValueError as e:
        mostrar_mensaje(f"Error al crear datos del dispositivo: {e}", "error")
        return None

def formatear_dispositivo_para_mostrar(dispositivo_dict):
    if not dispositivo_dict: return ""
    lineas = [
        f"{Color.CYAN}🔧 {Color.BOLD}TIPO:{Color.END} {dispositivo_dict.get('TIPO', 'N/A')}",
        f"{Color.CYAN}🏷️ {Color.BOLD}NOMBRE:{Color.END} {dispositivo_dict.get('NOMBRE', 'N/A')}"
    ]
    if "IP" in dispositivo_dict:
        ip_type_info = f" ({dispositivo_dict.get('IP_TYPE', '')})" if dispositivo_dict.get('IP_TYPE') else ""
        lineas.append(f"{Color.CYAN}🌍 {Color.BOLD}IP:{Color.END} {dispositivo_dict['IP']}{ip_type_info}")
        if "MÁSCARA" in dispositivo_dict and dispositivo_dict.get('IP_TYPE') == "IPv4":
            lineas.append(f"{Color.CYAN}🌐 {Color.BOLD}MÁSCARA (IPv4):{Color.END} {dispositivo_dict['MÁSCARA']}")
    if "CAPA" in dispositivo_dict:
        lineas.append(f"{Color.CYAN}📊 {Color.BOLD}CAPA:{Color.END} {dispositivo_dict['CAPA']}")
    if "SERVICIOS" in dispositivo_dict:
        lineas.append(f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {dispositivo_dict['SERVICIOS']}")
    
    vlans_disp = dispositivo_dict.get("VLANS", [])
    if vlans_disp:
        vlan_str_list = [f"ID: {v['id']} (Nombre: {v.get('nombre', 'N/A')})" for v in vlans_disp]
        lineas.append(f"{Color.CYAN} VLANs:{Color.END} {', '.join(vlan_str_list)}")
    else:
        lineas.append(f"{Color.CYAN} VLANs:{Color.END} Ninguna")
        
    separador = f"{Color.BLUE}{'═' * 60}{Color.END}"
    return f"\n{separador}\n" + "\n".join(lineas) + f"\n{separador}"

# --- Generación de Reportes ---
def generar_reporte_estadistico(dispositivos_dicts):
    if not dispositivos_dicts:
        mostrar_mensaje("⚠️ No existen dispositivos registrados.", "advertencia")
        sleep(2)
        return

    mostrar_progreso("Generando Reporte Estadístico", 1)
    mostrar_titulo("📊 REPORTE ESTADÍSTICO DETALLADO")

    print(f"\n{Color.BOLD}{Color.PURPLE}📌 RESUMEN GENERAL{Color.END}")
    print(f"{Color.CYAN}📅 Total de dispositivos registrados:{Color.END} {len(dispositivos_dicts)}")
    print(f"{Color.CYAN}📅 Última actualización del reporte:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n{Color.BOLD}{Color.PURPLE}🔢 DISTRIBUCIÓN POR TIPO:{Color.END}")
    tipos_count = {}
    for disp_dict in dispositivos_dicts:
        tipo = disp_dict.get("TIPO", "Desconocido")
        tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

    for tipo, cantidad in sorted(tipos_count.items(), key=lambda x: x[1], reverse=True):
        print(f"\n   {Color.YELLOW}{tipo.upper()} ({cantidad} dispositivos):{Color.END}")
        count_detalle = 0
        for disp_dict in dispositivos_dicts:
            if count_detalle >= 3: break
            if disp_dict.get("TIPO") == tipo:
                nombre = disp_dict.get("NOMBRE", "N/A")
                ip_info = disp_dict.get("IP", "Sin IP")
                if "MÁSCARA" in disp_dict and disp_dict.get("IP_TYPE") == "IPv4":
                    ip_info += f" / {disp_dict['MÁSCARA']}"
                print(f"     - {nombre} ({ip_info})")
                count_detalle += 1
        if cantidad > 3:
            print(f"     {Color.DARKCYAN}...y {cantidad-3} más{Color.END}")

    print(f"\n{Color.BOLD}{Color.PURPLE}📡 DISTRIBUCIÓN POR CAPA DE RED:{Color.END}")
    capas_count = {}
    for disp_dict in dispositivos_dicts:
        capa = disp_dict.get("CAPA", "Sin capa especificada")
        capas_count[capa] = capas_count.get(capa, 0) + 1

    for capa, cantidad in sorted(capas_count.items(), key=lambda x: x[1], reverse=True):
        print(f"\n   {Color.YELLOW}{capa.upper()} ({cantidad} dispositivos):{Color.END}")
        count_detalle = 0
        for disp_dict in dispositivos_dicts:
            if count_detalle >= 3: break
            if disp_dict.get("CAPA", "Sin capa especificada") == capa:
                nombre = disp_dict.get("NOMBRE", "N/A")
                tipo_disp = disp_dict.get("TIPO", "N/A")
                servicios_str = disp_dict.get("SERVICIOS", "Ninguno")
                print(f"     - {nombre} ({tipo_disp}) con servicios: {servicios_str}")
                count_detalle += 1
        if cantidad > 3:
            print(f"     {Color.DARKCYAN}...y {cantidad-3} más{Color.END}")

    # Sección "SERVICIOS MÁS UTILIZADOS" eliminada

    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'📋 LISTADO COMPLETO DE DISPOSITIVOS'.center(70)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}")

    for i, disp_dict in enumerate(dispositivos_dicts, 1):
        print(f"\n{Color.YELLOW}🔹 Dispositivo {i}:{Color.END}")
        print(f"   {Color.CYAN}🔧 Tipo:{Color.END} {disp_dict.get('TIPO', 'N/A')}")
        print(f"   {Color.CYAN}🏷️ Nombre:{Color.END} {disp_dict.get('NOMBRE', 'N/A')}")
        if "IP" in disp_dict:
            ip_type_info = f" ({disp_dict.get('IP_TYPE', '')})" if disp_dict.get('IP_TYPE') else ""
            print(f"   {Color.CYAN}🌍 IP:{Color.END} {disp_dict['IP']}{ip_type_info}")
        if "MÁSCARA" in disp_dict and disp_dict.get('IP_TYPE') == "IPv4":
            print(f"   {Color.CYAN}🌐 Máscara (IPv4):{Color.END} {disp_dict['MÁSCARA']}")
        if "CAPA" in disp_dict: print(f"   {Color.CYAN}📊 Capa:{Color.END} {disp_dict['CAPA']}")
        if "SERVICIOS" in disp_dict: print(f"   {Color.CYAN}🛠️ Servicios:{Color.END} {disp_dict['SERVICIOS']}")
        
        vlans_disp = disp_dict.get("VLANS", [])
        if vlans_disp:
            vlan_str_list = [f"ID: {v['id']} (Nombre: {v.get('nombre', 'N/A')})" for v in vlans_disp]
            print(f"   {Color.CYAN} VLANs:{Color.END} {', '.join(vlan_str_list)}")
        else:
            print(f"   {Color.CYAN} VLANs:{Color.END} Ninguna")


    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.GREEN}🎉 Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}\n")
    input(f"{Color.GREEN}Presione Enter para volver al menú principal...{Color.END}")

# --- Funciones de Menú y Selección ---
def mostrar_menu_principal():
    mostrar_titulo("SISTEMA DE GESTIÓN DE DISPOSITIVOS DE RED")
    print(f"{Color.BOLD}{Color.YELLOW}1.{Color.END} 📱 Agregar nuevo dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}2.{Color.END} 📜 Mostrar todos los dispositivos")
    print(f"{Color.BOLD}{Color.YELLOW}3.{Color.END} 🔍 Buscar dispositivo por nombre")
    print(f"{Color.BOLD}{Color.YELLOW}4.{Color.END} ➕ Agregar servicio a dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}5.{Color.END} ➖ Eliminar servicio de dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}6.{Color.END} ⚙️ Gestionar VLANs de dispositivo") # Nueva opción VLAN
    print(f"{Color.BOLD}{Color.YELLOW}7.{Color.END} ❌ Eliminar dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}8.{Color.END} 📊 Generar reporte estadístico")
    print(f"{Color.BOLD}{Color.YELLOW}9.{Color.END} 💾 Exportar datos a archivo TXT")
    print(f"{Color.BOLD}{Color.YELLOW}10.{Color.END} 🚪 Salir") # Ajustar número de salida
    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")

def seleccionar_opcion(opciones, titulo, permitir_volver=True):
    # opciones puede ser un dict o una lista de tuplas/listas (clave, valor_a_mostrar)
    print(f"\n{Color.BOLD}{titulo}{Color.END}")
    
    opciones_list = []
    if isinstance(opciones, dict):
        opciones_list = list(opciones.items())
    elif isinstance(opciones, list): # Asumimos lista de (clave_interna, valor_mostrado)
        opciones_list = opciones

    for i, item in enumerate(opciones_list, 1):
        # item puede ser (clave, valor) de un dict, o (clave_interna, valor_mostrado) de una lista
        valor_a_mostrar = item[1] if isinstance(item, (tuple, list)) and len(item) > 1 else str(item)
        print(f"{Color.YELLOW}{i}.{Color.END} {valor_a_mostrar}")

    if permitir_volver:
        print(f"{Color.YELLOW}0.{Color.END} Volver / Cancelar")

    while True:
        try:
            max_opc = len(opciones_list)
            prompt = f"\n{Color.GREEN}↳ Seleccione una opción (1-{max_opc}"
            if permitir_volver: prompt += " o 0 para volver): "
            else: prompt += "): "
            opcion_num_str = input(f"{prompt}{Color.END}")
            opcion_num = int(opcion_num_str)
            
            if permitir_volver and opcion_num == 0: return "VOLVER"
            if 1 <= opcion_num <= max_opc:
                # Devolver la clave interna o el ítem completo según cómo se pasó 'opciones'
                selected_item = opciones_list[opcion_num-1]
                return selected_item[0] if isinstance(selected_item, (tuple, list)) else selected_item # Devuelve la clave o el valor si no es par
            mostrar_mensaje(f"Por favor ingrese un número entre 1 y {max_opc}{(', o 0' if permitir_volver else '')}", "error")
        except ValueError:
            mostrar_mensaje("Entrada inválida. Por favor ingrese un número.", "error")

def ingresar_ip_y_mascara(dispositivos_existentes):
    ip_final, mascara_final, tipo_ip_final, capa_final_str = None, None, None, None
    while True:
        ip_str = input(f"{Color.GREEN}↳ IP (IPv4/IPv6, vacío omite, '0' cancela): {Color.END}").strip()
        if not ip_str: return None, None, None, None
        if ip_str == "0": return "VOLVER", "VOLVER", "VOLVER", "VOLVER"
        try:
            tipo_ip_validado = validar_formato_ip(ip_str)
            if any(d.get("IP") == ip_str for d in dispositivos_existentes):
                mostrar_mensaje(f"Error: IP ({ip_str}) ya en uso.", "error"); continue
            
            if tipo_ip_validado:
                mostrar_mensaje(f"IP {Color.YELLOW}{ip_str}{Color.END} ({tipo_ip_validado}) válida.", "exito")
                print(f"\n{Color.CYAN}--- Selección Capa de Red para {ip_str} ---{Color.END}")
                capa_seleccionada_key = seleccionar_opcion(CAPAS_RED, "📌 Capa de red:")
                if capa_seleccionada_key == "VOLVER": continue
                capa_final_str = CAPAS_RED[capa_seleccionada_key]

                if tipo_ip_validado == "IPv4":
                    while True:
                        mascara_str = input(f"{Color.GREEN}↳ Máscara red para {Color.CYAN}{ip_str}{Color.END} ('0' cancela IP): {Color.END}").strip()
                        if mascara_str == "0": break 
                        if not mascara_str: mostrar_mensaje("Máscara obligatoria para IPv4.", "error"); continue
                        try:
                            validar_mascara_red_ipv4(mascara_str)
                            clase_ip, mascara_def = obtener_clase_y_mascara_predeterminada_ipv4(ip_str)
                            if clase_ip and mascara_str != mascara_def:
                                mostrar_mensaje(f"Advertencia: Máscara {mascara_str} no es predeterminada ({mascara_def}) para Clase {clase_ip}.", "advertencia")
                            return ip_str, mascara_str, tipo_ip_validado, capa_final_str
                        except ValueError as e_mask:
                            mostrar_mensaje(str(e_mask), "error")
                            _, sug_mask = obtener_clase_y_mascara_predeterminada_ipv4(ip_str)
                            if sug_mask: print(f"{Color.YELLOW}ℹ️ Máscara común para {ip_str}: {sug_mask}.{Color.END}")
                    if mascara_str == "0": continue 
                elif tipo_ip_validado == "IPv6":
                    mostrar_mensaje(f"No se requiere máscara para IPv6 ({ip_str}).", "info")
                    return ip_str, None, tipo_ip_validado, capa_final_str
        except ValueError as e_ip:
            mostrar_mensaje(str(e_ip), "error")
            print(f"\n{Color.YELLOW}💡 IPs válidas: IPv4 (192.168.1.1), IPv6 (2001:db8::1){Color.END}")
        if input(f"{Color.GREEN}¿Reintentar IP? (s/n): {Color.END}").strip().lower() != 's':
            return "VOLVER", "VOLVER", "VOLVER", "VOLVER"

# --- Funciones Principales de Gestión de Dispositivos ---
def agregar_dispositivo_interactivo(dispositivos_actuales):
    mostrar_progreso("Asistente de nuevo dispositivo", 0.5)
    mostrar_titulo("AGREGAR NUEVO DISPOSITIVO")

    tipo_sel_key = seleccionar_opcion(TIPOS_DISPOSITIVO, "📌 Tipo de dispositivo:")
    if tipo_sel_key == "VOLVER": return None
    tipo_sel_str = TIPOS_DISPOSITIVO[tipo_sel_key]

    nombre_disp = ""
    while True:
        nombre_in = input(f"{Color.GREEN}↳ Nombre dispositivo ('0' cancela): {Color.END}").strip()
        if nombre_in == "0": return None
        try:
            if validar_nombre(nombre_in):
                if any(d.get("NOMBRE", "").lower() == nombre_in.lower() for d in dispositivos_actuales):
                    mostrar_mensaje(f"Error: Nombre '{nombre_in}' ya existe.", "error")
                else: nombre_disp = nombre_in; break
        except ValueError as e: mostrar_mensaje(str(e), "error")

    ip_disp, mask_disp, ip_type_disp, capa_disp_str = None, None, None, None
    print(f"\n{Color.CYAN}--- Config. Red para: {tipo_sel_str} ({nombre_disp}) ---{Color.END}")
    ip_disp, mask_disp, ip_type_disp, capa_disp_str = ingresar_ip_y_mascara(dispositivos_actuales)
    if ip_disp == "VOLVER": return None

    msg_ip_capa = ""
    if ip_disp:
        msg_ip_capa = f"IP {Color.YELLOW}{ip_disp}{Color.END} ({ip_type_disp})"
        if mask_disp and ip_type_disp == "IPv4": msg_ip_capa += f", Máscara {Color.YELLOW}{mask_disp}{Color.END}"
        if capa_disp_str: msg_ip_capa += f", Capa: {Color.YELLOW}{capa_disp_str}{Color.END}"
        mostrar_mensaje(f"{msg_ip_capa} procesada.", "exito")
    else:
        mostrar_mensaje(f"No se configuró IP para {nombre_disp}.", "info")
        if tipo_sel_key in ['ROUTER', 'SWITCH', 'FIREWALL', 'SERVIDOR']:
            print(f"\n{Color.CYAN}--- Capa de Red (Opcional) para {nombre_disp} ---{Color.END}")
            capa_key_opc = seleccionar_opcion(CAPAS_RED, "📌 Capa de red ('0' omite):")
            if capa_key_opc != "VOLVER":
                capa_disp_str = CAPAS_RED[capa_key_opc]
                mostrar_mensaje(f"Capa: {Color.YELLOW}{capa_disp_str}{Color.END}", "info")
    sleep(1)

    servicios_disp_list = []
    if tipo_sel_key in ['SERVIDOR', 'ROUTER', 'FIREWALL']:
        mostrar_titulo(f"SERVICIOS PARA: {nombre_disp}")
        serv_copia = SERVICIOS_VALIDOS.copy()
        while True:
            print(f"\n{Color.CYAN}Servicios actuales: {Color.END}{', '.join(servicios_disp_list) or 'Ninguno'}")
            serv_menu = {k: v for k, v in serv_copia.items() if v not in servicios_disp_list}
            if not serv_menu: mostrar_mensaje("Todos los servicios disponibles agregados.", "info"); break
            serv_eleg_key = seleccionar_opcion(serv_menu, "Seleccione servicio ('0' finaliza):")
            if serv_eleg_key == "VOLVER": break
            serv_eleg_str = serv_menu[serv_eleg_key]
            if serv_eleg_str not in servicios_disp_list:
                servicios_disp_list.append(serv_eleg_str)
                mostrar_mensaje(f"Servicio {serv_eleg_str} agregado.", "exito")
            sleep(0.5)

    vlans_disp_list = []
    if tipo_sel_key in ['SWITCH', 'ROUTER', 'FIREWALL', 'SERVIDOR']: # Tipos que suelen usar VLANs
        mostrar_titulo(f"VLANS PARA: {nombre_disp}")
        if input(f"{Color.GREEN}¿Desea añadir VLANs a este dispositivo? (s/n): {Color.END}").strip().lower() == 's':
            while True:
                print(f"\n{Color.CYAN}VLANs actuales: {Color.END}")
                if vlans_disp_list:
                    for v in vlans_disp_list: print(f"  - ID: {v['id']}, Nombre: {v['nombre']}")
                else: print("  Ninguna")

                try:
                    vlan_id_str = input(f"{Color.GREEN}↳ Ingrese ID de VLAN ({VLAN_ID_MIN}-{VLAN_ID_MAX}, '0' para terminar): {Color.END}").strip()
                    if vlan_id_str == '0': break
                    vlan_id = validar_vlan_id(vlan_id_str)

                    if any(v['id'] == vlan_id for v in vlans_disp_list):
                        mostrar_mensaje(f"Error: VLAN ID {vlan_id} ya existe en este dispositivo.", "error")
                        continue
                    
                    vlan_nombre_str = input(f"{Color.GREEN}↳ Ingrese nombre para VLAN {vlan_id} (opcional, Enter omite): {Color.END}").strip()
                    vlan_nombre = validar_vlan_nombre(vlan_nombre_str) if vlan_nombre_str else f"VLAN_{vlan_id}"

                    vlans_disp_list.append({"id": vlan_id, "nombre": vlan_nombre})
                    mostrar_mensaje(f"VLAN ID: {vlan_id}, Nombre: {vlan_nombre} agregada.", "exito")
                except ValueError as e_vlan:
                    mostrar_mensaje(str(e_vlan), "error")
                
                if input(f"{Color.GREEN}¿Añadir otra VLAN? (s/n): {Color.END}").strip().lower() != 's':
                    break
    
    nuevo_disp_dict = crear_dispositivo_dict(
        tipo_sel_str, nombre_disp, ip_disp, mask_disp, ip_type_disp, capa_disp_str, servicios_disp_list, vlans_disp_list
    )

    if nuevo_disp_dict:
        mostrar_mensaje(f"Dispositivo '{nombre_disp}' creado.", "exito")
        print(formatear_dispositivo_para_mostrar(nuevo_disp_dict))
        input(f"{Color.GREEN}Presione Enter para guardar y volver...{Color.END}")
        mostrar_progreso("Guardando dispositivo", 0.5)
        return nuevo_disp_dict
    else:
        mostrar_mensaje("Creación de dispositivo cancelada/fallida.", "advertencia"); sleep(2)
        return None

def mostrar_dispositivos(dispositivos_dicts, titulo="LISTADO DE DISPOSITIVOS"):
    mostrar_progreso("Cargando listado", 0.5)
    mostrar_titulo(titulo)
    if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos registrados.", "advertencia")
    else:
        for i, disp_dict in enumerate(dispositivos_dicts, 1):
            nombre_enc = disp_dict.get("NOMBRE", f"Dispositivo {i}")
            print(f"{Color.YELLOW}{i}.{Color.END} {Color.BOLD}{nombre_enc}{Color.END}")
            print(formatear_dispositivo_para_mostrar(disp_dict))
    input(f"\n{Color.GREEN}Presione Enter para volver al menú...{Color.END}")

def buscar_dispositivo(dispositivos_dicts):
    mostrar_progreso("Iniciando búsqueda", 0.2)
    mostrar_titulo("BUSCAR DISPOSITIVO")
    if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos para buscar.", "advertencia"); sleep(2); return

    nombre_bus = input(f"{Color.GREEN}↳ Nombre (o parte) a buscar ('0' volver): {Color.END}").strip().lower()
    if nombre_bus == "0": return
    if not nombre_bus: mostrar_mensaje("Debe ingresar término de búsqueda.", "error"); sleep(2); return

    mostrar_progreso(f"Buscando '{nombre_bus}'", 0.5)
    encontrados = [d for d in dispositivos_dicts if nombre_bus in d.get("NOMBRE", "").lower()]

    if encontrados: mostrar_dispositivos(encontrados, f"RESULTADOS PARA '{nombre_bus.upper()}'")
    else: mostrar_mensaje(f"No se encontraron coincidencias para '{nombre_bus}'.", "advertencia"); sleep(2)

def agregar_servicio_dispositivo(dispositivos_dicts):
    mostrar_progreso("Gestión de servicios", 0.5)
    mostrar_titulo("AGREGAR SERVICIO A DISPOSITIVO")
    if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos.", "advertencia"); sleep(2); return

    modificables_info = []
    for i, d in enumerate(dispositivos_dicts):
        tipo_key = next((k for k, v in TIPOS_DISPOSITIVO.items() if v == d.get("TIPO")), None)
        if tipo_key in ['SERVIDOR', 'ROUTER', 'FIREWALL']:
            modificables_info.append({"idx_orig": i, "nombre": d.get("NOMBRE","N/A"), "tipo": d.get("TIPO")})

    if not modificables_info: mostrar_mensaje("No hay dispositivos aptos para agregar servicios.", "advertencia"); sleep(2); return
    
    print(f"{Color.BOLD}📋 Dispositivos para agregar servicio:{Color.END}")
    opciones_menu_disp = [(info["idx_orig"], f"{info['nombre']} ({info['tipo']})") for info in modificables_info]
    
    idx_real_sel = seleccionar_opcion(opciones_menu_disp, "Seleccione dispositivo:")
    if idx_real_sel == "VOLVER": return

    disp_modificar = dispositivos_dicts[idx_real_sel]
    nombre_disp_mod = disp_modificar.get("NOMBRE")
    mostrar_titulo(f"AGREGAR SERVICIO A: {nombre_disp_mod}")
    
    serv_actuales_str = disp_modificar.get("SERVICIOS", "Ninguno")
    serv_actuales_list = [s.strip() for s in serv_actuales_str.split(' ') if s.strip() and s != "Ninguno"]
    
    serv_disp_menu = {k: v for k, v in SERVICIOS_VALIDOS.items() if v not in serv_actuales_list}
    if not serv_disp_menu: mostrar_mensaje(f"'{nombre_disp_mod}' ya tiene todos los servicios.", "error"); sleep(3); return

    print(f"{Color.CYAN}Servicios en '{nombre_disp_mod}': {Color.END}{', '.join(serv_actuales_list) or 'Ninguno'}")
    serv_agregar_key = seleccionar_opcion(serv_disp_menu, "Seleccione servicio a agregar:")
    if serv_agregar_key == "VOLVER": return
    
    serv_agregar_str = serv_disp_menu[serv_agregar_key]
    serv_actuales_list.append(serv_agregar_str)
    disp_modificar["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales_list))))
    guardar_datos_json(dispositivos_dicts)
    mostrar_progreso("Guardando cambios", 0.5)
    mostrar_mensaje(f"Servicio '{serv_agregar_str}' agregado a '{nombre_disp_mod}'.", "exito")
    print(formatear_dispositivo_para_mostrar(disp_modificar))
    input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")

def eliminar_servicio_dispositivo(dispositivos_dicts):
    mostrar_progreso("Eliminación de servicios", 0.5)
    mostrar_titulo("ELIMINAR SERVICIO DE DISPOSITIVO")
    if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos.", "advertencia"); sleep(2); return

    disp_con_serv_info = []
    for i, d in enumerate(dispositivos_dicts):
        serv_str = d.get("SERVICIOS", "Ninguno")
        if serv_str != "Ninguno" and serv_str.strip():
            disp_con_serv_info.append({"idx_orig": i, "nombre": d.get("NOMBRE","N/A"), "tipo": d.get("TIPO"), "servicios": serv_str})

    if not disp_con_serv_info: mostrar_mensaje("No hay dispositivos con servicios configurados.", "advertencia"); sleep(2); return

    print(f"{Color.BOLD}📋 Dispositivos con servicios (seleccione para eliminar):{Color.END}")
    opciones_menu_disp = [(info["idx_orig"], f"{info['nombre']} ({info['tipo']}) - Servicios: {info['servicios']}") for info in disp_con_serv_info]
    
    idx_real_sel = seleccionar_opcion(opciones_menu_disp, "Seleccione dispositivo:")
    if idx_real_sel == "VOLVER": return
    
    disp_modificar = dispositivos_dicts[idx_real_sel]
    nombre_disp_mod = disp_modificar.get("NOMBRE")
    serv_actuales_list = [s.strip() for s in disp_modificar.get("SERVICIOS", "").split(' ') if s.strip() and s != "Ninguno"]

    if not serv_actuales_list: mostrar_mensaje(f"'{nombre_disp_mod}' no tiene servicios para eliminar.", "info"); sleep(2); return
        
    mostrar_titulo(f"ELIMINAR SERVICIO DE: {nombre_disp_mod}")
    print(f"{Color.CYAN}Servicios en '{nombre_disp_mod}': {Color.END}{', '.join(serv_actuales_list)}")
    
    serv_elim_menu = {serv_nombre: serv_nombre for serv_nombre in serv_actuales_list} # {valor: valor}
    serv_elim_nombre = seleccionar_opcion(serv_elim_menu, "Seleccione servicio a eliminar:") # Devuelve el valor (nombre del servicio)
    if serv_elim_nombre == "VOLVER": return

    if serv_elim_nombre in serv_actuales_list:
        serv_actuales_list.remove(serv_elim_nombre)
        disp_modificar["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales_list)))) if serv_actuales_list else "Ninguno"
        guardar_datos_json(dispositivos_dicts)
        mostrar_progreso("Guardando", 0.5)
        mostrar_mensaje(f"Servicio '{serv_elim_nombre}' eliminado de '{nombre_disp_mod}'.", "exito")
        print(formatear_dispositivo_para_mostrar(disp_modificar))
    else: mostrar_mensaje(f"Error: Servicio '{serv_elim_nombre}' no encontrado.", "error")
    input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")

def gestionar_vlans_dispositivo(dispositivos_dicts):
    mostrar_progreso("Gestión de VLANs", 0.5)
    mostrar_titulo("GESTIONAR VLANS DE DISPOSITIVO")

    if not dispositivos_dicts:
        mostrar_mensaje("No hay dispositivos registrados.", "advertencia"); sleep(2); return

    # Filtrar dispositivos que pueden tener VLANs (ej. Switches, Routers, Firewalls, Servidores)
    dispositivos_aptos_info = []
    for i, disp_dict in enumerate(dispositivos_dicts):
        tipo_key = next((k for k, v in TIPOS_DISPOSITIVO.items() if v == disp_dict.get("TIPO")), None)
        if tipo_key in ['SWITCH', 'ROUTER', 'FIREWALL', 'SERVIDOR']:
            dispositivos_aptos_info.append({
                "indice_original": i,
                "nombre": disp_dict.get("NOMBRE", "N/A"),
                "tipo": disp_dict.get("TIPO", "N/A")
            })
    
    if not dispositivos_aptos_info:
        mostrar_mensaje("No hay dispositivos aptos (Switches, Routers, etc.) para gestionar VLANs.", "advertencia"); sleep(2); return

    print(f"{Color.BOLD}📋 Dispositivos aptos para gestión de VLANs:{Color.END}")
    opciones_menu_disp = [(info["indice_original"], f"{info['nombre']} ({info['tipo']})") for info in dispositivos_aptos_info]
    
    idx_real_seleccionado = seleccionar_opcion(opciones_menu_disp, "Seleccione el dispositivo:")
    if idx_real_seleccionado == "VOLVER": return

    dispositivo_a_modificar = dispositivos_dicts[idx_real_seleccionado]
    nombre_disp = dispositivo_a_modificar.get("NOMBRE")

    while True:
        mostrar_titulo(f"GESTIONAR VLANS PARA: {nombre_disp}")
        vlans_actuales = dispositivo_a_modificar.get("VLANS", [])
        print(f"{Color.CYAN}VLANs actuales en '{nombre_disp}':{Color.END}")
        if vlans_actuales:
            for i, vlan_info in enumerate(vlans_actuales, 1):
                print(f"  {i}. ID: {vlan_info['id']}, Nombre: {vlan_info.get('nombre', 'N/A')}")
        else:
            print("  Ninguna VLAN configurada.")
        
        print(f"\n{Color.YELLOW}1.{Color.END} Añadir VLAN")
        print(f"{Color.YELLOW}2.{Color.END} Eliminar VLAN")
        print(f"{Color.YELLOW}0.{Color.END} Volver al menú anterior")
        
        opc_vlan = input(f"\n{Color.GREEN}↳ Seleccione una opción para VLANs: {Color.END}").strip()

        if opc_vlan == '1': # Añadir VLAN
            try:
                vlan_id_str = input(f"{Color.GREEN}↳ ID de la nueva VLAN ({VLAN_ID_MIN}-{VLAN_ID_MAX}): {Color.END}").strip()
                vlan_id = validar_vlan_id(vlan_id_str)

                if any(v['id'] == vlan_id for v in vlans_actuales):
                    mostrar_mensaje(f"Error: VLAN ID {vlan_id} ya existe en este dispositivo.", "error"); sleep(2); continue
                
                vlan_nombre_str = input(f"{Color.GREEN}↳ Nombre para VLAN {vlan_id} (opcional): {Color.END}").strip()
                vlan_nombre = validar_vlan_nombre(vlan_nombre_str) if vlan_nombre_str else f"VLAN_{vlan_id}"

                vlans_actuales.append({"id": vlan_id, "nombre": vlan_nombre})
                dispositivo_a_modificar["VLANS"] = sorted(vlans_actuales, key=lambda v: v['id']) # Mantener ordenado
                guardar_datos_json(dispositivos_dicts)
                mostrar_mensaje(f"VLAN ID: {vlan_id}, Nombre: {vlan_nombre} añadida a '{nombre_disp}'.", "exito")
            except ValueError as e:
                mostrar_mensaje(str(e), "error")
            sleep(1.5)

        elif opc_vlan == '2': # Eliminar VLAN
            if not vlans_actuales:
                mostrar_mensaje("No hay VLANs para eliminar.", "advertencia"); sleep(2); continue
            
            print(f"\n{Color.BOLD}Seleccione la VLAN a eliminar de '{nombre_disp}':{Color.END}")
            opciones_vlan_elim = [(idx, f"ID: {v['id']}, Nombre: {v.get('nombre', 'N/A')}") for idx, v in enumerate(vlans_actuales)]

            idx_vlan_a_eliminar_sel = seleccionar_opcion(opciones_vlan_elim, "VLAN a eliminar:")
            if idx_vlan_a_eliminar_sel == "VOLVER": continue
            
            vlan_eliminada = vlans_actuales.pop(idx_vlan_a_eliminar_sel)
            dispositivo_a_modificar["VLANS"] = vlans_actuales # Ya está ordenada
            guardar_datos_json(dispositivos_dicts)
            mostrar_mensaje(f"VLAN ID: {vlan_eliminada['id']} eliminada de '{nombre_disp}'.", "exito")
            sleep(1.5)

        elif opc_vlan == '0':
            break
        else:
            mostrar_mensaje("Opción de VLAN inválida.", "error"); sleep(1.5)


def eliminar_dispositivo(dispositivos_dicts):
    mostrar_progreso("Eliminación de dispositivo", 0.5)
    while True:
        mostrar_titulo("ELIMINAR DISPOSITIVO")
        if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos para eliminar.", "advertencia"); sleep(2); return

        print(f"{Color.BOLD}📋 Dispositivos para eliminar:{Color.END}\n")
        opciones_menu_disp = [(idx, f"{d.get('NOMBRE', f'Disp #{idx+1}')} (Tipo: {d.get('TIPO', 'N/A')})") for idx, d in enumerate(dispositivos_dicts)]
        
        idx_real_sel = seleccionar_opcion(opciones_menu_disp, "Seleccione dispositivo a eliminar:")
        if idx_real_sel == "VOLVER": return
        
        disp_eliminar = dispositivos_dicts[idx_real_sel]
        nombre_elim = disp_eliminar.get("NOMBRE", f"Dispositivo #{idx_real_sel+1}")
        
        print(f"\n{Color.RED}{'⚠' * 30} CONFIRMACIÓN {'⚠' * 30}{Color.END}")
        confirmar = input(f"{Color.RED}{Color.BOLD}¿SEGURO desea eliminar '{nombre_elim}'? (S/N): {Color.END}").strip().upper()
        print(f"{Color.RED}{'⚠' * (60 + len(' CONFIRMACIÓN '))}{Color.END}")
        
        if confirmar == 'S':
            mostrar_progreso(f"Eliminando '{nombre_elim}'", 1)
            dispositivos_dicts.pop(idx_real_sel)
            guardar_datos_json(dispositivos_dicts)
            mostrar_mensaje(f"'{nombre_elim}' eliminado.", "exito"); sleep(2)
            if not dispositivos_dicts: mostrar_mensaje("Todos los dispositivos eliminados.", "info"); sleep(2); return
        elif confirmar == 'N': mostrar_mensaje("Eliminación cancelada.", "info"); sleep(2)
        else: mostrar_mensaje("Opción inválida (S/N).", "error"); sleep(2)


# --- Sistema de Inicio de Sesión ---
def pantalla_login():
    intentos = 0; max_intentos = 3
    while intentos < max_intentos:
        mostrar_titulo("INICIO DE SESIÓN")
        usuario = input(f"{Color.GREEN}👤 Usuario: {Color.END}").strip()
        try:
            import getpass
            contraseña = getpass.getpass(f"{Color.GREEN}🔑 Contraseña: {Color.END}").strip()
        except ImportError: contraseña = input(f"{Color.GREEN}🔑 Contraseña (visible): {Color.END}").strip()
        
        if usuario in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[usuario] == contraseña:
            mostrar_progreso(f"Acceso concedido. Bienvenido {usuario}!", 1); return True
        else:
            intentos += 1; restantes = max_intentos - intentos
            if restantes > 0: mostrar_mensaje(f"Incorrecto. {restantes} {'intento' if restantes == 1 else 'intentos'} restantes.", "error"); sleep(1.5)
            else: mostrar_mensaje("Demasiados intentos. Programa se cerrará.", "error"); sleep(3); return False
    return False

# --- Función Principal (main) ---
def main():
    dispositivos = cargar_datos_json()
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Color.GREEN}↳ Seleccione una opción (1-10): {Color.END}").strip()
        mostrar_progreso("Procesando opción", 0.3)
        if opcion == "1":
            nuevo_disp = agregar_dispositivo_interactivo(dispositivos)
            if nuevo_disp: dispositivos.append(nuevo_disp); guardar_datos_json(dispositivos)
        elif opcion == "2": mostrar_dispositivos(dispositivos)
        elif opcion == "3": buscar_dispositivo(dispositivos)
        elif opcion == "4": agregar_servicio_dispositivo(dispositivos)
        elif opcion == "5": eliminar_servicio_dispositivo(dispositivos)
        elif opcion == "6": gestionar_vlans_dispositivo(dispositivos) # Nueva opción
        elif opcion == "7": eliminar_dispositivo(dispositivos)
        elif opcion == "8": generar_reporte_estadistico(dispositivos)
        elif opcion == "9": exportar_a_txt(dispositivos)
        elif opcion == "10":
            mostrar_mensaje("Guardando datos antes de salir...", "info")
            guardar_datos_json(dispositivos)
            mostrar_progreso("Saliendo del sistema", 1)
            mostrar_mensaje("¡Hasta pronto! 👋", "info"); sleep(1); limpiar_pantalla(); break
        else:
            mostrar_mensaje("Opción inválida. Seleccione del 1 al 10.", "error"); sleep(2)

if __name__ == "__main__":
    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═' * 70}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'BIENVENIDO AL SISTEMA AVANZADO DE GESTIÓN DE RED'.center(70)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 70}{Color.END}")
    sleep(1.5)
    if pantalla_login():
        main()
    else:
        limpiar_pantalla(); print(f"{Color.RED}{Color.BOLD}Acceso denegado.{Color.END}"); sleep(2); limpiar_pantalla()