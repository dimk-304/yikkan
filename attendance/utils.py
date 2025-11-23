import face_recognition
import numpy as np

def get_face_encoding(image_file):
    """
    Genera el encoding facial a partir de un archivo de imagen.
    Retorna el primer rostro encontrado o None si no hay rostros.
    """
    try:
        image = face_recognition.load_image_file(image_file)
        encodings = face_recognition.face_encodings(image)
        if encodings:
            return encodings[0].tolist() # Convertir numpy array a lista para JSON
        return None
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

def compare_faces(known_encodings, face_encoding_to_check, tolerance=0.5):
    """
    Compara un encoding desconocido con una lista de conocidos.
    Retorna el índice del match o -1 si no hay coincidencia.
    
    Usa una tolerancia balanceada (0.5) y verifica la distancia facial.
    Tolerancia más baja = más estricto (0.6 es el default, 0.5 es balanceado)
    """
    if not known_encodings:
        return -1
        
    # Convertir listas a numpy arrays
    known_encodings_np = [np.array(e) for e in known_encodings]
    face_encoding_to_check_np = np.array(face_encoding_to_check)

    # Comparar con tolerancia balanceada
    matches = face_recognition.compare_faces(
        known_encodings_np, 
        face_encoding_to_check_np, 
        tolerance=tolerance
    )
    
    # Calcular distancias faciales para mayor precisión
    face_distances = face_recognition.face_distance(
        known_encodings_np, 
        face_encoding_to_check_np
    )
    
    if True in matches:
        # Obtener el índice del mejor match (menor distancia)
        best_match_index = int(np.argmin(face_distances))  # Convertir a int de Python
        
        # Verificar que el mejor match esté dentro de la tolerancia
        if matches[best_match_index] and face_distances[best_match_index] < tolerance:
            print(f"Match found with distance: {face_distances[best_match_index]:.4f}")
            return best_match_index
    
    # Si no hay match o la distancia es muy alta
    if len(face_distances) > 0:
        min_distance = np.min(face_distances)
        print(f"No match found. Closest distance: {min_distance:.4f} (threshold: {tolerance})")
    
    return -1
