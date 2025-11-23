# ☁️ Configuración Específica para Google Cloud Platform (GCP)

Al estar usando una instancia **e2-medium** con **Debian 12**, sigue estos pasos adicionales para asegurar que todo funcione.

## 1️⃣ Configuración de Red (Firewall)
**¡CRÍTICO!** Antes de crear la instancia (o editándola después):
1.  Busca la sección **"Firewall"** (generalmente bajo "Redes" o al final del formulario de creación).
2.  Marca las casillas:
    - [x] **Permitir tráfico HTTP**
    - [x] **Permitir tráfico HTTPS**
3.  Sin esto, tu sitio no será accesible desde internet.

## 2️⃣ Dirección IP Estática
Por defecto, GCP te da una IP "efímera" que cambia si reinicias la máquina. Para un servidor de producción, necesitas una IP fija.
1.  Ve al menú de hamburguesa ☰ -> **Red de VPC** -> **Direcciones IP**.
2.  Busca la IP externa de tu instancia `ins-demoyikkan`.
3.  Haz clic en "Reservar" (o cambia el tipo de "Efímera" a "Estática").
4.  Asigna un nombre (ej: `ip-yikkan-prod`).
5.  **Actualiza tu DNS:** Ve a tu proveedor de dominio (HostGator) y apunta el registro **A** de `yikkan.com` y `www` a esta nueva IP estática.

## 3️⃣ Instalar Docker en Debian 12 (Bookworm)
Una vez conectado por SSH a tu instancia, ejecuta estos comandos bloque por bloque:

### A. Preparar el sistema
```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
```

### B. Agregar la llave GPG oficial de Docker
```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

### C. Configurar el repositorio
```bash
echo \
  "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### D. Instalar Docker Engine
```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### E. Probar instalación
```bash
sudo docker run hello-world
```

## 4️⃣ Subir tu Código
Tienes dos opciones principales:

### Opción A: Usar Git (Recomendado)
1.  Sube tu código a GitHub/GitLab (puede ser un repo privado).
2.  En el servidor GCP:
    ```bash
    git clone https://github.com/tu-usuario/tu-repo.git
    cd tu-repo
    ```

### Opción B: Copiar archivos directamente (SCP)
Desde tu terminal local (en tu Mac), ejecuta:
```bash
# Sube todo el contenido de la carpeta actual a la carpeta home del servidor
gcloud compute scp --recurse ./ ins-demoyikkan:~/uz-checkpoint --zone=northamerica-south1-a
```
*(Asegúrate de ajustar la zona si es diferente).*

---
Una vez tengas el código en el servidor y Docker instalado, continúa con el paso 1 de la guía `DEPLOY.md`.
