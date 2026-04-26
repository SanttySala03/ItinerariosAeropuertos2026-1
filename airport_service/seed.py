import urllib.request
import json

AIRPORT_API = "http://127.0.0.1:8001"

airports = [
    # Colombia
    {"name": "Aeropuerto Internacional El Dorado", "city": "Bogotá", "country": "Colombia", "iata_code": "BOG", "latitude": 4.7016, "longitude": -74.1469},
    {"name": "Aeropuerto Internacional José María Córdova", "city": "Medellín", "country": "Colombia", "iata_code": "MDE", "latitude": 6.1645, "longitude": -75.4231},
    {"name": "Aeropuerto Internacional Alfonso Bonilla Aragón", "city": "Cali", "country": "Colombia", "iata_code": "CLO", "latitude": 3.5432, "longitude": -76.3816},
    {"name": "Aeropuerto Internacional Rafael Núñez", "city": "Cartagena", "country": "Colombia", "iata_code": "CTG", "latitude": 10.4424, "longitude": -75.5130},
    {"name": "Aeropuerto Internacional Ernesto Cortissoz", "city": "Barranquilla", "country": "Colombia", "iata_code": "BAQ", "latitude": 10.8896, "longitude": -74.7808},
    {"name": "Aeropuerto Internacional Matecaña", "city": "Pereira", "country": "Colombia", "iata_code": "PEI", "latitude": 4.8127, "longitude": -75.7395},
    {"name": "Aeropuerto Internacional Camilo Daza", "city": "Cúcuta", "country": "Colombia", "iata_code": "CUC", "latitude": 7.9276, "longitude": -72.5115},
    {"name": "Aeropuerto Internacional Gustavo Rojas Pinilla", "city": "San Andrés", "country": "Colombia", "iata_code": "ADZ", "latitude": 12.5836, "longitude": -81.7112},
    # Europa
    {"name": "Aeropuerto Internacional Humberto Delgado", "city": "Lisboa", "country": "Portugal", "iata_code": "LIS", "latitude": 38.7742, "longitude": -9.1342},
    {"name": "Aeropuerto Adolfo Suárez Madrid-Barajas", "city": "Madrid", "country": "España", "iata_code": "MAD", "latitude": 40.4719, "longitude": -3.5626},
    {"name": "Aeropuerto de Barcelona-El Prat", "city": "Barcelona", "country": "España", "iata_code": "BCN", "latitude": 41.2971, "longitude": 2.0785},
    {"name": "Aeropuerto de París Charles de Gaulle", "city": "París", "country": "Francia", "iata_code": "CDG", "latitude": 49.0097, "longitude": 2.5479},
    {"name": "Aeropuerto de Londres Heathrow", "city": "Londres", "country": "Reino Unido", "iata_code": "LHR", "latitude": 51.4700, "longitude": -0.4543},
    # Norteamérica
    {"name": "Aeropuerto Internacional John F. Kennedy", "city": "Nueva York", "country": "Estados Unidos", "iata_code": "JFK", "latitude": 40.6413, "longitude": -73.7781},
    {"name": "Aeropuerto Internacional de Miami", "city": "Miami", "country": "Estados Unidos", "iata_code": "MIA", "latitude": 25.7959, "longitude": -80.2870},
    {"name": "Aeropuerto Internacional O'Hare", "city": "Chicago", "country": "Estados Unidos", "iata_code": "ORD", "latitude": 41.9742, "longitude": -87.9073},
    # Latinoamérica
    {"name": "Aeropuerto Internacional de Tocumen", "city": "Ciudad de Panamá", "country": "Panamá", "iata_code": "PTY", "latitude": 9.0714, "longitude": -79.3835},
    {"name": "Aeropuerto Internacional El Dorado de Lima", "city": "Lima", "country": "Perú", "iata_code": "LIM", "latitude": -12.0219, "longitude": -77.1143},
    {"name": "Aeropuerto Internacional de Guarulhos", "city": "São Paulo", "country": "Brasil", "iata_code": "GRU", "latitude": -23.4356, "longitude": -46.4731},
    {"name": "Aeropuerto Internacional Ezeiza", "city": "Buenos Aires", "country": "Argentina", "iata_code": "EZE", "latitude": -34.8222, "longitude": -58.5358},
]

def seed():
    creados = 0
    omitidos = 0

    for airport in airports:
        data = json.dumps(airport).encode("utf-8")
        req = urllib.request.Request(
            f"{AIRPORT_API}/airports",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as res:
                if res.status == 201:
                    print(f"✓ Creado: {airport['iata_code']} — {airport['city']}")
                    creados += 1
        except urllib.error.HTTPError as e:
            if e.code == 400:
                print(f"○ Ya existe: {airport['iata_code']} — {airport['city']}")
                omitidos += 1
            else:
                print(f"✗ Error {e.code}: {airport['iata_code']}")

    print(f"\n✓ {creados} aeropuertos creados, {omitidos} ya existían.")

if __name__ == "__main__":
    seed()