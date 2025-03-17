"""
Data generator module for creating sample data in the application.

This module provides functions to generate realistic sample data for
agents, users, chat messages, and usage statistics for demonstration
and testing purposes.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import json

# List of realistic course names for sample agents
COURSE_NAMES = [
    "Introducción a los Computadores",
    "Programación de Aplicaciones",
    "Programación Técnica y Científica",
    "Arquitectura de Computadores",
    "Estructura de Datos y Algoritmos",
    "Bases de Datos Avanzadas",
    "Inteligencia Artificial",
    "Sistemas Operativos",
    "Redes de Computadores",
    "Ingeniería del Software",
    "Cálculo y Métodos Numéricos",
    "Visualización de Datos",
    "Sistemas Distribuidos",
    "Computación en la Nube",
    "Ciberseguridad"
]

# Sample teacher names
TEACHER_NAMES = [
    "Aritz Bilbao Jayo",
    "Andoni Eguíluz Morán",
    "Carlos Quesada Granja",
    "Diego López de Ipiña",
    "Maite Urretavizcaya",
    "Isabel Fernández Castro",
    "Pablo García Bringas",
    "Begoña García Zapirain"
]

# Sample prompts/personalities for agents
SAMPLE_PROMPTS = [
    """Eres un asistente especializado en {course}. Tu objetivo es ayudar a los estudiantes 
    a comprender los conceptos fundamentales de la materia de forma clara y concisa. 
    Utiliza ejemplos prácticos para ilustrar conceptos abstractos. Sé paciente y mantén
    un tono amigable pero académico.""",
    
    """Actúas como un profesor experto en {course}. Debes responder preguntas de manera 
    educativa, desafiando a los estudiantes con contrapreguntas cuando sea apropiado.
    Utiliza analogías para explicar conceptos complejos y sugiere recursos adicionales
    cuando sea necesario.""",
    
    """Eres un tutor de {course} que busca guiar a los estudiantes a través del proceso 
    de aprendizaje. No des respuestas directas a problemas, sino pistas y sugerencias 
    para ayudarles a llegar a sus propias conclusiones. Mantén un tono alentador 
    y constructivo."""
]


def generate_sample_usage_data() -> Dict[str, Any]:
    """
    Generate realistic sample data for usage graphs.
    
    Returns:
        Dict with dates, interaction counts, and active student counts
    """
    today = datetime.now()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]

    # Create a more realistic pattern with a weekday peak
    base = random.randint(8, 15)
    variance = random.randint(3, 8)
    trend = random.choice([0.8, 1.0, 1.2])  # Downward, neutral, or upward trend

    counts = []
    active_students = []

    for i, date in enumerate(dates):
        # Lower usage on weekends (5 and 6 are weekend indices)
        is_weekend = date.weekday() >= 5
        weekend_factor = 0.4 if is_weekend else 1.0

        # Generate count with some randomness but following a pattern
        day_count = int((base + random.randint(-variance, variance)) * weekend_factor * (trend ** i))
        counts.append(max(1, day_count))  # Ensure at least 1 interaction

        # Generate active students (subset of total students)
        students = random.randint(max(1, day_count // 3), max(2, day_count // 2))
        active_students.append(students)

    return {
        "dates": dates, 
        "counts": counts,
        "active_students": active_students
    }


def generate_sample_agents(count: int = 4) -> List[Dict[str, Any]]:
    """
    Generate sample agent data.
    """
    agents = []
    
    # Ensure no duplicate course names
    selected_courses = random.sample(COURSE_NAMES, min(count, len(COURSE_NAMES)))
    
    for i in range(count):
        course_name = selected_courses[i] if i < len(selected_courses) else f"Curso {i+1}"
        teacher = random.choice(TEACHER_NAMES)
        
        # Create agent with string ID that matches Agent class format
        agent = {
            "id": str(1000 + i),  # Use string IDs
            "name": course_name,
            "created_by": teacher.lower().replace(" ", ".") + "@deusto.es",
            "created_at": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
            "students": generate_sample_student_emails(random.randint(5, 20)),
            "files": generate_sample_file_names(course_name, random.randint(0, 4)),
            "personality": random.choice(SAMPLE_PROMPTS).format(course=course_name)
        }
        
        agents.append(agent)
    
    return agents


def generate_sample_student_emails(count: int) -> List[str]:
    """
    Generate sample student email addresses.
    
    Args:
        count: Number of emails to generate
        
    Returns:
        List of email addresses
    """
    first_names = ["jon", "ane", "mikel", "amaia", "iker", "leire", "iñaki", "nerea", 
                  "unai", "maite", "gorka", "izaro", "aitor", "nahia", "eneko", "uxue"]
    last_names = ["garcia", "lopez", "gonzalez", "martinez", "fernandez", "etxeberria", 
                 "agirre", "mendez", "ibarra", "urrutia", "zabala", "goikoetxea"]
    
    emails = []
    for _ in range(count):
        first = random.choice(first_names)
        last1 = random.choice(last_names)
        last2 = random.choice(last_names)
        year = random.randint(19, 23)
        
        email = f"{first}.{last1}{year}@opendeusto.es"
        if email not in emails:  # Avoid duplicates
            emails.append(email)
    
    return emails


def generate_sample_file_names(course_name: str, count: int) -> List[str]:
    """
    Generate sample file names for agent knowledge base.
    
    Args:
        course_name: Name of the course for contextual file names
        count: Number of files to generate
        
    Returns:
        List of file names
    """
    if count == 0:
        return []
    
    # Course name keywords
    keywords = course_name.lower().replace("de ", "").split()
    if len(keywords) > 3:
        keywords = keywords[:3]
    
    # Possible file types
    file_types = [
        ("Programa", "pdf"),
        ("Tema", "pdf"),
        ("Apuntes", "pdf"),
        ("Práctica", "pdf"),
        ("Ejercicios", "pdf"),
        ("Referencias", "pdf"),
        ("Bibliografía", "txt"),
        ("Glosario", "txt"),
        ("FAQ", "txt"),
        ("Procedimientos", "docx")
    ]
    
    files = []
    for i in range(count):
        file_type, extension = random.choice(file_types)
        keyword = random.choice(keywords)
        number = random.randint(1, 10)
        
        if file_type == "Tema" or file_type == "Práctica" or file_type == "Ejercicios":
            name = f"{file_type} {number} - {keyword.capitalize()}.{extension}"
        else:
            name = f"{file_type} {keyword.capitalize()}.{extension}"
        
        files.append(name)
    
    return files


def generate_sample_messages(agent_id: str, user_email: str, count: int = 10) -> List[Dict[str, Any]]:
    """
    Generate sample chat messages between a student and an agent.
    
    Args:
        agent_id: ID of the agent
        user_email: Email of the student
        count: Number of message pairs to generate
        
    Returns:
        List of message dictionaries
    """
    # Get predefined Q&A pairs based on the agent ID
    qa_pairs = get_sample_qa_pairs(int(agent_id) % 5)
    
    messages = []
    
    # Use current time as reference point
    current_time = datetime.now()
    
    # Generate conversations with increasing timestamps
    for i in range(min(count, len(qa_pairs))):
        # Calculate message time (older messages first)
        message_time = current_time - timedelta(hours=(count-i), minutes=random.randint(0, 30))
        
        # Add student question
        messages.append({
            "role": "user",
            "content": qa_pairs[i]["question"],
            "timestamp": message_time.isoformat(),
            "agent_id": agent_id,
            "user_id": user_email
        })
        
        # Add agent response (a few minutes later)
        response_time = message_time + timedelta(minutes=random.randint(1, 3))
        messages.append({
            "role": "assistant",
            "content": qa_pairs[i]["answer"],
            "timestamp": response_time.isoformat(),
            "agent_id": agent_id,
            "user_id": user_email
        })
    
    return messages


def get_sample_qa_pairs(category: int) -> List[Dict[str, str]]:
    """
    Get predefined question-answer pairs for sample conversations.
    
    Args:
        category: Index to determine which set of Q&A pairs to return
        
    Returns:
        List of dictionaries with question and answer keys
    """
    qa_sets = [
        # Programming questions
        [
            {
                "question": "¿Cuál es la diferencia entre una lista y una tupla en Python?",
                "answer": "En Python, las listas son mutables, lo que significa que puedes cambiar sus elementos después de crearlas (añadir, eliminar o modificar elementos). Las tuplas, por otro lado, son inmutables - una vez creadas, no puedes cambiar sus elementos. Las listas se definen con corchetes [] y las tuplas con paréntesis (). Las tuplas suelen ser más eficientes en memoria y se utilizan cuando sabes que los datos no cambiarán."
            },
            {
                "question": "¿Puedes explicar qué es la recursividad con un ejemplo sencillo?",
                "answer": "La recursividad es cuando una función se llama a sí misma para resolver un problema. Un ejemplo clásico es el cálculo del factorial: ```python\ndef factorial(n):\n    if n <= 1:  # Caso base\n        return 1\n    else:  # Caso recursivo\n        return n * factorial(n-1)\n```\nEsta función calcula n! llamándose a sí misma con un valor más pequeño hasta llegar al caso base (n=1)."
            },
            {
                "question": "¿Cómo puedo manejar excepciones en Python?",
                "answer": "En Python, puedes manejar excepciones usando bloques try-except. Aquí tienes un ejemplo:\n```python\ntry:\n    # Código que podría generar una excepción\n    resultado = 10 / 0\nexcept ZeroDivisionError:\n    # Se ejecuta si ocurre la excepción específica\n    print('Error: División por cero')\nexcept Exception as e:\n    # Se ejecuta para otras excepciones\n    print(f'Ocurrió otro error: {e}')\nelse:\n    # Se ejecuta si no hay excepciones\n    print('Operación exitosa')\nfinally:\n    # Se ejecuta siempre\n    print('Proceso finalizado')\n```"
            }
        ],
        
        # Computer Architecture questions
        [
            {
                "question": "¿Qué es la jerarquía de memoria en un ordenador?",
                "answer": "La jerarquía de memoria es la organización de diferentes tipos de memoria en un sistema informático según su velocidad, capacidad y coste. De más rápida a más lenta: registros de CPU, caché (L1, L2, L3), memoria principal (RAM), almacenamiento secundario (SSD, HDD) y almacenamiento terciario (cintas, almacenamiento en red). Cuanto más rápida es la memoria, menor es su capacidad y mayor su coste. Esta estructura permite balancear rendimiento y coste."
            },
            {
                "question": "¿Puedes explicar la diferencia entre arquitectura RISC y CISC?",
                "answer": "RISC (Reduced Instruction Set Computing) y CISC (Complex Instruction Set Computing) son dos filosofías de diseño de CPU:\n\nRISC:\n- Instrucciones simples que se ejecutan en un ciclo\n- Menos instrucciones pero más especializadas\n- Pipeline más eficiente\n- Mayor dependencia del compilador para optimizaciones\n- Ejemplos: ARM, MIPS\n\nCISC:\n- Instrucciones complejas que pueden tomar varios ciclos\n- Conjunto de instrucciones más amplio\n- Microcodificación para instrucciones complejas\n- Mejor densidad de código\n- Ejemplos: x86, x86-64\n\nActualmente, muchas arquitecturas modernas son híbridos que incorporan ventajas de ambos enfoques."
            },
            {
                "question": "¿Cómo funciona la memoria caché y cuáles son sus niveles?",
                "answer": "La memoria caché es una memoria pequeña y rápida que almacena copias de datos de la memoria principal para reducir los tiempos de acceso. Funciona según el principio de localidad (temporal y espacial).\n\nNiveles típicos:\n- Caché L1: La más pequeña (32-64KB) y rápida, dividida en instrucciones y datos, integrada en el núcleo\n- Caché L2: Mayor (256KB-1MB) pero más lenta que L1, puede ser por núcleo o compartida\n- Caché L3: Más grande (varios MB) y más lenta, compartida entre todos los núcleos\n\nCuando la CPU necesita un dato, primero busca en L1, luego en L2, luego en L3, y finalmente en RAM si no lo encuentra en caché (esto se llama 'miss')."
            }
        ],
        
        # Database questions
        [
            {
                "question": "¿Cuáles son las diferencias entre bases de datos SQL y NoSQL?",
                "answer": "SQL (relacionales):\n- Esquema fijo y predefinido\n- Datos organizados en tablas con relaciones\n- Garantía ACID (Atomicidad, Consistencia, Aislamiento, Durabilidad)\n- Lenguaje estandarizado (SQL)\n- Mejor para datos estructurados y relaciones complejas\n- Ejemplos: MySQL, PostgreSQL, Oracle\n\nNoSQL (no relacionales):\n- Esquema flexible o sin esquema\n- Varios modelos: documentos, clave-valor, columnas, grafos\n- Escalabilidad horizontal más sencilla\n- Consistencia eventual (aunque algunos ofrecen ACID)\n- Mejor para grandes volúmenes de datos no estructurados o semiestructurados\n- Ejemplos: MongoDB (documentos), Redis (clave-valor), Cassandra (columnas), Neo4j (grafos)"
            },
            {
                "question": "¿Qué es la normalización en bases de datos y cuáles son las formas normales?",
                "answer": "La normalización es un proceso de diseño de bases de datos relacionales que elimina redundancias y dependencias problemáticas para mejorar la integridad de los datos.\n\nFormas normales principales:\n\n1NF: Elimina grupos repetitivos, garantiza valores atómicos\n- Cada celda contiene un solo valor\n- Cada registro es único (clave primaria)\n\n2NF: Cumple 1NF y elimina dependencias parciales\n- Atributos no clave dependen de toda la clave primaria\n\n3NF: Cumple 2NF y elimina dependencias transitivas\n- Atributos no clave no dependen de otros atributos no clave\n\nBCNF (Boyce-Codd): Versión más estricta de 3NF\n\n4NF: Elimina dependencias multivaluadas\n\n5NF: Elimina dependencias de join"
            },
            {
                "question": "¿Qué son los índices en una base de datos y cuándo deben usarse?",
                "answer": "Los índices son estructuras de datos especiales que mejoran la velocidad de las operaciones de búsqueda en una base de datos, similar a un índice en un libro.\n\nCaracterísticas:\n- Aceleran las consultas SELECT pero pueden ralentizar operaciones INSERT, UPDATE y DELETE\n- Suelen implementarse como árboles B o B+ (estructura balanceada)\n- Ocupan espacio adicional en disco\n\nCuándo usarlos:\n- En columnas usadas frecuentemente en cláusulas WHERE\n- En columnas usadas para JOIN\n- En columnas usadas en ORDER BY y GROUP BY\n- En claves primarias y foráneas (generalmente automático)\n\nCuándo evitarlos:\n- En tablas pequeñas\n- En columnas con baja cardinalidad (pocos valores únicos)\n- En columnas que cambian frecuentemente\n- Cuando el espacio es crítico\n\nUn exceso de índices puede degradar el rendimiento general del sistema."
            }
        ],
        
        # Algorithm questions
        [
            {
                "question": "¿Cuál es la diferencia entre algoritmos de ordenación estables e inestables?",
                "answer": "La estabilidad en algoritmos de ordenación se refiere a si el algoritmo mantiene el orden relativo de elementos iguales.\n\n- Algoritmos estables: Mantienen el orden relativo de elementos con la misma clave de ordenación.\n  Ejemplos: Merge Sort, Insertion Sort, Bubble Sort, Counting Sort\n\n- Algoritmos inestables: No garantizan preservar el orden relativo de elementos iguales.\n  Ejemplos: Quick Sort, Heap Sort, Selection Sort\n\nPor ejemplo, si ordenamos una lista de estudiantes primero por nota y luego por nombre, un algoritmo estable preservará el orden alfabético entre estudiantes con la misma nota."
            },
            {
                "question": "¿Puedes explicar la notación Big O y dar ejemplos?",
                "answer": "La notación Big O describe el comportamiento asintótico (límite superior) del tiempo de ejecución o espacio requerido por un algoritmo cuando el tamaño de entrada tiende a infinito.\n\nEjemplos comunes (de más eficiente a menos):\n\n- O(1) - Tiempo constante: Acceso a un elemento en un array, inserción/eliminación en una pila.\n- O(log n) - Logarítmico: Búsqueda binaria, operaciones en árboles balanceados.\n- O(n) - Lineal: Recorrer un array, búsqueda lineal.\n- O(n log n) - Lineal-logarítmico: Algoritmos eficientes de ordenación como Merge Sort y Quick Sort.\n- O(n²) - Cuadrático: Insertion Sort, Bubble Sort, algoritmos con bucles anidados simples.\n- O(2^n) - Exponencial: Soluciones por fuerza bruta para problemas NP-completos.\n- O(n!) - Factorial: Resolver el problema del viajante por fuerza bruta.\n\nAl analizar algoritmos, nos centramos en el comportamiento para entradas grandes y términos de mayor crecimiento."
            },
            {
                "question": "¿Qué es la programación dinámica y cuándo se utiliza?",
                "answer": "La programación dinámica es una técnica para resolver problemas complejos dividiéndolos en subproblemas más simples, resolviendo cada subproblema una sola vez, y almacenando sus soluciones para evitar recálculos.\n\nCaracterísticas clave:\n1. Subestructura óptima: La solución óptima contiene soluciones óptimas de subproblemas\n2. Subproblemas superpuestos: Los mismos subproblemas se resuelven múltiples veces\n\nEnfoques:\n- Top-down (memoización): Resolver recursivamente con caché de resultados\n- Bottom-up (tabulación): Construir soluciones de subproblemas pequeños a grandes\n\nEjemplos de problemas:\n- Secuencia de Fibonacci\n- Problema de la mochila (Knapsack)\n- Distancia de edición (Levenshtein)\n- Caminos más cortos (Algoritmo de Floyd-Warshall)\n- Subsecuencia común más larga\n- Corte óptimo de varillas\n\nSe utiliza cuando un problema tiene subproblemas superpuestos y una subestructura óptima, especialmente cuando un enfoque de fuerza bruta sería exponencial."
            }
        ],
        
        # Networks questions
        [
            {
                "question": "¿Puedes explicar las capas del modelo OSI?",
                "answer": "El modelo OSI (Open Systems Interconnection) es un marco conceptual de 7 capas que estandariza las funciones de un sistema de comunicaciones:\n\n7. Capa de aplicación: Interfaz entre aplicaciones y servicios de red (HTTP, SMTP, FTP)\n\n6. Capa de presentación: Traducción de datos, cifrado, compresión (SSL/TLS, JPEG, MP3)\n\n5. Capa de sesión: Establece, gestiona y termina conexiones (NetBIOS, RPC)\n\n4. Capa de transporte: Entrega fiable de datos extremo a extremo, control de flujo (TCP, UDP)\n\n3. Capa de red: Encaminamiento de paquetes entre redes diferentes (IP, ICMP, routers)\n\n2. Capa de enlace de datos: Transferencia fiable entre nodos conectados directamente (Ethernet, Wi-Fi, switches)\n\n1. Capa física: Transmisión de bits crudos a través del medio físico (cables, frecuencias radio, hubs)\n\nCada capa proporciona servicios a la capa superior y utiliza servicios de la capa inferior, lo que permite la modularidad en el diseño de redes."
            },
            {
                "question": "¿Cuál es la diferencia entre TCP y UDP?",
                "answer": "TCP (Transmission Control Protocol) y UDP (User Datagram Protocol) son protocolos de la capa de transporte con diferentes características:\n\nTCP:\n- Orientado a conexión: establece una conexión antes de enviar datos\n- Garantiza la entrega de datos (retransmisión de paquetes perdidos)\n- Control de congestión y flujo\n- Entrega ordenada de paquetes\n- Mayor overhead (cabeceras más grandes, establecimiento de conexión)\n- Ideal para: web (HTTP), email (SMTP), transferencia de archivos (FTP)\n\nUDP:\n- Sin conexión: envía datos sin establecer conexión previa\n- No garantiza la entrega ni el orden de los paquetes\n- Sin control de congestión o flujo\n- Menor overhead y latencia\n- Ideal para: streaming (video/audio), DNS, VoIP, juegos online\n\nEn resumen, TCP prioriza la fiabilidad mientras que UDP prioriza la velocidad y la simplicidad."
            },
            {
                "question": "¿Qué es CIDR y cómo funciona?",
                "answer": "CIDR (Classless Inter-Domain Routing) es un método de asignación de direcciones IP y enrutamiento IP que reemplazó al sistema de clases (A, B, C) anterior para utilizar el espacio de direcciones de forma más eficiente.\n\nCaracterísticas principales:\n\n- Notación CIDR: dirección IP seguida de una barra y un número que indica el tamaño del prefijo de red\n  Ejemplo: 192.168.1.0/24\n\n- El número después de la barra (prefijo) indica cuántos bits se usan para la parte de red\n  /24 significa 24 bits para red y 8 bits para host (en IPv4)\n\n- Cálculo de direcciones disponibles: 2^(32-prefijo) - 2\n  Ejemplo: /24 permite 2^(32-24) - 2 = 254 hosts\n\n- Permite subredes de tamaño variable (VLSM, Variable Length Subnet Masking)\n\n- Facilita la agregación de rutas (route summarization)\n\nCIDR permite una asignación más granular de direcciones IP, reduciendo el desperdicio y ralentizando el agotamiento de direcciones IPv4."
            }
        ]
    ]
    
    # Return the appropriate QA set with fallback
    return qa_sets[min(category, len(qa_sets)-1)]


def generate_sample_data_for_demo():
    """
    Generate a complete set of sample data for demonstration purposes.
    
    Returns:
        Dict containing all sample data (agents, messages, etc.)
    """
    # Generate agents
    agents = generate_sample_agents(5)
    
    # Generate messages for each agent
    all_messages = []
    for agent in agents:
        # Get some sample students
        sample_students = agent["students"][:3] if agent["students"] else []
        
        # Generate messages for each student
        for student in sample_students:
            messages = generate_sample_messages(agent["id"], student, random.randint(3, 8))
            all_messages.extend(messages)
    
    return {
        "agents": agents,
        "messages": all_messages
    }


def load_sample_data_to_session():
    """
    Load sample data into session state for demonstration.
    """
    import streamlit as st
    
    # Generate data
    data = generate_sample_data_for_demo()
    
    # Store in session state (but don't overwrite existing data)
    if "created_agents" not in st.session_state:
        st.session_state.created_agents = []
    
    # Add only agents that don't already exist
    existing_ids = [agent["id"] for agent in st.session_state.created_agents]
    for agent in data["agents"]:
        if agent["id"] not in existing_ids:
            st.session_state.created_agents.append(agent)
    
    if "chat_logs" not in st.session_state:
        st.session_state.chat_logs = []
    st.session_state.chat_logs.extend(data["messages"])
    
    return len(data["agents"]), len(data["messages"])