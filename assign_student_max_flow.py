import random

from ortools.graph.python import min_cost_flow
import numpy as np
import math
import itertools

students_per_event = 2
student_max_events = 4
two_exp = False
multiple_event_penalty = 1
prefs_multiplier = 1

def get_assignments(prefs, students_names, events_names, events_groups):
    students = len(prefs)
    events = len(prefs[0])

    smcf = min_cost_flow.SimpleMinCostFlow()

    # define source node as node 0
    source_node = 0
    node_count = 1

    # add edges from source node to a node representing each student, with first/second/third slot nodes in between to penalize assigning multiple events to any one student
    student_nodes = list(range(node_count, students + node_count))
    node_count += len(student_nodes)
    slot_nodes = []
    slot_nodes_by_student = {}
    for i in range(len(student_nodes)):
        # smcf.add_arc_with_capacity_and_unit_cost(0, student_nodes[i], student_max_events, 0)
        slot_nodes_for_student = list(range(node_count, student_max_events + node_count))
        node_count += student_max_events
        slot_nodes += slot_nodes_for_student
        slot_nodes_by_student[i] = slot_nodes_for_student
        for j in range(student_max_events):
            smcf.add_arc_with_capacity_and_unit_cost(0, slot_nodes_for_student[j], 1, 3 ** j * multiple_event_penalty)
            smcf.add_arc_with_capacity_and_unit_cost(slot_nodes_for_student[j], student_nodes[i], 1, 0)

    # add edges from each student node to a set of concurrent event groups
    concurrent_event_groups_by_student_node = {}
    concurrent_event_group_to_student_node = {}
    for student_node in student_nodes:
        concurrent_event_groups_for_student = list(range(node_count, len(events_groups) + node_count))
        node_count += len(events_groups)
        concurrent_event_groups_by_student_node[student_node] = concurrent_event_groups_for_student
        for group in concurrent_event_groups_for_student:
            smcf.add_arc_with_capacity_and_unit_cost(student_node, group, 1, 0)
            concurrent_event_group_to_student_node[group] = student_node

    # add edges from each student's set of concurrent event groups to every event, with corresponding pref cost
    event_nodes = list(range(node_count, events + node_count))
    node_count += len(event_nodes)
    event_name_by_node = {}
    event_node_by_name = {}
    event_idx_by_name = {}
    for i, event_node in enumerate(event_nodes):
        event_name_by_node[event_node] = events_names[i % len(events_names)]
        event_node_by_name[events_names[i % len(events_names)]] = event_node
        event_idx_by_name[events_names[i % len(events_names)]] = i
    for student_idx, student_node in enumerate(student_nodes):
        for group_idx, group_node in enumerate(concurrent_event_groups_by_student_node[student_node]):
            for event in events_groups[group_idx]:
                event_node = event_node_by_name[event]
                cost = prefs[student_idx][event_idx_by_name[event]]
                smcf.add_arc_with_capacity_and_unit_cost(group_node, event_node, 1, cost)

    # # add edges from student nodes to event nodes
    # event_nodes = list(range(node_count, events + node_count))
    # node_count += len(event_nodes)
    # for i, student_pref_row in enumerate(prefs):
    #     for j, event_pref in enumerate(student_pref_row):
    #         smcf.add_arc_with_capacity_and_unit_cost(student_nodes[i], event_nodes[j], 1, event_pref)

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

    assignments = []
    if status == smcf.OPTIMAL:
        print('Total cost = ', smcf.optimal_cost())
        print()
        for arc in range(smcf.num_arcs()):
            # Can ignore arcs leading out of source or into sink. Also between student nodes and concurrent event group nodes
            if smcf.tail(arc) != source_node and smcf.head(arc) != sink_node and smcf.tail(arc) not in student_nodes and smcf.head(arc) not in student_nodes:
                if smcf.flow(arc) == 1:
                    student = student_name_by_node[concurrent_event_group_to_student_node[smcf.tail(arc)]]
                    event = event_name_by_node[smcf.head(arc)]
                    cost = int(math.log(smcf.unit_cost(arc) / prefs_multiplier, 2)) if two_exp else int(smcf.unit_cost(arc) / prefs_multiplier)
                    # print(f'{student:<25} assigned to event {event:30}.' +
                    #       f' Cost: {cost}')
                    assignments.append(f'{student:<25} assigned to event {event:30}.' +
                          f' Cost: {cost}')
                elif smcf.flow(arc) > 1:
                    print("ERROR STATE")
                    # student = student_name_by_node[concurrent_event_group_to_student_node[smcf.tail(arc)]]
                    # event = event_name_by_node[smcf.head(arc)]
                    # cost = int(math.log(smcf.unit_cost(arc), 2))
                    # print(f'{student:<25} assigned to event {event:30}.' +
                    #       f' Cost: {cost}')
                    # assignments.append(f'{student:<25} assigned to event {event:30}.' +
                    #       f' Cost: {cost}')
                    # print("FLOW: ", smcf.flow(arc))
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

    events_groups = [
        ["Road Scholar", "Disease Detectives", "Codebusters"] + ["Anatomy and Physiology", "Solar System", "Sounds of Music"],
        ["Experimental Design", "Forestry", "Crave The Wave"],
        ["Can't Judge a Powder", "Dynamic Planet", "Fast Facts"],
        ["Bio Process Lab", "Crime Busters", "Rocks and Minerals"],
        ["Green Generation", "Meteorology", "Write It Do It"],
        ["Storm the Castle"],
        ["Bridge"],
        ["Flight"],
        ["Roller Coaster"],
        ["Wheeled Vehicle"]
    ]

    # preference validation
    for i, row in enumerate(prefs):
        for j in range(1, 23):
            freq = row.count(j)
            if freq != 1:
                print(f"{students_names[i]:20} had {freq} events ranked {j}")
            if freq > 1:
                while prefs[i].count(j) > 1:
                    prefs[i][row.index(j)] = j + 1

    if two_exp:
        prefs = (np.exp2(prefs).astype(np.uint) * prefs_multiplier).tolist()

    teamA = list(range(25, 34))
    teamB = list(range(14, 25))
    toAssign = list(range(14))
    best_loss = 9223372036854775807
    best_assignments = []
    i = 0
    # for comb in random.sample(list(itertools.combinations(toAssign, 8)), 1):
    for comb in list(itertools.combinations(toAssign, 8)):
        a = teamA + list(comb)
        b = teamB + [i for i in toAssign if i not in list(comb)]
        print(a)
        print(b)
        assignments, loss = get_assignments([prefs[i] for i in a], [students_names[i] for i in a], events_names, events_groups)
        assignments2, loss2 = get_assignments([prefs[i] for i in b], [students_names[i] for i in b], events_names, events_groups)
        if best_loss > loss + loss2:
            best_assignments = [assignments, assignments2]
            best_loss = loss + loss2
        print(i)
        i += 1
    for i, assi in enumerate(best_assignments):
        print(best_loss)
        print(f"\n\nTeam {i}:")
        for row in assi:
            print(row)




if __name__ == '__main__':
    main()
