# UI - Console

Title: SuperPy v1 - Día: (dia_seleccionado)
1. Cargar Archivo (Input ruta)
2. Seleccionar Dia (L-D, Todos)
3. Mostrar Entradas
4. Mostrar Salidas
5. Generar Pronóstico
6. Tools (Completar EAN)

# Algoritmos de asignación de cajeros

Algo 1: Toma un n cajas y completa optimizando **nr cajas**
Algo 2: Itera Algo 1, midiendo el tiempo muerto promedio y toma las que tenga <=30

Cja 1 : 30
Cja 2 : 15
Cja 3 : 30
Cja 4 : 0

Dst 1: prom(Cja)

DistObj = min{Dist}


# Etapa 0

## Caja Preferencial

- Debe empezar a las 07:00
- Llenar una caja lo máximo que se pueda de 07:00 a 22:30

## Caja Rápida 1

- Debe empezar a las 07:00
- Llenar una caja lo máximo que se pueda

# Etapa 1

## Segmento 1 Cajas Seguidas

- Tiempos muertos minimos
- Algo2

## Segmento 2 Entren los cajeros restantes

- Algo1 

## Segmento 3

- No asignados

# Etapa 2

## Definir caja preferencial

- Debe ser de Segmento 1
- Empiece desde las 7am
- Mayor tiempo de atención
- Rellenar huecos con personal de noAsignados

## Definir cajas rápidas

- Se seleccionan las 2 cajas con mayor tiempo de atención de Segmento 1
- Se seleccionan la caja con mayor tiempo de atención de Segmento 2

Caja preferencial
Caja rápida 1
Caja rápida 2
Caja rápida 3
Caja regular n

# Etapa 3

Se muestra en una lista los cajeros que no se pudieron asignar en ninguna caja y sus horarios ordenados por orden de llegada

---

# Al cargar archivo introducir numero de self y numero de rs para detectar la tabla cajeros

# Generar excel de entras y salidas del día correspondiente

la hoja de entrada tiene nombre, entrada, salida
ordenado por entrada
la hoja de salida tiene nombre, salida, entrada
ordenado por salida

# Generar Pronostico:
- En un archivo y actualizar o añadir el día seleccionado
- TODO: Al implementar TODOS, que se pongan las 7 hojas correspondientes a los 7 días

# Al imprimir df
- No imprimir ids
- Alinear los nombres a la izquierda
- Imprimir lineas verticales separadoras

1. Cargar Archivo (Input ruta)
2. Seleccionar Dia (L-D)      
3. Mostrar Entradas
4. Mostrar Salidas
5. Generar Pronóstico
6. Configurar Min-Max de Cajas
7. Tools (Completar EAN)      
8. Salir
9. [debug] Mostrar Horario 


