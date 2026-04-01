# 🔐 Secure LLM Gateway

> Capa de seguridad (proxy) que intercepta prompts de usuarios antes de que lleguen a una API de IA, previniendo la fuga de datos sensibles (DLP).

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![Security](https://img.shields.io/badge/Focus-Cloud%20Security-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## ¿Qué hace?

Cuando un usuario envía un prompt a una IA, este gateway lo intercepta y escanea en busca de datos sensibles antes de reenviarlo. Si detecta PII, bloquea la request con un error `403 Forbidden` y registra el intento en los logs.
```
Usuario → [Secure LLM Gateway] → IA (OpenAI, etc.)
                  ↓
           Motor DLP (regex)
                  ↓
         PII encontrada? → 403 Blocked
         Prompt limpio?  → Reenviar al LLM
```

---

## Datos sensibles detectados

| Tipo | Ejemplo | Validación |
|------|---------|------------|
| DNI argentino | `32.456.789` | Regex |
| Tarjeta de crédito | `4532-0151-1283-0366` | Regex + Luhn |
| Email | `usuario@dominio.com` | Regex |
| CUIL / CUIT | `20-32456789-1` | Regex |
| Teléfono argentino | `+54 9 11 1234-5678` | Regex |

---

## Tecnologías

- **FastAPI** — framework web async de alto rendimiento
- **Pydantic** — validación de esquemas y datos
- **Uvicorn** — servidor ASGI
- **Pytest** — tests unitarios
- **Regex + Luhn** — detección y validación de PII

---

## Instalación
```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/secure-llm-gateway.git
cd secure-llm-gateway

# 2. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar el servidor
uvicorn main:app --reload --port 8000
```

---

## Uso

### Prompt limpio → pasa al LLM
```bash
curl -s -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Explicá el ciclo del agua."}' | python3 -m json.tool
```
```json
{
    "response": "[MOCK] Prompt limpio.",
    "model": "gpt-4o-mini",
    "gateway_status": "ALLOWED_MOCK"
}
```

### Prompt con PII → bloqueado
```bash
curl -s -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Mandá el reporte a juan@empresa.com"}' | python3 -m json.tool
```
```json
{
    "detail": {
        "error": "DLP_VIOLATION",
        "message": "Tu prompt contiene datos sensibles y fue bloqueado.",
        "violations": [
            {
                "type": "EMAIL",
                "redacted_value": "ju***@em***"
            }
        ]
    }
}
```

---

## Tests
```bash
pytest tests/ -v
```
```
tests/test_dlp.py::test_dni_con_puntos         PASSED
tests/test_dlp.py::test_dni_sin_puntos         PASSED
tests/test_dlp.py::test_email                  PASSED
tests/test_dlp.py::test_visa_valida            PASSED
tests/test_dlp.py::test_luhn_invalida_rechazada PASSED
tests/test_dlp.py::test_cuit                   PASSED
tests/test_dlp.py::test_prompt_limpio          PASSED
tests/test_dlp.py::test_multi_pii              PASSED

8 passed in 0.41s
```

---

## Estructura del proyecto
```
secure-llm-gateway/
├── main.py          # FastAPI app y lógica del gateway
├── dlp.py           # Motor DLP: detección de PII
├── schemas.py       # Modelos Pydantic
├── config.py        # Configuración por variables de entorno
├── requirements.txt
└── tests/
    └── test_dlp.py  # Tests unitarios
```

---

## Roadmap

- [ ] Autenticación con JWT
- [ ] Rate limiting por IP
- [ ] Docker + docker-compose
- [ ] Métricas con Prometheus
- [ ] Detección semántica con spaCy
- [ ] Deploy en AWS Lambda / Cloud Run

---

## Licencia

MIT