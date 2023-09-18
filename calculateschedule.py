"""    Hard Constraints: Always prioritize these. These are non-negotiable and include:
        Meeting the operational hours.
        Ensuring mandatory roles are always staffed.
        Meeting guest traffic requirements.

    Optimization Phase: This phase aims to optimize various objectives, which can be weighted according to the manager's preferences. The main objectives include:
        Labor Cost Minimization: Reducing the overall labor cost.
        Employee Preference Fulfillment: Scheduling employees as close to their preferences as possible.
        Fairness: Ensuring that hours are distributed fairly among employees, especially those with similar roles and preferences.
        (Any other objective that might be important, such as minimizing overtime, maximizing employee rest periods between shifts, etc.)

    Evaluation Phase: Evaluate the schedule based on the objectives and weights. We want to check that no hard constraints are violated and that the objectives are met.

    Adjustment Phase: After the initial schedule is generated, there should be functionalities to:
        Adjust for unexpected changes.
        Make manual adjustments if needed.

    Finalization: Once the manager is satisfied, finalize the schedule.
    
    """





# Utility functions and scheduling algorithms

from collections import defaultdict
import copy
import math
import random


def day_to_index(day):
    # Convert day string to index.
    days = ["su", "mo", "tu", "we", "th", "fr", "sa"]
    return days.index(day)


def enforce_breaks(schedule):
    '''Ensure that employees aren't scheduled back-to-back without breaks. '''
    # Sort schedule by employee ID and start time
    sorted_schedule = sorted(schedule, key=lambda x: (
        x['employee_id'], x['slot'].split('-')[0]))
    for i in range(len(sorted_schedule) - 1):
        if sorted_schedule[i]['employee_id'] == sorted_schedule[i + 1]['employee_id']:
            end_time_current_shift = int(
                sorted_schedule[i]['slot'].split('-')[1].split(':')[0])
            start_time_next_shift = int(
                sorted_schedule[i + 1]['slot'].split('-')[0].split(':')[0])
            if start_time_next_shift - end_time_current_shift < 1:  # No break between shifts
                return False
    return True


def is_employee_available(employee, day, hour):
    # Check if an employee is available at a specific day and hour.
    availability = employee["availability"].get(day, "off")
    if availability == "open":  # Available all day
        return True
    elif availability == "off":  # Not available
        return False
    else:
        # Check specific availability window
        start, end = map(lambda x: int(
            x.split(":")[0]), availability.split('-'))
        return start <= hour < end


def required_staff_for_guests(guest_count, max_guests_per_employee):
    # Calculate the required number of employees based on guest count.
    return (guest_count + max_guests_per_employee - 1) // max_guests_per_employee

# Hard Constraints


def enhanced_day_schedule(data, day_short):
    '''Enhanced scheduling for a specific day with prioritized allocation. '''
    day_schedule = []
    shift_count_by_employee = defaultdict(int)
    sorted_roles = sorted(
        data["role_requirements"].items(), key=lambda x: x[1], reverse=True)
    sorted_employees = sorted(
        data["empl"], key=lambda e: shift_count_by_employee[e["id"]])
    for slot in data["preferred_slots"].get(day_short, []):
        for role, min_required in sorted_roles:
            num_assigned = 0
            for employee in sorted_employees:
                if role in employee["roles"]:
                    availability = employee["availability"].get(
                        day_short, "off")
                    start_slot = int(slot.split("-")[0].split(":")[0])
                    end_slot = int(slot.split("-")[1].split(":")[0])
                    if availability == "open" or ("-" in availability and int(availability.split("-")[0].split(":")[0]) <= start_slot and int(availability.split("-")[1].split(":")[0]) >= end_slot):
                        temp_schedule = day_schedule.copy()
                        temp_schedule.append({
                            "employee_id": employee["id"],
                            "role": role,
                            "slot": slot
                        })
                        if enforce_breaks(temp_schedule):
                            day_schedule = temp_schedule
                            num_assigned += 1
                            shift_count_by_employee[employee["id"]] += 1
                            if num_assigned >= min_required:
                                break
    return day_schedule


def generate_entire_weekly_schedule_v4(data):
    '''Generate a schedule for the entire week using the enhanced day scheduling function.'''
    days = ["mo", "tu", "we", "th", "fr", "sa", "su"]
    weekly_schedule = {}
    for day in days:
        weekly_schedule[day] = enhanced_day_schedule(data, day)
    return weekly_schedule


def schedule_mandatory_roles(schedule, employees, hours, positions):
    # Schedule roles that need at least one employee at all times.
    for day, day_schedule in schedule.items():
        for hour_idx, _ in enumerate(day_schedule):
            for role, role_data in positions.items():
                if "min" in role_data:
                    for _ in range(role_data["min"]):
                        # Find an available employee for this role and hour
                        for employee in employees:
                            if employee["pos"] == role and is_employee_available(employee, day, hour_idx):
                                schedule[day][hour_idx] = {
                                    "role": role, "employee_id": employee["id"]}
                                break
    return schedule


def schedule_based_on_traffic(schedule, employees, daily_traffic, positions, hours):
    # Schedule employees based on estimated guest traffic.
    for day, day_schedule in schedule.items():
        operating_hours = hours[day]["operatingHours"]
        start_hour = int(operating_hours[0].split(":")[0])
        end_hour = int(operating_hours[1].split(":")[0])
        for hour_idx in range(start_hour, end_hour):
            traffic_for_hour = daily_traffic[day][hour_idx]
            for role, role_data in positions.items():
                required_staff = required_staff_for_guests(
                    traffic_for_hour, role_data["maxGuests"])
                for _ in range(required_staff):
                    # Find an available employee for this role and hour
                    for employee in employees:
                        if employee["pos"] == role and is_employee_available(employee, day, hour_idx):
                            schedule[day][hour_idx] = {
                                "role": role, "employee_id": employee["id"]}
                            break
    return schedule


def complete_schedule_with_preferred_hours(schedule, employees, hours):
    # Schedule employees based on their preferred hours.
    for employee in employees:
        preferred_hours = employee["ph"]
        hours_scheduled = sum(
            1 for _, day_schedule in schedule.items() for hour_schedule in day_schedule if hour_schedule["employee_id"] == employee["id"])
        if hours_scheduled >= preferred_hours:
            continue
        for day, day_schedule in schedule.items():
            operating_hours = hours[day]["operatingHours"]
            start_hour = int(operating_hours[0].split(":")[0])
            end_hour = int(operating_hours[1].split(":")[0])
            for hour_idx in range(start_hour, end_hour):
                if is_employee_available(employee, day, hour_idx) and not any(s["employee_id"] == employee["id"] for s in day_schedule):
                    schedule[day][hour_idx] = {
                        "role": employee["pos"], "employee_id": employee["id"]}
                    hours_scheduled += 1
                    if hours_scheduled >= preferred_hours:
                        break
            if hours_scheduled >= preferred_hours:
                break
    return schedule

# Optimization using simulated annealing


def perturb_schedule(schedule):
    """Perturb the given schedule to generate a new schedule."""
    new_schedule = copy.deepcopy(schedule)
    days = list(new_schedule.keys())
    day = random.choice(days)

    # Choose a random perturbation method
    method = random.choice(['swap_shifts_within_day', 'swap_shifts_between_days',
                            'change_role', 'swap_shifts_between_employees'])

    if method == 'swap_shifts_within_day':
        # Swap two time slots within the same day
        if len(new_schedule[day]) < 2:
            return new_schedule
        slot1, slot2 = random.sample(new_schedule[day], 2)
        idx1, idx2 = new_schedule[day].index(
            slot1), new_schedule[day].index(slot2)
        new_schedule[day][idx1], new_schedule[day][idx2] = slot2, slot1

    elif method == 'swap_shifts_between_days':
        # Swap time slots between two different days
        day2 = random.choice(days)
        if day2 == day or not new_schedule[day] or not new_schedule[day2]:
            return new_schedule
        slot1, slot2 = random.choice(
            new_schedule[day]), random.choice(new_schedule[day2])
        idx1, idx2 = new_schedule[day].index(
            slot1), new_schedule[day2].index(slot2)
        new_schedule[day][idx1], new_schedule[day2][idx2] = slot2, slot1

    elif method == 'change_role':
        # Change the role of an employee for a specific slot
        if not new_schedule[day]:
            return new_schedule
        slot = random.choice(new_schedule[day])
        roles = list(positions.keys())
        slot["role"] = random.choice(roles)

    elif method == 'swap_shifts_between_employees':
        # Swap shifts between two employees
        if len(new_schedule[day]) < 2:
            return new_schedule
        slot1, slot2 = random.sample(new_schedule[day], 2)
        slot1["employee_id"], slot2["employee_id"] = slot2["employee_id"], slot1["employee_id"]

    return new_schedule


def accept_schedule(current_cost, new_cost, temp):
    """Accept the new schedule with a probability based on the current cost, new cost, and temperature."""
    if new_cost < current_cost:
        return True
    return random.uniform(0, 1) < math.exp((current_cost - new_cost) / temp)


def calculate_labor_cost_v2(schedule, employees, positions):
    """Calculate the total labor cost for the given schedule."""
    total_cost = 0
    for day, roles in schedule.items():
        for role, time_slots in roles.items():
            for slot in time_slots:
                if slot["empl"]:
                    # Assuming only one employee per slot for simplicity
                    employee_id = slot["empl"][0]
                    employee = next(
                        e for e in employees if e["id"] == employee_id)
                    rate = positions[role]["hourlyRate"]
                    total_cost += rate
    return total_cost


def schedule_cost_v2(schedule, employees, positions, daily_traffic, weights):
    """Calculate the total cost of the schedule based on the given weights."""
    labor_cost = calculate_labor_cost_v2(schedule, employees, positions)
    all_hours = [employee_hours(schedule, employee["id"]) for employee in employees]
    mean_hours = sum(all_hours) / len(all_hours)
    fairness_penalty = sum(
        (h - mean_hours)**2 for h in all_hours) / len(all_hours)
    preference_penalty = sum(
        abs(employee_hours(schedule, employee["id"]) - employee["ph"])
        for employee in employees
    )
    cost = (
        labor_cost * weights.get('labor_cost', 1)
        + fairness_penalty * weights.get('fairness', 1)
        + preference_penalty * weights.get('preference', 1)
    )
    return cost


def simulated_annealing_v2(initial_schedule, employees, positions, daily_traffic, weights, initial_temp=1000, cooling_rate=0.995, max_iterations=10000):
    """Schedule employees using simulated annealing."""
    current_schedule = initial_schedule
    current_cost = schedule_cost_v2(
        current_schedule, employees, positions, daily_traffic, weights)
    best_schedule = current_schedule
    best_cost = current_cost
    temp = initial_temp
    for iteration in range(max_iterations):
        new_schedule = perturb_schedule(current_schedule)
        new_cost = schedule_cost_v2(
            new_schedule, employees, positions, daily_traffic, weights)
        if new_cost < current_cost or accept_schedule(current_cost, new_cost, temp):
            current_schedule, current_cost = new_schedule, new_cost
            if new_cost < best_cost:
                best_schedule, best_cost = new_schedule, new_cost
        temp *= cooling_rate
    return best_schedule


def perturb_schedule(schedule):
    """Perturb the given schedule to generate a new schedule."""
    new_schedule = copy.deepcopy(schedule)
    method = random.choice(['swap_shifts_within_day', 'swap_shifts_between_days',
    'change_role', 'swap_shifts_between_employees'])
    ...
    return new_schedule


def accept_schedule(current_cost, new_cost, temp):
    """Accept the new schedule with a probability based on the current cost, new cost, and temperature."""
    if new_cost < current_cost:
        return True
    return random.uniform(0, 1) < math.exp((current_cost - new_cost) / temp)


##############################################################################################################
# Evaluation


def employee_hours(schedule, employee_id):
    """
    Calculate the total hours scheduled for an employee based on the generated schedule.
    """
    hours = 0
    for day, day_schedule in schedule.items():
        for hour_schedule in day_schedule:
            if hour_schedule["employee_id"] == employee_id:
                hours += 1
    return hours


def evaluate_schedule(schedule, employees, hours, positions):
    """Evaluate the schedule based on certain criteria."""
    evaluation_results = {}
    total_hours_scheduled = sum(employee_hours(
        schedule, employee["id"]) for employee in employees)
    desired_hours = sum(employee["ph"] for employee in employees)
    hours_difference = total_hours_scheduled - desired_hours
    evaluation_results["hours_difference"] = hours_difference

    # Ensure mandatory roles are always scheduled
    mandatory_roles_met = all(
        any(hour_schedule["role"] == role for hour_schedule in day_schedule)
        for role, role_data in positions.items() if "min" in role_data
        for _, day_schedule in schedule.items()
    )
    evaluation_results["mandatory_roles_met"] = mandatory_roles_met

    # Ensure employees are not over-scheduled
    over_scheduled_employees = [
        employee["id"] for employee in employees if employee_hours(schedule, employee["id"]) > employee["maxh"]]
    evaluation_results["over_scheduled_employees"] = over_scheduled_employees

    # Ensure employees get their breaks
    breaks_enforced = enforce_breaks(
        [hour_schedule for _, day_schedule in schedule.items() for hour_schedule in day_schedule])
    evaluation_results["breaks_enforced"] = breaks_enforced

    return evaluation_results





##############################################################################################################
# Adjustment Phase

def manual_override(schedule, day, slot, employee_id, role):
    """
    Manually assign an employee to a specific slot and role on a given day.
    """
    for hour_schedule in schedule[day]:
        if hour_schedule["slot"] == slot:
            hour_schedule["employee_id"] = employee_id
            hour_schedule["role"] = role
            break
    return schedule


def find_replacement(schedule, day, slot, role, employees, positions):
    """
    Find a suitable replacement for a given slot and role on a specific day.
    """
    for employee in employees:
        if role in employee["roles"] and is_employee_available(employee, day, int(slot.split('-')[0].split(':')[0])):
            schedule = manual_override(
                schedule, day, slot, employee["id"], role)
            break
    return schedule


def rebalance_schedule(schedule, employees, hours, positions):
    """
    Rebalance the schedule after manual adjustments.
    """
    # ... (This function will be quite involved, considering all the constraints)
    return schedule


def correct_roles(schedule, employees, positions):
    """
    Ensure no employee is scheduled for a role they're not trained for.
    """
    for day, day_schedule in schedule.items():
        for hour_schedule in day_schedule:
            employee = next(
                e for e in employees if e["id"] == hour_schedule["employee_id"])
            if hour_schedule["role"] not in employee["roles"]:
                schedule = find_replacement(
                    schedule, day, hour_schedule["slot"], hour_schedule["role"], employees, positions)
    return schedule
