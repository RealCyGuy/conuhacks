import csv
import json
from collections import defaultdict

SEVERITIES = ["low", "medium", "high"]
DAMAGE_COSTS = {
    "low": 50000,
    "medium": 100000,
    "high": 200000,
}


def parse_data(data):
    units = [
        {"price": 5000, "units": 5},
        {"price": 2000, "units": 10},
        {"price": 8000, "units": 3},
        {"price": 15000, "units": 2},
        {"price": 3000, "units": 8},
    ]
    operational_cost = 0
    damage_cost = 0
    severity_report = defaultdict(int)
    addressed = 0
    delayed = 0

    for fire in data:
        unit_deployed_for_fire = False
        for unit in units:
            if unit["units"] > 0:
                unit["units"] -= 1
                operational_cost += unit["price"]
                addressed += 1
                unit_deployed_for_fire = True
                severity_report[fire["severity"]] += 1
                break
        if not unit_deployed_for_fire:
            delayed += 1
            damage_cost += DAMAGE_COSTS[fire["severity"]]

    return (
        f"Number of fires addressed: {addressed}\n"
        f"Number of fires delayed: {delayed}\n"
        f"Total operational cost: ${operational_cost}\n"
        f"Estimated damage costs from delayed responses: ${damage_cost}\n"
        f"Severity report: {json.dumps(severity_report)}"
    )


if __name__ == "__main__":
    data = []
    with open("current_wildfiredata.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    print(parse_data(data))
