# Proyecto: Atlas de Exoplanetas

En este proyecto se nos asigno la tarea de crear un sitio inspirandonos en lo que es el NASA Exoplanet Archive, que contiene una gran cantidad de datos astronómicos distribuidos en cientos de variables, donde la exploración directa de esta información puede resultar compleja para estudiantes o usuarios que no están familiarizados con la estructura del catálogo. Por lo que este proyecto propone una aplicación web orientada a facilitar la exploración del catálogo mediante una interfaz visual, filtros y gráficos interactivos.

## Estado Actual
[En Desarrollo]
Ultimas etapas del codigo base y corrigiendo los errores.

## Clientes del Proyecto
- Rubén Montecinos
- Marcela Best Reyes

## Integrantes

- Simón Ranilao simon.ranilao@usach.cl
- Ismael Salas ismael.salas@usach.cl
- Martin Estay martin.estay@usach.cl
- Catalina Figueroa catalina.figueroa.b@usach.cl
- Maximiliano Pasten maximiliano.pasten.u@usach.cl

## Instalación

### 1. Clonar el repositorio:

```bash
git clone https://github.com/3maxim33/proyecto-desarrollo-de-software.git
cd proyecto-desarrollo-de-software
```

### 2. Instalar dependencias:

```bash
pip install -r requerimientos.txt
```
### 3. Ejecución de Pruebas:
```bash
pytest
(Gracias a la libreria de pytest, con este comando podemos ejecutar las pruebas que llevamos hasta el momento del proyecto)
```

### 4. Ejecutar la aplicación:

```bash
PYTHONPATH=src streamlit run app.py
(PYTHONPATH ya que "python" debe enfocarse en la carpeta de src para que streamlit pueda arrancar, ya que en esa carpeta se encuentran los archivos).
```
## Ejemplo de Uso (ya dentro de la web)

Tras poner en marcha la web gracias a la instalación, nos encontraremos con el catalogo de exoplanetas que posee Atlas, tambien se mostrara el explorador virtual donde podran observar y modificar parametros de los graficos presentados en Atlas, tales como masa de planetas en funcion de la Tierra, exentricidad orbital, y otras mas que estan disponibles en la web.
Otra caracteristica que pueden ir modificando es el mapa de color de los exoplanetas mostrados en el grafico.
