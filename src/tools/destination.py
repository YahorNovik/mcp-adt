import os
import requests
from urllib.parse import urljoin

# === STEP 1: Load environment ===
from dotenv import load_dotenv
load_dotenv()

# These come from VCAP_SERVICES or your .env
XSUAA_CLIENT_ID = os.getenv("XSUAA_CLIENT_ID")
XSUAA_CLIENT_SECRET = os.getenv("XSUAA_CLIENT_SECRET")
XSUAA_URL = os.getenv("XSUAA_URL")  # e.g. https://<subdomain>.authentication.<region>.hana.ondemand.com
DESTINATION_NAME = os.getenv("DESTINATION_NAME", "SAP_E19_SYSTEM")

def get_final_url():
    # === STEP 2: Get OAuth token from XSUAA ===
 oauth_response = requests.post(
    url=f"{XSUAA_URL}/oauth/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    auth=(XSUAA_CLIENT_ID, XSUAA_CLIENT_SECRET),
    data={"grant_type": "client_credentials"},
)
 oauth_response.raise_for_status()
 oauth_token = oauth_response.json()["access_token"]

# === STEP 3: Get destination definition ===
 destination_config_url = f"https://destination-configuration.cfapps.<region>.hana.ondemand.com/destination-configuration/v1/destinations/{DESTINATION_NAME}"
 config_response = requests.get(
    url=destination_config_url,
    headers={"Authorization": f"Bearer {oauth_token}"}
)
 config_response.raise_for_status()
 destination = config_response.json()

# === STEP 4: Use Connectivity Proxy to call the actual endpoint ===
 connectivity_proxy_host = os.getenv("CONNECTIVITY_PROXY_HOST", "adt-mcp-server-connectivity.internal.cf")
 connectivity_proxy_port = os.getenv("CONNECTIVITY_PROXY_PORT", "20003")
 connectivity_token = oauth_token  # reuse same token

# Compose final call
 final_url = urljoin(destination["URL"], "/sap/bc/adt/ping")
 # Compose final call
 final_url = urljoin(destination["URL"], "/sap/bc/adt/ping")
 proxies = {
    "http": f"http://{connectivity_proxy_host}:{connectivity_proxy_port}",
    "https": f"http://{connectivity_proxy_host}:{connectivity_proxy_port}",
 }
 headers = {
    "Proxy-Authorization": f"Bearer {connectivity_token}",
    "Authorization": destination["Authentication"],  # If you want to inject manually
    "SAP-Connectivity-SCC-Location_ID": destination.get("CloudConnectorLocationId", "")
}

 response = requests.get(final_url, headers=headers, proxies=proxies)
 print("SAP response:", response.status_code, response.text)
 return get_final_url


# === STEP 2: Get OAuth token from XSUAA ===
oauth_response = requests.post(
    url=f"{XSUAA_URL}/oauth/token",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    auth=(XSUAA_CLIENT_ID, XSUAA_CLIENT_SECRET),
    data={"grant_type": "client_credentials"},
)
oauth_response.raise_for_status()
oauth_token = oauth_response.json()["access_token"]

# === STEP 3: Get destination definition ===
destination_config_url = f"https://destination-configuration.cfapps.eu10-004.hana.ondemand.com/destination-configuration/v1/destinations/{DESTINATION_NAME}"
config_response = requests.get(
    url=destination_config_url,
    headers={"Authorization": f"Bearer {oauth_token}"}
)
config_response.raise_for_status()
destination = config_response.json()

print("Destination info:", destination)

# === STEP 4: Use Connectivity Proxy to call the actual endpoint ===
connectivity_proxy_host = os.getenv("CONNECTIVITY_PROXY_HOST", "proxy.internal.cf")
connectivity_proxy_port = os.getenv("CONNECTIVITY_PROXY_PORT", "20003")
connectivity_token = oauth_token  # reuse same token

# Compose final call
final_url = urljoin(destination["URL"], "/sap/bc/adt/ping")
proxies = {
    "http": f"http://{connectivity_proxy_host}:{connectivity_proxy_port}",
    "https": f"http://{connectivity_proxy_host}:{connectivity_proxy_port}",
}
headers = {
    "Proxy-Authorization": f"Bearer {connectivity_token}",
    "Authorization": destination["Authentication"],  # If you want to inject manually
    "SAP-Connectivity-SCC-Location_ID": destination.get("CloudConnectorLocationId", "")
}

response = requests.get(final_url, headers=headers, proxies=proxies)
print("SAP response:", response.status_code, response.text)
 
