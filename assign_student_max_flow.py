from ortools.graph.python import min_cost_flow
import numpy as np
import math
import itertools

def get_assignments(prefs, students_names, events_names):
    students_per_event = 2
    student_max_events = 3

    students = len(prefs)
    events = len(prefs[0])

    smcf = min_cost_flow.SimpleMinCostFlow()

    # define source node as node 0
    source_node = 0
    node_count = 1

    # add edges from source node to a node representing each student
    student_nodes = list(range(node_count, students + node_count))
    node_count += len(student_nodes)
    for i in range(len(student_nodes)):
        for i in range(student_max_events):
            smcf.add_arc_with_capacity_and_unit_cost(0, student_nodes[i], 1, 3**i)

    # add edges from student nodes to event nodes
    event_nodes = list(range(node_count, events + node_count))
    node_count += len(event_nodes)
    for i, student_pref_row in enumerate(prefs):
        for j, event_pref in enumerate(student_pref_row):
            smcf.add_arc_with_capacity_and_unit_cost(student_nodes[i], event_nodes[j], 1, event_pref)

    # add edges from each event node to the sink node
    sink_node = node_count
    node_count += 1
    for event_node in event_nodes:
        smcf.add_arc_with_capacity_and_unit_cost(event_node, sink_node, students_per_event, 0)

    # add flow volume to source and sink nodes
    smcf.set_node_supply(source_node, events * students_per_event)
    smcf.set_node_supply(sink_node, -events * students_per_event)

    # Find the minimum cost flow between node 0 and node 10.
    status = smcf.solve()

    student_name_by_node = {}
    for i, slot in enumerate(student_nodes):
        student_name_by_node[slot] = students_names[i]

    event_name_by_node = {}
    for i, event_node in enumerate(event_nodes):
        event_name_by_node[event_node] = events_names[i % len(events_names)]

    assignments = []
    if status == smcf.OPTIMAL:
        print('Total cost = ', smcf.optimal_cost())
        print()
        for arc in range(smcf.num_arcs()):
            # Can ignore arcs leading out of source or into sink.
            if smcf.tail(arc) != source_node and smcf.head(arc) != sink_node:

                # Arcs in the solution have a flow value of 1. Their start and end nodes
                # give an assignment of worker to task.
                if smcf.flow(arc) > 0:
                    student = student_name_by_node[smcf.tail(arc)]
                    event = event_name_by_node[smcf.head(arc)]
                    cost = int(math.log(smcf.unit_cost(arc), 2))
                    # print(f'{student:<25} assigned to event {event:30}.' +
                    #       f' Cost: {cost}')
                    assignments.append(f'{student:<25} assigned to event {event:30}.' +
                          f' Cost: {cost}')
    else:
        print(f'Status: {status}')
    return assignments, smcf.optimal_cost()

def main():
    # Data
    prefs = [
        [16,3,11,18,6,14,10,15,1,23,22,19,9,5,12,21,20,2,4,8,13,17,7],
        [9,8,14,23,19,13,16,21,18,11,15,22,10,17,20,12,7,3,6,4,2,1,5],
        [3,2,3,6,4,10,4,4,9,12,5,10,10,11,1,1,4,7,5,1,3,3,2],
        [3,14,17,20,23,19,18,2,5,6,13,22,15,13,14,13,21,8,7,11,1,4,9],
        [13,3,12,20,7,23,9,15,14,22,19,10,16,17,21,18,8,11,5,2,1,4,6],
        [20,17,12,20,21,11,22,11,18,21,12,15,14,9,13,17,23,12,22,15,6,17,14],
        [4,12,8,5,17,7,10,21,3,1,6,2,20,14,16,15,23,13,18,19,9,18,22],
        [20,4,12,9,10,11,7,13,8,21,14,2,6,5,3,22,1,15,17,19,18,16,23],
        [16,5,19,20,6,12,23,15,8,9,21,11,13,14,22,10,7,17,18,2,1,3,4],
        [19,3,22,14,4,9,8,10,12,8,5,2,16,17,7,6,1,20,13,23,15,11,21],
        [12,4,6,9,22,18,19,20,13,17,10,8,21,16,11,7,3,22,14,2,1,15,5],
        [15,3,18,19,22,10,13,14,1,21,20,9,12,11,17,6,2,23,16,4,5,7,8],
        [23,1,4,23,23,23,23,23,23,23,23,23,23,23,23,23,7,23,2,1,1,2,3],
        [10,1,23,23,23,23,23,23,23,23,1,23,23,23,23,1,23,23,23,23,22,22,21],
        [7,1,9,9,9,8,1,6,3,9,8,6,7,6,9,7,2,7,8,9,8,7,8],
        [23,20,15,1,6,16,12,2,3,4,11,17,5,13,21,19,18,9,9,22,14,10,8],
        [7,5,8,10,21,14,17,12,19,23,18,16,9,13,22,15,1,11,4,3,6,2,20],
        [16,18,20,14,18,15,20,19,14,8,13,1,18,15,20,18,16,12,18,19,15,16,20],
        [20,7,16,15,23,13,21,22,2,4,11,6,14,8,12,3,5,17,18,10,7,9,19],
        [8,1,19,3,15,11,13,7,2,4,16,9,5,14,12,9,10,18,20,17,23,22,21],
        [8,1,19,3,15,11,13,7,2,4,16,9,5,14,12,9,10,18,20,17,23,22,21],
        [6,13,10,18,11,20,15,9,12,23,22,14,5,16,21,19,2,20,4,1,7,3,8],
        [17,5,11,2,6,10,18,16,7,3,12,14,4,1,19,21,8,22,23,13,15,9,20],
        [15,14,5,1,6,21,16,8,4,2,12,11,19,22,13,20,3,23,7,10,18,9,17],
        [3,2,19,5,14,18,15,16,13,22,10,12,4,7,21,17,1,8,20,23,6,11,12],
        [5,6,3,4,1,21,11,23,9,7,18,16,14,13,19,20,17,2,22,8,15,12,10],
        [1,3,7,2,2,15,15,5,23,3,2,5,4,4,2,10,2,2,2,8,10,5,2],
        [4,18,16,23,15,20,17,11,9,12,19,14,3,21,8,22,1,2,13,5,13,7,10],
        [18,20,13,17,2,14,12,23,15,7,15,11,10,22,9,21,8,3,19,5,6,4,1],
        [2,1,17,8,9,16,12,22,10,4,5,7,20,14,11,19,13,3,21,15,23,6,18],
        [7,19,20,19,23,11,6,13,5,2,4,3,17,1,15,21,22,11,10,12,18,8,22],
        [10,4,10,11,12,11,3,5,9,23,21,6,2,1,14,15,17,16,8,20,17,21,22],
        [13,4,2,5,6,8,15,14,12,11,10,7,16,17,3,9,1,22,21,19,18,23,20],
        [7,22,18,19,12,6,11,13,4,1,2,3,20,5,10,17,8,23,21,16,15,9,14]
    ]
    students_names = ["Sally Peng",
                    "Tytus Hubbard",
                    "Hemadri Jadaun",
                    "Vamsikrishna Pondrati",
                    "Eli Thomsen",
                    "Ananya Rajesh",
                    "Pranav Puligundla",
                    "Macie Mably",
                    "Somya Suman",
                    "Krisha Dubey",
                    "Nikhil Tanksale",
                    "Ryan Wu",
                    "Daniel Tong",
                    "Latika Ramdular",
                    "Harnoor Kaur",
                    "Michael Yu",
                    "Mitchell (Mitch) Wentink",
                    "Ziyue Li",
                    "Abhinav  Rai",
                    "Eric Zhang",
                    "Eric Li",
                    "Holden Then",
                    "Christine Kim",
                    "Shiven Kharidehal",
                    "Olivia Hu",
                    "Brayden Ye",
                    "Thomas Zhao",
                    "Evan Haryn",
                    "Samuel Zou",
                    "Tingting Wang",
                    "Leo  Chen",
                    "Richard Chen",
                    "Sidd Sastry",
                    "Ananya  Tiwari"]
    events_names = ["Rocks and Minerals",
                    "Codebusters",
                    "Experimental Design",
                    "Fast Facts",
                    "Write It Do It",
                    "Dynamic Planet",
                    "Meteorology",
                    "Road Scholar",
                    "Solar System",
                    "Anatomy and Physiology",
                    "Bio Process Lab",
                    "Disease Detectives",
                    "Forestry",
                    "Green Generation",
                    "Can't Judge a Powder",
                    "Crave The Wave",
                    "Crime Busters",
                    "Sounds of Music",
                    "Storm the Castle",
                    "Bridge",
                    "Flight",
                    "Roller Coaster",
                    "Wheeled Vehicle"]

    # preference validation
    for i, row in enumerate(prefs):
        for j in range(1, 23):
            freq = row.count(j)
            if freq != 1:
                print(f"{students_names[i]:20} had {freq} events ranked {j}")
            if freq > 1:
                while prefs[i].count(j) > 1:
                    prefs[i][row.index(j)] = j + 1

    prefs = np.exp2(prefs).astype(np.uint).tolist()

    teamA = list(range(25, 34))
    teamB = list(range(14, 25))
    toAssign = list(range(14))
    best_loss = 9223372036854775807
    best_assignments = []
    i = 0
    for comb in itertools.combinations(toAssign, 8):
        teamA += list(comb)
        teamB += [i for i in toAssign if i not in list(comb)]
        assignments, loss = get_assignments([prefs[i] for i in teamA], [students_names[i] for i in teamA], events_names)
        assignments2, loss2 = get_assignments([prefs[i] for i in teamB], [students_names[i] for i in teamB], events_names)
        if best_loss > loss + loss2:
            best_assignments = [assignments, assignments2]
            best_loss = loss + loss2
        print(i)
        i += 1
    for assi in best_assignments:
        print("Team:")
        for row in assi:
            print(row)




if __name__ == '__main__':
    main()
