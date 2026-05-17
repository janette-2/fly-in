# fly-in

# Resources:

https://es.wikipedia.org/wiki/Teor%C3%ADa_de_grafos
https://www.datacamp.com/tutorial/python-uv


EXTRACCION DE UN .tar.gz

tar -xzf maps.tar.gz

CREACION DE EXCEPCION:
- Parser_Error (Error generico de parseo)

USO DE SystemExit():
```
Qué hace \SystemExit(main())``

main() devuelve un entero (0, 1, 2, ...).
raise SystemExit(codigo) termina el proceso con ese código.
Es la forma estándar en Python CLI para que el shell reciba el exit code correcto.
Sin eso, si solo llamas main(), el valor que devuelve se ignora y el proceso suele terminar en 0.
```

Modificacion codigo en evaluacion: Añadir a los logs, al final Zone: drones/zones es decir, cantidad de drones totales/ zonas  ?? - capacity-info