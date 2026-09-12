from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class MessageData(BaseModel):
    conversation: Optional[str] = None
    extendedTextMessage: Optional[Dict[str, Any]] = None

class EvolutionWebhookPayload(BaseModel):
    event: str
    instance: str
    data: Dict[str, Any]

    def extract_phone_and_text(self) -> tuple[Optional[str], Optional[str]]:
        """Extrai o número de telefone e o texto limpo do payload."""
        key = self.data.get("key", {})
        from_me = key.get("fromMe", False)
        
        # Ignora mensagens enviadas pelo próprio bot
        if from_me:
            return None, None

        remote_jid = key.get("remoteJid", "")
        phone = remote_jid.split("@")[0] if "@" in remote_jid else None

        message = self.data.get("message", {})
        text = (
            message.get("conversation") 
            or message.get("extendedTextMessage", {}).get("text")
        )

        return phone, text
