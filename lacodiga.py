import re
from enum import Enum
import os
from time import sleep
from datetime import datetime  # Added for report generation

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

# 🎨 Diseño de la interfaz
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_titulo(titulo):
    limpiar_pantalla()
    print(f"{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{titulo.center(60)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}\n")

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
    'ACCESO': '🔌 Acceso'
}

def validar_ip(ip):
    # Verificación básica de formato
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        raise ValueError("Formato incorrecto. Debe ser X.X.X.X donde X es un número (0-255)")
    
    octetos = ip.split('.')
    if len(octetos) != 4:
        raise ValueError("La IP debe tener exactamente 4 partes separadas por puntos")
    
    for octeto_idx, octeto_str in enumerate(octetos):
        try:
            num = int(octeto_str)
            if not (0 <= num <= 255):
                raise ValueError(f"El octeto {num} no es válido (debe estar entre 0-255)")
        except ValueError:
            raise ValueError(f"'{octeto_str}' no es un número válido para un octeto de IP")
    
    # Verificación de rangos especiales
    primer_octeto = int(octetos[0])
    if primer_octeto == 0:
        raise ValueError("El primer octeto no puede ser 0 (reservado para 'esta red')")
    if primer_octeto == 127:
        raise ValueError("Las IPs 127.x.x.x están reservadas para loopback")
    if primer_octeto >= 224:
        if primer_octeto < 240:
            raise ValueError("Las IPs 224.x.x.x a 239.x.x.x están reservadas para multicast (Clase D)")
        else:
            raise ValueError("Las IPs 240.x.x.x y superiores están reservadas para uso futuro (Clase E)")
    
    # Verificación de direcciones especiales
    if ip == "255.255.255.255":
        raise ValueError("Esta IP (255.255.255.255) está reservada para broadcast limitado")
    
    return True

def validar_mascara_red(mascara_str):
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", mascara_str):
        raise ValueError("Formato incorrecto de máscara. Debe ser X.X.X.X.")
    
    octetos_str = mascara_str.split('.')
    if len(octetos_str) != 4: 
        raise ValueError("La máscara debe tener exactamente 4 octetos.")

    octetos_int = []
    for octeto_s in octetos_str:
        try:
            num = int(octeto_s)
            if not (0 <= num <= 255):
                raise ValueError(f"El octeto de máscara {num} no es válido (debe estar entre 0-255).")
            octetos_int.append(num)
        except ValueError:
            raise ValueError(f"'{octeto_s}' no es un número válido para un octeto de máscara.")

    binario_completo = "".join([bin(octeto)[2:].zfill(8) for octeto in octetos_int])

    if '01' in binario_completo:
        raise ValueError("Máscara inválida. Los bits '1' deben ser contiguos desde la izquierda, seguidos solo por bits '0'. Ejemplo: 255.255.255.0")

    if mascara_str == "0.0.0.0":
        raise ValueError("La máscara 0.0.0.0 no es una máscara de red válida para asignación.")
    return True

def obtener_clase_y_mascara_predeterminada(ip_str):
    try:
        primer_octeto = int(ip_str.split('.')[0])
    except (ValueError, IndexError):
        raise ValueError("Error al parsear la IP para obtener su clase.")

    if 1 <= primer_octeto <= 126:
        return 'A', '255.0.0.0'
    elif 128 <= primer_octeto <= 191:
        return 'B', '255.255.0.0'
    elif 192 <= primer_octeto <= 223:
        return 'C', '255.255.255.0'
    else:
        return None, None 

def validar_nombre(nombre):
    if not re.match(r'^[a-zA-Z0-9\-\.]+$', nombre):
        raise ValueError("El nombre solo puede contener letras, números, guiones (-) y puntos (.)")
    if len(nombre) > 30:
        raise ValueError("El nombre no puede exceder los 30 caracteres")
    return True

def validar_servicios(servicios):
    for servicio in servicios:
        if servicio not in SERVICIOS_VALIDOS.values(): 
            raise ValueError(f"Servicio inválido: {servicio}")
    return True

def crear_dispositivo(tipo, nombre, ip=None, mascara_red=None, capa=None, servicios=None):
    try:
        validar_nombre(nombre) 
        if servicios:
            validar_servicios(servicios)
        
        dispositivo = [
            f"{Color.CYAN}🔧 {Color.BOLD}TIPO:{Color.END} {tipo}",
            f"{Color.CYAN}🏷️ {Color.BOLD}NOMBRE:{Color.END} {nombre}"
        ]
        
        if ip:
            dispositivo.append(f"{Color.CYAN}🌍 {Color.BOLD}IP:{Color.END} {ip}")
            if mascara_red: 
                dispositivo.append(f"{Color.CYAN}🌐 {Color.BOLD}MÁSCARA:{Color.END} {mascara_red}")
        if capa:
            dispositivo.append(f"{Color.CYAN}📊 {Color.BOLD}CAPA:{Color.END} {capa}")
        if servicios and len(servicios) > 0:
            dispositivo.append(f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {' '.join(servicios)}")
        
        separador = f"{Color.BLUE}{'═' * 60}{Color.END}"
        return f"\n{separador}\n" + "\n".join(dispositivo) + f"\n{separador}"
    
    except ValueError as e:
        return f"{Color.RED}❌ Error al crear dispositivo: {e}{Color.END}"

def generar_reporte(dispositivos):
    if not dispositivos:
        mostrar_mensaje("⚠️ No existen dispositivos registrados.", "advertencia")
        sleep(2)
        return
    
    mostrar_titulo("📊 REPORTE ESTADÍSTICO DETALLADO")
    
    print(f"\n{Color.BOLD}{Color.PURPLE}📌 RESUMEN GENERAL{Color.END}")
    print(f"{Color.CYAN}📅 Total de dispositivos registrados:{Color.END} {len(dispositivos)}")
    print(f"{Color.CYAN}📅 Última actualización:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print(f"\n{Color.BOLD}{Color.PURPLE}🔢 DISTRIBUCIÓN POR TIPO:{Color.END}")
    tipos = {}
    for disp in dispositivos:
        tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
        if tipo_linea:
            tipo = tipo_linea.split("TIPO:")[1].strip().split(Color.END)[-1].strip() 
            tipos[tipo] = tipos.get(tipo, 0) + 1
    
    for tipo, cantidad in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        print(f"\n   {Color.YELLOW}{tipo.upper()} ({cantidad} dispositivos):{Color.END}")
        count = 0
        for disp in dispositivos:
            if count >= 3: break
            tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
            if tipo_linea and tipo_linea.split("TIPO:")[1].strip().split(Color.END)[-1].strip() == tipo:
                nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
                if nombre_linea:
                    nombre = nombre_linea.split("NOMBRE:")[1].strip().split(Color.END)[-1].strip()
                    ip_linea = next((linea for linea in disp.split('\n') if "IP:" in linea), None)
                    mascara_linea = next((linea for linea in disp.split('\n') if "MÁSCARA:" in linea), None)
                    ip_info = "Sin IP"
                    if ip_linea:
                        ip_val = ip_linea.split("IP:")[1].strip().split(Color.END)[-1].strip()
                        ip_info = ip_val
                        if mascara_linea:
                            mascara_val = mascara_linea.split("MÁSCARA:")[1].strip().split(Color.END)[-1].strip()
                            ip_info += f" / {mascara_val}"
                    print(f"     - {nombre} ({ip_info})")
                    count += 1
        if cantidad > 3:
            print(f"     {Color.DARKCYAN}...y {cantidad-3} más{Color.END}")
    
    print(f"\n{Color.BOLD}{Color.PURPLE}📡 DISTRIBUCIÓN POR CAPA DE RED:{Color.END}")
    capas = {}
    for disp in dispositivos:
        capa_linea = next((linea for linea in disp.split('\n') if "CAPA:" in linea), None)
        capa = capa_linea.split("CAPA:")[1].strip().split(Color.END)[-1].strip() if capa_linea else "Sin capa especificada"
        capas[capa] = capas.get(capa, 0) + 1
    
    for capa, cantidad in sorted(capas.items(), key=lambda x: x[1], reverse=True):
        print(f"\n   {Color.YELLOW}{capa.upper()} ({cantidad} dispositivos):{Color.END}")
        count = 0
        for disp in dispositivos:
            if count >= 3: break
            current_capa_linea = next((linea for linea in disp.split('\n') if "CAPA:" in linea), None)
            current_capa = current_capa_linea.split("CAPA:")[1].strip().split(Color.END)[-1].strip() if current_capa_linea else "Sin capa especificada"
            if current_capa == capa:
                nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
                tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
                if nombre_linea and tipo_linea:
                    nombre = nombre_linea.split("NOMBRE:")[1].strip().split(Color.END)[-1].strip()
                    tipo_disp = tipo_linea.split("TIPO:")[1].strip().split(Color.END)[-1].strip()
                    servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
                    servicios_str = servicios_linea.split("SERVICIOS:")[1].strip().split(Color.END)[-1].strip() if servicios_linea else "Ninguno"
                    print(f"     - {nombre} ({tipo_disp}) con servicios: {servicios_str}")
                    count += 1
        if cantidad > 3:
            print(f"     {Color.DARKCYAN}...y {cantidad-3} más{Color.END}")
            
    print(f"\n{Color.BOLD}{Color.PURPLE}🛠️ SERVICIOS MÁS UTILIZADOS:{Color.END}")
    servicios_count = {}
    for disp in dispositivos:
        servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
        if servicios_linea:
            servicios_disp_str = servicios_linea.split("SERVICIOS:")[1].strip().split(Color.END)[-1].strip()
            current_device_services = []
            temp_serv_str = servicios_disp_str
            for key_s, val_s in SERVICIOS_VALIDOS.items(): 
                if val_s in temp_serv_str:
                    current_device_services.append(val_s)
                    temp_serv_str = temp_serv_str.replace(val_s, "", 1) 

            for servicio_val in current_device_services:
                 servicios_count[servicio_val] = servicios_count.get(servicio_val, 0) + 1

    for servicio, cantidad in sorted(servicios_count.items(), key=lambda x: x[1], reverse=True):
        print(f"\n   {Color.YELLOW}{servicio} ({cantidad} dispositivos):{Color.END}")
        count = 0
        for disp in dispositivos:
            if count >= 3: break
            servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
            if servicios_linea and servicio in servicios_linea.split("SERVICIOS:")[1].strip().split(Color.END)[-1].strip():
                nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
                ip_linea = next((linea for linea in disp.split('\n') if "IP:" in linea), None)
                if nombre_linea:
                    nombre = nombre_linea.split("NOMBRE:")[1].strip().split(Color.END)[-1].strip()
                    ip_info = "Sin IP"
                    if ip_linea:
                        ip_val = ip_linea.split("IP:")[1].strip().split(Color.END)[-1].strip()
                        ip_info = ip_val
                    print(f"     - {nombre} ({ip_info})")
                    count += 1
        if cantidad > 3:
            print(f"     {Color.DARKCYAN}...usado por {cantidad-3} dispositivos más{Color.END}")

    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'📋 LISTADO COMPLETO DE DISPOSITIVOS'.center(60)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}")
    
    for i, disp_str in enumerate(dispositivos, 1):
        print(f"\n{Color.YELLOW}🔹 Dispositivo {i}:{Color.END}")
        disp_data = {}
        for linea in disp_str.split('\n'):
            if ":" in linea:
                partes = linea.split(":", 1)
                clave_raw = partes[0].strip()
                valor = partes[1].strip()
                clave = re.sub(r'\033\[[0-9;]*[mK]', '', clave_raw).replace('🔧','').replace('🏷️','').replace('🌍','').replace('🌐','').replace('📊','').replace('🛠️','').replace('BOLD','').strip()
                clave = clave.replace(Color.BOLD, "").replace(Color.CYAN, "").replace(Color.END, "").strip() 
                disp_data[clave] = valor.split(Color.END)[-1].strip()

        if "TIPO" in disp_data: print(f"   {Color.CYAN}🔧 Tipo:{Color.END} {disp_data['TIPO']}")
        if "NOMBRE" in disp_data: print(f"   {Color.CYAN}🏷️ Nombre:{Color.END} {disp_data['NOMBRE']}")
        if "IP" in disp_data: print(f"   {Color.CYAN}🌍 IP:{Color.END} {disp_data['IP']}")
        if "MÁSCARA" in disp_data: print(f"   {Color.CYAN}🌐 Máscara:{Color.END} {disp_data['MÁSCARA']}")
        if "CAPA" in disp_data: print(f"   {Color.CYAN}📊 Capa:{Color.END} {disp_data['CAPA']}")
        if "SERVICIOS" in disp_data: print(f"   {Color.CYAN}🛠️ Servicios:{Color.END} {disp_data['SERVICIOS']}")
    
    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.GREEN}🎉 Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}\n")
    
    input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")

def mostrar_menu_principal():
    mostrar_titulo("SISTEMA DE GESTIÓN DE DISPOSITIVOS")
    print(f"{Color.BOLD}{Color.YELLOW}1.{Color.END} 📱 Agregar nuevo dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}2.{Color.END} 📜 Mostrar todos los dispositivos")
    print(f"{Color.BOLD}{Color.YELLOW}3.{Color.END} 🔍 Buscar dispositivo por nombre")
    print(f"{Color.BOLD}{Color.YELLOW}4.{Color.END} ➕ Agregar servicio a dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}5.{Color.END} ❌ Eliminar dispositivo")
    print(f"{Color.BOLD}{Color.YELLOW}6.{Color.END} 📊 Generar reporte estadístico")
    print(f"{Color.BOLD}{Color.YELLOW}7.{Color.END} 🚪 Salir")
    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")

def seleccionar_opcion(opciones, titulo):
    print(f"\n{Color.BOLD}{titulo}{Color.END}")
    opciones_list = list(opciones.items()) 
    for i, (key, value) in enumerate(opciones_list, 1):
        print(f"{Color.YELLOW}{i}.{Color.END} {value}")
    
    while True:
        try:
            opcion_num_str = input(f"\n{Color.GREEN}↳ Seleccione una opción (1-{len(opciones_list)}): {Color.END}")
            opcion_num = int(opcion_num_str)
            if 1 <= opcion_num <= len(opciones_list):
                return opciones_list[opcion_num-1][1] 
            mostrar_mensaje(f"Por favor ingrese un número entre 1 y {len(opciones_list)}", "error")
        except ValueError:
            mostrar_mensaje("Entrada inválida. Por favor ingrese un número.", "error")

def ingresar_ip_y_mascara():
    ip_final = None
    mascara_final = None
    
    while True: 
        ip_str = input(f"{Color.GREEN}↳ Ingrese la dirección IP (deje vacío para omitir IP/Máscara): {Color.END}").strip()
        if not ip_str:
            return None, None 

        try:
            validar_ip(ip_str) 
            
            while True: 
                mascara_str = input(f"{Color.GREEN}↳ Ingrese la máscara de red para {Color.CYAN}{ip_str}{Color.END}: {Color.END}").strip()
                if not mascara_str: 
                    mostrar_mensaje("La máscara de red es obligatoria si se ingresa una IP. Déjela vacía solo si desea omitir la IP también.", "error")
                    continue
                try:
                    validar_mascara_red(mascara_str)

                    clase_ip, mascara_pred_ip = obtener_clase_y_mascara_predeterminada(ip_str)

                    if clase_ip: 
                        if mascara_str != mascara_pred_ip:
                            error_msg = (f"La máscara {Color.YELLOW}{mascara_str}{Color.END} no es la máscara predeterminada "
                                         f"({Color.YELLOW}{mascara_pred_ip}{Color.END}) para una IP de Clase {Color.YELLOW}{clase_ip}{Color.END}.\n"
                                         f"{Color.CYAN}Clase A (1-126.x.x.x) usa 255.0.0.0\n"
                                         f"Clase B (128-191.x.x.x) usa 255.255.0.0\n"
                                         f"Clase C (192-223.x.x.x) usa 255.255.255.0{Color.END}")
                            raise ValueError(error_msg)
                    
                    ip_final = ip_str
                    mascara_final = mascara_str
                    return ip_final, mascara_final 

                except ValueError as e_mask:
                    mostrar_mensaje(f"{str(e_mask)}", "error") 
                    clase_ip_info, mascara_esperada_info = obtener_clase_y_mascara_predeterminada(ip_str)
                    if clase_ip_info:
                        print(f"{Color.YELLOW}ℹ️ Para una IP de Clase {clase_ip_info} como {ip_str}, la máscara predeterminada es {mascara_esperada_info}.{Color.END}")
        
        except ValueError as e_ip:
            mostrar_mensaje(f"{str(e_ip)}", "error")
            print(f"\n{Color.YELLOW}💡 Ejemplos de IPs válidas:{Color.END}")
            print(f"- {Color.CYAN}10.0.0.1{Color.END} (Clase A, máscara predeterminada 255.0.0.0)")
            print(f"- {Color.CYAN}172.16.0.1{Color.END} (Clase B, máscara predeterminada 255.255.0.0)")
            print(f"- {Color.CYAN}192.168.1.1{Color.END} (Clase C, máscara predeterminada 255.255.255.0)")
            reintentar = input(f"{Color.GREEN}¿Desea intentar ingresar la IP nuevamente? (s/n): {Color.END}").strip().lower()
            if reintentar != 's':
                return None, None 


def agregar_dispositivo_interactivo():
    mostrar_titulo("AGREGAR NUEVO DISPOSITIVO")
    
    tipo_seleccionado_str = seleccionar_opcion(TIPOS_DISPOSITIVO, "📌 Seleccione el tipo de dispositivo:")
    
    nombre_disp = ""
    while True:
        nombre_disp = input(f"{Color.GREEN}↳ Ingrese el nombre del dispositivo: {Color.END}").strip()
        try:
            if validar_nombre(nombre_disp):
                break
        except ValueError as e:
            mostrar_mensaje(str(e), "error")
    
    ip_disp = None
    mascara_disp = None
    
    # ---- MODIFICACIÓN CLAVE AQUÍ ----
    # Se procede directamente a ingresar IP y máscara para TODOS los tipos de dispositivos.
    # El usuario puede omitir la IP dentro de ingresar_ip_y_mascara si lo desea.
    try:
        # Intenta obtener el nombre del tipo desde el string (ej. '💻 PC' -> 'PC')
        nombre_del_tipo_para_mensaje = tipo_seleccionado_str.split(' ', 1)[1] 
    except IndexError:
        nombre_del_tipo_para_mensaje = tipo_seleccionado_str # Fallback si no hay espacio

    print(f"\n{Color.CYAN}--- Configuración de Red para: {nombre_del_tipo_para_mensaje} ({nombre_disp}) ---{Color.END}")
    ip_disp, mascara_disp = ingresar_ip_y_mascara() 
    
    if ip_disp:
        mostrar_mensaje(f"IP {Color.YELLOW}{ip_disp}{Color.END} y Máscara {Color.YELLOW}{mascara_disp}{Color.END} procesadas para {nombre_disp}.", "exito")
    else:
        mostrar_mensaje(f"No se configuró IP ni Máscara para {nombre_disp}.", "info")
    # ---- FIN DE LA MODIFICACIÓN CLAVE ----
    
    capa_disp = None
    # La asignación de capa sigue siendo específica para ciertos tipos
    if tipo_seleccionado_str in [TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['SWITCH']]:
        capa_disp = seleccionar_opcion(CAPAS_RED, "📌 Seleccione la capa de red:")
    
    servicios_disp = []
    # La asignación de servicios sigue siendo específica para ciertos tipos
    if tipo_seleccionado_str in [TIPOS_DISPOSITIVO['SERVIDOR'], TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['FIREWALL']]:
        print(f"\n{Color.BOLD}🛠️ Agregar servicios:{Color.END}")
        
        servicios_seleccionables = SERVICIOS_VALIDOS.copy()
        clave_terminar = "TERMINAR_SVC" 
        servicios_seleccionables[clave_terminar] = "🏁 Terminar de agregar servicios"

        while True:
            servicio_elegido_str = seleccionar_opcion(servicios_seleccionables, "Seleccione un servicio o termine:")
            
            if servicio_elegido_str == servicios_seleccionables[clave_terminar]:
                break 
            
            if servicio_elegido_str not in servicios_disp:
                servicios_disp.append(servicio_elegido_str)
                mostrar_mensaje(f"Servicio {servicio_elegido_str} agregado.", "exito")
            else:
                mostrar_mensaje(f"El servicio {servicio_elegido_str} ya fue agregado.", "advertencia")
    
    return crear_dispositivo(tipo_seleccionado_str, nombre_disp, ip_disp, mascara_disp, capa_disp, servicios_disp)

def mostrar_dispositivos(dispositivos, titulo="LISTADO DE DISPOSITIVOS"):
    mostrar_titulo(titulo)
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")
        return
    
    for i, disp_str in enumerate(dispositivos, 1):
        nombre_encabezado = ""
        for linea in disp_str.split('\n'):
            if "NOMBRE:" in linea:
                try:
                    nombre_encabezado = linea.split("NOMBRE:")[1].split(Color.END)[-1].strip()
                    break
                except IndexError:
                    pass 
        
        print(f"{Color.YELLOW}{i}.{Color.END} {Color.BOLD}{nombre_encabezado}{Color.END if nombre_encabezado else ''}")
        print(disp_str) 
    
    input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")

def buscar_dispositivo(dispositivos):
    mostrar_titulo("BUSCAR DISPOSITIVO")
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        sleep(2)
        return
    
    nombre_buscado = input(f"{Color.GREEN}↳ Ingrese el nombre del dispositivo a buscar: {Color.END}").strip().lower()
    encontrados = []
    
    for d_str in dispositivos:
        nombre_actual = ""
        for linea in d_str.split('\n'):
            if "NOMBRE:" in linea:
                try:
                    nombre_actual = linea.split("NOMBRE:")[1].split(Color.END)[-1].strip().lower()
                    break 
                except IndexError:
                    continue 
        
        if nombre_buscado in nombre_actual:
            encontrados.append(d_str)
            
    if encontrados:
        mostrar_dispositivos(encontrados, "RESULTADOS DE LA BÚSQUEDA")
    else:
        mostrar_mensaje("No se encontraron dispositivos con ese nombre", "advertencia")
        sleep(2)

def agregar_servicio_dispositivo(dispositivos):
    mostrar_titulo("AGREGAR SERVICIO A DISPOSITIVO")
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        sleep(2)
        return
    
    print(f"{Color.BOLD}📋 Dispositivos disponibles para agregar servicio:{Color.END}")
    
    dispositivos_modificables = []
    indices_originales = []

    for i, disp_str in enumerate(dispositivos):
        tipo_disp = ""
        nombre_disp = ""
        for linea in disp_str.split('\n'):
            if "TIPO:" in linea:
                tipo_disp = linea.split("TIPO:")[1].split(Color.END)[-1].strip()
            elif "NOMBRE:" in linea:
                nombre_disp = linea.split("NOMBRE:")[1].split(Color.END)[-1].strip()
        
        if tipo_disp in [TIPOS_DISPOSITIVO['SERVIDOR'], TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['FIREWALL']]:
            dispositivos_modificables.append({'index': i, 'nombre': nombre_disp, 'str': disp_str})
            print(f"{Color.YELLOW}{len(dispositivos_modificables)}.{Color.END} {nombre_disp} ({tipo_disp})")

    if not dispositivos_modificables:
        mostrar_mensaje("No hay dispositivos (Servidor, Router, Firewall) a los que se les pueda agregar servicios.", "advertencia")
        sleep(2)
        return
    
    try:
        num_seleccion_str = input(f"\n{Color.GREEN}↳ Seleccione el número del dispositivo (1-{len(dispositivos_modificables)}): {Color.END}")
        num_seleccion = int(num_seleccion_str) - 1

        if 0 <= num_seleccion < len(dispositivos_modificables):
            disp_info = dispositivos_modificables[num_seleccion]
            idx_real_en_lista_original = disp_info['index']
            
            servicios_seleccionables = SERVICIOS_VALIDOS.copy()
            
            servicio_a_agregar_str = seleccionar_opcion(servicios_seleccionables, f"Seleccione el servicio a agregar a '{disp_info['nombre']}':")

            disp_original_str = dispositivos[idx_real_en_lista_original]
            lineas_disp = disp_original_str.split('\n')
            
            servicios_existentes_str = ""
            indice_linea_servicios = -1

            for j, linea in enumerate(lineas_disp):
                if f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END}" in linea:
                    servicios_existentes_str = linea.split(f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END}")[1].strip()
                    indice_linea_servicios = j
                    break
            
            if servicio_a_agregar_str in servicios_existentes_str.split(' '):
                mostrar_mensaje(f"El servicio '{servicio_a_agregar_str}' ya existe en este dispositivo.", "advertencia")
                sleep(2)
                return

            if indice_linea_servicios != -1: 
                nuevos_servicios = f"{servicios_existentes_str} {servicio_a_agregar_str}".strip()
                lineas_disp[indice_linea_servicios] = f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {nuevos_servicios}"
            else: 
                idx_insercion = len(lineas_disp) -1 
                for k_rev, linea_rev in reversed(list(enumerate(lineas_disp))):
                    if f"{Color.BLUE}{'═' * 60}{Color.END}" in linea_rev:
                        idx_insercion = k_rev
                        break
                lineas_disp.insert(idx_insercion, f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {servicio_a_agregar_str}")
            
            dispositivos[idx_real_en_lista_original] = "\n".join(lineas_disp)
            mostrar_mensaje(f"Servicio '{servicio_a_agregar_str}' agregado a '{disp_info['nombre']}' exitosamente!", "exito")
            sleep(2)
        else:
            mostrar_mensaje("Número de dispositivo inválido.", "error")
            sleep(2)
    except ValueError:
        mostrar_mensaje("Entrada inválida. Debe ingresar un número.", "error")
        sleep(2)

def eliminar_dispositivo(dispositivos):
    mostrar_titulo("ELIMINAR DISPOSITIVO")
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        sleep(2)
        return
    
    while True: 
        mostrar_titulo("SELECCIONE DISPOSITIVO A ELIMINAR") 
        print(f"{Color.BOLD}📋 Dispositivos disponibles:{Color.END}\n")
        
        nombres_dispositivos = []
        for i, disp_str in enumerate(dispositivos, 1):
            nombre_disp = f"Dispositivo {i} (Nombre no extraíble)" 
            for linea in disp_str.split('\n'):
                if "NOMBRE:" in linea:
                    try:
                        nombre_disp = linea.split("NOMBRE:")[1].split(Color.END)[-1].strip()
                        break
                    except IndexError: pass
            nombres_dispositivos.append(nombre_disp)
            print(f"{Color.YELLOW}{i}.{Color.END} {nombre_disp}")
        
        print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
        
        try:
            opcion_str = input(f"\n{Color.GREEN}↳ Seleccione el dispositivo a eliminar (1-{len(dispositivos)}) o 0 para cancelar: {Color.END}").strip()
            
            if opcion_str == "0":
                mostrar_mensaje("Operación cancelada.", "info")
                sleep(2)
                return 
            
            num_seleccion = int(opcion_str) - 1 
            
            if 0 <= num_seleccion < len(dispositivos):
                nombre_a_eliminar = nombres_dispositivos[num_seleccion]
                                
                print(f"\n{Color.RED}{'⚠' * 30} CONFIRMACIÓN {'⚠' * 30}{Color.END}") 
                confirmar = input(f"{Color.RED}{Color.BOLD}¿Está SEGURO que desea eliminar el dispositivo '{nombre_a_eliminar}'? (S/N): {Color.END}").upper()
                print(f"{Color.RED}{'⚠' * 68}{Color.END}") 
                
                if confirmar == 'S':
                    eliminado = dispositivos.pop(num_seleccion)
                    mostrar_mensaje(f"Dispositivo '{nombre_a_eliminar}' eliminado exitosamente.", "exito")
                    sleep(2)
                    return 
                elif confirmar == 'N':
                    mostrar_mensaje("Eliminación cancelada por el usuario.", "info")
                    sleep(2)
                    return 
                else:
                    mostrar_mensaje("Opción de confirmación inválida. Por favor ingrese S o N.", "error")
                    sleep(2) 
            else:
                mostrar_mensaje(f"Número inválido. Por favor ingrese un número entre 1 y {len(dispositivos)}, o 0 para cancelar.", "error")
                sleep(2) 
        except ValueError:
            mostrar_mensaje("Entrada inválida. Por favor ingrese un número.", "error")
            sleep(2)

def main():
    dispositivos = []
    
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Color.GREEN}↳ Seleccione una opción (1-7): {Color.END}").strip()
        
        if opcion == "1":
            nuevo_dispositivo_str = agregar_dispositivo_interactivo()
            if nuevo_dispositivo_str and not "❌ Error" in nuevo_dispositivo_str: 
                dispositivos.append(nuevo_dispositivo_str)
                # Los mensajes de éxito/info más específicos ya están dentro de agregar_dispositivo_interactivo
                # o ingresar_ip_y_mascara, por lo que un mensaje genérico aquí puede ser redundante
                # o se puede mantener uno muy breve.
                # mostrar_mensaje("Procesamiento de nuevo dispositivo completado.", "info") 
                sleep(1) 
            elif nuevo_dispositivo_str and "❌ Error" in nuevo_dispositivo_str:
                print(nuevo_dispositivo_str) 
                input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")
        
        elif opcion == "2":
            mostrar_dispositivos(dispositivos)
        
        elif opcion == "3":
            buscar_dispositivo(dispositivos)
        
        elif opcion == "4":
            agregar_servicio_dispositivo(dispositivos)
        
        elif opcion == "5":
            eliminar_dispositivo(dispositivos)
        
        elif opcion == "6":
            generar_reporte(dispositivos)
        
        elif opcion == "7":
            mostrar_mensaje("Saliendo del sistema... ¡Hasta pronto! 👋", "info")
            sleep(2)
            limpiar_pantalla()
            break
        
        else:
            mostrar_mensaje("Opción inválida. Por favor seleccione una opción del 1 al 7.", "error")
            sleep(2)

if __name__ == "__main__":
    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'BIENVENIDO AL SISTEMA DE GESTIÓN DE DISPOSITIVOS'.center(60)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}")
    sleep(2)
    main()