import pygame
import sys
import random

# Button class for the home screen
class Button:
    def __init__(
        self, x, y, width, height, text,
        color=(70, 130, 180),
        hover_color=(100, 160, 210),
        selected_color=(180, 60, 60)  # 🔴 red when chosen
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.selected_color = selected_color

        self.current_color = color
        self.selected = False

        self.font = pygame.font.SysFont("consolas", 24)

    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (240, 240, 240), self.rect, 2, border_radius=10)

        text_surf = self.font.render(self.text, True, (240, 240, 240))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_hovered(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, pos):
        if self.selected:
            self.current_color = self.selected_color
        elif self.is_hovered(pos):
            self.current_color = self.hover_color
        else:
            self.current_color = self.color

    def is_clicked(self, pos, event):
        return (
            self.is_hovered(pos)
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        )

# Home screen class
class HomeScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.running = True
        self.selected_difficulty = "EASY"
        self.start_game = False
        
        # Calculate center positions
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        # Create buttons
        button_width = 200
        button_height = 50
        button_spacing = 20
        
        self.easy_button = Button(
            center_x - button_width // 2,
            center_y - button_height - button_spacing,
            button_width, button_height, "EASY"
        )
        
        self.medium_button = Button(
            center_x - button_width // 2,
            center_y,
            button_width, button_height, "MEDIUM"
        )
        
        self.hard_button = Button(
            center_x - button_width // 2,
            center_y + button_height + button_spacing,
            button_width, button_height, "HARD"
        )
        
        # Start button (only enabled after selecting difficulty)
        self.start_button = Button(
            center_x - button_width // 2,
            center_y + 2 * (button_height + button_spacing),
            button_width, button_height, "START GAME", 
            color=(60, 180, 75), hover_color=(80, 200, 95)
        )
        
        # Title font
        self.title_font = pygame.font.SysFont("consolas", 48, bold=True)
        self.subtitle_font = pygame.font.SysFont("consolas", 20)
        
        # Background effect variables
        self.particles = []
        self.last_particle = 0
        self.particle_timer = 0
        
    def generate_particles(self):
        # Create ghost-like particles for background effect
        for _ in range(3):
            particle = {
                'x': random.randint(0, self.screen_width),
                'y': random.randint(0, self.screen_height),
                'size': random.randint(2, 8),
                'speed': random.uniform(0.1, 0.5),
                'alpha': random.randint(50, 150),
                'color': (random.randint(150, 220), random.randint(80, 150), random.randint(180, 220))
            }
            self.particles.append(particle)
    
    def update_particles(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_particle > 100:  # Add new particles every 100ms
            self.generate_particles()
            self.last_particle = current_time
            
        # Update existing particles
        for particle in self.particles[:]:
            particle['y'] -= particle['speed']
            particle['alpha'] -= 0.5
            
            if particle['alpha'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self, screen):
        for particle in self.particles:
            alpha_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, 
                             (*particle['color'], int(particle['alpha'])), 
                             (particle['size'], particle['size']), 
                             particle['size'])
            screen.blit(alpha_surface, (particle['x'], particle['y']))
    
    def run(self, screen):
        while self.running and not self.start_game:
            mouse_pos = pygame.mouse.get_pos()
            
            # Update button states
            self.easy_button.update(mouse_pos)
            self.medium_button.update(mouse_pos)
            self.hard_button.update(mouse_pos)
            self.start_button.update(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        return None
                
                # Check button clicks
                if self.easy_button.is_clicked(mouse_pos, event):
                    self.selected_difficulty = "EASY"
                    self.easy_button.selected = True
                    self.medium_button.selected = False
                    self.hard_button.selected = False

                elif self.medium_button.is_clicked(mouse_pos, event):
                    self.selected_difficulty = "MEDIUM"
                    self.easy_button.selected = False
                    self.medium_button.selected = True
                    self.hard_button.selected = False

                elif self.hard_button.is_clicked(mouse_pos, event):
                    self.selected_difficulty = "HARD"
                    self.easy_button.selected = False
                    self.medium_button.selected = False
                    self.hard_button.selected = True

                elif self.start_button.is_clicked(mouse_pos, event) and self.selected_difficulty:
                    self.start_game = True
            
            # Update background particles
            self.update_particles()
            
            # Draw everything
            screen.fill((15, 15, 25))  # Dark blue background
            
            # Draw particles
            self.draw_particles(screen)
            
            # Draw title
            title = self.title_font.render("EXORCIZE", True, (220, 180, 240))
            title_rect = title.get_rect(center=(self.screen_width // 2, 100))
            screen.blit(title, title_rect)
            
            # Draw subtitle
            subtitle = self.subtitle_font.render("A Spectral Pursuit", True, (180, 200, 220))
            subtitle_rect = subtitle.get_rect(center=(self.screen_width // 2, 150))
            screen.blit(subtitle, subtitle_rect)
            
            
            # Draw buttons
            self.easy_button.draw(screen)
            self.medium_button.draw(screen)
            self.hard_button.draw(screen)
            self.start_button.draw(screen)
            
            pygame.display.flip()
            pygame.time.Clock().tick(60)
        
        if self.start_game:
            return self.selected_difficulty
        return None