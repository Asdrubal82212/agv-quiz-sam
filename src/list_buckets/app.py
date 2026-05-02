import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    logger.info("Listando todos los buckets S3")
    try:
        response = s3_client.list_buckets()
        buckets  = response.get("Buckets", [])
        result   = [
            {
                "name": b["Name"],
                "creation_date": b["CreationDate"].isoformat(),
            }
            for b in buckets
        ]
        logger.info(f"Buckets encontrados: {len(result)}")
        return _response(200, {"buckets": result, "total": len(result)})

    except NoCredentialsError:
        return _response(403, {"error": "Credenciales inválidas o no encontradas"})
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg  = e.response["Error"]["Message"]
        return _response(500, {"error": msg, "code": code})
    except Exception as e:
        logger.exception("Error inesperado")
        return _response(500, {"error": "Error interno", "detail": str(e)})

def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body, ensure_ascii=False),
    }
