import heapq
from collections import deque
import tkinter as tk
from tkinter import messagebox

class State:
    def __init__(self, circles, parent=None, action=None, cost=0):
        self.circles = circles  # A, B, C, D, E (center)
        self.parent = parent
        self.action = action
        self.cost = cost

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.circles == other.circles

    def __hash__(self):
        return hash(tuple(tuple(circle) for circle in self.circles))

    def is_goal(self):
        return all(coin % 2 == 1 for circle in [self.circles[0], self.circles[2]] for coin in circle) and \
               all(coin % 2 == 0 for circle in [self.circles[1], self.circles[3]] for coin in circle) and \
               not self.circles[4]  # Center circle (E) should be empty

    def get_possible_actions(self):
        actions = []
        for i, from_circle in enumerate(self.circles):
            if from_circle:
                for j, to_circle in enumerate(self.circles):
                    if i != j and self.is_valid_move(from_circle[0], to_circle, j == 4):
                        actions.append((i, j))
        return actions

    def is_valid_move(self, coin, to_circle, is_center):
        if is_center:
            return True  # Always allow moving to the center
        if not to_circle:
            return True
        return coin < to_circle[0] and (coin % 2 == to_circle[0] % 2)

    def apply_action(self, action):
        new_circles = [circle[:] for circle in self.circles]
        from_circle, to_circle = action
        coin = new_circles[from_circle].pop(0)  # Remove from the top (beginning of the list)
        new_circles[to_circle].insert(0, coin)  # Insert at the top (beginning of the list)
        return State(new_circles, self, action, self.cost + 1)

    def __str__(self):
        circle_names = ['A', 'B', 'C', 'D', 'E']
        return '\n'.join(f"{circle_names[i]}: {circle}" for i, circle in enumerate(self.circles))

def create_initial_state(n_coins):
    return State([[], [], [], [], list(range(1, n_coins + 1))])  # Coins in ascending order in center

def depth_first_search(initial_state):
    stack = [(initial_state, [])]
    visited = set()

    while stack:
        state, path = stack.pop()
        if state.is_goal():
            return path

        if state not in visited:
            visited.add(state)
            for action in state.get_possible_actions():
                new_state = state.apply_action(action)
                new_path = path + [action]
                stack.append((new_state, new_path))

    return None

def breadth_first_search(initial_state):
    queue = deque([(initial_state, [])])
    visited = set()

    while queue:
        state, path = queue.popleft()
        if state.is_goal():
            return path

        if state not in visited:
            visited.add(state)
            for action in state.get_possible_actions():
                new_state = state.apply_action(action)
                new_path = path + [action]
                queue.append((new_state, new_path))

    return None

def greedy_best_first_search(initial_state, heuristic):
    pq = [(heuristic(initial_state), initial_state, [])]
    visited = set()

    while pq:
        _, state, path = heapq.heappop(pq)
        if state.is_goal():
            return path

        if state not in visited:
            visited.add(state)
            for action in state.get_possible_actions():
                new_state = state.apply_action(action)
                new_path = path + [action]
                heapq.heappush(pq, (heuristic(new_state), new_state, new_path))

    return None

def a_star_search(initial_state, heuristic):
    pq = [(0 + heuristic(initial_state), 0, initial_state, [])]
    visited = set()

    while pq:
        _, cost, state, path = heapq.heappop(pq)
        if state.is_goal():
            return path

        if state not in visited:
            visited.add(state)
            for action in state.get_possible_actions():
                new_state = state.apply_action(action)
                new_cost = cost + 1
                new_path = path + [action]
                heapq.heappush(pq, (new_cost + heuristic(new_state), new_cost, new_state, new_path))

    return None

def heuristic(state):
    misplaced = 0
    for i, circle in enumerate(state.circles):
        if i in [0, 2]:  # Odd circles (A and C)
            misplaced += sum(1 for coin in circle if coin % 2 == 0)
        elif i in [1, 3]:  # Even circles (B and D)
            misplaced += sum(1 for coin in circle if coin % 2 == 1)
        else:  # Center circle (E)
            misplaced += len(circle)
    return misplaced

def print_solution(initial_state, solution):
    result = ["Initial state:"]
    result.append(str(initial_state))
    result.append("\nSolution path:")
    current_state = initial_state
    for i, move in enumerate(solution, 1):
        from_circle, to_circle = move
        circle_names = ['A', 'B', 'C', 'D', 'E']
        moved_coin = current_state.circles[from_circle][0]  # Get the top coin (smallest)
        result.append(f"\nMove {i}: Coin {moved_coin} from {circle_names[from_circle]} to {circle_names[to_circle]}")
        current_state = current_state.apply_action(move)
        result.append(str(current_state))
    result.append("\nGoal state reached!")
    return '\n'.join(result)

# GUI Implementation
def run_search():
    n_coins = int(coin_var.get())
    algorithm_choice = algo_var.get()
    initial_state = create_initial_state(n_coins)

    if algorithm_choice == "Depth-First Search":
        solution = depth_first_search(initial_state)
    elif algorithm_choice == "Breadth-First Search":
        solution = breadth_first_search(initial_state)
    elif algorithm_choice == "Greedy Best-First Search":
        solution = greedy_best_first_search(initial_state, heuristic)
    else:
        solution = a_star_search(initial_state, heuristic)

    if solution:
        result_text = print_solution(initial_state, solution)
        messagebox.showinfo("Solution Found", result_text)
    else:
        messagebox.showinfo("No Solution", "No solution found.")

# Main GUI setup
root = tk.Tk()
root.title("Coin Sorting Problem Solver")

tk.Label(root, text="Select number of coins:").pack()
coin_var = tk.StringVar(value="4")
coin_options = ["4", "6", "8", "10"]
coin_menu = tk.OptionMenu(root, coin_var, *coin_options)
coin_menu.pack()

tk.Label(root, text="Select search algorithm:").pack()
algo_var = tk.StringVar(value="Depth-First Search")
algo_options = ["Depth-First Search", "Breadth-First Search", "Greedy Best-First Search", "A* Search"]
algo_menu = tk.OptionMenu(root, algo_var, *algo_options)
algo_menu.pack()

run_button = tk.Button(root, text="Run Search", command=run_search)
run_button.pack()

root.mainloop()
