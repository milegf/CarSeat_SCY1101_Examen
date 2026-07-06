# Car Seats - Evaluación Parcial N°3 (SCY1101)

Solución end-to-end de análisis de ventas para el dataset Car Seats: pipeline ETL con dos fuentes de datos (CSV + API de tipo de cambio), análisis exploratorio, dashboard interactivo con Plotly Dash y modelos supervisados para predecir si una tienda tendrá ventas altas o bajas.

**Asignatura:** SCY1101 - Programación para la Ciencia de Datos

## Estructura del Proyecto

```
.
├── data/
│   ├── raw/                 # dataset_car_seats.csv (original, sin modificar)
│   └── processed/           # carseats_clp.csv (salida del ETL: CLP + HighSales)
├── notebooks/
│   └── CarSeats_Ev3.ipynb   # Notebook principal: ETL, EDA, preparación y modelos
├── src/
│   └── dashboard.py         # Archivo de la entrega anterior (sin uso, sección 3 en notebook principal)
├── docs/
│   ├── Arquitectura.pdf     # Comparación de arquitecturas y justificación
│   ├── Docker.pdf           # Investigación de Docker en ciencia de datos
│   ├── Informe_examen.pdf   # Informe del proyecto (metodología CRISP-DM)
│   ├── CarSeats_ppt.pdf     # Presentación del proyecto
│   └── img/                 # Diagramas usados en Arquitectura.pdf
├── requirements.txt
└── README.md
```

## Requisitos

- Python 3.11
- Dependencias listadas en `requirements.txt`, con versiones fijadas para reproducibilidad

## Instalación

```bash
pip install -r requirements.txt
```

## Cómo Ejecutar el Notebook

```bash
jupyter notebook notebooks/CarSeats_Ev3.ipynb
```

Se recomienda **Kernel → Restart & Run All** para verificar que corre de principio a fin sin errores. El notebook cubre, en orden: importaciones, pipeline ETL (Sección 1), análisis exploratorio (Sección 2), dashboard con Plotly Dash (Sección 3), preparación de datos (Sección 4), modelos supervisados (Sección 5) y conclusiones generales (Sección 6).

El notebook genera `data/processed/carseats_clp.csv` en la Sección 1 (ETL), y ese mismo archivo es el que consume el dashboard de la Sección 3.

## Cómo Ejecutar el Dashboard

El dashboard corre desde el notebook (Sección 3), usando `app.run(jupyter_mode="external")`: el servidor se levanta en un hilo de fondo sin bloquear el kernel, por lo que "Run All" sigue ejecutando con normalidad las secciones de modelos y conclusiones. La celda imprime un enlace local (`http://127.0.0.1:8050`) que se abre en una pestaña del navegador, no un iframe embebido dentro del notebook.

**Solo local:**

```bash
jupyter notebook notebooks/CarSeats_Ev3.ipynb
```

Kernel → Restart & Run All. El dashboard queda disponible en `http://127.0.0.1:8050` mientras el kernel siga corriendo. Con `USE_NGROK = True` (valor por defecto en la celda de la Sección 3) también se intenta abrir un túnel público de ngrok; si no hay token configurado, falla en silencio y el enlace local sigue funcionando igual.

**Local + túnel público con ngrok:**

El authtoken de ngrok se configura **una sola vez por máquina/usuario**, fuera del notebook y del repositorio, para que no quede expuesto en ningún archivo:

```bash
ngrok config add-authtoken TU_TOKEN
```

Esto guarda el token en el archivo de configuración local de ngrok (`~/.config/ngrok/ngrok.yml` o equivalente según el sistema operativo), que el notebook lee automáticamente al llamar a `ngrok.connect()` — sin depender de variables de entorno ni de en qué terminal se inició Jupyter. Con eso ya configurado, basta con `USE_NGROK = True` (Kernel → Restart & Run All) para que se genere la URL pública junto al enlace local.

Si el túnel falla (por ejemplo, no se corrió `ngrok config add-authtoken` en esa máquina, o no hay internet), la celda lo indica en la salida y recuerda revisar la configuración de ngrok; el dashboard local sigue funcionando igual, solo no se genera la URL pública.

**Para detener el servidor:** Kernel → Shut Down Kernel (o Restart Kernel) desde la interfaz de Jupyter, o `Ctrl+C` en la terminal donde corre `jupyter notebook` para apagar todos los kernels.

> Si se cambia `USE_NGROK` o se configura el authtoken después de haber corrido el notebook, use Kernel → Restart & Run All (no solo re-ejecutar la celda), para asegurar que el servidor arranque limpio en ese kernel.

> `src/dashboard.py` es el archivo de la entrega anterior. Se mantiene en el repositorio como referencia con la misma lógica, pero ya no está conectado al notebook y no es necesario ejecutarlo, todo el dashboard se encuentra en la Sección 3 del notebook.

## Documentación Adicional

- **`docs/Arquitectura.pdf`**: compara las arquitecturas Lambda, Lakehouse y Pipeline Híbrido Modular, y justifica por qué esta última es la utilizada en el proyecto.
- **`docs/Docker.pdf`**: investigación sobre Docker en ciencia de datos.
- **`docs/Informe_examen.pdf`**: informe sobre el proyecto realizado en base a la metodología CRISP-DM.

## Resultados Principales

- **ETL:** conversión de 4 columnas monetarias de USD a CLP vía API (con fallback en cadena), y creación de la variable objetivo `HighSales` (59% bajas / 41% altas).
- **EDA:** `ShelveLoc` es la variable más asociada a las ventas (15% de ventas altas en ubicación `Bad` vs 78% en `Good`); `Price` y `Advertising` son predictores secundarios consistentes.
- **Modelos:** Regresión Logística y Random Forest, ambos optimizados con `GridSearchCV`. La Regresión Logística obtiene el mejor desempeño (F1 = 0.90, ROC-AUC = 0.98 en test).

## Flujo de Trabajo con Git

Una rama por etapa del proyecto (`feature/etl`, `feature/eda`, `feature/dashboard`, `feature/modelos`, `docs`, `fix/manejo-nulos`, `fix/dashboard`), integradas en `develop` antes de llegar a `main`.
