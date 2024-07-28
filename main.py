import pygame as pg
from utils import *
from typing import Callable
from tkinter.filedialog import askopenfile
from PIL import Image
import numpy as np 
#Works modularly with lib, visual is a configuration that can be chosen when importing lib

width = 600
height = 600

class UIConfiguation:
    text_color = "#616161"
    background_color = "#FDF6E3"
    button_color = "#FAFAFA"
    hover_color = "#ABA696"
    typing_background = "#FFFFFF"
    property_count = 2
    width = 600
    height = lambda self: self.property_count * 100 + 600
    preview = [(100,100),(500,500)]
    slider   = lambda self, i:    [(100        , 520 + 100 * i), (300        , 580+100*i)]
    autofunc = lambda self, i, j: [(320 + 100*j, 520 + 100 * j), (320 + 100*j, 580+100*i)]
    save_button = lambda self, i: [(500, 520 + 100 * i), (550, 580 + 100 * i)]
    font_size : int = 20
    font_lib = "OpenSans.ttf"
    font_init = None

class Automation:
    name : str = "Joe",
    function : Callable[[list], float] = lambda a: 1.0

class ImageFilterConfiguration:
    name : str = "Unnamed Image Processing Preview"
    property_names : list[str] = []
    property_intervals : list[tuple[float, float]]= []
    property_interval_segments : list[int] = []
    property_automations : list[list[tuple[str,Callable[[list], float]]]] = []
    def add_property(self, name : str, interval_left : float, interval_right : float, interval_segments : int, automations : list[Automation]):
        self.property_names.append(name)
        self.property_intervals.append((interval_left, interval_right))
        self.property_interval_segments.append((interval_left, interval_right))
        self.property_automations.append(automations)

class Slider:
    #Configuration
    interval_left : float = 0.0
    interval_right : float = 99.0
    interval_segments : int = 100
    slider_color = "#555555"
    pole_color = "#F0F0F0"

    #Size Configuration
    px_rec_offset_window = [(-20, -40), (20, 40)]
    height = 100
    width = 100
    slider_px_rel_location_window = [(0,70),(100,75)]
    y_center = 72

    #States
    value : float = 0
    mouse_on : bool = False
    mouse_grab_offset : float = 0

    def __init__(self, name, interval_left, interval_right, interval_segments, slider_color):
        self.name = name
        self.interval_left = interval_left
        self.interval_right = interval_right

    def get_slider_rel_x_location(self):
        lpx1 = self.slider_px_rel_location_window[0][0]
        lpx2 = self.slider_px_rel_location_window[0][1]
        return clamp(mapval(self.value, self.interval_left, self.interval_right, lpx1, lpx2), lpx1, lpx2)

    def get_value_from_slider(self, rel_mouse_x):
        rel_slider_x = rel_mouse_x
        lpx1 = self.slider_px_rel_location_window[0][0]
        lpx2 = self.slider_px_rel_location_window[0][1]
        il = self.interval_left
        ir = self.interval_right
        suggested_value = mapval(rel_slider_x, lpx1, lpx2, self.interval_left, self.interval_right)
        suggested_value = clamp(suggested_value, self.interval_left, self.interval_right)
        #The position by the mouse yields a certain value in the range, but this must be snapped to 
        #the nearest corresponding discretized value. This can be done by mapping the range of values
        #to a corresponding range of integer values, and then rounding and converting back.
        seg = round(mapval(suggested_value, il, ir, 0, self.interval_segments - 1))
        value = mapval(seg, 0, self.interval_segments - 1, il, ir)
        return value
    
    def mouse_on_slider(self, rel_mouse_x, rel_mouse_y) -> bool:
        o = self.px_rec_offset_window
        x = self.get_slider_rel_x_location()
        y = self.y_center
        lpx1 = x + o[0][0]
        lpx2 = x + o[1][0]
        lpy1 = y + o[0][1]
        lpy2 = y + o[1][1]
        return lpx1 <= rel_mouse_x and rel_mouse_x <= lpx2 and lpy1 <= rel_mouse_y and rel_mouse_y <= lpy2
    
    def try_slider(self, rel_mouse_x, rel_mouse_y, recent_events) -> bool:
        mos = self.mouse_on_slider(rel_mouse_x, rel_mouse_y)
        for e in recent_events:
            if e.type == pg.MOUSEBUTTONDOWN and mos:
                self.mouse_on = True
                self.mouse_grab_offset = rel_mouse_x - self.get_slider_rel_x_location()
            if e.type == pg.MOUSEBUTTONUP:
                self.mouse_on = False
        if self.mouse_on: 
            self.value = self.get_value_from_slider(rel_mouse_x - self.mouse_grab_offset)

    def render(self, interface, x, y):
        sx = self.get_slider_rel_x_location()
        sy = self.y_center
        oslide = self.px_rec_offset_window
        opole = self.slider_px_rel_location_window
        rslider = pg.Rect(x+sx+oslide[0][0],y+sy+oslide[0][1], oslide[1][0]-oslide[0][0], oslide[1][1]-oslide[0][1])
        rpole   = pg.Rect(x+opole[0][0]   , y+opole[0][1]  , opole[1][0]-opole[0][0], opole[1][1]-opole[0][1])
        pg.draw.rect(interface.screen, self.slider_color, rslider)
        pg.draw.rect(interface.screen, self.pole_color, rpole)
        
class Button:
    label : str = "Unnamed Button"
    height = 100
    width = 100
    color = "#999999"
    hover_color = "#888888"
    text_color = "#555555"
    font = None

    def __init__(self, label, font, width, height, color, hover_color,text_color):
        self.label =label
        self.font = font
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color

    def is_mouse_over(self, rel_mouse_x, rel_mouse_y):
        #TODO: Use collidepoint instead?
        return 0 < rel_mouse_x and rel_mouse_x < self.width and 0 < rel_mouse_y and rel_mouse_y < self.height

    def was_just_clicked(self, rel_mouse_x, rel_mouse_y, recent_events) -> bool:
        mob = self.is_mouse_over(rel_mouse_x, rel_mouse_y)
        for e in recent_events:
            if e.type == pg.MOUSEBUTTONDOWN and mob:
                return True
            
    def render(self, interface, x, y, rel_mouse_x, rel_mouse_y):
        r = pg.Rect(x,y,self.width,self.height)
        pg.draw.rect(interface.screen, self.hover_color if self.is_mouse_over(rel_mouse_x, rel_mouse_y) else self.color, r)
        interface.drawText(interface.screen, self.label, self.text_color, r, self.font, aa = True)

class ImagePreviewBox:
    """
    A box which displays an image preview from a source, which can be dragged around.
    Needs a quick-access source which can fetch an entire unfiltered version of the image
    filtered source to preview application of the properties on a smaller callable segment. 
    Also requires a loading image to assert to the user that the image is currently loading.
    Render before any other buttons to avoid the subtractive surfaces covering up other elements.
    Only use one image preview box at a time for them to correctly function.
    """ 

    #Configuration
    height = 400
    width = 400
    apply_properties_to_low_res_img : bool = True

    #Variables
    excerpt : list[tuple[int,int]] = [(0,0),(400,400)]
    unfiltered_image_coords : tuple[int,int] = (0,0)
    unfiltered_image_zoom : int = 1
    unfiltered_original_size : tuple[int,int] = None
    curr_image : pg.Surface = None
    curr_fp : str = None
    loading_fp : str = None

    #States
    should_state : int = 300 #100 for unfiltered, 200 for filtered, 300 for loading
    image_state : int = 0 #Trailing variable, will match should_state and regenerate image as needed
    zoom_mode = False


    unfiltered_image_source : Callable[[], pg.Surface] = None
    # Unfiltered image source should constantly return the whole image. When it is panned around,
    # it will actually be viewed through a window: the whole thing will be rendered and then 
    # background color will be overlay to show only a section of the image.
    filtered_image_source : Callable[[list[tuple[int,int]]], pg.Surface] = None
    # Filtered image source allows for more processing time by not requiring the image to be able to
    # be panned and zoomed on: given an excerpt, a loaded pg surface of a small processed image
    # (which can be done viapng conversion or direct loading of the image) is instead the parameter 
    # to be generated
    loading_image_source : Callable[[],pg.Surface]
    # A placeholder image for loading

    def __init__(self, height, width, unfiltered_image_source = None, 
                                      filtered_image_source = None, 
                                      loading_image_source = None):
        if unfiltered_image_source == None:
            unfiltered_image_source = self.default_source_routine
        if filtered_image_source == None:
            filtered_image_source = self.default_crop_source_routine
        if loading_image_source == None:
            loading_image_source = self.default_loading_source_routine
        self.height = height
        self.width = width
        self.unfiltered_image_source = unfiltered_image_source
        self.filtered_image_source = filtered_image_source
        self.loading_image_source = loading_image_source

    def from_pil_to_pg(img):
        numpy_array = np.array(img)
        surf = pg.surfarray.make_surface(numpy_array.swapaxes(0, 1))
        return surf

    def default_crop_source_routine(self, excerpt):
        e = excerpt
        box = (e[0][0],e[0][1],e[1][0],e[1][1])
        img = Image.open(self.curr_fp, 'r').convert("RGB")
        img = img.crop(box)
        return ImagePreviewBox.from_pil_to_pg(img)

    def default_source_routine(self):
        return pg.image.load(self.curr_fp)

    def default_loading_source_routine(self):
        return pg.image.load(self.curr_fp)

    def get_excerpt_focus(self) -> list[tuple[int,int]]:
        #return PLACEHOLDER
        pass

    def render(self, interface, x, y):
        #TODO Add thread so it doesnt wait
        #Figure out some sort of regeneration event
        c = self.unfiltered_image_coords
        if self.should_state == 100:
            if self.image_state != self.should_state:
                self.image_state = self.should_state
                self.curr_image = (self.unfiltered_image_source)()
            interface.screen.blit(self.curr_image, (x+c[0],y+c[1]))
            #Todo: Handle scaling and covering
        if self.should_state == 200:
            if self.image_state != self.should_state:
                self.image_state = self.should_state
                self.curr_image = (self.filtered_image_source)(self.excerpt)
            interface.screen.blit(self.curr_image, (x,y))

        if self.should_state == 300:
            if self.image_state != self.should_state:
                self.image_state = self.should_state
                self.curr_image = (self.loading_image_source)()
                self.should_state = 200
            interface.screen.blit(self.curr_image, (x,y))
    
    def try_drag_zoom(self):
        #TODO Update Zoom and Zoom MOde with dragging

        pass
        #updates excerpt and coordinates, saves

class Interface:
    #Config
    uiconf : UIConfiguation = UIConfiguation()
    imagefilterconf : ImageFilterConfiguration = ImageFilterConfiguration()

    #Operators
    screen = None
    clock = None

    #States
    sliders : list[Slider] = []
    save_and_next_button : Button = None
    quit_button : Button = None
    select_infolder_button : Button = None
    select_outfolder_button : Button = None
    reenable_auto_filter_button : Button = None

    #Variables
    infolder : str = None
    outfolder : str = None
    curr_img : str = None
    curr_img_i : str = 0
    imgs_cache : list[str] = None

    def begin_window(self):
        pg.init()
        self.screen = pg.display.set_mode((width, height))
        pg.display.set_caption(self.imagefilterconf.name)
        self.clock = pg.time.Clock()
        pg.font.init()
        self.uiconf.font = pg.font.Font(self.uiconf.font_lib, size = self.uiconf.font_size)

    #word wrap code from pygame.org wiki
    def drawText(self, surface, text, color, rect, font, aa=False, bkg=None):
        rect = pg.Rect(rect)
        y = rect.top
        lineSpacing = -2
        fontHeight = font.size("Tg")[1]
        while text:
            i = 1
            if y + fontHeight > rect.bottom:
                break
            while font.size(text[:i])[0] < rect.width and i < len(text):
                i += 1
            if i < len(text): 
                i = text.rfind(" ", 0, i) + 1
            if bkg:
                image = font.render(text[:i], 1, color, bkg)
                image.set_colorkey(bkg)
            else:
                image = font.render(text[:i], aa, color)
            surface.blit(image, (rect.left, y))
            y += fontHeight + lineSpacing
            text = text[i:]
        return text

    def await_select_folder(self):
        pass

    def image_operations(self):
        counter = 0
        poop = Button(str(counter), self.uiconf.font, 80, 80, self.uiconf.button_color, self.uiconf.hover_color, self.uiconf.text_color)
        pee = Slider(5, 15, 10, "#123456", "#654321")
        fart = ImagePreviewBox(500, 500)
        ImagePreviewBox.curr_fp = "test.JPG"
        ImagePreviewBox.loading_fp = "testload.PNG"
        while True:
            (mx, my) = pg.mouse.get_pos()
            self.screen.fill(self.uiconf.background_color)
            await_alert_box = pg.Rect(100,100,500,500)
            self.drawText(self.screen, "Please select infolder to see images", self.uiconf.text_color, await_alert_box, self.uiconf.font)
            change_infolder_block = pg.Rect(50,50,80,80)

            fart.render(self, 50, 50)

            poop.render(self, 50, 50, mx - 50, my - 50)

            pee.render(self, 100,100)

            pg.display.update() 
            self.clock.tick(60)
            recent_events = [e for e in pg.event.get()]
            for e in recent_events:
                if e.type == pg.QUIT:
                    pg.quit()

            if poop.was_just_clicked(mx - 50, my - 50, recent_events):
                counter += 1
                poop.label = str(counter)
            pee.try_slider(mx - 100, my - 100, recent_events)      


    def main(self):
        self.sliders = []
        si = self.imagefilterconf
        for i in range(len(si.property_names)):
            s = Slider()
            s.interval_left = si.property_intervals[i][0]
            s.interval_right = si.property_intervals[i][1]
            s.interval_segments = si.property_interval_segments[i]
            s.name = si.property_names[i]
            self.sliders.append()
            
        #self.await_select_folder()
        self.image_operations()

        #Display all elements
        prc = self.uiconf.preview
        preview = pg.Rect(prc[0][0], prc[0][1], prc[1][0] - prc[0][0], prc[1][1] - prc[0][1])
        
        #display_all elements:
        #    Image: apply filter
        #    Sliders: Check
        #    Buttons: Check

    def create_and_await_frq(question):
        global screen
        active_string = ""
        while True:

            if background_image is not None:
                screen.blit(background_image, (0, 0))
            else:
                surface = pg.Surface((width, height))
                surface.fill(background_color)
                screen.blit(surface, (0,0))

            question_block = pg.Rect(50, 50, width - 100, 100)
            self.drawText(screen, question, self.uiconf.text_color, question_block, question_font, bkg = button_color)

            answer_block = pg.Rect(50, 300, width - 100, 100)
            pg.draw.rect(screen, typing_background, answer_block)
            self.drawText(screen, active_string, text_color, answer_block, answer_font, aa = True)

            pg.display.update() 
            clock.tick(60)

            for event in pg.event.get():
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_BACKSPACE:
                        active_string = active_string[:-1]
                    elif event.key == pg.K_RETURN:
                        return active_string
                    else:
                        active_string += event.unicode
                if event.type == pg.QUIT:
                    pg.quit()
                    return "q"

interface : Interface = Interface()
interface.begin_window()
interface.main()
#begin_window()
#print(create_and_await_mcq("What is the capital of France?", ["Paris", "London", "Berlin", "Madrid"]))
#selected = create_and_await_mcq("What is the capital of France?", ["Paris", "London", "Berlin", "Madrid"])
#print(correctness_feedback_mcq("What is the capital of France?", ["Paris", "London", "Berlin", "Madrid"], 0, selected))