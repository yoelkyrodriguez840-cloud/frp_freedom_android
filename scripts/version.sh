#!/bin/bash
# ============================================
# SCRIPT PARA ACTUALIZAR LA VERSIÓN
# ============================================
# Uso: ./scripts/update_version.sh [nueva_version] [nuevo_build]
# Ejemplo: ./scripts/update_version.sh 1.0.1 2
# ============================================

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "  🔄 ACTUALIZADOR DE VERSIÓN FRP FREEDOM"
echo "================================================"

# Obtener la nueva versión desde argumentos o preguntar
if [ -z "$1" ]; then
  read -p "📦 Nueva versión (ej: 1.0.1): " NEW_VERSION
else
  NEW_VERSION="$1"
fi

if [ -z "$2" ]; then
  read -p "🔢 Nuevo número de build (ej: 2): " NEW_BUILD
else
  NEW_BUILD="$2"
fi

# Validar formato de versión
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
  echo -e "${RED}❌ Error: Versión inválida. Debe ser formato MAJOR.MINOR.PATCH${NC}"
  echo "Ejemplo: 1.0.0, 2.1.3"
  exit 1
fi

# Validar número de build
if ! [[ "$NEW_BUILD" =~ ^[0-9]+$ ]]; then
  echo -e "${RED}❌ Error: Número de build inválido. Debe ser un número entero${NC}"
  exit 1
fi

echo ""
echo "📋 Resumen de cambios:"
echo "   Versión: $NEW_VERSION"
echo "   Build: $NEW_BUILD"
echo ""

read -p "¿Continuar? (s/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[sS]$ ]]; then
  echo -e "${YELLOW}⚠️ Operación cancelada${NC}"
  exit 0
fi

echo ""
echo -e "${GREEN}🔄 Actualizando archivos...${NC}"

# 1. Actualizar version.env
echo "   📝 Actualizando version.env..."
sed -i "s/^APP_VERSION=.*/APP_VERSION=$NEW_VERSION/" version.env
sed -i "s/^BUILD_NUMBER=.*/BUILD_NUMBER=$NEW_BUILD/" version.env

# 2. Actualizar pyproject.toml
echo "   📝 Actualizando pyproject.toml..."
sed -i "s/^version = \".*\"/version = \"$NEW_VERSION\"/" pyproject.toml

# 3. Actualizar flet_config.yaml
echo "   📝 Actualizando flet_config.yaml..."
sed -i "s/version: \${APP_VERSION:-.*}/version: \${APP_VERSION:-$NEW_VERSION}/" flet_config.yaml
sed -i "s/build_number: \${BUILD_NUMBER:-.*}/build_number: \${BUILD_NUMBER:-$NEW_BUILD}/" flet_config.yaml

# 4. Actualizar build.gradle (si existe)
if [ -f "build.gradle" ]; then
  echo "   📝 Actualizando build.gradle..."
  sed -i "s/versionName System.getenv('APP_VERSION') ?: \".*\"/versionName System.getenv('APP_VERSION') ?: \"$NEW_VERSION\"/" build.gradle
fi

echo ""
echo -e "${GREEN}✅ ¡Versión actualizada exitosamente!${NC}"
echo ""
echo "📊 Nuevos valores:"
echo "   Versión: $NEW_VERSION"
echo "   Build: $NEW_BUILD"
echo ""
echo "📝 Archivos modificados:"
echo "   - version.env"
echo "   - pyproject.toml"
echo "   - flet_config.yaml"
if [ -f "build.gradle" ]; then
  echo "   - build.gradle"
fi
echo ""
echo "💡 Recuerda:"
echo "   - Commitear los cambios"
echo "   - Los tags se generarán automáticamente en CI/CD"
echo "   - Si usas GitHub Actions, la versión se tomará de las variables de entorno"
