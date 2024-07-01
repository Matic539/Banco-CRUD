from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
import pprint
import datetime
import os
import random

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client['Banco']

# Limpiar
def clear():
    os.system('cls')
    

# Crear
def insertar_cliente():
    numero_cta = input("Ingrese el número de cuenta: ")
    rut_titular = input("Ingrese el RUT del titular: ")
    nombre_titular = input("Ingrese el nombre del titular: ")
    direccion_titular = input("Ingrese la dirección del titular: ")
    fono_titular = input("Ingrese el teléfono del titular: ")
    email_titular = input("Ingrese el email del titular: ")

    ejecutivas = list(db.ejecutiva.find())
    if not ejecutivas:
        print("No hay ejecutivas disponibles.")
        return
    
    ejecutiva_seleccionada = random.choice(ejecutivas)
    id_ejecutiva = ejecutiva_seleccionada['_id']

    cliente = {
        "numero_cta": numero_cta,
        "rut_titular": rut_titular,
        "nombre_titular": nombre_titular,
        "direccion_titular": direccion_titular,
        "fono_titular": fono_titular,
        "email_titular": email_titular,
        "cuentas": [],
        "fecha_creacion": datetime.datetime.utcnow(),
        "id_ejecutiva": ObjectId(id_ejecutiva)
    }
    result = db.cliente.insert_one(cliente)
    print(f"Cliente insertado con ID: {result.inserted_id}")

def insertar_cuenta():
    numero_cta = input("Ingrese el número de cuenta: ")
    tipo_cta = input("Ingrese el tipo de cuenta (corriente/ahorro): ")
    saldo = float(input("Ingrese el saldo inicial: "))
    rut_titular = input("Ingrese el RUT del titular: ")

    cliente = db.cliente.find_one({"rut_titular": rut_titular})
    if cliente is None:
        print("El RUT no existe.")
        return

    cuenta = {
        "numero_cta": numero_cta,
        "tipo_cta": tipo_cta,
        "saldo": saldo,
        "rut_titular": rut_titular
    }
    result = db.cuenta.insert_one(cuenta)
    cuenta_id = result.inserted_id

    db.cliente.update_one(
        {"rut_titular": rut_titular},
        {"$push": {"cuentas": cuenta_id}}
    )
    print(f"Cuenta insertada con ID: {result.inserted_id} y agregada al cliente: {rut_titular}")

def insertar_ejecutiva():
    nombre_ejecutiva = input("Ingrese el nombre de la ejecutiva: ")
    sucursal = input("Ingrese la sucursal: ")
    fono_ejecutiva = input("Ingrese el teléfono de la ejecutiva: ")
    email_ejecutiva = input("Ingrese el email de la ejecutiva: ")

    ejecutiva = {
        "nombre_ejecutiva": nombre_ejecutiva,
        "sucursal": sucursal,
        "fono_ejecutiva": fono_ejecutiva,
        "email_ejecutiva": email_ejecutiva
    }
    result = db.ejecutiva.insert_one(ejecutiva)
    print(f"Ejecutiva insertada con ID: {result.inserted_id}")

def insertar_transaccion():
    numero_cta = input("Ingrese el número de cuenta: ")
    tipo = input("Ingrese el tipo de transacción (depósito/retiro): ").lower()
    monto = float(input("Ingrese el monto: "))
    descripcion = input("Ingrese la descripción: ")
    # if tipo != 'deposito' or 'retiro':
    #     print('Ingrese un tipo de transaccion valido')
    #     return

    cuenta = db.cuenta.find_one({"numero_cta": numero_cta})
    if cuenta is None:
        print("La cuenta no existe.")
        return

    transaccion = {
        "numero_cta": numero_cta,
        "tipo": tipo,
        "monto": monto,
        "fecha_hora": datetime.datetime.utcnow(),
        "descripcion": descripcion
    }
    result = db.transaccion.insert_one(transaccion)
    print(f"Transacción insertada con ID: {result.inserted_id}, de la cuenta N°: {numero_cta} ")

    # Actualizar
    actualizar_saldo(numero_cta)

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

# Leer
def leer_clientes():
    clientes = db.cliente.find()
    lista_clientes = []
    for cliente in clientes:
        lista_clientes.append(cliente)
    return lista_clientes

def leer_cuentas():
    cuentas = db.cuenta.find()
    lista_cuenta = []
    for cuenta in cuentas:
        lista_cuenta.append(cuenta)
    return lista_cuenta

def leer_transacciones():
    transacciones = db.transaccion.find()
    lista_transacciones = []
    for transaccion in transacciones:
        lista_transacciones.append(transaccion)
    return lista_transacciones

def leer_movimientos():
    clientes = db.cliente.find()
    for cliente in clientes:
        print("\n##################################################################################################\n")
        print(f"Cliente: {cliente['nombre_titular']} (RUT: {cliente['rut_titular']})")
        for cuenta_id in cliente['cuentas']:
            cuenta = db.cuenta.find_one({"_id": ObjectId(cuenta_id)})
            if cuenta:
                print("--------------------------------------------------------------------------------------------------")
                print(f"Cuenta: {cuenta['numero_cta']} (Tipo: {cuenta['tipo_cta']}, Saldo: {cuenta['saldo']})")
                transacciones = db.transaccion.find({"numero_cta": cuenta['numero_cta']})
                for transaccion in transacciones:
                    print(f"Transacción: {transaccion['tipo']} (Monto: {transaccion['monto']}, Fecha: {transaccion['fecha_hora']})")
                    print(f"Descripción: {transaccion['descripcion']}\n")

def leer_ejec_relacionados():
    clientes = db.cliente.find()
    for cliente in clientes:
        print("\n##################################################################################################\n")
        # print(f"Cliente: {cliente['nombre_titular']} (RUT: {cliente['rut_titular']})")
        print('CLIENTE:')
        pprint.pp(cliente)
        if 'id_ejecutiva' in cliente:
            ejecutiva = db.ejecutiva.find_one({"_id": ObjectId(cliente['id_ejecutiva'])})
            if ejecutiva:
                print("\n--------------------------------------------------------------------------------------------------\n")
                # print(f"Ejecutiva: {ejecutiva['nombre_ejecutiva']} (Sucursal: {ejecutiva['sucursal']}, Teléfono: {ejecutiva['fono_ejecutiva']}, Email: {ejecutiva['email_ejecutiva']})")
                print('EJECUTIVA:')
                pprint.pp(ejecutiva)

def leer_ejec_cliente():
    rut_titular = input("Ingrese el RUT del titular: ")

    cliente = db.cliente.find_one({"rut_titular": rut_titular})
    if cliente is None:
        print("El RUT del titular no existe.")
        return

    if 'id_ejecutiva' in cliente:
        ejecutiva = db.ejecutiva.find_one({"_id": ObjectId(cliente['id_ejecutiva'])})
        if ejecutiva:
            print("\n##################################################################################################\n")
            print(f"Ejecutiva del Cliente: {cliente['nombre_titular']}")
            print("--------------------------------------------------------------------------------------------------")
            pprint.pp(ejecutiva)

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

# Actualizar
def actualizar_saldo(numero_cta):
    cuenta = db.cuenta.find_one({"numero_cta": numero_cta})
    if cuenta is None:
        print(f"La cuenta {numero_cta} no existe.")
        return

    transacciones = db.transaccion.find({"numero_cta": numero_cta})

    saldo = 0
    for transaccion in transacciones:
        if transaccion['tipo'] == 'deposito':
            saldo += transaccion['monto']
        elif transaccion['tipo'] == 'retiro':
            saldo -= transaccion['monto']

    db.cuenta.update_one(
        {"numero_cta": numero_cta},
        {"$set": {"saldo": saldo}}
    )

    print(f"Saldo actualizado para la cuenta {numero_cta}. Nuevo saldo: {saldo}")

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

# Borrar
def borrar_cuenta():
    print("ELIMINAR CUENTA")
    numero_cta = input("Ingrese el número de cuenta: ")

    cuenta = db.cuenta.find_one({"numero_cta": numero_cta})
    if cuenta is None:
        print("La cuenta no existe.")
        return

    if cuenta['saldo'] != 0:
        print("No se puede eliminar la cuenta porque tiene saldo.")
        return

    db.cuenta.delete_one({"numero_cta": numero_cta})

    db.transaccion.delete_many({"numero_cta": numero_cta})

    db.cliente.update_one(
        {"rut_titular": cuenta['rut_titular']},
        {"$pull": {"cuentas": cuenta['_id']}}
    )

    print(f"La cuenta {numero_cta} y sus transacciones han sido eliminadas.")

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

#  Funcionalidades Adicionales
def transferir():
    cuenta_origen = input("Ingrese el número de cuenta de origen: ")
    cuenta_destino = input("Ingrese el número de cuenta de destino: ")
    monto = float(input("Ingrese el monto a transferir: "))
    descripcion = input("Ingrese la descripción de la transaccion: ")

    origen = db.cuenta.find_one({"numero_cta": cuenta_origen})
    destino = db.cuenta.find_one({"numero_cta": cuenta_destino})

    if origen is None:
        print(f"La cuenta de origen {cuenta_origen} no existe.")
        return

    if destino is None:
        print(f"La cuenta de destino {cuenta_destino} no existe.")
        return

    if origen['saldo'] < monto:
        print("La cuenta de origen no tiene saldo suficiente")
        return

    db.cuenta.update_one(
        {"numero_cta": cuenta_origen},
        {"$inc": {"saldo": -monto}}
    )

    db.cuenta.update_one(
        {"numero_cta": cuenta_destino},
        {"$inc": {"saldo": monto}}
    )

    transaccion_origen = {
        "numero_cta": cuenta_origen,
        "tipo": "transferencia",
        "monto": -monto,
        "fecha_hora": datetime.datetime.utcnow(),
        "descripcion": f"Transferencia a {cuenta_destino}: {descripcion}"
    }
    transaccion_destino = {
        "numero_cta": cuenta_destino,
        "tipo": "transferencia",
        "monto": monto,
        "fecha_hora": datetime.datetime.utcnow(),
        "descripcion": f"Transferencia desde {cuenta_origen}: {descripcion}"
    }
    db.transaccion.insert_one(transaccion_origen)
    db.transaccion.insert_one(transaccion_destino)

    print(f"Transferencia de {monto} desde la cuenta {cuenta_origen} a la cuenta {cuenta_destino} realizada.")

##############################################################################################################################
##############################################################################################################################
##############################################################################################################################

def menu():
    while True:
        print("\n##################################################################################################\n")
        print("Menú:")
        print("1. Inserta Documentos")
        print("2. Leer Documentos")
        print("3. Eliminar Documentos")
        print("4. Transferir dinero")
        print("5. Salir")
        opcion = input("Elige una opción: ")

        ###################################################################################################################################
        ###################################################################################################################################

        if opcion == '1':
            clear()
            print("\nMenú:")
            print("1. Cliente")
            print("2. Ejecutiva")
            print("3. Crear Cuentas")
            print("4. Transacción")
            print("5. Salir")
            opcion = input("Elige una opción: ")

            if opcion == '1':
                insertar_cliente()
            elif opcion == '2':
                insertar_ejecutiva()
            elif opcion == '3':
                insertar_cuenta()
            elif opcion =='4':
                insertar_transaccion() 
            else:
                print("Opción no válida, por favor elige nuevamente.")

        ###################################################################################################################################
        ###################################################################################################################################

        elif opcion == '2':
            print("\nMenú:")
            print("1. Leer todos los clientes")
            print("2. Leer todas las cuentas bancarias")
            print("3. Leer todas las cuentas bancarias de la colección transacción")
            print("4. Leer todos los movimientos bancarios (deposito, retiro, etc.)")
            print("5. Leer todos los ejecutivos relacionados con los clientes")
            print("6. Leer el ejecutivo de un cliente.")
            print("7. Salir")
            opcion = input("Elige una opción: ")

            if opcion == '1':
                clear()
                todos_los_clientes = leer_clientes()
                print("\nClientes:")
                for cliente in todos_los_clientes:
                    print("\n##################################################################################################\n")
                    pprint.pp(cliente)
            elif opcion == '2':
                clear()
                todas_las_cuentas = leer_cuentas()
                print("\nCuentas Bancarias:")
                for cuenta in todas_las_cuentas:
                    print("\n##################################################################################################\n")
                    pprint.pp(cuenta)
            elif opcion == '3':
                clear()
                cuentas_en_transacciones = leer_transacciones()
                print("\nCuentas Bancarias en Transacciones:")
                for cuenta in cuentas_en_transacciones:
                    print("\n##################################################################################################\n")
                    pprint.pp(cuenta)
            elif opcion == '4':
                clear()
                leer_movimientos()
            elif opcion == '5':
                clear()
                leer_ejec_relacionados()
            elif opcion == '6':
                clear()
                leer_ejec_cliente()
            elif opcion == '7':
                clear()
                print("Saliendo...")
                break
            else:
                clear()
                print("Opción no válida, por favor elige nuevamente.")

        ###################################################################################################################################
        ###################################################################################################################################

        elif opcion == '3':
            clear()
            borrar_cuenta()

        ###################################################################################################################################
        ###################################################################################################################################

        elif opcion == '4':
            clear()
            transferir()
        ###################################################################################################################################
        ###################################################################################################################################

        elif opcion == '5':
            clear()
            print("Saliendo...")
            break
        else:
            clear()
            print("Opción no válida, por favor elige nuevamente.")


def main():
    menu()

main()
