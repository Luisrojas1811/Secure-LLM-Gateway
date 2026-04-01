from pydantic import BaseModel, Field

class GatewayRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    model: str = Field("gpt-4o-mini")
    max_tokens: int = Field(512, ge=1, le=4096)
    temperature: float = Field(0.7, ge=0.0, le=2.0)

class SecurityViolation(BaseModel):
    type: str
    redacted_value: str

class GatewayResponse(BaseModel):
    response: str
    model: str
    prompt_tokens: int
    gateway_status: str