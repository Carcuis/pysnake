import argparse
import os
import random
import time
from collections import deque

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pygame
import torch
import torch.nn.functional as F
from tqdm import tqdm

from board import Text
from event import EventManager
from game import Game
from settings import Global
from snake import Direction
from util import Util


class ReplayBuffer:
    def __init__(self, capacity: int):
        self.buffer: deque[tuple] = deque(maxlen=capacity)

    def add(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        transitions = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*transitions)
        return np.array(state), action, reward, np.array(next_state), done

    @property
    def size(self):
        return len(self.buffer)


class Qnet(torch.nn.Module):
    def __init__(self, state_dim, hidden_dim, action_dim):
        super(Qnet, self).__init__()
        self.fc1 = torch.nn.Linear(state_dim, hidden_dim)
        self.fc2 = torch.nn.Linear(hidden_dim, action_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        return self.fc2(x)


class DQN:
    """ DQN algorithm """

    def __init__(self, state_dim: int, hidden_dim: int, action_dim: int,
                 learning_rate: float, gamma: float, epsilon: float, target_update: int, device: torch.device):
        self.action_dim: int = action_dim
        self.q_net: Qnet = Qnet(state_dim, hidden_dim, self.action_dim).to(device)  # Q网络
        self.target_q_net: Qnet = Qnet(state_dim, hidden_dim, self.action_dim).to(device)
        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=learning_rate)
        self.gamma: float = gamma  # 折扣因子
        self.epsilon: float = epsilon  # epsilon-贪婪策略
        self.target_update: int = target_update  # 目标网络更新频率
        self.count: int = 0  # 计数器,记录更新次数
        self.device: torch.device = device

    def save(self) -> None:
        """ save the model """
        model_save_path = "weights/model.pt"

        # only save state_dict
        # torch.save({
        #     "model_state_dict": self.q_net.state_dict(),
        #     "optimizer_state_dict": self.optimizer.state_dict(),
        # }, model_save_path)

        # save the whole model
        torch.save(self.q_net, model_save_path)

    def load(self, path: str, device: torch.device) -> None:
        """ load the model """
        model_save_path = path

        # only load state_dict
        # checkpoint = torch.load(model_save_path)
        # self.q_net.load_state_dict(checkpoint['model_state_dict'])
        # self.q_net.eval()
        # self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        # load the whole model
        self.q_net = torch.load(model_save_path, map_location=device)

    def take_action(self, state: npt.NDArray) -> int:  # epsilon-贪婪策略采取动作
        """ take action according to epsilon-greedy policy using Q-network """
        if np.random.random() < self.epsilon:
            action = np.random.randint(self.action_dim)
        else:
            state = torch.from_numpy(state).float().unsqueeze(0).to(self.device)
            action = self.q_net(state).argmax().item()
        return action

    def update(self, transition_dict: dict) -> None:
        states = torch.tensor(transition_dict["states"], dtype=torch.float).to(self.device)
        actions = torch.tensor(transition_dict["actions"]).view(-1, 1).to(self.device)
        rewards = torch.tensor(transition_dict["rewards"], dtype=torch.float).view(-1, 1).to(self.device)
        next_states = torch.tensor(transition_dict["next_states"], dtype=torch.float).to(self.device)
        dones = torch.tensor(transition_dict["dones"], dtype=torch.float).view(-1, 1).to(self.device)
        q_values = self.q_net(states).gather(1, actions)
        max_next_q_values = self.target_q_net(next_states).max(1)[0].view(-1, 1)  # 下个状态的最大Q值
        q_targets = rewards + self.gamma * max_next_q_values * (1 - dones)  # TD误差目标
        dqn_loss = torch.mean(F.mse_loss(q_values, q_targets))  # 均方误差损失函数
        self.optimizer.zero_grad()  # PyTorch中默认梯度会累积,这里需要显式将梯度置为0
        dqn_loss.backward()  # 反向传播更新参数
        self.optimizer.step()

        if self.count % self.target_update == 0:
            self.target_q_net.load_state_dict(self.q_net.state_dict())  # 更新目标网络
        self.count += 1


def moving_average(a, window_size: int):
    cumulative_sum = np.cumsum(np.insert(a, 0, 0))
    middle = (cumulative_sum[window_size:] - cumulative_sum[:-window_size]) / window_size
    r = np.arange(1, window_size - 1, 2)
    begin = np.cumsum(a[:window_size - 1])[::2] / r
    end = (np.cumsum(a[:-window_size:-1])[::2] / r)[::-1]
    return np.concatenate((begin, middle, end))


def get_surroundings(game: Game, level: int) -> npt.NDArray:
    """
    get the surroundings of the snake head
    :param game: the game object
    :param level: the number of layers surrounding the snake head
    :return: 1-dim flattened numpy array
    """
    surroundings = np.zeros((level * 2 + 1, level * 2 + 1))
    for i in range(level * 2 + 1):
        for j in range(level * 2 + 1):
            if i == j == level:
                surroundings[i][j] = 0
                continue
            surroundings[i][j] = game.grid.get_value(game.snake.x[0] - level + i, game.snake.y[0] - level + j)
    return surroundings.flatten()


def get_game_state(game: Game) -> npt.NDArray:
    game_state = np.array((
        game.snake.x[0] - game.food_manager.apple.x[0],
        game.snake.y[0] - game.food_manager.apple.y[0],
        game.snake.hungry.hungry_step_count,
        max(200 - game.snake.hungry.hungry_step_count, 100),
        game.snake.x[0],
        game.snake.y[0],
        game.snake.direction.value
    ))
    return np.concatenate((game_state, get_surroundings(game, 4)))


def update_game_surface(game: Game, reward: int, max_score: int, time_start: float) -> None:
    EventManager.get_event()
    game.set_base_color(Global.BACK_GROUND_COLOR)
    total_time = time.time() - time_start
    hours = int(total_time / 3600)
    minutes = int((total_time % 3600) // 60)
    seconds = int((total_time % 3600) % 60)
    game.board.add(
        Text(f"FPS: {round(game.clock.get_fps())}", pygame.Color("white"), "left_top", alpha=255),
        Text(f"reward: {round(reward, 2)}", pygame.Color("white"), position=(0.2, 0, "left_top"), alpha=255),
        Text(f"score: {game.get_score()}", pygame.Color("springgreen"), position=(0.75, 0), alpha=255),
        Text(f"max: {max_score}", pygame.Color("springgreen"), position=(0.5, 0), alpha=255),
        Text(f"len: {game.snake.length}", pygame.Color("springgreen"), "right_top", alpha=255),
        Text(f"level: {game.level}", pygame.Color("chartreuse"), "middle_bottom", alpha=255),
        Text(f"HSC: {game.snake.hungry.hungry_step_count}", pygame.Color("white"), position=(0.25, 1), alpha=255),
        Text("{:02d}: {:02d}: {:02d}".format(hours, minutes, seconds), pygame.Color("white"),
             position=(0.7, 1), alpha=255)
    )
    game.draw_surface()
    Util.update_screen()
    game.clock.tick()


def get_direction_from_action(action: int) -> Direction:
    # action(3): 0 -> nothing; 1 -> turn left; 2 -> turn right
    # if action == 0:
    #     pass
    # elif action == 1:
    #     if direction.value <= 0:
    #         direction = Direction(3)
    #     else:
    #         direction = Direction(direction.value - 1)
    # elif action == 2:
    #     direction = Direction((direction.value + 1) % 4)
    # else:
    #     raise ValueError(f"{action}")

    # action(4): 0 -> Up; 1 -> Right; 2 -> Down; 3 -> Left
    direction = Direction(action)
    return direction


def rename_model(max_score: int) -> None:
    """ rename the model to a time format """
    time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    original_model_path = "weights/model.pt"
    model_save_path = f"weights/{time_str}_max_{max_score}.pt"
    if not os.path.exists("weights/model.pt"):
        raise FileNotFoundError("model.pt not found in ./weights/")
    os.rename(original_model_path, model_save_path)
    print(f"model renamed to {model_save_path}")


def get_game_reward(game: Game, collide_with_food: bool, collide_with_body: bool, collide_with_wall: bool) -> int:
    # if game.move_distance < 20:
    #     reward += 1 / max(1, game.move_distance)
    #     reward += 1
    # elif reward > -80:
    #     reward -= 1
    # else:
    #     reward -= 1
    # reward = 1 / max(1, game.move_distance)
    # reward = max(- game.snake.hungry.hungry_step_count, - 50)
    # reward = - game.snake.hungry.hungry_step_count
    # reward = 1
    reward = (20 - abs(game.snake.x[0] - game.food_manager.apple.x[0]) -
              abs(game.snake.y[0] - game.food_manager.apple.y[0]) - game.snake.hungry.hungry_step_count)

    if collide_with_food:
        # reward = 100 * game.eat_food_count
        # reward = 100
        reward = max(200 - game.snake.hungry.hungry_step_count, 100)
    if collide_with_body:
        reward = -200
    if collide_with_wall:
        reward = -200

    return reward


def train():
    lr = 2e-3
    num_episodes = 100
    gamma = 0.98
    epsilon = 0.01
    target_update = 10
    buffer_size = 100000
    minimal_size = 100
    batch_size = 64
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    # init game
    game = Game()

    # random.seed(0)
    # np.random.seed(0)
    # torch.manual_seed(0)
    replay_buffer = ReplayBuffer(buffer_size)
    state_dim = get_game_state(game).size
    hidden_dim = 64
    action_dim = 4
    agent = DQN(state_dim, hidden_dim, action_dim, lr, gamma, epsilon, target_update, device)

    max_score = 0
    return_list = []
    time_start = time.time()
    it = 0
    while True:
        it += 1
        try:
            with tqdm(total=num_episodes, desc=f"Iteration {it}") as pbar:
                for i_episode in range(num_episodes):
                    state = get_game_state(game)
                    done = False
                    while not done:
                        action = agent.take_action(state)
                        direction = get_direction_from_action(action)
                        alive, _, collide_with_food, collide_with_body, collide_with_wall = \
                            game.play(direction=direction, full_speed=True, teleport=Global.TELEPORT)
                        reward = get_game_reward(game, collide_with_food, collide_with_body, collide_with_wall)
                        next_state = get_game_state(game)
                        done = not alive
                        replay_buffer.add(state, action, reward, next_state, done)
                        state = next_state
                        if replay_buffer.size > minimal_size:
                            # 当buffer数据的数量超过一定值后,才进行Q网络训练
                            b_s, b_a, b_r, b_ns, b_d = replay_buffer.sample(batch_size)
                            transition_dict = {
                                "states": b_s,
                                "actions": b_a,
                                "next_states": b_ns,
                                "rewards": b_r,
                                "dones": b_d
                            }
                            agent.update(transition_dict)
                        update_game_surface(game, reward, max_score, time_start)

                    result = game.get_score()
                    if result > max_score:
                        agent.save()
                        max_score = result
                    game.reset_game()
                    return_list.append(result)
                    if (i_episode + 1) % 10 == 0:
                        pbar.set_postfix({
                            "episode": "%d" % (num_episodes * it + i_episode + 1),
                            "return": "%.3f" % np.mean(return_list[-10:])
                        })
                    pbar.update(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt")
            break

    print(f"max score: {max_score}")
    rename_model(max_score)
    plot_result(return_list)


def plot_result(return_list: list[float | int]):
    episodes_list = list(range(len(return_list)))
    plt.plot(episodes_list, return_list)
    plt.xlabel("Episodes")
    plt.ylabel("Returns")
    plt.title("DQN on pysnake")
    plt.show()

    mv_return = moving_average(return_list, 9)
    plt.plot(episodes_list, mv_return)
    plt.xlabel("Episodes")
    plt.ylabel("Returns")
    plt.title("DQN on pysnake")
    plt.show()


def auto_play():
    game = Game()
    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    agent = DQN(1, 1, 1, 0, 0, 0, 0, device)
    agent.load("weights/20230315_105629_max_42.pt", device)
    max_score = 0
    time_start = time.time()
    while True:
        state = get_game_state(game)
        action = agent.take_action(state)
        direction = get_direction_from_action(action)
        alive, _, cwf, cwb, cww = game.play(direction=direction, full_speed=True, teleport=Global.TELEPORT)
        reward = get_game_reward(game, cwf, cwb, cww)
        if not alive:
            result = game.get_score()
            if result > max_score:
                max_score = result
            game.reset_game()
        update_game_surface(game, reward, max_score, time_start)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, default="play", help="train or play by ai")
    args = parser.parse_args()
    if args.mode in ("train", "play"):
        Global.GRID_ROW = Global.GRID_COL = 10
        Global.BLOCK_SIZE = 100
        Global.SCREEN_SIZE = (Global.GRID_COL * Global.BLOCK_SIZE + Global.LEFT_PADDING + Global.RIGHT_PADDING,
                              Global.GRID_ROW * Global.BLOCK_SIZE + Global.TOP_PADDING + Global.BOTTOM_PADDING)
        Global.WITH_AI = True
        Global.FOOD_MAX_COUNT_PER_KIND = 1
        Global.WALL_COUNT_IN_THOUSANDTHS = 0
        Global.HIT_WALL_DAMAGE = 999
        Global.EAT_BODY_DAMAGE = 999
        Global.TELEPORT = False
    if args.mode == "train":
        train()
    elif args.mode == "play":
        try:
            auto_play()
        except KeyboardInterrupt:
            print("Keyboard Interrupt.")
    else:
        raise ValueError(f"mode {args.mode} is not supported")
