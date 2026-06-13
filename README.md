# fly-in

Simulador de rutas de drones con parseo de mapas.

## Requisitos

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — gestor de paquetes que aísla las dependencias sin contaminar el entorno del sistema.

## Makefile

| Target         | Descripción |
|----------------|-------------|
| `make` / `make all` | Ejecuta `lint` (target por defecto). |
| `make install` | Instala `flake8` y `mypy` con `uv tool install` en entornos aislados. |
| `make run MAP=<archivo>` | Ejecuta el simulador con el mapa indicado. Si no se pasa `MAP`, usa `maps/medium/03_priority_puzzle.txt`. |
| `make debug MAP=<archivo>` | Ejecuta el simulador con `pdb` para depuración paso a paso. |
| `make clean` | Elimina `__pycache__`, `.mypy_cache`, `.pytest_cache` y archivos `*.pyc`. |
| `make lint` | Ejecuta `flake8 .` y `mypy .` con los flags obligatorios del subject. |
| `make lint-strict` | Ejecuta `flake8 .` y `mypy . --strict` (recomendado para mayor rigor). |

### ¿Por qué uv?

[uv](https://docs.astral.sh/uv/) es un gestor de paquetes y proyectos de Python escrito en Rust. Es compatible con `pip` y `pipx` pero mucho más rápido y con varias ventajas:

**Aislamiento:** `uv tool install` instala herramientas (como `flake8` y `mypy`) en entornos virtuales propios dentro de `~/.local/share/uv/tools/`. Cada herramienta vive en su propio directorio sin depender del Python del sistema.

**No contamina el sistema:** A diferencia de `pip install` (que instala en site-packages del sistema) o `pip install --user` (que instala en site-packages del usuario), uv no escribe ni modifica ninguna ruta de Python. Tampoco requiere `--break-system-packages`, una bandera peligrosa que desactiva la protección PEP 668 y puede romper el sistema.

**Idempotente con `--force`:** Si ya tienes la herramienta instalada, `uv tool install --force` la reinstala limpiamente en su entorno aislado sin dejar residuos ni conflictos de版本.

**Rapidez:** Al estar escrito en Rust, uv resuelve dependencias e instala paquetes entre 10x y 100x más rápido que `pip`, especialmente útil en proyectos grandes o CI.

**Fácil de instalar:**
```sh
# Con pipx
pipx install uv

# O directo (recomendado)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Para este proyecto:** Ejecutando `make install` se instalan `flake8` y `mypy` con uv en sus entornos aislados. Los binarios quedan disponibles en `~/.local/bin/` y se pueden usar directamente como `flake8 .` o `mypy .`. Si en algún momento quieres desinstalarlos: `uv tool uninstall flake8`.

### Uso rápido

```sh
# Instalar herramientas de linting
make install

# Verificar el proyecto
make

# Ejecutar con un mapa específico
make run MAP=maps/easy/01_simple.txt

# Limpiar cachés
make clean
```

## Extracción de mapas

```sh
tar -xzf maps.tar.gz
```

## Notas

- `Parser_Error` es el error genérico de parseo. Captura `IndexError` cuando el mapa no tiene suficientes datos.
- Para que el shell reciba el código de salida correcto: `raise SystemExit(main())`

## En sucio

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
