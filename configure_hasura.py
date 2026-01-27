"""
Track tables in Hasura and configure permissions
"""
import requests
import json

HASURA_URL = "http://localhost:8081/v1/metadata"
HASURA_ADMIN_SECRET = "myadminsecret"

headers = {
    "Content-Type": "application/json",
    "x-hasura-admin-secret": HASURA_ADMIN_SECRET
}

# Track tables
tables_to_track = ["workflows", "nodes", "edges", "faqs"]

for table in tables_to_track:
    payload = {
        "type": "pg_track_table",
        "args": {
            "source": "default",
            "table": {
                "schema": "public",
                "name": table
            }
        }
    }
    
    response = requests.post(HASURA_URL, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"✓ Tracked table: {table}")
    else:
        print(f"✗ Failed to track {table}: {response.text}")

# Set up foreign key relationships
relationships = [
    {
        "table": "nodes",
        "name": "workflow",
        "using": {
            "foreign_key_constraint_on": "workflow_id"
        }
    },
    {
        "table": "edges",
        "name": "workflow",
        "using": {
            "foreign_key_constraint_on": "workflow_id"
        }
    },
    {
        "table": "edges",
        "name": "source_node",
        "using": {
            "foreign_key_constraint_on": "source_node_id"
        }
    },
    {
        "table": "edges",
        "name": "target_node",
        "using": {
            "foreign_key_constraint_on": "target_node_id"
        }
    },
    {
        "table": "workflows",
        "name": "nodes",
        "using": {
            "foreign_key_constraint_on": {
                "table": {
                    "schema": "public",
                    "name": "nodes"
                },
                "column": "workflow_id"
            }
        }
    },
    {
        "table": "workflows",
        "name": "edges",
        "using": {
            "foreign_key_constraint_on": {
                "table": {
                    "schema": "public",
                    "name": "edges"
                },
                "column": "workflow_id"
            }
        }
    }
]

print("\nSetting up relationships...")
for rel in relationships:
    payload = {
        "type": "pg_create_object_relationship",
        "args": {
            "source": "default",
            "table": rel["table"],
            "name": rel["name"],
            "using": rel["using"]
        }
    }
    
    response = requests.post(HASURA_URL, json=payload, headers=headers)
    if response.status_code == 200:
        print(f"✓ Created relationship: {rel['table']}.{rel['name']}")
    else:
        # Try array relationship if object relationship fails
        payload["type"] = "pg_create_array_relationship"
        response = requests.post(HASURA_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✓ Created array relationship: {rel['table']}.{rel['name']}")
        else:
            print(f"✗ Failed to create relationship {rel['table']}.{rel['name']}: {response.text}")

# Set up permissions for anonymous/public access
print("\nSetting up permissions...")
for table in tables_to_track:
    # Allow all operations for admin role
    permission_types = ["insert", "select", "update", "delete"]
    
    for perm_type in permission_types:
        payload = {
            "type": f"pg_create_{perm_type}_permission",
            "args": {
                "source": "default",
                "table": table,
                "role": "user",
                "permission": {
                    "columns": "*",
                    "filter": {},
                    "check": {} if perm_type in ["insert", "update"] else None
                }
            }
        }
        
        # Remove None values
        if payload["args"]["permission"].get("check") is None:
            payload["args"]["permission"].pop("check", None)
        
        response = requests.post(HASURA_URL, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"✓ Set {perm_type} permission on {table} for user role")
        else:
            print(f"✗ Failed to set {perm_type} permission on {table}: {response.text}")

print("\n✓ Hasura configuration complete!")
