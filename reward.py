import csv

class AverageReward():
    def __init__(self, initial_measurement, num_measurements = 3, threshold = 0.01):
        #must be THRESHOLD % higher than average of last rewards to be counted as improvement-- vice versa for a worse result (negative reward)
        #this should help against small measurement errors that don't actually affect performance
        self.THRESHOLD = threshold
        self.last_measurements = [initial_measurement] * num_measurements

#-1 to 1 reward function based on rolling window of past x results
class BinaryAverageReward(AverageReward):
    def __init__(self, initial_measurement, num_measurements = 3, threshold = 0.01):
        super().__init__(initial_measurement, num_measurements = num_measurements, threshold = threshold)

    def get_reward(self, new_measurement):
        avg = sum(self.last_measurements) / len(self.last_measurements)
        self.last_measurements.pop(0)
        self.last_measurements.append(new_measurement)
        if new_measurement > self.THRESHOLD*avg + avg:
            return 1
        if new_measurement < -self.THRESHOLD*avg + avg:
            return -1
        return 0

#reward function based on rolling window of past x results, but uses the difference between measurements as the reward
class ContinuousAverageReward(AverageReward):
    def __init__(self, initial_measurement, num_measurements = 3, threshold=0.01):
        super().__init__(initial_measurement, num_measurements = num_measurements, threshold = threshold)

    def get_reward(self, new_measurement):
        avg = sum(self.last_measurements) / len(self.last_measurements)
        self.last_measurements.pop(0)
        self.last_measurements.append(new_measurement)
        if new_measurement > self.THRESHOLD*avg + avg:
            return new_measurement - avg
        if new_measurement < -self.THRESHOLD*avg + avg:
            return new_measurement - avg
        return 0

#reward function that uses difference from average of precomputed baseline
#I still don't think it's fair to base the decision *only* on historical data (otherwise why are we doing RL), but the general idea could be combined with the former 2 reward functions
#see below for an example of how
class VsBaselineReward():
    def __init__(self, baseline_file = "8000.csv", window = 100, threshold = 0.01):
        self.THRESHOLD = threshold
        with open(baseline_file) as fin:
            reader = csv.reader(fin)
            self.baseline_measurements = [float(row[1]) for row in reader]
        self.window = window
        self.num_steps = 0

    def get_reward(self, new_measurement):
        min_idx = max(0, self.num_steps - self.window)
        max_idx = self.num_steps + 1
        array_subset = self.baseline_measurements[min_idx:max_idx]
        avg = sum(array_subset) / len(array_subset)
        self.num_steps += 1
        if new_measurement > self.THRESHOLD*avg + avg:
            return new_measurement - avg
        if new_measurement < -self.THRESHOLD*avg + avg:
            return new_measurement - avg
        return 0

#reward function that uses difference from last x measurements, with option to reset w.r.t. baseline measurements if needed
#can use same structure for binary version
class ContinuousVsBaselineReward(ContinuousAverageReward):
    #call this function every new episode, for example
    def recompute_starting_measurement(self, init = False):
        min_idx = max(0, self.num_steps - self.window)
        max_idx = self.num_steps + 1
        array_subset = self.baseline_measurements[min_idx:max_idx]
        avg = sum(array_subset) / len(array_subset)
        if init:
            self.last_measurements = [avg] * len(self.last_measurements)
        else:
            return avg

    def __init__(self, baseline_file = "8000.csv", window = 100, num_measurements = 3, threshold = 0.01):
        with open(baseline_file) as fin:
            reader = csv.reader(fin)
            self.baseline_measurements = [float(row[1]) for row in reader]
        self.window = window
        self.num_steps = 0

        super().__init__(self.recompute_starting_measurement(), num_measurements = num_measurements, threshold = threshold)

    def get_reward(self, new_measurement):
        avg = sum(self.last_measurements) / len(self.last_measurements)
        self.last_measurements.pop(0)
        self.last_measurements.append(new_measurement)
        self.num_steps += 1
        if new_measurement > self.THRESHOLD*avg + avg:
            return new_measurement - avg
        if new_measurement < -self.THRESHOLD*avg + avg:
            return new_measurement - avg
        return 0



#USAGE:
if __name__ == "__main__":
    #binary
    b = BinaryAverageReward(150) #150 is a fake initial measurement, you would want to run the benchmark to get this number
    for i in [150, 140, 190, 200, 156]: #these are fake throughput measurements, it should be obtained through the benchmark connector
        print(b.get_reward(i))

    print("====")

    #...and continuous
    c = ContinuousAverageReward(150) #150 is a fake initial measurement, you would want to run the benchmark to get this number
    for i in [150, 140, 190, 200, 156]: #these are fake throughput measurements, it should be obtained through the benchmark connector
        print(c.get_reward(i))

    print("====")

    v = VsBaselineReward()
    for i in [150, 140, 190, 200, 156]: #these are fake throughput measurements, it should be obtained through the benchmark connector
        print(v.get_reward(i))

    print("====")

    v = ContinuousVsBaselineReward()
    for i in [150, 140, 190, 200, 156]: #these are fake throughput measurements, it should be obtained through the benchmark connector

        #call this on every episode restart, should be called with argument True (False just returns what the measurements *should* be but does not set them itself)
        v.recompute_starting_measurement(True)
        print(v.get_reward(i))
