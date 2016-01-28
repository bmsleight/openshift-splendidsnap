from wand.image import Image
from wand.drawing import Drawing
from wand.image import Font
from wand.color import Color
from wand.display import display

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4, cm

from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.styles import ParagraphStyle


import random, tempfile, binascii

import argparse, sys, glob, os, shutil, zipfile
 

class CardPosition:
    def __init__(self, position, thumb_filename, thumb_width):
        x, y  = position
        self.x = x * thumb_width
        self.y = y * thumb_width
        self.thumb_width = thumb_width
        self.thumb_height = thumb_width
        self.rotate = random.randrange(0, 360, 5)
#        self.percentageSize = random.randrange(20, 90, 10)
        self.percentageSize = random.choice([40,45,50,75,80])
        self.thumb = tempfile.NamedTemporaryFile(delete=True, suffix="XX.png")
        self.thumb_as_list = []
        with Image(filename=thumb_filename) as img:
            with img[:, :] as duplicate:
                # Trim takes out border, so I need to double line
                with Color('Chocolate') as border_color:
                    duplicate.border(color=border_color, width=int(duplicate.width/10), height=int(duplicate.height/10))
                with Color('white') as border_color:
                    duplicate.border(color=border_color, width=2, height=2)
                duplicate.rotate(self.rotate)
                duplicate.transform(resize=str(thumb_width)) # make sure still width s
                # + 5% to give space between images
                duplicate.transform(resize=str(self.percentageSize+5)+'%')
                duplicate.trim()
                self.thumb_width = duplicate.width # Newe resized width
                self.thumb_height = duplicate.height # Newe resized width

class Pack:
    def __init__(self, images_filenames_list):
        self.standard_width = 300
        self.thumb_width = 30
        self.thumb_ratio = self.standard_width / self.thumb_width
        self.card_width = self.standard_width * 3
        self.thumb_ext = '_thumb.png' 
        self.card_image_filenames_list = []
        self.images_filenames_list = []
        self.cards = []
        self.card_positions = []
        self.debug = True
        for images_filename in images_filenames_list:
            filename_copied = tempfile.NamedTemporaryFile(delete=False, suffix="YY.png")
            with Image(width=self.standard_width, height=self.standard_width) as img:
                offset_x, offset_y = (0,0)
                with Image(filename=images_filename) as master_img:
                    aspect_ratio = float(master_img.width)/float(master_img.height)
                    if master_img.width > master_img.height:
                        master_img.transform(resize=str(self.standard_width))
                        offset_y = int((self.standard_width - master_img.height)/2)
                    else:
                        master_img.transform(resize='x' + str(self.standard_width))
                        offset_x = int((self.standard_width - master_img.width)/2)
                    img.composite(master_img, offset_x, offset_y)
                img.save(filename=filename_copied.name)
                img.transform(resize=str(self.thumb_width))
                img.save(filename=filename_copied.name + self.thumb_ext)
            self.images_filenames_list.append(filename_copied.name)
    def list_of_thumbs(self):
        t = []
        for images_filenames in self.images_filenames_list:
            t.append(images_filenames + self.thumb_ext)
        return(t)
    def make_card(self, image_index_list):
        position = []
        for x in range(0,3):
            for y in range(0,3):
                #if x == 1 and y == 1:
                if False:
                    pass # not the centre
                else:
                    position.append((x,y))
        random.shuffle(position)
        self.card_positions = []
        p = 0
        for index in image_index_list:
            card_position = CardPosition(position[p], 
                                         self.images_filenames_list[index]+self.thumb_ext, 
                                         self.thumb_width)
            self.card_positions.append(card_position)
            p = p + 1
        #Squeeze them together 
        interactions = 0
        while(self.move_closer() and interactions < 150):
            interactions = interactions +1
        self.inspect_card_positions(display = False)
        with Image(width=self.card_width, height=self.card_width) as img:
            final_card = tempfile.NamedTemporaryFile(delete=False, suffix="ZZ.png")
            card_index = 0 
            # the index refered to the long list of images [0,1,5,6]
            # card_index is to work through positions of the cards [0,1,2,3]
            for index in image_index_list:
                 with Image(filename=self.images_filenames_list[index]) as overlay:
                     # self.thumb_ratio
                     overlay.rotate(self.card_positions[card_index].rotate)
                     overlay.transform(resize=str(self.standard_width)) # make sure still width s
                     overlay.transform(resize=str(self.card_positions[card_index].percentageSize)+'%')
                     x = self.card_positions[card_index].x * self.thumb_ratio
                     y = self.card_positions[card_index].y * self.thumb_ratio
                     img.composite(overlay, int(x), int(y))
                 card_index = card_index + 1
            img.trim()
            with Image(width=self.card_width, height=self.card_width) as final_img:
                if img.width > img.height:
                    img.transform(resize=str(self.card_width))
                    final_img.composite(img, 0, int((self.card_width - img.height)/2))
                else:
                    img.transform(resize='x' + str(self.card_width))      
                    final_img.composite(img, int((self.card_width - img.width)/2), 0)            
                final_img.save(filename=final_card.name)

            self.cards.append(final_card.name)

    def inspect_card_positions(self, display = False):
        inspect_canvas = []
        # Canvas is three times bigger than thumb
        inspect_width = self.thumb_width*3
        clash = False
        for x in range(0, inspect_width):
            for y in range(0, inspect_width):
                inspect_canvas.append(0)
        for card_position in self.card_positions:
            pos_x_on_canvas = card_position.x 
            pos_y_on_canvas = card_position.y

            for x in range(0, card_position.thumb_width):
                for y in range(0, card_position.thumb_height):
                    pixel = 1
                    inspect_x = pos_x_on_canvas + x
                    inspect_y = pos_y_on_canvas + y
                    inspect_canvas[(inspect_x * inspect_width) + inspect_y] = inspect_canvas[(inspect_x * inspect_width) + inspect_y] + pixel
                    if inspect_canvas[(inspect_x * inspect_width) + inspect_y] > 1:
                        clash = True
        if (display):
            for x in range(0, inspect_width):
                g = ""
                for y in range(0, inspect_width):
                    g = g + str(inspect_canvas[(x * inspect_width) + y])
                print(g)
        return clash
    def move_closer(self):
        movement = False # No movements
        tmp_card_positions = self.card_positions
#        inc = self.thumb_width / 10
        inc = 1
        for index in range(0, len(self.card_positions)):
            x = self.card_positions[index].x
            if x > (self.thumb_width * 1.5):
                self.card_positions[index].x = self.card_positions[index].x - inc
            else:
                self.card_positions[index].x = self.card_positions[index].x + inc
            if (self.inspect_card_positions()):
                # We have a clash with this move - revert
                self.card_positions[index].x = x
            else:
                movement = True
        for index in range(0, len(self.card_positions)):
            y = self.card_positions[index].y
            if y > (self.thumb_width * 1.5):
                self.card_positions[index].y = self.card_positions[index].y - inc
            else:
                self.card_positions[index].y = self.card_positions[index].y + inc
            if (self.inspect_card_positions()):
                # We have a clash with this move - revert
                self.card_positions[index].y = y
            else:
                movement = True
        return movement

	

#http://stackoverflow.com/questions/6240113/what-are-the-mathematical-computational-principles-behind-this-game
def simple_card_list(p):
    cards = []
    for i in range(p):
        pictures=[]
        for j in range(p):
            pictures.append(i * p + j)
        pictures.append(p*p)
        cards.append(pictures)
    for i in range(p):
        for j in range(p):
            pictures=[]
            for k in range(p):
                pictures.append(k * p + (j + i * k) % p)
            pictures.append(p * p + 1 + i)
            cards.append(pictures)
     
    pictures=[]
    for i in range(p+1):
        pictures.append(p * p + i)
    cards.append(pictures)
    return cards, p * p + p +1
    # q = p * p + p + 1
    # q-1 = p * p + p

def display_using_stars(cards, num_pictures):
    for pictures_for_card in cards:
        p = ""
        for c in range(1,num_pictures+1):
            if c in pictures_for_card:
                p = p  + '{: >3d}'.format(c)
            else:
                p = p + "   "
        print (p)
      

def random_colour_text():
    colours = ['red', 'Orange', 'Green', 'NavyBlue', 'Purple', 'Brown']
    return(random.choice(colours))
#    r = random.randrange(0, 255, 1)
#    g = random.randrange(0, 255, 1)
#    b = random.randrange(0, 255, 1)
#    colour = 'rgb(' + str(r) + ',' + str(g) + ',' + str(b) + ')'
    return(colour)

def random_font_path_text():
    fonts = ['LiberationMono-BoldItalic.ttf', 'LiberationSansNarrow-Bold.ttf', 
             'LiberationMono-Bold.ttf', 'LiberationSansNarrow-Italic.ttf',
             'LiberationMono-Italic.ttf', 'LiberationSansNarrow-Regular.ttf',
             'LiberationMono-Regular.ttf ', 'LiberationSans-Regular.ttf',
             'LiberationSans-BoldItalic.ttf', 'LiberationSerif-BoldItalic.ttf',
             'LiberationSans-Bold.ttf', 'LiberationSerif-Bold.ttf',
             'LiberationSans-Italic.ttf', 'LiberationSerif-Italic.ttf'
             'LiberationSansNarrow-BoldItalic.ttf', 'LiberationSerif-Regular.ttf']
#    return('/usr/share/fonts/truetype/liberation/' + random.choice(fonts))
    paths = ['/usr/share/fonts/truetype/freefont/*', '/usr/share/fonts/truetype/liberation/*', '/usr/share/fonts/truetype/ubuntu-font-family/*']
    font = []
    for path in paths:
        fonts = fonts + glob.glob(path)
    return(random.choice(fonts)) 

def text_as_image(width=300, height=300, text="Hello", filename="tmp.png"):
    with Image(width=width, height=height) as img:
        font = Font(path=random_font_path_text(), color=Color(random_colour_text() ))
        img.caption(text,left=8, top=8,width=width-15,height=height-15,font=font,gravity='center')
        img.save(filename=filename)

def showcase_image(images_filenames_list, showcase = "/tmp/show.png", width=850, height=450):
    # Need to mkae these width actually not just globals. lazy code
    index = len(images_filenames_list) - 1
    with Image(width=width, height=height) as img:
       with Image(filename=images_filenames_list[index]) as overlay:
           overlay.transform(resize=str(300))
           with Color('white') as border_color:
               overlay.border(color=border_color, width=20, height=20)
           with Color('black') as border_color:
               overlay.border(color=border_color, width=5, height=5)
           img.composite(overlay, 50, 50)
       with Image(filename=images_filenames_list[index-1]) as overlay:
           overlay.transform(resize=str(300))
           with Color('white') as border_color:
               overlay.border(color=border_color, width=20, height=20)
           with Color('black') as border_color:
               overlay.border(color=border_color, width=5, height=5)
           img.composite(overlay, 450, 50)
       img.save(filename=showcase)


def unpack_flat(hilly_zip):
    tmp_dir = tempfile.mkdtemp(suffix="_flat_zip")
    with zipfile.ZipFile(hilly_zip) as zip_file:    

        for member in zip_file.namelist():
            filename = os.path.basename(member)
            # skip directories
            if not filename:
                continue

            # copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            # myfile = open(myfile_path, "wb")
            target = open(os.path.join(tmp_dir, filename), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
    return tmp_dir

def simple_text_wrap(canvas, h_from_top, text, style="", w_from_side = 1*cm, increment_h = 1*cm):
    width, height = A4
    if not style:
        style = ParagraphStyle('nostyle',
        fontName='Helvetica-Bold', fontSize=6, leading=6,
        alignment=TA_CENTER,
        )
    p = Paragraph(text, style)
    p_width, p_height = p.wrapOn(canvas, width-2*w_from_side, h_from_top)
    h_from_top = h_from_top - p_height
    p.drawOn(canvas, w_from_side, h_from_top)
    return h_from_top

def titlePage(canvas, pack_name, creator, images_per_card, word_list, image_zip_name, source_of_images):
    width, height = A4
    title = ParagraphStyle('title',
        fontName='Helvetica-Bold', fontSize=24, leading=48,
        alignment=TA_CENTER,
    )
    normal = ParagraphStyle('normal',
        fontName='Helvetica', fontSize=12, leading=18,
        alignment=TA_LEFT,
    )    
    config = ParagraphStyle('normal',
        fontName='Helvetica', fontSize=10, leading=10,
        alignment=TA_LEFT,
    )

    text_title = "<link href='http://SplendidSnap.com'  color='blue'>Splendid Snap</link>"
    text_detail='''
Splendid Snap is a group card game. It consists of a pack of cards, with a selection of symbols on each card.  On two cards, there is one identical symbol in common on each card. On any two cards, there will always be one and only one match of symbols. 
<br/>
<br/>
<u>How to play - Two to Six Players</u>
<br/>
Choose one person to deal the cards between the players. 
<br/>
A full game you deal 10 cards face down for each player and one card in the middle, (less cards can be dealt for a quicker game).
<br/>
<br/>
Each player turns their pile of cards over but keeps them covered with their hand. The dealer turns the centre card and shouts "Splendid".
<br/>
<br/>
Each player looks for a matching symbol (or words) on their top card which matches the centre card. When they find one they must shout the symbol as they put it on top of the centre pile. This card placed becomes the new card everyone must now try and match. If the person does not shout the name they will not be allowed to place the card. If two people call out exactly the same time, they can both place their card.
<br/>
<br/>
The person to win is the one who manages to get rid of all of their cards first.
'''
    h_from_top = height - 1*cm
    w_from_side = 1*cm

    h_from_top = simple_text_wrap(canvas, h_from_top, text_title, title)
    h_from_top = simple_text_wrap(canvas, h_from_top, text_detail, normal)
    h_from_top = h_from_top - 5*cm
    h_from_top = simple_text_wrap(canvas, h_from_top, "<u>Pack Details</u>", normal)
    h_from_top = simple_text_wrap(canvas, h_from_top, "Pack name: " + pack_name + " with " + str(images_per_card) + " images per card", config)
    if word_list:
        using = "Using word list of " + str(word_list)
        h_from_top = simple_text_wrap(canvas, h_from_top, using, config)
    if image_zip_name:
        using = "Using images in zip file: " + image_zip_name
        h_from_top = simple_text_wrap(canvas, h_from_top, using, config)
    if source_of_images:
        h_from_top = simple_text_wrap(canvas, h_from_top, "Images from: " + source_of_images, config)
    h_from_top = simple_text_wrap(canvas, h_from_top, "Created by: " + creator, config)
    canvas.showPage()



def list_of_images_from_text(textList):
    images = []
    for text in textList:
        if text:
            tf = tempfile.NamedTemporaryFile(delete=False, suffix="WW.png")
            text_as_image(text=text.rstrip().lstrip(), filename=tf.name)
            images.append(tf.name)
    return images

def draw_grid_lines(pdf, total_card_size_mm, page_x, page_y, cards_x, page_margin_x, cards_y, page_margin_y):
    # draw grid lines
    pdf.setLineWidth(0.1)
    pdf.setDash(1,10)
    for x in range(0, cards_x+1):
        x_line = page_margin_x + (x * total_card_size_mm)
        pdf.line(x_line*mm, 0, x_line*mm, page_y*mm) 
    for y in range(0, cards_y+1):
        y_line = page_margin_y + (y * total_card_size_mm)
        pdf.line(0, y_line*mm, page_x*mm, y_line*mm)


def generate__a4_pdf_from_images_list(pdf_name="ss.pdf", images_filenames_list=[], card_size_mm = 80, card_boarder_mm = 5, pack_name = "SplendidSomething", creator="bmsleight", images_per_card = 3, word_list = [], image_zip_name = "", source_of_images = ""):
    pdf = Canvas(pdf_name)
    titlePage(pdf, pack_name, creator, images_per_card, word_list, image_zip_name, source_of_images)
    page_x = 210
    page_y = 297
    total_card_size_mm = card_size_mm + card_boarder_mm*2
    cards_x = int(page_x / total_card_size_mm)
    page_margin_x = (page_x-(cards_x*total_card_size_mm))/2
    cards_y = int(page_y / total_card_size_mm)
    page_margin_y = (page_y-(cards_y*total_card_size_mm))/2
    index_images = 0
    for pages in range(0, int(1+(len(images_filenames_list)/(cards_x*cards_y)) ) ):
        draw_grid_lines(pdf, total_card_size_mm, page_x, page_y, cards_x, page_margin_x, cards_y, page_margin_y)
        for x in range(0,cards_x):
            for y in range(0,cards_y):
                if index_images < len(images_filenames_list):
                    x_pos = page_margin_x + (x * total_card_size_mm) + card_boarder_mm
                    y_pos = page_margin_y + (y * total_card_size_mm) + card_boarder_mm
                    pdf.drawImage(images_filenames_list[index_images], x_pos*mm, y_pos*mm, 
                                  width=card_size_mm*mm, height=card_size_mm*mm, mask='auto')
                    index_images = index_images + 1
        simple_text_wrap(pdf, 5*mm, "<link href='http://SplendidSnap.com' color='blue'>Created at http://SplendidSnap.com</link>")
        pdf.showPage()
    # Backing
    tf = tempfile.NamedTemporaryFile(delete=False, suffix="ssc.png")
    with Image(width=300, height=300) as img:
        font = Font(path="/usr/share/fonts/truetype/freefont/LiberationMono-Bold.ttf", color=Color('NavyBlue'))
        img.caption('Splendid\nSnap\n.com', font=font, gravity='center')
        img.save(filename=tf.name)
        draw_grid_lines(pdf, total_card_size_mm, page_x, page_y, cards_x, page_margin_x, cards_y, page_margin_y)
        for x in range(0,cards_x):
            for y in range(0,cards_y):
                x_pos = page_margin_x + (x * total_card_size_mm) + card_boarder_mm
                y_pos = page_margin_y + (y * total_card_size_mm) + card_boarder_mm
                pdf.drawImage(tf.name, x_pos*mm, y_pos*mm, 
                              width=card_size_mm*mm, height=card_size_mm*mm, mask='auto')
        pdf.showPage()
    pdf.save()

def clean_up(remove):
    for rm in remove:
        os.remove(rm)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make of pack of Splendid Snap cards')
 
    parser.add_argument('-v', '--verbose',
        action="store_true",
        help="verbose output" ) 
    parser.add_argument('-t', '--texts',
        type=argparse.FileType('r'), 
        help="List of Texts to convert to images")
    parser.add_argument('-e', '--etexts',
        type=argparse.FileType('r'), 
        help="List of Texts to convert to images, will be are essential and will be used")
    parser.add_argument('-i', '--imagesdir',
        help="Directory of images to add")
    parser.add_argument('-z', '--imageszip',
        help="A zip files of images to add")
    parser.add_argument('outfile',
        help="pdf file to be created")
    parser.add_argument("-n", "--number", required=True, 
                    type=int, choices=[3, 4, 5, 6, 7, 8],
                    help="Number of Images per card")
    parser.add_argument('--stayinorder', action='store_true', help='Keep order, not random' )
    args = parser.parse_args()

    arrangements, total_needed = simple_card_list(args.number-1)
    if args.verbose:
        print("Total Images: ", total_needed-1, "Images per card: ", args.number, "Total Cards: ", len(arrangements))
        display_using_stars(arrangements, total_needed)

    images = []
    texts = []
    text_images = []
    if args.texts:
        texts = args.texts.read().splitlines()
        texts = filter(None, texts)
        text_images = list_of_images_from_text(texts)
        images = text_images
    if args.imageszip:
        tmp_imagesdir = unpack_flat(args.imageszip)
        images = images + glob.glob(tmp_imagesdir + '/*')
    if args.imagesdir:
        images = images + glob.glob(args.imagesdir + '/*')
    if args.stayinorder:
        pass
    else:
        random.shuffle(images)
    if args.etexts:
        texts = args.etexts.read().splitlines()
        texts = filter(None, texts)
        text_images_e = list_of_images_from_text(texts) 
        text_images = text_images_e + text_images
        images = text_images_e + images
    if total_needed > len(images):
        raise ValueError('Not enough Images')
    
    if args.verbose:
        print(images[:total_needed], texts)

    pack = Pack(images[:total_needed])
    for arrangement in arrangements:
        pack.make_card(arrangement)

    generate__a4_pdf_from_images_list(images_filenames_list=pack.cards, pdf_name=args.outfile) 
    showcase_image(pack.cards)

    clean_up(pack.cards + pack.list_of_thumbs() + pack.images_filenames_list)
    clean_up(text_images)
    if args.imageszip:
        shutil.rmtree(tmp_imagesdir)


