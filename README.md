# fly-in

# Resources:

https://es.wikipedia.org/wiki/Teor%C3%ADa_de_grafos
https://www.datacamp.com/tutorial/python-uv


EXTRACCION DE UN .tar.gz

tar -xzf maps.tar.gz

CREACION DE EXCEPCION:
- Parser_Error (Error generico de parseo)
- DEBE CAPTURAR INDEXERROR, para cuando va a buscar un dato en el texto y el mapa pasado no tiene la cantidad de contenido necesario para llegar a la posicion del dato necesario.
USO DE SystemExit():
```
Qué hace \SystemExit(main())``

main() devuelve un entero (0, 1, 2, ...).
raise SystemExit(codigo) termina el proceso con ese código.
Es la forma estándar en Python CLI para que el shell reciba el exit code correcto.
Sin eso, si solo llamas main(), el valor que devuelve se ignora y el proceso suele terminar en 0.
```

Modificacion codigo en evaluacion: Añadir a los logs, al final Zone: drones/zones es decir, cantidad de drones totales/ zonas  ?? - capacity-info

# Parser dispatcher (modelo selector categorias):

```
checking_data(data):
    validate_nb_drones(data[0])

    start_count = 0
    end_count = 0

    for line_no, line in data[1:]:
        if line startswith "start_hub:":
            start_count += 1
            validate_start_hub(line_no, line)

        elif line startswith "end_hub:":
            end_count += 1
            validate_end_hub(line_no, line)

        elif line startswith "hub:":
            validate_hub(line_no, line)

        elif line startswith "connection:":
            validate_connection(line_no, line)

        else:
            error unknown line type

    if start_count != 1:
        error missing/duplicated start_hub

    if end_count != 1:
        error missing/duplicated end_hub
```