import argparse
import os
import random
import shutil
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
    def __init__(self, capacity: int) -> None:
        self.buffer: deque[tuple] = deque(maxlen=capacity)

    def add(self, state, action, reward, next_state, done) -> None:
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size: int) -> tuple:
        transitions = random.sample(self.buffer, batch_size)
        state, action, reward, next_state, done = zip(*transitions)
        return np.array(state), action, reward, np.array(next_state), done

    @property
    def size(self) -> int:
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
                 learning_rate: float, gamma: float, epsilon: float, target_update: int, device: torch.device,
                 mode: str, model_path: str = "") -> None:
        self.action_dim: int = action_dim
        self.device: torch.device = device
        if mode == "train":
            if model_path == "":
                self.q_net: Qnet = Qnet(state_dim, hidden_dim, self.action_dim).to(device)  # Q网络
                self.target_q_net: Qnet = Qnet(state_dim, hidden_dim, self.action_dim).to(device)
            else:
                self.load(model_path, "train")
        elif mode == "eval":
            if model_path == "":
                raise ValueError("model path must be provided in `eval` mode")
            self.load(model_path, "eval")
        else:
            raise ValueError(f"mode: {mode} error, must be `train` or `eval`")
        self.optimizer = torch.optim.Adam(self.q_net.parameters(), lr=learning_rate)
        self.gamma: float = gamma  # 折扣因子
        self.epsilon: float = epsilon  # epsilon-贪婪策略
        self.target_update: int = target_update  # 目标网络更新频率
        self.count: int = 0  # 计数器,记录更新次数

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

    def load(self, path: str, load_mode: str) -> None:
        """
        load the model

        :param path: the path of the model
        :param load_mode: `train` or `eval`
        """

        if not os.path.exists(path):
            raise FileNotFoundError(f"model file: {path} not found")

        # only load state_dict
        # checkpoint = torch.load(path)
        # self.q_net.load_state_dict(checkpoint['model_state_dict'])
        # self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])

        # load the whole model
        self.q_net = torch.load(path, map_location=self.device)

        if load_mode == "train":
            self.q_net.train()
            self.target_q_net = torch.load(path, map_location=self.device)
            self.target_q_net.train()
        elif load_mode == "eval":
            self.q_net.eval()
        else:
            raise ValueError(f"mode: {load_mode} error, must be `train` or `eval`")

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


class AI:
    @staticmethod
    def moving_average(input_list: list[int | float], window_size: int) -> npt.NDArray:
        """
        calculate the moving average of a numpy array

        :param input_list: list[int | float]
        :param window_size: int
        :return: moving average of the input array
        """

        cumulative_sum = np.cumsum(np.insert(input_list, 0, 0))
        middle = (cumulative_sum[window_size:] - cumulative_sum[:-window_size]) / window_size
        r = np.arange(1, window_size - 1, 2)
        begin = np.cumsum(input_list[:window_size - 1])[::2] / r
        end = (np.cumsum(input_list[:-window_size:-1])[::2] / r)[::-1]
        return np.concatenate((begin, middle, end))

    @staticmethod
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

    def get_game_state(self, game: Game) -> npt.NDArray:
        game_state = np.array((
            game.snake.x[0] - game.food_manager.apple.x[0],
            game.snake.y[0] - game.food_manager.apple.y[0],
            game.snake.hungry.hungry_step_count,
            game.snake.direction.value
        ))
        return np.concatenate((game_state, self.get_surroundings(game, 4)))

    @staticmethod
    def update_game_surface(game: Game, reward: int, max_score: int, time_start: float) -> None:
        EventManager.get_event()
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
            Text(f"HSC: {game.snake.hungry.hungry_step_count}", pygame.Color("white"),
                 position=(0.25, 1, "left_bottom"), alpha=255),
            Text("{:02d}: {:02d}: {:02d}".format(hours, minutes, seconds), pygame.Color("white"),
                 position=(0.7, 1), alpha=255)
        )
        game.update_board()
        Util.update_screen()
        game.clock.tick()

    @staticmethod
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

    @staticmethod
    def rename_model(max_score: int, final=False) -> None:
        """
        rename the model to a time format

        :param max_score: the max score of the model
        :param final: whether the model is the final model, if final=True, then the original model will be removed and
                      add "_final" to the model name, otherwise, the original model will be remained
        """

        time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        if final:
            time_str = f"{time_str}_final"
        original_model_path = "weights/model.pt"
        model_save_path = f"weights/{time_str}_max_{max_score}.pt"
        if not os.path.exists(original_model_path):
            raise FileNotFoundError("original model.pt file not found in ./weights/")
        if final:
            os.rename(original_model_path, model_save_path)
            print(f"newest model renamed to {model_save_path}")
        else:
            shutil.copyfile(original_model_path, model_save_path)
            print(f"model at max score copied to {model_save_path}")

    @staticmethod
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
        reward = max(
            (100 - abs(game.snake.x[0] - game.food_manager.apple.x[0]) -
             abs(game.snake.y[0] - game.food_manager.apple.y[0]) - game.snake.hungry.hungry_step_count),
            # -50
            0
        )

        if collide_with_food:
            # reward = 100 * game.eat_food_count
            # reward = 100
            reward = max(200 - game.snake.hungry.hungry_step_count, 100)
        if collide_with_body:
            reward = -200
        if collide_with_wall:
            reward = -200

        return reward

    def train_model(self, path: str = "") -> None:
        """
        train the model

        :param path: pre-trained model path
        """

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
        state_dim = self.get_game_state(game).size
        hidden_dim = 64
        action_dim = 4
        agent = DQN(state_dim, hidden_dim, action_dim, lr, gamma, epsilon, target_update, device, "train", path)

        max_score = 0
        return_list: list[int | float] = []
        time_start = time.time()
        it = 0
        while True:
            it += 1
            try:
                with tqdm(total=num_episodes, desc=f"Iteration {it}") as pbar:
                    for i_episode in range(num_episodes):
                        state = self.get_game_state(game)
                        alive = True
                        game.init_game_surface()
                        while alive:
                            action = agent.take_action(state)
                            direction = self.get_direction_from_action(action)
                            alive, _, collide_with_food, collide_with_body, collide_with_wall = \
                                game.play(direction=direction, full_speed=True, teleport=Global.TELEPORT)
                            reward = self.get_game_reward(game, collide_with_food, collide_with_body, collide_with_wall)
                            next_state = self.get_game_state(game)
                            replay_buffer.add(state, action, reward, next_state, not alive)
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
                            self.update_game_surface(game, reward, max_score, time_start)

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
                print("Keyboard Interrupt.")
                break

        print(f"max score: {max_score}")
        self.rename_model(max_score)
        agent.save()
        self.rename_model(max_score, final=True)
        self.plot_result(return_list)

    def plot_result(self, return_list: list[int | float]) -> None:
        """
        plot the result

        :param return_list: data to plot
        """

        time_str = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        if not os.path.exists("weights/img"):
            os.makedirs("weights/img")
        episodes_list = list(range(len(return_list)))
        plt.plot(episodes_list, return_list)
        plt.xlabel("Episodes")
        plt.ylabel("Returns")
        plt.title("DQN on pysnake")
        plt.savefig(f"weights/img/result_{time_str}.png")
        print(f"result saved to weights/img/result_{time_str}.png")

        mv_return = self.moving_average(return_list, 9)
        plt.plot(episodes_list, mv_return)
        plt.xlabel("Episodes")
        plt.ylabel("Returns")
        plt.title("DQN on pysnake")
        plt.savefig(f"weights/img/mv_result_{time_str}.png")
        print(f"moving average result saved to weights/img/mv_result_{time_str}.png")

    def auto_play(self, path: str) -> None:
        """
        play using the trained model automatically

        :param path: trained model path
        """

        game = Game()
        device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        agent = DQN(1, 1, 1, 0, 0, 0, 0, device, "eval", path)
        max_score = 0
        time_start = time.time()

        while True:
            game.init_game_surface()
            alive = True
            while alive:
                state = self.get_game_state(game)
                action = agent.take_action(state)
                direction = self.get_direction_from_action(action)
                alive, _, cwf, cwb, cww = game.play(direction=direction, full_speed=True, teleport=Global.TELEPORT)
                reward = self.get_game_reward(game, cwf, cwb, cww)
                self.update_game_surface(game, reward, max_score, time_start)

            result = game.get_score()
            if result > max_score:
                max_score = result
            game.reset_game()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", action="store_true", help="use `train` mode instead of default `play` mode")
    parser.add_argument(
        "--model-path", type=str,
        help="path to a pre-trained model, available for both `train` and `play` mode"
    )
    args = parser.parse_args()

    mode: str = "train" if args.train else "play"
    model_path: str = args.model_path or ""
    if model_path == "":
        if mode == "play":
            model_path = "weights/20230401_123536_final_max_92.pt"
    elif not os.path.exists(model_path):
        raise ValueError(f"model path {model_path} does not exist")

    Global.GRID_ROW = Global.GRID_COL = 50
    # Global.BLOCK_SIZE = 100
    Global.SCREEN_SIZE = (Global.GRID_COL * Global.BLOCK_SIZE + Global.LEFT_PADDING + Global.RIGHT_PADDING,
                          Global.GRID_ROW * Global.BLOCK_SIZE + Global.TOP_PADDING + Global.BOTTOM_PADDING)
    Global.WITH_AI = True
    Global.FOOD_MAX_COUNT_PER_KIND = 1
    Global.WALL_COUNT_IN_THOUSANDTHS = 0
    Global.HIT_WALL_DAMAGE = 999
    Global.EAT_BODY_DAMAGE = 999
    Global.TELEPORT = False

    ai = AI()
    if mode == "train":
        if model_path == "":
            print("No pre-trained model found, training a new model...")
        else:
            print(f"USING pre-trained model {model_path}")
        ai.train_model(model_path)
    elif mode == "play":
        try:
            print(f"USING pre-trained model {model_path}")
            ai.auto_play(model_path)
        except KeyboardInterrupt:
            print("Keyboard Interrupt.")


if __name__ == "__main__":
    main()
