# Guía Rápida: Instalar Driver para Kinect Camera

## Paso 1: Descargar Zadig
Ya tienes acceso - búscalo en tu carpeta de Descargas o descarga de: https://zadig.akeo.ie/

## Paso 2: Ejecutar Zadig como Administrador
1. Click derecho en `zadig.exe`
2. "Ejecutar como administrador"

## Paso 3: Listar TODOS los Dispositivos
1. En Zadig, ve a menú: **Options**
2. Marca: **List All Devices**

## Paso 4: Seleccionar el Dispositivo Correcto
En el dropdown grande arriba, busca y selecciona:
**"Xbox NUI Camera"** 

IMPORTANTE: Verifica que abajo diga:
- **USB ID: 045E 02AE** (esto confirma que es la cámara, no el motor)

## Paso 5: Seleccionar Driver
En el dropdown del MEDIO (donde dice el driver a instalar):
- Selecciona: **WinUSB** o **libusbK** (cualquiera funciona)

## Paso 6: Instalar
1. Click en el botón grande: **"Replace Driver"** o **"Install Driver"**
2. Espera 30-60 segundos
3. Debería decir "Driver installed successfully"

## Paso 7: Verificar
Cierra Zadig y yo ejecutaré un test automático para confirmar que funciona.

---

**NOTA CRÍTICA**: 
- Si ves "Xbox NUI Motor" (045E 02B0) → ESE NO, ese ya funciona
- Si ves "Xbox NUI Audio" (045E 02BB) → Ese tampoco
- Necesitas específicamente: **"Xbox NUI Camera" (045E 02AE)**
