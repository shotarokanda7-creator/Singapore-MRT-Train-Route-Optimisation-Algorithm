import turtle

#Turtle Functions

def draw_title(title_string, size):              #Draw out the title of each
    screen = turtle.Screen()
    screen.clear()
    screen.setup(width=1200, height=800)
    screen.title("MRT Route Visualizer")
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    t.penup()
    t.goto(0,100)
    t.write(title_string, align="center", font=("Arial", size, "normal"))

def sub_text(title_string, size, x_pos, y_pos):  #Draw the smaller text
    screen = turtle.Screen()
    screen.setup(width=1200, height=800)
    screen.title("MRT Route Visualizer")
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    t.penup()
    t.goto(x_pos,y_pos)
    t.write(title_string, align="left", font=("Times New Roman", size, "normal"))

def draw_mrt_path(station_list, lines):         #Draw the MRT Path 
    if len(lines) == len(station_list) - 1:
        lines = [lines[0]] + lines
    elif len(lines) != len(station_list):
        print("Error: lines list should be same length as station_list.")      #Filter out incase not all station or lines are not stored
        return
    #Display setting/creating boundaries
    screen = turtle.Screen()
    screen.setup(width=1200, height=800)
    screen.title("MRT Route Visualizer")
    t = turtle.Turtle()
    t.speed(0)
    t.hideturtle()
    t.penup()
    screen_width = 1200
    screen_height = 800
    margin = 40
    vertical_step = 60

    total_stations = len(station_list)
    available_width = screen_width - 2 * margin
    spacing = available_width // max(total_stations+1, 1)

    # Initial position
    x = -screen_width // 2 + margin
    y = 0
    t.goto(x, y)
    t.setheading(0)  # face right

    # Draw first station
    t.dot(20, "Black")
    t.goto(x, y - 20)
    t.write(station_list[0], align="center", font=("Arial", 6, "normal"))
    t.goto(x, y)

    prev_line = lines[0]
    i = 1
    while i < len(station_list):
        curr_line = lines[i]
        # Move horizontally to the right
        x += spacing
        t.setheading(0)
        t.pendown()
        t.goto(x, y)
        t.penup()
        if curr_line != prev_line and prev_line != "INTERCHANGE":
            # Draw the vertical componemnts (Dotted line, stations and station name on the side)
            for j in range(10):
                y -= vertical_step // 10
                t.setheading(270)
                if j % 2 == 0:
                    t.pendown()
                    t.goto(x, y)
                    t.penup()
                else:
                    t.goto(x, y)
            t.dot(20,"Black")
            t.dot(12, line_colors[lines[i]])
            t.goto(x - 20, y)
            t.write(station_list[i], align="right", font=("Arial", 6, "normal"))
            t.goto(x, y)
            prev_line = curr_line
            i += 1
            continue

        # Draw station name above and below
        elif i % 2 == 0:
            t.goto(x, y - 20)
            t.write(station_list[i], align="center", font=("Arial", 6, "normal"))
        else:
            t.goto(x, y + 20)
            t.write(station_list[i], align="center", font=("Arial", 6, "normal"))
        #Draw Station dot with colors
        t.goto(x, y)
        t.dot(20,"Black")
        t.dot(12, line_colors[lines[i]])
        prev_line = curr_line
        i += 1

def draw_and_wait(path, line_seq, i, total_time):
    turtle.clearscreen()
    draw_mrt_path(path, line_seq)

    # Display route info on screen
    info = turtle.Turtle()
    info.hideturtle()
    info.penup()
    info.speed(0)
    info.goto(0, 250)
    info.write(f"Route #{i+1} — Estimated time: {round(total_time)} minutes",
               align="center", font=("Arial", 16, "bold"))

    # Wait for user click before continuing
    screen = turtle.Screen()
    screen.textinput("Next Route", "Click OK ")

#---------------------------------------------------------------------------------------------------
    
#---------------------------------------------------------------------------------------------------

#Functions to calculate

# Speeds of each line km/h
line_speeds = {
    'North-South': 41,
    'East-West': 43,
    'Circle': 36,
    'Thomson-East Coast': 40,
    'North East': 34,
    'Downtown': 38}

# Read MRT data from text file
def parse_mrt_file(filename):
    graph = {}                      # station: list of (connected_station, distance, line)
    times = {}                      # (station1, station2): (first_train_time, last_train_time)
    lines = {}                      # line_name: list of stations in order
    station_name_to_codes = {}      # station_name: list of station codes

    infile = open(filename, "r")           #Open file
    for line in infile:
        parts = line.strip().split(';')
        if len(parts) < 8 or '<->' not in parts[1]:
            continue

        num, pair, line_name, dist, fwd_first, fwd_last, bwd_first, bwd_last = parts
        dist = float(dist)
        station1_full, station2_full = pair.split('<->')            #Extract the full name of all stations
        station1_full = station1_full.strip()
        station2_full = station2_full.strip()
        #Remove the code to deal with overlapping stations (eg. EW24 Jurong East and NS1 Jurong East
        name1 = " ".join(station1_full.split()[1:])
        name2 = " ".join(station2_full.split()[1:])

        if name1 not in station_name_to_codes:                      #If first one just creates an dict
            station_name_to_codes[name1] = []
        if station1_full not in station_name_to_codes[name1]:       #If already found appends the full station name eg: Jurong East: EW24 Jurong East
            station_name_to_codes[name1].append(station1_full)

        if name2 not in station_name_to_codes:
            station_name_to_codes[name2] = []
        if station2_full not in station_name_to_codes[name2]:
            station_name_to_codes[name2].append(station2_full)

        # Create the list graph and times
        for s1, s2, first, last in [(station1_full, station2_full, fwd_first, fwd_last),            #s1 eg: TE27 Marine Terrace
                                    (station2_full, station1_full, bwd_first, bwd_last)]:
    
            if s1 not in graph:
                graph[s1] = []                                          #If station not in graph create an dict
            graph[s1].append((s2, dist, line_name))                     #Store Full_station_name: (full_name_connected_station, distance, line) into graph
            times[(s1, s2)] = (int(first), int(last))                   #Store (station1, station2): (first_train_time, last_train_time) into times

        # Add to lines
        if line_name not in lines:                                      #if line_name (eg. Circle) not in lines create an dict
            lines[line_name] = []
        if station1_full not in lines[line_name]:                       #Add full_station_name 1 and 2 into line list (eg. Circle: CC2 Promenade)
            lines[line_name].append(station1_full)
        if station2_full not in lines[line_name]:
            lines[line_name].append(station2_full)

    #DEAL with interchange station. Append 0 distance and "Interchange" to graph
    for name in station_name_to_codes:
        codes = station_name_to_codes[name]
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                c1 = codes[i]
                c2 = codes[j]
                if c1 not in graph:
                    graph[c1] = []
                graph[c1].append((c2, 0.0, 'INTERCHANGE'))
                if c2 not in graph:
                    graph[c2] = []
                graph[c2].append((c1, 0.0, 'INTERCHANGE'))

    return graph, times, lines                                           #return 3 dict

# Task 1: List all stations on a line
def list_stations(line_name, lines):                                     #Intake user input (name of line) and the dictionary lines
    list_station = []
    if line_name in lines:
        print(f"Stations on {line_name} Line:")
        for station in lines[line_name]:
            list_station.append(station)                                 #Append all the stations in the line into list_station 
            print(f"- {station}")                                        #Iterate print all
        return list_station                                              #Return the list of stations
            
    else:
        print("Line not found.")
        return "e"                                                       #Return "e" for error

# Task 2: Find most efficient route
def find_fastest_route(start, end, graph):       #intake start station, end station and dict graph
    # queue = (total_time_minutes, current_station, path_so_far, line_sequence, distances)
    queue = [(0, start, [start], [], [])]
    visited = {}

    while len(queue) > 0:                                                   
        min_index = 0                                                       # Find the state with the least total_time
        for i in range(1, len(queue)):
            if queue[i][0] < queue[min_index][0]:                           #If total_time for queue[i] <queue[min_index] replace min_index, setting fastest time
                min_index = i                                               

        # Pop the route with the lowest time
        total_time, current, path, line_seq, dist_seq = queue[min_index]
        queue.pop(min_index)

        # Skip if already visited this station with a faster route
        if current in visited and visited[current] <= total_time:   #Prevent a loop. If A-->B, prevents B-->A
            continue
        visited[current] = total_time

        if current == end:
            return path, dist_seq, line_seq, total_time

        # Check for all potential routes by branching out at each connection
        for i in range(len(graph.get(current, []))):              #Branches out to all connecting stations 
            neighbor, dist, line = graph[current][i]              

            if line == 'INTERCHANGE':                           #Interchange time is considered to be 3
                travel_time = 3
            else:
                speed = line_speeds[line]                       #Recall from line_speed dict to find speed
                travel_time = (dist / speed) * 60               #Time = dist/speed

            queue.append((                                      #Add all to queue
                total_time + travel_time,
                neighbor,
                path + [neighbor],
                line_seq + [line],
                dist_seq + [dist]
            ))

    return None, [], [], float('inf')

# Task 4: Check train availability (Created this code before the error in mrt.txt was found, to overcome the error) 

def find_top_n_routes(start, end, graph, max_paths=5):                                 #Find top 5 fastest routes for the case the fastest route fails
    queue = [(0, start, [start], [], [])]  # (time, station, path, lines, distances)
    completed_routes = []
    visited = {}
    iterations = 0

    while queue and len(completed_routes) < max_paths and iterations<30000:
        iterations += 1
        # Pick route with smallest total time
        min_index = 0                                                           # Find the index with the least total_time
        for i in range(1, len(queue)):                                          #If total_time for queue[i] <queue[min_index] replace min_index, setting fastest time
            if queue[i][0] < queue[min_index][0]:
                min_index = i

        total_time, current, path, line_seq, dist_seq = queue.pop(min_index)    # Pop the route with the lowest time

        if current == end:                                                      #When reach destination, terminate
            completed_routes.append((path, dist_seq, line_seq, total_time))
            continue

        # Allow different paths to the same station
        state_signature = (current, tuple(path))
        if state_signature in visited:
            continue
        visited[state_signature] = True

        for neighbor, dist, line in graph.get(current, []):      #retrive list of neightbours if exists and an empty list if DNE
            if neighbor in path:
                continue  # interchange <-> interchange loop

            if line == 'INTERCHANGE':
                travel_time = 3                                 #Interchange time is considered to be 3min
            else:
                speed = line_speeds[line]                       #Recall from line_speed dict to find speed
                travel_time = (dist / speed) * 60               #Time = dist/speed

            queue.append((                                      #Add all to queue
                total_time + travel_time,
                neighbor,
                path + [neighbor],
                line_seq + [line],
                dist_seq + [dist]
            ))
    if iterations ==1999:
        print("Potentially in a loop or lack of machine power. Try with other stations ")


    return completed_routes



def find_any_valid_route_at_time(start, end, current_time, graph, times):             #Examine whether one of the 5 alternative paths is available at the time
    # Get up to 5 alternative paths (fastest first)
    routes = find_top_n_routes(start, end, graph, max_paths=5)                        #Get the list of routes
    for path, dist_list, line_list, time in routes:                                   #Go through each route and check return, path,dist_list, line_list, time, msg if exist
        ok, msg = is_train_running(current_time, path, times, dist_list, line_list)
        if ok:
            return path, dist_list, line_list, time, msg

    return None, [], [], 0, "No available route found within last train timings."     #Return none and empty lists if DNE

def is_train_running(start_time, path, times, distances, line_seq):                   #Examine whether the train path is valid during a time
    current_time = int(start_time)                                                    #Input start_time, path, dictionary times, distances, line_seq 

    for i in range(len(path) - 1):
        s1 = path[i]                                                                  #Station 1
        s2 = path[i + 1]                                                              #Station 2
        line = line_seq[i]                                                            #line going between station 1,2 
        dist = distances[i]                                                           #Distance between station 1,2

        if line == 'INTERCHANGE':                                                     #if interchange += 3 min 
            current_time = add_minutes_to_time(current_time, 3)
            if current_time >= 2400:
                current_time -= 2400
            continue

        elif (s1, s2) in times:                                                       #Extract first and last train data between stations 1 and 2
            first, last = times[(s1, s2)]

            # Adjust last if it's "2400"
            if last < first:
                last += 2400

            # If current_time < first and first > 1200, assume we're checking after midnight (e.g., 0020)
            adjusted_time = current_time
            if adjusted_time < first and first > 1200:
                adjusted_time += 2400

            # Check if adjusted time is within operating hours                        #if time is earlier than first and later than last train it is unavailable
            if adjusted_time < first or adjusted_time > last:
                return False, f"No train running from {s1} to {s2} at {current_time:04d}."

        else:
            return False, f"No timing data found for {s1} to {s2}."

        # Add travel time for next segment
        speed = line_speeds[line]                                                      #Recall from line_speed dict to find speed
        travel_minutes = (dist / speed) * 60                                           #Time = dist/speed
        current_time = add_minutes_to_time(current_time, int(round(travel_minutes)))   #Update current time to move on the list

        # Convert to 24-hour format again
        if current_time >= 2400:
            current_time -= 2400

    return True, f"You will arrive at {path[-1]} by {current_time:04d}, before the last train cutoff."    #Return True (train is operating)

#Used when adding minutes to time (eg. 1230+45 = 1315)
def add_minutes_to_time(current_time_hhmm, minutes_to_add):
    # Extract hours and minutes from HHMM format
    hours = current_time_hhmm // 100
    minutes = current_time_hhmm % 100

    # Convert to total minutes
    total_minutes = hours * 60 + minutes + minutes_to_add

    # Convert back to HHMM format
    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60

    return new_hours * 100 + new_minutes

#Task 5: List all the train lines running on the given train station
def all_lines_per_station(graph, station_input):                                    #Input dictionary graph, users input station
    station_input_lower = station_input.lower()                                     #lowercase station name
    station_match_list =[]                                                          #Matching station
    lines_found = []                                                                #lines running in the station
    for station in graph:                                                           #Iterate over all station
        if station_input_lower in station.lower():                                  #If input_station match append to match_list
            station_match_list.append(station)
    if not station_match_list:
        print("No matches. Station DNE")
    for station_name in station_match_list:
        for neighbor, dist, line in graph[station_name]:                            #Extract line in the matched stations(station_match_list)
            if line != 'INTERCHANGE' and line not in lines_found:
                lines_found.append(line)                                            #Append to lines_found
    if lines_found:
        return station_input, lines_found                                           #Return list of lines found
    else:
        return station_input, []
            
#Task 6 Find most efficient route and tell which colour to colour they should transit. For young kids or tourist, who may struggle to read
line_colors = {
                'North-South': 'Red',
                'East-West': 'Green',
                'Circle': 'Orange',
                'Thomson-East Coast': 'Brown',
                'North East': 'Purple',
                'Downtown': 'Blue',
                'INTERCHANGE': 'Yellow'
            }

def describe_line_transitions(path, line_list):                                     #Input path list and line_list
    if not line_list:
        return
    y_pos = -280                                                                    #Initalise the y position of text
    prev_line = None                                                                #Initialise previous line data
    for i in range(len(line_list)):                                                 #Iterate over all index of stations 
        current_line = line_list[i]
        station = path[i]
        if current_line == 'INTERCHANGE':
            continue

        if current_line != prev_line:                                                                       #If previous != current line, use dictionary of line to colors to get the colour of line
            color = line_colors.get(current_line, "Unknown color")
            if prev_line is None:
                print(f"Start on the {color} Line ({current_line})")
                sub_text(f"Start on the {color} Line ({current_line})", 20, -500, y_pos)                    #Display starting line color
            else:
                b = " ".join(station.split()[1:])
                print(f"Get off at {b}. Change to the {color} Line ({current_line})")
                sub_text(f"Get off at {b}. Change to the {color} Line ({current_line})", 20, -500, y_pos)   #Displaying transiting lines color
            y_pos -= 25                                                                                     #Move down by 25 

        prev_line = current_line        #Store the current line when iterating on to the next

#Task 7 Find when you need to depart the first station to reach the destination
#Deal with situation eg: Error: 1340-50 = 1290 Fix: 1340-50=1250 
def subtract_minutes_from_time(current_time_hhmm, minutes_to_subtract):                                     #Input current time and minutes to subtract it 
    hours = current_time_hhmm // 100
    minutes = current_time_hhmm % 100
    total_minutes = hours * 60 + minutes - minutes_to_subtract

    if total_minutes < 0:
        total_minutes += 24 * 60  

    new_hours = (total_minutes // 60) % 24
    new_minutes = total_minutes % 60

    return new_hours * 100 + new_minutes                                                                    #Return the new time after being subtracted


#Task 7: Find Departure time given desired arrival time"
def find_departure_time_for_arrival(start, end, target_arrival_hhmm, graph, times):                         #Input start station, end station, targeted arrival_time, dictionary of graph and times 
    path, dist_list, line_list, total_time = find_fastest_route(start, end, graph)                          #Find the fastest route using function

    if not path:                                                                                            #If path DNE
        return None, "No route found."
    
    current_time = int(target_arrival_hhmm)                                                                 #Work backwards from the arrival time
    for i in reversed(range(len(line_list))):
        line = line_list[i]
        dist = dist_list[i]
        if line == 'INTERCHANGE':                                                                           #If Interchange station take 3 min
            travel_minutes = 3
        else:
            speed = line_speeds[line]                                                                           #Speed recall from line_speed dict to find speed
            travel_minutes = int(round((dist / speed) * 60))                                                    #Time = dist/speed
        current_time = subtract_minutes_from_time(current_time, travel_minutes)                             #Subtract travel_time from current_time

    departure_time = current_time                                                                           #Departure time = current_time as it is backtracked

    # Now check if this time works
    ok, msg = is_train_running(departure_time, path, times, dist_list, line_list)

    return departure_time, msg                                                                              #Return what time to leave and check whether it is in operation

# Task 8: Estimate total travel time using linespeeds 
def estimate_time(distance_list, line_list):                                                                #Input distance list and line list
    total_time = 0                                                                                          #Initalise the total time taken
    for i in range(len(distance_list)):
        dist = distance_list[i]
        line = line_list[i]
        if line == 'INTERCHANGE':                                                                           #If Interchange station take 3 min
            total_time += 3
            continue
        speed = line_speeds[line]                                                                           #Speed recall from line_speed dict to find speed
        total_time += (dist / speed) * 60                                                                   #Time = dist/speed
    return round(total_time)                                                                                #Return the total time taken for the journey

#Dealing with inputs
     #Easier inputs ( (e.g., CC1 Dhoby Ghaut --> Dhoby)
def abbrev(start_input, end_input, graph):                                                                  #Input the start and end station name (not full) and dict graph
    def extract_base_name(full_name):                                                                       #Remove the code (e.g."NS1") and return station name
        return " ".join(full_name.split()[1:]).strip().lower()

    def resolve_station(input_text):                                                                        #Extract the full name from the users input
        matches = []                                                                                        #Initialise the input list of matches
        base_name_to_full_station = {}                                                                      #Initialise the base_name list

        for station in graph:
            if input_text.lower() in station.lower():                                                       #If the input matches a full_name append to matches list
                base_name = extract_base_name(station)
                if base_name not in base_name_to_full_station:
                    base_name_to_full_station[base_name] = station
                matches.append(station)

        base_names = list(base_name_to_full_station.keys())

        if len(matches) == 0:
            turtle.clearscreen()
            print(f"❌ No matches found for '{input_text}'.")
            sub_text(f"❌ No matches found for '{input_text}'", 20, -300, 70)
            screen = turtle.Screen()
            screen.textinput("Next Route", "Click OK ")
            return "e"                                                                                      #Return "e" to catch error of no search hits
        elif len(base_names) > 1:
            turtle.clearscreen()
            print(f"⚠️ Input '{input_text}' is ambiguous. Matches multiple distinct stations:")
            sub_text(f"⚠️ Input '{input_text}' is ambiguous. Matches multiple distinct stations:", 20, -300, 70)
            y_pos = -205
            for name in base_names:
                print(f" - {name.title()}")                                                                 #If multiple search hits prints all the hits
                sub_text(f" - {name.title()}", 20, -300, y_pos)
                y_pos-=25
            screen = turtle.Screen()
            screen.textinput("Next Route", "Click OK ")
            return "e"                                                                                      #Return "e" to catch error of multiple search hits
        else:
            return base_name_to_full_station[base_names[0]]                                                 # Pick one matching full code

    # Try to resolve both stations
    start = resolve_station(start_input)
    end = resolve_station(end_input)

    return start, end                                                                                       #return the full station name


    #Easier inputs(eg. North-South --> South) (task 1)

def abb_line(in_line):                                                                                      #input name of line
    in_line_lower = in_line.lower()
    lines =["Circle", "North East", "Thomson-East Coast", "East-West","Downtown","North-South"]             #List of lines in MRT
    return_list = []
    for line in lines:
        if in_line_lower in line.lower():
            return_list.append(line)
    if len(return_list) == 1:
        return return_list[0]                                                                               #Return full name of line if only 1 hit
    else:
        return "e"                                                                                          #Return "e" to catch errors. eg input DNE or too ambiguous



#--------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
# Main menu
def main():
    while True:
        filename = input("Enter input file name: ")                                                         #Ask for users data input file until a valid file is found
        try:
            open(filename, "r")                                                                             #Open and read the file 
            break
        except FileNotFoundError:
            print("File not found. Try again")
    graph, times, lines = parse_mrt_file(filename)                                                          #Process the data into lists,tuples and dictionary
    while True:                                                                                             #Ask for users input 
        print("\nMenu:")
        print("1. List all stations on a line")
        print("2. Find best route between two stations")
        print("3. Determine Availability")
        print("4. List all interchange stations")
        print("5. List all the lines running given station")
        print("6. Step by Step Instructions of path")
        print("7. Find Departure time given desired arrival time")
        print("8. Find distance and estimate time between two stations")
        print("9. Find the maximum (Up to 5) possible routes")
        print("10. Exit")
        choice = input("Choose an option (1-9): ")

        if choice == '1':
            line = turtle.textinput("MRT Line Input", "Enter line name (e.g., Circle):")
            full_name_line = abb_line(line)                                                                         #Find full name of line 
            if full_name_line == "e":
                draw_title(f"INPUT ERROR. RETURN BACK", 50)                                                         #Return to selection screen if line is not found
                continue
            a = list_stations(full_name_line, lines)                                                                #List of stations in the given line
            line1_list =[]                                                                                          #Initialise the list of lines                                                  
            if a == "e":
                draw_title(f"ERROR. RETURN BACK", 50)                                                               #Return to selection screen if line list is not found
                continue
            else:
                for i in range(len(a)):                                                                             #For len(a) append line to list of lines eg. [Circle, Circle, Circle] 
                    line1_list.append(full_name_line)
                draw_title(f"List all stations on {full_name_line} line", 50)                                              #Print title to turtle and draw path
                draw_mrt_path(a,line1_list)

        elif choice == '2':
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g., CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. EW24 Jurong East or Jurong): ").strip()
            start, end = abbrev(start1,end1,graph)
            if start == "e" or end == "e" or start == end:
                draw_title(f"INPUT ERROR. RETURN BACK", 50)                                                         #Return to selection screen if station is not found
                continue
            draw_title(f"Find best route between {start} and {end}",30)                                             #Print title to turtle
            path, dist, line_seq, total_time = find_fastest_route(start, end, graph)                                #Find fastest route's (path, dist, line_seq, total_time)
            if path:                                                                                                #If path exists draw on turtle the path
                print("\nBest Route:")
                print(" -> ".join(path))
                tot_dis = 0
                for d in dist:
                    tot_dis += float(d)
                draw_mrt_path(path, line_seq)
                continue
            else:
                print("Route not found.")
                continue

        elif choice == '3':
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g. CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. EW24 Jurong East or Jurong): ").strip()
            time = turtle.textinput("MRT Line Input","Enter journey start time (HHMM): ").strip()
            start, end = abbrev(start1,end1,graph)
            if start == "e" or end == "e" or float(time)<0 or float(time)>2400 or start==end:                                    #Return to selection screen if station is not found or input time is out of range
                draw_title(f"INPUT ERROR. RETURN BACK", 50)
                continue
            # First, try the fastest route
            path, dist_list, line_list, total_time = find_fastest_route(start, end, graph)                          #Find fastest route's (path, dist, line_seq, total_time)

            if path:
                draw_title(f"Availability from {start} to {end} at {time}",30)                                      #Print title to turtle
                ok, msg = is_train_running(time, path, times, dist_list, line_list)
                if ok:                                                                                              #If fastest route is found draw path and print availability message
                    print("Fastest route is available:")
                    sub_text(f"Fastest route is available:", 20, -300, 70)
                    sub_text(f"{msg}",20,-300,40)
                    print(" -> ".join(path))
                    print(f"Estimated time: {round(total_time)} minutes")
                    print(msg)
                    draw_mrt_path(path, line_list)
                    continue
                else:                                                                                                          #If fastest route is not available search for alternative path
                    print("Fastest route is NOT available.")
                    print(msg)
                    print("Searching for alternate valid routes...")

                    alt_path, alt_dist, alt_lines, alt_time, alt_msg = find_any_valid_route_at_time(start, end, time, graph, times)
                    if alt_path:                                                                                                #Check if alternative path is available
                        print("Alternate route found:")
                        sub_text(f"Alternate route is available:", 20, -300, 70)
                        sub_text(f"{alt_msg}",20,-300,40)
                        print(" -> ".join(alt_path))
                        print(f"Estimated time: {round(alt_time)} minutes")
                        print(alt_msg)
                        draw_mrt_path(alt_path, alt_lines)                                                                      #If alternative route is found draw path and print availability message                                                                       
                        continue
                    else:                                                                                                       #Print route not found if no trains running
                        print("No alternate route available at this time.")
                        sub_text(f"No alternate route available at this time.",20,0,40)
                        continue
            else:
                print("No route found.")
                sub_text(f"No route found",20,0,40)
                continue
        elif choice == '4':
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g., CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. EW24 Jurong East or Jurong): ").strip()
            time = turtle.textinput("MRT Line Input","Enter journey start time (HHMM): ").strip()
            start, end = abbrev(start1,end1,graph)
            if start == "e" or end == "e" or float(time)<0 or float(time)>2400 or start==end:                                         #Return to selection screen if station is not found or input time is out of range
                draw_title(f"INPUT ERROR. RETURN BACK", 50)
                continue
            path, dist_list, line_list, total_time = find_fastest_route(start, end, graph)                              #Find fastest route's (path, dist, line_seq, total_time)
            det_inter = []

            ok, msg = is_train_running(time, path, times, dist_list, line_list)
            if ok:                                                                                                      #If fastest route is found draw path and print estimate time and all interchange
                draw_title(f"Interchange stations from {start} to {end} at {time}",30)
                print("\nBest Route:")
                print(" -> ".join(path))
                print("Estimated time:", round(total_time), "minutes")
                draw_mrt_path(path, line_list)
                sub_text(f"Estimated time: {round(total_time)} minutes",20,- 500,-160)

                # Detect interchange stations
                for i in range(len(line_list)):                                                                         #If station is interchange station, append to det_inter
                    if line_list[i] == "INTERCHANGE":
                        det_inter.append(path[i + 1])

                if det_inter:                                                                                           #If there are interchange stations
                    y_pos = -205                                                                                        #Initialise the y-cord 
                    print("Interchange Stations:")
                    sub_text(f"Interchange stations:", 20, -500, -180)                                                  
                    for station in det_inter:
                        print(f"- {station}")
                        sub_text(f"- {station}",20,- 500,y_pos)                                                         #Print on turtle all the interchange stations
                        y_pos -= 25                                                                                     #Move y-cord everytime after printing each station
                    continue
                else:
                    print("No interchanges needed.")                                                                    #If no interchange station is found, then print "NO interchange needed"
                    sub_text(f"No Interchanges Needed",20,- 500,-180)
                    continue

            else:
                print("Fastest route is not available. Trying alternatives...")
                alt_path, alt_dist, alt_lines, alt_time, alt_msg = find_any_valid_route_at_time(start, end, time, graph, times)     #If the fastest route is not available, find alternative routes

                if alt_path:                                                                                            #If alternative routes exists, draw the mrt_path and their interchange stations
                    print("Alternate route found:")
                    print(" -> ".join(alt_path))
                    print("Estimated time:", round(alt_time), "minutes")
                    draw_mrt_path(alt_path, alt_line)
                    sub_text("Estimated time:", round(alt_time), "minutes",20,- 500,-160)
                    for i in range(len(alt_lines)):
                        if alt_lines[i] == "INTERCHANGE":
                            det_inter.append(alt_path[i + 1])                                                           #If station is an interchange append to det_inter

                    if det_inter:
                        y_pos = -205                                                                                    #Initialise the y-cord 
                        print("Interchange Stations:")
                        for station in det_inter:
                            print(f"- {station}")
                            sub_text(f"- {station}",20,- 500,y_pos)
                            y_pos -= 25
                        continue
                    else:                                                                                               #If no interchange is required print,"No Interchange"
                        print("No interchanges needed.")
                        sub_text(f"No Interchanges Needed",20,- 500,-180)
                        continue
                else:                                                                                                   #If alt_path is not available at the time, print turtle "unavailable"
                    print("No alternate route available at this time.")
                    sub_text(f"No alternate route available at this time",20,- 500,-180)
                    continue
        elif choice == '5':
            start1 = turtle.textinput("MRT Line Input","Enter station name or part of it (e.g., 'Jurong', 'Dhoby'): ").strip()
            end1 = "Jurong"
            print("Requirements: The input names must all be unqiue. For example, DO NOT enter 'Marina' as it can detect Marina Bay and Marina South Pier")
            start, end = abbrev(start1,end1,graph)
            if start == "e":
                draw_title(f"INPUT ERROR. RETURN BACK", 50)                                                             #Return to selection screen if station is not found
                continue
            b = " ".join(start.split()[1:])
            station_name, liness = all_lines_per_station(graph, b)                                                      #Function to determine all the lines passing through station
            print(f"Station: {station_name}")
            if liness:                                                                                                  #If MRT lines exist on the station, print list of stations
                draw_title(f"Train lines passing through {b}",50)
                print("Lines running through this station:")
                sub_text(f"Lines running through this station:", 40,-380,5)
                y_pos = -35
                for line in liness:
                    print(f"  - {line}")
                    sub_text(f"  - {line}", 40, -350, y_pos)
                    screen = turtle.Screen()
                    screen.setup(width=1200, height=800)
                    screen.title("MRT Route Visualizer")
                    t = turtle.Turtle()
                    t.speed(0)
                    t.hideturtle()
                    t.penup()
                    t.goto(-370,y_pos+20)
                    t.dot(30, line_colors[line])
                    y_pos -= 40
                continue
            else:                                                                                                       #Else, MRT lines ot found, print("No MRT lines found")
                print("No MRT lines found")
                sub_text("No MRT lines found", 40,-350,5)
                continue
        elif choice == '6':
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g. CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. NS13 Yishun or Yishun): ").strip()
            start, end = abbrev(start1,end1,graph)
            if start == "e" or end =="e" or start ==end:
                draw_title(f"ERROR. RETURN BACK", 50)                                                                   #Return to selection screen if station is not found
                continue
            path, dist, line_seq, total_time = find_fastest_route(start, end, graph)                                    #Find fastest route's (path, dist, line_seq, total_time)

            if path:                                                                                                    #If path exists, print title, path and describe_line_transition
                draw_title(f"Tourist Mode: Route from {start} to {end}",30)
                draw_mrt_path(path, line_seq)
                print("\nBest Route for Tourists:")
                print(" -> ".join(path))
                sub_text(f"Total time: {round(total_time)} minutes", 20, -500, -230)
                print(f"Total time: {round(total_time)} minutes")
                print("Route with line colors:")
                print(f"At {start}", end = " ")
                sub_text(f"From {start}", 20, -500, -255)
                describe_line_transitions(path, line_seq)
                continue
            else:                                                                                                       #Else, path not found, print("No Route Found")
                print("No route found.")
                sub_text("No route found", 20, -500, -255)
                continue
        elif choice == '7':
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g. CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. NS13 Yishun or Yishun): ").strip()
            arrival_time = turtle.textinput("MRT Line Input","Enter your desired arrival time (HHMM): ").strip()
            start, end = abbrev(start1,end1,graph)
            path, dist, line_seq, total_time = find_fastest_route(start, end, graph)
            if start == "e" or end =="e" or float(arrival_time)<0 or float(arrival_time)>2400 or start==end:
                draw_title(f"INPUT ERROR. RETURN BACK", 50)                                                             #Return to selection screen if station is not found or input time is out of range
                continue
            
            depart_time, message = find_departure_time_for_arrival(start, end, arrival_time, graph, times)              #Find departure time and check whether train is available
            if depart_time:                                                                                             #If departure time exists, print title, path and depart time
                draw_title(f"Find depature time from {start} to {end}",30)
                draw_mrt_path(path, line_seq)
                print(f"You should depart at {depart_time:04d} to arrive by {arrival_time}.")
                sub_text(f"You should depart at {depart_time:04d} to arrive by {arrival_time}.", 20, -500, -255)
                print(message)
                if "No train running" in message:                                                                       #If train unavailable return back to main selection 
                    sub_text(f"However, {message} Find a different timing", 20,-500,-280)
                    continue
                else:
                    sub_text(f"{message}", 20,-500,-280)                                                                #Print the departure time if available
                    continue
            else:
                print(message)
                sub_text(message, 20,-500,-255)
                continue
        elif choice == '8':
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g., CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. NS13 Yishun or Yishun): ").strip()
            start, end = abbrev(start1,end1,graph)
            if start == "e" or end =="e" or start==end:
                draw_title(f"INPUT ERROR. RETURN BACK", 50)                                                         #Return to selection screen if station is not found
                continue
            path, dist, line_seq, total_time = find_fastest_route(start, end, graph)                                #Find fastest route's (path, dist, line_seq, total_time)
            if path:                                                                                                #If route exist, print title, path
                draw_title(f"Distance and estimate time from {start} to {end}",30)
                draw_mrt_path(path, line_seq)
                tot_dis = 0                                                                                         #Initialise the total distance 
                for d in dist:                                                                                      #Sum all of the distance of the route
                    tot_dis += float(d)
                print(f"Total distance: {tot_dis:.1f} km")
                sub_text(f"Total distance: {tot_dis:.1f} km", 20,-500,-255)
                # Calculate segment distances by adding each distance to list
                distances = []
                for i in range(len(path) - 1):
                    for j in range(len(graph[path[i]])):
                        neighbor, d, line = graph[path[i]][j]
                        if neighbor == path[i + 1]:                                                                 
                            distances.append(d)
                            continue

                est_time = estimate_time(distances, line_seq)                                                       #Estimate time taken for the journey
                print(f"Estimated time: {est_time} minutes")
                sub_text(f"Estimated time: {est_time} minutes", 20,-500,-280)
                continue
            else:                                                                                                   #If path not found then print("Route not Found")
                print("Route not found.")
                sub_text("Route not found.", 20,-500,-255)
                continue
        elif choice == '9':                                                                                         
            start1 = turtle.textinput("MRT Line Input","Enter start station (e.g., CC1 Dhoby Ghaut or Dhoby): ").strip()
            end1 = turtle.textinput("MRT Line Input","Enter destination station (e.g. EW24 Jurong East or Jurong): ").strip()
            start, end = abbrev(start1,end1,graph)
            if start == "e" or end == "e" or start==end:                                                                          #Return to selection screen if station is not found or input time is out of range
                draw_title(f"INPUT ERROR. RETURN BACK", 50)
                continue

            routes = find_top_n_routes(start, end, graph)                                                           #Find 5 Alternative routes
            
            if not routes:
                print("No routes found.")
                draw_title(f"INPUT ERROR. RETURN BACK", 50)
                sub_text("Route not found.", 20,-500,-255)
                screen = turtle.Screen()
                screen.textinput("Next Route", "Click OK ")
                continue
            else:
                for i, (path, dist_seq, line_seq, total_time) in enumerate(routes):
                    draw_and_wait(path, line_seq, i, total_time)

                print("All routes displayed.")
                sub_text("All routes displayed.", 20,-500,-255)
                screen = turtle.Screen()
                screen.textinput("DONE", "Click OK ")
                continue
        elif choice == '10':                                                                                        #Break from the program                                                                                        
            break
            
        else:                                                                                                       #Invalid input, return back to main selection                                                                                                  
            print("Invalid option. Please try again.")
            draw_title(f"INPUT ERROR. RETURN BACK", 50)
            continue
            
main()
