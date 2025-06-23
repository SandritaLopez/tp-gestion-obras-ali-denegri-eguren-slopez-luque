# test.py
from gestionar_obras import GestionarObra

def menu():
    while True:
        print("\n--- SISTEMA DE GESTIÓN DE OBRAS ---")
        print("1. Crear nueva obra")
        print("2. Ver indicadores")
        print("3. Salir")
        opcion = input("Elegí una opción: ")

        if opcion == "1":
            GestionarObra.nueva_obra()
        elif opcion == "2":
            GestionarObra.obtener_indicadores()
        elif opcion == "3":
            print("Saliste del la gestion de obras")
            break
        else:
            print("Opción inválida")

if __name__ == "__main__":
    GestionarObra.mapear_orm()  # Esto asegura que existan las tablas en la base
    menu()
