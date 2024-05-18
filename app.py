import os
from dotenv import load_dotenv
from pathlib import Path
import psutil
import requests
import json
import datetime
from time import sleep

dotenv_path = Path('.env')
load_dotenv(dotenv_path=dotenv_path)

def sendToBaselime(data, dataset="logs", namespace="GetSystemStats", service="GetSystemStats"):
    """curl -X 'POST' 'https://events.baselime.io/v1/logs' \
    -H 'x-api-key: $BASELIME_API_KEY' \
    -H 'Content-Type: application/json' \
    -H 'x-service: my-service' \
    -H 'x-namespace: my-namespace' \
    -d '[
            {
                "message": "This is an example log event",
                "error": "TypeError: Cannot read property 'something' of undefined",
                "requestId": "6092d6f0-3bfa-4d62-9d0b-5bc7ae6518a1",
                "namespace": "https://api.domain.com/resource/{id}"
            },
            {
                "message": "This is another example log event",
                "requestId": "6092d6f0-3bfa-4d62-9d0b-5bc7ae6518a1",
                "data": {"userId": "01HBRCB38K2K4V5SDR7YC1D0ZB"},
                "duration": 127
            }
        ]'
    """

    url = "https://events.baselime.io/v1/" + dataset
    headers = {
        "x-api-key": os.getenv("BASELIME_API_KEY"),
        "Content-Type": "application/json",
        "x-service": service,
        "x-namespace": namespace,
    }
    data = [
        {
            "message": "System Stats",
            "data": data,
            "timestamp": datetime.datetime.now().isoformat(),
        }
    ]

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 202:
        print("Data sent to Baselime successfully")
    else:
        raise Exception("Failed to send data to Baselime", response.text)

def getData(disks=["/"]):
    memory_info = psutil.virtual_memory()

    disks_info = []
    for disk in disks: # get info for each disk
        if not os.path.exists(disk): # check if disk exists
            raise Exception(f"Disk {disk} does not exist")
        
        disks_info.append(psutil.disk_usage(disk))

    data = {
        "CPU": {
            "total_number_of_cpus": psutil.cpu_count(),
            "cpu_utilization_percentage": psutil.cpu_percent(),
        },
        "RAM": {
            "total_ram": (memory_info.total / (1024 ** 3)).__round__(2),
            "used_ram": (memory_info.used / (1024 ** 3)).__round__(2),
            "available_ram": (memory_info.available / (1024 ** 3)).__round__(2),
        },
        "Disk": {

        },
    }

    for i, disk in enumerate(disks):
        data["Disk"][disk] = {
            "total_disk_space": (disks_info[i].total / (1024 ** 3)).__round__(2),
            "used_disk_space": (disks_info[i].used / (1024 ** 3)).__round__(2),
            "free_disk_space": (disks_info[i].free / (1024 ** 3)).__round__(2),
        }

    return data

def waitToRetry(minutes=5):
    print(f"Waiting for {minutes} minutes before retrying...")
    sleep(minutes*60)
    print("Retrying...")

if __name__ == "__main__":

    while True:
        try:
            data = getData(disks=["/", "/home"])
            print(data)
            sendToBaselime(data)

            waitToRetry(5)
        except Exception as e:
            print(e)

            waitToRetry(5)
        except KeyboardInterrupt:
            print("Exiting...")
            break