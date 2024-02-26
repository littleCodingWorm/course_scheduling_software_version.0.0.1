import tkinter as tk
import json
import random


root = tk.Tk()
root.title("Data Input")
root.geometry("600x400")

# Function to process the data

def format_schedule(schedule):
  schedule.sort(key=lambda x: (x['day'], x['time'], x['room']))  # Sort by day, then time, then room
  schedule_str = "Schedule:\n"
  for item in schedule:
    schedule_str += f"Course: {item['course']}, Room: {item['room']}, Day: {item['day']}, Time: {item['time']}\n"
  return schedule_str

# Function to create an individual (a potential solution)
def create_individual(data):
    individual = []
    for course in data["courses"]:
        room = random.choice(data["rooms"])
        timeslot = random.choice(data["timeslots"])
        individual.append({
            "course": course["name"],
            "room": room["name"],
            "day": timeslot["day"],
            "time": timeslot["time"]
        })
    return individual
  
# Function to evaluate the fitness of an individual
def evaluate_individual(individual, data):
    fitness = 0
    for course in individual:
        course_data = next((c for c in data["courses"] if c["name"] == course["course"]), None)
        room_data = next((r for r in data["rooms"] if r["name"] == course["room"]), None)
        if course_data and room_data:
            difference = abs(course_data["students"] - room_data["capacity"])
            fitness += difference
            # Add more factors to the fitness function
            if course["time"] == "9:00":
                fitness += 1
            if course["room"] == "Room 101":
                fitness += 1
    return fitness

# Function to select parents for crossover using tournament selection
def select_parents(population, fitnesses, tournament_size):
    selected = random.sample(list(zip(population, fitnesses)), tournament_size)
    selected.sort(key=lambda x: x[1])  # Sort by fitness (lower is better)
    return selected[0][0], selected[1][0]  # Return the best two individuals

# Crossover function to combine two parents into a new child
def crossover(parent1, parent2):
    crossover_point = random.randint(1, len(parent1) - 1)
    child = parent1[:crossover_point] + parent2[crossover_point:]
    return child

# Mutation function to introduce variation
def mutate(individual, data, mutation_probability):
    if random.random() < mutation_probability:
        mutation_point = random.randint(0, len(individual) - 1)
        new_timeslot = random.choice(data["timeslots"])
        new_room = random.choice(data["rooms"])
        individual[mutation_point]["day"] = new_timeslot["day"]
        individual[mutation_point]["time"] = new_timeslot["time"]
        individual[mutation_point]["room"] = new_room["name"]
    return individual

# Main genetic algorithm function
def genetic_algorithm(data, population_size=10, generations=1000, mutation_probability=0.1, tournament_size=3, elitism_size=2):
    population = [create_individual(data) for _ in range(population_size)]
    for generation in range(generations):
        fitnesses = [evaluate_individual(ind, data) for ind in population]
        new_population = []
        # Add elitism
        elites = sorted(zip(population, fitnesses), key=lambda x: x[1])[:elitism_size]
        new_population.extend(ind for ind, fit in elites)
        while len(new_population) < population_size:
            parent1, parent2 = select_parents(population, fitnesses, tournament_size)
            child = crossover(parent1, parent2)
            child = mutate(child, data, mutation_probability)
            new_population.append(child)
        population = new_population
        print(f"Generation {generation + 1}: Best Fitness = {min(fitnesses)}")
    best_index = fitnesses.index(min(fitnesses))
    best_solution = population[best_index]
    return best_solution

# Run the genetic algorithm and print the final schedule

def process_data():
  try:
    # Get data from text widget
    input_data = text_widget.get("1.0", tk.END)
    # Convert string data to dictionary
    data = json.loads(input_data)
    final_schedule = genetic_algorithm(data)
    # Create a new window
    new_window = tk.Toplevel(root)
    new_window.title("Final Schedule")
    # Create a text widget and add it to the new window
    result_text = tk.Text(new_window, height=15, width=80)
    result_text.pack(padx=10, pady=10)
    # Insert the final schedule into the text widget
    result_text.insert(tk.END, str(format_schedule(final_schedule)))
  except json.JSONDecodeError as e:
    print("Invalid JSON data:", e)

        # final_schedule = genetic_algorithm(data)
        # print_schedule(final_schedule)
# Text widget for input
text_widget = tk.Text(root, height=15, width=80)
text_widget.pack(padx=10, pady=10)

# Button to process data
process_button = tk.Button(root, text="Process Data", command=process_data)
process_button.pack(pady=10)

root.mainloop()
