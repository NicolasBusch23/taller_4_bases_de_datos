#Archivo encargado de ejecutar las funciones definidas dentro de ETL

import sys
import logging

from etl.extract.extract import extract_main
from etl.transform.transform import transform_main
from etl.load.load import load_main


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def main() -> None:
    _setup_logging()
    if len(sys.argv) < 2:
        print("Usage: python main.py [extract|transform|load|run]")
        sys.exit(1)

    cmd: str = sys.argv[1].lower()

    if cmd == "extract":
        extract_main()
    elif cmd == "transform":
        transform_main()
    elif cmd == "load":
        load_main()
    elif cmd == "run":
        extract_main()
        transform_main()
        load_main()
    else:
        print("Unknown command. Use: extract | transform | load | run")
        sys.exit(1)


if __name__ == "__main__":
    main()
