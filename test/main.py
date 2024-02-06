import pygame, sys, random, os, neat, pickle
from copy import deepcopy
from game import Game
from simpliedGame import SimplifiedGame
from slider import Slider
from setting import *
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('NEAT demonstration')

config_path = os.path.join(LOCAL_DIR, 'config.txt')
assist_config_path = os.path.join(LOCAL_DIR, 'assist-config.txt')

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

assist_config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     assist_config_path)

class ReturnToMenu(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.message = message

def formatTime(time):
    minutes = time // 60000
    seconds = time // 1000 % 60
    milliseconds = time % 1000

    result_string = ''
    if minutes < 10:
        result_string += '0'
    result_string += f'{minutes}:'
    if seconds < 10:
        result_string += '0'
    result_string += f'{seconds}:'
    if milliseconds < 10:
        result_string += '00'
    elif milliseconds < 100:
        result_string += '0'
    result_string += str(milliseconds)

    return result_string

def flatten_array(arr):
    flattened = []
    for item in arr:
        if isinstance(item, list):
            flattened.extend(flatten_array(item))
        else:
            flattened.append(item)
    return flattened  

visited_states = []

def getFutures(game, moves, move_left):
    visited_states.append(deepcopy(game.state))
    if move_left == 0:
        return game
    
    games = [SimplifiedGame(deepcopy(game.state), moves-move_left+1, 2 if moves - move_left == 0 else game.initial_direction, direction='left'),
             SimplifiedGame(deepcopy(game.state), moves-move_left+1, 3 if moves - move_left == 0 else game.initial_direction, direction='right'),
             SimplifiedGame(deepcopy(game.state), moves-move_left+1, 0 if moves - move_left == 0 else game.initial_direction, direction='up'),
             SimplifiedGame(deepcopy(game.state), moves-move_left+1, 1 if moves - move_left == 0 else game.initial_direction, direction='down')]
    
    return [getFutures(moved_game, moves, move_left-1) for moved_game in filter(lambda g: g.move_possible and g.state not in visited_states, games)]

def minimax(state, moves):
    global visited_states
    visited_states.clear()

    game = SimplifiedGame(state, 0, None)
    futures = flatten_array(getFutures(game, moves, moves))
    best_game = game
    for future_game in futures:
        if future_game.game_won:
            if best_game.game_won:
                if best_game.move_done > future_game.move_done:
                    best_game = future_game
            else:
                best_game = future_game
        elif not best_game.game_won:
            if future_game.score > best_game.score:
                best_game = future_game

    return best_game.initial_direction

clock = pygame.time.Clock()
MAX_FPS = 60
current_state = 'menu'

# menu screen labels and buttons
title = big_font.render('Number Slider', False, WHITE)
title_rect = title.get_rect(center=(915, 120))

subtitle = small_font.render('a NEAT demonstration', False, WHITE)
subtitle_rect = subtitle.get_rect(center=(950, 165))

train_button_background = pygame.Rect(800, 530, 250, 45)
train_button_text = small_font.render('train', False, WHITE)
train_button_rect = train_button_text.get_rect(center=(925, 555))

play_button_background = pygame.Rect(800, 600, 250, 45)
play_button_text = small_font.render('play', False, WHITE)
play_button_rect = play_button_text.get_rect(center=(925, 625))

# play mode labels and buttons
retry_button_background = pygame.Rect(800, 50, 250, 45)
retry_button_text = small_font.render('Retry', False, WHITE)
retry_button_rect = retry_button_text.get_rect(center=(925, 75))

play_menu_button_background = pygame.Rect(800, 125, 250, 45)
play_menu_button_text = small_font.render('Back to Menu', False, WHITE)
play_menu_button_rect = play_menu_button_text.get_rect(center=(925, 150))

time_label = big_font.render('Time:', False, WHITE)
time_label_rect = time_label.get_rect(center=(830, 250))

rules_label = big_font.render('Rules:', False, WHITE)
rules_label_rect = rules_label.get_rect(center=(847, 480))

rules_text = 'Try and rearrange the puzzles so that the numbers are in order from left to right, up to down! Press the arrow keys to move the panels around!'
lines = []

words = rules_text.split()
current_line = words[0]

# train setting labels and buttons
generations_label = big_font.render('Train Generations:', False, WHITE)
generations_label_rect = generations_label.get_rect(center=(550, 75))

action_after_training_label = small_font.render('Action after training:', False, WHITE)
action_after_training_rect = action_after_training_label.get_rect(center=(550, 240))

visualise_button_background = pygame.Rect(253, 270, 250, 45)
visualise_button_text = small_font.render('Visualise Model', False, WHITE)
visualise_button_rect = visualise_button_text.get_rect(center=(379, 295))

play_against_button_background = pygame.Rect(597, 270, 250, 45)
play_against_button_text = small_font.render('Play against Model', False, WHITE)
play_against_button_rect = play_against_button_text.get_rect(center=(723, 295))

train_mode_label = small_font.render('Train Mode:', False, WHITE)
train_mode_rect = train_mode_label.get_rect(center=(550, 375))

normal_train_button_background = pygame.Rect(253, 405, 250, 45)
normal_train_button_text = small_font.render('Normal Train', False, WHITE)
normal_train_button_rect = normal_train_button_text.get_rect(center=(379, 430))

assisted_train_button_background = pygame.Rect(597, 405, 250, 45)
assisted_train_button_text = small_font.render('Assisted Train', False, WHITE)
assisted_train_button_rect = assisted_train_button_text.get_rect(center=(723, 430))

start_training_button_background = pygame.Rect(425, 650, 250, 45)
start_training_button_text = small_font.render('Start Training', False, WHITE)
start_train_button_rect = start_training_button_text.get_rect(center=(550, 675))

for word in words[1:]:
    test_line = current_line + " " + word
    test_width, _ = small_font.size(test_line)

    if test_width <= 275:
        current_line = test_line
    else:
        lines.append(current_line)
        current_line = word

lines.append(current_line)

rules_text_lines = []
rules_text_rects = []
line_y_position = 510
for line in lines:
    rendered_line = small_font.render(line, False, WHITE)
    rules_text_lines.append(rendered_line)
    rules_text_rects.append(rendered_line.get_rect(topleft=(800, line_y_position)))
    line_y_position += small_font.get_linesize()

slider = None
action_after_train = 'play'
train_mode = 'normal'

def main():
    global current_state, generations, train_mode, action_after_train
    game = Game(750, 750, screen)

    while True:
        clock.tick(MAX_FPS)
        direction = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = event.pos
                if current_state == 'menu':
                    if train_button_background.collidepoint(mouse):
                        current_state = 'train'       
                        slider = Slider(screen, 5, 100, (550, 150), 750, 40, 50, 100, 2)                
                    if play_button_background.collidepoint(mouse):
                        current_state = 'play'
                        game = Game(750, 750, screen)
                elif current_state == 'play':
                    if retry_button_background.collidepoint(mouse):
                        game = Game(750, 750, screen)
                    if play_menu_button_background.collidepoint(mouse):
                        current_state = 'menu'
                        game = Game(750, 750, screen)
                    if game.game_won:
                        if (0 <= mouse[0] <= 750) and (0 <= mouse[1] <= 750):
                            game = Game(750, 750, screen)

                    if train_menu_button_background.collidepoint(mouse):
                        current_state = 'menu'
                        game = Game(750, 750, screen)
                elif current_state == 'train':
                    if slider.onKnob(mouse):
                        slider.dragging = True

                    if normal_train_button_background.collidepoint(mouse):
                        train_mode = 'normal'
                    if assisted_train_button_background.collidepoint(mouse):
                        train_mode = 'assisted'
                    if visualise_button_background.collidepoint(mouse):
                        action_after_train = 'visualise'
                    if play_against_button_background.collidepoint(mouse):
                        action_after_train = 'play'
                    if start_training_button_background.collidepoint(mouse):
                        trainMode(slider.getValue())

            if event.type == pygame.MOUSEBUTTONUP:
                if current_state == 'train':
                    if slider.dragging:
                        slider.dragging = False

            if event.type == pygame.KEYDOWN and current_state == 'play' and not game.game_won:
                if event.key == pygame.K_LEFT:
                    direction = 'left'
                if event.key == pygame.K_RIGHT:
                    direction = 'right'
                if event.key == pygame.K_UP:
                    direction = 'up'
                if event.key == pygame.K_DOWN:
                    direction = 'down'

        screen.fill(BLACK)
        if current_state == 'menu':
            direction = random.choice(['up', 'down', 'left', 'right'])
            game.update(direction, 20)

            screen.blit(title, title_rect)
            screen.blit(subtitle, subtitle_rect)

            pygame.draw.rect(screen, WHITE, train_button_background, 3)
            screen.blit(train_button_text, train_button_rect)

            pygame.draw.rect(screen, WHITE, play_button_background, 3)
            screen.blit(play_button_text, play_button_rect)

        elif current_state == 'play':
            current_time = pygame.time.get_ticks()
            if not game.game_won:
                time_display = big_font.render(formatTime(current_time - game.start_time), False, WHITE)
                time_display_rect = rules_label.get_rect(center=(925, 300))

                move_label = big_font.render(f'Moves: {game.moves}', False, WHITE)
                move_label_rect = move_label.get_rect(topleft=(780, 365))

            pygame.draw.rect(screen, WHITE, retry_button_background, 3)
            screen.blit(retry_button_text, retry_button_rect)
            pygame.draw.rect(screen, WHITE, play_menu_button_background, 3)
            screen.blit(play_menu_button_text, play_menu_button_rect)

            screen.blit(time_label, time_label_rect)
            screen.blit(time_display, time_display_rect)
            screen.blit(move_label, move_label_rect)
            screen.blit(rules_label, rules_label_rect)
            
            for i in range(len(rules_text_lines)):
                screen.blit(rules_text_lines[i], rules_text_rects[i])

            game.update(direction, 10)
            if game.game_won:
                game.displayEndCard()
        
        elif current_state == 'train':
            if slider.dragging:
                mouse = pygame.mouse.get_pos()
                slider.drag(mouse[0])

            generations_label = big_font.render(f'Train Generations: {slider.getValue()}', False, WHITE)
            generations_label_rect = generations_label.get_rect(center=(550, 75))  

            visualise_button_text = small_font.render('Visualise Model', False, WHITE if action_after_train == 'visualise' else GREY)
            play_against_button_text = small_font.render('Play against Model', False, WHITE if action_after_train == 'play' else GREY)
            normal_train_button_text = small_font.render('Normal Train', False, WHITE if train_mode == 'normal' else GREY)
            assisted_train_button_text = small_font.render('Assisted Train', False, WHITE if train_mode == 'assisted' else GREY)

            slider.draw()
            screen.blit(generations_label, generations_label_rect)

            screen.blit(action_after_training_label, action_after_training_rect)
            pygame.draw.rect(screen, WHITE if action_after_train == 'visualise' else GREY, visualise_button_background, 3)
            screen.blit(visualise_button_text, visualise_button_rect)
            pygame.draw.rect(screen, WHITE if action_after_train == 'play' else GREY, play_against_button_background, 3)
            screen.blit(play_against_button_text, play_against_button_rect)

            screen.blit(train_mode_label, train_mode_rect)
            pygame.draw.rect(screen, WHITE if train_mode == 'normal' else GREY, normal_train_button_background, 3)
            screen.blit(normal_train_button_text, normal_train_button_rect)
            pygame.draw.rect(screen, WHITE if train_mode == 'assisted' else GREY, assisted_train_button_background, 3)
            screen.blit(assisted_train_button_text, assisted_train_button_rect)

            pygame.draw.rect(screen, WHITE, start_training_button_background, 3)
            screen.blit(start_training_button_text, start_train_button_rect)

        pygame.display.update()

def trainMode(generation):
    global generations, slider, current_state
    p = neat.Population(config if train_mode == 'normal' else assist_config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    generations = 1
    slider = Slider(screen, 0, 20, (925, 100), 250, 25, 30, 50, 1)

    try:
        winner = p.run(train, generation)
        with open("best.pickle", "wb") as f:
            pickle.dump(winner, f)

        if action_after_train == 'visualise':
            visualise_ai(config if train_mode == 'normal' else assist_config)
        else:
            playAgainst(config if train_mode == 'normal' else assist_config)

    except ReturnToMenu:
        game = Game(750, 750, screen)
        current_state = 'menu'

#train mode labels and buttons
speed_label = small_font.render('Train Speed', False, WHITE)
speed_label_rect = speed_label.get_rect(center=(870, 50))

train_menu_button_background = pygame.Rect(800, 675, 250, 45)
train_menu_button_text = small_font.render('Back to Menu', False, WHITE)
train_menu_button_rect = train_menu_button_text.get_rect(center=(925, 700))

def train(genomes, config):
    global generations
    generation_label = small_font.render(f'Generation: {generations}', False, WHITE)
    generation_rect = generation_label.get_rect(topleft=(800, 150))
    networks = 0

    for genome_id, genome in genomes:
        networks += 1
        prev_direction = 0
        genome.fitness = 0
        game = Game(750, 750, screen)

        network_label = small_font.render(f'Network {networks}/{len(genomes)}', False, WHITE)
        network_rect = network_label.get_rect(topleft=(800, 200))

        running = True
        while running:
            genome.fitness += 1
            clock.tick(MAX_FPS)
            moved = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse = event.pos
                    if slider.onKnob(mouse):
                        slider.dragging = True

                    if train_menu_button_background.collidepoint(mouse):
                        raise ReturnToMenu('return to menu requested from user', None)

                if event.type == pygame.MOUSEBUTTONUP:
                    if slider.dragging:
                        slider.dragging = False

            screen.fill(BLACK)
            
            screen.blit(speed_label, speed_label_rect)
            slider.draw()

            if slider.dragging:
                mouse = pygame.mouse.get_pos()
                slider.drag(mouse[0])
        
            pygame.draw.rect(screen, WHITE, train_menu_button_background, 3)
            screen.blit(train_menu_button_text, train_menu_button_rect)

            network = neat.nn.FeedForwardNetwork.create(genome, config)
            prev_game_state = [element for row in game.state for element in row]
            direction = None
            if not game.animating:
                for row in range(3):
                    for col in range(3):
                        if game.state[row][col] == 0:
                            if train_mode == 'normal':
                                activation_list = [0 for i in range(19)]
                                activation_list[18] = prev_direction
                                element = game.state[row][col]
                                activation_list[element * 2] = col
                                activation_list[element * 2 + 1] = row
                                output = network.activate(activation_list)
                                decision = output.index(max(output))
                            else:
                                output = network.activate((prev_direction, minimax(game.state, MOVES_LOOK_AHEAD), row, col))
                                decision = output.index(max(output))

                direction = directions[decision]
                moved = True

                decision_label = small_font.render(f'Decision: {direction}', False, WHITE)
                decision_rect = decision_label.get_rect(topleft=(800, 250))

                if prev_direction != None:
                    if direction == opposites[directions[prev_direction]]:
                        running = False
                prev_direction = decision

            game.update(direction, 20 - slider.getValue())
            if moved:
                if [element for row in game.state for element in row] == prev_game_state:
                    running = False

            move_label = small_font.render(f'Moves: {game.moves}', False, WHITE)
            move_label_rect = move_label.get_rect(topleft=(800, 300))

            screen.blit(generation_label, generation_rect)
            screen.blit(network_label, network_rect)
            screen.blit(decision_label, decision_rect)
            screen.blit(move_label, move_label_rect)

            pygame.display.update()

            if game.moves >= 50 or game.game_won or not running:
                if game.game_won:
                    genome.fitness += (51 - game.moves) * 100
                else:
                    counter = 1
                    broken = False
                    for row in range(3):
                        for column in range(3):
                            if not broken:
                                element = game.state[row][column]
                                if element != counter:
                                    broken = True
                                else:
                                    genome.fitness += 10
                                
                                counter += 1
                break
    generations += 1

# visualise ai buttons and labels
best_model_label = big_font.render("Best Network:", False, WHITE)
best_model_rect = best_model_label.get_rect(center=(925, 100))

visualise_time_label = small_font.render('Time:', False, WHITE)
visualise_time_label_rect = visualise_time_label.get_rect(center=(829, 277))

visualise_menu_button_background = pygame.Rect(800, 675, 250, 45)
visualise_menu_button_text = small_font.render('Back to Menu', False, WHITE)
visualise_menu_button_rect = visualise_menu_button_text.get_rect(center=(925, 700))

visualise_play_against_button_background = pygame.Rect(800, 610, 250, 45)
visualise_play_against_button_text = small_font.render('Play against Model', False, 'white')
visualise_play_against_button_rect = visualise_play_against_button_text.get_rect(center=(925, 635))

def visualise_ai(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    global current_state, generations
    game = Game(750, 750, screen)
    prev_direction = 0

    while True:
        clock.tick(MAX_FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = event.pos
                if visualise_menu_button_background.collidepoint(mouse):
                    raise ReturnToMenu('return to menu requested from user', None)
                
                if visualise_play_against_button_background.collidepoint(mouse):
                    playAgainst(config)
                
                if game.game_won:
                        if (0 <= mouse[0] <= 750) and (0 <= mouse[1] <= 750):
                            game = Game(750, 750, screen)

        if not game.animating and not game.game_won:
            for row in range(3):
                for col in range(3):
                    if game.state[row][col] == 0:
                        if train_mode == 'normal':
                            activation_list = [0 for i in range(19)]
                            activation_list[18] = prev_direction
                            element = game.state[row][col]
                            activation_list[element * 2] = col
                            activation_list[element * 2 + 1] = row
                            output = winner_net.activate(activation_list)
                            decision = output.index(max(output))
                        else:
                            output = winner_net.activate((prev_direction, minimax(game.state, MOVES_LOOK_AHEAD), row, col))
                            decision = output.index(max(output))

            prev_direction = decision
            decision_label = small_font.render(f'Decision:  {directions[decision]}', False, WHITE)
            decision_rect = decision_label.get_rect(topleft=(800, 165))

        move_label = small_font.render(f'Moves:  {game.moves}', False, WHITE)
        move_label_rect = move_label.get_rect(topleft=(800, 215))

        if not game.game_won:
            current_time = pygame.time.get_ticks()
            time_display = small_font.render(formatTime(current_time - game.start_time), False, WHITE)
            time_display_rect = time_display.get_rect(topleft=(875, 265))

        screen.fill(BLACK)
        screen.blit(best_model_label, best_model_rect)
        pygame.draw.rect(screen, WHITE, visualise_menu_button_background, 3)
        screen.blit(visualise_menu_button_text, visualise_menu_button_rect)
        pygame.draw.rect(screen, WHITE, visualise_play_against_button_background, 3)
        screen.blit(visualise_play_against_button_text, visualise_play_against_button_rect)
        screen.blit(visualise_menu_button_text, visualise_menu_button_rect)
        screen.blit(move_label, move_label_rect)
        screen.blit(decision_label, decision_rect)   
        screen.blit(visualise_time_label, visualise_time_label_rect)
        screen.blit(time_display, time_display_rect)   

        game.update(directions[decision], 10)
        if game.game_won:
            game.displayEndCard()

        pygame.display.update()

# play against AI mode labels and buttons

user_game_label_background = pygame.Rect(0, 0, 600, 150)
your_game_label = big_font.render('Your Game', False, BLACK)
your_game_rect = your_game_label.get_rect(center=(300, 75))

vs_label = big_font.render('VS', False, WHITE)
vs_rect = vs_label.get_rect(center=(700, 225))

ai_game_label_background = pygame.Rect(800, 0, 300, 75)
ai_game_label = small_font.render('AI\'s Game', False, BLACK)
ai_game_rect = ai_game_label.get_rect(center=(950, 37.5))

play_against_time_label = big_font.render('Time:', False, WHITE)
play_against_time_label_rect = play_against_time_label.get_rect(center=(700, 490))

score_label = big_font.render('Score:', False, WHITE)
score_label_rect = score_label.get_rect(center=(725, 575))

play_against_menu_button_background = pygame.Rect(812, 675, 250, 45)
play_against_menu_button_text = small_font.render('Back to Menu', False, WHITE)
play_against_menu_button_rect = play_against_button_text.get_rect(center=(970, 700))

def playAgainst(config):
    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)

    global current_state, generations
    user_game = Game(600, 600, screen, (0, 150))
    network_game = Game(300, 300, screen, (800, 75))
    network_prev_direction = 0
    scores = [0, 0]
    race_over = False
    score_updated = False

    score_display = big_font.render('0  to  0', False, WHITE)
    score_display_rect = score_display.get_rect(topleft=(825, 555)) 

    while True:
        clock.tick(MAX_FPS)
        direction = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse = event.pos
                if play_against_menu_button_background.collidepoint(mouse):
                    raise ReturnToMenu('return to menu requested from user', None)
                
                if race_over:
                    if 0 <= mouse[0] <= 600 and 150 <= mouse[1] <= 750:
                        user_game = Game(600, 600, screen, (0, 150))
                        network_game = Game(300, 300, screen , (800, 75))
                        race_over = False
                        score_updated = False
                
            if event.type == pygame.KEYDOWN and not race_over:
                if event.key == pygame.K_LEFT:
                    direction = 'left'
                if event.key == pygame.K_RIGHT:
                    direction = 'right'
                if event.key == pygame.K_UP:
                    direction = 'up'
                if event.key == pygame.K_DOWN:
                    direction = 'down'

        if not network_game.animating and not race_over:
            for row in range(3):
                for col in range(3):
                    if network_game.state[row][col] == 0:
                        if train_mode == 'normal':
                            activation_list = [0 for i in range(19)]
                            activation_list[18] = network_prev_direction
                            element = network_game.state[row][col]
                            activation_list[element * 2] = col
                            activation_list[element * 2 + 1] = row
                            output = winner_net.activate(activation_list)
                            decision = output.index(max(output))
                        else:
                            output = winner_net.activate((network_prev_direction, minimax(network_game.state, MOVES_LOOK_AHEAD), row, col))
                            decision = output.index(max(output))

            direction = directions[decision]
            network_prev_direction = decision

        if not race_over:
            current_time = pygame.time.get_ticks()
            time_display = big_font.render(formatTime(current_time - user_game.start_time), False, WHITE)
            time_display_rect = time_display.get_rect(topleft=(800, 468))

        screen.fill(BLACK)        

        pygame.draw.rect(screen, WHITE, user_game_label_background)
        pygame.draw.rect(screen, WHITE, ai_game_label_background)
        pygame.draw.rect(screen, WHITE, play_against_menu_button_background, 3)
        screen.blit(play_against_menu_button_text, play_against_menu_button_rect)
        screen.blit(your_game_label, your_game_rect)
        screen.blit(ai_game_label, ai_game_rect)
        screen.blit(play_against_time_label, play_against_time_label_rect)
        screen.blit(time_display, time_display_rect)
        screen.blit(score_label, score_label_rect)
        screen.blit(score_display, score_display_rect)
        screen.blit(vs_label, vs_rect)

        user_game.update(direction, 10)
        network_game.update(directions[decision], 10)

        if (user_game.game_won or network_game.game_won) and not score_updated:
            scores[0 if user_game.game_won else 1] += 1
            race_over = True
            score_display = big_font.render(f'{scores[0]}  to  {scores[1]}', False, WHITE)
            score_display_rect = score_display.get_rect(topleft=(825, 555))
            score_updated = True

        if race_over:
            user_game.displayWonMessage() if user_game.game_won else user_game.displayLostMessage()

        pygame.display.update()

if __name__ == "__main__":    
    main()