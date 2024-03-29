from setting import *
import pygame, sys, os, threading, pickle
from puzzle import Puzzle
from displayPuzzle import DisplayPuzzle
from slider import Slider
from animation import Animation
from ai import Ai
from copy import deepcopy
pygame.init()

# updating the demo on screen in the main menu, play and choosing difficulty screen
def updateDemo(deltaTime: int) -> None:
    global time_since_last_demo_move, previous_frame_time

    current_frame_time = pygame.time.get_ticks()
    time_since_last_demo_move += current_frame_time - previous_frame_time
    previous_frame_time = current_frame_time

    screen.blit(title_card_line_one, title_card_line_one_rect)
    screen.blit(title_card_line_two, title_card_line_two_rect)
    screen.blit(title_card_line_three, title_card_line_three_rect)
    
    if time_since_last_demo_move > 500:
        puzzle1.update(puzzle1.getDemoMove(), deltaTime)
        time_since_last_demo_move = 0
    else:
        puzzle1.update(None, deltaTime)

# format the time from millisecond form to mm:ss:ms form
def formatTime(time: int) -> str:
    if time == None:
        return '--:--:---'
    
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

#retrieve save data
try:
    with open('data.pkl', 'rb') as file:
        data = pickle.load(file)

        music_volume = data['music_volume']
        sfx_volume = data['sfx_volume']
        best_time = data['best_time']
        current_difficulty = data['current_difficulty']
except:
    music_volume = 0.5
    sfx_volume = 0.5
    best_time = {
        3: None,
        4: None,
        5: None,
    }
    current_difficulty = 4

# initialising global variables
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('2P Number Slider')
pygame.display.set_icon(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile1.png')))

pygame.mixer.music.load(os.path.join(LOCAL_DIR, 'Assets/bgmusic.mp3'))
click_sound = pygame.mixer.Sound(os.path.join(LOCAL_DIR, 'Assets/click.ogg'))
slide_sound = pygame.mixer.Sound(os.path.join(LOCAL_DIR, 'Assets/slide.wav'))
pygame.mixer.music.set_volume(music_volume)
click_sound.set_volume(sfx_volume)
slide_sound.set_volume(sfx_volume)
pygame.mixer.music.play(-1)

puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
puzzle2 = None
previous_mode = None
current_mode = 'main-menu'
time_since_last_demo_move = 0
previous_frame_time = pygame.time.get_ticks()

player_one_score = 0
player_two_score = 0
race_finished = False
tutorial_phase = 0

# variables and functions for preparing the A.I. puzzles
def initialiseAiPuzzles() -> None:
    global three_by_three_puzzles,four_by_four_puzzles, three_by_three_ai, four_by_four_ai, first_move_four_by_four_ai, first_move_three_by_three_ai, current_puzzle_index, update_ai_puzzle
    three_by_three_puzzles = []
    four_by_four_puzzles = []
    three_by_three_ai = Ai(AI_LOOK_FORWARD_MOVES[3], 3)
    four_by_four_ai = Ai(AI_LOOK_FORWARD_MOVES[4], 4)
    first_move_four_by_four_ai = Ai(5, 4)
    first_move_three_by_three_ai = Ai(6, 3)
    update_ai_puzzle = True
    current_puzzle_index = 0

    for _ in range(3):
        three_by_three_puzzle = Puzzle(3, True)
        four_by_four_puzzle = Puzzle(4, True)
        three_by_three_initial_state = deepcopy(three_by_three_puzzle.getState())
        four_by_four_initial_state = deepcopy(four_by_four_puzzle.getState())

        three_by_three_move_list = first_move_three_by_three_ai.getOptimalMove(three_by_three_puzzle.getState(), None)
        for move in three_by_three_move_list:
            three_by_three_puzzle.move(move)

        four_by_four_move_list = first_move_four_by_four_ai.getOptimalMove(four_by_four_puzzle.getState(), None)
        for move in four_by_four_move_list:
            four_by_four_puzzle.move(move)
        
        three_by_three_puzzles.append([three_by_three_initial_state, deepcopy(three_by_three_puzzle), deepcopy(three_by_three_move_list)])
        four_by_four_puzzles.append([four_by_four_initial_state, deepcopy(four_by_four_puzzle), deepcopy(four_by_four_move_list)])

def addPuzzle(difficulty: int) -> None:
    global three_by_three_puzzles, four_by_four_puzzles, update_ai_puzzle, current_puzzle_index

    ai = first_move_three_by_three_ai if difficulty == 3 else first_move_four_by_four_ai
    puzzle_list = three_by_three_puzzles if difficulty == 3 else four_by_four_puzzles

    puzzle = Puzzle(difficulty, True)
    initial_state = deepcopy(puzzle.getState())
    update_ai_puzzle = True

    move_list = ai.getOptimalMove(puzzle.getState(), None)
    for move in move_list:
        puzzle.move(move)

    puzzle_list.append([initial_state, deepcopy(puzzle), deepcopy(move_list)])

    while updating:
        pass

    puzzle_list.pop(0)
    current_puzzle_index -= 1

updating = False
def updatePuzzles(difficulty: int) -> None:
    global three_by_three_puzzles, four_by_four_puzzles, update_ai_puzzle, updating

    ai = three_by_three_ai if difficulty == 3 else four_by_four_ai
    puzzle_list = three_by_three_puzzles if difficulty == 3 else four_by_four_puzzles

    initial_state, puzzle, move_list = puzzle_list[current_puzzle_index]
    new_move_list = ai.getOptimalMove(puzzle.getState(), move_list[-1])
    for move in new_move_list:
        puzzle.move(move)
    move_list += new_move_list
    puzzle_list[current_puzzle_index] = deepcopy([initial_state, puzzle, move_list])

    if puzzle.isSolved():
        update_ai_puzzle = False
    updating = False

initialise_ai_puzzles_thread = threading.Thread(target=initialiseAiPuzzles)
initialise_ai_puzzles_thread.start()

# main menu buttons and labels
title_card_line_one = big_font.render('Two Player', False, WHITE)
title_card_line_one_rect = title_card_line_one.get_rect(center=(930, 100))

title_card_line_two = big_font.render('Number', False, WHITE)
title_card_line_two_rect = title_card_line_two.get_rect(center=(930, 160))

title_card_line_three = big_font.render('Slider', False, WHITE)
title_card_line_three_rect = title_card_line_three.get_rect(center=(930, 220))

play_button_background = pygame.Rect(800, 512, 250, 60)
play_button_text = medium_font.render('play', False, WHITE)
play_button_rect = play_button_text.get_rect(center=(925, 545))

main_menu_options_button_background = pygame.Rect(800, 592, 250, 60)
main_menu_options_button_text = medium_font.render('options', False, WHITE)
main_menu_options_button_rect = main_menu_options_button_text.get_rect(center=(925, 625))

# options menu buttons, labels and sliders
music_slider = Slider(screen, 0, 1, (640, 450), 750, 40, 50, 100, 2, music_volume)
sfx_slider = Slider(screen, 0, 1, (640, 570), 750, 40, 50, 100, 2, sfx_volume)

options_label = big_font.render('Options', False, WHITE)
options_label_rect = options_label.get_rect(center=(550, 50))

difficulty_label = medium_font.render('Difficulty:', False, WHITE)
difficulty_label_rect = difficulty_label.get_rect(topleft=(50, 130))

three_by_three_button_background = pygame.Rect(148, 210, 250, 66)
three_by_three_button_text = big_font.render('3x3', False, WHITE)
three_by_three_button_rect = three_by_three_button_text.get_rect(center=(275, 250))

four_by_four_button_background = pygame.Rect(423, 210, 250, 66)
four_by_four_button_text = big_font.render('4x4', False, WHITE)
four_by_four_button_rect = four_by_four_button_text.get_rect(center=(550, 250))

five_by_five_button_background = pygame.Rect(698, 210, 250, 66)
five_by_five_button_text = big_font.render('5x5', False, WHITE)
five_by_five_button_rect = five_by_five_button_text.get_rect(center=(825, 250))

volumn_label = medium_font.render('Volume:', False, WHITE)
volumn_label_rect = volumn_label.get_rect(topleft=(50, 320))

music_label = big_font.render('Music', False, WHITE)
music_label_rect = music_label.get_rect(topleft=(75, 425))

sfx_label = big_font.render('SFX', False, WHITE)
sfx_label_rect = sfx_label.get_rect(topleft=(75, 545))

return_button_background = pygame.Rect(420, 660, 250, 66)
return_button_text = big_font.render('Return', False, WHITE)
return_button_rect = return_button_text.get_rect(center=(550, 700))

# play screen buttons and labels
time_trial_button_background = pygame.Rect(785, 310, 280, 60)
time_trial_button_text = medium_font.render('Time Trial', False, WHITE)
time_trial_button_rect = time_trial_button_text.get_rect(center=(925, 345))

versus_ai_button_background = pygame.Rect(785, 390, 280, 60)
versus_ai_button_text = medium_font.render('Versus A.I.', False, WHITE)
versus_ai_button_rect = versus_ai_button_text.get_rect(center=(925, 425))

two_players_button_background = pygame.Rect(785, 470, 280, 60)
two_players_button_text = medium_font.render('Two Players', False, WHITE)
two_players_button_rect = two_players_button_text.get_rect(center=(925, 505))

tutorial_button_background = pygame.Rect(785, 550, 280, 60)
tutorial_button_text = medium_font.render('Tutorial', False, WHITE)
tutorial_button_rect = tutorial_button_text.get_rect(center=(925, 585))

play_screen_back_to_menu_background = pygame.Rect(785, 630, 280, 60)
play_screen_back_to_menu_button_text = medium_font.render('Back to menu', False, WHITE)
player_screen_back_to_menu_button_rect = play_screen_back_to_menu_button_text.get_rect(center=(925, 665))

# choosing difficulty screen buttons and labels
pick_a_difficulty_label = medium_font.render('Pick a difficulty', False, WHITE)
pick_a_difficulty_rect = pick_a_difficulty_label.get_rect(center=(925, 340))

easy_button_background = pygame.Rect(800, 410, 250, 60)
easy_button_text = medium_font.render('Easy', False, WHITE)
easy_button_rect = easy_button_text.get_rect(center=(925, 445))

medium_button_background = pygame.Rect(800, 490, 250, 60)
medium_button_text = medium_font.render('Medium', False, WHITE)
medium_button_rect = medium_button_text.get_rect(center=(925, 525))

difficult_button_background = pygame.Rect(800, 570, 250, 60)
difficult_button_text = medium_font.render('Hard', False, WHITE)
difficult_button_rect = difficult_button_text.get_rect(center=(925, 605))

# time trial mode buttons and labels
time_trial_best_time_label = medium_font.render('Best Time: ', False, WHITE)
time_trial_best_time_rect = time_trial_best_time_label.get_rect(topleft=(770, 100))

time_trial_time_label = medium_font.render('Time: ', False, WHITE)
time_trial_time_rect = time_trial_time_label.get_rect(topleft=(770, 230))

time_trial_move_label = medium_font.render('Moves:', False, WHITE)
time_trial_move_rect = time_trial_move_label.get_rect(topleft=(770, 365))

time_trial_restart_button_background = pygame.Rect(780, 500, 290, 60)
time_trial_restart_button_text = medium_font.render('Restart', False, WHITE)
time_trial_restart_button_rect = time_trial_restart_button_text.get_rect(center=(925, 535))

time_trial_back_to_menu_button_background = pygame.Rect(780, 580, 290, 60)
time_trial_back_to_menu_button_text = medium_font.render('Back to menu', False, WHITE)
time_trial_back_to_menu_button_rect = time_trial_back_to_menu_button_text.get_rect(center=(925, 615))

time_trial_options_button_background = pygame.Rect(780, 660, 290, 60)
time_trial_options_button_text = medium_font.render('Options', False, WHITE)
time_trial_options_button_rect = time_trial_options_button_text.get_rect(center=(925, 695))

# two players mode buttons and labels
player_one_label = big_font.render(f'Player 1', False, WHITE)
player_one_rect = player_one_label.get_rect(topleft=(25, 25))

player_two_label = big_font.render(f'Player 2', False, WHITE)
player_two_rect = player_two_label.get_rect(topright=(1075, 25))

score_label = medium_font.render(f'{player_one_score} vs {player_two_score}', False, WHITE)
score_rect = score_label.get_rect(center=(550, 75))

two_players_restart_button_background = pygame.Rect(38, 675, 290, 60)
two_players_restart_button_text = medium_font.render('Restart', False, WHITE)
two_players_restart_button_rect = two_players_restart_button_text.get_rect(center=(183, 710))

two_players_back_to_menu_button_background = pygame.Rect(405, 675, 290, 60)
two_players_back_to_menu_button_text = medium_font.render('Back to menu', False, WHITE)
two_players_back_to_menu_button_rect = two_players_back_to_menu_button_text.get_rect(center=(550, 710))

two_players_options_button_background = pygame.Rect(772, 675, 290, 60)
two_players_options_button_text = medium_font.render('Options', False, WHITE)
two_players_options_button_rect = two_players_options_button_text.get_rect(center=(917, 710))

# tutorial mode buttons and labels
tutorial_instruction_button_background = pygame.Rect(780, 420, 290, 60)
tutorial_instruction_button_text = medium_font.render('Instruction', False, WHITE)
tutorial_instruction_button_rect = tutorial_instruction_button_text.get_rect(center=(925, 455))

tutorial_restart_button_background = pygame.Rect(780, 500, 290, 60)
tutorial_restart_button_text = medium_font.render('Restart', False, WHITE)
tutorial_restart_button_rect = tutorial_restart_button_text.get_rect(center=(925, 535))

tutorial_back_to_menu_button_background = pygame.Rect(780, 580, 290, 60)
tutorial_back_to_menu_button_text = medium_font.render('Back to menu', False, WHITE)
tutorial_back_to_menu_button_rect = tutorial_back_to_menu_button_text.get_rect(center=(925, 615))

tutorial_options_button_background = pygame.Rect(780, 660, 290, 60)
tutorial_options_button_text = medium_font.render('Options', False, WHITE)
tutorial_options_button_rect = tutorial_options_button_text.get_rect(center=(925, 695))

instruction_display_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
instruction_display_background_rect = instruction_display_background.get_rect()
instruction_display_background.set_alpha(200)
instruction_display_background.fill(BLACK)

objective_label = medium_font.render('Objective:', False, WHITE)
objective_rect = objective_label.get_rect(topleft=(775, 50))

phase_one_objective_label = small_font.render('Move 5 times', False, WHITE)
phase_one_objective_rect = phase_one_objective_label.get_rect(topleft=(775, 110))

phase_two_objective_label1 = small_font.render('Create the pattern shown', False, WHITE)
phase_two_objective_rect1 = phase_two_objective_label1.get_rect(topleft=(775, 110))

phase_two_objective_label2 = small_font.render('in the instructions', False, WHITE)
phase_two_objective_rect2 = phase_two_objective_label2.get_rect(topleft=(775, 150))

phase_three_objective_label1 = small_font.render('Solve the first layer of', False, WHITE)
phase_three_objective_rect1 = phase_three_objective_label1.get_rect(topleft=(775, 110))

phase_three_objective_label2 = small_font.render('the puzzle', False, WHITE)
phase_three_objective_rect2 = phase_three_objective_label2.get_rect(topleft=(775, 150))

phase_four_objective_label1 = small_font.render('Solve the second layer of', False, WHITE)
phase_four_objective_rect1 = phase_four_objective_label1.get_rect(topleft=(775, 110))

phase_four_objective_label2 = small_font.render('the puzzle', False, WHITE)
phase_four_objective_rect2 = phase_four_objective_label2.get_rect(topleft=(775, 150))

phase_five_objective_label = small_font.render('Solve the puzzle', False, WHITE)
phase_five_objective_rect = phase_five_objective_label.get_rect(topleft=(775, 110))

instruction_displayed = False

# versus A.I. mode buttons and labels
versus_ai_restart_button_background = pygame.Rect(38, 675, 290, 60)
versus_ai_restart_button_text = medium_font.render('Restart', False, WHITE)
versus_ai_restart_button_rect = versus_ai_restart_button_text.get_rect(center=(183, 710))

versus_ai_back_to_menu_button_background = pygame.Rect(405, 675, 290, 60)
versus_ai_back_to_menu_button_text = medium_font.render('Back to menu', False, WHITE)
versus_ai_back_to_menu_button_rect = versus_ai_back_to_menu_button_text.get_rect(center=(550, 710))

versus_ai_options_button_background = pygame.Rect(772, 675, 290, 60)
versus_ai_options_button_text = medium_font.render('Options', False, WHITE)
versus_ai_options_button_rect = versus_ai_options_button_text.get_rect(center=(917, 710))

versus_ai_best_time_label = medium_font.render('Best Time: ', False, WHITE)
versus_ai_best_time_rect = versus_ai_best_time_label.get_rect(topleft=(670, 50))

versus_ai_time_label = medium_font.render('Time: ', False, WHITE)
versus_ai_time_rect = versus_ai_time_label.get_rect(topleft=(670, 180))

players_game_label = big_font.render('Your Game', False, WHITE)
players_game_rect = players_game_label.get_rect(center=(275, 60))

ai_games_label = medium_font.render('A.I. Game', False, WHITE)
ai_games_rect = ai_games_label.get_rect(center=(975, 370))

versus_label = big_font.render('vs', False, WHITE)
versus_rect = versus_label.get_rect(center=(700, 530))

versus_ai_score_label = medium_font.render('Score:', False, WHITE)
versus_ai_score_rect = versus_ai_score_label.get_rect(center=(710, 400))

# the main program
def main() -> None:
    global current_mode, music_volume, sfx_volume, current_difficulty, puzzle1, puzzle2, best_time, player_one_score, player_two_score, player_two_rect, race_finished, score_label, score_rect, tutorial_phase, instruction_displayed, three_by_three_puzzles, four_by_four_puzzles, current_puzzle_index, updating
    ai_difficulty = None
    ai_time_since_last_move = 0
    previous_frame_time = pygame.time.get_ticks()
    current_frame_time = pygame.time.get_ticks()
    added_animations = False

    while True:
        player_one_direction = None
        player_two_direction = None

        # checking deltaTime
        current_frame_time = pygame.time.get_ticks()
        deltatime = current_frame_time - previous_frame_time
        previous_frame_time = current_frame_time

        # initialising animations for tutorial mode
        if not added_animations:
            if not initialise_animations_thread.is_alive():
                add_animations_thread = threading.Thread(target=addAnimations)
                add_animations_thread.start()
                added_animations = True

        for event in pygame.event.get():
            # closing the game
            if event.type == pygame.QUIT:
                data = {
                    'music_volume': music_volume,
                    'sfx_volume': sfx_volume,
                    'best_time': best_time,
                    'current_difficulty': current_difficulty
                }

                with open('data.pkl', 'wb') as file:
                     pickle.dump(data, file)

                pygame.quit()
                sys.exit()

            # mouse click events
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if current_mode == 'main-menu':
                    if play_button_background.collidepoint(mouse_pos):
                        pygame.mixer.Sound.play(click_sound)
                        current_mode = 'play'
                    elif main_menu_options_button_background.collidepoint(mouse_pos):
                        pygame.mixer.Sound.play(click_sound)
                        previous_mode = 'main-menu'
                        current_mode = 'options'
                elif current_mode == 'options':
                    if music_slider.mouseOnKnob(mouse_pos):
                        music_slider.setDragging(True)
                    elif sfx_slider.mouseOnKnob(mouse_pos):
                        sfx_slider.setDragging(True)
                    elif three_by_three_button_background.collidepoint(mouse_pos):
                        current_difficulty = 3
                        pygame.mixer.Sound.play(click_sound)
                    elif four_by_four_button_background.collidepoint(mouse_pos):
                        current_difficulty = 4
                        pygame.mixer.Sound.play(click_sound)
                    elif five_by_five_button_background.collidepoint(mouse_pos):
                        if previous_mode != 'versus-ai':
                            current_difficulty = 5
                            pygame.mixer.Sound.play(click_sound)
                    elif return_button_background.collidepoint(mouse_pos):
                        current_mode = previous_mode
                        pygame.mixer.Sound.play(click_sound)
                elif current_mode == 'play':
                    if time_trial_button_background.collidepoint(mouse_pos):
                        current_mode = 'time-trial'
                        pygame.mixer.Sound.play(click_sound)
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'time-trial')
                    elif versus_ai_button_background.collidepoint(mouse_pos):
                        if current_difficulty != 5:
                            current_mode = 'choosing-difficulty'
                            pygame.mixer.Sound.play(click_sound)
                        else:
                            screen.blit(instruction_display_background, instruction_display_background_rect)
                            displayWarningScreen()
                    elif two_players_button_background.collidepoint(mouse_pos):
                        current_mode = 'two-players'
                        player_one_score = 0
                        player_two_score = 0
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'two-players')
                        puzzle2 = DisplayPuzzle(current_difficulty, 550, screen, (550, 100), 'two-players')

                        score_label = medium_font.render(f'{player_one_score} vs {player_two_score}', False, WHITE)
                        score_rect = score_label.get_rect(center=(550, 75))
                        race_finished = False
                        pygame.mixer.Sound.play(click_sound)
                    elif tutorial_button_background.collidepoint(mouse_pos):
                        current_mode = 'tutorial'
                        tutorial_phase = 0
                        puzzle1 = DisplayPuzzle(3, SCREEN_HEIGHT, screen, (0, 0), 'tutorial')
                        pygame.mixer.Sound.play(click_sound)
                    elif play_screen_back_to_menu_background.collidepoint(mouse_pos):
                        current_mode = 'main-menu'
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'choosing-difficulty':
                    start = False
                    if easy_button_background.collidepoint(mouse_pos):
                        current_mode = 'versus-ai'
                        ai_difficulty = 'easy'
                        start = True
                        
                    elif medium_button_background.collidepoint(mouse_pos):
                        current_mode = 'versus-ai'
                        ai_difficulty = 'medium'
                        start = True

                    elif difficult_button_background.collidepoint(mouse_pos):
                        current_mode = 'versus-ai'
                        ai_difficulty = 'difficult'
                        start = True

                    if start:
                        pygame.mixer.Sound.play(click_sound)
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'versus-ai')
                        puzzle2 = DisplayPuzzle(current_difficulty, 250, screen, (850, 400), 'versus-ai', scramble=False, ai=True)
                        puzzle_list = three_by_three_puzzles if current_difficulty == 3 else four_by_four_puzzles
                        puzzle2.setState(deepcopy(puzzle_list[current_puzzle_index][0]))
                        ai_time_since_last_move = 1000
                        player_one_score = 0
                        player_two_score = 0
                        race_finished = False

                elif current_mode == 'time-trial':
                    if puzzle1.getGameWon() and puzzle1.getBoardRect().collidepoint(mouse_pos):
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'time-trial')

                    if time_trial_restart_button_background.collidepoint(mouse_pos):
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'time-trial')
                        pygame.mixer.Sound.play(click_sound)
                    elif time_trial_back_to_menu_button_background.collidepoint(mouse_pos):
                        current_mode = "main-menu"
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
                        pygame.mixer.Sound.play(click_sound)
                    elif time_trial_options_button_background.collidepoint(mouse_pos):
                        previous_mode = current_mode
                        current_mode = "options"
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'two-players':
                    if two_players_restart_button_background.collidepoint(mouse_pos):
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'two-players')
                        puzzle2 = DisplayPuzzle(current_difficulty, 550, screen, (550, 100), 'two-players')
                        race_finished = False
                        pygame.mixer.Sound.play(click_sound)
                    elif two_players_back_to_menu_button_background.collidepoint(mouse_pos):
                        current_mode = "main-menu"
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
                        pygame.mixer.Sound.play(click_sound)
                    elif two_players_options_button_background.collidepoint(mouse_pos):
                        previous_mode = current_mode
                        current_mode = "options"
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'tutorial':
                    if tutorial_instruction_button_background.collidepoint(mouse_pos):
                        screen.blit(instruction_display_background, instruction_display_background_rect)
                        displayTutorialInstruction()
                    elif tutorial_restart_button_background.collidepoint(mouse_pos):
                        puzzle1 = DisplayPuzzle(3, SCREEN_HEIGHT, screen, (0, 0), 'tutorial')
                        tutorial_phase = 0
                        pygame.mixer.Sound.play(click_sound)
                    elif tutorial_back_to_menu_button_background.collidepoint(mouse_pos):
                        current_mode = "main-menu"
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
                        pygame.mixer.Sound.play(click_sound)
                    elif tutorial_options_button_background.collidepoint(mouse_pos):
                        previous_mode = current_mode
                        current_mode = "options"
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'versus-ai':
                    if versus_ai_restart_button_background.collidepoint(mouse_pos):
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'versus-ai')
                        puzzle2 = DisplayPuzzle(current_difficulty, 250, screen, (850, 400), 'versus-ai', scramble=False, ai=True)
                        current_puzzle_index += 1
                        puzzle_list = three_by_three_puzzles if current_difficulty == 3 else four_by_four_puzzles
                        puzzle2.setState(deepcopy(puzzle_list[current_puzzle_index][0]))
                        ai_time_since_last_move = 1000
                        add_puzzle_thread = threading.Thread(target=lambda: addPuzzle(current_difficulty))
                        add_puzzle_thread.start()
                        race_finished = False
                        pygame.mixer.Sound.play(click_sound)
                    elif versus_ai_back_to_menu_button_background.collidepoint(mouse_pos):
                        current_mode = "main-menu"
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
                        initialise_ai_puzzles_thread = threading.Thread(target=initialiseAiPuzzles)
                        initialise_ai_puzzles_thread.start()
                        pygame.mixer.Sound.play(click_sound)
                    elif versus_ai_options_button_background.collidepoint(mouse_pos):
                        previous_mode = current_mode
                        current_mode = "options"
                        pygame.mixer.Sound.play(click_sound)

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if current_mode == 'options':
                    if music_slider.getDragging():
                        music_slider.setDragging(False)
                    elif sfx_slider.getDragging():
                        sfx_slider.setDragging(False)

            # key presses events
            elif event.type == pygame.KEYDOWN:
                if current_mode == 'main-menu':
                    if event.key == pygame.K_SPACE:
                        pygame.mixer.Sound.play(click_sound)
                        current_mode = 'play'  
                    elif event.key == pygame.K_o:
                        pygame.mixer.Sound.play(click_sound)
                        previous_mode = 'main-menu'
                        current_mode = 'options'

                elif current_mode == 'options':
                    if event.key == pygame.K_3:
                        current_difficulty = 3
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_4:
                        current_difficulty = 4
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_5:
                        if previous_mode != 'versus-ai':
                            current_difficulty = 5
                            pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_ESCAPE:
                        current_mode = previous_mode
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'play':
                    if event.key == pygame.K_1:
                        current_mode = 'time-trial'
                        pygame.mixer.Sound.play(click_sound)
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'time-trial')
                    elif event.key == pygame.K_2:
                        if current_difficulty != 5:
                            current_mode = 'choosing-difficulty'
                            pygame.mixer.Sound.play(click_sound)
                        else:
                            screen.blit(instruction_display_background, instruction_display_background_rect)
                            displayWarningScreen()
                    elif event.key == pygame.K_3:
                        current_mode = 'two-players'
                        player_one_score = 0
                        player_two_score = 0
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'two-players')
                        puzzle2 = DisplayPuzzle(current_difficulty, 550, screen, (550, 100), 'two-players')

                        score_label = medium_font.render(f'{player_one_score} vs {player_two_score}', False, WHITE)
                        score_rect = score_label.get_rect(center=(550, 75))
                        race_finished = False
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_4:
                        current_mode = 'tutorial'
                        tutorial_phase = 0
                        puzzle1 = DisplayPuzzle(3, SCREEN_HEIGHT, screen, (0, 0), 'tutorial')
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_ESCAPE:
                        current_mode = 'main-menu'
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'choosing-difficulty':
                    start = False
                    if event.key == pygame.K_1:
                        current_mode = 'versus-ai'
                        ai_difficulty = 'easy'
                        start = True
                        
                    elif event.key == pygame.K_2:
                        current_mode = 'versus-ai'
                        ai_difficulty = 'medium'
                        start = True

                    elif event.key == pygame.K_3:
                        current_mode = 'versus-ai'
                        ai_difficulty = 'difficult'
                        start = True

                    if start:
                        pygame.mixer.Sound.play(click_sound)
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'versus-ai')
                        puzzle2 = DisplayPuzzle(current_difficulty, 250, screen, (850, 400), 'versus-ai', scramble=False, ai=True)
                        puzzle_list = three_by_three_puzzles if current_difficulty == 3 else four_by_four_puzzles
                        puzzle2.setState(deepcopy(puzzle_list[current_puzzle_index][0]))
                        ai_time_since_last_move = 1000
                        player_one_score = 0
                        player_two_score = 0
                        race_finished = False

                if current_mode in ['time-trial', 'versus-ai', 'tutorial']:
                    if event.key == pygame.K_LEFT:
                        player_one_direction = 'left'
                    if event.key == pygame.K_RIGHT:
                        player_one_direction = 'right'
                    if event.key == pygame.K_UP:
                        player_one_direction = 'up'
                    if event.key == pygame.K_DOWN:
                        player_one_direction = 'down'

                    if event.key == pygame.K_r:
                        if current_mode == 'time-trial':
                            puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'time-trial')
                        elif current_mode == 'versus-ai':
                            puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'versus-ai')
                            puzzle2 = DisplayPuzzle(current_difficulty, 250, screen, (850, 400), 'versus-ai', scramble=False, ai=True)
                            current_puzzle_index += 1
                            puzzle_list = three_by_three_puzzles if current_difficulty == 3 else four_by_four_puzzles
                            puzzle2.setState(deepcopy(puzzle_list[current_puzzle_index][0]))
                            ai_time_since_last_move = 1000
                            add_puzzle_thread = threading.Thread(target=lambda: addPuzzle(current_difficulty))
                            add_puzzle_thread.start()
                            race_finished = False
                        elif current_mode == 'tutorial':
                            puzzle1 = DisplayPuzzle(3, SCREEN_HEIGHT, screen, (0, 0), 'tutorial')
                            tutorial_phase = 0
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_m:
                        current_mode = "main-menu"
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_o:
                        previous_mode = current_mode
                        current_mode = "options"
                        pygame.mixer.Sound.play(click_sound)

                elif current_mode == 'two-players':
                    if event.key == pygame.K_a:
                        player_one_direction = 'left'
                    if event.key == pygame.K_d:
                        player_one_direction = 'right'
                    if event.key == pygame.K_w:
                        player_one_direction = 'up'
                    if event.key == pygame.K_s:
                        player_one_direction = 'down'

                    if event.key == pygame.K_LEFT:
                        player_two_direction = 'left'
                    if event.key == pygame.K_RIGHT:
                        player_two_direction = 'right'
                    if event.key == pygame.K_UP:
                        player_two_direction = 'up'
                    if event.key == pygame.K_DOWN:
                        player_two_direction = 'down'

                    if event.key == pygame.K_r:
                        puzzle1 = DisplayPuzzle(current_difficulty, 550, screen, (0, 100), 'two-players')
                        puzzle2 = DisplayPuzzle(current_difficulty, 550, screen, (550, 100), 'two-players')
                        race_finished = False
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_m:
                        current_mode = "main-menu"
                        puzzle1 = DisplayPuzzle(current_difficulty, SCREEN_HEIGHT, screen, (0, 0), 'demo')
                        pygame.mixer.Sound.play(click_sound)
                    elif event.key == pygame.K_o:
                        previous_mode = current_mode
                        current_mode = "options"
                        pygame.mixer.Sound.play(click_sound)
                    
        screen.fill(BLACK)

        # displays the elements in main menu
        if current_mode == 'main-menu':
            updateDemo(deltatime)

            pygame.draw.rect(screen, WHITE, play_button_background, 3)
            screen.blit(play_button_text, play_button_rect)

            pygame.draw.rect(screen, WHITE, main_menu_options_button_background, 3)
            screen.blit(main_menu_options_button_text, main_menu_options_button_rect)

        # displays the elements in options menu
        elif current_mode == 'options':
            if music_slider.getDragging():
                music_slider.drag(pygame.mouse.get_pos()[0])
                music_volume = music_slider.getValue()
                pygame.mixer.music.set_volume(music_volume)
            if sfx_slider.getDragging():
                sfx_slider.drag(pygame.mouse.get_pos()[0])
                sfx_volume = sfx_slider.getValue()
                click_sound.set_volume(sfx_volume)
                slide_sound.set_volume(sfx_volume)
            
            screen.blit(options_label, options_label_rect)
            screen.blit(difficulty_label, difficulty_label_rect)
            
            screen.blit(three_by_three_button_text, three_by_three_button_rect)
            screen.blit(four_by_four_button_text, four_by_four_button_rect)

            five_by_five_button_text = big_font.render('5x5', False, WHITE if previous_mode != 'versus-ai' else DISABLED)
            five_by_five_button_rect = five_by_five_button_text.get_rect(center=(825, 250))
            screen.blit(five_by_five_button_text, five_by_five_button_rect)

            if current_difficulty == 3:
                pygame.draw.rect(screen, WHITE, three_by_three_button_background, 3)
            elif current_difficulty == 4:
                pygame.draw.rect(screen, WHITE, four_by_four_button_background, 3)
            else:
                pygame.draw.rect(screen, WHITE, five_by_five_button_background, 3)

            screen.blit(volumn_label, volumn_label_rect)
            screen.blit(music_label, music_label_rect)
            music_slider.draw()
            screen.blit(sfx_label, sfx_label_rect)
            sfx_slider.draw()

            pygame.draw.rect(screen, WHITE, return_button_background, 3)
            screen.blit(return_button_text, return_button_rect)

        # displays elements in play screen
        elif current_mode == 'play':
            updateDemo(deltatime)

            pygame.draw.rect(screen, WHITE, time_trial_button_background, 3)
            screen.blit(time_trial_button_text, time_trial_button_rect)

            pygame.draw.rect(screen, WHITE, versus_ai_button_background, 3)
            screen.blit(versus_ai_button_text, versus_ai_button_rect)

            pygame.draw.rect(screen, WHITE, two_players_button_background, 3)
            screen.blit(two_players_button_text, two_players_button_rect)

            pygame.draw.rect(screen, WHITE, tutorial_button_background, 3)
            screen.blit(tutorial_button_text, tutorial_button_rect)

            pygame.draw.rect(screen, WHITE, play_screen_back_to_menu_background, 3)
            screen.blit(play_screen_back_to_menu_button_text, player_screen_back_to_menu_button_rect)

        # displays elements in chossing difficulty screen
        elif current_mode == 'choosing-difficulty':
            updateDemo(deltatime)

            screen.blit(pick_a_difficulty_label, pick_a_difficulty_rect)

            pygame.draw.rect(screen, WHITE, easy_button_background, 3)
            screen.blit(easy_button_text, easy_button_rect)

            pygame.draw.rect(screen, WHITE, medium_button_background, 3)
            screen.blit(medium_button_text, medium_button_rect)

            pygame.draw.rect(screen, WHITE, difficult_button_background, 3)
            screen.blit(difficult_button_text, difficult_button_rect)

        # displays elements in time trial mode
        elif current_mode == 'time-trial':
            puzzle1.update(player_one_direction, deltatime)
            screen.blit(time_trial_best_time_label, time_trial_best_time_rect)

            best_time_text = big_font.render(formatTime(best_time[puzzle1.getDifficulty()]), False, WHITE)
            best_time_text_rect = best_time_text.get_rect(topleft=(775, 160))
            screen.blit(best_time_text, best_time_text_rect)
            
            screen.blit(time_trial_time_label, time_trial_time_rect)

            if not puzzle1.getGameWon():
                time_passed = pygame.time.get_ticks() - puzzle1.getCreationTime()
                time_label = big_font.render(formatTime(time_passed), False, WHITE)
                time_rect = time_label.get_rect(topleft=(775, 285))
            elif not puzzle1.getCheckedAgainstBestTime():
                if best_time[puzzle1.getDifficulty()] == None :
                    best_time[puzzle1.getDifficulty()] = time_passed
                elif time_passed < best_time[puzzle1.getDifficulty()]:
                    best_time[puzzle1.getDifficulty()] = time_passed
                puzzle1.setCheckedAgainstBestTime(True)
        
            screen.blit(time_label, time_rect)
            screen.blit(time_trial_move_label, time_trial_move_rect)

            move_label = big_font.render(f'{puzzle1.getMoves()}', False, WHITE)
            move_rect = move_label.get_rect(topleft=(775, 410))
            screen.blit(move_label, move_rect)

            pygame.draw.rect(screen, WHITE, time_trial_restart_button_background, 3)
            screen.blit(time_trial_restart_button_text, time_trial_restart_button_rect)

            pygame.draw.rect(screen, WHITE, time_trial_back_to_menu_button_background, 3)
            screen.blit(time_trial_back_to_menu_button_text, time_trial_back_to_menu_button_rect)

            pygame.draw.rect(screen, WHITE, time_trial_options_button_background, 3)
            screen.blit(time_trial_options_button_text, time_trial_options_button_rect)

        # displays elements in two players mode
        elif current_mode == 'two-players':
            puzzle1.update(player_one_direction, deltatime)
            puzzle2.update(player_two_direction, deltatime)
            if (puzzle1.getGameWon() or puzzle2.getGameWon()) and not race_finished:
                puzzle1.setRaceFinished(True)
                puzzle2.setRaceFinished(True)
                race_finished = True

                if puzzle1.getGameWon():
                    player_one_score += 1
                else:
                    player_two_score += 1

                score_label = medium_font.render(f'{player_one_score} vs {player_two_score}', False, WHITE)
                score_rect = score_label.get_rect(center=(550, 75))
            
            if not race_finished:
                time_passed = pygame.time.get_ticks()
                time_string = formatTime(time_passed - puzzle1.getCreationTime())
                time_label = small_font.render(f'Time: {time_string}', False, WHITE)
                time_rect = time_label.get_rect(topleft=(450, 20))

            screen.blit(player_one_label, player_one_rect)
            screen.blit(player_two_label, player_two_rect)
            screen.blit(score_label, score_rect)

            pygame.draw.rect(screen, WHITE, two_players_restart_button_background, 3)
            screen.blit(two_players_restart_button_text, two_players_restart_button_rect)

            pygame.draw.rect(screen, WHITE, two_players_back_to_menu_button_background, 3)
            screen.blit(two_players_back_to_menu_button_text, two_players_back_to_menu_button_rect)

            pygame.draw.rect(screen, WHITE, two_players_options_button_background, 3)
            screen.blit(two_players_options_button_text, two_players_options_button_rect)

            screen.blit(time_label, time_rect)

        # displays elements in tutorial mode
        elif current_mode == 'tutorial':
            puzzle1.update(player_one_direction, deltatime)

            pygame.draw.rect(screen, WHITE, tutorial_instruction_button_background, 3)
            screen.blit(tutorial_instruction_button_text, tutorial_instruction_button_rect)

            pygame.draw.rect(screen, WHITE, tutorial_restart_button_background, 3)
            screen.blit(tutorial_restart_button_text, tutorial_restart_button_rect)

            pygame.draw.rect(screen, WHITE, tutorial_back_to_menu_button_background, 3)
            screen.blit(tutorial_back_to_menu_button_text, tutorial_back_to_menu_button_rect)

            pygame.draw.rect(screen, WHITE, tutorial_options_button_background, 3)
            screen.blit(tutorial_options_button_text, tutorial_options_button_rect)

            screen.blit(objective_label, objective_rect)

            # handles what objectives to display at different phases of the tutorial
            if tutorial_phase == 0:
                screen.blit(instruction_display_background, instruction_display_background_rect)
                displayTutorialInstruction()
                tutorial_phase += 1
            elif tutorial_phase == 1:
                if not instruction_displayed:
                    screen.blit(instruction_display_background, instruction_display_background_rect)
                    displayTutorialInstruction()
                    instruction_displayed = True

                objective_progress_label = small_font.render(f'{puzzle1.getMoves()}/5', False, WHITE)
                objective_progress_rect = objective_progress_label.get_rect(topleft=(775, 150))
                screen.blit(phase_one_objective_label, phase_one_objective_rect)
                screen.blit(objective_progress_label, objective_progress_rect)

                if puzzle1.getMoves() == 5 and not puzzle1.getAnimating():
                    tutorial_phase += 1
                    instruction_displayed = False
            elif tutorial_phase == 2:
                if not instruction_displayed:
                    screen.blit(instruction_display_background, instruction_display_background_rect)
                    displayTutorialInstruction()
                    instruction_displayed = True

                objective_progress_label = small_font.render(f'0/1', False, WHITE)
                objective_progress_rect = objective_progress_label.get_rect(topleft=(775, 190))
                screen.blit(phase_two_objective_label1, phase_two_objective_rect1)
                screen.blit(phase_two_objective_label2, phase_two_objective_rect2)
                screen.blit(objective_progress_label, objective_progress_rect)

                if puzzle1.layerOnePatternMade() and not puzzle1.getAnimating():
                    tutorial_phase += 1
                    instruction_displayed = False
            elif tutorial_phase == 3:
                if not instruction_displayed:
                    screen.blit(instruction_display_background, instruction_display_background_rect)
                    displayTutorialInstruction()
                    instruction_displayed = True

                objective_progress_label = small_font.render(f'0/1', False, WHITE)
                objective_progress_rect = objective_progress_label.get_rect(topleft=(775, 190))
                screen.blit(phase_three_objective_label1, phase_three_objective_rect1)
                screen.blit(phase_three_objective_label2, phase_three_objective_rect2)
                screen.blit(objective_progress_label, objective_progress_rect)

                if puzzle1.firstLayerSolved() and not puzzle1.getAnimating():
                    tutorial_phase += 1
                    instruction_displayed = False
            elif tutorial_phase == 4:
                if not instruction_displayed:
                    screen.blit(instruction_display_background, instruction_display_background_rect)
                    displayTutorialInstruction()
                    instruction_displayed = True

                objective_progress_label = small_font.render(f'0/1', False, WHITE)
                objective_progress_rect = objective_progress_label.get_rect(topleft=(775, 190))
                screen.blit(phase_four_objective_label1, phase_four_objective_rect1)
                screen.blit(phase_four_objective_label2, phase_four_objective_rect2)
                screen.blit(objective_progress_label, objective_progress_rect)

                if puzzle1.getGameWon() and not puzzle1.getAnimating():
                    tutorial_phase += 2
                    instruction_displayed = False
                elif puzzle1.secondLayerSolved() and not puzzle1.getAnimating():
                    tutorial_phase += 1
                    instruction_displayed = False
            elif tutorial_phase == 5:
                if not instruction_displayed:
                    screen.blit(instruction_display_background, instruction_display_background_rect)
                    displayTutorialInstruction()
                    instruction_displayed = True

                objective_progress_label = small_font.render(f'0/1', False, WHITE)
                objective_progress_rect = objective_progress_label.get_rect(topleft=(775, 150))
                screen.blit(phase_five_objective_label, phase_five_objective_rect)
                screen.blit(objective_progress_label, objective_progress_rect)

                if puzzle1.getGameWon() and puzzle1.getAnimating():
                    tutorial_phase += 2
                    instruction_displayed = False
            elif tutorial_phase == 6:
                screen.blit(instruction_display_background, instruction_display_background_rect)
                displayTutorialInstruction()
                tutorial_phase += 1
            elif tutorial_phase == 7:
                if not instruction_displayed:
                    screen.blit(instruction_display_background, instruction_display_background_rect)
                    displayTutorialInstruction()
                    instruction_displayed = True
            
                objective_progress_label = small_font.render(f'1/1', False, WHITE)
                objective_progress_rect = objective_progress_label.get_rect(topleft=(775, 150))
                screen.blit(phase_five_objective_label, phase_five_objective_rect)
                screen.blit(objective_progress_label, objective_progress_rect)

        # displays the elements in the versus A.I. mode
        elif current_mode == 'versus-ai':
            if current_puzzle_index == 0 and update_ai_puzzle and not updating:
                updating = True
                update_puzzle_thread = threading.Thread(target=lambda: updatePuzzles(current_difficulty))
                update_puzzle_thread.start()

            puzzle1.update(player_one_direction, deltatime)

            ai_time_since_last_move += deltatime
            moved = False
            if ai_time_since_last_move >= AI_WAIT_TIME[ai_difficulty] and not race_finished:
                puzzle_list = three_by_three_puzzles if current_difficulty == 3 else four_by_four_puzzles
                move_list = puzzle_list[current_puzzle_index][2]
                if move_list:
                    moved = True
                    puzzle2.update(move_list.pop(0), deltatime)
                    ai_time_since_last_move = 0
            
            if not moved:
                puzzle2.update(None, deltatime)

            if (puzzle1.getGameWon() or puzzle2.getGameWon()) and not race_finished:
                puzzle1.setRaceFinished(True)
                puzzle2.setRaceFinished(True)
                race_finished = True

                if puzzle1.getGameWon():
                    player_one_score += 1
                    if best_time[puzzle1.getDifficulty()] == None :
                        best_time[puzzle1.getDifficulty()] = time_passed
                    elif time_passed < best_time[puzzle1.getDifficulty()]:
                        best_time[puzzle1.getDifficulty()] = time_passed
                    puzzle1.setCheckedAgainstBestTime(True)
                else:
                    player_two_score += 1

            if not race_finished:
                time_passed = pygame.time.get_ticks() - puzzle1.getCreationTime()
                time_label = big_font.render(formatTime(time_passed), False, WHITE)
                time_rect = time_label.get_rect(topleft=(675, 235))

            pygame.draw.rect(screen, WHITE, versus_ai_restart_button_background, 3)
            screen.blit(versus_ai_restart_button_text, versus_ai_restart_button_rect)

            pygame.draw.rect(screen, WHITE, versus_ai_back_to_menu_button_background, 3)
            screen.blit(versus_ai_back_to_menu_button_text, versus_ai_back_to_menu_button_rect)

            pygame.draw.rect(screen, WHITE, versus_ai_options_button_background, 3)
            screen.blit(versus_ai_options_button_text, versus_ai_options_button_rect)

            screen.blit(players_game_label, players_game_rect)
            screen.blit(ai_games_label, ai_games_rect)

            screen.blit(versus_ai_best_time_label, versus_ai_best_time_rect)
            best_time_text = big_font.render(formatTime(best_time[puzzle1.getDifficulty()]), False, WHITE)
            best_time_text_rect = best_time_text.get_rect(topleft=(675, 110))
            screen.blit(best_time_text, best_time_text_rect)
            screen.blit(versus_ai_time_label, versus_ai_time_rect)
            screen.blit(time_label, time_rect)

            player_score_label = big_font.render(f'{player_one_score}', False, WHITE)
            player_score_rect = player_score_label.get_rect(topleft=(575, 450))

            ai_score_label = big_font.render(f'{player_two_score}', False, WHITE)
            ai_score_rect = ai_score_label.get_rect(topright=(830, 555))

            screen.blit(versus_ai_score_label, versus_ai_score_rect)
            screen.blit(player_score_label, player_score_rect)
            screen.blit(versus_label, versus_rect)
            screen.blit(ai_score_label, ai_score_rect)

        pygame.display.update()

# variables used for displaying instructions
instruction_surface_width = SCREEN_WIDTH - 200
instruction_surface_height = SCREEN_HEIGHT - 200
instruction_display_surface = pygame.Surface((instruction_surface_width, instruction_surface_height))
instruction_display_surface_rect = instruction_display_surface.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

instruction_label = big_font.render('Instruction:', False, WHITE)
instruction_label_rect = instruction_label.get_rect(center=(instruction_surface_width/2, 40))

instruction_button_background = pygame.Rect(345, 490, 200, 50)
next_button_text = medium_font.render('Next', False, WHITE)
next_button_rect = next_button_text.get_rect(center=(instruction_surface_width/2, 521))

got_it_button_text = medium_font.render('Got it', False, WHITE)
got_it_button_rect = got_it_button_text.get_rect(center=(instruction_surface_width/2, 521))

instruction_texts = ['''Welcome to Number Slider! This game is played on a square grid, and the goal is to get the number arranged
                        in order from left to right, up to down. The solved state of the puzzle is shown on the right. I hope you
                        will have fun with the game!''',
                     '''In all the single player modes, you will control the puzzle by pressing the arrow keys. In the two players 
                        race mode, the puzzle of the left side is controlled with WASD keys and the one on the right will be controlled
                         with arrow keys. Let's first try move the puzzle around 5 times!''',
                     '''Next, we will learn how to solve the puzzle. In this tutorial, we will take a layer by layer approach, so
                        let's start with the first layer. If you try and approach this without any strategies, you will notice that
                        it is very difficult to get the three pieces in order up top. The tip is to first place 2 and 3 in the top left
                        and middle position, and then place 1 below 2. This pattern is shown on the right''',
                     '''Now that you have created this pattern, put the empty tile on the top right corner. Then you can slide the whole 
                        layer into their right positions just like how it is shown in the animation.''',
                     '''It's time to move on to the second layer. Our approach is very similar, first create a similar pattern, place
                        the empty tile in the middle right, and slide the layer right in! You can always look at the animation for
                        reference.''',
                     '''Great Job! Now the rest of the puzzle is really straightforward, go and finish it!''',
                     '''Great Job! Looks like you have solved the whole puzzle along with the second layer, but in case you didn't 
                        the last layer is extremely simple to solve and there really isn't much instruction needed.''',
                     '''Congratulations on solving the puzzle! I hope you now have a solid grasp of how to solve these puzzles. If
                        you are unsure about any parts of the tutorial, you can always redo it and see if you get any new insights.
                        Next up, you can try solving some 3x3 puzzles by your own! Or if you feel like it, challenge yourself to the
                        4x4 and 5x5 difficulties by switching them up in the options menu. If you are competitive, race against a friend
                        or our A.I. player and see who is victorious!''']
instruction_lines = []
instruction_rects = []

# convert the instructions into individual text labels to display on screen
max_line_width = 580
for texts in instruction_texts:
    words = texts.split()
    lines = []
    current_line = words[0]
    for word in words[1:]:
        test_line = current_line + "  " + word
        test_width, _ = small_font.size(test_line)

        if test_width <= max_line_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)

    current_lines = []
    current_rects = []
    line_y_position = 100
    for line in lines:
        rendered_line = small_font.render(line, False, WHITE)
        current_lines.append(rendered_line)
        current_rects.append(rendered_line.get_rect(topleft=(30, line_y_position)))
        line_y_position += small_font.get_linesize() + 5

    instruction_lines.append(current_lines)
    instruction_rects.append(current_rects)

# thread to intialise the animations for the first two phases of the animation
def initialiseAnimations() -> None:
    global animations
    animations = [Animation([None],
                            [[1, 2, 3],
                            [4, 5, 6],
                            [7, 8, 0]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False)),
                Animation(['right', 'down', 'left', 'up'],
                            [[1, 2, 3],
                            [4, 5, 6],
                            [7, 8, 0]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False))]
    
# thread to initialise the rest of the animations for the tutorial mode
def addAnimations() -> None:
    global animations
    new_animations = [Animation([None],
                            [[2, 3, 0],
                            [1, 6, 8],
                            [5, 4, 7]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False)),
                Animation(['right', 'right', 'up'],
                            [[2, 3, 0],
                            [1, 6, 8],
                            [5, 4, 7]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False)),
                Animation(['right', 'right', 'up'],
                            [[1, 2, 3],
                            [5, 6, 0],
                            [4, 7, 8]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False)),
                Animation(['right', 'right', 'left', 'left'],
                            [[1, 2, 3],
                            [4, 5, 6],
                            [7, 8, 0]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False)),
                Animation(['right', 'right', 'left', 'left'],
                            [[1, 2, 3],
                            [4, 5, 6],
                            [7, 8, 0]],
                            DisplayPuzzle(3, 250, instruction_display_surface, (625, 150), 'instructions', False)),
                Animation(['down', 'right', 'up', 'left'],
                            [[1, 2, 3, 4],
                            [5, 6, 7, 8],
                            [9, 10, 11, 12],
                            [13, 14, 15, 0]],
                            DisplayPuzzle(4, 250, instruction_display_surface, (625, 150), 'instructions', False))]
    animations += new_animations
    
initialise_animations_thread = threading.Thread(target=initialiseAnimations)
initialise_animations_thread.start()

objectives_in_phase = [False, True, True, True, True, True, False, True]

# displays the instruction on screen and wait for the player to press the button
def displayTutorialInstruction() -> None:
    previous_frame_time = pygame.time.get_ticks()
    current_frame_time = pygame.time.get_ticks()
        
    while True:
        current_frame_time = pygame.time.get_ticks()
        deltatime = current_frame_time - previous_frame_time
        previous_frame_time = current_frame_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data = {
                    'music_volume': music_volume,
                    'sfx_volume': sfx_volume,
                    'best_time': best_time,
                    'current_difficulty': current_difficulty
                }

                with open('data.pkl', 'wb') as file:
                     pickle.dump(data, file)

                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = (event.pos[0] - 100, event.pos[1] - 100)
                if instruction_button_background.collidepoint(mouse_pos):
                    return

        screen.blit(instruction_display_surface, instruction_display_surface_rect)

        instruction_display_surface.fill(GREY)
        instruction_display_surface.blit(instruction_label, instruction_label_rect)
        pygame.draw.rect(instruction_display_surface, WHITE, instruction_button_background, 3)
        if objectives_in_phase[tutorial_phase]:
            instruction_display_surface.blit(got_it_button_text, got_it_button_rect)
        else:
            instruction_display_surface.blit(next_button_text, next_button_rect)

        for index in range(len(instruction_lines[tutorial_phase])):
            instruction_display_surface.blit(instruction_lines[tutorial_phase][index], instruction_rects[tutorial_phase][index])
        animations[tutorial_phase].update(deltatime)

        pygame.display.update()

# displays the warning screen and wait for the player to press the button
def displayWarningScreen() -> None:
    warning_label = big_font.render('Warning!', False, WHITE)
    warning_rect = warning_label.get_rect(center=(instruction_surface_width/2, 60))

    warning_msg = medium_font.render('5x5 is not supported in this mode', False, WHITE)
    warning_msg_rect = warning_msg.get_rect(center=(instruction_surface_width/2, 250))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                data = {
                    'music_volume': music_volume,
                    'sfx_volume': sfx_volume,
                    'best_time': best_time,
                    'current_difficulty': current_difficulty
                }

                with open('data.pkl', 'wb') as file:
                     pickle.dump(data, file)

                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = (event.pos[0] - 100, event.pos[1] - 100)
                if instruction_button_background.collidepoint(mouse_pos):
                    return

        screen.blit(instruction_display_surface, instruction_display_surface_rect)

        instruction_display_surface.fill(GREY)
        instruction_display_surface.blit(warning_label, warning_rect)
        instruction_display_surface.blit(warning_msg, warning_msg_rect)
        pygame.draw.rect(instruction_display_surface, WHITE, instruction_button_background, 3)
        instruction_display_surface.blit(got_it_button_text, got_it_button_rect)

        pygame.display.update()

# calls the main function
if __name__ == '__main__':
    main()