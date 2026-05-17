# proyecto-mortalidad - Dashboard de Mortalidad en Colombia 2019

## Introducción
Aplicación web interactiva desarrollada con Python, Dash y Plotly para el análisis
de datos de mortalidad no fetal en Colombia durante el año 2019.

## Objetivo
Explorar visualmente patrones de mortalidad a nivel departamental y municipal,
identificando las principales causas de muerte, distribución por sexo, edad y
variaciones a lo largo del año.

## Estructura del proyecto
```
proyecto-mortalidad/
├── app.py               # Layout de Dash y registro de callbacks
├── data_loader.py       # Carga, limpieza y preparación de datos
├── figures.py           # Funciones que generan cada figura Plotly
├── requirements.txt     # Dependencias Python
├── Procfile             # Comando de inicio para Render
└── data/
    ├── Anezo1.NoFetal2019_CE_15-03-23.xlsx
    ├── Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx
    ├── DiviPola_CE.xlsx
    └── colombia_departamentos.geojson
```

## Requisitos
| Librería   | Versión |
|------------|---------|
| dash       | 2.17.1  |
| plotly     | 5.22.0  |
| pandas     | 2.2.2   |
| openpyxl   | 3.1.2   |
| gunicorn   | 22.0.0  |

## Instalación local
```bash
git clone https://github.com/<usuario>/<repositorio>.git
cd proyecto-mortalidad
pip install -r requirements.txt
python app.py
```
La app quedará disponible en `http://localhost:8050`

## Despliegue en Render
1. Subir el repositorio a GitHub (incluir la carpeta `data/`).
2. Crear cuenta en [Render](https://render.com) y seleccionar **New Web Service**.
3. Conectar el repositorio de GitHub.
4. Configurar:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:server`
5. Render asigna una URL pública automáticamente.

> **Nota:** En el plan gratuito de Render la app se duerme tras 15 minutos de
> inactividad. La primera carga puede tardar ~30 segundos.

## Software utilizado
- Python 3.11
- Dash 2.17
- Plotly 5.22
- Pandas 2.2

## Gráficas principales

### Distribución geográfica
<img width="1173" height="504" alt="image" src="https://github.com/user-attachments/assets/cc2033b3-fe73-40a6-8d0b-ffe5c913d625" />

### Tendencia Mensual | Ciudades más violentas
<img width="1208" height="531" alt="image" src="https://github.com/user-attachments/assets/2f0a9ec6-160b-4b8a-b5cc-62bbd1a29c1a" />

### Menor índice de mortalidad | Top 10 Causas de muerte
<img width="1208" height="596" alt="image" src="https://github.com/user-attachments/assets/9782dca5-eb2c-487e-af79-ddce021dfa80" />







