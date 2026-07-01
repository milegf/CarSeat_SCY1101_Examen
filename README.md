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

Se recomienda **Kernel → Restart & Run All** para verificar que corre de principio a fin sin errores. El notebook cubre, en orden: importaciones, pipeline ETL (Sección 1), análisis exploratorio (Sección 2), dashboard embebido con Plotly Dash (Sección 3), preparación de datos (Sección 4), modelos supervisados (Sección 5) y conclusiones generales (Sección 6).

El notebook genera `data/processed/carseats_clp.csv` en la Sección 1 (ETL), y ese mismo archivo es el que consume el dashboard embebido en la Sección 3.

## Cómo Ejecutar el Dashboard

El dashboard corre directamente dentro del notebook (Sección 3), usando `app.run(jupyter_mode="inline")`, es decir, el servidor se levanta en un hilo de fondo sin bloquear el kernel, por lo que "Run All" sigue ejecutando con normalidad las secciones de modelos y conclusiones.

**Solo local:**

```bash
jupyter notebook notebooks/CarSeats_Ev3.ipynb
```

Con `USE_NGROK = False` (valor por defecto en la celda de la Sección 3), Kernel → Restart & Run All. El dashboard queda dentro de esta sección y disponible en `http://127.0.0.1:8050` mientras el kernel siga corriendo.

**Local + túnel público con ngrok, desde el inicio:**

```bash
export NGROK_AUTHTOKEN=tu_token_aqui
jupyter notebook notebooks/CarSeats_Ev3.ipynb
```

Luego, en la celda de la Sección 3, cambiar `USE_NGROK = False` por `USE_NGROK = True` antes de ejecutarla (Kernel → Restart & Run All). Si el túnel falla (sin token o sin internet), el dashboard local sigue funcionando igual, solo no se genera la URL pública.

**Para detener el servidor:** Kernel → Shut Down Kernel (o Restart Kernel) desde la interfaz de Jupyter, o `Ctrl+C` en la terminal donde corre `jupyter notebook` para apagar todos los kernels.

> Si ya se ejecutó el notebook sin ngrok y quiere activarlo después, cambie `USE_NGROK` a `True` y use Kernel → Restart & Run All (no solo re-ejecutar la celda), para asegurar que el servidor arranque limpio en ese kernel.

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

Una rama por etapa del proyecto (`feature/etl`, `feature/eda`, `feature/dashboard`, `feature/modelos`, `feature/docs`, `fix/manejo-nuloes`, `fix/dashboard` ), integradas en `develop` antes de llegar a `main`.
