import streamlit as st
import math
import base64
import json
import hashlib
from datetime import datetime
import numpy as np

# --- Constants ---
TOLERANCIA = 0.05 # Tolerance of +/- 0.05 for answers
GRAVEDAD = 9.81 # Acceleration due to gravity in m/s^2

# --- Image dictionary per question ---
# The keys are the question indices (0 to 4 for questions 1 to 5)
# The values are the URLs to your image files.
# IMPORTANT: These paths are placeholders. You MUST replace them with the direct public URLs
# from your GitHub repository (e.g., https://github.com/your_username/your_repo/raw/main/images/graficadesplazamiento.jpg)
pregunta_imagenes = {
    0: "images2/1.jpg", # Para la Pregunta 1 (Desplazamiento vs. Tiempo)
    1: "images2/2.jpg", # Para la Pregunta 2 (Desplazamiento vs. Tiempo)
    2: "images2/3.png", # Para la Pregunta 3 (Desplazamiento vs. Tiempo)
    3: "images2/4.jpg",      # Para la Pregunta 4 (Velocidad vs. Tiempo)
    4: "images2/5.jpg"       # Para la Pregunta 5 (Velocidad vs. Tiempo)
}


# --- Auxiliary Functions ---

def redondear_a_2_decimales(numero):
    """
    Rounds a number to 2 decimal places and formats it as a float with two decimal places.
    If it is None, inf, or nan, returns None.
    """
    if numero is None or math.isinf(numero) or math.isnan(numero):
        return None
    try:
        return float(f"{numero:.2f}")
    except (TypeError, ValueError): # Handle cases where the number is not convertible to float
        return None

def calcular_respuestas_fisicas(clave):
    """Calculates the correct answers for each physics question."""
    respuestas = {}
    
    if not isinstance(clave, (int, float)) or clave <= 0:
        for i in range(1, 6): # Only 5 physics questions
            respuestas[f'pregunta{i}'] = None
        return respuestas

    # Question 1: If the woman pushes the 'clave' kg box with a force of 20 N and the friction force is 5 N, calculate the acceleration of the box.
    # F_net = F_applied - F_friction = m * a
    # a = (F_applied - F_friction) / m
    # clave = mass (kg)
    fuerza_aplicada_q1 = 20
    fuerza_friccion_q1 = 5
    masa_q1 = float(clave)
    aceleracion_q1 = (fuerza_aplicada_q1 - fuerza_friccion_q1) / masa_q1
    respuestas['pregunta1'] = redondear_a_2_decimales(aceleracion_q1)

    # Question 2: If the mass is 2 kg, the angle is 30 degrees and the force F is 'clave' N, find the value of the normal force.
    # N = mg cos(theta) + F sin(theta)
    # clave = Force F (N)
    masa_q2 = 2.0
    angulo_q2_grados = 30.0
    angulo_q2_radianes = math.radians(angulo_q2_grados)
    fuerza_f_q2 = float(clave)
    normal_q2 = (masa_q2 * GRAVEDAD) - (fuerza_f_q2 * math.sin(angulo_q2_radianes))
    respuestas['pregunta2'] = redondear_a_2_decimales(normal_q2)

    # Question 3: If the mass of the spherical object is 'clave' kg and the tension lifting it is 1000 N, find the acceleration of the object.
    # F_net = T - mg = ma
    # a = (T - mg) / m
    # clave = mass (kg)
    tension_q3 = 1000.0
    masa_q3 = float(clave)
    aceleracion_q3 = (tension_q3 - (masa_q3 * GRAVEDAD)) / masa_q3
    respuestas['pregunta3'] = redondear_a_2_decimales(aceleracion_q3)

    # Question 4: Calculate the acceleration if the friction is 'clave'.
    # Assume a fixed applied force and mass for this problem to be solvable.
    # F_net = F_applied - F_friction = m * a
    # F_friction = F_applied - m * a
    # clave = acceleration (m/s^2)
    fuerza_aplicada_q4 = 30.0 # Assumed fixed force
    masa_q4 = 10.0 # Assumed fixed mass
    friccion_q4 = float(clave)
    aceleracion_q4 = (fuerza_aplicada_q4 - friccion_q4)/masa_q4
    respuestas['pregunta4'] = redondear_a_2_decimales(aceleracion_q4)

    # Question 5: If the mass is 5 kg and the force is 'clave', calculate the acceleration.
    # F = ma
    # a = F / m
    # clave = part of the force calculation
    masa_q5 = 5.0
    angulo_q5_grados = 25.0
    angulo_q5_radianes = math.radians(angulo_q5_grados)
    fuerza_q5 = (float(clave))*math.cos(angulo_q5_radianes)
    aceleracion_q5 = fuerza_q5 / masa_q5
    respuestas['pregunta5'] = redondear_a_2_decimales(aceleracion_q5)

    return respuestas

def codificar_calificacion(datos_calificacion):
    json_data = json.dumps(datos_calificacion)
    encoded_data = base64.b64encode(json_data.encode('utf-8')).decode('utf-8')
    return encoded_data

# --- Streamlit Application Logic ---

st.title("Comprobación de D.C.L y Fuerzas")

# Initialization of session_state (crucial for maintaining state between interactions)
if 'nombre_alumno' not in st.session_state:
    st.session_state.nombre_alumno = ""
if 'clave_alumno' not in st.session_state:
    st.session_state.clave_alumno = None
if 'preguntas_list' not in st.session_state:
    st.session_state.preguntas_list = []
if 'respuestas_estudiante_guardadas' not in st.session_state:
    st.session_state.respuestas_estudiante_guardadas = []
if 'pregunta_actual_idx' not in st.session_state:
    st.session_state.pregunta_actual_idx = 0
if 'examen_iniciado' not in st.session_state:
    st.session_state.examen_iniciado = False
if 'examen_finalizado' not in st.session_state:
    st.session_state.examen_finalizado = False
if 'respuestas_correctas_calc' not in st.session_state:
    st.session_state.respuestas_correctas_calc = {}
if 'final_dat_content' not in st.session_state:
    st.session_state.final_dat_content = None
if 'final_filename' not in st.session_state:
    st.session_state.final_filename = None


# --- Start Screen ---
if not st.session_state.examen_iniciado:
    st.write("¡Bienvenido a la comprobación de D.C.L y Fuerzas!")
    nombre_input = st.text_input("Por favor, ingresa tu nombre completo:", key="nombre_entrada")
    clave_input = st.text_input("Ingresa tu número de clave (un número POSITIVO):", key="clave_entrada")

    if st.button("Iniciar Examen"):
        if not nombre_input:
            st.error("Por favor, ingresa tu nombre.")
            st.stop() # Stop execution so the error is visible
        try:
            clave = float(clave_input) # Clave can now be float for physics problems
            if clave <= 0:
                st.error("La clave debe ser un número POSITIVO.")
                st.stop()
        except ValueError:
            st.error("Número de clave inválido. Ingresa un número.")
            st.stop()

        st.session_state.nombre_alumno = nombre_input
        st.session_state.clave_alumno = clave
        st.session_state.examen_iniciado = True
        st.session_state.respuestas_correctas_calc = calcular_respuestas_fisicas(clave)
        
        # Physics question texts with LaTeX
        st.session_state.preguntas_list = [
            r"1) Si la mujer empuja la caja de $" + str(clave) + r"$ kgs con fuerza de $20 N$ y la fuerza de fricción es de $5 N$, calcule la aceleración de la caja. La respuesta estará en $m/s^2$ pero solo responde con la cantidad numérica. (2 decimales)",
            r"2) Si la masa es de $2 kg$, el ángulo es de $30^\circ$ y la fuerza $F$ es de $" + str(clave) + r"$ N, encuentre el valor de la fuerza normal. La respuesta estará en $N$ pero solo responde con la cantidad numérica. (2 decimales)",
            r"3) Si la masa del objeto esférico es de $" + str(clave) + r"$ kg y la tensión que lo levanta es de $1000 N$, encuentre la aceleración del objeto. La respuesta estará en $m/s^2$ pero solo responde con la cantidad numérica. (2 decimales)",
            r"4) Calcule la aceleración si la fricción es $" + str(clave) + r"$ $N$, tomando en cuenta las fuerzas de la figura y una masa de $10 kg$. La respuesta estará en $N$ pero solo responde con la cantidad numérica. (2 decimales)",
            r"5) Si la masa es de $5 kg$ y la fuerza es $" + str(clave) + r"$ $N$, calcule la aceleración. La respuesta estará en $m/s^2$ pero solo responde con la cantidad numérica. (2 decimales)"
        ]
        st.rerun()

# --- Exam Screen ---
elif st.session_state.examen_iniciado and not st.session_state.examen_finalizado:
    st.header(f"¡Hola, {st.session_state.nombre_alumno}!")
    st.subheader(f"Clave de examen: {st.session_state.clave_alumno}")

    if st.session_state.pregunta_actual_idx < len(st.session_state.preguntas_list):
        pregunta_idx = st.session_state.pregunta_actual_idx
        pregunta_actual_text = st.session_state.preguntas_list[pregunta_idx]
        st.markdown(f"**Pregunta {pregunta_idx + 1} de {len(st.session_state.preguntas_list)}:**")
        st.markdown(pregunta_actual_text)

        # --- Show image associated with the question, if it exists ---
        if pregunta_idx in pregunta_imagenes:
            try:
                # Check if the URL still contains a local path, and warn the user.
                if "images/" in pregunta_imagenes[pregunta_idx]:
                    st.warning(f"Advertencia: La imagen para la pregunta {pregunta_idx + 1} aún utiliza una ruta local ('{pregunta_imagenes[pregunta_idx]}'). Por favor, reemplázala con la URL pública de tu imagen de GitHub para que sea visible en la aplicación web.")
                
                st.image(pregunta_imagenes[pregunta_idx], caption=f"Imagen para la Pregunta {pregunta_idx + 1}", use_container_width=True)
                st.markdown("---") # Visual separator
            except Exception as e:
                st.warning(f"Error al cargar la imagen para la pregunta {pregunta_idx + 1}. Asegúrate de que la URL sea correcta y accesible: {e}")

        # --- Numerical answer inputs ---
        respuestas_ingresadas_actuales = []
        
        # All physics questions require a single numerical input
        labels = ["Tu respuesta (ej. 1.00):"]
        num_inputs = 1

        for i in range(num_inputs):
            input_val = st.text_input(labels[i], key=f"respuesta_{pregunta_idx}_{i}")
            respuestas_ingresadas_actuales.append(input_val)

        st.markdown("---") # Visual separator

        if st.button("Siguiente Pregunta"):
            st.session_state.respuestas_estudiante_guardadas.append({
                "pregunta_idx": pregunta_idx,
                "respuestas_ingresadas": respuestas_ingresadas_actuales
            })
            st.session_state.pregunta_actual_idx += 1
            st.rerun()
    else:
        # --- Finalize Exam ---
        calificacion = 0
        detalles_respuestas = []
        total_preguntas_validas_para_calificar = 0

        for i, respuesta_guardada in enumerate(st.session_state.respuestas_estudiante_guardadas):
            pregunta_idx = respuesta_guardada['pregunta_idx']
            respuestas_usuario_str_list = respuesta_guardada['respuestas_ingresadas'] # Now it's a list of strings
            
            respuesta_correcta_actual = st.session_state.respuestas_correctas_calc.get(f'pregunta{pregunta_idx + 1}')

            es_correcta_esta_pregunta = True # Assume it's correct until proven otherwise
            respuestas_usuario_num = [] # To store numerical answers for detailed log

            # Only attempt to grade if there is a valid expected correct answer
            if respuesta_correcta_actual is not None:
                # For physics questions, answers are single numbers
                if len(respuestas_usuario_str_list) != 1: # Should only be 1 input
                    es_correcta_esta_pregunta = False
                else:
                    try:
                        usuario_val = float(respuestas_usuario_str_list[0])
                        respuestas_usuario_num.append(round(usuario_val, 2)) # Round for logging
                        if abs(round(usuario_val, 2) - respuesta_correcta_actual) > TOLERANCIA:
                            es_correcta_esta_pregunta = False
                    except ValueError:
                        es_correcta_esta_pregunta = False
                
                if es_correcta_esta_pregunta: # Only count if grading was attempted and is possible
                    total_preguntas_validas_para_calificar += 1
            else: # When respuesta_correcta_actual is None (e.g., if clave was invalid)
                es_correcta_esta_pregunta = False # By default incorrect

            if es_correcta_esta_pregunta:
                calificacion += 1

            # --- Format the entered answer for the .dat file ---
            # For single answers, it's already a string
            respuesta_ingresada_formateada = respuestas_usuario_str_list[0]

            detalles_respuestas.append({
                "pregunta": st.session_state.preguntas_list[pregunta_idx],
                "respuesta_ingresada": respuesta_ingresada_formateada,
                "respuestas_ingresadas_num": respuestas_usuario_num, 
                "respuesta_correcta_esperada": respuesta_correcta_actual,
                "es_correcta": es_correcta_esta_pregunta,
                # No need to save the student's attached photo here, as the teacher provides it.
            })

        # Prepare data for HASH
        datos_para_hash = {
            "nombre_estudiante": st.session_state.nombre_alumno,
            "clave_ingresada": st.session_state.clave_alumno,
            "calificacion_obtenida": calificacion,
            "total_preguntas_examinadas": len(st.session_state.preguntas_list),
            "total_preguntas_validas_para_calificar": total_preguntas_validas_para_calificar,
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "respuestas_detalles": detalles_respuestas
        }

        datos_json_str = json.dumps(datos_para_hash, sort_keys=True)
        hash_sha256 = hashlib.sha256(datos_json_str.encode('utf-8')).hexdigest()

        datos_finales_para_guardar = datos_para_hash.copy()
        datos_finales_para_guardar["hash_sha256_integridad"] = hash_sha256

        # Generate the encoded .dat file and save it in session_state for persistent download
        st.session_state.final_dat_content = codificar_calificacion(datos_finales_para_guardar)
        st.session_state.final_filename = f"calificacion_{st.session_state.nombre_alumno.replace(' ', '_')}_{st.session_state.clave_alumno}.dat"

        # Show completion message
        st.session_state.examen_finalizado = True
        st.rerun()

# --- Exam Finished Screen ---
elif st.session_state.examen_finalizado:
    st.success(f"¡Gracias por completar el examen, {st.session_state.nombre_alumno}!")
    st.write("Tu examen ha terminado. Por favor, descarga tu archivo de calificación y envíaselo a tu profesor.")
    
    if st.session_state.final_dat_content and st.session_state.final_filename:
        st.download_button(
            label="Descargar Archivo de Calificación (.dat)",
            data=st.session_state.final_dat_content.encode('utf-8'),
            file_name=st.session_state.final_filename,
            mime="application/octet-stream"
        )
    else:
        st.warning("No se pudo generar el archivo de descarga. Por favor, contacta a tu profesor.")
    
    st.write("Puedes cerrar esta pestaña del navegador.")
    st.info("Para realizar el examen de nuevo, cierra y vuelve a abrir esta pestaña.")
