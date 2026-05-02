import json
import logging
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client("s3")

def lambda_handler(event, context):
    path_params = event.get("pathParameters") or {}
    bucket_name = path_params.get("bucket_name", "").strip()

    if not bucket_name:
        return _response(400, {"error": "El parámetro bucket_name es requerido"})

    query_params = event.get("queryStringParameters") or {}
    prefix       = query_params.get("prefix", "")
    page_token   = query_params.get("page_token", "")

    try:
        max_keys = int(query_params.get("max_keys", 100))
        max_keys = max(1, min(max_keys, 1000))
    except ValueError:
        return _response(400, {"error": "max_keys debe ser un número entero"})

    logger.info(f"Listando objetos — bucket={bucket_name} prefix={prefix!r} max_keys={max_keys}")

    try:
        kwargs = {"Bucket": bucket_name, "MaxKeys": max_keys}
        if prefix:     kwargs["Prefix"]            = prefix
        if page_token: kwargs["ContinuationToken"] = page_token

        resp    = s3_client.list_objects_v2(**kwargs)
        objects = [
            {
                "key":           obj["Key"],
                "size_bytes":    obj["Size"],
                "last_modified": obj["LastModified"].isoformat(),
                "storage_class": obj.get("StorageClass", "STANDARD"),
            }
            for obj in resp.get("Contents", [])
        ]

        return _response(200, {
            "bucket":          bucket_name,
            "prefix":          prefix,
            "objects":         objects,
            "total":           len(objects),
            "is_truncated":    resp.get("IsTruncated", False),
            "next_page_token": resp.get("NextContinuationToken"),
        })

    except NoCredentialsError:
        return _response(403, {"error": "Credenciales inválidas o no encontradas"})
    except ClientError as e:
        code = e.response["Error"]["Code"]
        msg  = e.response["Error"]["Message"]
        if code == "NoSuchBucket":
            return _response(404, {"error": f"El bucket '{bucket_name}' no existe"})
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
