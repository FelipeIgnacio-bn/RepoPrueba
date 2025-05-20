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

def validar_nombre(nombre, dispositivos_existentes=None, id_actual=None): # id_actual es el índice del dispositivo que se edita
    nombre = nombre.strip()
    if not nombre: raise ValueError("El nombre no puede estar vacío.")
    if not re.match(r'^[a-zA-Z0-9\-\.\s_]+$', nombre):
        raise ValueError("Nombre: letras, números, espacios, '-', '.' y '_'.")
    if len(nombre) > 50: raise ValueError("Nombre no exceder 50 caracteres.")
    if dispositivos_existentes:
        nombre_lower = nombre.lower()
        for i, disp in enumerate(dispositivos_existentes):
            if i == id_actual: continue # No comparar consigo mismo al editar
            if disp.get("NOMBRE", "").lower() == nombre_lower:
                raise ValueError(f"Nombre '{nombre}' ya existe en otro dispositivo.")
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
    if not vlan_nombre_str: return f"VLAN_{VLAN_ID_MIN}" 
    if not re.match(r'^[a-zA-Z0-9\-\s_]+$', vlan_nombre_str):
        raise ValueError("Nombre VLAN: letras, números, espacios, '-', '_'.")
    if len(vlan_nombre_str) > 30: raise ValueError("Nombre VLAN no exceder 30 chars.")
    return vlan_nombre_str

# --- Representación de Dispositivos ---
def crear_dispositivo_dict(tipo, nombre, ip=None, mascara_red=None, ip_type=None, capa=None, servicios=None, vlans=None):
    dispositivo_dict = {"TIPO": tipo, "NOMBRE": nombre}
    if ip:
        dispositivo_dict["IP"] = ip; dispositivo_dict["IP_TYPE"] = ip_type
        if mascara_red and ip_type == "IPv4": dispositivo_dict["MÁSCARA"] = mascara_red
    if capa: dispositivo_dict["CAPA"] = capa
    dispositivo_dict["SERVICIOS"] = ' '.join(sorted(list(set(servicios)))) if servicios else "Ninguno"
    dispositivo_dict["VLANS"] = sorted(vlans, key=lambda v: v['id']) if vlans else []
    return dispositivo_dict


def formatear_dispositivo_para_mostrar(dispositivo_dict, indice=None):
    if not dispositivo_dict: return ""
    header_parts = []
    if indice is not None: header_parts.append(f"{Color.YELLOW}{str(indice)}.{Color.END}")
    header_parts.append(f"{Color.BOLD}{dispositivo_dict.get('NOMBRE', 'N/A')}{Color.END}")
    header = " ".join(header_parts)
    
    lineas = [ f"   {Color.CYAN}🔧 {Color.BOLD}TIPO:{Color.END} {dispositivo_dict.get('TIPO', 'N/A')}"]
    
    current_ip = dispositivo_dict.get('IP')
    current_mask = dispositivo_dict.get('MÁSCARA')
    current_ip_type = dispositivo_dict.get('IP_TYPE')
    current_capa = dispositivo_dict.get('CAPA')

    if current_ip:
        ip_type_info = f" ({current_ip_type})" if current_ip_type else ""
        lineas.append(f"   {Color.CYAN}🌍 {Color.BOLD}IP:{Color.END} {current_ip}{ip_type_info}")
        if current_mask and current_ip_type == "IPv4":
            lineas.append(f"   {Color.CYAN}🌐 {Color.BOLD}MÁSCARA (IPv4):{Color.END} {current_mask}")
    else:
        lineas.append(f"   {Color.CYAN}🌍 {Color.BOLD}IP:{Color.END} No asignada")


    if current_capa:
        lineas.append(f"   {Color.CYAN}📊 {Color.BOLD}CAPA:{Color.END} {current_capa}")
    else:
        lineas.append(f"   {Color.CYAN}📊 {Color.BOLD}CAPA:{Color.END} No asignada")

    lineas.append(f"   {Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {dispositivo_dict.get('SERVICIOS', 'Ninguno')}")
    
    vlans_disp = dispositivo_dict.get("VLANS", [])
    vlan_str = "Ninguna"
    if vlans_disp: vlan_str = ", ".join([f"ID:{v['id']}({v.get('nombre','N/A')})" for v in vlans_disp])
    lineas.append(f"   {Color.CYAN} VLANs:{Color.END} {vlan_str}")
        
    separador = f"{Color.BLUE}{'═' * 70}{Color.END}"
    return f"\n{header}\n" + "\n".join(lineas) + f"\n{separador}"


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
    print(f"{Color.BOLD}{Color.YELLOW}4.{Color.END} ✍️ Editar dispositivo existente")
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
    if mostrar_actual is not None : print(f"{Color.DARKCYAN}Valor actual: {mostrar_actual or 'No asignado'}{Color.END}")
    
    op_list = list(opciones.items()) if isinstance(opciones, dict) else opciones
    for i, item in enumerate(op_list, 1):
        val_mostrar = item[1] if isinstance(item, (tuple, list)) and len(item) > 1 else str(item)
        print(f"{Color.YELLOW}{i}.{Color.END} {val_mostrar}")
    if permitir_volver: print(f"{Color.YELLOW}0.{Color.END} Volver / No cambiar / Cancelar")

    while True:
        try:
            max_opc = len(op_list)
            prompt_text = f"Opción (1-{max_opc}"
            if permitir_volver: prompt_text += ", 0 para Volver/No cambiar"
            prompt_text += "): "
            op_num_str = input(f"\n{Color.GREEN}↳ {prompt_text}{Color.END}").strip()
            
            if permitir_volver and op_num_str == "0": return "VOLVER"
            # Si se muestra valor actual y el usuario presiona Enter (string vacío), es "No cambiar" -> VOLVER
            if permitir_volver and not op_num_str and mostrar_actual is not None: return "VOLVER"

            op_num = int(op_num_str)
            if 1 <= op_num <= max_opc:
                sel_item = op_list[op_num-1]
                return sel_item[0] if isinstance(sel_item, (tuple, list)) else sel_item
            mostrar_mensaje(f"Número entre 1-{max_opc}{(', o 0' if permitir_volver else '')}", "error")
        except ValueError: mostrar_mensaje("Entrada inválida. Ingrese número.", "error")


def ingresar_ip_y_mascara_para_nuevo(dispositivos_existentes):
    """Función específica para ingresar IP, Máscara Y CAPA para un NUEVO dispositivo."""
    ip_final, mascara_final, tipo_ip_final, capa_final_str = None, None, None, None
    while True:
        ip_str_in = input(f"{Color.GREEN}↳ IP (IPv4/IPv6, vacío omite, '0' cancela): {Color.END}").strip()
        if not ip_str_in: return None, None, None, None # Sin IP, sin máscara, sin tipo, sin capa
        if ip_str_in == "0": return "VOLVER_MENU", None, None, None # Señal para cancelar creación

        try:
            tipo_ip_validado = validar_formato_ip(ip_str_in)
            if any(d.get("IP") == ip_str_in for d in dispositivos_existentes):
                mostrar_mensaje(f"Error: IP ({ip_str_in}) ya en uso.", "error"); continue
            
            ip_final = ip_str_in
            tipo_ip_final = tipo_ip_validado
            
            if tipo_ip_final == "IPv4":
                while True:
                    mascara_str_in = input(f"{Color.GREEN}↳ Máscara red para {Color.CYAN}{ip_final}{Color.END} ('0' cancela IP): {Color.END}").strip()
                    if mascara_str_in == "0": ip_final = None; tipo_ip_final = None; break 
                    if not mascara_str_in: mostrar_mensaje("Máscara obligatoria para IPv4.", "error"); continue
                    try:
                        validar_mascara_red_ipv4(mascara_str_in); mascara_final = mascara_str_in; break
                    except ValueError as e_mask:
                        mostrar_mensaje(str(e_mask), "error")
                        _, sug_mask = obtener_clase_y_mascara_predeterminada_ipv4(ip_final)
                        if sug_mask: print(f"{Color.YELLOW}ℹ️ Máscara común: {sug_mask}{Color.END}")
                if ip_final is None: continue 
            elif tipo_ip_final == "IPv6":
                mostrar_mensaje(f"No se requiere máscara para IPv6 ({ip_final}).", "info"); mascara_final = None
            
            # Preguntar por la capa después de IP y Máscara
            print(f"\n{Color.CYAN}--- Selección Capa de Red para {ip_final or 'el dispositivo'} ---{Color.END}")
            capa_key_sel = seleccionar_opcion(CAPAS_RED, "📌 Capa de red:")
            if capa_key_sel == "VOLVER": # Si cancela capa, ¿cancelar IP también o continuar sin capa?
                 mostrar_mensaje("Selección de capa cancelada. La IP se mantendrá sin capa asignada explícitamente aquí.", "info")
                 capa_final_str = None # Opcional: o se podría volver a pedir la IP.
            else:
                capa_final_str = CAPAS_RED[capa_key_sel]
            
            return ip_final, mascara_final, tipo_ip_final, capa_final_str
        except ValueError as e_ip:
            mostrar_mensaje(str(e_ip), "error")
            print(f"\n{Color.YELLOW}💡 IPs: IPv4 (192.168.1.1), IPv6 (2001:db8::1){Color.END}")
        if input(f"{Color.GREEN}¿Reintentar IP? (s/n): {Color.END}").lower() != 's':
            return "VOLVER_MENU", None, None, None


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
            validar_nombre(nombre_in, dispositivos_actuales, None) # id_actual es None para nuevos
            nombre_disp = nombre_in; break
        except ValueError as e: mostrar_mensaje(str(e), "error")

    ip_disp, mask_disp, ip_type_disp, capa_disp_str = ingresar_ip_y_mascara_para_nuevo(dispositivos_actuales)
    if ip_disp == "VOLVER_MENU": return None

    msg_ip_capa = []
    if ip_disp: msg_ip_capa.append(f"IP {Color.YELLOW}{ip_disp}{Color.END}({ip_type_disp})")
    if mask_disp and ip_type_disp=="IPv4": msg_ip_capa.append(f"Máscara {Color.YELLOW}{mask_disp}{Color.END}")
    if capa_disp_str: msg_ip_capa.append(f"Capa {Color.YELLOW}{capa_disp_str}{Color.END}")
    
    if msg_ip_capa: mostrar_mensaje(", ".join(msg_ip_capa) + " procesada(s).", "exito")
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
                    v_nom = validar_vlan_nombre(v_nom_str) # ya maneja nombre por defecto
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
    import copy
    disp_edit = copy.deepcopy(dispositivo_original) # Trabajar sobre una copia

    cambios_realizados = False

    while True:
        mostrar_titulo(f"EDITANDO DISPOSITIVO: {disp_edit.get('NOMBRE')}")
        print(f"{Color.DARKCYAN}Valores actuales (los cambios se reflejan aquí temporalmente):{Color.END}")
        print(formatear_dispositivo_para_mostrar(disp_edit))

        print(f"{Color.YELLOW}1.{Color.END} Editar Nombre")
        print(f"{Color.YELLOW}2.{Color.END} Editar Tipo")
        print(f"{Color.YELLOW}3.{Color.END} Editar IP y Máscara de Red") # Separado
        print(f"{Color.YELLOW}4.{Color.END} Editar Capa de Red")        # Separado
        print(f"{Color.YELLOW}5.{Color.END} Gestionar Servicios")
        print(f"{Color.YELLOW}6.{Color.END} Gestionar VLANs")
        print(f"{Color.YELLOW}---{Color.END}")
        print(f"{Color.YELLOW}8.{Color.END} Guardar Cambios y Salir")
        print(f"{Color.YELLOW}9.{Color.END} Descartar Cambios y Salir")
        
        opc_edit = input(f"\n{Color.GREEN}↳ Seleccione atributo a editar (o acción): {Color.END}").strip()

        if opc_edit == '1': # Editar Nombre
            nuevo_nombre_str = input(f"{Color.GREEN}↳ Nuevo nombre [{disp_edit.get('NOMBRE')}]: {Color.END}").strip()
            if nuevo_nombre_str and nuevo_nombre_str != disp_edit.get('NOMBRE'):
                try:
                    validar_nombre(nuevo_nombre_str, dispositivos_actuales, indice_dispositivo)
                    disp_edit['NOMBRE'] = nuevo_nombre_str
                    mostrar_mensaje("Nombre actualizado temporalmente.", "exito"); cambios_realizados = True
                except ValueError as e: mostrar_mensaje(str(e), "error")
                sleep(1)

        elif opc_edit == '2': # Editar Tipo
            tipo_actual_str = disp_edit.get('TIPO')
            nuevo_tipo_key = seleccionar_opcion(TIPOS_DISPOSITIVO, "Seleccione nuevo tipo:", mostrar_actual=tipo_actual_str)
            if nuevo_tipo_key != "VOLVER" and TIPOS_DISPOSITIVO[nuevo_tipo_key] != tipo_actual_str:
                disp_edit['TIPO'] = TIPOS_DISPOSITIVO[nuevo_tipo_key]
                mostrar_mensaje(f"Tipo actualizado temporalmente a {disp_edit['TIPO']}.", "exito"); cambios_realizados = True
                # Podrían añadirse advertencias sobre servicios/VLANs aquí
                sleep(1)
        
        elif opc_edit == '3': # Editar IP y Máscara
            ip_actual = disp_edit.get('IP')
            mask_actual = disp_edit.get('MÁSCARA')
            ip_type_actual = disp_edit.get('IP_TYPE')
            
            nueva_ip_str = input(f"{Color.GREEN}↳ Nueva IP [{ip_actual or 'ninguna'}] (vacío no cambia, '-' limpia): {Color.END}").strip()
            
            ip_cambiada_o_limpiada = False

            if nueva_ip_str == "-" : # Limpiar IP
                disp_edit['IP'] = None
                disp_edit['MÁSCARA'] = None
                disp_edit['IP_TYPE'] = None
                mostrar_mensaje("IP y Máscara limpiadas temporalmente.", "info"); cambios_realizados = True; ip_cambiada_o_limpiada = True
            elif nueva_ip_str and nueva_ip_str != ip_actual:
                try:
                    nuevo_ip_type = validar_formato_ip(nueva_ip_str)
                    # Validar unicidad
                    es_duplicada = False
                    for i, d in enumerate(dispositivos_actuales):
                        if i == indice_dispositivo: continue # No comparar consigo mismo
                        if d.get("IP") == nueva_ip_str: es_duplicada = True; break
                    if es_duplicada: raise ValueError(f"IP {nueva_ip_str} ya está en uso.")

                    disp_edit['IP'] = nueva_ip_str
                    disp_edit['IP_TYPE'] = nuevo_ip_type
                    if nuevo_ip_type == "IPv6": disp_edit['MÁSCARA'] = None # IPv6 no usa máscara aquí
                    mostrar_mensaje(f"IP actualizada temporalmente a {nueva_ip_str}.", "exito"); cambios_realizados = True; ip_cambiada_o_limpiada = True
                except ValueError as e: mostrar_mensaje(str(e), "error"); sleep(1); continue
            
            # Si la IP es IPv4 (nueva o existente que se mantuvo pero se quiere re-evaluar máscara)
            if disp_edit.get('IP') and disp_edit.get('IP_TYPE') == 'IPv4':
                if ip_cambiada_o_limpiada or input(f"{Color.GREEN}¿Revisar máscara para {disp_edit.get('IP')}? (s/n): {Color.END}").lower() == 's':
                    nueva_mask_str = input(f"{Color.GREEN}↳ Nueva Máscara [{mask_actual or 'ninguna'}]: {Color.END}").strip()
                    if nueva_mask_str and nueva_mask_str != mask_actual:
                        try:
                            validar_mascara_red_ipv4(nueva_mask_str)
                            disp_edit['MÁSCARA'] = nueva_mask_str
                            mostrar_mensaje("Máscara actualizada temporalmente.", "exito"); cambios_realizados = True
                        except ValueError as e: mostrar_mensaje(str(e), "error")
                    elif not nueva_mask_str and not disp_edit.get('MÁSCARA'): # Si no había máscara y no se ingresa una
                         mostrar_mensaje("Máscara es requerida para IPv4. No se cambió.", "advertencia")


            sleep(1)


        elif opc_edit == '4': # Editar Capa de Red
            capa_actual_str = disp_edit.get('CAPA')
            nueva_capa_key = seleccionar_opcion(CAPAS_RED, "Seleccione nueva capa de red:", mostrar_actual=capa_actual_str)
            if nueva_capa_key != "VOLVER" and CAPAS_RED.get(nueva_capa_key) != capa_actual_str :
                disp_edit['CAPA'] = CAPAS_RED[nueva_capa_key]
                mostrar_mensaje("Capa de red actualizada temporalmente.", "exito"); cambios_realizados = True
            sleep(1)

        elif opc_edit == '5': # Gestionar Servicios
            # ... (lógica similar a la función gestionar_servicios_dispositivo, aplicada a disp_edit)
            # Asegurarse de que 'cambios_realizados = True' si algo cambia.
            tipo_disp_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == disp_edit.get("TIPO")), None)
            if tipo_disp_key not in TIPOS_CON_SERVICIOS:
                mostrar_mensaje(f"El tipo '{disp_edit.get('TIPO')}' no admite servicios.", "advertencia"); sleep(2); continue
            # Lógica para gestionar servicios (añadir/eliminar) en disp_edit
            # ... (esta parte se mantiene igual que en la versión anterior de editar_dispositivo_interactivo)
            serv_actuales_list = [s.strip() for s in disp_edit.get("SERVICIOS", "Ninguno").split(' ') if s.strip() and s != "Ninguno"]
            hubo_cambio_servicio = False
            while True:
                # Mini-título para la subsección
                print(f"\n{Color.CYAN}{'─'*10} Gestionando Servicios para: {disp_edit.get('NOMBRE')} {'─'*10}{Color.END}")
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
                        mostrar_mensaje(f"Servicio {SERVICIOS_VALIDOS[serv_key_add]} añadido.", "exito"); hubo_cambio_servicio = True
                elif opc_serv == '2': #Eliminar
                    if not serv_actuales_list: mostrar_mensaje("No hay servicios para eliminar.", "info"); sleep(1); continue
                    serv_menu_del = {s:s for s in serv_actuales_list} 
                    serv_val_del = seleccionar_opcion(serv_menu_del, "Seleccione servicio a eliminar:")
                    if serv_val_del != "VOLVER":
                        serv_actuales_list.remove(serv_val_del)
                        disp_edit["SERVICIOS"] = " ".join(sorted(list(set(serv_actuales_list)))) if serv_actuales_list else "Ninguno"
                        mostrar_mensaje(f"Servicio {serv_val_del} eliminado.", "exito"); hubo_cambio_servicio = True
                elif opc_serv == '0': break
                else: mostrar_mensaje("Opción inválida.", "error")
                sleep(1)
            if hubo_cambio_servicio: cambios_realizados = True


        elif opc_edit == '6': # Gestionar VLANs
            # ... (lógica similar a la función gestionar_vlans_dispositivo, aplicada a disp_edit)
            # Asegurarse de que 'cambios_realizados = True' si algo cambia.
            tipo_disp_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == disp_edit.get("TIPO")), None)
            if tipo_disp_key not in TIPOS_CON_VLANS:
                mostrar_mensaje(f"El tipo '{disp_edit.get('TIPO')}' no admite VLANs.", "advertencia"); sleep(2); continue
            # Lógica para gestionar VLANs (añadir/eliminar) en disp_edit
            # ... (esta parte se mantiene igual que en la versión anterior de editar_dispositivo_interactivo)
            vlans_actuales_list = disp_edit.get("VLANS", []) 
            hubo_cambio_vlan = False
            while True:
                print(f"\n{Color.CYAN}{'─'*10} Gestionando VLANs para: {disp_edit.get('NOMBRE')} {'─'*10}{Color.END}")
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
                        v_nom = validar_vlan_nombre(v_nom_str) 
                        vlans_actuales_list.append({"id":v_id, "nombre":v_nom})
                        disp_edit["VLANS"] = sorted(vlans_actuales_list, key=lambda x: x['id'])
                        mostrar_mensaje(f"VLAN ID:{v_id}, Nombre:{v_nom} añadida.", "exito"); hubo_cambio_vlan = True
                    except ValueError as e: mostrar_mensaje(str(e), "error")
                elif opc_vlan == '2': #Eliminar
                    if not vlans_actuales_list: mostrar_mensaje("No hay VLANs para eliminar.", "info"); continue
                    vlan_menu_del = [(idx, f"ID:{v['id']}, Nombre:{v.get('nombre','N/A')}") for idx,v in enumerate(vlans_actuales_list)]
                    idx_vlan_del_sel = seleccionar_opcion(vlan_menu_del, "Seleccione VLAN a eliminar:")
                    if idx_vlan_del_sel != "VOLVER":
                        v_elim = vlans_actuales_list.pop(idx_vlan_del_sel)
                        disp_edit["VLANS"] = vlans_actuales_list 
                        mostrar_mensaje(f"VLAN ID:{v_elim['id']} eliminada.", "exito"); hubo_cambio_vlan = True
                elif opc_vlan == '0': break
                else: mostrar_mensaje("Opción inválida.", "error")
                sleep(1)
            if hubo_cambio_vlan: cambios_realizados = True


        elif opc_edit == '8': # Guardar Cambios
            if not cambios_realizados:
                mostrar_mensaje("No se realizaron cambios para guardar.", "info"); sleep(1.5); continue

            try: # Re-validar nombre por si acaso antes de guardar, contra la lista original
                validar_nombre(disp_edit.get("NOMBRE"), dispositivos_actuales, indice_dispositivo)
                dispositivos_actuales[indice_dispositivo] = disp_edit # Actualiza el original con la copia editada
                guardar_datos_json(dispositivos_actuales)
                mostrar_mensaje("Cambios guardados exitosamente.", "exito")
                sleep(1.5)
                return # Salir de la función de edición
            except ValueError as e:
                mostrar_mensaje(f"Error al guardar: {str(e)}. El nombre podría estar duplicado. Por favor, edite el nombre.", "error")
                sleep(2) # No salir, permitir corregir
            

        elif opc_edit == '9': # Descartar Cambios
            if cambios_realizados:
                mostrar_mensaje("Cambios descartados.", "info"); sleep(1.5)
            else:
                mostrar_mensaje("No había cambios pendientes. Saliendo de edición.", "info"); sleep(1.5)
            return # Salir de la función de edición
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

def seleccionar_dispositivo_para_accion(dispositivos_dicts, accion_str, filtro_tipo_keys=None):
    if not dispositivos_dicts:
        mostrar_mensaje("No hay dispositivos registrados.", "advertencia"); sleep(2); return None

    candidatos = []
    for i, d in enumerate(dispositivos_dicts):
        if filtro_tipo_keys:
            tipo_actual_key = next((k for k,v in TIPOS_DISPOSITIVO.items() if v == d.get("TIPO")), None)
            if not tipo_actual_key or tipo_actual_key not in filtro_tipo_keys:
                continue # Saltar si el tipo no coincide con el filtro
        candidatos.append({"indice_original": i, "nombre": d.get("NOMBRE", "N/A"), "tipo": d.get("TIPO", "N/A")})
    
    if not candidatos:
        msg = f"No hay dispositivos aptos para {accion_str}."
        if filtro_tipo_keys : msg += f" (Tipos esperados: {', '.join(filtro_tipo_keys)})"
        mostrar_mensaje(msg, "advertencia"); sleep(2); return None

    print(f"{Color.BOLD}📋 Dispositivos disponibles para {accion_str}:{Color.END}")
    opciones_menu = [(info["indice_original"], f"{info['nombre']} ({info['tipo']})") for info in candidatos]
    
    indice_real_seleccionado = seleccionar_opcion(opciones_menu, f"Seleccione el dispositivo para {accion_str}:")
    if indice_real_seleccionado == "VOLVER": return None
    return indice_real_seleccionado


def agregar_servicio_dispositivo(dispositivos_dicts):
    mostrar_titulo("AGREGAR SERVICIO A DISPOSITIVO")
    indice_disp_sel = seleccionar_dispositivo_para_accion(dispositivos_dicts, "agregar servicio", TIPOS_CON_SERVICIOS)
    if indice_disp_sel is None: return

    disp_mod = dispositivos_dicts[indice_disp_sel]
    # ... (resto de la lógica igual)
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
    # ... (resto de la lógica igual)
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
    # ... (resto de la lógica igual)
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
                v_nom=validar_vlan_nombre(v_nom_str) 
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
    # ... (resto de la lógica igual)
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
        if not opcion.isdigit() or not (1 <= int(opcion) <= 11) : # Validación básica de entrada
             mostrar_mensaje("Opción inválida. Seleccione del 1 al 11.", "error"); sleep(2); continue
        
        mostrar_progreso("Procesando", 0.2)

        if opcion == "1":
            nuevo_d = agregar_dispositivo_interactivo(dispositivos)
            if nuevo_d: dispositivos.append(nuevo_d); guardar_datos_json(dispositivos)
        elif opcion == "2": mostrar_dispositivos(dispositivos)
        elif opcion == "3": buscar_dispositivo(dispositivos)
        elif opcion == "4": 
            indice_a_editar = seleccionar_dispositivo_para_accion(dispositivos, "editar")
            if indice_a_editar is not None:
                editar_dispositivo_interactivo(indice_a_editar, dispositivos) 
        elif opcion == "5": agregar_servicio_dispositivo(dispositivos)
        elif opcion == "6": eliminar_servicio_dispositivo(dispositivos)
        elif opcion == "7": gestionar_vlans_dispositivo(dispositivos)
        elif opcion == "8": eliminar_dispositivo(dispositivos)
        elif opcion == "9": generar_reporte_estadistico(dispositivos)
        elif opcion == "10": exportar_a_txt(dispositivos)
        elif opcion == "11":
            mostrar_mensaje("Guardando datos...", "info"); guardar_datos_json(dispositivos)
            mostrar_progreso("Saliendo",1); mostrar_mensaje("¡Hasta pronto! 👋","info");sleep(1);limpiar_pantalla();break
        # No se necesita 'else' aquí debido a la validación de entrada al principio del bucle

if __name__ == "__main__":
    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═'*70}{Color.END}\n{Color.BOLD}{Color.PURPLE}{'BIENVENIDO AL SISTEMA AVANZADO DE GESTIÓN DE RED'.center(70)}{Color.END}\n{Color.BLUE}{'═'*70}{Color.END}\n")
    sleep(1.5)
    if pantalla_login(): main()
    else: limpiar_pantalla();print(f"{Color.RED}{Color.BOLD}Acceso denegado.{Color.END}");sleep(2);limpiar_pantalla()