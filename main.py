"""Punto de entrada; ejecutar: python main.py [--demo]"""
import argparse
from software_fj.consola import menu
from software_fj.demo import ejecutar_demo

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Gestor de clientes, servicios y reservas de Software FJ')
    parser.add_argument('--demo', action='store_true', help='Ejecutar 20 operaciones simuladas')
    args = parser.parse_args()
    if args.demo:
        ejecutar_demo()
    else:
        menu()
