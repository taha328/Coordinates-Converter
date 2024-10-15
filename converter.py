import math
import unittest

a = 6378137.0  # axe semi-majeur en mètres
f = 1 / 298.257223563  # aplatissement
b = a * (1 - f)  # axe semi-minor
e2 = (a**2 - b**2) / a**2  # premier excentricité au carré

def geodetic_to_cartesian(lat, lon, h):
    # Convertir la latitude et la longitude des degrés en radians
    lat = math.radians(lat)
    lon = math.radians(lon)
    
    # Calculer N (le rayon de courbure dans le vertical premier)
    N = a / math.sqrt(1 - e2 * math.sin(lat)**2)
    
    # Calculer les coordonnées X, Y, Z
    X = (N + h) * math.cos(lat) * math.cos(lon)
    Y = (N + h) * math.cos(lat) * math.sin(lon)
    Z = (N * (1 - e2) + h) * math.sin(lat)
    
    return X, Y, Z

# Fonction pour convertir de cartésien à géodétique en utilisant la méthode directe
def cartesian_to_geodetic_direct(X, Y, Z):
    # Étape 1 : Calculer r
    r = math.sqrt(X**2 + Y**2 + Z**2)

    # Étape 2 : Calculer mu (μ)
    mu = math.atan((Z / math.sqrt(X**2 + Y**2))*(((1 - f )) + ((a * e2)/r)))

    # Étape 3 : Calculer la longitude (λ)
    lon = math.atan(Y / X)  # Utilisation correcte de atan2 pour la longitude

    # Étape 4 : Calculer la latitude (φ)
    sin_mu = math.sin(mu)
    cos_mu = math.cos(mu)
    
    lat = math.atan(
        (Z * (1 - f) + e2 * a * sin_mu**3) /
        ((1 - f) * (math.sqrt(X**2 + Y**2) - e2 * a * cos_mu**3))
    )

    # Étape 5 : Calculer la hauteur (h)
    h = (math.sqrt(X**2 + Y**2) * math.cos(lat) +
         Z * math.sin(lat) -
         a * math.sqrt(1 - e2 * math.sin(lat)**2))
    
    # Convertir les radians en degrés pour la latitude et la longitude
    lat = math.degrees(lat)
    lon = math.degrees(lon)
    
    return lat, lon, h

def cartesian_to_geodetic_iterative(X, Y, Z, epsilon=1e-12, max_iter=1000):
    # Calculer la longitude initiale (λ)
    lon = math.atan2(Y, X)
    
    # Valeur initiale de φ₀ (approximation)
    p = math.sqrt(X**2 + Y**2)
    phi = math.atan(Z / p)
    
    # Processus itératif
    for i in range(max_iter):
        N = a / math.sqrt(1 - e2 * math.sin(phi)**2)
        h = p / math.cos(phi) - N
        
        # Nouvelle valeur de φₙ
        phi_new = math.atan((Z / p) * (1 / (1 - e2 * N / (N + h))))
        
        # Vérification de la convergence utilisant le critère de différence relative
        if abs((phi_new - phi) / phi_new) < epsilon:
            phi = phi_new
            break
        
        # Mettre à jour φ pour l'itération suivante
        phi = phi_new
    
    # Latitude, longitude, et hauteur finales
    lat = math.degrees(phi)
    lon = math.degrees(lon)
    
    return lat, lon, h

class TestGeodeticCartesianConversion(unittest.TestCase):
    
    def test_geodetic_to_cartesian(self):
        # Point géodétique connu (latitude, longitude, hauteur)
        lat, lon, h = 52.2296756, 21.0122287, 100.0
        
        # Coordonnées cartésiennes attendues (X, Y, Z)
        expected_X = 3654529.60
        expected_Y = 1403737.48
        expected_Z = 5018575.77
        
        X, Y, Z = geodetic_to_cartesian(lat, lon, h)
        
        # Vérifier si les valeurs retournées sont proches des attendues
        self.assertAlmostEqual(X, expected_X, places=1)
        self.assertAlmostEqual(Y, expected_Y, places=1)
        self.assertAlmostEqual(Z, expected_Z, places=1)

    def test_cartesian_to_geodetic(self):
        # Point géodétique connu (latitude, longitude, hauteur)
        X, Y, Z = 3654529.60, 1403737.48, 5018575.77 
        
        # Coordonnées géodétiques attendues (latitude, longitude, hauteur)
        expected_lat = 52.2296756
        expected_lon = 21.0122287
        expected_h = 100.0
        
        lat, lon, h = cartesian_to_geodetic_direct(X, Y, Z)
        
        # Vérifier si les valeurs retournées sont proches des attendues
        self.assertAlmostEqual(lat, expected_lat, places=1)
        self.assertAlmostEqual(lon, expected_lon, places=1)
        self.assertAlmostEqual(h, expected_h, places=1)

def main():
    print("Choisissez la transformation :")
    print("1. Coordonnées géographiques vers les coordonnées cartésiennes")
    print("2. Coordonnées cartésiennes vers les coordonnées géographiques")
    choice = int(input("Entrez votre choix (1 ou 2) : "))

    if choice == 1:
        # Géodétique à cartésien
        lat = float(input("Entrez la latitude (en degrés) : "))
        lon = float(input("Entrez la longitude (en degrés) : "))
        h = float(input("Entrez la hauteur (en mètres) : "))
        
        X, Y, Z = geodetic_to_cartesian(lat, lon, h)
        print(f"Coordonnées cartésiennes : X = {X}, Y = {Y}, Z = {Z}")
    
    elif choice == 2:
        method_choice = input("Choisissez la méthode de conversion : A (Directe) ou B (Itérative) : ").strip().upper()

        X = float(input("Entrez X (en mètres) : "))
        Y = float(input("Entrez Y (en mètres) : "))
        Z = float(input("Entrez Z (en mètres) : "))
        
        if method_choice == 'A':
            lat, lon, h = cartesian_to_geodetic_direct(X, Y, Z)
            print(f"Coordonnées géodétiques (Méthode Directe) : Latitude = {lat}°, Longitude = {lon}°, Hauteur = {h} mètres")
        
        elif method_choice == 'B':
            lat, lon, h = cartesian_to_geodetic_iterative(X, Y, Z)
            print(f"Coordonnées géodétiques (Méthode Itérative) : Latitude = {lat}°, Longitude = {lon}°, Hauteur = {h} mètres")
        
        else:
            print("Choix de méthode invalide. Veuillez redémarrer et sélectionner A ou B.")
    
    else:
        print("Choix invalide. Veuillez redémarrer et sélectionner 1 ou 2.")

if __name__ == "__main__":
    main()
    unittest.main()
