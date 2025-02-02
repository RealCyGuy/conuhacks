import csv
import json
import datetime
import heapq
from collections import defaultdict
from enum import Enum, auto


class FireSeverity(Enum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


class FireUnit:
    def __init__(self, price, units, deployment_time):
        self.price = price
        self.units = units
        self.deployment_time = deployment_time  # Time taken to deploy the unit

    def deploy_unit(self):
        if self.units > 0:
            self.units -= 1
            return self.price
        return None

    def reset(self):
        self.units = self.total_units


class FireStation:
    DAMAGE_COSTS = {
        FireSeverity.LOW: 50000,
        FireSeverity.MEDIUM: 100000,
        FireSeverity.HIGH: 200000,
    }

    def __init__(self, units):
        self.units = [FireUnit(unit["price"], unit["units"], unit["deployment_time"]) for unit in units]
        self.operational_cost = 0
        self.damage_cost = 0
        self.severity_report = defaultdict(int)
        self.addressed = 0
        self.delayed = 0

    def handle_fire(self, severity):
        severity_enum = FireSeverity[severity.upper()]
        max_cost = sum(unit.price for unit in self.units)
        dp = [[float('inf')] * (max_cost + 1) for _ in range(len(self.units) + 1)]
        dp[0][0] = 0  # Base case: No cost for zero fires handled

        for i in range(1, len(self.units) + 1):
            unit = self.units[i - 1]
            for j in range(max_cost + 1):
                if j >= unit.price:
                    dp[i][j] = min(dp[i - 1][j], dp[i - 1][j - unit.price] + self.DAMAGE_COSTS[severity_enum])
                else:
                    dp[i][j] = dp[i - 1][j]

        best_unit = None
        min_cost = float('inf')

        for unit in self.units:
            if unit.units > 0 and dp[len(self.units)][unit.price] < min_cost:
                min_cost = dp[len(self.units)][unit.price]
                best_unit = unit

        if best_unit and best_unit.deploy_unit():
            self.operational_cost += best_unit.price
            self.addressed += 1
            self.severity_report[severity_enum.name.lower()] += 1
        else:
            self.delayed += 1
            self.damage_cost += self.DAMAGE_COSTS[severity_enum]

    def parse_data(self, data):
        fire_queue = []
        for fire in data:
            severity_enum = FireSeverity[fire["severity"].upper()]
            heapq.heappush(fire_queue, (fire["fire_start_time"], -severity_enum.value, fire))

        while fire_queue:
            _, _, fire = heapq.heappop(fire_queue)
            self.handle_fire(fire["severity"])

    def report(self):
        ordered_severity_report = {key: self.severity_report[key] for key in ["low", "medium", "high"] if
                                   key in self.severity_report}
        return (
            f"Number of fires addressed: {self.addressed}\n"
            f"Number of fires delayed: {self.delayed}\n"
            f"Total operational cost: ${self.operational_cost}\n"
            f"Estimated damage costs from delayed responses: ${self.damage_cost}\n"
            f"Fire Severity report: {json.dumps(ordered_severity_report)}"
        )


def load_fire_data(filename):
    data = []
    with open(filename, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["fire_start_time"] = datetime.datetime.strptime(row["fire_start_time"], "%Y-%m-%d %H:%M:%S")
            data.append(row)
    return data


def get_fire_units():
    return [
        {"price": 5000, "units": 5, "deployment_time": datetime.timedelta(minutes=30)},
        {"price": 2000, "units": 10, "deployment_time": datetime.timedelta(hours=1)},
        {"price": 8000, "units": 3, "deployment_time": datetime.timedelta(minutes=45)},
        {"price": 15000, "units": 2, "deployment_time": datetime.timedelta(hours=2)},
        {"price": 3000, "units": 8, "deployment_time": datetime.timedelta(hours=1, minutes=30)},
    ]


if __name__ == "__main__":
    fire_units = get_fire_units()
    station = FireStation(fire_units)
    fire_data = load_fire_data("current_wildfiredata.csv")
    station.parse_data(fire_data)
    print(station.report())