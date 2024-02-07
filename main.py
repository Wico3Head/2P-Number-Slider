from setting import *
import pygame, sys, os
from displayPuzzle import DisplayPuzzle
from slider import Slider
pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('2P Number Slider')
pygame.display.set_icon(pygame.image.load(os.path.join(LOCAL_DIR, 'Assets/Tile1.png')))

music_volume = 0
sfx_volume = 0.5

pygame.mixer.music.load(os.path.join(LOCAL_DIR, 'Assets/bgmusic.mp3'))
click_sound = pygame.mixer.Sound(os.path.join(LOCAL_DIR, 'Assets/click.ogg'))
slide_sound = pygame.mixer.Sound(os.path.join(LOCAL_DIR, 'Assets/slide.wav'))
pygame.mixer.music.set_volume(music_volume)
click_sound.set_volume(sfx_volume)
slide_sound.set_volume(sfx_volume)
pygame.mixer.music.play(-1)

puzzle = DisplayPuzzle(4, SCREEN_HEIGHT, screen, (0, 0))
current_mode = 'main-menu'
time_since_last_demo_move = 0
previous_frame_time = pygame.time.get_ticks()

# main menu buttons and labels
title_card_line_one = big_font.render('Two Player', False, WHITE)
title_card_line_one_rect = title_card_line_one.get_rect(center=(880, 100))

title_card_line_two = big_font.render('Number Slider', False, WHITE)
title_card_line_two_rect = title_card_line_two.get_rect(center=(945, 160))

play_button_background = pygame.Rect(800, 530, 250, 45)
play_button_text = small_font.render('play', False, WHITE)
play_button_rect = play_button_text.get_rect(center=(925, 555))

options_button_background = pygame.Rect(800, 600, 250, 45)
options_button_text = small_font.render('options', False, WHITE)
options_button_rect = options_button_text.get_rect(center=(925, 625))

# options menu buttons, labels and sliders
slider = Slider(screen, 0, 1, (550, 150), 750, 40, 50, 100, 2, sfx_volume)

def main():
    global time_since_last_demo_move, previous_frame_time, current_mode

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if current_mode == 'main-menu':
                    if play_button_background.collidepoint(mouse_pos):
                        pygame.mixer.Sound.play(click_sound)
                        print('play mode')
                    elif options_button_background.collidepoint(mouse_pos):
                        pygame.mixer.Sound.play(click_sound)
                        current_mode = 'options'
                if current_mode == 'options':
                    if slider.mouseOnKnob(mouse_pos):
                        slider.dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and slider.dragging:
                slider.dragging = False

        screen.fill(BLACK)
        if current_mode == 'main-menu':
            current_frame_time = pygame.time.get_ticks()
            time_since_last_demo_move += current_frame_time - previous_frame_time
            previous_frame_time = current_frame_time

            screen.blit(title_card_line_one, title_card_line_one_rect)
            screen.blit(title_card_line_two, title_card_line_two_rect)

            pygame.draw.rect(screen, WHITE, play_button_background, 3)
            screen.blit(play_button_text, play_button_rect)

            pygame.draw.rect(screen, WHITE, options_button_background, 3)
            screen.blit(options_button_text, options_button_rect)

            if time_since_last_demo_move > 500:
                puzzle.update(puzzle.getDemoMove(), 5)
                time_since_last_demo_move = 0
            else:
                puzzle.update(None, 5)

        elif current_mode == 'options':
            slider.draw()
            if slider.dragging:
                slider.drag(pygame.mouse.get_pos()[0])

        pygame.display.update()

if __name__ == '__main__':
    main()