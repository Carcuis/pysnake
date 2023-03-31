# PySnake
![banner](resources/img/banner.png)

A python snake game based on pygame.

---

## Requirements

| Package       |  version   |
|---------------|:----------:|
| pygame        |   latest   |
| opencv-python |   latest   |
| matplotlib    |   latest   |
| numpy         |   latest   |
| tqdm          |   latest   |
| torch         | \>= 1.13.1 |

## Run the main game

```bash
python3 main.py
```

## Train the model using Reinforcement Learning (DQN)

```bash
python3 ai.py --mode train
```
  
## Play by AI

```bash
python3 ai.py --mode play
```
