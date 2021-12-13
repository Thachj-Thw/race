# python 3.9
import pygame
from random import randint
import time
import sys

# color
RED = (255, 0, 0)
GRAY = (192, 192, 192)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 250)
BLACK = (0, 0, 0)


class MysteryBox:
    def __init__(self, start: tuple):
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 236, 64))
        icon = pygame.font.SysFont("sans", 15, bold=True).render("?", True, WHITE)
        self.image.blit(icon, icon.get_rect(center=(10, 10)))
        self.x_box = start[0] + randint(150, 250)
        self.y_box = start[1]
        self.mystery_num = randint(1, 1000)
        self.hit = False

    def new(self, x: int = None):
        if x is None:
            self.x_box = self.x_box + randint(150, 250)
        else:
            self.x_box = x + randint(150, 250)
        self.mystery_num = randint(1, 1000)
        self.hit = False

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, (self.x_box, self.y_box))


class RaceCar(pygame.sprite.Sprite):
    def __init__(self, master, image, lane: int):
        super().__init__()
        self.master = master
        self.image = image
        self.x = 0
        self.y = int(lane/5 * 2/3 * self.master.get_height() + self.master.get_height()/3)
        self.size = image.get_size()
        self.rect = pygame.Rect((self.x, self.y), self.size)
        self.speed = randint(6, 8)
        self.ID = lane
        self.finished = False
        self.box = MysteryBox((self.x, self.y))
        self.flip = False
        self.timer = None

    def reset(self):
        self.rect.x = 0
        self.finished = False
        self.speed = randint(6, 8)
        self.box.new(0)
        if self.flip:
            self.image = pygame.transform.flip(self.image, True, False)
        self.flip = False
        self.timer = None

    def is_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.x < mouse_pos[0] < self.rect.x + self.size[0] and self.y < mouse_pos[1] < self.y + self.size[1]

    def update(self):
        if not self.finished:
            self.rect.x = max(0, min(self.rect.x + self.speed, self.master.get_width() - self.size[0]))
            if self.rect.x >= self.box.x_box - self.size[0]//4:
                self.box.hit = True
            if self.box.hit:
                if self.box.mystery_num == 1000:
                    self.speed = 30
                elif self.box.mystery_num == 1:
                    self.speed = -30
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.flip = True
                elif self.box.mystery_num in range(2, 250):
                    self.speed += 2
                    self.box.new()
                elif self.box.mystery_num in range(250, 500):
                    self.speed = max(self.speed - 2, 1)
                    self.box.new()
                elif self.box.mystery_num in range(500, 750):
                    self.speed = 0
                    if not self.timer:
                        self.timer = time.perf_counter()
                    if time.perf_counter() - self.timer > 0.3:
                        self.speed = randint(6, 8)
                        self.box.new()
                        self.timer = None
                elif self.box.mystery_num in range(750, 1000):
                    self.speed = -1
                    if not self.timer:
                        self.timer = time.perf_counter()
                    if time.perf_counter() - self.timer > 0.2:
                        self.speed = randint(6, 8)
                        self.box.new()
                        self.timer = None
            else:
                self.box.draw(self.master)


class Button(pygame.sprite.Sprite):
    def __init__(self, rect: tuple, font , text, amount):
        super().__init__()
        self.font = font
        text_surf = self.font.render(text, True, (0, 0, 0))
        self.x = rect[0]
        self.y = rect[1]
        self.width = rect[2]
        self.height = rect[3]
        self.size = (rect[2], rect[3])
        self.button_image = pygame.Surface(self.size)
        self.button_image.fill((96, 96, 96))
        self.button_image.blit(text_surf, text_surf.get_rect(center=(self.width // 2, self.height // 2)))
        self.hover_image = pygame.Surface(self.size)
        self.hover_image.fill((96, 96, 96))
        self.hover_image.blit(text_surf, text_surf.get_rect(center=(self.width // 2, self.height // 2)))
        pygame.draw.rect(self.hover_image, (96, 196, 96), self.hover_image.get_rect(), 3)
        self.clicked_image = pygame.Surface(self.size)
        self.clicked_image.fill((96, 196, 96))
        self.clicked_image.blit(text_surf, text_surf.get_rect(center=(self.width // 2, self.height // 2)))
        self.image = self.button_image
        self.rect = pygame.Rect(*rect)
        self.clicked = False
        self.amount = amount

    def check_mouse_click(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            return self

    def update(self):
        if self.clicked:
            self.image = self.clicked_image
        elif self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = self.hover_image
        else:
            self.image = self.button_image


class Game:
    def __init__(self, master: pygame.Surface):
        self.screen = master
        self.money = 400
        # Font
        self.font_sans_30 = pygame.font.SysFont("sans", 30)
        self.font_sans_20 = pygame.font.SysFont("sans", 20)
        # Images background
        size = list(self.screen.get_size())
        size[1] -= self.screen.get_height()//3 - 47
        self.racetrack_bg = pygame.transform.scale(pygame.image.load("images/racetrack.png"), size)
        self.bg = pygame.transform.scale(pygame.image.load("images/background.jpg"), self.screen.get_size())
        # Images horse
        img_size = (int(self.screen.get_width() * 0.1), int(self.screen.get_height()/20))
        img_horse0 = pygame.transform.scale(pygame.image.load("images/img1.png"), img_size)
        img_horse1 = pygame.transform.scale(pygame.image.load("images/img2.png"), img_size)
        img_horse2 = pygame.transform.scale(pygame.image.load("images/img3.png"), img_size)
        img_horse3 = pygame.transform.scale(pygame.image.load("images/img4.png"), img_size)
        img_horse4 = pygame.transform.scale(pygame.image.load("images/img5.png"), img_size)
        # Horses
        self.horses = [
            RaceCar(master=self.screen, image=img_horse0, lane=0),
            RaceCar(master=self.screen, image=img_horse1, lane=1),
            RaceCar(master=self.screen, image=img_horse2, lane=2),
            RaceCar(master=self.screen, image=img_horse3, lane=3),
            RaceCar(master=self.screen, image=img_horse4, lane=4)
        ]
        self.group_horse = pygame.sprite.Group(self.horses)
        # Button bet
        x, y, s = 20, 70, 120
        self.bet_level = [
            Button((x, y, 70, 50), self.font_sans_30, "100", 100),
            Button((x + s, y, 70, 50), self.font_sans_30, "200", 200),
            Button((x + 2*s, y, 70, 50), self.font_sans_30, "500", 500),
            Button((x + 3*s, y, 70, 50), self.font_sans_30, "Half", self.money/2),
            Button((x + 4*s, y, 70, 50), self.font_sans_30, "All-in", self.money)
        ]
        self.group_buttons = pygame.sprite.Group(self.bet_level)

        self.status = self.font_sans_30.render("Choose your bet", True, WHITE)
        self.message = ""
        self.bet = 0
        self.select = None
        self.clock = pygame.time.Clock()
        self.fps = 60
    
    def restart(self):
        for horse in self.horses:
            horse.reset()
        for button in self.bet_level:
            button.clicked = False
        self.bet_level[-1].amount = self.money
        self.bet_level[-2].amount = self.money/2
        self.message = "Choose your bet"
        self.bet = 0
        self.select = None
        pygame.display.set_mode(self.screen.get_size(), pygame.RESIZABLE)

    def change_status(self, text: str, color: tuple):
        self.status = self.font_sans_30.render(text, True, color)

    def draw_taskbar(self):
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.status, (20, 5))
        self.screen.blit(self.font_sans_20.render(self.message, True, RED), (650, 75))
        text = self.font_sans_30.render(f"You currently have: {self.money:.2f}$", True, WHITE)
        self.screen.blit(text, (self.screen.get_width() - text.get_width() - 50, 5))
        self.group_buttons.draw(self.screen)
        self.group_buttons.update()

    def update_size(self):
        size = list(self.screen.get_size())
        size[1] -= self.screen.get_height() // 3 - 47
        self.racetrack_bg = pygame.transform.scale(pygame.image.load("images/racetrack.png"), size)
        self.bg = pygame.transform.scale(pygame.image.load("images/background.jpg"), self.screen.get_size())

    def run(self):
        while True:
            self.clock.tick(self.fps)
            # graphic
            self.draw_taskbar()
            self.group_horse.draw(self.screen)
            pygame.display.update()
            # event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.VIDEORESIZE:
                    self.update_size()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.bet_level:
                        # kiểm tra tất cả các nút cược xem nút nào được nhấn khi có sự kiện nhấn chuột trái
                        # := chỉ có trên python 3.9
                        # phiên bản thấp hơn sử dụng
                        # obj = button.check_mouse_click()
                        # if obj:
                        if obj := button.check_mouse_click():
                            if self.money == 0 or self.money < obj.amount:
                                self.message = "You don't have enough money"
                                print("You don't have enough money")
                            else:
                                self.message = ""
                                for b in self.bet_level:
                                    b.clicked = False
                                obj.clicked = True
                                self.bet = obj.amount
                            break
                    for horse in self.horses:
                        if horse.is_clicked():
                            if self.bet:
                                print("Selected", horse.ID)
                                print("Bet", self.bet)
                                self.select = horse.ID
                                self.start()
                                break
                            else:
                                self.message = "You have not chosen your bet"
                                print('You have not chosen your bet')

    def start(self):
        pygame.display.set_mode(self.screen.get_size(), 0)
        self.draw_taskbar()
        rank = []
        timer = 0
        while True:
            self.clock.tick(self.fps)
            # graphic
            self.screen.blit(self.racetrack_bg, (0, self.screen.get_height()//3 - 47))
            self.group_horse.draw(self.screen)
            self.group_horse.update()
            pygame.display.update()
            # event
            if all((horse.finished for horse in self.horses)):
                if not timer:
                    timer = time.perf_counter()
                    print(rank)
                    if rank:
                        if self.select == rank[0]:
                            self.change_status("YOU WIN", RED)
                            self.money += self.bet * 4
                        else:
                            self.change_status("YOU LOSE", RED)
                            self.money -= self.bet
                if time.perf_counter() - timer >= 1:
                    self.restart()
                    return
            for horse in self.horses:
                if not horse.finished:
                    if horse.rect.x == self.screen.get_width() - horse.size[0]:
                        rank.append(horse.ID)
                        horse.finished = True
                    if horse.rect.x == 0:
                        horse.finished = True
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                if event.type == pygame.VIDEORESIZE:
                    pass


if __name__ == '__main__':
    pygame.init()
    window = pygame.display.set_mode((1080, 600), pygame.RESIZABLE)
    Game(master=window).run()