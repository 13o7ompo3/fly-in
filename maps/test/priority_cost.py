

def main(file_name: str, number_zones: int):
    output = "nb_drones: 1\n"
    output += "\n"
    output += "start_hub: start 0 0 [color=green]\n"
    output += "\n"
    for i in range(1, number_zones + 1):
        output += f"hub: waypoint{i} {i} 0 [color=blue]\n"
    output += "\n"
    for i in range(1, number_zones + 2):
        output += f"hub: priority{i} {i} 1 [color=yellow zone=priority]\n"
    output += "\n"
    output += f"end_hub: goal {number_zones + 1} 0 [color=red]\n"
    output += "\n"
    output += "connection: start-waypoint1\n"
    output += "connection: start-priority1\n"
    output += "\n"
    for i in range(1, number_zones):
        output += f"connection: waypoint{i}-waypoint{i + 1}\n"
    output += "\n"
    for i in range(1, number_zones + 1):
        output += f"connection: priority{i}-priority{i + 1}\n"
    output += "\n"
    output += f"connection: waypoint{number_zones}-goal\n"
    output += f"connection: priority{number_zones + 1}-goal\n"
    with open(file_name, "w") as f:
        f.write(output)


main("maps/test/priority_cost.txt", 11)
