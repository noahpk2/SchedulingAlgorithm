import random

num_employees = 25

def generate_test_data(num_employees):
    data = {
        #Two sets of hours - 1st is operating hours(prep, opening, closing , etc), 2nd is open hours(business service hours)

        

        "hours": {
            
            "su": ["08:00-00:00", "16:00-23:00"],
            "mo": ["10:00-00:00", "16:00-23:00"],
            "tu": ["10:00-00:00", "16:00-23:00"],
            "we": ["10:00-00:00", "16:00-23:00"],
            "th": ["10:00-00:00", "16:00-23:00"],
            "fr": ["10:00-01:00", "16:00-00:00"],
            "sa": ["08:00-01:00", "16:00-00:00"]
        },
        "positions": {
            #           role : 
            #           hourlyRate: what the business pays this employee per hour,
            #           maxGuests: how many guests in an hour one person in this role can serve, 
            #           minOnPeak: how many instances of this role are required during peak hours
            #           min: how many instances of this role are required total
            #           max: how many instances of this role are allowed total
            #           hours_before_open: how many hours before open this role should be scheduled
            #           hours_after_close: how many hours after close this role should be scheduled

            "manager": {"hourlyRate": 35, "maxGuests": 0, "min": 1},
            "server": {"hourlyRate": random.randint(10, 15), "maxGuests": 25},
            "bartender": {"hourlyRate": random.randint(10, 15), "maxGuests": 50},
            "host": {"hourlyRate": random.randint(8, 10), "maxGuests": 100},
            "expo": {"hourlyRate": random.randint(8, 10), "maxGuests": 100, "minOnPeak": 1},
            "support": {"hourlyRate": random.randint(8, 10), "maxGuests": 75},
            "line cook": {"hourlyRate": random.randint(12, 20), "maxGuests": 75},
            "prep cook": {"hourlyRate": random.randint(8, 10), "maxGuests": 75},
            "dishwasher": {"hourlyRate": random.randint(8, 10), "maxGuests": 75},
            "sous chef": {"hourlyRate": random.randint(18, 25), "maxGuests": 75},
            "head chef": {"hourlyRate": random.randint(25, 35), "maxGuests": 75},

        },
        # Daily traffic is totally random right now, but we could improve this later to more accurately reflect a real business.
        "dailyTraffic": {day: [random.randint(10, 80) for _ in range(16)] for day in ["su", "mo", "tu", "we", "th", "fr", "sa"]},
        "empl": []
    }

    roles = list(data["positions"].keys())
    for _ in range(num_employees - 4):  # reserving slots for 4 managers
        role = random.choice(roles[1:])  # exclude manager
        availability = random.choice(
            #creating random availability for each employee. 0 = not available, 1 = available, string = specific hours
            [1, 0, f"{random.randint(8, 10)}:00-{random.randint(14, 16)}:00", f"{random.randint(16, 18)}:00-{random.randint(22, 24)}:00"])
        data["empl"].append({
            "id": _ + 1, # employee id
            "pos": role, # employee position
            "ph": random.randint(4, 8), # employee hourly rate
            "maxh": random.randint(5, 10), # employee max hours (per day)
            "avl": [availability for _ in range(7)] # employee availability (per day, for the week)
        })

    # Add managers separately to ensure there are enough of them
    for i in range(num_employees - 4, num_employees):
        data["empl"].append({
            "id": i + 1,
            "pos": "manager",
            "ph": random.randint(6, 10),
            "maxh": random.randint(8, 12),
            "avl": [1 for _ in range(7)]
        })

    return data
