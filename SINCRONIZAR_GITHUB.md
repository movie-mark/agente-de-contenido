# 🔄 Sincronizar con GitHub

**IMPORTANTE:** Este proyecto usa **GitHub como fuente de verdad**. Siempre mantén tu repositorio local sincronizado con GitHub.

## ✅ Verificar Estado de Sincronización

### Método Rápido (Recomendado)

Ejecuta estos comandos para verificar si tu repositorio local está actualizado:

```bash
# 1. Verificar estado local
git status

# 2. Traer información del remoto (sin modificar archivos)
git fetch origin

# 3. Comparar commits locales vs remotos
git log HEAD..origin/main --oneline
git log origin/main..HEAD --oneline
```

**Interpretación:**
- Si `git log HEAD..origin/main` muestra commits → **Hay cambios en GitHub que no tienes localmente**
- Si `git log origin/main..HEAD` muestra commits → **Tienes commits locales que no están en GitHub**
- Si ambos están vacíos → **Estás sincronizado** ✅

### Método Visual

```bash
# Ver gráfico de commits (local vs remoto)
git log --oneline --graph --all -10
```

## 🔄 Actualizar Repositorio Local

**SIEMPRE actualiza tu repositorio local antes de trabajar:**

```bash
# Opción 1: Fetch + Pull (recomendado)
git fetch origin
git pull origin main

# Opción 2: Pull directo
git pull origin main
```

## 📤 Subir Cambios a GitHub

**Después de hacer cambios localmente:**

```bash
# 1. Ver qué archivos cambiaron
git status

# 2. Agregar archivos al staging
git add .

# 3. Hacer commit
git commit -m "Descripción de los cambios"

# 4. Subir a GitHub
git push origin main
```

## ⚠️ Resolver Conflictos

Si hay conflictos al hacer pull:

```bash
# 1. Ver el estado
git status

# 2. Resolver conflictos manualmente en los archivos marcados

# 3. Después de resolver, agregar los archivos
git add .

# 4. Completar el merge
git commit

# 5. Subir los cambios
git push origin main
```

## 🔍 Verificar Última Versión en GitHub

Si quieres verificar directamente en GitHub sin usar git:

1. Ve a: https://github.com/movie-mark/agente-de-contenido
2. Revisa el último commit en la rama `main`
3. Compara el SHA del último commit con tu local:
   ```bash
   git log -1 --oneline
   ```

## 📋 Checklist de Sincronización

Antes de empezar a trabajar, verifica:

- [ ] `git status` muestra "working tree clean"
- [ ] `git fetch origin` no trae nuevos commits
- [ ] `git log HEAD..origin/main` está vacío
- [ ] Tu rama está actualizada: `git status` muestra "Your branch is up to date with 'origin/main'"

## 🚨 Si el Repositorio Local Está Desactualizado

**SIEMPRE usa la versión de GitHub como fuente de verdad:**

```bash
# 1. Descartar cambios locales no guardados (CUIDADO: esto elimina cambios)
git restore .

# 2. Actualizar desde GitHub
git fetch origin
git reset --hard origin/main
```

**⚠️ ADVERTENCIA:** `git reset --hard` elimina todos los cambios locales no guardados. Úsalo solo si estás seguro de que quieres descartar tus cambios locales.

## 💡 Buenas Prácticas

1. **Siempre hacer `git pull` antes de empezar a trabajar**
2. **Hacer commits frecuentes y descriptivos**
3. **Hacer `git push` regularmente para no perder trabajo**
4. **Si hay dudas, GitHub es la fuente de verdad**

## 🔗 Información del Repositorio

- **URL del repositorio:** https://github.com/movie-mark/agente-de-contenido
- **Rama principal:** `main`
- **Remoto:** `origin` (git@github.com:movie-mark/agente-de-contenido.git)

---

**Última actualización:** 2025-12-18
