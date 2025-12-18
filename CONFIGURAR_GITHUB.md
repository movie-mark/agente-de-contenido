# Configurar GitHub en Cursor

Esta guía te ayudará a configurar Cursor para que pueda crear repositorios en GitHub automáticamente.

## ✅ Verificar Configuración Actual

**Para verificar si tu SSH key está configurada:**
```bash
ssh -T git@github.com
```

Si ves "Hi [usuario]! You've successfully authenticated", tu SSH está funcionando.

**Para configurar Git para usar SSH por defecto:**
```bash
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

**Para crear repositorios automáticamente, necesitas un token de acceso personal (solo para crear repos, luego todo funciona con SSH).**

---

## Opción 1: Usar SSH (Ya configurado ✅)

**Para push/pull/clone:** Ya está funcionando con SSH. No necesitas hacer nada más.

**Para crear repositorios:** Necesitas crear el repo manualmente en GitHub (1 minuto) o usar un token (ver Opción 2).

### Crear repositorio manualmente y conectarlo:
1. Ve a https://github.com/new
2. Crea el repositorio (elige el nombre que prefieras)
3. **NO** marques "Initialize with README"
4. Copia la URL SSH que aparece (formato: `git@github.com:TU_USUARIO/NOMBRE_REPO.git`)
5. Conecta el repositorio:
   ```bash
   git remote add origin git@github.com:TU_USUARIO/NOMBRE_REPO.git
   git push -u origin main
   ```

---

## Opción 2: Token de Acceso Personal (Para crear repos automáticamente)

Si quieres que Cursor pueda crear repositorios automáticamente, necesitas un token:

## Paso 1: Crear un Token de Acceso Personal de GitHub

1. **Ve a la configuración de tokens de GitHub:**
   - Abre: https://github.com/settings/tokens
   - O ve a: GitHub → Tu perfil (arriba derecha) → Settings → Developer settings → Personal access tokens → Tokens (classic)

2. **Crear un nuevo token:**
   - Haz clic en "Generate new token" → "Generate new token (classic)"
   - Dale un nombre descriptivo: `Cursor GitHub Access`
   - Selecciona la expiración (recomendado: 90 días o "No expiration" si es solo para uso personal)

3. **Seleccionar permisos (scopes):**
   Marca estos permisos:
   - ✅ `repo` (Full control of private repositories)
     - Esto incluye: repo:status, repo_deployment, public_repo, repo:invite, security_events
   - ✅ `workflow` (Update GitHub Action workflows) - opcional pero útil

4. **Generar y copiar el token:**
   - Haz clic en "Generate token" al final de la página
   - **⚠️ IMPORTANTE:** Copia el token inmediatamente. Solo se muestra una vez.
   - Guárdalo en un lugar seguro (como un gestor de contraseñas)

## Paso 2: Configurar el Token en Cursor

Tienes dos opciones para configurar el token:

### Opción A: Variable de Entorno (Recomendada)

1. **Crear/editar archivo de configuración del shell:**
   
   Si usas **bash** (por defecto en macOS):
   ```bash
   nano ~/.bash_profile
   ```
   
   O si usas **zsh** (macOS moderno):
   ```bash
   nano ~/.zshrc
   ```

2. **Agregar el token como variable de entorno:**
   Agrega esta línea al final del archivo:
   ```bash
   export GITHUB_TOKEN="tu_token_aqui"
   ```
   
   Reemplaza `tu_token_aqui` con el token que copiaste en el Paso 1.

3. **Guardar y recargar:**
   - Presiona `Ctrl + X`, luego `Y`, luego `Enter` para guardar
   - Recarga la configuración:
     ```bash
     source ~/.bash_profile
     ```
     O si usas zsh:
     ```bash
     source ~/.zshrc
     ```

4. **Verificar que funciona:**
   ```bash
   echo $GITHUB_TOKEN
   ```
   Debería mostrar tu token.

### Opción B: Configurar Git Credential Helper

1. **Configurar Git para usar el token:**
   ```bash
   git config --global credential.helper store
   ```

2. **O usar el token directamente en la URL del remoto:**
   Cuando agregues un remoto, usa este formato:
   ```bash
   git remote add origin https://TU_TOKEN@github.com/USUARIO/REPO.git
   ```

## Paso 3: Verificar la Configuración

Para verificar que todo funciona, puedes probar crear un repositorio de prueba:

```bash
# Esto debería funcionar si el token está configurado correctamente
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

Si ves información de tu usuario, ¡está funcionando!

## Paso 4: Usar en Cursor

Una vez configurado el token como variable de entorno, Cursor podrá:
- Crear repositorios automáticamente
- Hacer push a GitHub
- Gestionar repositorios sin pedirte credenciales

## Notas de Seguridad

⚠️ **IMPORTANTE:**
- **NUNCA** subas el token a GitHub o lo compartas públicamente
- El archivo `.env` ya está en `.gitignore`, pero el token NO debe ir ahí
- Si el token se compromete, revócalo inmediatamente en GitHub
- Usa tokens con expiración para mayor seguridad

## Solución de Problemas

### El token no funciona
- Verifica que el token tenga el permiso `repo`
- Asegúrate de haber recargado la configuración del shell (`source ~/.bash_profile` o `source ~/.zshrc`)
- Verifica que la variable esté disponible: `echo $GITHUB_TOKEN`

### Cursor no detecta el token
- Reinicia Cursor después de configurar la variable de entorno
- Verifica que Cursor esté usando el mismo shell donde configuraste la variable

### Token expirado
- Ve a https://github.com/settings/tokens
- Genera un nuevo token
- Actualiza la variable de entorno con el nuevo token
