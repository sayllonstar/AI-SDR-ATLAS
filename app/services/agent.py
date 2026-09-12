import os
import json
import boto3
import requests
from botocore.exceptions import BotoCoreError, ClientError
from app.schemas.tools import BEDROCK_TOOLS, SDR_SYSTEM_PROMPT

# Inicialização do Cliente AWS Bedrock Runtime
bedrock_client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# ID do modelo no Bedrock (ex: Claude 3.5 Sonnet ou Claude 3 Haiku)
MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")

EVOLUTION_URL = os.getenv("EVOLUTION_API_URL", "http://evolution-api:8080")
EVOLUTION_KEY = os.getenv("EVOLUTION_API_KEY")
INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE", "sdr_atlas")

def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Executa a lógica de negócio associada às ferramentas do agente."""
    if tool_name == "check_available_slots":
        return {
            "status": "success",
            "available_slots": ["Amanhã às 14:00", "Amanhã às 16:30", "Quinta-feira às 10:00"]
        }
    elif tool_name == "book_meeting":
        return {
            "status": "confirmed",
            "event_id": "evt_aws_889123",
            "message": "Reunião agendada com sucesso via AWS Bedrock Agent."
        }
    return {"error": "Ferramenta não encontrada."}

def send_whatsapp_message(phone: str, text: str):
    """Envia a mensagem gerada de volta ao usuário via Evolution API."""
    url = f"{EVOLUTION_URL}/message/sendText/{INSTANCE_NAME}"
    headers = {
        "apikey": EVOLUTION_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "number": phone,
        "options": {"delay": 1000, "presence": "composing"},
        "textMessage": {"text": text}
    }
    try:
        requests.post(url, headers=headers, json=payload, timeout=5)
    except requests.RequestException as e:
        print(f"Erro ao enviar mensagem via WhatsApp API: {e}")

def run_sdr_agent(phone_number: str, incoming_message: str):
    """Orquestra a chamada ao Bedrock com suporte a Tool Calling."""
    
    # Montagem do histórico no formato exigido pela API Converse
    messages = [
        {
            "role": "user",
            "content": [{"text": incoming_message}]
        }
    ]

    system_prompts = [{"text": SDR_SYSTEM_PROMPT}]

    try:
        # PRIMEIRA CHAMADA: Envia o contexto e as ferramentas disponíveis ao Bedrock
        response = bedrock_client.converse(
            modelId=MODEL_ID,
            messages=messages,
            system=system_prompts,
            inferenceConfig={"temperature": 0.3, "maxTokens": 500},
            toolConfig={"tools": BEDROCK_TOOLS}
        )

        output_message = response["output"]["message"]
        stop_reason = response.get("stopReason")

        # Verifica se o modelo decidiu acionar uma Tool
        if stop_reason == "tool_use":
            # Adiciona a resposta com a requisição da ferramenta ao histórico
            messages.append(output_message)

            tool_requests = [
                content for content in output_message["content"] if "toolUse" in content
            ]

            tool_results_content = []

            for tool_req in tool_requests:
                tool_use = tool_req["toolUse"]
                tool_use_id = tool_use["toolUseId"]
                tool_name = tool_use["name"]
                tool_args = tool_use["input"]

                # Executa a função Python correspondente
                execution_result = execute_tool(tool_name, tool_args)

                # Formata o retorno da Tool exigido pela API Converse do Bedrock
                tool_results_content.append({
                    "toolResult": {
                        "toolUseId": tool_use_id,
                        "content": [{"json": execution_result}]
                    }
                })

            # Adiciona o resultado da ferramenta com o papel 'user'
            messages.append({
                "role": "user",
                "content": tool_results_content
            })

            # SEGUNDA CHAMADA: Envia o resultado da Tool de volta para sintetizar a resposta
            final_response = bedrock_client.converse(
                modelId=MODEL_ID,
                messages=messages,
                system=system_prompts,
                inferenceConfig={"temperature": 0.3, "maxTokens": 500},
                toolConfig={"tools": BEDROCK_TOOLS}
            )

            final_content = final_response["output"]["message"]["content"]
            final_text = "".join([c["text"] for c in final_content if "text" in c])

        else:
            # Caso não tenha chamado ferramenta, extrai o texto direto
            final_text = "".join([c["text"] for c in output_message["content"] if "text" in c])

        # Envia a resposta processada para o WhatsApp do Lead
        if final_text:
            send_whatsapp_message(phone_number, final_text)

    except (BotoCoreError, ClientError) as error:
        print(f"Erro na execução do Amazon Bedrock: {error}")

