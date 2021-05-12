import gym
from stable_baselines3 import A2C, DQN, DDPG, PPO, SAC, TD3
# from postgres_env import DiscreteEnv, ContinuousEnv, SimpleEnv
# from envs import SimpleEnv, SimpleContinuousEnv
# from envs.postgres_env import PostgresEnv
from parameter import Parameter
import numpy as np
from stable_baselines3.common.env_checker import check_env
from datetime import datetime
from gym.envs.registration import register
from stable_baselines3.common.env_util import make_vec_env

# register envs
register(
    id='SimpleDiscrete-v0',
    entry_point='test_envs:SimpleDiscreteEnv'
) 
register(
    id='SimpleContinuous-v0',
    entry_point='test_envs:SimpleContinuousEnv'
) 
register(
    id='Postgres-v0',
    entry_point='postgres_env:PostgresEnv'
)

# initialize parameters
random_page_cost = Parameter("random_page_cost", 1, 4, 4, 4)
io_concurrency = Parameter("effective_io_concurrency", 1, 1000, 1, 1)
parameters = [random_page_cost, io_concurrency]

# create the env with the parameters
env = make_vec_env('Postgres-v0', env_kwargs=parameters)
check_env(env)

# initialize model
# model = DDPG("MlpPolicy", env, verbose=1)
# model = DQN("MlpPolicy", env, verbose=1)
model = PPO("MlpPolicy", env, verbose=1)

# learn
start = datetime.now()
model.learn(total_timesteps=10)
end = datetime.now()
print(f'training time: {end-start}')

obs = env.reset()
actions = []
states = []
all_rewards = []

# run the trained model
for i in range(10):
  # print(f'step {i}')
  action, _states = model.predict(obs)
  obs, rewards, done, info = env.step(action)
  env.render()

  actions.append(round(action[0],2))
  states.append(round(env.state[0],2))
  all_rewards.append(rewards)

print(actions)
print(states)
# print(all_rewards)
print(np.mean(all_rewards))