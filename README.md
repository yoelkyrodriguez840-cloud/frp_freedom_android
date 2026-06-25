# FRP Freedom Android

Android FRP Bypass Tool - Recupera el acceso a tu dispositivo bloqueado

## Descripción

FRP Freedom Android es una herramienta diseñada para recuperar el acceso a un dispocitivo bloqueado por credenciales de Google.

## Características

- **Detección automática de dispositivos** - Escanea dispositivos USB conectados
- **Múltiples métodos de bypass** - ADB, Interfaz, Sistema
- **Análisis IA** - Recomendaciones inteligentes
- **Interfaz nativa Android** - Optimizada para pantallas táctiles
- **Seguimiento de progreso** - Visualización en tiempo real
- **Seguridad** - Logs cifrados y auditoría

## Instalación

### Desde APK

1. Descarga la última APK de [Releases](https://github.com/frp-freedom/frp-freedom-android/releases)
2. Habilita "Instalar desde orígenes desconocidos" en tu dispositivo
3. Instala la APK

### Desde código fuente

```bash
git clone https://github.com/yoelkyrodriguez840-cloud/frp-freedom-android.git
cd frp-freedom-android
pip install -r requirements.txt
python android_app.py
```

Construcción de APK

```bash
# Instalar dependencias
pip install flet

# Construir APK
flet build apk

# La APK estará en build/app-release.apk
```

Uso

1. Conecta tu dispositivo vía USB
2. Habilita USB Debugging en Opciones de Desarrollador
3. Abre FRP Freedom
4. Selecciona tu dispositivo
5. Elige los métodos de bypass
6. Ejecuta el bypass

Advertencias

⚠️ Esta herramienta es solo para propósitos educativos y de recuperación legítima de dispositivos. No debe usarse para acceder a dispositivos sin autorización.

Licencia

GNU License - Ver archivo LICENSE

Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

Enlaces

· Documentación
· Soporte
· GitHub
