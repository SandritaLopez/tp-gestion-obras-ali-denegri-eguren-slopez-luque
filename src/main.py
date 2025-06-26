# Main que funciona como ejecucion de todo el programa.

from gestionar_obra import GestionarObra

def main():
    # Conexión y mapeo de datos
    df = GestionarObra.extraer_datos()
    conexion_db = GestionarObra.conectar_db()
    GestionarObra.mapear_orm(conexion_db)

    # Limpieza y carga
    df_limpio = GestionarObra.limpiar_datos(df)
    GestionarObra.cargar_datos(df_limpio)

    # # Creacion de nuevas obras
    obra = GestionarObra.nueva_obra()
    obra2 =  GestionarObra.nueva_obra()
    

    obra.nuevo_proyecto("Arquitectura", "Ministerio De Cultura", "San Nicolás")

    # Iniciar contratación
    obra.iniciar_contratacion("Licitación Pública", "PL-1234")

    # Adjudicar la obra a una empresa
    obra.adjudicar_obra("Constructora Solana S.A")

    # Iniciar la obra con más detalles
    
    obra.iniciar_obra(
        esDestacada=True,
        fechaInicio="2025-07-01",
        fechaFinInicial="2026-07-01",
        fuenteFinanc="Nación Gcba",
        manoObra=20
    )

    # Actualizar porcentaje de avance
    obra.actualizar_porcentaje_avance(35)

    # Incrementar mano de obra
    obra.incrementar_mano_obra(30)

    # Incrementar plazo
    obra.incrementar_plazo(18)

    # Finalizar la obra
    obra.finalizar_obra()

    # Ver el resultado
    print(f"✅ Obra actualizada:\n{obra}")

    #Obtener indicadores finales
    GestionarObra.obtener_indicadores()

if __name__ == "__main__":
    main()