# Algoritmos de asignación de cajeros

Algo 1: Toma un n cajas y completa optimizando **nr cajas**
Algo 2: Itera Algo 1, midiendo el tiempo muerto promedio y toma las que tenga <=30

Cja 1 : 30
Cja 2 : 15
Cja 3 : 30
Cja 4 : 0

Dst 1: prom(Cja)

DistObj = min{Dist}

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
