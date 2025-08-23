from typing import List, Tuple, Literal
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
import pandas as pd
from copy import deepcopy

# Now simulate the full process 
TOTAL_TIME = 150

# runner highspeed time 
HIGH_SPEED_TIME = 142.857
ACTION_DISTANCE = 10000

RUNNER_DEDUC = 0.24 # 0.16 # 0.22
PULLER_DEDUC = 0.24 + 0.25 # 0.16 + 0.25 # 0.47

RUNNER_DEDUC_2 = 0.24 # 0.16
PULLER_DEDUC_2 = 0.24 # 0.16

PULLER_NORMAL_ATTACK_DEDUC = 0.3

# Results = []

class Action():
    def __init__(self, action_name, time, par_action):
        self.action_name = action_name
        self.time = time
        self.par_action = par_action

    def __str__(self):
        return f"({self.action_name}, time: {self.time:.2f})"

class Character():
    def __init__(self, speed, left_distance):
        self.speed = speed
        self.left_distance = left_distance

class Runner(Character):
    def __init__(self, speed, left_distance, action_time, speed_up_sign):
        super().__init__(speed, left_distance)
        self.action_time = action_time
        self.speed_up_sign = speed_up_sign

class Puller(Character):
    def __init__(self, speed, left_distance, has_ultimate, has_2_ultimate):
        super().__init__(speed, left_distance)
        self.has_ultimate = has_ultimate
        self.has_2_ultimate = has_2_ultimate


def trace_action(action):
    path = [action]
    while action.par_action is not None:
        action = action.par_action
        path.append(action)
    
    return list(reversed(path))

def simulate(cur_time, runner, puller, last_action, Results):
    # Try both: no-ult first, then ult (if available)
    for use_ultimate in (0, 1):
        for use_2_ultimate in (0,1):
            # snapshot base state for this branch
            br_runner = deepcopy(runner)
            br_puller = deepcopy(puller)
            br_last_action = last_action

            if use_ultimate:
                if not br_puller.has_ultimate:
                    continue  # can't use it
                # apply ultimate as an action at current time
                br_last_action = Action("puller Ultimate", time=cur_time, par_action=br_last_action)
                br_runner.left_distance = max(0, br_runner.left_distance - RUNNER_DEDUC * ACTION_DISTANCE)
                br_puller.left_distance = max(0, br_puller.left_distance - PULLER_DEDUC * ACTION_DISTANCE)
                br_puller.has_ultimate = False
            
            if use_2_ultimate:
                if not br_puller.has_2_ultimate:
                    continue
                # apply ultimate as an action at current time
                br_last_action = Action("puller Ultimate 2", time=cur_time, par_action=br_last_action)
                br_runner.left_distance = max(0, br_runner.left_distance - RUNNER_DEDUC_2 * ACTION_DISTANCE)
                br_puller.left_distance = max(0, br_puller.left_distance - PULLER_DEDUC_2 * ACTION_DISTANCE)
                br_puller.has_2_ultimate = False

            # start from here
            # change the runner time if time passed the HIGH_SPEED_TIME
            if cur_time >= HIGH_SPEED_TIME:
                runner_time = br_runner.left_distance / (br_runner.speed - 60)
            else:
                runner_time_tmp = br_runner.left_distance / br_runner.speed
                if runner_time_tmp + cur_time > HIGH_SPEED_TIME:
                    dis_after_high_speed = br_runner.left_distance - br_runner.speed * (HIGH_SPEED_TIME - cur_time)

                    runner_time = dis_after_high_speed / (br_runner.speed - 60) + HIGH_SPEED_TIME - cur_time
                else:
                    runner_time = runner_time_tmp

            puller_time = br_puller.left_distance / br_puller.speed

            # choose next event time; explicit tie-break (puller first only if used ultimate)
            if runner_time < puller_time or (runner_time == puller_time and not use_ultimate):
                next_time = cur_time + runner_time
                if next_time > TOTAL_TIME:
                    Results.append({"Action Series": trace_action(br_last_action),
                                    "Num of Run": br_runner.action_time})
                    continue
                # runner acts
                new_action = Action("runner run", time=next_time, par_action=br_last_action)
                if br_runner.speed_up_sign:
                    new_runner = Runner(speed=br_runner.speed - 109 * 0.3,
                                        left_distance=ACTION_DISTANCE,
                                        action_time=br_runner.action_time + 1,
                                        speed_up_sign=False)
                else:
                    new_runner = Runner(speed=br_runner.speed,
                                        left_distance=ACTION_DISTANCE,
                                        action_time=br_runner.action_time + 1,
                                        speed_up_sign=False)
                new_puller = Puller(speed=br_puller.speed,
                                    left_distance=br_puller.left_distance - runner_time * br_puller.speed,
                                    has_ultimate=br_puller.has_ultimate,
                                    has_2_ultimate=br_puller.has_2_ultimate)
                simulate(next_time, new_runner, new_puller, new_action, Results)
            else:
                next_time = cur_time + puller_time
                if next_time > TOTAL_TIME:
                    Results.append({"Action Series": trace_action(br_last_action),
                                    "Num of Run": br_runner.action_time})
                    continue
                # puller acts: branch on skill vs normal attack (no mutation of branch roots)
                # if we just want to test the highest runner rounds, then we always pull
                # for use_skill in (1, 0):
                # if use_skill:
                new_action = Action("puller pull", time=next_time, par_action=br_last_action)
                new_puller = Puller(speed=br_puller.speed,
                                    left_distance=ACTION_DISTANCE,
                                    has_ultimate=br_puller.has_ultimate,
                                    has_2_ultimate=br_puller.has_2_ultimate)
                # simulate the speed up given by the puller
                new_runner = Runner(speed=br_runner.speed + 109 * 0.3,
                                    left_distance=0,
                                    action_time=br_runner.action_time,
                                    speed_up_sign=True)
                    # else:
                    #     new_action = Action("puller normal attack", time=next_time, par_action=br_last_action)
                    #     new_puller = Puller(speed=br_puller.speed,
                    #                         left_distance=ACTION_DISTANCE * (1 - PULLER_NORMAL_ATTACK_DEDUC),
                    #                         has_ultimate=br_puller.has_ultimate)
                    #     new_runner = Runner(speed=br_runner.speed,
                    #                         left_distance=br_runner.left_distance - puller_time * br_runner.speed,
                    #                         action_time=br_runner.action_time)
                simulate(next_time, new_runner, new_puller, new_action, Results)
    return Results


def cal_speed_turns(runner_speed, puller_speed):
    bronya = Puller(puller_speed, ACTION_DISTANCE, has_ultimate=True, has_2_ultimate=True)
    firefly = Runner(runner_speed, ACTION_DISTANCE, action_time=0, speed_up_sign=False)

    # print("I'm here")
    Results = []
    Results = simulate(cur_time=0, runner=firefly, puller=bronya, last_action=None, Results=Results)

    max_Result = Results[0]
    for i in range(1, len(Results)):
        r = Results[i]
        if r["Num of Run"] > max_Result["Num of Run"]:
            max_Result = r
    return max_Result
    # return Results


def write_results_to_file(Results, filename="results.txt"):
    with open(filename, 'w') as f:
        for r in Results:
            f.write("======= \n")
            f.write(f"Num of Runner run: {r['Num of Run']}\n")
            f.write("Action Series: ")
            for a in r['Action Series']:
                f.write(str(a))
            f.write("\n")  # Add newline after each result

# Testing with some speed that will be affected by the speed drop

# 139 speed: if always high speed, then it should take 143.88 for second run
# however, due to speed loss, it will have second act at 144.66
# max_Result = cal_speed_turns(runner_speed=139, puller_speed=1)
# write_results_to_file(max_Result)


# Usage:
# write_results_to_file(Results)
# Or specify a custom filename:

min_puller_speed = 99 + 10
max_puller_speed = 195 + 10

min_runner_speed = 169 + 11
max_runner_speed = 265 + 11

round_table = np.zeros((max_puller_speed - min_puller_speed + 1, max_runner_speed - min_runner_speed + 1))

for p_speed in range(min_puller_speed, max_puller_speed + 1):
    for r_speed in range(min_runner_speed, max_runner_speed + 1):
        max_Result = cal_speed_turns(runner_speed=r_speed, puller_speed=p_speed)
        t = max_Result['Num of Run']
        round_table[p_speed - min_puller_speed][r_speed - min_runner_speed] = t
# write_results_to_file(Results, "my_results.txt")

runner_speeds = np.arange(min_runner_speed, max_runner_speed + 1)
puller_speeds = np.arange(min_puller_speed, max_puller_speed + 1)
df = pd.DataFrame(round_table, index=puller_speeds, columns=runner_speeds)
df.index.name = 'Puller_speed'
df.columns.name = 'Runner_speed'

csv_filename = "round_table_with_full_time_other.csv"
df.to_csv(csv_filename)
print(f"Round table saved to {csv_filename}")

fig, ax = plt.subplots(figsize=(7, 5))

im = ax.imshow(
    round_table,
    origin='lower',          # smallest speeds at bottom/left
    aspect='auto',           # don’t force square pixels
    interpolation='nearest', # keep sharp grid cells
    extent=[                 # map array indices to actual speeds
        min_runner_speed - 0.5, max_runner_speed + 0.5,  # x (columns)
        min_puller_speed - 0.5, max_puller_speed + 0.5   # y (rows)
    ]
)

cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Turns (t)')

ax.set_xlabel('Runner speed')
ax.set_ylabel('Puller speed')
ax.set_title('Turns heatmap across speeds')

# Nice integer ticks every 5 or 10 units (tweak step to taste)
ax.set_xticks(np.arange(min_runner_speed, max_runner_speed + 1, 10))
ax.set_yticks(np.arange(min_puller_speed, max_puller_speed + 1, 10))

plt.tight_layout()
plt.savefig("with 2 wuwuwu other.png", dpi=300)
plt.show()
