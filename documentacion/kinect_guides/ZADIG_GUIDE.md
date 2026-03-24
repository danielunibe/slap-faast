# Guía: Instalar Driver WinUSB para Kinect v1

## ¿Por qué necesitamos esto?
Para que Slap!Faast controle el Kinect **sin el SDK de Microsoft**, necesitamos cambiar el driver USB de "Microsoft Kinect" a "WinUSB".

## Herramienta: Zadig
**Zadig** es una aplicación portable (no requiere instalación) que cambia drivers USB en Windows.

---

## Pasos (5 minutos)

### 1. Ejecutar Zadig
- Abre `zadig.exe` (está en la carpeta del proyecto)
- **IMPORTANTE:** Ejecútalo como Administrador (clic derecho → "Run as administrator")

### 2. Activar modo de listado completo
- En el menú superior: **Options** → **List All Devices** ✅

### 3. Seleccionar Kinect Camera
- En el dropdown superior, busca y selecciona:
  - **"Xbox NUI Camera"** o  
  - **"Kinect for Windows Camera"** o
  - Cualquier dispositivo con VID `045E` y PID `02AE` o `02B0`

### 4. Elegir WinUSB
- En la parte central, verás dos dropdowns:
  - **Izquierda:** Driver actual (probablemente "Microsoft")
  - **Derecha:** Driver a instalar → Selecciona **"WinUSB"**

### 5. Instalar
- Click en el botón grande **"Replace Driver"** o **"Install Driver"**
- Espera ~30 segundos
- Verás "Driver installed successfully"

### 6. Repetir para Motor (opcional)
Si quieres control del motor/LED:
- Selecciona **"Xbox NUI Motor"** (VID `045E` PID `02B0`)
- Instalar **WinUSB** también
  
---

## Verificación
Después de instalar:
1. Cierra Zadig
2. Ejecuta `python src/sensors/kinect_usb_driver.py`
3. Deberías ver:
   ```
   ✅ Kinect conectado via USB
   ```

---

## Notas Importantes
- ⚠️ Esto **no afecta** el funcionamiento del Kinect en Xbox
- ⚠️ Si quieres volver al driver de Microsoft, usa Zadig y selecciona "Microsoft Kinect" en lugar de WinUSB
- ✅ Este cambio es **permanente** hasta que lo reviertas
- ✅ Solo necesitas hacerlo **una vez** por PC
