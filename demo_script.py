import requests as r
import time

endpoint = "/openapi.json"

urls = [
    "gateway.redwater-58716629.eastus.azurecontainerapps.io",
    "reservations.redwater-58716629.eastus.azurecontainerapps.io",
    "users.redwater-58716629.eastus.azurecontainerapps.io",
    "communications.redwater-58716629.eastus.azurecontainerapps.io",
    "stats.redwater-58716629.eastus.azurecontainerapps.io",
    "venues.redwater-58716629.eastus.azurecontainerapps.io",
    "opinions.redwater-58716629.eastus.azurecontainerapps.io",
    "points.redwater-58716629.eastus.azurecontainerapps.io",
    "summaries.redwater-58716629.eastus.azurecontainerapps.io"
]


def make_requests(urls: list[str], proto: str = "https://", endpoint: str = "/openapi.json") -> list[str]:
    results = []
    for url in urls:
        service = url.split(".").pop(0)
        try:
            response = r.get(f"{proto}{url}{endpoint}", timeout=2)
            result = f"{service}-"
            if response.status_code > 199 or response.status_code < 300:
                result += "OK"
            else:
                result += f"Failed({response.status_code})"
            results.append(result)
        except:
            results.append(f"{service}- Timeout")
    return results

def loop(urls: list[str]):
    responses = make_requests(urls)
    for response in responses:
        print(response)
    time.sleep(5.0)

if __name__ == "__main__":
    while True:
        loop(urls)
        print("=========================")
