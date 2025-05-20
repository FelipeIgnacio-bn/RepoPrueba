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

# Tipos de dispositivos que pueden tener servicios o VLANs (para lógica de edición/creación)
TIPOS_CON_SERVICIOS = ['SERVIDOR', 'ROUTER', 'FIREWALL']
TIPOS_CON_VLANS = ['SWITCH', 'ROUTER', 'FIREWALL', 'SERVIDOR']


CAPAS_RED = {
    'NUCLEO': '💎 Núcleo (Core)',
    'DISTRIBUCION': '📦 Distribución',
    'ACCESO': '🔌 Acceso',
    'TRANSPORTE': '🚢 Transporte',
    'APLICACION': '📱 Aplicación',
    'FISICA': '🔗 Física',
    'ENLACE_DATOS': '🔗 Enlace de Datos',
    'RED': '🌐 Red'
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
    if tipo == "error": icono = "❌ "; color = Color.RED
    elif tipo == "exito": icono = "✅ "; color = Color.GREEN
    elif tipo == "advertencia": icono = "⚠️ "; color = Color.YELLOW
    elif tipo == "info": icono = "ℹ️ "
    print(f"{color}{Color.BOLD}{icono}{mensaje}{Color.END}\n")

def mostrar_progreso(mensaje="Cargando", duracion_total=1, pasos=20):
    limpiar_pantalla()
    print(f"\n{Color.CYAN}{mensaje}...{Color.END}")
    for i in range(pasos + 1):
        porcentaje = int((i / pasos) * 100)
        barra = '█' * i + ' ' * (pasos - i)
        print(f"\r{Color.GREEN}[{barra}] {porcentaje}%{Color.END}", end="")
        sleep(duracion_total / pasos)
    print("\n"); sleep(0.5)

# --- Gestión de Archivo JSON ---
def cargar_datos_json():
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    if not os.path.exists(ARCHIVO_JSON):
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f: json.dump([], f)
        return []
    try:
        with open(ARCHIVO_JSON, 'r', encoding='utf-8') as f: return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        mostrar_mensaje(f"Error al cargar {ARCHIVO_JSON}. Se creará uno nuevo.", "advertencia")
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f: json.dump([], f)
        return []

def guardar_datos_json(dispositivos):
    os.makedirs(CARPETA_DATOS, exist_ok=True)
    try:
        with open(ARCHIVO_JSON, 'w', encoding='utf-8') as f:
            json.dump(dispositivos, f, ensure_ascii=False, indent=4)
    except IOError:
        mostrar_mensaje(f"Error: No se pudo guardar en {ARCHIVO_JSON}", "error")

# --- Funciones de Exportación ---
def exportar_a_txt(dispositivos):
    CARPETA_REPORTES = "reportes"; NOMBRE_BASE_ARCHIVO_TXT = "reporte_dispositivos.txt"
    if not dispositivos: mostrar_mensaje("No hay dispositivos para exportar.", "advertencia"); sleep(2); return
    os.makedirs(CARPETA_REPORTES, exist_ok=True)
    ruta_completa_archivo_txt = os.path.join(CARPETA_REPORTES, NOMBRE_BASE_ARCHIVO_TXT)
    mostrar_progreso(f"Exportando a {ruta_completa_archivo_txt}", 1.5)
    try:
        with open(ruta_completa_archivo_txt, 'w', encoding='utf-8') as f:
            f.write("="*70+"\nINFORME DE DISPOSITIVOS DE RED\n"+"="*70+"\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nTotal: {len(dispositivos)}\n"+("-"*70+"\n\n"))
            for i, disp_dict in enumerate(dispositivos, 1):
                f.write(f"Dispositivo #{i}\n"+("-"*30+"\n"))
                for clave, valor in disp_dict.items():
                    valor_limpio = re.sub(r'\033\[[0-9;]*[mK]', '', str(valor))
                    clave_fmt = clave.replace('_', ' ').capitalize()
                    if clave == "VLANS":
                        f.write(f"{clave_fmt}:\n")
                        if isinstance(valor, list) and valor:
                            for v_info in valor: f.write(f"  - ID: {v_info.get('id')}, Nombre: {v_info.get('nombre', 'N/A')}\n")
                        else: f.write("  Ninguna\n")
                    else: f.write(f"{clave_fmt}: {valor_limpio}\n")
                f.write("\n"+("-"*70+"\n\n"))
            f.write("FIN DEL INFORME\n"+"="*70+"\n")
        mostrar_mensaje(f"Datos exportados a '{ruta_completa_archivo_txt}'", "exito")
    except IOError: mostrar_mensaje(f"Error al escribir en '{ruta_completa_archivo_txt}'", "error")
    input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")

# --- Validaciones Específicas ---
def validar_formato_ip(ip_str):
    ip_str = ip_str.strip()
    if not ip_str: raise ValueError("IP no puede estar vacía.")
    if ' ' in ip_str: raise ValueError("IP no debe contener espacios.")
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        if isinstance(ip_obj, ipaddress.IPv4Address):
            octetos = ip_str.split('.'); primer_octeto = int(octetos[0])
            if primer_octeto == 0: raise ValueError("IPv4: 1er octeto no puede ser 0.")
            if primer_octeto == 127: raise ValueError("IPv4: IPs 127.x.x.x reservadas.")
            if primer_octeto >= 224:
                if primer_octeto < 240: raise ValueError("IPv4: IPs 224-239 reservadas (multicast).")
                else: raise ValueError("IPv4: IPs >= 240 reservadas (futuro).")
            if ip_str == "255.255.255.255": raise ValueError("IPv4: IP 255.255.255.255 reservada.")
            return "IPv4"
        elif isinstance(ip_obj, ipaddress.IPv6Address): return "IPv6"
    except ValueError as e: raise ValueError(f"Formato IP incorrecto: {e}")
    return None

def validar_mascara_red_ipv4(mascara_str):
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", mascara_str): raise ValueError("Formato máscara IPv4 X.X.X.X.")
    oct_int = [int(o) for o in mascara_str.split('.')]
    if any(not (0 <= o <= 255) for o in oct_int): raise ValueError("Octetos máscara IPv4 entre 0-255.")
    bin_comp = "".join([bin(o)[2:].zfill(8) for o in oct_int])
    if '01' in bin_comp: raise ValueError("Máscara IPv4 inválida (bits '1' no contiguos).")
    if mascara_str == "0.0.0.0": raise ValueError("Máscara 0.0.0.0 no válida para asignación.")
    return True

def obtener_clase_y_mascara_predeterminada_ipv4(ip_str):
    try: primer_octeto = int(ip_str.split('.')[0])
    except: return None, None
    if 1 <= primer_octeto <= 126: return 'A', '255.0.0.0'
    elif 128 <= primer_octeto <= 191: return 'B', '255.255.0.0'
    elif 192 <= primer_octeto <= 223: return 'C', '255.255.255.0'
    return None, None

def validar_nombre(nombre, dispositivos_existentes=None, id_actual=None):
    if not re.match(r'^[a-zA-Z0-9\-\.\s_]+$', nombre):
        raise ValueError("Nombre: letras, números, espacios, '-', '.' y '_'.")
    if len(nombre) > 50: raise ValueError("Nombre no exceder 50 caracteres.")
    if dispositivos_existentes:
        nombre_lower = nombre.lower()
        for i, disp in enumerate(dispositivos_existentes):
            if i == id_actual: continue # No comparar consigo mismo al editar
            if disp.get("NOMBRE", "").lower() == nombre_lower:
                raise ValueError(f"Nombre '{nombre}' ya existe.")
    return True


def validar_servicios(servicios):
    for s in servicios:
        if s not in SERVICIOS_VALIDOS.values(): raise ValueError(f"Servicio inválido: {s}")
    return True

def validar_vlan_id(vlan_id_str):
    vlan_id_str = vlan_id_str.strip()
    if not vlan_id_str.isdigit(): raise ValueError("ID VLAN debe ser número.")
    vlan_id = int(vlan_id_str)
    if not (VLAN_ID_MIN <= vlan_id <= VLAN_ID_MAX):
        raise ValueError(f"ID VLAN entre {VLAN_ID_MIN}-{VLAN_ID_MAX}.")
    return vlan_id

def validar_vlan_nombre(vlan_nombre_str):
    vlan_nombre_str = vlan_nombre_str.strip()
    if not vlan_nombre_str: return f"VLAN_{VLAN_ID_MIN}" # Nombre por defecto o manejar como error
    if not re.match(r'^[a-zA-Z0-9\-\s_]+$', vlan_nombre_str):
        raise ValueError("Nombre VLAN: letras, números, espacios, '-', '_'.")
    if len(vlan_nombre_str) > 30: raise ValueError("Nombre VLAN no exceder 30 chars.")
    return vlan_nombre_str

# --- Representación de Dispositivos ---
def crear_dispositivo_dict(tipo, nombre, ip=None, mascara_red=None, ip_type=None, capa=None, servicios=None, vlans=None):
    try:
        # La validación de nombre único se hace antes de llamar a esta función si es necesario
        dispositivo_dict = {"TIPO": tipo, "NOMBRE": nombre}
        if ip:
            dispositivo_dict["IP"] = ip; dispositivo_dict["IP_TYPE"] = ip_type
            if mascara_red and ip_type == "IPv4": dispositivo_dict["MÁSCARA"] = mascara_red
        if capa: dispositivo_dict["CAPA"] = capa
        dispositivo_dict["SERVICIOS"] = ' '.join(sorted(list(set(servicios)))) if servicios else "Ninguno"
        dispositivo_dict["VLANS"] = sorted(vlans, key=lambda v: v['id']) if vlans else []
        return dispositivo_dict
    except ValueError as e: mostrar_mensaje(f"Error al crear datos: {e}", "error"); return None


def formatear_dispositivo_para_mostrar(dispositivo_dict, indice=None):
    if not dispositivo_dict: return ""
    header = f"{Color.YELLOW}{str(indice)+'.' if indice else ''}{Color.END} {Color.BOLD}{dispositivo_dict.get('NOMBRE', 'N/A')}{Color.END}"
    lineas = [
        f"{Color.CYAN}🔧 {Color.BOLD}TIPO:{Color.END} {dispositivo_dict.get('TIPO', 'N/A')}",
    ]
    if "IP" in dispositivo_dict:
        ip_type_info = f" ({dispositivo_dict.get('IP_TYPE', '')})" if dispositivo_dict.get('IP_TYPE') else ""
        lineas.append(f"{Color.CYAN}🌍 {Color.BOLD}IP:{Color.END} {dispositivo_dict['IP']}{ip_type_info}")
        if "MÁSCARA" in dispositivo_dict and dispositivo_dict.get('IP_TYPE') == "IPv4":
            lineas.append(f"{Color.CYAN}🌐 {Color.BOLD}MÁSCARA (IPv4):{Color.END} {dispositivo_dict['MÁSCARA']}")
    if "CAPA" in dispositivo_dict: lineas.append(f"{Color.CYAN}📊 {Color.BOLD}CAPA:{Color.END} {dispositivo_dict['CAPA']}")
    lineas.append(f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {dispositivo_dict.get('SERVICIOS', 'Ninguno')}")
    
    vlans_disp = dispositivo_dict.get("VLANS", [])
    vlan_str = "Ninguna"
    if vlans_disp: vlan_str = ", ".join([f"ID:{v['id']}({v.get('nombre','N/A')})" for v in vlans_disp])
    lineas.append(f"{Color.CYAN} VLANs:{Color.END} {vlan_str}")
        
    separador = f"{Color.BLUE}{'═' * 70}{Color.END}"
    return f"\n{header}\n" + "\n".join([f"   {l}" for l in lineas]) + f"\n{separador}"


# --- Generación de Reportes ---
def generar_reporte_estadistico(dispositivos_dicts):
    if not dispositivos_dicts: mostrar_mensaje("⚠️ No hay dispositivos.", "advertencia"); sleep(2); return
    mostrar_progreso("Generando Reporte Estadístico", 1)
    mostrar_titulo("📊 REPORTE ESTADÍSTICO DETALLADO")
    print(f"\n{Color.BOLD}{Color.PURPLE}📌 RESUMEN GENERAL{Color.END}")
    print(f"{Color.CYAN}📅 Total registrados:{Color.END} {len(dispositivos_dicts)}")
    print(f"{Color.CYAN}📅 Reporte generado:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print(f"\n{Color.BOLD}{Color.PURPLE}🔢 DISTRIBUCIÓN POR TIPO:{Color.END}")
    tipos_count = {}
    for d in dispositivos_dicts: tipo = d.get("TIPO", "Desc."); tipos_count[tipo] = tipos_count.get(tipo, 0) + 1
    for tipo, cant in sorted(tipos_count.items(),key=lambda x:x[1],reverse=True):
        print(f"\n   {Color.YELLOW}{tipo.upper()} ({cant} dispositivos):{Color.END}")
        det_cnt=0
        for d in dispositivos_dicts:
            if det_cnt >= 3: break
            if d.get("TIPO") == tipo:
                nombre = d.get("NOMBRE", "N/A"); ip_info = d.get("IP", "Sin IP")
                if "MÁSCARA" in d and d.get("IP_TYPE")=="IPv4": ip_info += f" / {d['MÁSCARA']}"
                print(f"     - {nombre} ({ip_info})"); det_cnt+=1
        if cant > 3: print(f"     {Color.DARKCYAN}...y {cant-3} más{Color.END}")

    print(f"\n{Color.BOLD}{Color.PURPLE}📡 DISTRIBUCIÓN POR CAPA DE RED:{Color.END}")
    capas_count = {}
    for d in dispositivos_dicts: capa = d.get("CAPA","Sin capa"); capas_count[capa] = capas_count.get(capa,0)+1
    for capa, cant in sorted(capas_count.items(),key=lambda x:x[1],reverse=True):
        print(f"\n   {Color.YELLOW}{capa.upper()} ({cant} dispositivos):{Color.END}")
        det_cnt=0
        for d in dispositivos_dicts:
            if det_cnt >= 3: break
            if d.get("CAPA","Sin capa") == capa:
                nombre=d.get("NOMBRE","N/A"); tipo_d=d.get("TIPO","N/A"); servs=d.get("SERVICIOS","Ninguno")
                print(f"     - {nombre} ({tipo_d}) servicios: {servs}"); det_cnt+=1
        if cant > 3: print(f"     {Color.DARKCYAN}...y {cant-3} más{Color.END}")

    print(f"\n{Color.BLUE}{'═'*70}{Color.END}\n{Color.BOLD}{Color.PURPLE}{'📋 LISTADO COMPLETO DE DISPOSITIVOS'.center(70)}{Color.END}\n{Color.BLUE}{'═'*70}{Color.END}")
    for i,d in enumerate(dispositivos_dicts,1): print(formatear_dispositivo_para_mostrar(d, indice=i))
    print(f"\n{Color.BLUE}{'═'*70}{Color.END}\n{Color.BOLD}{Color.GREEN}🎉 Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.END}\n{Color.BLUE}{'═'*70}{Color.END}\n")
    input(f"{Color.GREEN}Presione Enter para volver...{Color.END}")

# --- Funciones de Menú y Selección ---
def mostrar_menu_principal():
    mostrar_titulo("SISTEMA DE GESTIÓN DE DISPOSITIVOS DE RED")
    print(f"{Color.BOLD}{Color.YELLOW}1.{Color.END} 📱 Agregar nuevo dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}2.{Color.END} 📜 Mostrar todos los dispositivos")
    print(f"{Color.BOLD}{Color.YELLOW}3.{Color.END} 🔍 Buscar dispositivo por nombre")
    print(f"{Color.BOLD}{Color.YELLOW}4.{Color.END} ✍️ Editar dispositivo existente") # Nueva Opción Editar
    print(f"{Color.BOLD}{Color.YELLOW}5.{Color.END} ➕ Agregar servicio a dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}6.{Color.END} ➖ Eliminar servicio de dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}7.{Color.END} ⚙️ Gestionar VLANs de dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}8.{Color.END} ❌ Eliminar dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}9.{Color.END} 📊 Generar reporte estadístico")
    print(f"{Color.BOLD}{Color.YELLOW}10.{Color.END} 💾 Exportar datos a archivo TXT")
    print(f"{Color.BOLD}{Color.YELLOW}11.{Color.END} 🚪 Salir")
    print(f"\n{Color.BLUE}{'═'*70}{Color.END}")

def seleccionar_opcion(opciones, titulo, permitir_volver=True, mostrar_actual=None):
    print(f"\n{Color.BOLD}{titulo}{Color.END}")
    if mostrar_actual: print(f"{Color.DARKCYAN}Valor actual: {mostrar_actual}{Color.END}")
    
    op_list = list(opciones.items()) if isinstance(opciones, dict) else opciones
    for i, item in enumerate(op_list, 1):
        val_mostrar = item[1] if isinstance(item, (tuple, list)) and len(item) > 1 else str(item)
        print(f"{Color.YELLOW}{i}.{Color.END} {val_mostrar}")
    if permitir_volver: print(f"{Color.YELLOW}0.{Color.END} Volver / No cambiar / Cancelar")

    while True:
        try:
            max_opc = len(op_list)
            prompt = f"\n{Color.GREEN}↳ Opción (1-{max_opc}{(', 0 volver' if permitir_volver else '')}): {Color.END}"
            op_num_str = input(prompt).strip()
            if permitir_volver and (op_num_str == "0" or (not op_num_str and mostrar_actual is not None)): return "VOLVER" # Permite Enter para no cambiar
            op_num = int(op_num_str)
            if 1 <= op_num <= max_opc:
                sel_item = op_list[op_num-1]
                return sel_item[0] if isinstance(sel_item, (tuple, list)) else sel_item
            mostrar_mensaje(f"Número entre 1-{max_opc}{(', o 0' if permitir_volver else '')}", "error")
        except ValueError: mostrar_mensaje("Entrada inválida. Ingrese número.", "error")


def ingresar_ip_y_mascara(dispositivos_existentes, dispositivo_actual_editando=None):
    # Si dispositivo_actual_editando no es None, estamos en modo edición.
    ip_original = dispositivo_actual_editando.get("IP") if dispositivo_actual_editando else None
    
    ip_final, mascara_final, tipo_ip_final, capa_final_str = \
        dispositivo_actual_editando.get("IP"), \
        dispositivo_actual_editando.get("MÁSCARA"), \
        dispositivo_actual_editando.get("IP_TYPE"), \
        dispositivo_actual_editando.get("CAPA")

    while True:
        prompt_ip = f"{Color.GREEN}↳ IP (IPv4/IPv6) [{ip_final or 'ninguna'}], (vacío no cambia, '-' limpia IP, '0' cancela): {Color.END}"
        ip_str_in = input(prompt_ip).strip()

        if ip_str_in == "0": return "VOLVER_MENU_EDIT", None, None, None # Señal para volver al menú de edición
        if not ip_str_in and dispositivo_actual_editando: # Usuario presionó Enter, no cambia IP
            break # Sale del bucle de IP, los valores actuales se mantienen
        if ip_str_in == "-": # Limpiar IP
            ip_final, mascara_final, tipo_ip_final = None, None, None
            mostrar_mensaje("IP y Máscara eliminadas. Puede seleccionar una capa si es necesario.", "info")
            break # Se limpió, ahora se pedirá capa si es relevante.

        try:
            tipo_ip_validado = validar_formato_ip(ip_str_in)
            # Validar unicidad, excepto si la IP es la original del dispositivo que se está editando
            es_ip_duplicada = False
            for i, disp in enumerate(dispositivos_existentes):
                # Si estamos editando, el 'id' del dispositivo_actual_editando sería su índice en la lista original.
                # Esta validación de unicidad es compleja si el índice no se pasa.
                # Por ahora, asumimos que el nombre es el identificador principal para duplicados.
                # La IP duplicada se maneja de forma más simple:
                if disp.get("IP") == ip_str_in and (not dispositivo_actual_editando or disp.get("IP") != ip_original):
                    es_ip_duplicada = True; break
            if es_ip_duplicada:
                mostrar_mensaje(f"Error: IP ({ip_str_in}) ya en uso por otro dispositivo.", "error"); continue
            
            ip_final = ip_str_in # IP validada y no duplicada (o es la original)
            tipo_ip_final = tipo_ip_validado
            
            # Si la IP cambió o era nula, se debe pedir máscara (si IPv4) y capa
            if tipo_ip_final == "IPv4":
                while True:
                    mascara_actual_str = mascara_final or "ninguna"
                    mascara_str_in = input(f"{Color.GREEN}↳ Máscara red para {Color.CYAN}{ip_final}{Color.END} [{mascara_actual_str}] (vacío no cambia, '0' cancela IP): {Color.END}").strip()
                    if mascara_str_in == "0": ip_final = None; tipo_ip_final = None; break # Cancela IP
                    if not mascara_str_in and mascara_final: break # No cambia máscara
                    if not mascara_str_in and not mascara_final: mostrar_mensaje("Máscara obligatoria para IPv4 nueva.", "error"); continue
                    
                    try:
                        validar_mascara_red_ipv4(mascara_str_in)
                        mascara_final = mascara_str_in
                        break # Máscara válida
                    except ValueError as e_mask:
                        mostrar_mensaje(str(e_mask), "error")
                        _, sug_mask = obtener_clase_y_mascara_predeterminada_ipv4(ip_final)
                        if sug_mask: print(f"{Color.YELLOW}ℹ️ Máscara común para {ip_final}: {sug_mask}.{Color.END}")
                if ip_final is None: continue # Se canceló la IP desde la máscara
            
            elif tipo_ip_final == "IPv6":
                mostrar_mensaje(f"No se requiere máscara para IPv6 ({ip_final}).", "info")
                mascara_final = None # Asegurar que no haya máscara para IPv6
            
            # Preguntar por la capa siempre que se haya procesado una IP o se haya limpiado
            print(f"\n{Color.CYAN}--- Selección Capa de Red ---{Color.END}")
            capa_key_sel = seleccionar_opcion(CAPAS_RED, "📌 Capa de red:", mostrar_actual=capa_final_str)
            if capa_key_sel != "VOLVER": capa_final_str = CAPAS_RED[capa_key_sel]
            
            break # Configuración de IP/Máscara/Capa completada o no cambiada

        except ValueError as e_ip:
            mostrar_mensaje(str(e_ip), "error")
            print(f"\n{Color.YELLOW}💡 IPs válidas: IPv4 (192.168.1.1), IPv6 (2001:db8::1){Color.END}")
        
        if input(f"{Color.GREEN}¿Reintentar IP? (s/n): {Color.END}").strip().lower() != 's':
            # Si no se reintenta, y estamos editando, devolvemos los valores originales que tenía el dispositivo
            if dispositivo_actual_editando:
                return dispositivo_actual_editando.get("IP"), \
                       dispositivo_actual_editando.get("MÁSCARA"), \
                       dispositivo_actual_editando.get("IP_TYPE"), \
                       dispositivo_actual_editando.get("CAPA")
            else: # Creando nuevo
                return "VOLVER_MENU_EDIT", None, None, None # O VOLVER_MENU_PRINCIPAL si es creación

    return ip_final, mascara_final, tipo_ip_final, capa_final_str


# --- Funciones Principales de Gestión ---
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
            validar_nombre(nombre_in, dispositivos_actuales) # Valida unicidad aquí
            nombre_disp = nombre_in; break
        except ValueError as e: mostrar_mensaje(str(e), "error")

    ip_disp, mask_disp, ip_type_disp, capa_disp_str = None, None, None, None
    print(f"\n{Color.CYAN}--- Config. Red para: {tipo_sel_str} ({nombre_disp}) ---{Color.END}")
    # Para agregar, no pasamos dispositivo_actual_editando
    ip_disp, mask_disp, ip_type_disp, capa_disp_str = ingresar_ip_y_mascara(dispositivos_actuales, None) 
    if ip_disp == "VOLVER_MENU_EDIT": return None # En creación, esto significa cancelar

    msg_ip_capa = ""
    if ip_disp:
        msg_ip_capa = f"IP {Color.YELLOW}{ip_disp}{Color.END} ({ip_type_disp})"
        if mask_disp and ip_type_disp == "IPv4": msg_ip_capa += f", Máscara {Color.YELLOW}{mask_disp}{Color.END}"
    if capa_disp_str: msg_ip_capa += f", Capa: {Color.YELLOW}{capa_disp_str}{Color.END}"
    if msg_ip_capa: mostrar_mensaje(f"{msg_ip_capa} procesada.", "exito")
    else: mostrar_mensaje(f"No se configuró IP/Capa para {nombre_disp}.", "info")
    sleep(1)

    servicios_disp_list = []
    if tipo_sel_key in TIPOS_CON_SERVICIOS:
        mostrar_titulo(f"SERVICIOS PARA: {nombre_disp}")
        serv_copia = SERVICIOS_VALIDOS.copy()
        while True:
            print(f"\n{Color.CYAN}Servicios: {Color.END}{', '.join(servicios_disp_list) or 'Ninguno'}")
            serv_menu = {k:v for k,v in serv_copia.items() if v not in servicios_disp_list}
            if not serv_menu: mostrar_mensaje("Todos servicios agregados.", "info"); break
            serv_eleg_key = seleccionar_opcion(serv_menu, "Seleccione servicio ('0' finaliza):")
            if serv_eleg_key == "VOLVER": break
            servicios_disp_list.append(serv_menu[serv_eleg_key])
            mostrar_mensaje(f"Servicio {serv_menu[serv_eleg_key]} agregado.", "exito"); sleep(0.5)

    vlans_disp_list = []
    if tipo_sel_key in TIPOS_CON_VLANS:
        mostrar_titulo(f"VLANS PARA: {nombre_disp}")
        if input(f"{Color.GREEN}¿Añadir VLANs? (s/n): {Color.END}").strip().lower() == 's':
            while True:
                print(f"\n{Color.CYAN}VLANs: {Color.END}")
                if vlans_disp_list:
                    for v in vlans_disp_list: print(f"  - ID:{v['id']}, Nombre:{v['nombre']}")
                else: print("  Ninguna")
                try:
                    v_id_str = input(f"{Color.GREEN}↳ ID VLAN ({VLAN_ID_MIN}-{VLAN_ID_MAX}, '0' termina): {Color.END}").strip()
                    if v_id_str == '0': break
                    v_id = validar_vlan_id(v_id_str)
                    if any(v['id']==v_id for v in vlans_disp_list):
                        mostrar_mensaje(f"Error: VLAN ID {v_id} ya existe.", "error"); continue
                    v_nom_str = input(f"{Color.GREEN}↳ Nombre VLAN {v_id} (opcional): {Color.END}").strip()
                    v_nom = validar_vlan_nombre(v_nom_str) if v_nom_str else f"VLAN_{v_id}"
                    vlans_disp_list.append({"id":v_id, "nombre":v_nom})
                    mostrar_mensaje(f"VLAN ID:{v_id}, Nombre:{v_nom} agregada.", "exito")
                except ValueError as e: mostrar_mensaje(str(e), "error")
                if input(f"{Color.GREEN}¿Otra VLAN? (s/n): {Color.END}").lower()!='s': break
    
    nuevo_dict = crear_dispositivo_dict(tipo_sel_str,nombre_disp,ip_disp,mask_disp,ip_type_disp,capa_disp_str,servicios_disp_list,vlans_disp_list)
    if nuevo_dict:
        mostrar_mensaje(f"Dispositivo '{nombre_disp}' creado.", "exito")
        print(formatear_dispositivo_para_mostrar(nuevo_dict))
        input(f"{Color.GREEN}Presione Enter para guardar...{Color.END}")
        mostrar_progreso("Guardando",0.5); return nuevo_dict
    mostrar_mensaje("Creación cancelada/fallida.","advertencia");sleep(2);return None


def editar_dispositivo_interactivo(indice_dispositivo, dispositivos_actuales):
    dispositivo_original = dispositivos_actuales[indice_dispositivo]
    # Crear una copia profunda para editar, y solo actualizar el original si se guardan cambios
    import copy
    disp_edit = copy.deepcopy(dispositivo_original)
    
    nombre_original_para_validacion = disp_edit.get("NOMBRE")


    while True:
        mostrar_titulo(f"EDITANDO DISPOSITIVO: {disp_edit.get('NOMBRE')}")
        print(f"{Color.DARKCYAN}Valores actuales:{Color.END}")
        print(formatear_dispositivo_para_mostrar(disp_edit))

        print(f"{Color.YELLOW}1.{Color.END} Editar Nombre")
        print(f"{Color.YELLOW}2.{Color.END} Editar Tipo")
        print(f"{Color.YELLOW}3.{Color.END} Editar IP, Máscara y Capa de Red")
        print(f"{Color.YELLOW}4.{Color.END} Gestionar Servicios")
        print(f"{Color.YELLOW}5.{Color.END} Gestionar VLANs")
        print(f"{Color.YELLOW}---{Color.END}")
        print(f"{Color.YELLOW}8.{Color.END} Guardar Cambios y Salir")
        print(f"{Color.YELLOW}9.{Color.END} Descartar Cambios y Salir")
        print(f"{Color.YELLOW}0.{Color.END} Salir sin guardar (si no hubo cambios previos)")


        opc_edit = input(f"\n{Color.GREEN}↳ Seleccione atributo a editar: {Color.END}").strip()

        if opc_edit == '1': # Editar Nombre
            nuevo_nombre = input(f"{Color.GREEN}↳ Nuevo nombre [{disp_edit.get('NOMBRE')}]: {Color.END}").strip()
            if nuevo_nombre and nuevo_nombre != disp_edit.get('NOMBRE'):
                try:
                    # Pasar el índice del dispositivo actual para que la validación de nombre único lo ignore
                    validar_nombre(nuevo_nombre, dispositivos_actuales, indice_dispositivo)
                    disp_edit['NOMBRE'] = nuevo_nombre
                    mostrar_mensaje("Nombre actualizado.", "exito")
                except ValueError as e:
                    mostrar_mensaje(str(e), "error")
                sleep(1)

        elif opc_edit == '2': # Editar Tipo
            tipo_actual_str = disp_edit.get('TIPO')
            tipo_actual_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == tipo_actual_str), None)
            
            nuevo_tipo_key = seleccionar_opcion(TIPOS_DISPOSITIVO, "Seleccione nuevo tipo:", mostrar_actual=tipo_actual_str)
            if nuevo_tipo_key != "VOLVER" and nuevo_tipo_key != tipo_actual_key:
                disp_edit['TIPO'] = TIPOS_DISPOSITIVO[nuevo_tipo_key]
                mostrar_mensaje(f"Tipo actualizado a {disp_edit['TIPO']}.", "exito")
                # Advertir si el nuevo tipo no soporta servicios/VLANs que el dispositivo ya tiene
                if tipo_actual_key in TIPOS_CON_SERVICIOS and nuevo_tipo_key not in TIPOS_CON_SERVICIOS and disp_edit.get("SERVICIOS","Ninguno") != "Ninguno":
                    mostrar_mensaje(f"Advertencia: El nuevo tipo '{disp_edit['TIPO']}' podría no ser compatible con los servicios existentes. Revise la configuración de servicios.", "advertencia")
                if tipo_actual_key in TIPOS_CON_VLANS and nuevo_tipo_key not in TIPOS_CON_VLANS and disp_edit.get("VLANS"):
                     mostrar_mensaje(f"Advertencia: El nuevo tipo '{disp_edit['TIPO']}' podría no ser compatible con las VLANs existentes. Revise la configuración de VLANs.", "advertencia")
                sleep(2)


        elif opc_edit == '3': # Editar IP, Máscara, Capa
            # Pasar disp_edit para que ingr_ip_y_mask sepa que está editando
            ip_n, mask_n, ip_type_n, capa_n = ingresar_ip_y_mascara(dispositivos_actuales, disp_edit)
            if ip_n != "VOLVER_MENU_EDIT": # Si no se canceló desde la función de IP
                disp_edit['IP'] = ip_n
                disp_edit['MÁSCARA'] = mask_n
                disp_edit['IP_TYPE'] = ip_type_n
                disp_edit['CAPA'] = capa_n
                mostrar_mensaje("Configuración de red actualizada (si hubo cambios).", "info")
                sleep(1)


        elif opc_edit == '4': # Gestionar Servicios
            tipo_disp_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == disp_edit.get("TIPO")), None)
            if tipo_disp_key not in TIPOS_CON_SERVICIOS:
                mostrar_mensaje(f"El tipo '{disp_edit.get('TIPO')}' no admite servicios.", "advertencia"); sleep(2); continue

            serv_actuales_list = [s.strip() for s in disp_edit.get("SERVICIOS", "Ninguno").split(' ') if s.strip() and s != "Ninguno"]
            while True:
                mostrar_titulo(f"GESTIONAR SERVICIOS DE: {disp_edit.get('NOMBRE')}")
                print(f"{Color.CYAN}Servicios actuales: {Color.END}{', '.join(serv_actuales_list) or 'Ninguno'}")
                print(f"{Color.YELLOW}1.{Color.END} Añadir Servicio")
                print(f"{Color.YELLOW}2.{Color.END} Eliminar Servicio")
                print(f"{Color.YELLOW}0.{Color.END} Terminar gestión de servicios")
                opc_serv = input(f"\n{Color.GREEN}↳ Opción: {Color.END}").strip()

                if opc_serv == '1': #Añadir
                    serv_menu = {k:v for k,v in SERVICIOS_VALIDOS.items() if v not in serv_actuales_list}
                    if not serv_menu: mostrar_mensaje("Todos los servicios aplicables ya están añadidos.", "info"); sleep(1); continue
                    serv_key_add = seleccionar_opcion(serv_menu, "Seleccione servicio a añadir:")
                    if serv_key_add != "VOLVER":
                        serv_actuales_list.append(SERVICIOS_VALIDOS[serv_key_add])
                        disp_edit["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales_list))))
                        mostrar_mensaje(f"Servicio {SERVICIOS_VALIDOS[serv_key_add]} añadido.", "exito")
                elif opc_serv == '2': #Eliminar
                    if not serv_actuales_list: mostrar_mensaje("No hay servicios para eliminar.", "info"); sleep(1); continue
                    serv_menu_del = {s:s for s in serv_actuales_list} # valor:valor
                    serv_val_del = seleccionar_opcion(serv_menu_del, "Seleccione servicio a eliminar:")
                    if serv_val_del != "VOLVER":
                        serv_actuales_list.remove(serv_val_del)
                        disp_edit["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales_list)))) if serv_actuales_list else "Ninguno"
                        mostrar_mensaje(f"Servicio {serv_val_del} eliminado.", "exito")
                elif opc_serv == '0': break
                else: mostrar_mensaje("Opción inválida.", "error")
                sleep(1)


        elif opc_edit == '5': # Gestionar VLANs
            tipo_disp_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == disp_edit.get("TIPO")), None)
            if tipo_disp_key not in TIPOS_CON_VLANS:
                mostrar_mensaje(f"El tipo '{disp_edit.get('TIPO')}' no admite VLANs.", "advertencia"); sleep(2); continue
            
            vlans_actuales_list = disp_edit.get("VLANS", []) # Lista de dicts
            while True:
                mostrar_titulo(f"GESTIONAR VLANS DE: {disp_edit.get('NOMBRE')}")
                print(f"{Color.CYAN}VLANs actuales:{Color.END}")
                if vlans_actuales_list:
                    for i, v_info in enumerate(vlans_actuales_list,1): print(f"  {i}. ID:{v_info['id']}, Nombre:{v_info.get('nombre','N/A')}")
                else: print("  Ninguna.")
                print(f"{Color.YELLOW}1.{Color.END} Añadir VLAN")
                print(f"{Color.YELLOW}2.{Color.END} Eliminar VLAN")
                print(f"{Color.YELLOW}0.{Color.END} Terminar gestión de VLANs")
                opc_vlan = input(f"\n{Color.GREEN}↳ Opción: {Color.END}").strip()

                if opc_vlan == '1': #Añadir
                    try:
                        v_id_str = input(f"{Color.GREEN}↳ ID VLAN ({VLAN_ID_MIN}-{VLAN_ID_MAX}): {Color.END}").strip()
                        v_id = validar_vlan_id(v_id_str)
                        if any(v['id']==v_id for v in vlans_actuales_list): mostrar_mensaje(f"VLAN ID {v_id} ya existe.", "error"); continue
                        v_nom_str = input(f"{Color.GREEN}↳ Nombre VLAN {v_id} (opcional): {Color.END}").strip()
                        v_nom = validar_vlan_nombre(v_nom_str) if v_nom_str else f"VLAN_{v_id}"
                        vlans_actuales_list.append({"id":v_id, "nombre":v_nom})
                        disp_edit["VLANS"] = sorted(vlans_actuales_list, key=lambda x: x['id'])
                        mostrar_mensaje(f"VLAN ID:{v_id}, Nombre:{v_nom} añadida.", "exito")
                    except ValueError as e: mostrar_mensaje(str(e), "error")
                elif opc_vlan == '2': #Eliminar
                    if not vlans_actuales_list: mostrar_mensaje("No hay VLANs para eliminar.", "info"); continue
                    vlan_menu_del = [(idx, f"ID:{v['id']}, Nombre:{v.get('nombre','N/A')}") for idx,v in enumerate(vlans_actuales_list)]
                    idx_vlan_del_sel = seleccionar_opcion(vlan_menu_del, "Seleccione VLAN a eliminar:")
                    if idx_vlan_del_sel != "VOLVER":
                        v_elim = vlans_actuales_list.pop(idx_vlan_del_sel)
                        disp_edit["VLANS"] = vlans_actuales_list # Ya está ordenada
                        mostrar_mensaje(f"VLAN ID:{v_elim['id']} eliminada.", "exito")
                elif opc_vlan == '0': break
                else: mostrar_mensaje("Opción inválida.", "error")
                sleep(1)

        elif opc_edit == '8': # Guardar Cambios
            # Antes de guardar, validar el nombre contra la lista original, excluyendo el índice actual
            try:
                validar_nombre(disp_edit.get("NOMBRE"), dispositivos_actuales, indice_dispositivo)
                dispositivos_actuales[indice_dispositivo] = disp_edit # Actualiza el dispositivo en la lista principal
                guardar_datos_json(dispositivos_actuales)
                mostrar_mensaje("Cambios guardados exitosamente.", "exito")
                sleep(1.5)
                return True # Indica que se guardó
            except ValueError as e: # Error de validación de nombre duplicado al intentar guardar
                mostrar_mensaje(f"Error al guardar: {str(e)}. Por favor, edite el nombre.", "error")
                sleep(2)
                # No salir, permitir al usuario corregir el nombre.
            

        elif opc_edit == '9': # Descartar Cambios
            mostrar_mensaje("Cambios descartados.", "info"); sleep(1.5); return False # No se guardó
        
        elif opc_edit == '0': # Salir sin guardar (si no hubo cambios)
            if disp_edit == dispositivo_original:
                 mostrar_mensaje("No hubo cambios. Saliendo.", "info"); sleep(1.5); return False
            else:
                 mostrar_mensaje("Hay cambios sin guardar. Use 'Guardar' o 'Descartar'.", "advertencia"); sleep(1.5)
        else:
            mostrar_mensaje("Opción de edición inválida.", "error"); sleep(1)

def mostrar_dispositivos(dispositivos_dicts, titulo="LISTADO DE DISPOSITIVOS"):
    mostrar_progreso("Cargando listado", 0.5)
    mostrar_titulo(titulo)
    if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos.", "advertencia")
    else:
        for i, d_dict in enumerate(dispositivos_dicts, 1):
            print(formatear_dispositivo_para_mostrar(d_dict, indice=i))
    input(f"\n{Color.GREEN}Presione Enter para volver...{Color.END}")

def buscar_dispositivo(dispositivos_dicts):
    mostrar_progreso("Iniciando búsqueda",0.2); mostrar_titulo("BUSCAR DISPOSITIVO")
    if not dispositivos_dicts: mostrar_mensaje("No hay dispositivos.", "advertencia"); sleep(2); return
    n_bus = input(f"{Color.GREEN}↳ Nombre (o parte) ('0' volver): {Color.END}").strip().lower()
    if n_bus=="0":return
    if not n_bus: mostrar_mensaje("Término de búsqueda vacío.","error");sleep(2);return
    mostrar_progreso(f"Buscando '{n_bus}'",0.5)
    enc = [d for d in dispositivos_dicts if n_bus in d.get("NOMBRE","").lower()]
    if enc: mostrar_dispositivos(enc, f"RESULTADOS PARA '{n_bus.upper()}'")
    else: mostrar_mensaje(f"No se encontraron coincidencias para '{n_bus}'.","advertencia");sleep(2)

def seleccionar_dispositivo_para_accion(dispositivos_dicts, accion_str, filtro_tipo=None):
    """Función genérica para seleccionar un dispositivo."""
    if not dispositivos_dicts:
        mostrar_mensaje("No hay dispositivos registrados.", "advertencia"); sleep(2); return None

    candidatos = []
    for i, d in enumerate(dispositivos_dicts):
        tipo_key_actual = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == d.get("TIPO")), None)
        if filtro_tipo is None or (tipo_key_actual and tipo_key_actual in filtro_tipo):
            candidatos.append({"indice_original": i, "nombre": d.get("NOMBRE", "N/A"), "tipo": d.get("TIPO", "N/A"), "objeto": d})
    
    if not candidatos:
        msg = "No hay dispositivos."
        if filtro_tipo: msg = f"No hay dispositivos del tipo adecuado ({', '.join(filtro_tipo)}) para esta acción."
        mostrar_mensaje(msg, "advertencia"); sleep(2); return None

    print(f"{Color.BOLD}📋 Dispositivos disponibles para {accion_str}:{Color.END}")
    opciones_menu = [(info["indice_original"], f"{info['nombre']} ({info['tipo']})") for info in candidatos]
    
    indice_real_seleccionado = seleccionar_opcion(opciones_menu, f"Seleccione el dispositivo para {accion_str}:")
    if indice_real_seleccionado == "VOLVER": return None
    return indice_real_seleccionado # Devuelve el índice en la lista original 'dispositivos_dicts'


def agregar_servicio_dispositivo(dispositivos_dicts):
    mostrar_titulo("AGREGAR SERVICIO A DISPOSITIVO")
    indice_disp_sel = seleccionar_dispositivo_para_accion(dispositivos_dicts, "agregar servicio", TIPOS_CON_SERVICIOS)
    if indice_disp_sel is None: return

    disp_mod = dispositivos_dicts[indice_disp_sel]
    nombre_disp = disp_mod.get("NOMBRE")
    mostrar_titulo(f"AGREGAR SERVICIO A: {nombre_disp}")
    serv_actuales = [s.strip() for s in disp_mod.get("SERVICIOS","Ninguno").split(' ') if s.strip() and s!="Ninguno"]
    serv_disp_menu = {k:v for k,v in SERVICIOS_VALIDOS.items() if v not in serv_actuales}

    if not serv_disp_menu: mostrar_mensaje("Todos servicios ya están asignados.", "info"); sleep(2); return
    print(f"{Color.CYAN}Servicios en '{nombre_disp}': {Color.END}{', '.join(serv_actuales) or 'Ninguno'}")
    serv_key_add = seleccionar_opcion(serv_disp_menu, "Seleccione servicio a agregar:")
    if serv_key_add == "VOLVER": return
    
    serv_actuales.append(SERVICIOS_VALIDOS[serv_key_add])
    disp_mod["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales))))
    guardar_datos_json(dispositivos_dicts)
    mostrar_mensaje(f"Servicio '{SERVICIOS_VALIDOS[serv_key_add]}' agregado a '{nombre_disp}'.", "exito")
    print(formatear_dispositivo_para_mostrar(disp_mod)); input(f"{Color.GREEN}Enter...{Color.END}")


def eliminar_servicio_dispositivo(dispositivos_dicts):
    mostrar_titulo("ELIMINAR SERVICIO DE DISPOSITIVO")
    indice_disp_sel = seleccionar_dispositivo_para_accion(dispositivos_dicts, "eliminar servicio", TIPOS_CON_SERVICIOS)
    if indice_disp_sel is None: return

    disp_mod = dispositivos_dicts[indice_disp_sel]
    nombre_disp = disp_mod.get("NOMBRE")
    serv_actuales = [s.strip() for s in disp_mod.get("SERVICIOS","").split(' ') if s.strip() and s!="Ninguno"]
    if not serv_actuales: mostrar_mensaje(f"'{nombre_disp}' no tiene servicios para eliminar.","info");sleep(2);return

    mostrar_titulo(f"ELIMINAR SERVICIO DE: {nombre_disp}")
    print(f"{Color.CYAN}Servicios en '{nombre_disp}': {Color.END}{', '.join(serv_actuales)}")
    serv_elim_menu = {s:s for s in serv_actuales}
    serv_val_del = seleccionar_opcion(serv_elim_menu, "Seleccione servicio a eliminar:")
    if serv_val_del == "VOLVER": return

    serv_actuales.remove(serv_val_del)
    disp_mod["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales)))) if serv_actuales else "Ninguno"
    guardar_datos_json(dispositivos_dicts)
    mostrar_mensaje(f"Servicio '{serv_val_del}' eliminado de '{nombre_disp}'.", "exito")
    print(formatear_dispositivo_para_mostrar(disp_mod)); input(f"{Color.GREEN}Enter...{Color.END}")

def gestionar_vlans_dispositivo(dispositivos_dicts):
    mostrar_titulo("GESTIONAR VLANS DE DISPOSITIVO")
    indice_disp_sel = seleccionar_dispositivo_para_accion(dispositivos_dicts, "gestionar VLANs", TIPOS_CON_VLANS)
    if indice_disp_sel is None: return

    disp_mod = dispositivos_dicts[indice_disp_sel]
    nombre_disp = disp_mod.get("NOMBRE")

    while True:
        mostrar_titulo(f"GESTIONAR VLANS PARA: {nombre_disp}")
        vlans_actuales = disp_mod.get("VLANS", [])
        print(f"{Color.CYAN}VLANs en '{nombre_disp}':{Color.END}")
        if vlans_actuales:
            for i,v_info in enumerate(vlans_actuales,1): print(f"  {i}. ID:{v_info['id']}, Nombre:{v_info.get('nombre','N/A')}")
        else: print("  Ninguna VLAN.")
        
        print(f"\n{Color.YELLOW}1.Añadir{Color.END} {Color.YELLOW}2.Eliminar{Color.END} {Color.YELLOW}0.Volver{Color.END}")
        opc_v = input(f"\n{Color.GREEN}↳ Opción VLANs: {Color.END}").strip()

        if opc_v=='1':
            try:
                v_id_str=input(f"{Color.GREEN}↳ ID VLAN ({VLAN_ID_MIN}-{VLAN_ID_MAX}): {Color.END}").strip()
                v_id = validar_vlan_id(v_id_str)
                if any(v['id']==v_id for v in vlans_actuales): mostrar_mensaje(f"VLAN ID {v_id} ya existe.","error");continue
                v_nom_str=input(f"{Color.GREEN}↳ Nombre VLAN {v_id} (opc): {Color.END}").strip()
                v_nom=validar_vlan_nombre(v_nom_str) if v_nom_str else f"VLAN_{v_id}"
                vlans_actuales.append({"id":v_id,"nombre":v_nom})
                disp_mod["VLANS"]=sorted(vlans_actuales,key=lambda x:x['id'])
                guardar_datos_json(dispositivos_dicts)
                mostrar_mensaje(f"VLAN ID:{v_id}, Nombre:{v_nom} añadida.","exito")
            except ValueError as e: mostrar_mensaje(str(e),"error")
        elif opc_v=='2':
            if not vlans_actuales: mostrar_mensaje("No hay VLANs para eliminar.","info");continue
            v_menu_del=[(idx,f"ID:{v['id']},Nombre:{v.get('nombre','N/A')}") for idx,v in enumerate(vlans_actuales)]
            idx_v_del=seleccionar_opcion(v_menu_del,"VLAN a eliminar:")
            if idx_v_del != "VOLVER":
                v_elim=vlans_actuales.pop(idx_v_del)
                disp_mod["VLANS"]=vlans_actuales
                guardar_datos_json(dispositivos_dicts)
                mostrar_mensaje(f"VLAN ID:{v_elim['id']} eliminada.","exito")
        elif opc_v=='0': break
        else: mostrar_mensaje("Opción VLAN inválida.","error")
        sleep(1)


def eliminar_dispositivo(dispositivos_dicts):
    mostrar_titulo("ELIMINAR DISPOSITIVO")
    indice_disp_sel = seleccionar_dispositivo_para_accion(dispositivos_dicts, "eliminar")
    if indice_disp_sel is None: return

    disp_elim = dispositivos_dicts[indice_disp_sel]
    nombre_elim = disp_elim.get("NOMBRE", f"Disp #{indice_disp_sel+1}")
    print(f"\n{Color.RED}{'⚠'*30} CONFIRMACIÓN {'⚠'*30}{Color.END}")
    confirmar=input(f"{Color.RED}{Color.BOLD}¿SEGURO eliminar '{nombre_elim}'? (S/N): {Color.END}").strip().upper()
    print(f"{Color.RED}{'⚠'*(60+len(' CONFIRMACIÓN '))}{Color.END}")
    if confirmar=='S':
        mostrar_progreso(f"Eliminando '{nombre_elim}'",1)
        dispositivos_dicts.pop(indice_disp_sel)
        guardar_datos_json(dispositivos_dicts)
        mostrar_mensaje(f"'{nombre_elim}' eliminado.","exito");sleep(2)
        if not dispositivos_dicts: mostrar_mensaje("Todos dispositivos eliminados.","info");sleep(2);return
    elif confirmar=='N': mostrar_mensaje("Eliminación cancelada.","info");sleep(2)
    else: mostrar_mensaje("Opción inválida (S/N).","error");sleep(2)

# --- Sistema de Inicio de Sesión ---
def pantalla_login():
    intentos=0;max_i=3
    while intentos<max_i:
        mostrar_titulo("INICIO DE SESIÓN")
        usr=input(f"{Color.GREEN}👤 Usuario: {Color.END}").strip()
        try: import getpass; pwd=getpass.getpass(f"{Color.GREEN}🔑 Contraseña: {Color.END}").strip()
        except ImportError: pwd=input(f"{Color.GREEN}🔑 Contraseña (visible): {Color.END}").strip()
        if usr in USUARIOS_PERMITIDOS and USUARIOS_PERMITIDOS[usr]==pwd:
            mostrar_progreso(f"Acceso concedido. Bienvenido {usr}!",1);return True
        intentos+=1;restantes=max_i-intentos
        if restantes>0: mostrar_mensaje(f"Incorrecto.{restantes} {'intento' if restantes==1 else 'intentos'} restantes.","error");sleep(1.5)
        else: mostrar_mensaje("Demasiados intentos. Cerrando.","error");sleep(3);return False
    return False

# --- Función Principal (main) ---
def main():
    dispositivos = cargar_datos_json()
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Color.GREEN}↳ Opción (1-11): {Color.END}").strip()
        mostrar_progreso("Procesando", 0.2)
        if opcion == "1":
            nuevo_d = agregar_dispositivo_interactivo(dispositivos)
            if nuevo_d: dispositivos.append(nuevo_d); guardar_datos_json(dispositivos)
        elif opcion == "2": mostrar_dispositivos(dispositivos)
        elif opcion == "3": buscar_dispositivo(dispositivos)
        elif opcion == "4": # Editar dispositivo
            indice_a_editar = seleccionar_dispositivo_para_accion(dispositivos, "editar")
            if indice_a_editar is not None:
                editar_dispositivo_interactivo(indice_a_editar, dispositivos) # La función guarda si hay cambios
        elif opcion == "5": agregar_servicio_dispositivo(dispositivos)
        elif opcion == "6": eliminar_servicio_dispositivo(dispositivos)
        elif opcion == "7": gestionar_vlans_dispositivo(dispositivos)
        elif opcion == "8": eliminar_dispositivo(dispositivos)
        elif opcion == "9": generar_reporte_estadistico(dispositivos)
        elif opcion == "10": exportar_a_txt(dispositivos)
        elif opcion == "11":
            mostrar_mensaje("Guardando datos...", "info"); guardar_datos_json(dispositivos)
            mostrar_progreso("Saliendo",1); mostrar_mensaje("¡Hasta pronto! 👋","info");sleep(1);limpiar_pantalla();break
        else: mostrar_mensaje("Opción inválida (1-11).","error");sleep(2)

if __name__ == "__main__":
    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═'*70}{Color.END}\n{Color.BOLD}{Color.PURPLE}{'BIENVENIDO AL SISTEMA AVANZADO DE GESTIÓN DE RED'.center(70)}{Color.END}\n{Color.BLUE}{'═'*70}{Color.END}\n")
    sleep(1.5)
    if pantalla_login(): main()
    else: limpiar_pantalla();print(f"{Color.RED}{Color.BOLD}Acceso denegado.{Color.END}");sleep(2);limpiar_pantalla()