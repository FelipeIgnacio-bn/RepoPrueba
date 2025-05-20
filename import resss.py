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
    
    for octeto in octetos:
        try:
            num = int(octeto)
            if not (0 <= num <= 255):
                raise ValueError(f"El octeto {num} no es válido (debe estar entre 0-255)")
        except ValueError:
            raise ValueError(f"'{octeto}' no es un número válido para un octeto de IP")
    
    # Verificación de rangos especiales
    primer_octeto = int(octetos[0])
    if primer_octeto == 0:
        raise ValueError("El primer octeto no puede ser 0 (reservado)")
    if primer_octeto == 127:
        raise ValueError("Las IPs 127.x.x.x están reservadas para loopback")
    if primer_octeto >= 224:
        if primer_octeto < 240:
            raise ValueError("Las IPs 224.x.x.x a 239.x.x.x están reservadas para multicast")
        else:
            raise ValueError("Las IPs 240.x.x.x y superiores están reservadas para uso futuro")
    
    # Verificación de direcciones especiales
    if ip == "255.255.255.255":
        raise ValueError("Esta IP está reservada para broadcast limitado")
    if octetos[3] == "255":
        raise ValueError("El último octeto no puede ser 255 (reservado para broadcast)")
    
    return True

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

# 🖥️ Función para crear dispositivo
def crear_dispositivo(tipo, nombre, ip=None, capa=None, servicios=None):
    try:
        validar_nombre(nombre)
        if ip:
            validar_ip(ip)
        if servicios:
            validar_servicios(servicios)
        
        dispositivo = [
            f"{Color.CYAN}🔧 {Color.BOLD}TIPO:{Color.END} {tipo}",
            f"{Color.CYAN}🏷️ {Color.BOLD}NOMBRE:{Color.END} {nombre}"
        ]
        
        if ip:
            dispositivo.append(f"{Color.CYAN}🌍 {Color.BOLD}IP:{Color.END} {ip}")
        if capa:
            dispositivo.append(f"{Color.CYAN}📊 {Color.BOLD}CAPA:{Color.END} {capa}")
        if servicios:
            dispositivo.append(f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {' '.join(servicios)}")
        
        separador = f"{Color.BLUE}{'═' * 60}{Color.END}"
        return f"\n{separador}\n" + "\n".join(dispositivo) + f"\n{separador}"
    
    except ValueError as e:
        return f"{Color.RED}❌ Error al crear dispositivo: {e}{Color.END}"

# 📊 Función para generar reporte estadístico
def generar_reporte(dispositivos):
    """Genera un reporte estadístico detallado de los dispositivos."""
    if not dispositivos:
        mostrar_mensaje("⚠️ No existen dispositivos registrados.", "advertencia")
        sleep(2)
        return
    
    mostrar_titulo("📊 REPORTE ESTADÍSTICO DETALLADO")
    
    # 1. Resumen general
    print(f"\n{Color.BOLD}{Color.PURPLE}📌 RESUMEN GENERAL{Color.END}")
    print(f"{Color.CYAN}📅 Total de dispositivos registrados:{Color.END} {len(dispositivos)}")
    print(f"{Color.CYAN}📅 Última actualización:{Color.END} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 2. Conteo por tipo con detalles
    print(f"\n{Color.BOLD}{Color.PURPLE}🔢 DISTRIBUCIÓN POR TIPO:{Color.END}")
    tipos = {}
    for disp in dispositivos:
        # Extraer tipo del dispositivo
        tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
        if tipo_linea:
            tipo = tipo_linea.split("TIPO:")[1].strip()
            tipos[tipo] = tipos.get(tipo, 0) + 1
    
    for tipo, cantidad in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        print(f"\n  {Color.YELLOW}{tipo.upper()} ({cantidad} dispositivos):{Color.END}")
        count = 0
        for disp in dispositivos:
            if count >= 3:  # Mostrar solo 3 ejemplos por tipo
                break
            tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
            if tipo_linea and tipo_linea.split("TIPO:")[1].strip() == tipo:
                # Extraer nombre del dispositivo
                nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
                if nombre_linea:
                    nombre = nombre_linea.split("NOMBRE:")[1].strip()
                    # Extraer IP si existe
                    ip_linea = next((linea for linea in disp.split('\n') if "IP:" in linea), None)
                    ip = ip_linea.split("IP:")[1].strip() if ip_linea else "Sin IP"
                    print(f"    - {nombre} ({ip})")
                    count += 1
        if cantidad > 3:
            print(f"    {Color.DARKCYAN}...y {cantidad-3} más{Color.END}")
    
    # 3. Conteo por capa con detalles
    print(f"\n{Color.BOLD}{Color.PURPLE}📡 DISTRIBUCIÓN POR CAPA DE RED:{Color.END}")
    capas = {}
    for disp in dispositivos:
        # Extraer capa del dispositivo
        capa_linea = next((linea for linea in disp.split('\n') if "CAPA:" in linea), None)
        capa = capa_linea.split("CAPA:")[1].strip() if capa_linea else "Sin capa especificada"
        capas[capa] = capas.get(capa, 0) + 1
    
    for capa, cantidad in sorted(capas.items(), key=lambda x: x[1], reverse=True):
        print(f"\n  {Color.YELLOW}{capa.upper()} ({cantidad} dispositivos):{Color.END}")
        count = 0
        for disp in dispositivos:
            if count >= 3:  # Mostrar solo 3 ejemplos por capa
                break
            current_capa_linea = next((linea for linea in disp.split('\n') if "CAPA:" in linea), None)
            current_capa = current_capa_linea.split("CAPA:")[1].strip() if current_capa_linea else "Sin capa especificada"
            if current_capa == capa:
                # Extraer nombre y tipo del dispositivo
                nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
                tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
                if nombre_linea and tipo_linea:
                    nombre = nombre_linea.split("NOMBRE:")[1].strip()
                    tipo = tipo_linea.split("TIPO:")[1].strip()
                    # Extraer servicios si existen
                    servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
                    servicios = servicios_linea.split("SERVICIOS:")[1].strip() if servicios_linea else "Ninguno"
                    print(f"    - {nombre} ({tipo}) con servicios: {servicios}")
                    count += 1
        if cantidad > 3:
            print(f"    {Color.DARKCYAN}...y {cantidad-3} más{Color.END}")
    
    # 4. Servicios más comunes con dispositivos que los usan
    print(f"\n{Color.BOLD}{Color.PURPLE}🛠️ SERVICIOS MÁS UTILIZADOS:{Color.END}")
    servicios = {}
    for disp in dispositivos:
        # Extraer servicios del dispositivo
        servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
        if servicios_linea:
            servicios_disp = servicios_linea.split("SERVICIOS:")[1].strip().split()
            for servicio in servicios_disp:
                servicios[servicio] = servicios.get(servicio, 0) + 1
    
    for servicio, cantidad in sorted(servicios.items(), key=lambda x: x[1], reverse=True):
        print(f"\n  {Color.YELLOW}{servicio} ({cantidad} dispositivos):{Color.END}")
        count = 0
        for disp in dispositivos:
            if count >= 3:  # Mostrar solo 3 ejemplos por servicio
                break
            servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
            if servicios_linea and servicio in servicios_linea:
                # Extraer nombre e IP del dispositivo
                nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
                ip_linea = next((linea for linea in disp.split('\n') if "IP:" in linea), None)
                if nombre_linea:
                    nombre = nombre_linea.split("NOMBRE:")[1].strip()
                    ip = ip_linea.split("IP:")[1].strip() if ip_linea else "Sin IP"
                    print(f"    - {nombre} ({ip})")
                    count += 1
        if cantidad > 3:
            print(f"    {Color.DARKCYAN}...usado por {cantidad-3} dispositivos más{Color.END}")
    
    # 5. Listado completo de dispositivos (resumido)
    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'📋 LISTADO COMPLETO DE DISPOSITIVOS'.center(60)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}")
    
    for i, disp in enumerate(dispositivos, 1):
        print(f"\n{Color.YELLOW}🔹 Dispositivo {i}:{Color.END}")
        # Extraer todos los campos del dispositivo
        tipo_linea = next((linea for linea in disp.split('\n') if "TIPO:" in linea), None)
        nombre_linea = next((linea for linea in disp.split('\n') if "NOMBRE:" in linea), None)
        ip_linea = next((linea for linea in disp.split('\n') if "IP:" in linea), None)
        capa_linea = next((linea for linea in disp.split('\n') if "CAPA:" in linea), None)
        servicios_linea = next((linea for linea in disp.split('\n') if "SERVICIOS:" in linea), None)
        
        if tipo_linea:
            print(f"  {Color.CYAN}🔧 Tipo:{Color.END} {tipo_linea.split('TIPO:')[1].strip()}")
        if nombre_linea:
            print(f"  {Color.CYAN}🏷️ Nombre:{Color.END} {nombre_linea.split('NOMBRE:')[1].strip()}")
        if ip_linea:
            print(f"  {Color.CYAN}🌍 IP:{Color.END} {ip_linea.split('IP:')[1].strip()}")
        if capa_linea:
            print(f"  {Color.CYAN}📊 Capa:{Color.END} {capa_linea.split('CAPA:')[1].strip()}")
        if servicios_linea:
            print(f"  {Color.CYAN}🛠️ Servicios:{Color.END} {servicios_linea.split('SERVICIOS:')[1].strip()}")
    
    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.GREEN}🎉 Reporte generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}\n")
    
    input(f"{Color.GREEN}Presione Enter para continuar...{Color.END}")

# 🎮 Funciones del menú interactivo
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
    for i, (key, value) in enumerate(opciones.items(), 1):
        print(f"{Color.YELLOW}{i}.{Color.END} {value}")
    
    while True:
        try:
            opcion = input(f"\n{Color.GREEN}↳ Seleccione una opción (1-{len(opciones)}): {Color.END}")
            opcion = int(opcion)
            if 1 <= opcion <= len(opciones):
                return list(opciones.values())[opcion-1]
            mostrar_mensaje(f"Por favor ingrese un número entre 1 y {len(opciones)}", "error")
        except ValueError:
            mostrar_mensaje("Entrada inválida. Por favor ingrese un número.", "error")

def ingresar_ip():
    while True:
        ip = input(f"{Color.GREEN}↳ Ingrese la dirección IP (deje vacío si no aplica): {Color.END}").strip()
        if not ip:
            return None
        
        try:
            validar_ip(ip)
            return ip
        except ValueError as e:
            mostrar_mensaje(f"❌ Error en la IP: {e}", "error")
            # Mostrar ejemplos de IPs válidas
            print(f"\n{Color.YELLOW}💡 Ejemplos de IPs válidas:{Color.END}")
            print(f"- {Color.CYAN}192.168.1.1{Color.END} (privada clase C)")
            print(f"- {Color.CYAN}10.0.0.1{Color.END} (privada clase A)")
            print(f"- {Color.CYAN}172.16.0.1{Color.END} (privada clase B)")
            print(f"- {Color.CYAN}8.8.8.8{Color.END} (DNS público de Google)")

def agregar_dispositivo_interactivo():
    mostrar_titulo("AGREGAR NUEVO DISPOSITIVO")
    
    # Seleccionar tipo
    tipo = seleccionar_opcion(TIPOS_DISPOSITIVO, "📌 Seleccione el tipo de dispositivo:")
    
    # Ingresar nombre
    while True:
        nombre = input(f"{Color.GREEN}↳ Ingrese el nombre del dispositivo: {Color.END}").strip()
        try:
            if validar_nombre(nombre):
                break
        except ValueError as e:
            mostrar_mensaje(str(e), "error")
    
    # Ingresar IP (solo para algunos dispositivos)
    ip = None
    if tipo in [TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['SERVIDOR'], TIPOS_DISPOSITIVO['FIREWALL']]:
        ip = ingresar_ip()
    
    # Seleccionar capa (solo para algunos dispositivos)
    capa = None
    if tipo in [TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['SWITCH']]:
        capa = seleccionar_opcion(CAPAS_RED, "📌 Seleccione la capa de red:")
    
    # Seleccionar servicios
    servicios = []
    if tipo in [TIPOS_DISPOSITIVO['SERVIDOR'], TIPOS_DISPOSITIVO['ROUTER'], TIPOS_DISPOSITIVO['FIREWALL']]:
        print(f"\n{Color.BOLD}🛠️ Agregar servicios (ingrese 0 cuando termine):{Color.END}")
        while True:
            servicio = seleccionar_opcion(SERVICIOS_VALIDOS, "Seleccione un servicio:")
            if servicio == SERVICIOS_VALIDOS['DNS'] and len(servicios) == 0:
                break  # Opción para salir
            if servicio not in servicios:
                servicios.append(servicio)
                mostrar_mensaje(f"Servicio {servicio} agregado", "exito")
            else:
                mostrar_mensaje("Este servicio ya fue agregado", "advertencia")
            
            continuar = input(f"{Color.GREEN}¿Agregar otro servicio? (s/n): {Color.END}").lower()
            if continuar != 's':
                break
    
    # Crear y retornar dispositivo
    return crear_dispositivo(tipo, nombre, ip, capa, servicios)

# 📋 Función para mostrar dispositivos
def mostrar_dispositivos(dispositivos, titulo="LISTADO DE DISPOSITIVOS"):
    mostrar_titulo(titulo)
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")
        return
    
    for i, disp in enumerate(dispositivos, 1):
        print(f"{Color.YELLOW}{i}.{Color.END}")
        # Extraer nombre de manera segura para el encabezado
        lineas = [linea.strip() for linea in disp.split('\n') if linea.strip()]
        nombre_linea = next((linea for linea in lineas if "NOMBRE:" in linea), None)
        if nombre_linea:
            partes_nombre = [parte.strip() for parte in nombre_linea.split(':') if parte.strip()]
            if len(partes_nombre) >= 2:
                print(f"Nombre: {partes_nombre[1]}")
        
        print(disp)
        print()
    
    input(f"\n{Color.GREEN}Presione Enter para continuar...{Color.END}")

# 🔍 Función para buscar dispositivos
def buscar_dispositivo(dispositivos):
    mostrar_titulo("BUSCAR DISPOSITIVO")
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        sleep(2)
        return
    
    nombre = input(f"{Color.GREEN}↳ Ingrese el nombre del dispositivo a buscar: {Color.END}")
    encontrados = []
    
    for d in dispositivos:
        try:
            lineas = [linea.strip() for linea in d.split('\n') if linea.strip()]
            nombre_linea = next((linea for linea in lineas if "NOMBRE:" in linea), None)
            if nombre_linea:
                partes_nombre = [parte.strip() for parte in nombre_linea.split(':') if parte.strip()]
                if len(partes_nombre) >= 2 and nombre.lower() in partes_nombre[1].lower():
                    encontrados.append(d)
        except:
            continue
    
    if encontrados:
        mostrar_dispositivos(encontrados, "RESULTADOS DE LA BÚSQUEDA")
    else:
        mostrar_mensaje("No se encontraron dispositivos con ese nombre", "advertencia")
        sleep(2)

# ➕ Función para agregar servicio
def agregar_servicio_dispositivo(dispositivos):
    mostrar_titulo("AGREGAR SERVICIO A DISPOSITIVO")
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        sleep(2)
        return
    
    print(f"{Color.BOLD}📋 Dispositivos disponibles:{Color.END}")
    dispositivos_validos = []
    
    for i, disp in enumerate(dispositivos, 1):
        try:
            lineas = [linea.strip() for linea in disp.split('\n') if linea.strip()]
            nombre_linea = next((linea for linea in lineas if "NOMBRE:" in linea), None)
            if nombre_linea:
                partes_nombre = [parte.strip() for parte in nombre_linea.split(':') if parte.strip()]
                if len(partes_nombre) >= 2:
                    nombre = partes_nombre[1]
                    print(f"{Color.YELLOW}{i}.{Color.END} {nombre}")
                    dispositivos_validos.append(disp)
        except:
            continue
    
    if not dispositivos_validos:
        mostrar_mensaje("No hay dispositivos válidos para modificar", "error")
        sleep(2)
        return
    
    try:
        num = input(f"\n{Color.GREEN}↳ Seleccione el número del dispositivo (1-{len(dispositivos_validos)}): {Color.END}")
        num = int(num) - 1
        if 0 <= num < len(dispositivos_validos):
            servicio = seleccionar_opcion(SERVICIOS_VALIDOS, "Seleccione el servicio a agregar:")
            
            # Encontrar el índice real en la lista original
            disp_real = dispositivos_validos[num]
            idx_real = dispositivos.index(disp_real)
            
            # Actualizar el dispositivo
            disp_lines = [linea.strip() for linea in dispositivos[idx_real].split('\n') if linea.strip()]
            servicio_line = next((i for i, line in enumerate(disp_lines) if "SERVICIOS:" in line), None)
            
            if servicio_line is not None:
                servicios = disp_lines[servicio_line].split("SERVICIOS: ")[1] + " " + servicio
                disp_lines[servicio_line] = f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {servicios}"
            else:
                disp_lines.insert(-1, f"{Color.CYAN}🛠️ {Color.BOLD}SERVICIOS:{Color.END} {servicio}")
            
            dispositivos[idx_real] = "\n".join(disp_lines)
            mostrar_mensaje("Servicio agregado exitosamente!", "exito")
            sleep(2)
        else:
            mostrar_mensaje("Número de dispositivo inválido", "error")
            sleep(2)
    except ValueError:
        mostrar_mensaje("Entrada inválida. Debe ingresar un número.", "error")
        sleep(2)

# ❌ Función mejorada para eliminar dispositivo
def eliminar_dispositivo(dispositivos):
    mostrar_titulo("ELIMINAR DISPOSITIVO")
    if not dispositivos:
        mostrar_mensaje("No hay dispositivos registrados", "advertencia")
        sleep(2)
        return
    
    while True:
        mostrar_titulo("SELECCIONE DISPOSITIVO A ELIMINAR")
        print(f"{Color.BOLD}📋 Dispositivos disponibles:{Color.END}\n")
        
        dispositivos_validos = []
        # Mostrar lista numerada de dispositivos
        for i, disp in enumerate(dispositivos, 1):
            try:
                # Extraer nombre del dispositivo de manera más segura
                lineas = [linea.strip() for linea in disp.split('\n') if linea.strip()]
                nombre_linea = next((linea for linea in lineas if "NOMBRE:" in linea), None)
                
                if nombre_linea:
                    partes_nombre = [parte.strip() for parte in nombre_linea.split(':') if parte.strip()]
                    if len(partes_nombre) >= 2:
                        nombre = partes_nombre[1]
                        print(f"{Color.YELLOW}{i}.{Color.END} {nombre}")
                        dispositivos_validos.append(disp)
                    else:
                        print(f"{Color.YELLOW}{i}.{Color.END} Dispositivo con formato inválido (nombre no encontrado)")
                else:
                    print(f"{Color.YELLOW}{i}.{Color.END} Dispositivo sin nombre")
            except Exception as e:
                print(f"{Color.YELLOW}{i}.{Color.END} Dispositivo con formato inválido (error: {str(e)})")
        
        if not dispositivos_validos:
            mostrar_mensaje("No hay dispositivos válidos para eliminar", "error")
            sleep(2)
            return
        
        print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
        
        try:
            opcion = input(f"\n{Color.GREEN}↳ Seleccione el dispositivo a eliminar (1-{len(dispositivos)}) o 0 para cancelar: {Color.END}").strip()
            
            if opcion == "0":
                mostrar_mensaje("Operación cancelada", "info")
                sleep(2)
                return
            
            num = int(opcion) - 1
            if 0 <= num < len(dispositivos):
                # Obtener nombre del dispositivo seleccionado de manera segura
                disp_seleccionado = dispositivos[num]
                lineas = [linea.strip() for linea in disp_seleccionado.split('\n') if linea.strip()]
                nombre_linea = next((linea for linea in lineas if "NOMBRE:" in linea), None)
                
                if nombre_linea:
                    partes_nombre = [parte.strip() for parte in nombre_linea.split(':') if parte.strip()]
                    nombre = partes_nombre[1] if len(partes_nombre) >= 2 else "dispositivo desconocido"
                else:
                    nombre = "dispositivo sin nombre"
                
                # Confirmación con estilo
                print(f"\n{Color.RED}{'⚠' * 60}{Color.END}")
                confirmar = input(f"{Color.RED}¿Está SEGURO que desea eliminar el dispositivo '{nombre}'? (Y/N): {Color.END}").upper()
                print(f"{Color.RED}{'⚠' * 60}{Color.END}")
                
                if confirmar == 'Y':
                    eliminado = dispositivos.pop(num)
                    mostrar_mensaje(f"Dispositivo '{nombre}' eliminado exitosamente", "exito")
                    sleep(2)
                    return
                elif confirmar == 'N':
                    mostrar_mensaje("Eliminación cancelada", "info")
                    sleep(2)
                    return
                else:
                    mostrar_mensaje("Opción inválida. Por favor ingrese Y o N", "error")
                    sleep(2)
            else:
                mostrar_mensaje(f"Por favor ingrese un número entre 1 y {len(dispositivos)}", "error")
                sleep(2)
        except ValueError:
            mostrar_mensaje("Entrada inválida. Por favor ingrese un número.", "error")
            sleep(2)

# 🎛️ Función principal
def main():
    dispositivos = []
    
    while True:
        mostrar_menu_principal()
        opcion = input(f"{Color.GREEN}↳ Seleccione una opción (1-7): {Color.END}")
        
        if opcion == "1":
            dispositivo = agregar_dispositivo_interactivo()
            if dispositivo and not "❌ Error" in dispositivo:
                dispositivos.append(dispositivo)
                mostrar_mensaje("Dispositivo agregado exitosamente!", "exito")
                sleep(2)
            elif dispositivo:
                print(dispositivo)
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
            mostrar_mensaje("Opción inválida. Por favor seleccione 1-7", "error")
            sleep(2)

if __name__ == "__main__":
    limpiar_pantalla()
    print(f"\n{Color.BLUE}{'═' * 60}{Color.END}")
    print(f"{Color.BOLD}{Color.PURPLE}{'BIENVENIDO AL SISTEMA DE GESTIÓN DE DISPOSITIVOS'.center(60)}{Color.END}")
    print(f"{Color.BLUE}{'═' * 60}{Color.END}")
    sleep(2)
    main()