import pygame as pg
from utils import *
from typing import Callable
from tkinter import filedialog
from tkinter.filedialog import askopenfile
from PIL import Image
import numpy as np 
from tkinter import filedialog
#Works modularly with lib, visual is a configuration that can be chosen when importing lib

class UIConfiguation:
    text_color = "#616161"
    background_color = "#FDF6E3"
    background_color2 = "#FF0000"
    button_color = "#FAFAFA"
    hover_color = "#ABA696"
    typing_background = "#FFFFFF"
    property_count = 2
    width = 750
    height = lambda self: self.property_count * 100 + 600
    preview_coords = (50,50)
    preview_size = (500,500)
    slider   = lambda self, i:    [(100        , 520 + 100 * i), (300        , 580+100*i)]
    autofunc = lambda self, i, j: [(320 + 100*j, 520 + 100 * j), (320 + 100*j, 580+100*i)]
    save_button = lambda self, i: [(500, 520 + 100 * i), (550, 580 + 100 * i)]
    font_size : int = 20
    font_size_small : int = 12
    font_lib = "OpenSans.ttf"
    font = None
    font_small = None

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

    def __init__(self, interval_left, interval_right, interval_segments, slider_color):
        self.interval_left = interval_left
        self.interval_right = interval_right
        self.interval_segments = interval_segments

    def get_slider_rel_x_location(self):
        lpx1 = self.slider_px_rel_location_window[0][0]
        lpx2 = self.slider_px_rel_location_window[1][0]
        return clamp(mapval(self.value, self.interval_left, self.interval_right, lpx1, lpx2), lpx1, lpx2)

    def get_value_from_slider(self, rel_mouse_x):
        rel_slider_x = rel_mouse_x
        lpx1 = self.slider_px_rel_location_window[0][0]
        lpx2 = self.slider_px_rel_location_window[1][0]
        il = self.interval_left
        ir = self.interval_right
        suggested_value = mapval(rel_slider_x, lpx1, lpx2, self.interval_left, self.interval_right)
        suggested_value = clamp(suggested_value, self.interval_left, self.interval_right)
        #The position by the mouse yields a certain value in the range, but this must be snapped to 
        #the nearest corresponding discretized value. This can be done by mapping the range of values
        #to a corresponding range of integer values, and then rounding and converting back.
        seg = round(mapval(suggested_value, il, ir, 0, self.interval_segments - 1))
        print("seg#:"+str(seg))
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
        #print(self.value)

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
    recc_x : int = 0 #Reccomended location, for storing in configuration. Non-binding to this location.
    recc_y : int = 0

    def __init__(self, label, font, width, height, color, hover_color, text_color, recc_x, recc_y):
        self.label =label
        self.font = font
        self.width = width
        self.height = height
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.recc_x = recc_x
        self.recc_y = recc_y
    def is_mouse_over(self, rel_mouse_x, rel_mouse_y):
        #TODO: Use collidepoint instead?
        return 0 < rel_mouse_x and rel_mouse_x < self.width and 0 < rel_mouse_y and rel_mouse_y < self.height

    def was_just_clicked(self, rel_mouse_x, rel_mouse_y, recent_events) -> bool:
        mob = self.is_mouse_over(rel_mouse_x, rel_mouse_y)
        for e in recent_events:
            if e.type == pg.MOUSEBUTTONDOWN and mob:
                return True
            
    def render(self, interface, x, y, mouse_x, mouse_y):
        rel_mouse_x = mouse_x - x
        rel_mouse_y = mouse_y - y
        r = pg.Rect(x,y,self.width,self.height)
        pg.draw.rect(interface.screen, self.hover_color if self.is_mouse_over(rel_mouse_x, rel_mouse_y) else self.color, r)
        interface.drawText(interface.screen, self.label, self.text_color, r, self.font, aa = True)
    
    def render_rec(self, interface, mouse_x, mouse_y):
        self.render(interface, self.recc_x, self.recc_y, mouse_x, mouse_y)

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
    unzoomed_image : pg.Surface = None
    curr_image : pg.Surface = None
    curr_fp : str = None
    loading_fp : str = None

    #States
    should_state : int = 100 #100 for unfiltered, 200 for filtered, 300 for loading
    image_state : int = 0 #Trailing variable, will match should_state and regenerate image as needed
    zoom_mode = False
    zoom_ratio : float = 1.0
    zoom_rate : float = 1.05
    mouse_on : bool = False
    mouse_grab_offset : tuple[float, float] = None

    unfiltered_image_source : Callable[[], pg.Surface] = None
    # Unfiltered image source should constantly return the whole image. When it is panned around,
    # it will actually be viewed through a window: the whole thing will be rendered and then 
    # background color will be overlay to show only a section of the image.

    #TODO: figure out a way this can dynamically change with a cached image instead -- probably a flag,
    #rename the variable to represent both

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

    def get_curr_img_size(self):
        return self.get_curr_image().get_size()

    def get_unzoomed_img_size(self):
        self.get_curr_image()
        return self.unzoomed_image.get_size()

    def mouse_on_image(self, rel_mouse_x, rel_mouse_y) -> bool:
        return 0 <= rel_mouse_x and rel_mouse_x <= self.width and 0 <= rel_mouse_y and rel_mouse_y <= self.height
    
    def try_drag_zoom(self, rel_mouse_x, rel_mouse_y, recent_events) -> bool:
        moi = self.mouse_on_image(rel_mouse_x, rel_mouse_y)
        for e in recent_events:
            if e.type == pg.MOUSEBUTTONDOWN and moi:
                self.mouse_on = True
                self.mouse_grab_offset = sub2((rel_mouse_x,rel_mouse_y), self.unfiltered_image_coords)
                self.should_state = 100
                self.zoom_mode = True
            if e.type == pg.MOUSEBUTTONUP:
                self.mouse_on = False
            if e.type == pg.MOUSEWHEEL:
                self.should_state = 100
                self.zoom_mode = True
                self.zoom_ratio *= self.zoom_rate ** e.y
                sz = self.get_unzoomed_img_size()
                neww = self.zoom_ratio * sz[0]
                newh = self.zoom_ratio * sz[1]
                #If this zoom out would theoretically make the image smaller than the frame
                if neww < self.width or newh < self.height:
                    #Check which dimension is the worse offender and constrain image to that one
                    if neww/self.width < newh/self.height:
                        self.zoom_ratio = self.width / sz[0]
                    else:
                        self.zoom_ratio = self.height / sz[1]
                    neww = self.zoom_ratio * sz[0]
                    newh = self.zoom_ratio * sz[1]
                self.curr_image = pg.transform.scale(self.unzoomed_image, (neww, newh))
        if self.mouse_on: 
            #Assume the current image is in state 100; that should have happened upon actuating mouse_on
            surfsize = self.get_curr_img_size()
            minx = self.width - surfsize[0] 
            miny = self.height - surfsize[1]
            maxx = 0
            maxy = 0
            self.unfiltered_image_coords = clamp2(
                sub2((rel_mouse_x, rel_mouse_y), self.mouse_grab_offset),
                minx,miny,maxx,maxy)
        #print("IC:" + str(self.unfiltered_image_coords) + "MC"+ str(rel_mouse_x) + " " + str(rel_mouse_y) + "MO" + str(self.mouse_grab_offset))
        #print(self.value)

    def get_curr_image(self):
        if self.should_state == 100:
            if self.image_state != self.should_state:
                self.image_state = self.should_state
                self.curr_image = (self.unfiltered_image_source)()
                self.unzoomed_image = self.curr_image
        if self.should_state == 200:
            if self.image_state != self.should_state:
                self.image_state = self.should_state
                self.curr_image = (self.filtered_image_source)(self.excerpt)

        if self.should_state == 300:
            if self.image_state != self.should_state:
                self.image_state = self.should_state
                self.curr_image = (self.loading_image_source)()
                self.should_state = 200

        return self.curr_image

    def render(self, interface, x, y):
        #TODO Add thread so it doesnt wait
        #Figure out some sort of regeneration event
        c = self.unfiltered_image_coords
        if self.should_state == 100:
            w = interface.uiconf.width
            h = interface.uiconf.height()
            xo = self.unfiltered_image_coords[0]
            yo = self.unfiltered_image_coords[1]
            interface.screen.blit(self.get_curr_image(), (x+xo,y+yo))
            neg1 = pg.Rect(0,          0,x,h)
            neg2 = pg.Rect(0,          0,w,y)
            neg3 = pg.Rect(self.width ,0,w - self.width,h)
            neg4 = pg.Rect(0,self.height,w             ,h - self.height)
            pg.draw.rect(interface.screen, interface.uiconf.background_color, neg1)
            pg.draw.rect(interface.screen, interface.uiconf.background_color, neg2)
            pg.draw.rect(interface.screen, interface.uiconf.background_color, neg3)
            pg.draw.rect(interface.screen, interface.uiconf.background_color, neg4)
            
            #Todo: Handle scaling and covering
        if self.should_state == 200 or self.should_state == 300:
            interface.screen.blit(self.get_curr_image(), (x,y))

class Interface:
    #Config
    uiconf : UIConfiguation = UIConfiguation()
    imagefilterconf : ImageFilterConfiguration = ImageFilterConfiguration()

    #Operators
    screen = None
    clock = None

    #Elements
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
        self.screen = pg.display.set_mode((self.uiconf.width, self.uiconf.height()))
        pg.display.set_caption(self.imagefilterconf.name)
        self.clock = pg.time.Clock()
        pg.font.init()
        self.uiconf.font =       pg.font.Font(self.uiconf.font_lib, size = self.uiconf.font_size)
        self.uiconf.font_small = pg.font.Font(self.uiconf.font_lib, size = self.uiconf.font_size_small)

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
        while True:
            (mx, my) = pg.mouse.get_pos()
            self.screen.fill(self.uiconf.background_color)
            await_alert_box = pg.Rect(100,100,500,500)
            self.drawText(self.screen, "Please select infolder to see images", self.uiconf.text_color, await_alert_box, self.uiconf.font)
            self.select_infolder_button.render_rec(self, mx, my)
            self.select_outfolder_button.render_rec(self, mx, my)
            self.cache_button.render_rec(self, mx, my)
            self.save_and_next_button.render_rec(self, mx, my)
            self.quit_button.render_rec(self, mx, my)
            

            pg.display.update() 
            self.clock.tick(60)
            recent_events = [e for e in pg.event.get()]

            if self.select_infolder_button.was_just_clicked(mx - self.select_infolder_button.recc_x, 
                                                            my - self.select_infolder_button.recc_y, 
                                                            recent_events):
                self.select_input_folder()

            if self.select_outfolder_button.was_just_clicked(mx - self.select_outfolder_button.recc_x, 
                                                             my - self.select_outfolder_button.recc_y, 
                                                             recent_events):
                self.select_output_folder()

            if self.quit_button.was_just_clicked(mx - self.quit_button.recc_x, 
                                                 my - self.quit_button.recc_y, 
                                                 recent_events):
                pg.quit()
                return "q"

            if self.select_outfolder_button.was_just_clicked(mx, my, recent_events):
                self.select_output_folder()

            if self.quit_button.was_just_clicked(mx, my, recent_events):
                pg.quit()
                return "q"
            
            for e in recent_events:
                if e.type == pg.QUIT:
                    pg.quit()
                

    def select_input_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select Input Folder")
        print(f"Selected input folder: {self.input_folder}")

    def select_output_folder(self):
        self.output_folder = askopenfile(title="Select Output Folder")
        print(f"Selected output folder: {self.output_folder}")

    def image_operations(self):
        pee = Slider(5, 15, 10, "#123456")
        fart = ImagePreviewBox(500, 500)
        ImagePreviewBox.curr_fp = "test.JPG"
        ImagePreviewBox.loading_fp = "testload.PNG"
        while True:
            (mx, my) = pg.mouse.get_pos()
            self.screen.fill(self.uiconf.background_color)
            fart.render(self, 50, 50)

            pee.render(self, 100,100)

            pg.display.update() 
            self.clock.tick(60)
            recent_events = [e for e in pg.event.get()]
            for e in recent_events:
                if e.type == pg.QUIT:
                    pg.quit()

            pee.try_slider(mx - 100, my - 100, recent_events)      
            fart.try_drag_zoom(mx - 50, my - 50, recent_events)


    def main(self):
        self.sliders = []
        self.select_infolder_button = Button("Select Input  Folder",
                                              self.uiconf.font_small,
                                                100, 40,
                                              self.uiconf.button_color,
                                              self.uiconf.hover_color,
                                              self.uiconf.text_color,
                                              recc_x = 600,
                                              recc_y = 50+5)
        self.select_outfolder_button = Button("Select Output Folder",
                                              self.uiconf.font_small,
                                                100, 40,
                                              self.uiconf.button_color,
                                              self.uiconf.hover_color,
                                              self.uiconf.text_color,
                                              recc_x = 600,
                                              recc_y = 50+50+5
                                              )
        self.cache_button            = Button("Cache Window",
                                              self.uiconf.font_small,
                                                100, 40,
                                              self.uiconf.button_color,
                                              self.uiconf.hover_color,
                                              self.uiconf.text_color,
                                              recc_x = 600,
                                              recc_y = 50+100+5
                                              )
        self.save_and_next_button    = Button("Save and Next",
                                              self.uiconf.font_small,
                                                100, 40,
                                              self.uiconf.button_color,
                                              self.uiconf.hover_color,
                                              self.uiconf.text_color,
                                              recc_x = 600,
                                              recc_y = 50+150+5
                                              )
        self.quit_button            = Button("Quit",
                                              self.uiconf.font_small,
                                                100, 40,
                                              self.uiconf.button_color,
                                              self.uiconf.hover_color,
                                              self.uiconf.text_color,
                                              recc_x = 600,
                                              recc_y = 50+200+5
                                              )
        
        si = self.imagefilterconf
        for i in range(len(si.property_names)):
            s = Slider()
            s.interval_left = si.property_intervals[i][0]
            s.interval_right = si.property_intervals[i][1]
            s.interval_segments = si.property_interval_segments[i]
            s.name = si.property_names[i]
            self.sliders.append()
            
        self.await_select_folder()
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