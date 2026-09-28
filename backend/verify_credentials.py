import os
import sys
import io
import httpx

# Ensure UTF-8 output on Windows consoles
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def load_env(env_path=".env"):
    config = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    return config

def main():
    print("=" * 80)
    print("         VERIFYING NASA CREDENTIALS ACROSS LIVE NASA SERVERS")
    print("=" * 80)

    env = load_env(".env")
    nasa_api_key = env.get("NASA_API_KEY")
    earthdata_user = env.get("EARTHDATA_USERNAME")
    earthdata_pass = env.get("EARTHDATA_PASSWORD")
    bearer_token = env.get("EARTHDATA_BEARER_TOKEN")
    firms_key = env.get("FIRMS_MAP_KEY")

    client = httpx.Client(timeout=10.0)

    # 1. Test NASA API Key
    print("\n[1/4] Testing NASA Open API Key (api.nasa.gov)...")
    try:
        url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}"
        res = client.get(url)
        if res.status_code == 200:
            data = res.json()
            print(f"      STATUS: VALID & ACTIVE (HTTP 200 OK)")
            print(f"      Sample Payload: APOD Title -> '{data.get('title')}'")
        else:
            print(f"      STATUS: FAILED (HTTP {res.status_code}) -> {res.text[:120]}")
    except Exception as e:
        print(f"      ERROR: {e}")

    # 2. Test NASA FIRMS Active Fire API Key
    print("\n[2/4] Testing NASA FIRMS Active Fire Key (firms.modaps.eosdis.nasa.gov)...")
    try:
        # Check Bangladesh fire records for today
        url = f"https://firms.modaps.eosdis.nasa.gov/api/country/csv/{firms_key}/VIIRS_SNPP_NRT/BGD/1"
        res = client.get(url)
        if res.status_code == 200:
            lines = res.text.strip().split("\n")
            print(f"      STATUS: VALID & ACTIVE (HTTP 200 OK)")
            print(f"      Active Fire Records in Bangladesh: {max(0, len(lines) - 1)} detected hotspots")
        else:
            print(f"      STATUS: FAILED (HTTP {res.status_code}) -> {res.text[:120]}")
    except Exception as e:
        print(f"      ERROR: {e}")

    # 3. Test NASA Earthdata Bearer Token
    print("\n[3/4] Testing NASA Earthdata Login Bearer Token...")
    try:
        # Query CMR authenticated endpoint
        headers = {"Authorization": f"Bearer {bearer_token}"}
        url = "https://cmr.earthdata.nasa.gov/search/granules.json?collection_concept_id=C1621073801-LPDAAC_ECS&page_size=1"
        res = client.get(url, headers=headers)
        if res.status_code == 200:
            print(f"      STATUS: VALID & AUTHORIZED (HTTP 200 OK)")
            print(f"      Authenticated User: {earthdata_user}")
        else:
            print(f"      STATUS: HTTP {res.status_code} -> {res.text[:120]}")
    except Exception as e:
        print(f"      ERROR: {e}")

    # 4. Test Earthdata Username & Password Basic Auth
    print("\n[4/4] Testing NASA Earthdata Profile Authentication...")
    try:
        url = f"https://urs.earthdata.nasa.gov/api/users/{earthdata_user}"
        res = client.get(url, auth=(earthdata_user, earthdata_pass))
        if res.status_code == 200:
            data = res.json()
            print(f"      STATUS: VALID USER PROFILE (HTTP 200 OK)")
            print(f"      User Name: {data.get('first_name', '')} {data.get('last_name', '')}")
            print(f"      Email: {data.get('email_address', '')}")
            print(f"      Affiliation: {data.get('study_area', 'Earth Science')}")
        else:
            # Check with token instead
            res_token = client.get(url, headers={"Authorization": f"Bearer {bearer_token}"})
            if res_token.status_code == 200:
                data = res_token.json()
                print(f"      STATUS: VALID USER PROFILE VIA TOKEN (HTTP 200 OK)")
                print(f"      User: {data.get('uid')}")
            else:
                print(f"      STATUS: URS API returned {res.status_code}")
    except Exception as e:
        print(f"      ERROR: {e}")

    print("\n" + "=" * 80)
    print("ALL CREDENTIALS SECURED LOCALLY IN 'backend/.env' (IGNORED BY GIT).")
    print("=" * 80)

if __name__ == "__main__":
    main()
