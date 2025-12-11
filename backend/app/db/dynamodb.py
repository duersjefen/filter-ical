"""
DynamoDB client setup and table operations.

Single-table design with the following key patterns:
- PK: DOMAIN#<key>, FILTER#<uuid>, ADMIN#<email>, CALENDAR#<id>
- SK: METADATA, EVENT#<date>#<uid>, GROUP#<id>, etc.
"""

import os
from functools import lru_cache
from typing import Optional

import boto3
from boto3.dynamodb.conditions import Key, Attr


# Table name from environment (set by SST)
TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "filter-ical-table")

# AWS region
REGION = os.environ.get("AWS_REGION", "eu-north-1")


@lru_cache()
def get_client():
    """Get boto3 DynamoDB client (cached)."""
    return boto3.client("dynamodb", region_name=REGION)


@lru_cache()
def get_resource():
    """Get boto3 DynamoDB resource (cached)."""
    return boto3.resource("dynamodb", region_name=REGION)


@lru_cache()
def get_table():
    """Get DynamoDB table resource (cached)."""
    return get_resource().Table(TABLE_NAME)


# Key builders for single-table design
def domain_pk(domain_key: str) -> str:
    """Build partition key for domain."""
    return f"DOMAIN#{domain_key}"


def filter_pk(link_uuid: str) -> str:
    """Build partition key for filter."""
    return f"FILTER#{link_uuid}"


def admin_pk(email: str) -> str:
    """Build partition key for admin."""
    return f"ADMIN#{email}"


def calendar_pk(calendar_id: int) -> str:
    """Build partition key for calendar."""
    return f"CALENDAR#{calendar_id}"


def metadata_sk() -> str:
    """Sort key for metadata records."""
    return "METADATA"


def event_sk(date: str, uid: str) -> str:
    """Sort key for event records (sorted by date)."""
    return f"EVENT#{date}#{uid}"


def group_sk(group_id: int) -> str:
    """Sort key for group records."""
    return f"GROUP#{group_id}"


# Query helpers
def query_by_pk(pk: str, sk_prefix: Optional[str] = None) -> list:
    """
    Query items by partition key, optionally filtering by sort key prefix.

    Args:
        pk: Partition key value
        sk_prefix: Optional sort key prefix to filter by

    Returns:
        List of items matching the query
    """
    table = get_table()

    if sk_prefix:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(pk) & Key("SK").begins_with(sk_prefix)
        )
    else:
        response = table.query(
            KeyConditionExpression=Key("PK").eq(pk)
        )

    return response.get("Items", [])


def get_item(pk: str, sk: str) -> Optional[dict]:
    """
    Get a single item by primary key.

    Args:
        pk: Partition key value
        sk: Sort key value

    Returns:
        Item dict or None if not found
    """
    table = get_table()
    response = table.get_item(Key={"PK": pk, "SK": sk})
    return response.get("Item")


def put_item(item: dict) -> dict:
    """
    Put an item into the table.

    Args:
        item: Item dict (must include PK and SK)

    Returns:
        The item that was put
    """
    table = get_table()
    table.put_item(Item=item)
    return item


def delete_item(pk: str, sk: str) -> bool:
    """
    Delete an item by primary key.

    Args:
        pk: Partition key value
        sk: Sort key value

    Returns:
        True if deleted
    """
    table = get_table()
    table.delete_item(Key={"PK": pk, "SK": sk})
    return True


def update_item(pk: str, sk: str, updates: dict) -> dict:
    """
    Update specific attributes of an item.

    Args:
        pk: Partition key value
        sk: Sort key value
        updates: Dict of attribute names to new values

    Returns:
        Updated item
    """
    table = get_table()

    # Build update expression
    update_expr_parts = []
    expr_attr_names = {}
    expr_attr_values = {}

    for i, (key, value) in enumerate(updates.items()):
        attr_name = f"#attr{i}"
        attr_value = f":val{i}"
        update_expr_parts.append(f"{attr_name} = {attr_value}")
        expr_attr_names[attr_name] = key
        expr_attr_values[attr_value] = value

    update_expr = "SET " + ", ".join(update_expr_parts)

    response = table.update_item(
        Key={"PK": pk, "SK": sk},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
        ReturnValues="ALL_NEW"
    )

    return response.get("Attributes", {})


def query_by_gsi(index_name: str, key_name: str, key_value: str) -> list:
    """
    Query items using a Global Secondary Index.

    Args:
        index_name: Name of the GSI
        key_name: Attribute name to query on
        key_value: Value to match

    Returns:
        List of items matching the query
    """
    table = get_table()
    response = table.query(
        IndexName=index_name,
        KeyConditionExpression=Key(key_name).eq(key_value)
    )
    return response.get("Items", [])


def batch_write(items: list[dict]) -> None:
    """
    Batch write multiple items.

    Args:
        items: List of items to write (each must include PK and SK)
    """
    table = get_table()

    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)


def batch_delete(keys: list[tuple[str, str]]) -> None:
    """
    Batch delete multiple items.

    Args:
        keys: List of (pk, sk) tuples to delete
    """
    table = get_table()

    with table.batch_writer() as batch:
        for pk, sk in keys:
            batch.delete_item(Key={"PK": pk, "SK": sk})
