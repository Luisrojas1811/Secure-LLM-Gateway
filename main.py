import logging
import httpx
from fastapi import FastAPI, HTTPException, Request
from schemas import GatewayRequest, GatewayResponse, SecurityViolation
from dlp import PIIDetector
from config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  [%(levelname)s]  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("secure-llm-gateway")

app = FastAPI(title="Secure LLM Gateway", version="1.0.0")
pii_detector = PIIDetector()

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "secure-llm-gateway"}

@app.post("/v1/chat", response_model=GatewayResponse)
async def chat_gateway(request: GatewayRequest, raw_request: Request):
    client_ip = raw_request.client.host if raw_request.client else "unknown"
    logger.info("Incoming request from %s", client_ip)

    violations = pii_detector.scan(request.prompt)

    if violations:
        types = ", ".join({v.type for v in violations})
        preview = (request.prompt[:60] + "…") if len(request.prompt) > 60 else request.prompt
        logger.warning("🚨 DLP BLOCK | ip=%s | types=[%s] | preview='%s'", client_ip, types, preview)
        raise HTTPException(
            status_code=403,
            detail={
                "error": "DLP_VIOLATION",
                "message": "Tu prompt contiene datos sensibles y fue bloqueado.",
                "violations": [v.model_dump() for v in violations],
            },
        )

    logger.info("Prompt limpio — reenviando al proveedor LLM.")
    return GatewayResponse(
        response="[MOCK] Prompt limpio. Configurá LLM_API_KEY en .env para requests reales.",
        model=request.model,
        prompt_tokens=len(request.prompt.split()),
        gateway_status="ALLOWED_MOCK",
    )