import json
import os
import urllib.error
import urllib.request

from dotenv import load_dotenv

load_dotenv()
ctx7_key = os.getenv("CONTEXT7_API_KEY")

req_data = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "query-docs",
        "arguments": {
            "libraryId": "/websites/tally_prime_developer",
            "query": "Tally XML envelope structure for exporting Ledger Vouchers with IGST"
        }
    }
}).encode("utf-8")

req = urllib.request.Request("https://mcp.context7.com/mcp", data=req_data)
req.add_header("Content-Type", "application/json")
req.add_header("CONTEXT7_API_KEY", ctx7_key)

try:
    with urllib.request.urlopen(req, timeout=10) as response:
        print("SUCCESS:")
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP ERROR {e.code}: {e.reason}")
    print(e.read().decode())
except Exception as e:
    print(f"ERROR: {e!s}")
