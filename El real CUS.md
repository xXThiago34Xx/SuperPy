(Las sgte 8 lineas van a cambiar en cualquier momento porfavor NO IMPLEMENTAR)
Segmento 1:
Cajas con Mayor Tiempo de Atención

son cosas diferentes

- Mayor tiempo de atención
- Ir de corrido sin huecos
- Menor tiempo muerto

---

Requisito General:
✨Minimizar la cantidad de cambios de cajeros✨

Caja Preferencial:

-(0) Debe estar disponible de 07:00 - 22:30 sin huecos

Caja Rápida 1

-(0) Debe estar disponible desde 07:00

Caja Rápida 1, 2, 3

-(0) Debe haber al menos 1 disponible de 07:00 - 22:30

Caja Rápida 1, 2

-(1) Maximizar tiempo de atención

Caja Rápida 3

-(3) Solo se le asigna si:
-- No hay nadie en caja rápida 1 o 2
-- No se puede asignar a ninguna otra caja

Caja Regular:

hay que balancear
-(1) Tiempo de atención
-(2) Cambios de cajero
-(3) Tiempo muerto
-(4) Huecos (cantidad)


# Las siguientes cajas: Caja Rápida 2, Caja Rápida 3, Cajas regulares se asignan bajo los sgts requerimientos por orden descendiente de prioridad:

- Si alguien llega se le asigna alguna caja, con la excepción de que todas las cajas estén ocupadas

* Si no hay cajas disponibles se asigna al trabajador a una [tarea] hasta que la sgte caja esté disponible, ahí cubrirá el resto de su turno.

Tareas secundarias:

- Devolución de productos

Se pueden asignar 2 personas a hacer 1

Tareas terciarias:

- Colocar viñetas [01:00]
- Reposición de Snacks [01:00]
- Reposición de punteras [01:00]
- Reposición de cajas de agua [01:00]
- Reposición de bolsas [01:00]

Se deben completar todas 1 vez al día
Se pueden hacer 2 a la vez
